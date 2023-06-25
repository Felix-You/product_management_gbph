from abc import ABC,abstractmethod


class Presenter(ABC):
    tablet_index = 0
    contain_root_item = None#界面的根节点类型，
    contain_root_ids = []#包含的根节点类型的id

    @abstractmethod
    def setDataModel(self,condition:dict):
        pass



    @abstractmethod
    def setBoundWidget(self,obj):
        self.bound_widget = obj

    # def renderWidget(self):
    #     pass

    @abstractmethod
    def Accept(self,cmd):
        '''首先应该查找cmd中的数据是否在自己的DataModel中,如果不存在则直接抛弃。
        判断的过程是一个搜索过程
        如果是project类型的数据，一步直接搜索_id; 如果是log类型的数据，则要到project类的属性下面去搜索，task，memo，meeting分别对应各自的搜
        索空间。
        搜索到了数据之后再判断所对应的控件位置
        '''
        pass
