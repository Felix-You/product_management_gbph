import threading
from DataCenter import ToDo, GCmd
from apps.TodoPanel.Interface import ModelPresenter
from apps.TodoPanel.TodoUnitView import TodoUnitView
from threading import Thread, Timer
from time import sleep, ctime

from core.KitModels import LogType


class MyThread(threading.Thread):
    def __init__(self, target, args,kwargs):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args
        self.kwarg = kwargs

    def run(self):
        self.result = self.func(*self.args, *self.kwarg)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

class TodoUnitPresenter(ModelPresenter):
    def __init__(self, parent=None , parent_widget=None):
        super(TodoUnitPresenter, self).__init__()
        self.parent = parent
        self.parent_widget = parent_widget
        self.models = {} # this a table for access to todo_unit model, and it works only as a cache table,
                         # for it does not really delete the model from memory
        self.model_counter = {}
        self.views:dict[str:TodoUnitView] = {}
        self.timer = Timer(10, self.on_timer)
        self.timer.start()
        self.ok_to_trim_model_cache = False

    def exclusiveThread(func):
        '''decorator'''
        def wrapper(*args, **kwargs):
            thread = MyThread(target=func, args=args, kwargs=kwargs)
            thread.start()
            thread.join()
            ret = thread.get_result()
            return ret
        return wrapper

    def on_timer(self):
        self.ok_to_trim_model_cache = True

    # @exclusiveThread
    def trimModelCache(self):
        # This if not absolutely thread-safe. There is a small chance that this function starts right before _trim_lock get flipped from False to True,
        # and functions under "lockTrim" goes on together with this function.
        for id in self.model_counter.keys():
            if id in self.parent.GridModel.id_unit_map:
                continue
            # if self._trim_lock == True and id == self._todo_id_lock:
            #     continue
            counter = self.model_counter[id]
            if counter <= 0:
                self.model_counter.pop(id, None)
                self.models.pop(id, None)
            self.model_counter[id] -= 1
        self.ok_to_trim_model_cache = False

    def addModelCache(self, model:LogType):
        todo_id = model._id
        self.model_counter[todo_id] = 5
        self.models[model._id] = model

    # @exclusiveThread
    def makeModel(self, todo_id:str ,fields:list[str], values: list):
        if self.ok_to_trim_model_cache:
            self.trimModelCache()
        if todo_id in self.models:
            return self.models[todo_id]
        todo_model = ToDo()
        todo_model.assign_data(fields, values)
        self.addModelCache(todo_model)
        return todo_model


    def removeModel(self, id):
        self.models.pop(id, None)
        self.model_counter.pop(id,None)
        # self.views.pop(id, None)

    # def createView(self, model:ToDo):
    #     id = model._id
    #     new_view = TodoUnitView(parent=self.parent, parent_view = self.parent_widget)
    #     new_view.intit_data(model.getModelAttribData())
    #     self.views[id] = new_view


    def update_basic_field(self, id:str, field_values:dict):
        # self.model.conclusion_desc(desc)
        self.model_counter[id] = 5
        model = self.models[id]
        for key, value in field_values.items():
            model.__setattr__(key, value)
        model.saveBasicData()
        pass


    def handleShowOtherModel(self, model_name, model_id):
        self.parent.handleShowExternalModel(model_name, model_id)

    def handleDeleteModel(self, todo_id):
        self.models[todo_id].destroyed = True
        self.models[todo_id].saveBasicData()
        self.models.pop(todo_id)
        self.model_counter.pop(todo_id)
        self.parent.handleDeleteModel(todo_id)

    def update_other_model(self,  model_name:str, updata_cmd:GCmd):
        self.parent.listener.accept(updata_cmd)
        pass

    def updateConnData(self):
        pass


    def setDataToView(self, id):
        model = self.models[id]
        data = model.getModelAttribData()
        self.views[id].init_data(data)
