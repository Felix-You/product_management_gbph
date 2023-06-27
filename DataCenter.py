import sys, re, threading, time, openpyxl

from typing import Union
from xml.dom.minidom import parse
import ConnSqlite as CS
from datetime import datetime, timedelta
from enum import Enum
import AreaInfo as AREA
from core.GlobalListener import global_logger
from core.KitModels import DataObject, File, LogType, Company, DataOjectWithMultiFileFields, CheckPoint, CheckItem
import os, json, configparser, csv, sqlite3
from FilePathInit import userDir, workingDir
from ID_Generate import Snow
from collections import namedtuple

# from win32 import win32api , win32gui, win32print

# 进度的存储名和显示名映射
this_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_file_path)
progress_code = {'inv': 0,
                 'ini': 1,
                 'sst': 2,  # small scale test
                 'sup': 3,
                 'clt': 4,  # clinical trial
                 'fil': 5,
                 'cmm': 6}
progress_code_r = {v: k for k, v in progress_code.items()}  # 反转progress_code
progress_text = {'inv': '调研',
                 'ini': '立项',
                 'sst': '小试',
                 'sup': '中试',
                 'clt': '临床',
                 'fil': '申报',
                 'cmm': '商业'}
# office_job_dict = {"A":"A上游信息",
#                    "B":"B下游信息",
#                    "C":"C内部决策",
#                    "D":"D合同协议",
#                    "E":"E资料文件"}
user_dir = workingDir.getUserDirectory()
with open(os.path.join(user_dir, 'office_job_types.json'), 'r', encoding='utf-8') as f:
    office_job_dict = json.load(f)
working_dir = workingDir.getWorkingDirectory()
with open(os.path.join(working_dir, 'todo_arrange_strategies.json'), 'r', encoding='utf-8') as f:
    todo_arrange_strategies = json.load(f)


# 机会代码、机会名称、机会标签映射

def update_office_job_types(type_code: str, name: str):
    '''

    :param code: "A" or "B" or  "C" ...
    :param name: Name defined by user
    :return: code, message
    '''
    if not type_code in 'ABCDE':
        # raise KeyError('"code" should be in "ABCDE". ')
        return 1, "请使用大写字母作为分类代码"
    if ":" in name or "\"" in name or ":" in name or "{" in name or "}" in name:  # 防止注入
        return 2, "名称中请勿包含英文的引号（\"）、冒号（:）、逗号（,）、大括号（{}）"
    global office_job_dict
    office_job_dict.update({type_code: name})
    with open(os.path.join(user_dir, 'office_job_types.json'), 'w', encoding='utf-8') as f:
        json.dump(office_job_dict, f, ensure_ascii=False)
    return 0, ""


def convertInt(str: str):
    if str.isdigit():
        return int(str)
    else:
        return str


change_tags = []

with open(os.path.join(this_file_path, 'tag_projection.csv')) as f:
    f_tag_projection = csv.reader(f)
    headings = next(f_tag_projection)
    for r in f_tag_projection:
        Row = namedtuple('Row', headings)
        r = map(convertInt, r)
        row = Row(*r)
        change_tags.append(row)
# 创建两个字典：{sequence_code:chance_tag_name},{change_code:[sequence_code]}
# csv模块读取到的都是字符串，数字需要转换
change_codes = [row.chance_code for row in change_tags]
change_codes = list(set(change_codes))
chance_sequence_code_dict = {}  # {chance_code： [sequence_code(status_code)]}
sequence_chance_code_dict = {}
for item in change_codes:
    chance_sequence_code_dict[item] = []
code_name_dict = {}
for row in change_tags:
    code_name_dict[row.sequence_code] = row.chance_tag_name
    chance_sequence_code_dict[row.chance_code].append(row.sequence_code)
    sequence_chance_code_dict[row.sequence_code] = row.chance_code


def convert_date_log_json(json_text: str):
    '''convert json serialized list in the format of [{'date':xxx, 'log_desc':xxx}] into text for textEdit exibhition'''
    if not json_text:
        return ''
    try:
        list_data = json.loads(json_text)
        log_list = []
        for log in reversed(list_data):
            log_list.append(log['date'] + ':')
            log_list.append(log['log_desc'])
        log_text = '\n'.join(log_list)
    except ValueError:
        log_text = json_text
    return log_text


def tableInfoFromJson(json_text):
    '''从json文件读取数据库的表结构信息'''
    table_dict = json.loads(json_text)
    table_name = table_dict['name']
    table_ddl = table_dict['ddl']
    columns = table_dict['columns']
    table_columns = []
    for column in columns:
        table_column = {}
        column_name = column['name']
        column_type = column['type']
        column_constrain_text = ''
        if 'constraints' in column.keys():
            column_constrains = column['constraints']
            for constraint in column_constrains:
                column_constrain_text += constraint['definition']
                column_constrain_text += ' '
        table_column['name'] = column_name
        table_column['ddl'] = column_name + ' ' + column_type + ' ' + column_constrain_text
        table_columns.append(table_column)
    table = {}
    table['name'] = table_name
    table['ddl'] = table_ddl
    table['columns'] = table_columns
    return table


