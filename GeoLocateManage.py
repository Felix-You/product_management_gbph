from DataCenter import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from ID_Generate import Snow
from CatogeryManageUi import Ui_Dialog
import copy


class GeoLocateManage(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        super(GeoLocateManage,self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('片区名称')
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint)
        self.setFixedSize(350,300)
        self.parent = parent
        self.model = self.parent.model
        self.locates = self.model.locates
        self.locate_dict = self.model.client_dict
        self.track_id = Snow('track')#用于跟踪locate的id,自动生成，自增长
        self.locate_id_bounds = [(self.track_id.get(), locate) for locate in self.locates]#给locate编号跟踪[(id,locate_name)]
        self.source_locate_id_bounds = copy.deepcopy(self.locate_id_bounds)
        self.listView.clicked.connect(self.handleItemPressed)
        self.pushButton.clicked.connect(self.on_add_button_clicked)
        self.pushButton_2.clicked.connect(self.on_delete_button_clicked)
        self.pushButton_3.clicked.connect(self.on_apply_button_clicked)
        self.pushButton_4.clicked.connect(self.on_quit_button_clicked)
        self.setUpListView()

    def setUpListView(self):
        '''初始化区域名称列表'''
        self.listModel = QStandardItemModel()

        for i, locate in enumerate(self.locate_id_bounds):
            self.listModel.setItem(i,0,QStandardItem(locate[1]))
            self.listModel.item(i,).setCheckState(QtCore.Qt.Unchecked)
            self.listModel.item(i,).setEditable(True)
        self.listView.setModel(self.listModel)
        self.listModel.dataChanged.connect(self.on_locate_name_edit)

    def on_add_button_clicked(self):
        current_row = self.listModel.rowCount()
        if current_row >= 12:
            QMessageBox.about(self,'注意', '最多添加12个分区！')
            return
        self.listModel.setItem(current_row,0,QStandardItem('区域%s'%current_row))
        self.listModel.item(current_row).setCheckState(QtCore.Qt.Unchecked)
        self.locate_id_bounds.append((self.track_id.get(), '区域%s'%current_row))
        # print('self.locate_id_bounds',self.locate_id_bounds)

    def on_delete_button_clicked(self):
        ok = QMessageBox.question(self, '删除', '删除选中区域？')
        if not ok:
            return
        for i in range(self.listModel.rowCount()-1, -1, -1):
            # print(self.listModel.item(i).data(0),self.listModel.item(i).checkState())
            if self.listModel.item(i).checkState() == QtCore.Qt.Checked:
                self.listModel.removeRow(i)
                self.locate_id_bounds.pop(i)
        # print('self.locate_id_bounds',self.locate_id_bounds)

    def on_apply_button_clicked(self):
        #获取编辑后的locate名称
        self.new_locate_id_bounds = []#编辑完成后，重新获取一遍绑定的id和locate
        for i in range(self.listModel.rowCount()):
            self.new_locate_id_bounds.append((self.locate_id_bounds[i][0], self.listModel.item(i).data(0)))
        #剔除被删掉的locate
        for i, old_item in enumerate(self.source_locate_id_bounds):
            for new_item in self.new_locate_id_bounds:
                if new_item[0] == old_item[0]:
                    break
            else:
                self.locate_dict.pop(old_item[1])
        #保存修改到文件
        for new_item in self.new_locate_id_bounds:
            for old_item in self.source_locate_id_bounds:
                if new_item == old_item:
                    break
                elif new_item[0] == old_item[0]:#属于原有的locate被改名的情况
                    locate_city_codes = self.locate_dict[old_item[1]]
                    self.locate_dict.pop(old_item[1])
                    self.locate_dict[new_item[1]] = locate_city_codes
                    break
            else:
                self.locate_dict[new_item[1]] = []
        self.model.saveUserClientFilter()
        self.accept()

    def on_quit_button_clicked(self):
        self.reject()

    def on_locate_name_edit(self,qindex_topleft,qindex_bottomright,qvector):
        # print(qindex_topleft.row(),qindex_topleft.column(),qindex_topleft.data(),qindex_topleft.flags(), qvector)
        if not qvector:#新建了一个item
            return
        if qvector[-1] == 2:# QVector的值，代表修改了字符串
            if qindex_topleft.data() == self.locate_id_bounds[qindex_topleft.row()][1]:
                pass
            else:
                for item in self.locate_id_bounds:
                    if qindex_topleft.data().strip() == item[1]:
                        QMessageBox.about(self, '错误','命名重复，请重新输入！')
                        self.listModel.item(qindex_topleft.row()).setData('!重命名%s'%qindex_topleft.row(), 0)
                        return
                locate_id_bound_before = self.locate_id_bounds[qindex_topleft.row()]
                self.locate_id_bounds[qindex_topleft.row()] = (locate_id_bound_before[0], qindex_topleft.data().strip())

    def handleItemPressed(self, index):
        item = self.listView.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
