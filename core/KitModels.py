
import shutil, hashlib
import sys, os, json
from FilePathInit import userDir
import time
from abc import ABCMeta, abstractmethod
from PyQt5 import QtWidgets
from xpinyin import Pinyin
import ConnSqlite as CS
from typing import Callable,Any
from enum import Enum
from ID_Generate import Snow


def getCurrentTime():
    return time.strftime("%Y-%m-%d %H:%M:%S")


class ItemTypeCreateFactory(object):
    _instance = None
    item_type_create_function : dict[str, Callable[..., Any]] = {}
    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        return super(ItemTypeCreateFactory, cls).__new__(cls)

    def register(self, item_type:str, creation_function:Callable) -> None:
        self.item_type_create_function[item_type] = creation_function

    def unregister(self, item_type:str) ->None:
        self.item_type_create_function.pop(item_type)

    def create(self, father_node, item_type:str):
        create_function = self.item_type_create_function[item_type]
        return create_function.asChild(father_node=father_node)

def convert_date_log_json(json_text: str):
        '''convert json serialized list in the format of [{'date':xxx, 'log_desc':xxx}] into text for textEdit exibhition'''
        if not json_text:
            return ''
        try:
            list_data = json.loads(json_text)
            log_list = []
            for log in list_data:
                log_list.append(log['date'] + ':')
                log_list.append(log['log_desc'])
            log_text = '<br />-->'.join(log_list)
        except ValueError:
            log_text = json_text
        return log_text


class ProductCat(Enum):
    cmo =  'CMO服务'
    API = '原料药'
    excipient = '辅料'
    rld = '参比制剂'


class AbstractDataObject(object):
    '''根据使用的表的名称来确定类的基本字段，并包含保存基本字段的方法，并且'''
    table_name = None
    # face表示用于对用户显示的名称, 在子类中仅赋值其中一项

    def __init__(self, _id = None):
        self.data_fields = None
        self._id = _id
        self.basic_data_load_success = False
        self.initDataFields()

    def redefined_super(self, cls, obj):
        # 重定义的super()函数
        current_members = self.get_current_members()
        super(cls, obj).__init__()
        self.add_current_member_to_data_fields(current_members)

    def saveFieldsUpdate(self, fields: list):
        new_data = {}
        for key in fields:
            new_data[key] = getattr(self, key)
        CS.updateSqliteCells(table_name=self.table_name, conditions={'_id': self._id},
                             update_fields=new_data)

    def saveFieldsToDB(self, fields:list , values:list):
        if not self.table_name:
            raise ValueError('field "table_name" not assigned, please assign the target database table name.')
        CS.upsertSqlite(self.table_name , fields , values)

    def initDataFields(self):
        db_fields = CS.getTableFields(self.table_name)
        self.data_fields = set(db_fields)

    def saveBasicData(self):
        """保存该类的基本字段，不包括关联的类实例的字段内容"""
        fields = []
        values = []
        for field in self.data_fields:
            if hasattr(self, field):
                fields.append(field)
                values.append(getattr(self, field))
        self.saveFieldsToDB(fields, values)

    def add_current_member_to_data_fields(self, members):
        for name in members:
            # if not callable(getattr(cls, name)) and not name.startswith("__"):
            self.data_fields.add(name)

    def assign_data(self,keys,values):
        for i, key in enumerate(keys):
            if hasattr(self, key):
                setattr(self,key,values[i])

    def delete_by_id(self, _id:str):
        CS.deleteLineFromTable(self.table_name, {'_id':_id})

    @abstractmethod
    def setFace(self):
        pass

    def load_basic_data(self, _id: str = None, order: list=None):
        """加载对应类实例的基本字段，不包含关联的类"""

        if not _id:
            _id = self._id
        if not _id:
            raise ValueError('attribute "_id" not assigned')
        data = CS.getLinesFromTable(table_name=self.table_name, conditions={'_id': _id}, order=order)

        keys = data.pop()
        if not data:
            self.basic_data_load_success = False
            return
        values = data[0]

        self.assign_data(keys, values)
        self.basic_data_load_success = True
        self.setFace()

    def get_current_members(self):
        return self.__dict__.keys()