def checkDatabase():
    '''校验并初始化数据库字段'''
    curpath = working_dir  # 当前文件路径
    table_constructor_dir = os.path.join(curpath, "tables")
    tables = {}
    for root, dirs, files in os.walk(table_constructor_dir):
        for file in files:  # 所有的csv文件
            table_name = file.split('.')[0]
            src_file = os.path.join(root, file)
            with open(src_file) as f:
                text = f.read()
                table_info = tableInfoFromJson(text)
                tables[table_name] = table_info
    # print(tables)
    db_file = userDir.getDatabase()
    if not db_file:
        global_logger.exception('未找到数据库文件')
    path = workingDir.getUserDirectory()
    # path = 'D:/'
    cx = sqlite3.connect(db_file)
    for table, table_info in tables.items():
        cursor = cx.cursor()
        sql = 'select count(*)  from sqlite_master where type= "table" and name = "%s"' % table
        nTable = cx.execute(sql).fetchall()[0][0]
        if not nTable:
            cursor.execute(table_info['ddl'])
            cx.commit()
        else:
            # 获取存在的全部字段
            col_info = cx.execute('pragma table_info("{}")'.format(table)).fetchall()
            # print('table_name',table_name,'col_info',col_info)
            col_names = []
            for item in col_info:
                col_names.append(item[1])
            # 检查字段名是否存在
            for column in table_info['columns']:
                column_name = column['name']
                if not column_name in col_names:
                    sql = 'alter table %s add column %s' % (table, column['ddl'])
                    cursor.execute(sql)
            cx.commit()


class LazyProxy:
    def __init__(self, cls, *args, **kwargs):
        self.__dict__['_cls'] = cls
        self.__dict__['_params'] = args
        self.__dict__['_kwargs'] = kwargs
        self.__dict__['_obj'] = None

    def __getattr__(self, item):
        if self.__dict__['_obj'] is None:
            self._init_obj()
        return getattr(self.__dict__['_obj'], item)

    def __setattr__(self, key, value):
        if self.__dict__['_obj'] is None:
            self._init_obj()

        setattr(self.__dict__['_obj'], key, value)

    def _init_obj(self):
        self.__dict__['_obj'] = object.__new__(self.__dict__['_cls'])


class CompanyLog(LogType):
    table_name = 'client_log'

    def __init__(self, company_catelog: str = None):
        # 首先对类属性进行初始化
        self.log_desc = None
        if company_catelog == 'client':
            self.setTableName('client_log')
        elif company_catelog == 'supplier':
            self.setTableName('supplier_log')
        self.company_id = None
        # 初始化父类
        super(CompanyLog, self).__init__()
        # 将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.redefined_super(CompanyLog, self)
        # self.trimDataFields()


class TaskType(LogType):
    table_name = 'tasks'

    def __init__(self, _id: str = '', task_desc: str = None, update_desc_list: str = None,
                 conn_project_id: str = '', inter_order_weight: int = 0,
                 create_time: datetime = None, update_time: datetime = None,
                 is_critical: bool = False, switch: bool = True,
                 officejob_type: str = 'A', on_pending: bool = False,
                 pending_days_required: int = 0, pending_start: datetime = None, pending_till: datetime = None,
                 task_weight: float = 0.0, destroy: bool = False, conn_project_table: str = 'proj_list'):
        super(TaskType, self).__init__()
        self._id = _id
        self.conn_project_id = conn_project_id
        self.create_time = create_time
        self.task_desc = task_desc
        self.update_time = update_time
        self.update_desc_list = update_desc_list
        self.is_critical = is_critical
        self.switch = switch
        self.officejob_type = officejob_type
        self.on_pending = on_pending
        self.pending_days_required = pending_days_required
        self.pending_start = pending_start
        self.pending_till = pending_till
        self.task_weight = task_weight
        self.destroy = destroy
        self.inter_order_weight = inter_order_weight
        self.conn_project_table = conn_project_table
        # self.data_fields = ['_id','conn_project_id','conn_project_table','task_desc','create_time','update_time',
        #                     'update_desc_list','is_critical','switch','officejob_type','on_pending',
        #                     'pending_days_required','pending_start','pending_till','task_weight','destroy',
        #                     'inter_order_weight']
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.redefined_super(TaskType, self)
        # self.trimDataFields()

    def load_data(self, _id):
        task_data = CS.getLinesFromTable(table_name=self.table_name, conditions={'_id': _id})
        # print(task_data)
        keys = task_data.pop()
        values = task_data[0]
        self.assign_data(keys, values)

    def renewUpdateDescList(self, update_time, update_desc):
        self.update_time = update_time
        self.update_desc_list = update_desc

    def saveTaskInsert(self):
        CS.insertSqlite(table=self.table_name, row_data=self.__dict__)

    def saveTaskUpdate(self, keys: list):
        new_data = {}
        for key in keys:
            new_data[key] = getattr(self, key)
        CS.updateSqliteCells(table_name=self.table_name, conditions={'_id': self._id},
                             update_fields=new_data)


class Task(TaskType):

    def __init__(self, _id: str = None, conn_project_id: str = None):
        super().__init__()
        self._id = _id
        self.status = 0
        self.destroyed = 0
        self.conn_project_id = conn_project_id
        # 将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.redefined_super(Task, self)
        # self.trimDataFields()

    @property
    def id(self):
        return self._id

    def getTaskDesc(self):
        return self.task_desc

    def setTaskDesc(self, desc):
        self.task_desc = desc

    def setOfficeJob(self, job_type: str = 'A'):
        self.officejob_type = job_type

    def setCritical(self, is_critical: bool = True):
        self.is_critical = is_critical

    def setSwitch(self, switch_on: bool = True):
        self.switch = switch_on

    def setCreateTime(self, time: datetime):
        self.create_time = time

    def setOnPending(self, on_pending: bool = False):
        self.on_pending = on_pending

    def setPendingDaysRequired(self, pending_days_required: int = 0):
        self.pending_days_required = pending_days_required

    def setPendingStart(self, pending_start: datetime = None):
        self.pending_start = pending_start
        if self.pending_start and self.pending_days_required:
            self.pending_till = self.pending_start + timedelta(days=self.pending_days_required)

    def setTaskWeight(self):
        pass

    def setDestroyed(self, destroy: bool = False):
        self.destroy = destroy


