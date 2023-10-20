import datetime
import json
import ConnSqlite as CS
import DataCenter
import RedefinedWidget
from ID_Generate import ID_Generator, Snow


class ToDoUnitCreator():
    def __init__(self, company_id: str = None, conn_project_id: str = None, conn_task_id: str = None,
                  parent_presenter = None):
        self.parent_presenter = parent_presenter
        self.model = DataCenter.ToDo()
        self.initial_company_id = company_id
        self.initial_project_id = conn_project_id
        self.initial_task_id = conn_task_id
        self.task = conn_task_id
        self.init_project = conn_project_id
        self.is_critical = False
        # 主表单

    def getInitFields(self,json_request_fields:str):
        requested_fields = json.loads(json_request_fields)
        requested_fields_map = {}
        for field in requested_fields:
            requested_fields_map[field] = getattr(self, field)
        return json.dumps(requested_fields_map)

    def createWithDialog(self, parent_widget):
        self.dialog = RedefinedWidget.ToDoUnitCreateDialog(parent=parent_widget, presenter=self)
        ok = self.dialog.exec()
        if ok :
            return ok, self.json_model_data
        else:
            return False, None

    def getAllCompany(self)->list[tuple[str]]:
        companies = CS.getLinesFromTable('clients', conditions={}, columns_required=['_id', 'short_name'])
        companies.pop()
        return companies

    def getCompanyProjects(self, company_id: str)->list[tuple[str]]:
        projects = CS.getLinesFromTable('proj_list', conditions={'client_id': company_id},
                                        columns_required=['_id', 'product'])
        projects.pop()
        return projects

    def getProjectTasks(self, project_id: str)->list[tuple[str]]:
        tasks = CS.getLinesFromTable('tasks', conditions={'conn_project_id': project_id},
                                     columns_required=['_id', 'task_desc', 'officejob_type'])
        tasks.pop()
        return tasks

    def checkTaskTodoExistance(self, conn_task_id):
        if conn_task_id:
            find_todo = CS.getLinesFromTable('todo_log', conditions={'conn_task_id': conn_task_id})
            find_todo.pop()
            if find_todo:
                return True
        return False

    def setModelCompany(self, id:str):
        self.model.conn_company_id = id

    def setModelProject(self, id:str):
        self.model.conn_project_id = id

    def setModelIsCritical(self, is_critical:bool):
        self.model.is_critical = is_critical

    def setModelConnTaskId(self, id:str):
        self.model.conn_task_id = id

    def setModelDesc(self, desc:str):
        self.model.todo_desc = desc

    def setModelOfficeJobType(self, type:int):
        self.model.officejob_type = type

    def setModelConclusionDesc(self,json_desc:str):
        self.model.conclusion_desc = json_desc

    def saveModel(self, json_fields_values:str):
        '''

        :param json_fields_values: json of a python dict
        :return:
        '''
        fields_values: dict = json.loads(json_fields_values)
        fields_values['_id'] = ID_Generator.get('td')
        pending_days = fields_values['pending_days']
        if pending_days:
            fields_values['on_pending'] = True
            today = datetime.datetime.today().date()
            # datetime日期加一个数字，得到的结果是日期直接加这个数字的值，与两个日期相减的逆运算是对称的
            pending_till_date = today + datetime.timedelta(days=(int(pending_days)))
            pending_till_date = str(pending_till_date)
            fields_values['pending_till_date'] = pending_till_date
        self.setModelFieldsValues(fields_values)
        if not self.model.conn_task_id:
            self.model.conn_task_id = Snow('ts').get()
            self.broadCastTaskUpdate(as_new_task=True)
        else:
            self.broadCastTaskUpdate(as_new_task=False)
        self.model.saveBasicData()
        self.json_model_data = json.dumps(fields_values)

    def broadCastTaskUpdate(self, as_new_task:bool):
        return # This broadcast is for related model 'task'. For it's from the View, it should be launched by the View,
        if not self.model.conn_company_id or not self.model.conn_project_id:
            return

        task_fields_values = {}
        task_fields_values['_id'] = self.model.conn_task_id
        task_fields_values['task_desc'] = self.model.todo_desc
        task_fields_values['is_critical'] = self.model.is_critical
        task_fields_values['officejob_type'] = self.model.officejob_type
        task_fields_values['conn_project_id'] = self.model.conn_project_id

        if not as_new_task:
            if self.initial_task_id:  # 来源是projectTabBar等可以指定具体task_id的控件，此时强制要求接收source_widget接收广播
                source_widget = None
            else:
                source_widget = self.parent_presenter.view.tab_bar  # 来源仅仅是追踪模式的tab_bar
            cmd = DataCenter.GTaskCmd('update', _id=task_fields_values['_id'], fields_values=task_fields_values,
                                      source_widget=source_widget,
                                      conn_company_name=self.model.conn_company_id)

        else:  # 是为关联的项目建立的一个新的todo
            # task_fields_values['conn_company_id'] = self.model.conn_company_id

            existing_task = CS.getLinesFromTable('tasks', {'conn_project_id': self.model.conn_project_id},
                                                 ['inter_order_weight'])
            existing_task.pop()
            if not existing_task:
                task_fields_values['inter_order_weight'] = 1
            else:
                task_fields_values['inter_order_weight'] = len(existing_task) + 1
            task_fields_values['create_time'] = self.model.create_time
            source_widget = self.parent_presenter.view.tab_bar  # 来源仅仅是追踪模式的tab_bar
            cmd = DataCenter.GTaskCmd('insert', _id=task_fields_values['_id'], fields_values=task_fields_values,
                                      source_widget=source_widget,
                                      conn_company_name=self.model.conn_company_id)
        self.parent_presenter.listener.accept(cmd)

    def setModelFieldsValues(self, fields_values:dict):
        '''

        :param json_fields_values: a python dict
        :return:
        '''
        for field, value in fields_values.items():
            setattr(self.model, field, value)