class DataObject(AbstractDataObject):
    ''''''
    face_name = None# 用于构建文件路径的名字
    face_field = None
    idx = None # 生成id的前缀
    _id_generator = None
    def __new__(cls, *args, **kwargs):
        if cls.idx and not cls._id_generator:
            cls._id_generator = Snow(idx=cls.idx)
        return super(DataObject, cls).__new__(cls)

    def __init__(self, face_field:str=None):
        super(DataObject, self).__init__()
        self.create_time = None
        self.update_time = None
        self.father_node = None # 创建此实例的父节点
        if face_field :
            self.face_field = face_field

    def __str__(self):
        return self.face_name

    @classmethod
    def asChildNode(cls, *args, **kwargs):
        '''类的实例化方法，将类创建为其他实例的子节点'''
        # print('args:', args, 'kwargs:', kwargs)
        # print('child_node_is', cls)
        vars = cls.__init__.__code__.co_varnames
        # vars = vars[1:]
        # print(vars)
        try:
            father_node = kwargs.pop('father_node')
        except KeyError as e:
            raise KeyError('No father node assigned.')
        keys = set(kwargs.keys())
        for k in keys:
            if k in vars:
                pass
            else:
                raise KeyError("Unexpected keyword argument %s" % (k))
        _class = father_node.__class__
        if not issubclass(_class, DataObject):
            raise ValueError("father_node must be a subclass of <class 'DataObject'>, got {} instead.".format(_class))
        # print('args:',args,'kwargs:', kwargs)
        instance = cls(*args, **kwargs)
        # print('instance created')
        instance.__setattr__('father_node', father_node)
        return instance

    @classmethod
    def get_new_id(cls):
        return cls._id_generator.get()

    @classmethod
    def serializeModel(cls, model):
        data = {}
        # _dict = model.__dict__
        if not model:
            return data
        for key, value in model.__dict__.items():
            if key == 'father_node':
                data[key] = value.__str__()
            elif not isinstance(value, (DataObject,AbstractArray)):
                if isinstance(value, (list, tuple)):
                    data[key] = [cls.serializedata(item) for item in value]
                elif isinstance(value,dict):
                    data[key] = {key:value.__str__() if key =='father_node' else cls.serializedata(value) for key, value in value.items()}
                else:
                    data[key] = value
            else:
                data[key] = cls.serializeModel(value)
        return data

    @classmethod
    def serializedata(cls, data):
        if isinstance(data,(DataObject,AbstractArray)):
            return cls.serializeModel(data)
        elif isinstance(data, (list, tuple)):
            return [cls.serializedata(item) for item in data]
        elif isinstance(data, dict):
            return {key: value.__str__() if key =='father_node' else cls.serializedata(value) for key, value in data.items()}
        else:
            return data

    def serialize(self):
        return self.serializeModel(self)

    def assign_new_id(self):
        self._id = self._id_generator.get()

    def setFace(self):
        if self.face_field and self.__getattribute__(self.face_field):
            self.__setattr__('face_name', self.__getattribute__(self.face_field))
        elif self.face_name:
            pass
        else:
            pass

    def setTableName(self, name:str):
        self.table_name = name

    def updateFieldValueAndDB(self, field:str, value:str):
        '''更新类实例的单个属性值，并将其保存到数据库'''
        if not self.table_name:
            raise ValueError('field "table_name" not assigned, please assign the target database table name.')
        if hasattr(self, field):
            setattr(self, field, value)
            self.saveFieldsToDB([field],[value])
        else:
            raise ValueError('No such field named %s.'%field)


class LogType(DataObject):
    '''DataObject object with only basic database fields, thus no fields to be assigned with <DataObject> instances'''
    table_name = None
    def __init__(self, _id:str = None):
        super(LogType, self).__init__()
        self._id = None
        self.create_time = None
        self.update_time = None
        #将已有字段的名称保存成集合
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and \
        #                      not attr.startswith("__") and not isinstance(getattr(self, attr), list)]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.redefined_super(LogType, self)
        # self.trimDataFields()
        pass

    # def trimDataFields(self):
    #     self.data_fields.discard('data_fields')
    #     self.data_fields.discard('table_name')
    def saveUpdate(self):
        '''增加或更新记录'''
        self.saveBasicData()



    def saveByInsert(self):
        '''仅适用于明确是新创建的记录，否则会产生数据库 unique constraint violated'''
        new_data = {}
        for i, key in enumerate(self.data_fields):
            new_data[key] = getattr(self, key)
        CS.insertSqlite(self.table_name, new_data)
        pass

    def getTextLog(self):
        '''返回基本的记录信息：日期、(换行)记录文字'''
        log_1 = ''#常规记录
        log_2 = ''#带有后续反馈记录的任务记录

        for attr in self.data_fields:
            if attr.find('update_desc') == 0:#带有后续反馈记录的任务记录
                log_text = getattr(self, attr)
                log_2 = convert_date_log_json(log_text)
                # print(attr,log_2)

            elif attr.find('_desc') > 0:
                log_1 = getattr(self, attr)
                # print(attr,log_1)

        if log_2:
            log_1 = log_1 + '<br />-->' + log_2
        text = '<font size = "3" face="Microsoft YaHei">' \
               '<b>{0}</b><br />{1}<br /><font>'.format(self.create_time,log_1)
        return text