class MemoType(LogType):
    table_name = 'project_memo_log'

    def __init__(self):
        super(MemoType, self).__init__()
        self._id = ''
        self.conn_project_id = ''
        self.memo_desc = None
        self.create_time = None
        self.inter_order_weight = 0
        # 将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.trimDataFields()

    def saveMemoUpdate(self, keys: list):
        new_data = {}
        for key in keys:
            new_data[key] = getattr(self, key)
        CS.updateSqliteCells(table_name=self.table_name, conditions={'_id': self._id},
                             update_fields=new_data)

    def saveMemoInsert(self):
        new_data = {}
        for i, key in enumerate(self.data_fields):
            new_data[key] = getattr(self, key)
        CS.insertSqlite(self.table_name, new_data)
        pass

    def setLogContent(self, txt: str):
        self.log_content = txt

    def setCreateTime(self, t: datetime):
        self.create_time = t

    def setInterOrderWeight(self, w: int):
        self.inter_order_weight = w


class Memo(MemoType):

    def __init__(self, _id: str = None):
        super(Memo, self).__init__()

    def load_data(self, _id):
        memo_info = CS.getLinesFromTable(table_name=self.table_name, conditions={'_id': _id},
                                         order=['inter_order_weight'])
        memo_keys = memo_info.pop()
        self.assign_data(memo_keys, memo_info[0])


class MeetingType(LogType):
    table_name = 'project_meeting_log'

    def __init__(self):
        super(MeetingType, self).__init__()
        self._id = ''
        self.conn_project_id = ''
        self.meeting_desc = None
        self.create_time = None
        self.inter_order_weight = 0
        # 将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.trimDataFields()

    def saveMeetingUpdate(self, keys: list):
        new_data = {}
        for key in keys:
            new_data[key] = getattr(self, key)
        CS.updateSqliteCells(table_name=self.table_name, conditions={'_id': self._id},
                             update_fields=new_data)

    def saveMeetingInsert(self):
        new_data = {}
        for i, key in enumerate(self.data_fields):
            new_data[key] = getattr(self, key)
        CS.insertSqlite(self.table_name, new_data)
        pass

    def setLogContent(self, txt: str):
        self.log_content = txt

    def setCreateTime(self, t: datetime):
        self.create_time = t

    def setInterOrderWeight(self, w: int):
        self.inter_order_weight = w


class Meeting(MeetingType):
    def __init__(self, _id: str = None):
        super(Meeting, self).__init__()

    def load_data(self, _id):
        meeting_info = CS.getLinesFromTable(table_name=self.table_name, conditions={'_id': _id},
                                            order=['inter_order_weight'])
        meeting_keys = meeting_info.pop()
        self.assign_data(meeting_keys, meeting_info[0])


class ProjectType(DataObject):
    table_name = 'proj_list'
    log_table = 'project_meeting_log'
    status_table = 'proj_status_log'
    task_table = 'tasks'

    def __init__(self):
        super(ProjectType, self).__init__()
        # 首先初始化与数据库对应的字段
        self._id = None
        self.product = None
        self.product_id = None
        self.client = None
        self.client_id = None
        self.in_act = True
        self.clear_chance = False
        self.order_tobe = False
        self.to_visit = False
        self.is_deal = False
        self.weight = None
        self.status_code = 0  # 默认值，从
        self.current_task_num = 0
        self.highlight = False
        self.form_classification = None
        self.current_progress = None
        # self.current_pricing = None
        # self.current_demand = None
        # self.rival_pricing = None
        # self.rival_quantity = None
        # self.ladder_pricing = None
        # self.stage_demand = None

        # 将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.trimDataFields()

    def trimDataFields(self):
        self.data_fields.discard('table_name')
        self.data_fields.discard('log_table')
        self.data_fields.discard('status_table')
        self.data_fields.discard('task_table')
        self.data_fields.discard('data_fields')

    def saveProjectUpdate(self, keys: list):
        new_data = {}
        for key in keys:
            if key in self.data_fields:  # 这里仅仅只保存ProjectType包含的属性
                new_data[key] = getattr(self, key)
        CS.updateSqliteCells(table_name=self.table_name, conditions={'_id': self._id},
                             update_fields=new_data)

    def saveProjectInsert(self):
        new_data = {}
        for i, key in enumerate(self.data_fields):
            new_data[key] = getattr(self, key)
        CS.insertSqlite(self.table_name, new_data)
        pass


