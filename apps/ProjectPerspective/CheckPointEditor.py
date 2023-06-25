import os
import time

from apps.ProjectPerspective.CheckPointEditorView import CheckPointEditorView
from core.KitModels import CheckPoint, File, CheckItem, getCurrentTime
from core.Presenter import Presenter
from abc import abstractmethod


class CheckpointEditor(Presenter):

    def __init__(self,
                 model:CheckPoint,
                parent = None
    ):
        self.model = model
        self.parent = parent
        self._checkPointView = None
        # self.action_widget:

    @property
    # @abstractmethod
    def checkPointView(self):
        return self._checkPointView
        pass

    @checkPointView.setter
    # @abstractmethod
    def checkPointView(self, view:CheckPointEditorView):
        self._checkPointView = view
        pass

    def setDataModel(self, condition: dict):
        pass

    def on_dataChanged(self):
        # self.model.int
        if not self.model.children_items_ids_json:
            self.model.renew_children_files_ids_json()
            self.model.save_all_children_items()
        else:
            self.model.renew_children_files_ids_json()
        self.model.saveBasicData()

        self.model.father_node.saveBasicData()

    def receive_data_stream(self, data_stream):
        ...

    def display(self):
        data = self.model.serialize()
        field_type = CheckItem.field_type
        fields_to_edit = ['desc', 'complete_level', 'file_array']
        self.checkPointView.setupView(data, field_type, fields_to_edit)

    # @abstractmethod
    def setModelItemDesc(self, index:int, text:str) -> None:
        item = self.model.children_items[index]
        item.desc = text
        item.update_time = getCurrentTime()
        item.saveBasicData()
        self.on_dataChanged()
        pass

    # @abstractmethod
    def setModelItemCompleteLevel(self, index:int, c_code:int) -> None:
        item = self.model.children_items[index]
        item.complete_level = c_code
        item.update_time = getCurrentTime()
        item.saveBasicData()
        self.on_dataChanged()
        pass

    def uploadFiles(self, index, file_paths:list[str]):
        '''

        :param index:
        :return:
        '''
        file_array_data = self.model.serializeModel(self.model.children_items[index].file_array)
        src_file_paths = file_paths ## self.checkPointView.handleFileUploadDialog(file_array_data)
        if not src_file_paths:
            return None
        for src_file_path in src_file_paths:
            file = File.asChildNode(father_node = self.model.children_items[index]) # File的father_node是其所附属的item
            file.assign_new_id()
            file.file_name = os.path.split(src_file_path)[1]
            file.path = file.create_path()
            file.create_time = getCurrentTime()
            file.conn_log_id = self.model.conn_log_id
            n_Oper = file.try_upload_self(src_file_path)
            if n_Oper == file.FILE_NAME_EXIST: # 存在同名文件
                do_replace = self.checkPointView.raiseFileExist(file.file_name)
                if do_replace:
                    file.upload_self(src_file_path)
                    self.model.children_items[index].add_file(file)
                else:
                    del file
                    pass
            elif n_Oper == file.SRC_FILE_NOT_FOUND: # 目标文件不存在
                self.checkPointView.raiseSrcFileNotExist()
                del file
            else:
                file.upload_self(src_file_path)
            # file.saveBasicData()
                self.model.children_items[index].add_file(file)
        self.on_dataChanged()
        return self.model.serializeModel(self.model.children_items[index].file_array)


    def setBoundWidget(self, obj):
        self.bound_widget = obj

    # def renderWidget(self):
    #     pass
        pass
    def Accept(self, cmd):
        '''首先应该查找cmd中的数据是否在自己的DataModel中,如果不存在则直接抛弃。
        判断的过程是一个搜索过程
        如果是project类型的数据，一步直接搜索_id; 如果是log类型的数据，则要到project类的属性下面去搜索，task，memo，meeting分别对应各自的搜
        索空间。
        搜索到了数据之后再判断所对应的控件位置
        '''
        pass