class File(LogType):
    table_name = 'files'
    idx = 'fil'
    PROJECT_REPORT = 'PR'
    BUSINESS_FILE = 'BF'
    RESEARCH_SCHEME = 'RS'
    TECH_SCHEME = 'TS'
    ANY = 'ANY'
    FILE_USAGE_CHOICES = (
        (PROJECT_REPORT, '调研'),
        (BUSINESS_FILE, '商务文件'),
        (RESEARCH_SCHEME, '研究方案'),
        (TECH_SCHEME, '技术方案'),
        (ANY, '一般文件')
    )
    FILE_NAME_EXIST = 1
    SRC_FILE_NOT_FOUND = 2
    FILE_SAME_FILE = 3
    def __init__(self, _id: str = None, file_name: str = None, usage: str = 'ANY', ):
        super(File, self).__init__()
        self._id = _id
        self.file_name = file_name
        self.usage = usage
        self.path = None #包含文件名的完整路径
        self.conn_log_id = None
        self.suffix = self.get_suffix()
        # self.conn_log = None

    @classmethod
    def upload_file(cls, file_instance, parent_widget):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(parent_widget, '选择要上传的文件', 'C:/','.')
        src_file_path, file_name = os.path.split(file_path)
        target_path = os.path.join(userDir , file_instance.create_path())
        tgt_file = os.path.join(target_path, file_name)
        if os.path.exists(tgt_file):  # todo:若文件已存在，需用户判断是否覆盖
            return
        shutil.copy(file_path, target_path)
        file_instance.path = tgt_file
        file_instance.create_time = time.strftime( "%Y-%m-%d %H:%M:%S" )
        file_instance.saveBasicData()
        return file_instance
        pass

    def upload_self(self, src_file_path):
        file_name = self.file_name
        rel_target_path = os.path.split(self.path)[0]
        file_dir = userDir.getUserFileDirectory()
        abs_target_path = os.path.join(file_dir, rel_target_path)
        tgt_file = os.path.join(abs_target_path, file_name)

        if not os.path.exists(abs_target_path):
            print(abs_target_path, '\n配置文件目录不存在，创建目录...')
            # os.mkdir(target_path)
            os.makedirs(abs_target_path)
            print('创建新文件目录成功！\n')
        shutil.copyfile(src_file_path, tgt_file)
        return True

    def try_upload_self(self, src_file_path):
        file_name = self.file_name
        rel_target_path = os.path.split(self.path)[0]
        file_dir = userDir.getUserFileDirectory()
        abs_target_path = f'{file_dir}/{rel_target_path}'
        tgt_file = os.path.join(abs_target_path, file_name)

        if os.path.exists(tgt_file):  # 若文件已存在，需用户判断是否覆盖
            return self.FILE_NAME_EXIST
        if tgt_file == src_file_path: # 指定了同一文件
            return self.FILE_SAME_FILE
        if not os.path.exists(src_file_path): # 目标文件不存在
            return self.SRC_FILE_NOT_FOUND
        else:
            return 0

    @classmethod
    def create_file(cls, parent:QtWidgets.QWidget, usage:ANY):
        file = cls()
        file.assign_new_id()
        file.usage = usage
        file = cls.upload_file(file_instance=file, parent_widget=parent)
        return file
        pass

    def get_suffix(self):
        if self.path:
            s = os.path.splitext(os.path.split(self.path)[1])[1]
        else:
            s = ''
        self.suffix = s
        return s

    def validate_values(self):
        if not self.usage in dict(self.FILE_USAGE_CHOICES):
            raise ValueError("Unexpected value for feature 'usage' ")

    def create_path(self):
        # 客户名/项目名/类型名
        father_node_face_names = []
        pinyin = Pinyin()
        from DataCenter import Project
        name_node = self.father_node # 从每个节点的父节点上取值
        def merge_in_translated_name(_name):
            name_hash = hashlib.md5(_name.encode('utf8')).hexdigest()  # 名称的哈希值
            name_pinyin = pinyin.get_pinyin(_name, '_')  # 将中文转换成拼音
            father_node_face_names.append(name_pinyin + '_' + name_hash[:3])
        while True: # 查找调用链上的父节点
            if name_node:
                if name := name_node.face_name:
                    merge_in_translated_name(name)
                else:
                    pass
                if isinstance(name_node, Project):# Project类不指定上级，
                    name = name_node.client
                    merge_in_translated_name(name)
                    break
                else:
                    pass
                name_node = name_node.father_node
            else:
                 break
        path = '/'.join(reversed(father_node_face_names))
        file_path = f"/{path}/{self.file_name}"
        self.suffix = self.get_suffix()
        return file_path

    # def parse_attched_object(self):
    #     pass

    def delete_self_file(self):
        self.delete_by_id(self._id)
        os.remove(os.path.join(self.path, self.file_name))
        pass

    def open_file(self):
        os.startfile(self.path)
    #
    # def copy_to_path(self):

    def get_source_file_path(self):

        pass

    def get_path(self):
        return self.path