class ProjectStatus(DataObject):
    '''商务项目的信息'''
    table_name = 'proj_status_log'
    face_name = 'Status'
    file_fields = (  # 注册文件字段
        ('research_scheme_files', File.RESEARCH_SCHEME),
        ('bid_files', File.BUSINESS_FILE),
        ('contract_files', File.BUSINESS_FILE),
    )
    CHECK_ITEMS = (
        ('client_demand', '客户关注', True),
        ('advantage_statement', '优势描述', True),
        ('bid_files', '投标文件', True),
        ('research_scheme', '研究方案', True),
        ('contract_file', '合同文件', True),
        # ('',)
    )

    def __init__(self):
        super(ProjectStatus, self).__init__()
        self._id = None
        self.status_desc = None
        self.conn_project_id = None
        self.status_code = None
        # self.conn_file_ids = None
        self.check_point_id = None
        self.check_point = None
        # self.advantage_statement = None
        # self.bid_offered = False
        # self.bid_files_ids = None
        # self.research_scheme_offered = False
        # self.research_scheme_files_ids = None
        # self.contract_file_offered = False
        # self.contract_files_ids = None

        self.current_pricing = None
        self.deal_price = None
        self.rival_pricing = None
        self.rival_disk = None
        self.is_order = False  # 是否已成交
        self.person_in_charge = None

    def make_checkpoint(self, _id:str = None):
        before_make_checkpoint = time.perf_counter()
        check_point = CheckPoint.asChildNode(father_node=self, conn_log_id=self._id)
        check_point.label = '商务/文件'
        check_point.field_name = 'project_business_files'
        check_point.create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # before_assign_id = time.perf_counter()
        if not _id:
            check_point.assign_new_id()
        else:
            check_point._id = _id
        # after_assign_id = time.perf_counter()
        # print('time for assign id= ', after_assign_id - before_assign_id)
        for field_name, name, has_file in self.CHECK_ITEMS:
            before_one_loop = time.perf_counter()
            item = CheckItem.asChildNode(father_node=self)
            item.assign_new_id()
            item.create_time = time.strftime("%Y-%m-%d %H:%M:%S")
            item.has_file = has_file
            item.field_name = field_name
            item.label = name
            item.setFace()
            item.conn_log_id = self._id
            check_point.add_children_item(item)
            after_one_loop = time.perf_counter()
            # print('item._id = ',item._id)
            # print('time for one loop = ', after_one_loop - before_one_loop)
        self.check_point_id = check_point._id
        self.check_point = check_point
        # after_make_checkpoint = time.perf_counter()
        # print('time_for_make_checkpoint=', after_make_checkpoint - before_make_checkpoint )

    def load_checkpoint(self):
        # before_load_checkpoint = time.perf_counter()
        if not self.check_point_id:
            self.make_checkpoint()
        else:
            self.check_point = CheckPoint.asChildNode(father_node=self)
            self.check_point.load_complete_data(self.check_point_id)
            if not self.check_point.basic_data_load_success:
                self.check_point = None
                self.make_checkpoint(self.check_point_id)
        after_load_checkpoint = time.perf_counter()
        # print('time for load checkpoint = ', after_load_checkpoint - before_load_checkpoint)

    def load_data(self, conn_project_id):
        proj_data = CS.getLinesFromTable(table_name=self.table_name, conditions={'conn_project_id': conn_project_id})
        keys = proj_data.pop()
        try:
            values = proj_data[0]
        except:
            return
        self.assign_data(keys, values)
        self.load_checkpoint()


class ProjectProfile(DataObject):
    '''可供立项的药品项目的自然属性、特征'''

    def __init__(self):
        self.registration_cat = None
        self.api_name = None
        self.api_id = None
        self.indications = None
        self.medical_desc = None
        self.tech_desc = None
        self.rld = None
        self.rld_id = None  # 参比
        self.specs = None  # 规格

        super(ProjectProfile, self).__init__()


