import datetime
import json
import time
from functools import reduce
from operator import mul
from typing import Union
import jsonschema
from DataCenter import LogType, AccceptState,ToDo
from apps.TodoPanel.Interface import Schema
from apps.TodoPanel.TodoUnitPresenter import TodoUnitPresenter
from apps.TodoPanel.TodoUnitView import TodoUnitView
import ConnSqlite as CS
from core.GlobalListener import global_logger


def bools2binary(bl_0):
    '''convert a sequence of booleans to a binary representation'''
    assert len(bl_0) > 0, 'The sequence bl_0 should not be empty'
    bl_0 = map(str, map(int, bl_0))
    b0 = int(''.join(bl_0), 2)
    return b0
    # for i in range(len(tp_0)):
    #     if tp_0[i] and tp_1[i]:
    #       return True
    # else:
    #     return False

class Box:
    def __init__(self, level:int = 0, father = None, name:str = None):
        self.level = level
        self.name = name
        self.father = father
        self.children:list[Box] = None
        self.elements:list[LogType] = None
        self._flatten = []

    def addChildBox(self, child_box, index: int=-1):
        if self.elements is not None:
            raise Exception('This box node instance is already used as an element container, should not be used as a box container at the same time.')
        if self.children is None:
            self.children = []
        child_box.father = self
        if index == -1:
            self.children.append(child_box)
        else:
            self.children.insert( index,child_box)
        child_box.setLevel(self.level + 1)

    def removeChildBox(self, box, delete = False):
        if not isinstance(box, Box):
            raise ValueError('Expected an instance of %s, got %s instead '%(Box.__class__, box.__class__))
        if box in self.children:
            self.children.remove(box)
        else:
            raise ValueError('Trying to remove a box from a father_box that does not contain it as a child_box.')
        if delete:
            box.deleteSelf()
        else:
            box.level = 0

    def deleteSelf(self): # help GC
        if self.children:
            for box in self.children:
                box.deleteSelf()
        del self

    def addElement(self, element:TodoUnitView, index:int = -1 ):
        if self.children is not None:
            raise Exception('This box node instance is already used as a box container, '
                            'which should not be used as an element container at the same time.')
        if self.elements is None:
            self.elements = []
        element.box = self
        self.elements.insert( index, element)

    def removeElement(self, element:TodoUnitView):
        if not self.elements:
            raise ValueError('This box does not have any elements.')
        if not element in self.elements:
            raise ValueError('This element does not exist in the box.')
        element.box = None
        self.elements.remove(element)

    def broadcastLevelNum(self):
        if self.children:
            for child_box in self.children:
                child_box.level = self.level + 1
                child_box.broadcastLevelNum()

    def setLevel(self,level:int):
        self.level = level
        self.broadcastLevelNum()

    @classmethod
    def getRootBoxName(cls, node):
        if isinstance(node, cls):
            father_node = node.father
        else:
            if hasattr(node, 'box'):
                father_node = node.box
            else:
                raise Exception('This node does not have a father node or box node.')
        while True:
            if father_node.level == 0:
                return father_node.name
            father_node = father_node.father

    @classmethod
    def flatten(cls, box, flatten_container:list):
        if box.elements:
            flatten_container += box.elements
        if box.children:
            for child_box in box.children:
                box.flatten(child_box, flatten_container)
        return flatten_container