class DataOjectWithFileField(DataObject):
    has_file = False
    def __init__(self, _id:str=None ):
        super(DataOjectWithFileField, self).__init__()
        self._id = _id
        self.attached_file_ids_json = None
        self.file_array = None

    def load_files(self):
        if self.attached_file_ids_json:
            self.file_array = FileArray(father_node=self, json_ids= self.attached_file_ids_json)# FileArray的fatherNode是所依附的item
            self.has_file = True

    def add_file(self,file:File):
        if self.file_array:
            self.file_array.add_item(file)
        else:
            self.init_file_array_from_file(file)
            file.saveBasicData()
        self.update_file_changes()


    def init_file_array_from_file(self, file:File):
        self.file_array = FileArray(father_node=self)
        self.file_array.init_from_file(file)

    def update_file_changes(self):
        if hasattr(self, 'file_array') and self.file_array:
            if self.file_array.has_item():
                self.attached_file_ids_json = self.file_array.getJsonIds()
                self.file_array.save_all_items()
            else:
                self.attached_file_ids_json = None
            self.saveFieldsUpdate(fields=['_id', 'attached_file_ids_json'])

    def remove_file(self):
        pass


class DataOjectWithMultiFileFields(DataObject):
    HAS_FILE = False
    file_fields = ()
    def __init__(self):
        super(DataOjectWithMultiFileFields, self).__init__()
        if self.file_fields:
            self.HAS_FILE = True

    def load_files(self):
        for f, f_usage in self.file_fields:
            for key in locals().keys():
                if key.startswith(f) and key.endswith('_ids'):
                    # self.__setattr__(key, json.loads(self.__getattribute__(key)))
                    try:
                        f_ids = json.loads(self.__getattribute__(key))
                        self.__setattr__(key, f_ids)
                        file_array = FileArray(father_node=self, json_ids=self.__getattribute__(key))
                        self.__setattr__(f, file_array)
                    except:
                        pass

    def add_file(self, file_field:str, file_path:str):
        pass
    pass


class PersonLog(LogType):
    table_name = 'person_log'
    def __init__(self):
        super(PersonLog, self).__init__()
        self._id = None
        self.conn_person_id = None
        self.conn_company_id = None
        self.conn_company_name = None
        self.job_title = None
        self.log_desc = None
        self.in_service = None
        self.name = None

    def addPersonLog(self):
        self.saveBasicData()
        pass

    def addPerson(self,):
        # self.saveBasicData()
        pass

    @staticmethod
    def findPersonLog(person_id)-> list:
        person_log_get = CS.getLinesFromTable(PersonLog.table_name, {'conn_person_id':person_id},order=['createtime'])
        person_log_keys = person_log_get.pop()
        if not person_log_get:
            return None
        person_log = []
        for log in person_log_get:
            person_log_dict = dict(zip(person_log_keys,log))
            person_log.append(person_log_dict)
        return person_log


class CompanyLog(LogType):
    table_name = 'client_log'
    def __init__(self, company_catelog:str = None):
        #首先对类属性进行初始化
        self.log_desc = None
        if company_catelog == 'client':
            self.setTableName('client_log')
        elif company_catelog == 'supplier':
            self.setTableName('supplier_log')
        self.company_id = None
        #初始化父类
        super(CompanyLog, self).__init__()
        #将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.redefined_super(CompanyLog, self)
        # self.trimDataFields()