class Project(ProjectType):
    face_field = 'product'

    def __init__(self, _id=None):
        super().__init__()
        if _id:
            self._id = _id
        self.tasks = []
        self.meeting_log = []
        self.memo_log = []
        self.product = None
        if self.face_field:
            self.setFace()

    def resetWeight(self):
        '''重置weight的值'''
        weight = 0
        # if self.tasks:
        #     if self.current_task_num:#current_task_num可能是None
        #         try:
        #             current_task = self.tasks[self.current_task_num-1]
        #         except IndexError:
        #             current_task = self.tasks[-1]
        #         if current_task.is_critical:
        #             weight += 3
        #         if current_task.switch == True:
        #             weight += 1
        if self.in_act:
            weight += 2
        if self.order_tobe:
            weight += 3
        if self.clear_chance:
            weight += 3
        if self.current_progress == 'ini':
            weight += 2
        elif self.current_progress == 'inv':
            weight += 1
        if sequence_chance_code_dict[self.status_code] == 1:
            weight *= 1.2
        elif sequence_chance_code_dict[self.status_code] >= 4:
            weight *= 0.5
        if self.highlight:
            weight *= 1.8
        self.weight = weight

    def load_id_data(self, _id):
        self._id = _id
        self.load_basic_data()
        self.load_status()
        self.load_task()
        self.load_task_todo_status()
        self.load_meeting()
        self.load_memo()

    def load_basic_data(self):
        '''通过project的_id查找并赋值给所有属性'''
        proj_data = CS.getLinesFromTable(table_name=self.table_name, conditions={'_id': self._id})
        keys = proj_data.pop()
        values = proj_data[0]
        for i, key in enumerate(keys):
            if hasattr(self, key):
                setattr(self, key, values[i])
        self.setFace()

    def load_status(self):
        # 装载status信息
        self.status = ProjectStatus.asChildNode(father_node=self)
        self.status.load_data(conn_project_id=self._id)
        if not self.status._id:
            self.status_code = 0
            self.status_id = Snow('st').get()
            self.status._id = self.status_id
        else:
            self.status_code = self.status.status_code
            self.status_id = self.status._id

    def load_status_code(self):
        status_code_info = CS.getLinesFromTable(table_name='proj_status_log', conditions={'conn_project_id': self._id},
                                                columns_required=['status_code'])
        status_code_info.pop()
        if not status_code_info:
            self.status_code = 0
        else:
            self.status_code = status_code_info[0][0]

    def load_task(self):
        # 装载tasks信息
        tasks_info = CS.getLinesFromTable(table_name='tasks', conditions={'conn_project_id': self._id},
                                          order=['inter_order_weight'])
        task_keys = tasks_info.pop()
        task_ids = []
        for values in tasks_info:
            temp_task = TaskType()
            temp_task.assign_data(task_keys, values)  # 给task的属性赋值
            self.tasks.append(temp_task)
            task_ids.append(temp_task._id)

    def is_active_task_critical(self, project_id:str = None):
        if not project_id:
            project_id = self._id
        if not project_id:
            raise ValueError('project_id should be a str, not None.')
        proj_task_in_act = CS.innerJoin_withList_getLines('tasks', 'todo_log', '_id', 'conn_task_id',
                                                          ['conn_project_id', 'is_critical'], ['status', 'destroyed'],
                                                          {'conn_project_id': project_id, 'is_critical': 1}, {'destroyed':0, 'status': [0, 1]},
                                                          method='left join')
        critial_in_act = 0
        for conn_project_id, is_critical, status, destroyed in proj_task_in_act:
            if is_critical and status is not None and status < 2 and not destroyed:
                critial_in_act += 1
        return

    def load_task_todo_status(self):
        task_ids = [task._id for task in self.tasks]
        # 后期改为联表查询方式。
        todo_logs = CS.getLinesFromTable(table_name='todo_log', conditions={'conn_task_id': task_ids})
        todo_keys = todo_logs.pop()
        index_of_task_id = todo_keys.index('conn_task_id')
        index_of_todo_status = todo_keys.index('status')
        index_of_todo_destroyed = todo_keys.index('destroyed')
        index_of_task_pending_till_date = todo_keys.index('pending_till_date')
        for task in self.tasks:
            for todo_log in todo_logs:
                if todo_log[index_of_task_id] == task._id:
                    task.status = todo_log[index_of_todo_status]
                    task.destroyed = todo_log[index_of_todo_destroyed]
                    task.pending_till_date = todo_log[index_of_task_pending_till_date]
                    break
            else:
                task.status = None
                task.destroyed = None
                task.pending_till_date = None

    def load_meeting(self):
        # 装载meeting_log信息
        meeting_logs_info = CS.getLinesFromTable(table_name='project_meeting_log',
                                                 conditions={'conn_project_id': self._id},
                                                 order=['inter_order_weight'])
        meeting_keys = meeting_logs_info.pop()
        for values in meeting_logs_info:
            temp = Meeting()
            temp.assign_data(meeting_keys, values)
            self.meeting_log.append(temp)

    def load_memo(self):
        # 装载memo_log信息
        memo_logs_info = CS.getLinesFromTable(table_name='project_memo_log', conditions={'conn_project_id': self._id},
                                              order=['inter_order_weight'])
        memo_keys = memo_logs_info.pop()
        for values in memo_logs_info:
            temp = Memo()
            temp.assign_data(memo_keys, values)
            self.memo_log.append(temp)


class Client(Company):
    table_name = 'clients'
    log_table_name = 'client_log'
    meeting_log_table = 'client_meeting_log'

    def __init__(self, company_name: str = None, _id: str = None, parent=None):
        super(Client, self).__init__()
        self._id = _id
        self.short_name = company_name
        self.province = None
        self.city = None
        self.town = None
        self.desc = None
        # 将以上字段的名称保存成列表
        # current_members = self.get_current_members()

        # self.add_current_member_to_data_fields(current_members)
        # self.redefined_super(Client, self)
        # self.data_fields.update([ key for key ,value in locals().items()])
        # self.trimDataFields()

        self.projects = []
        self.loadBasicData()

    def addProject(self, obj: Project):
        self.projects.append(obj)

    def reOrderProjects(self):
        # w = [project.weight for project in self.projects]
        # print(w)
        self.projects = sorted(self.projects, key=lambda project: project.weight if project.weight is not None else 0,
                               reverse=True)  # 按weight排序
        # x = [project.weight for project in self.projects]
        # print(x)


class ToDo(LogType):
    table_name = 'todo_log'

    def __init__(self, _id: str = None):
        super(ToDo, self).__init__()
        self._id = _id
        self.conn_task_id = None
        self.conn_project_id = None
        self.todo_desc = None
        self.status = 0
        self.on_pending = False
        self.pending_till_date = None
        self.is_critical = False
        self.conclusion_desc = None
        self.waiting_desc = None
        self.officejob_type = 'A'
        self.conn_task_desc = None
        self.conn_task_cat = None
        self.conn_project_id = None
        self.conn_project_name = None
        self.conn_project_in_act = False
        self.conn_project_order_tobe = False
        self.conn_project_clear_chance = False
        self.conn_project_highlight = False
        self.conn_project_is_deal = False
        self.conn_project_weight = None
        self.conn_company_id = None
        self.conn_company_name = None
        self.inter_order_weight = 0
        self.destroyed = False

    def load_basic_data(self, _id: str = None):
        if not _id:
            _id = self._id
        if not _id:
            raise ValueError('attribute "_id" not assigned')
        LogType.load_basic_data(self, _id)

    def loadConnProjectInfo(self):
        if self.conn_project_id:
            conn_project = CS.getLinesFromTable('proj_list', {'_id': self.conn_project_id})
            project_fields = conn_project.pop()
            if conn_project:
                project = dict(zip(project_fields, conn_project[0]))
                self.conn_project_name = project['product']
                self.conn_company_name = project['client']
                self.conn_company_id = project['client_id']
                self.conn_project_order_tobe = project['order_tobe']
                self.conn_project_weight = project['weight']
                self.conn_project_in_act = project['in_act']
                self.conn_project_clear_chance = project['clear_chance']
                self.conn_project_highlight = project['highlight']
                self.conn_project_is_deal = project['is_deal']
        elif self.conn_company_id:  # 无关联的项目信息
            conn_company = CS.getLinesFromTable('clients', {'_id': self.conn_company_id}, ['short_name'])
            conn_company.pop()
            self.conn_company_name = conn_company[0][0]
        if self.conn_task_id:
            conn_task = CS.getLinesFromTable('tasks', {'_id': self.conn_task_id}, ['officejob_type'])
            # task_fields = conn_task.pop()
            if conn_task:
                # task = dict(zip(task_fields, conn_task[0]))
                self.conn_task_cat = conn_task[0][0]