class GridModel:
    def __init__(self):
        self.n_lane = 0
        self.id_unit_map = {}

    def set_lanes(self, lane_names: list):
        self.lane_names = lane_names
        self.lanes = [Box(name=lane_name) for lane_name in lane_names]

    def clear(self):
        self.lanes.clear()
        self.lane_names.clear()


    def add_unit(self, id: str, unit_model, box: Box, i_pos: int):
        '''
        id: the id of the unit
        unit: unit should have its widget
        box: index of the lane the unit is expected to be put in
        i_pos: the index the unit in the lane
        Return: None
        '''
        if i_pos > 0:
            if i_pos > len(box.elements):
                raise IndexError('Index i_pos is out of range of box.elements')
            elif i_pos == len(box.elements):
                next_unit_model = None
            else:
                next_unit_model = box.elements[i_pos]
            former_unit_model = box.elements[i_pos - 1]
        else:
            former_unit_model = None
            next_unit_model = box.elements[0]

        self.id_unit_map.update({id: {'unit': unit_model,
                                      'former_unit': former_unit_model,
                                      'next_unit': next_unit_model,
                                      'box': box,
                                      'i_pos': i_pos}})
        if next_unit_model:
            self.id_unit_map[next_unit_model._id]['former_unit'] = unit_model
        if former_unit_model:
            self.id_unit_map[former_unit_model._id]['next_unit'] = unit_model
        box.addElement(unit_model, i_pos)

        while True:
            if not next_unit_model:
                break
            next_id = next_unit_model._id
            self.id_unit_map[next_id]['i_pos'] += 1
            next_unit_model = self.id_unit_map[next_id]['next_unit']

    def remove_unit(self, id: str):
        if not id in self.id_unit_map:
            print('the id does not exist in the current map')
            return
        box = self.id_unit_map[id]['box']
        i_pos = self.id_unit_map[id]['i_pos']

        if i_pos == 0:
            former_unit_model = None
        elif i_pos >= len(box.elements):
            raise IndexError('Index i_pos is out of range of list "lane"')
        else:
            former_unit_model = box.elements[i_pos - 1]
        if i_pos == len(box.elements) - 1:
            next_unit_model = None
        else:
            next_unit_model = box.elements[i_pos]

        if former_unit_model:
            if next_unit_model:
                self.id_unit_map[former_unit_model._id]['next_unit'] = next_unit_model
                self.id_unit_map[next_unit_model._id]['former_unit'] = former_unit_model
            else:
                self.id_unit_map[former_unit_model._id]['next_unit'] = None
        else:
            if next_unit_model:
                self.id_unit_map[next_unit_model._id]['former_unit'] = None
            else:
                pass

        while True:
            if not next_unit_model:
                break
            next_id = next_unit_model._id
            self.id_unit_map[next_id]['i_pos'] += 1
            next_unit_model = self.id_unit_map[next_id]['next_unit']

    def get_unit(self, id: str):
        return self.id_unit_map[id]['unit']

    def get_unit_coord(self, id: str):
        return self.id_unit_map[id]['i_lane'], self.id_unit_map[id]['i_pos']

    # def setup_unit_widget(self, id:str):
    #     unit = self.id_unit_map[id]['unit']
    #     unit.setWidget()
    #
    # def get_unit_wigdet(self, id:str):
    #     unit = self.id_unit_map[id]['unit']
    #     if not unit.widget:
    #         unit.setWidget()
    #     return unit.widget

    def buildLanesFromDict(self, cat_map:dict):
        self.lanes = [self.buildBoxFromDict(key, value) for key, value in cat_map.items()]

    def buildBoxFromDict(self, key, cat_map:dict):
        box = Box(name=key)
        if isinstance(cat_map, dict):
            cat_map.pop('n_model_prior_show', None)
            for key, log in cat_map.items():
                box.addChildBox(self.buildBoxFromDict(key, log))
        else:
            for unit in cat_map:
                box.addElement(unit)
        return box

    def yield_all_models_to_json(self):
        data = [ ]
        for box in self.lanes:
            tmp = []
            Box.flatten(box,tmp)
            data += tmp
        for element in data:
            model_data = element.getModelAttribData()
            data.append(model_data)
        return json.dumps(data)