class Person(DataObject):
    table_name = 'person'
    def __init__(self):
        super(Person, self).__init__()
        self.name = None
        self._id = None
        self.telephone = None
        self.email = None
        self.person_desc = None

    def addPerson(self):
        #若是批量添加，则必须提前分配_id
        if not self._id:
            self.assign_new_id()
        self.saveBasicData()

    def updatePerson(self):
        CS.upsertSqlite('person',['_id','name', 'telephone', 'email', 'person_desc'],
                        [self._id, self.name, self.telephone, self.email, self.person_desc])

    def loadPersonInfo(self, _id=None):
        if self._id and not _id:
            _id = self._id
        if not _id:
            raise ValueError('_id can not be NoneType' )
        data = CS.getLinesFromTable(table_name='person',conditions={'_id':_id})
        # print(task_data)
        keys = data.pop()
        values = data[0]
        self.assign_data(keys, values)


    @staticmethod
    def findPerson(name):
        person_get = CS.getLinesFromTable(Person.table_name,{'name':name})
        person_keys = person_get.pop()
        if not person_get:
            return None
        person_list = []
        for person in person_get:
            person_dict = dict(zip(person_keys,person))
            person_list.append(person_dict)
        return person_list


class Staff(Person):
    table_name = None
    def __init__(self, _id:str = None):
        super(Staff, self).__init__()
        self._id = _id
        self.tittle = None
        self.company = None
        self.company_id = None
        self.in_service = True
        self.modified = False
        self.deleted = False
        # self.career_track = None #json[{'start_time':datetime, 'end_time':datetime, 'company_name':'', 'company_id':'', 'last_tittle':''}]
        #将以上字段的名称保存成列表
        # class_data_fields = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        # self.data_fields = self.data_fields.union(set(class_data_fields))
        # self.redefined_super(Person, self)
        # self.trimDataFields()

    def load_career(self):
        pass

    def assign_data(self,keys,values):
        for i , key in enumerate(keys):
            if hasattr(self, key):
                setattr(self,key,values[i])


class Personnel(DataObject):
    """公司成员的集合"""
    def __init__(self):
        super(Personnel, self).__init__()
        self.staff = []# 员工列表，保存Person实例
        self.staff_adjusted = []

    def loadFromJson(self, data: str):
        if not data:
            return
        personnel_log = json.loads(data) #[{'name':'', '_id':'', 'tittle':'', 'telephone':'', 'email':'', }]
        for item in personnel_log:
            person = Staff()
            item_keys = list(item.keys())
            item_values = list(item.values())
            person.assign_data(item_keys,item_values)
            self.staff.append(person)

    def updatePersonLog(self):
        for staff in self.staff:
            if staff.modified:
                staff.updatePerson()

        person_log_id_get = Snow('psl')
        #记录调整过的人员信息
        for staff in self.staff_adjusted:
            person_log = PersonLog()
            person_log._id = person_log_id_get.get()
            person_log.conn_person_id = staff._id
            person_log.conn_company_id = staff.company_id
            person_log.conn_company_name = staff.company
            person_log.job_title = staff.tittle
            person_log.in_service = staff.in_service
            person_log.addPersonLog()

    def dumpToJson(self):
        personnel_list_data = []
        for person in self.staff:
            person_info = {}
            person_info['name'] = person.name
            person_info['_id'] = person._id
            person_info['tittle'] = person.tittle
            person_info['telephone'] = person.telephone
            person_info['email'] = person.email
            personnel_list_data.append(person_info.copy())
        return json.dumps(personnel_list_data)

    def addPersonnel(self, person_id):
        pass


class CheckUnit(DataOjectWithFileField):
    '''以json格式存储的ids属性，应该以_ids_json结尾'''
    idx = None
    table_name = None
    face_field = 'label'
    Completion_Level_Flag = dict((
        (0, '未开始'),
        (1, '进行中'),
        (2, '解决'),
        (3, '已完善')
    ))
    NotStarted = 0
    Started = 1
    Settled = 2
    Comleted = 3
    def __init__(self):
        self.complete_level = CheckUnit.NotStarted
        super(CheckUnit, self).__init__()

    def load_json_fields(self):
        '''将json格式的属性转换成列表[id]'''
        for attr in self.__dir__():
            if attr.endswith('_ids_json'):
                new_attr = attr.removesuffix('_json')
                try:
                    js = json.loads(self.__getattribute__(attr))
                    self.__setattr__(new_attr, js)
                except:
                    self.__setattr__(new_attr, None)