class TargetFlag(Enum):
    '''操作对象的枚举'''
    project = 1
    task = 2
    meeting = 3
    memo = 4
    personnel = 5


class GOperation(Enum):
    '''操作类型的枚举'''
    update = 1
    get = 2
    insert = 3
    delete = 4


class GDbCmd(object):
    db = {1: 'proj_list',
          2: 'tasks',
          3: 'project_meeting_log',
          4: 'project_memo_log',
          5: 'client'}

    def __init__(self, cmd):
        self.db_table = self.db[cmd.flag]
        self.primary_key = cmd._id
        self.fields_values = cmd.fields_values
        self.operation = cmd.operation

    def insertLine(self):
        if '_id' in self.fields_values.keys():
            if self.primary_key != self.fields_values['_id']:
                raise ValueError('Values of primary key and Gcmd._id do not match')
            else:
                CS.insertSqlite(self.db_table, self.fields_values)
        else:
            raise ValueError('Primary key not assigned')

    def updateLine(self):
        if '_id' in self.fields_values.keys():
            if self.primary_key != self.fields_values['_id']:
                raise ValueError('Values of primary key and Gcmd._id do not match')
            else:
                conditon = {'_id': self.fields_values.pop('_id')}
                CS.updateSqliteCells(self.db_table, conditions=conditon, update_fields=self.fields_values)
        else:
            raise ValueError('Primary key not assigned')

    def deleteLine(self):
        CS.deleteLineFromTable(self.db_table, {'_id': self.primary_key})

    def dumpData(self):
        operation = {1: self.updateLine,
                     3: self.insertLine,
                     4: self.deleteLine}
        operation[self.operation]()

    def getTableName(self, flag: int):
        return self.db[flag]


class GCmd(object):
    '''命令基类'''
    flag = None
    operation = None
    data = None

    def __init__(self):
        '''GCmd可以绑定一个flag，用来说明其所属的广播事件，以及自身在广播事件中的ID'''
        self.broadcast_space = None
        self.need_to_dump_data = True

    def setBroadcastSpace(self, broadcast_space):
        self.broadcast_space = broadcast_space


class GTaskCmd(GCmd):
    '''task类命令'''
    flag = TargetFlag.task.value
    table_name = 'tasks'

    def __init__(self, operation: str, _id: str, conn_company_name: str, source_widget, fields_values: dict):
        super(GTaskCmd, self).__init__()
        self._id = _id
        self.operation = getattr(GOperation, operation).value
        self.conn_company_name = conn_company_name
        self.fields_values = fields_values
        self.source_widget = source_widget


class GProjectCmd(GCmd):
    '''project类命令'''
    flag = TargetFlag.project.value
    table_name = 'proj_list'

    def __init__(self, operation: str, _id: str, conn_company_name: str, source_widget, fields_values: dict):
        super(GProjectCmd, self).__init__()
        self._id = _id
        self.operation = getattr(GOperation, operation).value
        self.fields_values = fields_values
        self.source_widget = source_widget
        self.conn_company_name = conn_company_name


class GMemoCmd(GCmd):
    '''project类命令'''
    flag = TargetFlag.memo.value
    table_name = 'project_memo_log'

    def __init__(self, operation: str, _id: str, source_widget, conn_company_name: str = None,
                 fields_values: dict = None):
        super(GMemoCmd, self).__init__()
        self._id = _id
        self.operation = getattr(GOperation, operation).value
        self.conn_company_name = conn_company_name
        self.fields_values = fields_values
        self.source_widget = source_widget


class GMeetingCmd(GCmd):
    '''project类命令'''
    flag = TargetFlag.meeting.value
    table_name = 'project_meeting_log'

    def __init__(self, operation: str, _id: str, conn_company_name: str, source_widget, fields_values: dict):
        super(GMeetingCmd, self).__init__()
        self._id = _id
        self.operation = getattr(GOperation, operation).value
        self.conn_company_name = conn_company_name
        self.fields_values = fields_values
        self.source_widget = source_widget


class GPersonnelCmd(GCmd):
    '''project类命令'''
    flag = TargetFlag.personnel.value
    table_name = 'project_meeting_log'

    def __init__(self, operation: str, _id: str, conn_company_name: str = None, source_widget=None,
                 fields_values: dict = None):
        super(GPersonnelCmd, self).__init__()
        self._id = _id  # company_id
        self.operation = getattr(GOperation, operation).value
        self.conn_company_name = conn_company_name
        self.fields_values = fields_values
        self.source_widget = source_widget