class TodoPanelPresenter:
    ARRANGE_WEIGHT = 0
    ARRANGE_COMPANY = 1
    ARRANGE_PROJECT = 2
    ARRANGE_OFFI_TYPE = 0
    COMPANY_KEY_ALIAS_FIELD = ('conn_company_id', 'conn_company_name') # (field_name_of_database, field_to_show_user)
    JOBTYPE_KEY_ALIAS_FIELD = ('officejob_type', None)
    PROJECT_KEY_ALIAS_FIELD = ('conn_project_name', 'conn_project_name')

    def __init__(self,parent=None):
        super(TodoPanelPresenter, self).__init__()
        self.parent = parent
        # self.parent_widget = parent_widget
        self.units = []
        self.units_for_render = [] ## units_for_render来自于units的浅拷贝，并对元素进行重组值。
        self.todo_id_map = {} # todo_id_map记录的是ToDoUnit在tableWidget中的坐标，相当于是对于其在todo_view_matrix中的坐标进行了转置
        self.GridModel = GridModel()
        self.accept_state = AccceptState()
        self.todoUnitPresentor = TodoUnitPresenter(self)
        self.listener = self.parent.listener
        self.view = None
        # self.check_status = self.view.tab_bar.getCheckStatus()
        # self.todo_view_matrix = None
        # self.todo_view_header_array = []
        self.arrange_strategy = self.ARRANGE_WEIGHT
        self.drag_drop_enabled = True

        self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]

        self.bound_widget = None
        self.bound_widget_header = None
    def set_arrange_strategy(self, index):
        self.arrange_strategy = index
        if self.arrange_strategy == self.ARRANGE_COMPANY:
            self.leveled_key_alias_fields = [self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD,
                                             self.JOBTYPE_KEY_ALIAS_FIELD]
        elif self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD,
                                             self.PROJECT_KEY_ALIAS_FIELD]
        else:
            self.leveled_key_alias_fields = [self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD,
                                             self.COMPANY_KEY_ALIAS_FIELD]

    def setDataModel(self, condition: dict=None):
        self.units.clear() # self.units就是最后准备渲染的全部单元
        self.units_for_render.clear()
        self.units_for_render = self.units

        get_pending = self.check_status['mission_range'][0] # to_do.pending_date - today
        timespace_distance_wanted = self.check_status['timespace_distance_checked']
        mask = self.check_status['project_check_status']
        mask_b = bools2binary(mask) # 将系列bool值转换成二进制掩码，用于筛选comboBox所选的类型 # project
        condition = self.handleSearchCondition(condition)

        todo_fields = ['_id', 'conn_task_id', 'todo_desc', 'status','on_pending', 'pending_till_date', 'is_critical',
                       'conclusion_desc', 'waiting_desc', 'create_time', 'destroyed', 'inter_order_weight',
                       'timespace_distance', 'conn_project_id', 'conn_company_id', 'officejob_type']
        project_fields = ['product', 'client', 'client_id', 'order_tobe', 'weight', 'in_act', 'clear_chance',
                          'highlight']
        company_fields = ['short_name']
        task_fields = ['officejob_type']


        todo_logs = CS.getLinesFromTable('todo_log', conditions=condition, order=['inter_order_weight'])

        # combined_todo_logs = CS.triple_innerJoin_withList_getLines(
        #     'todo_log', 'proj_list', 'clients',
        #     target_colums_a=todo_fields, target_colunms_b=project_fields, target_colunms_c=company_fields,
        #     joint_key_a_b=('conn_project_id', '_id'), joint_key_a_c=('conn_company_id', '_id'),
        #     condition_a=condition, method='left join')
        keys = todo_logs.pop()

        # load extra information about todo_units
        index_todo_id = keys.index('_id')
        index_project_id = keys.index('conn_project_id')
        index_company_id = keys.index('conn_company_id')
        index_task_id = keys.index('conn_task_id')
        dict_todo_project = {}
        dict_todo_company = {}
        dict_todo_task = {}

        for log in todo_logs:
            if conn_project_id := log[index_project_id] :
                dict_todo_project[log[index_todo_id]] = conn_project_id
            if conn_company_id := log[index_company_id]:
                dict_todo_company[log[index_todo_id]] = conn_company_id
            if conn_task_id := log[index_task_id] :
                dict_todo_task[log[index_todo_id]] = conn_task_id

        project_ids = list(dict_todo_project.values())
        company_ids = list(dict_todo_company.values())
        task_ids = list(dict_todo_task.values())

        project_fields = ['_id','product', 'client', 'client_id', 'order_tobe', 'weight', 'in_act',
                          'is_deal', 'clear_chance', 'highlight']
        project_logs  = CS.getLinesFromTable('proj_list', conditions = {'_id': project_ids},
                                             columns_required= project_fields)
        project_dict = {}

        for project_log in project_logs:
            project_dict[project_log[0]] = project_log

        company_fields = ['_id', 'short_name']
        company_logs = CS.getLinesFromTable('clients', conditions = {'_id': company_ids}, columns_required=company_fields)
        company_dict = {}
        for company_log in company_logs:
            company_dict[company_log[0]] = company_log

        task_fields = ['_id', 'officejob_type']
        task_logs = CS.getLinesFromTable('tasks', {'_id': task_ids}, columns_required=task_fields)
        task_dict = {}
        for task_log in task_logs:
            task_dict[task_log[0]] = task_log

        # indexes = range(len(keys))
        # 根据get_pending 和延期到的日期来确定要保留的任务
        j = 0
        before_create_units = time.perf_counter()
        for i, log in enumerate(todo_logs):
            todo_id = log[index_todo_id]
            pending_till_date = log[keys.index('pending_till_date')]
            if get_pending == 0:# 获取到期的任务
                if not pending_till_date:# 不存在延期，保留
                    pass
                else:
                    pending_days = (datetime.datetime.strptime(str(pending_till_date), '%Y-%m-%d').date()\
                                - datetime.datetime.today().date()).days
                    if pending_days > 0: # 还未到期，跳过
                        continue
                    else:# 已到期，保留
                        pass
            elif get_pending == 1:# 获取未到期的任务
                if not pending_till_date:# 不存在延期
                    continue
                else:
                    pending_days = (datetime.datetime.strptime(str(pending_till_date), '%Y-%m-%d').date()\
                                - datetime.datetime.today().date()).days
                    if pending_days > 0: # 还未到期
                        pass
                    else:# # 已到期，跳过
                        continue
            elif get_pending == 2:# 获取全部任务
                pass
            before_create_unit = time.perf_counter()

            todo_model = self.todoUnitPresentor.makeModel(todo_id, keys, log)
            # todo_unit = self.todoUnitPresentor.views[todo_id]
            todo_unit_data = {}  # dict(zip(keys, log))
            # todo_unit = TodoUnitView(parent=self.view.tab_bar, parent_view = self.view.tab_bar)

            # project info
            if todo_id in dict_todo_project.keys():
                conn_project_id = dict_todo_project[todo_id]
                project_log = project_dict[conn_project_id]
                project = dict(zip(project_fields, project_log))

                todo_unit_data['conn_project_name'] = project['product']
                todo_unit_data['conn_company_name'] = project['client']
                todo_unit_data['conn_company_id ']= project['client_id']
                todo_unit_data['conn_project_order_tobe'] = project['order_tobe']
                todo_unit_data['conn_project_weight'] = project['weight']
                todo_unit_data['conn_project_in_act'] = project['in_act']
                todo_unit_data['conn_project_clear_chance'] = project['clear_chance']
                todo_unit_data['conn_project_highlight'] = project['highlight']
                todo_unit_data['conn_project_is_deal'] = project['is_deal']

            # company info
            if todo_id in dict_todo_company and todo_model.conn_company_name is None:
                conn_company_id = dict_todo_company[todo_id]
                company_log = company_dict[conn_company_id]
                todo_unit_data['conn_company_name']= company_log[1]

            # task info
            if todo_id in dict_todo_task.keys():
                conn_task_id = dict_todo_task[todo_id]
                task_log = task_dict.get(conn_task_id, None)
                if task_log is not None:
                    todo_unit_data['conn_task_cat'] = task_log[1]

            if todo_model.timespace_distance not in timespace_distance_wanted:
                continue


            if not mask:
                pass
            elif mask and reduce(mul, mask) == 1:
                pass
            elif not todo_id in dict_todo_project:
                continue
            else:
                maskee = (todo_unit_data['conn_project_in_act'] ,
                          todo_unit_data['conn_project_order_tobe'],
                          todo_unit_data['conn_project_clear_chance'],
                          todo_unit_data['conn_project_highlight'],
                          todo_unit_data['conn_project_in_act'],
                          not (todo_unit_data['conn_project_in_act'] or
                               todo_unit_data['conn_project_order_tobe'] or
                               todo_unit_data['conn_project_clear_chance'] or
                               todo_unit_data['conn_project_highlight'] or
                               todo_unit_data['conn_project_in_act'] or
                               not bool(todo_model.conn_project_id)),
                          not bool(todo_model.conn_project_id))
                maskee = bools2binary(maskee)

                if not mask_b & maskee: # if only one positional condition matches
                    continue
            j += 1
            before_todo_unitWidget = time.perf_counter()
            todo_model.data.update(todo_unit_data)
            # todo_model.setWidget()
            after_todo_unitWidget = time.perf_counter()
            # print('time_for_render_todowidget:', after_todo_unitWidget - before_todo_unitWidget)
            self.units.append(todo_model)
        after_create_units = time.perf_counter()

    def setUnitsForRender(self):
        if self.units_for_render == self.units:
            return

    def sortUnits(self):
        self.units.sort(key= lambda unit_model: unit_model.conn_project_weight + unit_model.is_critical * 5 if \
                unit_model.conn_project_weight else unit_model.is_critical * 5, reverse=True)
        if self.units_for_render is self.units:
            return
        self.units_for_render.sort(key= lambda unit_model: unit_model.conn_project_weight + unit_model.is_critical * 5 if \
                unit_model.conn_project_weight else unit_model.is_critical * 5, reverse=True)

    def arrangeUnitsIntoLanes(self) -> dict:
        '''
        todo卡片的组织策略，具有默认排序策略和指定排序策略这两级
        默认排序策略是基础，指定排序策略则将其中某项策略的优先级提高。
        在不同列间，存在列长度相差过大的情况，可适当进行合并，使得显示结果尽可能接近矩形。
        0: 权重优先
        1：客户优先
        2：项目优先
        3: 类型优先
        4: 主线支线--需明确主线和支线的定义
        '''
        # self.arrange_strategy = self.tab_bar.comboBox_order.currentIndex()

        self.sortUnits() # 使用weight做整体初步排序

        cat_map = self.classify(self.units_for_render, self.leveled_key_alias_fields)

        return cat_map

    @classmethod
    def classify(cls, source_model_list: list[ToDo], leveled_key_fields: list[tuple])->dict:
        '''Recursively classify todo_units according to the assigned key_fields from leveled_key_fields.
        Return a dict in the form of {first_level_key_field: {second_level_key_field:{...:[TodoUnitView]}}
        The relative order of items shall be passed to items in every leaf list'''
        cat_map = {}
        n_model_prior_show = 0
        for i, unit_model in enumerate(source_model_list):
            if unit_model.isPriority():
                n_model_prior_show += 1
            key_name = unit_model.__getattribute__(leveled_key_fields[0][0])
            if key_name:
                if key_name in cat_map:
                    cat_map[key_name].append(unit_model)
                else:
                    cat_map[key_name] = [unit_model]
            else:
                if '__' in cat_map:
                    cat_map['__'].append(unit_model)
                else:
                    cat_map['__'] = [unit_model]

        if len(leveled_key_fields) > 1:
            next_leveled_key_fields = leveled_key_fields[1:]
            for key, model_list in cat_map.items():
                value = cls.classify(model_list, next_leveled_key_fields)
                cat_map.update({key: value})

        cat_map['n_model_prior_show'] = n_model_prior_show
        return cat_map

    def handleSettingChange(self, panel_check_status):
        check_status = json.loads(panel_check_status)
        jsonschema.validate(check_status, Schema.todo_panel_checkstatus)
        self.set_arrange_strategy(check_status.pop('arrange_strategy'))
        self.check_status = check_status
        condition = self.parent.overall_project_search(2)  # todo: 不适用基于project的搜索，否则无法加载未关联项目的
        self.setDataModel(condition)
        self.makeTodoGridModel()
        return self.getModelGroups(with_model_data=True)

    def handleSearchCondition(self, condition: dict):
        if not condition:
            project_ids = []
        else:
            project_id_get = CS.getLinesFromTable('proj_list',conditions=condition,columns_required=['_id'])
            project_id_get.pop()
            project_ids = [item[0] for item in project_id_get]
        condition = {}
        if project_ids:
            condition['conn_project_id'] = project_ids
        # self.check_status =
        get_pending = self.check_status['mission_range'][0]#to_do.pending_date-today
        get_destroyed = self.check_status['mission_range'][1]#to_do类属性
        get_progress = self.check_status['progress_check_status']
        get_critical = self.check_status['urgence_range'][0]#to_do类属性
        get_normal = self.check_status['urgence_range'][1]#to_do类属性
        # mask = self.check_status[2]#掩码用于筛选comboBox所选的类型#project
        #对is_critical的筛选
        if get_critical ^ get_normal:
            if get_critical:
                condition['is_critical'] = True
            else:
                condition['is_critical'] = False
        #对destroyed删选
        if get_destroyed:
            condition['destroyed'] = True
        else:
            condition['destroyed'] = False
        # 对status筛选
        progress_checked = []
        for i, bo in enumerate(get_progress):#status包括0,1,2三种状态分别代表未进行，进行中，已完成
            if bo:
                progress_checked.append(i)
        if len(progress_checked) == 0 or len(progress_checked) == 3:
            pass
        else:
            condition['status'] = progress_checked
        return condition

    def makeTodoGridModel(self) -> (list[list],list[str]):
        '''
        :return: (headers of columns, colums)
        '''
        cat_map = self.arrangeUnitsIntoLanes()
        n = cat_map.pop('n_model_prior_show', None)
        header_col_pairs = list(cat_map.items())
        self.GridModel = GridModel()
        if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            header_col_pairs.sort(key=lambda item: item[0]) # 直接
            self.GridModel.lanes = [self.GridModel.buildBoxFromDict(header, col) for header, col in header_col_pairs]
            self.GridModel.lane_names = [header for header, col in header_col_pairs]

        else:
            n_all_to_show = 0
            for header, col in header_col_pairs:
                len_col = max(col['n_model_prior_show'], 1)
                n_all_to_show += len_col
            header_col_pairs.sort(key=lambda item: item[1]['n_model_prior_show'])
            n_cat = len(header_col_pairs)
            max_len_col = max(header_col_pairs[-1][1]['n_model_prior_show'], n_all_to_show**0.55) # When the magic number is between 0.5 and 1.0, it tends add length to vertical scroll.
            nest_threshold_n_col = 5
            allowed_min_len_col = 5
            max_len_col = max(max_len_col, allowed_min_len_col) # todo: para to be extracted
            # 构造todo_view布局
            todo_view_headers = []

            if n_cat <= nest_threshold_n_col:
                self.GridModel.lanes = [self.GridModel.buildBoxFromDict(header, col) for header, col in header_col_pairs]
                self.GridModel.lane_names = []
                for i, box in enumerate(self.GridModel.lanes):
                    header = header_col_pairs[i][0]
                    if self.leveled_key_alias_fields[0][1]:
                        tmp_box = box
                        while tmp_box.children is not None :
                            tmp_box = tmp_box.children[0]
                        tmp_unit = tmp_box.elements[0]
                        header_alias = tmp_unit.data[self.leveled_key_alias_fields[0][1]]
                    else:
                        header_alias = header
                    self.GridModel.lane_names.append([header_alias])
            else:
                self.GridModel.lanes= [Box()]
                self.GridModel.lane_names = [[]]
                len_counter = 0

                for header, col in header_col_pairs:
                    len_col = max(col.pop('n_model_prior_show'), 1)
                    if len_counter + len_col > max_len_col or len_col >= max_len_col / 2:
                        self.GridModel.lanes.append(Box(name=header))
                        self.GridModel.lanes[-1].addChildBox(self.GridModel.buildBoxFromDict(header, col))
                        self.GridModel.lane_names.append([])
                        len_counter = 0


                    else:
                        self.GridModel.lanes[-1].addChildBox(self.GridModel.buildBoxFromDict(header, col))
                        pass

                    col_list = self.extractDictIntoList(col)
                    header_alias = col_list[0].data[self.leveled_key_alias_fields[0][1]] if \
                        self.leveled_key_alias_fields[0][1] else header
                    header_alias = header_alias if header_alias is not None else '__'
                    print(header_alias, col)
                    self.GridModel.lane_names[-1].append(header_alias)
                    len_counter += len_col
            self.GridModel.lanes.reverse()
            self.GridModel.lane_names.reverse()
            self.GridModel.lane_names = [ ' | '.join(collective_name) for  collective_name in self.GridModel.lane_names]
        # self.todo_view_matrix = todo_view_matrix
        # return todo_view_matrix, todo_view_headers


    # def resetUnitWidgets(self, start:int = 0, stop:int = None):
    #     if not stop:
    #         stop = len(self.units_for_render)
    #     else:
    #         stop += 1
    #     for i in range(start, stop):
    #         self.units_for_render[i].setWidget()

    @classmethod
    def extractDictIntoList(cls, cat_map:dict):
        '''
        将dict形式的树转变为list形式
        cat_map: 字典形式的树状分类
        '''
        lst = []
        cat_map.pop('n_model_prior_show', None)
        for key, value in cat_map.items():
            if isinstance(value, dict):
                lst.extend(cls.extractDictIntoList(value))
            else:
                lst.extend(value)
        return lst

    @classmethod
    def extractDictIntoGroups(cls, cat_map:dict, depth:int = 2):
        '''depth: the max depth of the list-tree to return,'''
        lst = []
        cat_map.pop('n_model',None)
        depth -= 1
        for key, value in cat_map.items():
            if depth <= 1 or not isinstance(value, dict):
                lst.append(cls.extractDictIntoList(value))
            else:
                lst.append(cls.extractDictIntoGroups(value, depth))
        return lst

    def uniteByTodoType(self, type:str):
        """根据待办事项的类型进行选择"""
        tmp_units = self.units.copy()
        for i in reversed(range(len(tmp_units))):
            if tmp_units[i].model.officejob_type:
                if tmp_units[i].model.officejob_type != type:
                    tmp_units.pop(i)
                else:
                    pass
            elif tmp_units[i].model.conn_task_id:
                if tmp_units[i].model.conn_task_cat != type:
                    tmp_units.pop(i)
                else:
                    pass
            else:
                tmp_units.pop(i)
        self.units_for_render = tmp_units
        del tmp_units
        if not self.units_for_render:
            return
        self.makeTodoGridModel()
        json_group_info = self.getModelGroups()
        self.view.acceptRefresh(json_group_info)

    def getModelGroups(self, with_model_data= False):
        ''''''
        lane_names = self.GridModel.lane_names
        # lanes = {lane_name:{} for lane_name in lane_names}
        model_data = []
        lst = []
        # hidden_marks = {}
        for box in self.GridModel.lanes:
            lane = []
            for children in box.children:
                tmp_models = []
                tmp_id_hidden = []
                Box.flatten(children, tmp_models)
                if len(tmp_models) == 0:
                    continue
                for model in tmp_models:
                    if model.isPriority():
                        tmp_id_hidden.append([model._id, False])
                    else:
                        tmp_id_hidden.append([model._id, True])
                    tmp_id_hidden[0][1] = False
                    if with_model_data:
                        model_data_single = model.getModelAttribData()
                        model_data_single.pop('box')
                        model_data.append(model_data_single)
                lane.append(tmp_id_hidden)
            # lanes
            lst.append(lane)

        lanes = {lane_name: lane for lane_name, lane in zip(lane_names, lst)}
        return json.dumps({'group_info': lanes, 'model_data':model_data})

    def getModelData(self):
        data = self.GridModel.yield_all_models_to_json()
        return data

    def setUI(self,  view, parent_widget=None):
        self.view = view
        self.view.setupUI(parent_widget)
        pass

    def Accept(self, cmd):
        if cmd.broadcast_space is None:
            #如果收到的广播命令没有绑定广播域，则将接收状态重置，并设定到接收完成状态
            self.accept_state.__init__()
            self.accept_state.acceptComplete()
        elif self.accept_state.accept_ID != cmd.broadcast_space.broadcast_ID:#接收到了新的广播域
            #重置接收状态
            self.accept_state.__init__(cmd.broadcast_space.broadcast_ID, cmd.broadcast_space.broadcast_names)
            self.accept_state.argAccepted(cmd._id)
        else:
            self.accept_state.argAccepted(cmd._id)

        # global_logger.debug('todo_view accepted')
        target_flag = cmd.flag
        if target_flag  == 1:#project
           return
        elif target_flag == 2:#task
            self.acceptTaskCmd(cmd)
        else:
            return

    def acceptTaskCmd(self,cmd):
        pass
        # global_logger.debug('Todo accepted task')
        # # client_name = cmd.conn_company_name
        # conn_task_id = cmd._id
        # source_widget = cmd.source_widget
        # if source_widget is self.view.tab_bar:
        #     return
        # # 查找被修改的todo_unit的位置
        #
        # index_in_units = None
        # index_in_units_for_render = None
        # for k, todo_model in enumerate(self.units) :
        #     if conn_task_id == todo_model.conn_task_id :
        #         index_in_units = k
        #         break
        # else:
        #     return
        # for i, todo_model in enumerate(self.units_for_render):
        #     if conn_task_id == todo_model.conn_task_id:
        #         index_in_units_for_render = i
        #         break
        # else:
        #     pass
        #
        # if cmd.operation == 4:  # delete
        #     if not index_in_units_for_render is None:# 如果操作是删除，先单独对units_for_render列表执行pop()
        #         self.units_for_render.pop(index_in_units_for_render)
        #     self.units.pop(index_in_units)
        #     for i, todo_model in enumerate(self.units):
        #         todo_model.inter_order_weight = i + 1
        #     if self.accept_state.accept_complete:
        #         self.makeTodoGridModel()
        # elif cmd.operation == 1:  # update
        #     todo_model = self.units[index_in_units]
        #     if 'task_desc' in cmd.fields_values.keys():
        #         todo_model.conn_task_desc = cmd.fields_values['task_desc']
        #         todo_model.todo_desc = cmd.fields_values['task_desc']
        #         todo_model.conclusion_desc = cmd.fields_values['update_desc_list']
        #     if 'is_critical' in cmd.fields_values.keys():
        #         todo_model.is_critical = cmd.fields_values['is_critical']
        #     if 'officejob_type' in cmd.fields_values.keys():
        #         todo_model.officejob_type = cmd.fields_values['officejob_type']
        #
        #     if self.accept_state.accept_complete and not index_in_units_for_render is None:
        #         coord = self.todo_id_map[self.units_for_render[index_in_units_for_render]._id]


    def handleShowExternalModel(self, model_name, model_id):
        if model_name == 'project':
            self.parent.showProjectPerspective(model_id)
        elif model_name == 'clients':
            self.parent.displayCompanyEditor(client_id=model_id)

    def handleDeleteModel(self, todo_id):
        self.GridModel.remove_unit(todo_id)
        json_group_info = self.getModelGroups()
        self.view.acceptRefresh(json_group_info)

    def handleAddModel(self, ):
        pass

    def resetWeight(self, start = 0, stop=None):
        if not stop:
            stop = len(self.units_for_render)
        else:
            stop += 1
        for i in range(start, stop):
            unit = self.units_for_render[i]
            unit.model.inter_order_weight = i+1
            unit.model.saveBasicData()

    def removeUnitsFromCache(self,_id:Union[list[str],str]):
        if isinstance(_id,str):
            ids = [_id]
        else:
            ids = _id

        for i in reversed(range(len(self.units))):
            unit = self.units[i]
            if unit.model._id in ids:
                self.units.pop(i)
                self.todo_id_map.pop(unit.model._id, None)

                self.todoUnitPresentor.removeModel(_id)
                self.GridModel.remove_unit(_id)


        if self.units_for_render == self.units:
            return
        for i in reversed(range(len(self.units_for_render))):
            unit = self.units_for_render[i]
            if unit.model._id in ids:
                self.units_for_render.pop(i)

    def replaceUnit(self, todo_id:str, new_todo_unit):

        for i in reversed(range(len(self.units))):
            unit = self.units[i]
            if unit.model._id == todo_id:
                self.units.pop(i)
                self.units.insert(i, new_todo_unit)

        if self.units_for_render is self.units:
            return

        for i in reversed(range(len(self.units_for_render))):
            unit = self.units_for_render[i]
            if unit.model._id == todo_id:
                self.units_for_render.pop(i)
                self.units_for_render.insert(i, new_todo_unit)