class CheckItem(CheckUnit):
    #CheckPoint下的检查项目
    idx = 'cki'
    file_fields = ('attached_file', File.ANY)
    face_field = 'label'
    field_type = {
        'label': 'text',
        'desc': 'text',
        'file_array': 'file',
        'complete_level':'enum',
    }
    table_name = 'check_items'
    def __init__(self,  _id:str = None, conn_log_id:str = None, field_name:str = None, label: str = None, attached_file_ids_json = None):
        '''
        :param _id:
        :param field_name: 字段名称
        :param label: 显示给用户的名称
        '''
        super(CheckItem, self).__init__( )
        self._id = _id
        self.field_name = field_name  # 在checkpoint当中作为一个子项的存储字段名，对应label为显示给用户看的字段名
        self.label = label
        self.conn_log_id = conn_log_id
        self.attached_file_ids_json = attached_file_ids_json
        self.desc = None
        self.setFace()

    def setDesc(self, desc: str):
        self.desc = desc

    def setCompleteLevel(self, complete_level:int):
        self.complete_level = complete_level

    def renew_file_ids_json(self):
        file_ids_json = self.file_array.getJsonIds()
        if file_ids_json:
            self.attached_file_ids_json = file_ids_json
        else:
            self.attached_file_ids_json = None

    def saveAllData(self):
        self.renew_file_ids_json()
        self.saveBasicData()


class CheckPoint(CheckUnit):
    '''checkPoint层需要维护的和下级字段有关的字段包括：children_chains_ids_json、children_items_ids_json、attached_file_ids_json
       对于上述字段，只有在对应的下级的数量变化时才需要维护。

    '''
    idx = 'cpt'
    table_name = 'check_points'
    '''项目按时间顺序向下推进过程中的检查点'''
    def __init__(self, conn_log_id:str = None):
        super(CheckPoint, self).__init__()
        self.last_ckp_id = None
        self.next_ckp_id = None
        self.conn_log_id = conn_log_id
        self.children_chains_json = None # 检查点包含的子流程。
        self.children_items_ids_json = None
        self.attached_file_ids_json = None # 相关文件
        self.label = None
        self.field_name = None

    def load_basic_data(self, _id: str=None, order: list=None):
        # print('checkPoint_id :',_id)
        super(CheckPoint, self).load_basic_data(_id=_id)
        self.load_json_fields()

    def load_complete_data(self, _id: str=None,):
        self.load_basic_data(_id = _id)
        # self.load_json_fields()
        self.load_files()
        self.load_children_items()

    def load_children_items(self):
        if hasattr(self, 'children_items_ids') and self.children_items_ids:
            self.children_items = []
            for id in self.children_items_ids:
                item = CheckItem.asChildNode(father_node=self.father_node)
                item.load_basic_data(_id=id)
                item.load_files()
                self.children_items.append(item)
            self.sort_children_items()
        else:
            self.children_items = None

    def save_all_children_chains(self):
        if not hasattr(self, 'children_chains') or not self.children_chains:
            return
        ids = []
        for chain in self.children_chains:
            ids.append(chain._id)
            chain.saveAllData()
        self.children_chains_ids_json = json.dumps(ids)
        pass

    def renew_children_items_ids_json(self):
        if not self.children_items:
            return
        ids = []
        for item in self.children_items:
            ids.append(item._id)
        self.children_items_ids_json = json.dumps(ids)
        pass

    def renew_children_files_ids_json(self):
        if not self.file_array:
            return
        ids = []
        for file in self.children_items:
            ids.append(file._id)
        self.attached_file_ids_json = json.dumps(ids)
        pass

    def save_all_children_items(self):
        if not hasattr(self, 'children_items') or not self.children_items:
            return
        ids = []
        for item in self.children_items:
            ids.append(item._id)
            item.saveBasicData()
        self.children_items_ids_json = json.dumps(ids)
        pass

    def load_children_chains(self):

        if hasattr(self, 'children_chains_ids') and self.children_chains_ids:
            self.children_chains = []
            for id in self.children_chains_ids:
                chain = CheckPointChain()
                chain.load_basic_data(id)
        else:
            self.children_chains = None

    def sort_children_items(self):
        if self.children_items:
            self.children_items.sort(key=lambda x: x.create_time)

    def add_children_item(self, check_item:CheckItem):
        if not hasattr(self, 'children_items'):
            self.children_items = []
        self.children_items.append(check_item)

    def saveAllData(self):
        self.save_all_children_items()
        self.save_all_children_chains()
        self.saveBasicData()
        pass