class BroadcastSpace(object):
    '''生成新的广播事件类'''

    def __init__(self, broadcast_ID, broadcast_amount: int = 1):
        self.broadcast_ID = broadcast_ID
        self.broadcast_amount = broadcast_amount
        self.broadcast_sent = 0
        self.broadcast_names = set()

    def initNewBroadcastID(self):
        return self.broadcast_ID.get()

    def argNameToBroadcast(self, names: set):
        '''
        设定被广播者的ID集合
        :param names: 被广播者的ID集合
        :return:
        '''
        self.broadcast_names = names

    '''def argBroadcasted(self, name):
        self.broadcast_sent += 1
        if self.broadcast_sent == self.broadcast_amount:
            del self'''


class AccceptState(object):
    '''状态机，判断是否在接收新的一轮广播，以及广播的内容是否都接收到了
        一次操作触发的广播事件，涉及到多个内容，接收方需要在接收完所有数据后再更新模型和控件
    '''

    def __init__(self, accept_ID=None, accept_names: set = None):
        self.accept_ID = accept_ID
        self.accept_names = accept_names
        self.name_accepted = set()
        self._accept_complete = False
        if accept_names and len(accept_names) <= 1:
            self.acceptComplete()

    def argAccepted(self, name):
        self.name_accepted.add(name)
        if self.name_accepted == self.accept_names:
            self._accept_complete = True

    def acceptComplete(self):
        self._accept_complete = True

    @property
    def accept_complete(self):
        return self._accept_complete


class GeoModel(object):
    '''地理位置分片的模型'''
    _instance = None
    __lock__ = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls.__lock__:
            if not cls._instance:
                cls._instance = super(GeoModel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        from core.Geo import ChinaGeo
        self.geo = ChinaGeo()
        self.file_path_model = workingDir
        self.client_dict_file_path = os.path.join(self.file_path_model.getUserDirectory(), "ClientDict.ini")
        self.locates = []
        self.client_dict = {}
        self.loadUserClientFilter()

    def loadUserClientFilter(self):
        # 当前文件路径
        self.client_dict_file = configparser.ConfigParser()
        self.client_dict_file.read(self.client_dict_file_path, encoding='utf-8')
        self.createClientDict()

    def saveUserClientFilter(self):
        '''保存对用户自定义区域的模型的修改'''
        # to_dump_client_dict = {}
        # for key in self.client_dict.keys():
        #     to_dump_client_dict[key] = json.dumps(self.client_dict[key],)
        # print('self.client_dict', self.client_dict)
        self.serializeClientDict()
        self.client_dict_file['locates'] = self.client_dict
        try:
            with open(self.client_dict_file_path, 'w', encoding='utf-8') as f:
                self.client_dict_file.write(f)
            return True
        except PermissionError as e:
            global_logger.error(e, exc_info=True)
            return False
        pass

    def serializeClientDict(self):
        for key, value in self.client_dict.items():
            value_json = json.dumps(value)
            self.client_dict.update({key: value_json})

    def createClientDict(self):
        '''生成{区域:[city_code]}字典'''
        if not self.client_dict_file.has_section('locates'):
            self.client_dict_file.add_section('locates')
        self.locates = self.client_dict_file.options("locates")  # 重新获取locates
        client_list = []
        for key in self.locates:
            list_str = self.client_dict_file.get("locates", key)
            list_city = json.loads(list_str)
            list_tuple_city = [tuple(city) for city in list_city]
            client_list.append(list_tuple_city)
        worker = zip(self.locates, client_list)
        self.client_dict = dict(worker)  # {区域:[city_code]}

    def addLocate(self, locate: str):
        self.client_dict[locate] = []

    def addCityCode(self, locate: str, city_code: Union[int, str]):
        self.client_dict[locate].append(city_code)

    def getProvinceFromCode(self, code: Union[int, str], country_code=None):
        Code = str(code)
        Province = self.geo.getCountryProvince(country_code=country_code, state_code=Code)
        if Province is not None:
            return self.geo.getName(Province)
        else:
            return None

    def getCityNameFromCode(self, city_code: Union[int, str], country_code='1', province_code=None):
        is_china = self.geo.checkCityCodeChineseVersion(city_code)
        str_code = str(city_code)
        if is_china and len(str_code) == 4:
            province_code = str_code[:2]
            city_code = str_code[2:]
            city_code = str(convertInt(city_code))
        else:
            city_code = str_code
        province = self.geo.getCountryProvince(state_code=province_code, country_code=country_code)
        if province is None:
            return None
        city = self.geo.getCity(province, city_code)
        if city is None:
            return None
        return self.geo.getName(city)

    def getTownFromCode(self, town_code: Union[int, str], country_code='1', province_code=None, city_code=None):
        is_china_old = self.geo.checkTownCodeChineseVersion(town_code)
        str_code = str(town_code)
        if is_china_old and len(str_code) == 6:
            province_code = str_code[:2]
            city_code = str_code[2:4]
            city_code = str(convertInt(city_code))
            town_code = str_code[2:4]
            town_code = str(convertInt(town_code))
        else:
            town_code = str_code
        province = self.geo.getCountryProvince(state_code=province_code, country_code=country_code)
        if province is None:
            return None
        city = self.geo.getCity(province, city_code)
        if city is None:
            return None
        town = self.geo.getTown(city, town_code)
        if town is None:
            return None
        return self.geo.getName(town)

    def getProvinceIndex(self, province_code: Union[int, str]):
        province_code = str(province_code)
        provinceItems = self.getProvinceItems()
        province_codes = [province[0] for province in provinceItems]
        return province_codes.index(province_code)

    def getProvinceItems(self):
        return self.geo.getAllProvinces()

    def getCityIndex(self, city_code, province_code: str = None):
        is_china = self.geo.checkCityCodeChineseVersion(city_code)
        str_code = str(city_code)
        if is_china and len(str_code) == 4:
            province_code = str_code[:2]
            city_code = str_code[2:]
            city_code = str(convertInt(city_code))
        else:
            city_code = str_code
        city_items = self.getCityItems(province_code)
        city_codes = [city[0] for city in city_items]
        try:
            return city_codes.index(city_code)
        except:
            return None

    def getCityItems(self, province_code: Union[int, str]):
        city_items = self.geo.getCities(province_code)
        return city_items

    def getTownIndex(self, town_code: Union[int, str], city_code, province_code: str = None):
        is_china_old = self.geo.checkTownCodeChineseVersion(town_code)
        str_code = str(town_code)
        if is_china_old and len(str_code) == 6:
            province_code = str_code[:2]
            city_code = str_code[2:4]
            city_code = str(convertInt(city_code))
            town_code = str_code[2:4]
            town_code = str(convertInt(town_code))
        else:
            town_code = str_code
        town_items = self.getTownItems(city_code=city_code, province_code=province_code)
        town_codes = [town[0] for town in town_items]
        try:
            return town_codes.index(town_code)
        except:
            return None

    def getTownItems(self, city_code: Union[int, str], province_code: str = None):
        is_china = self.geo.checkCityCodeChineseVersion(city_code)
        str_code = str(city_code)
        if is_china and len(str_code) == 4:
            province_code = str_code[:2]
            city_code = str_code[2:4]
            city_code = str(convertInt(city_code))
        else:
            city_code = str_code
        town_items = self.geo.getTowns(city_code, province_code)
        return town_items


class CompanyGroupModel(object):
    '''公司分组模型'''

    def __init__(self):
        self.file_path_model = workingDir
        self.client_dict_file_path = os.path.join(self.file_path_model.getUserDirectory(), "ClientDict.ini")
        self.groups = []
        self.company_dict = {}
        self.loadUserCompanyGroupFilter()
        # id_company_bounds = CS.getLinesFromTable('clients', conditions={}, columns_required=['_id','short_name'])
        # id_company_bounds.pop()
        # self.id_company_dict = {}
        # for item in id_company_bounds:
        #     self.id_company_dict[item[0]] = item[1]

    def loadUserCompanyGroupFilter(self):
        # 当前文件路径
        self.client_dict_file = configparser.ConfigParser()
        self.client_dict_file.read(self.client_dict_file_path, encoding='utf-8')
        self.createClientDict()

    def createClientDict(self):
        '''生成{区域:[city_code]}字典'''
        if not self.client_dict_file.has_section('groups'):
            self.client_dict_file.add_section('groups')
        self.groups = self.client_dict_file.options("groups")  # 重新获取groups
        company_list = []
        for key in self.groups:
            list_str = self.client_dict_file.get("groups", key)
            list_company = eval(list_str)
            company_list.append(list_company)
        worker = zip(self.groups, company_list)
        self.company_dict = dict(worker)  # {分组:[company_id]}

    def saveCompanyGroupFilter(self):
        '''保存对用户自定义分组的模型的修改'''
        # print('self.client_dict', self.company_dict)
        self.client_dict_file['groups'] = self.company_dict
        try:
            with open(self.client_dict_file_path, 'w', encoding='utf-8') as f:
                self.client_dict_file.write(f)
            return True
        except PermissionError as e:
            global_logger.error(e, exc_info=True)
            return False
        pass

    def addLocate(self, group: str):
        self.company_dict[group] = []

    def addCompanyId(self, group: str, company_id: str):
        self.company_dict[group].append(company_id)

    def getCompanyFromCityCode(self, city_code: str, province_code: str):
        '''返回(_id,short_name), 兼用新旧的行政区划编码方式'''
        conv = convertInt(city_code)
        city_code = str(city_code)
        if province_code is None:
            city_code_long = city_code
            city_code_short = city_code
            pass
        elif re.match(r'^\d{4}$', city_code):
            city_code_long = city_code
            province_code = city_code[:2]
            city_code_short = city_code[2:4]
        elif re.match(r'^\w{1,3}$', city_code) and re.match(r'^\w{2,3}$', province_code):
            city = city_code if len(city_code) == 2 else '0' + city_code
            city_code_short = city_code
            city_code_long = str(province_code) + city
        else:
            raise ValueError('Unexpected city_code "{}".'.format(city_code))
        id_company_binds_part1 = CS.getLinesFromTable('clients', conditions={'city': city_code_long},
                                                      columns_required=['_id', 'short_name'])
        id_company_binds_part2 = CS.getLinesFromTable('clients',
                                                      conditions={'city': city_code_short, 'province': province_code},
                                                      columns_required=['_id', 'short_name'])
        id_company_binds_part1.pop()
        id_company_binds_part2.pop()
        set1 = set(id_company_binds_part1)
        set2 = set(id_company_binds_part2)
        set_ = set1.union(set2)
        return list(set_)

    def getCompanyFromProvinceCode(self, province_code: str):
        id_company_binds = CS.getLinesFromTable('clients', conditions={'province': province_code},
                                                columns_required=['_id', 'short_name'])
        id_company_binds.pop()
        return id_company_binds

    def getCompanyNameFromId(self, _id: str):
        _ids = CS.getLinesFromTable('clients', conditions={'_id': _id}, columns_required=['short_name'])
        _ids.pop()
        name = _ids[0][0]
        return name


if __name__ == '__main__':
    # cls0 = Company()
    # print(cls0.data_fields)

    checkDatabase()