class CheckPointChain(DataObject):
    '''项目的检查点链条，构成整个项目的流程框架
       新的chain从json模板来创建，json模板通过预定义的模板加载，也可以从之前保存的用户自定义模板来加载。
       chain创建后，为每个point和point下面的item分配id,
    '''
    idx = 'cpc'
    table_name = 'check_point_chains'
    def __init__(self):
        super(CheckPointChain, self).__init__()
        self.CHAIN = None #json dict
        self.solving_status = None  # 未开始、开展中、可交付（有遗留问题）、完成

    def makeChain(self):
        pass

    def saveAllData(self):
        pass


class Company(DataObject):
    table_name = None
    log_table_name =None
    meeting_log_table = None
    def __init__(self):
        super(Company, self).__init__()
        self._id = None
        self.short_name = None
        self.enterprise_name = None
        self.country = None
        self.desc = None
        self.create_time = None
        self.personnel = None
        self.update_time = None
        self.detailed_location = None
        self.telephone = None
        self.email = None
        self.person_responsible = None
        #将以上字段的名称保存成列表
        # self.redefined_super(Company, self)
        # self.data_fields.update([ key for key ,value in locals().items()])
        # self.trimDataFields()
        self.personnel_class = None
        self.logs = []

    # def trimDataFields(self):
    #     self.data_fields.discard('data_fields')
    #     self.data_fields.discard('table_name')
    #     self.data_fields.discard('log_table_name')

    def setId(self):
        pass

    def saveAllData(self):
        #保存personnel
        self.personnel = self.personnel_class.dumpToJson() if self.personnel_class.staff else None
        #保存人员信息变化
        self.savePersonLog()
        #client_log
        self.log_num = len(self.logs)
        self.saveBasicData()
        # print('self.province',self.province)
        for log in self.logs:
            log.saveBasicData()
        return True

    def loadBasicData(self, _id:str = None, company_name:str = None):
        '''根据_id或者client_name来初始化数据，优先使用_id，并在_id和client不符是返回0
        这个函数会将整个实例的所有基本参数重新赋值，基本相当于变成一个新的client实例
        '''
        if not _id:
            _id = self._id
            if _id:#优先使用_id 进行检索
                client_basic_info  = CS.getLinesFromTable(self.table_name, conditions={'_id': _id})
            elif not company_name:
                company_name = self.short_name
                if company_name:
                    client_basic_info  = CS.getLinesFromTable(self.table_name,
                                                              conditions={'short_name': company_name})
                else:#
                    raise ValueError('%s is not able to be assigned data without assigning _id or client_name first'%self.__str__())
        keys = client_basic_info.pop()#这里没问题，不用管
        values = client_basic_info[0]
        self.assign_data(keys, values)
        if company_name and values[keys.index('short_name')] != company_name:
            return 0
        else:
            return 1

    def loadCompanyLogs(self):
        '''加载公司的备注记录信息'''
        self.logs.clear()
        if not self._id:
            self.loadBasicData()

        logs = CS.getLinesFromTable(self.log_table_name, conditions={'company_id':self._id},
                                    order=['create_time'],ascending=True)
        keys = logs.pop()

        for values in logs:
            company_log = CompanyLog()
            company_log.setTableName(self.log_table_name)#
            # setattr(company_log,'company_id',None)##增加一个company_id属性
            company_log.assign_data(keys,values)

            self.logs.append(company_log)

    def savePersonLog(self):
        if self.personnel_class:
            self.personnel_class.updatePersonLog()

    def assign_data(self,keys,values):
        for i , key in enumerate(keys):
            if hasattr(self, key):
                setattr(self,key,values[i])

    def setPersonnelClass(self):
        '''创建公司职员信息类实例'''
        self.personnel_class = Personnel()
        self.personnel_class.loadFromJson(self.personnel)
        self.personnel_class.staff_adjusted.clear()


class Manufacturer(Company):
    product_choices = (
        ('cmo', 'CMO服务'),
        ('API', '原料药'),
        ('excipient', '辅料'),
        ('rld', '参比制剂')
    )
    pass


class Supplier:
    pass

class Chemical(DataObject):
    def __init__(self):
        self.name = None
    pass


class Drug(DataObject):
    def __init__(self):
        super(Drug, self).__init__()
        self.api_name = None

        pass


class ReferenceListedDrug(Drug):
    def __init__(self):
        self._id = None
        self.serial_num = None
        self.common_name = None
        self.specs = None #规格
        self.dosage_form = None
        self.holder = None
        self.note_1 = None
        self.note_2 = None
        self.release_date = None
        self.renewal_date = None
        pass


class DataObjectArray(metaclass=ABCMeta):
    '''
    Abstract class describing the basic collective behavior of the packed Logtype or File instances.
    Logs such as memo, task, meeting_log, file can come up in bunch, and be assigned to an attribute of
    another class or instance.
    '''
    @abstractmethod
    def rearrange_items_by_time(self)->None:
        pass

    @abstractmethod
    def save_all_items(self)->None:
        pass

    @abstractmethod
    def load_all_items(self)->None:
        pass

    # @abstractmethod
    # def get_face_text_and_time_by_index(self, index:int) -> dict:
    #     '''
    #     :index
    #     :return: {text:str, create_time:datetime, update_time:datetime}
    #     '''
    #     pass
    #
    # @abstractmethod
    # def get_all_create_times(self)->list:
    #     pass


class AbstractArray(DataObjectArray):
    table_name = None
    item_type = None
    factory = ItemTypeCreateFactory()
    def __init__(self, father_node):
        self.father_node:DataObject = father_node
        self.items:list = []

    def load_all_items(self) ->None:
        conn_obj_id = None
        for attr in self.father_node.__dir__():
            if attr.startswith('conn_'):
                conn_obj_id = getattr(self.father_node, attr)

        item_info = CS.getLinesFromTable(table_name=self.table_name, conditions={'conn_project_id': conn_obj_id},
                                          order=['inter_order_weight'])
        item_keys = item_info.pop()
        for values in item_info:
            temp_item = self.factory.create(self.father_node, self.item_type)
            temp_item.assign_data(item_keys, values)
            self.items.append(temp_item)

    def rearrange_items_by_time(self) ->None:
        pass

    def save_all_items(self) ->None:
        for item in self.items:
            item.saveBasicData()

    def has_item(self) ->bool:
        return len(self.items) > 0

    def remove_item(self, log_item:LogType)->None:
        for i, item in enumerate(reversed(self.items)):
            if item._id == log_item._id:
                self.items.pop(i)

    def pop_item(self, index: int) -> File:
        try:
            return self.items.pop(index)
        except IndexError:
            raise IndexError

    def get_item(self, index):
        try:
            return self.items[index]
        except IndexError:
            raise IndexError


class TaskArray(AbstractArray):
    table_name = 'tasks'
    item_type = 'task'

    def rearrange_items(self) ->None:
        self.items.sort(key = lambda x: x.create_time)
        pass


class MemoArray(AbstractArray):
    table_name = 'project_memo_log'
    item_type = 'memo'


class MeetingLogArray(AbstractArray):
    table_name = 'project_meeting_log'
    item_type = 'meeting_log'


class FileArray(AbstractArray):
    table_name = 'files'
    item_type = 'file'
    def __init__(self, father_node, json_ids:str=None ):
        super(FileArray, self).__init__(father_node = father_node) # FileArray的father_node是checkItem
        self.items:list[File] = []
        self.ids:list[str]
        if json_ids:
            self.ids: list = json.loads(json_ids)
            self.load_all_files_from_ids()

    def init_from_file(self, file:File):
        self.items.append(file)
        self.ids = [file._id]

    def load_all_files_from_ids(self) ->None:
        for id in self.ids:
            file = File.asChildNode(father_node=self.father_node) # FileArray的father_node是checkItem
            file.load_basic_data(_id=id, order=['create_time'])
            self.items.append(file)

    def rearrange_items_by_time(self) ->None:
        pass

    def save_all_items(self) ->None:
        for item in self.items:
            item.saveBasicData()

    def getJsonIds(self) ->str:
        ids = []
        for item in self.items:
            ids.append(item._id)
        if ids:
            return json.dumps(ids)
        else:
            return ''

    def add_item(self, file: File) -> None:
        self.items.append(file)
        self.ids.append(file._id)
        file.saveBasicData()

    def delete_file(self, file:File) ->bool:
        if self.remove_file(file):
            file.delete_self_file()
            return True
        else:
            return False

    def remove_file(self, file:File)->bool:
        for i, item in enumerate(reversed(self.items)):
            if item._id == file._id:
                self.items.pop(i)
                return True
        else:
            return False

    def refresh(self) -> None:
        self.ids.clear()
        self.ids = [item._id for item in self.items]


if __name__ == '__main__':
    d = DataObject()
    d.face_name = 'Test'
    from DataCenter import Project
    x = Project.asChildNode(father_node = d)  
    x.client = "广东国标"
    x.face_name = '阿立哌唑注射剂'
    y = CheckItem.asChildNode(father_node = x)
    y.label = '合同草案'
    y.setFace()
    f = File.asChildNode(father_node = y)
    print(f.create_path())