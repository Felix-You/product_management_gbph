import sys,copy
import time
from DataCenter import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5 import QtCore
from GeoFilterEditorUi import Ui_Dialog
from GeoLocateManage import GeoLocateManage



class GeoFilterEditor(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        '''
        listView:行政区城市信息列表视图
        listView_2:自定义区域城市列表视图
        '''
        super(GeoFilterEditor,self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.model = GeoModel()
        self.setWindowTitle('自定义区域')
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)
        self.comboBox.setEditable(True)
        self.comboBox.lineEdit().setPlaceholderText('请选择省份')
        self.comboBox.addItems(map(lambda X: X[1],self.model.getProvinceItems()))
        self.locate_city_codes = None
        self.comboBox.setCurrentIndex(-1)
        self.comboBox_2.addItems(self.model.locates)
        self.comboBox_2.setCurrentIndex(-1)
        self.comboBox_2.setEditable(True)
        # placeHodler = self.comboBox_2.setPlaceholderText()
        self.comboBox_2.lineEdit().setPlaceholderText(u'设置区域')
        # self.comboBox_2.setCurrentIndex(-1)
        # self.locate = self.comboBox_2.currentText()
        # print('self.locate_before',self.locate)
        # print('self.model.client_dict_before',self.model.client_dict)
        # if self.locate: self.locate_city_codes = self.model.client_dict[self.locate]#从model的字典里面读取

        self.cities = None#行政区城市信息(代码，名称) 列表
        self.locate_city_codes = None#自定义区域城市代码 列表
        self.comboBox.currentIndexChanged.connect(self.initListView)
        self.locate_selected = self.comboBox_2.currentText()
        #模型之类的先提前完成初始化，数据可以后面再载入
        self.listModel = QStandardItemModel()
        self.listView.setModel(self.listModel)
        self.listModel_2 = QStandardItemModel()
        self.listView_2.setModel(self.listModel_2)
        self.initListView()
        self.initListView_2()
        #页面控件信号
        self.listView.clicked.connect(self.handleItemPressed)
        self.listView_2.clicked.connect(self.handleItemPressed)
        self.comboBox_2.currentIndexChanged.connect(self.resetListView_2)
        self.pushButton.clicked.connect(self.on_delete_button_clicked)
        self.pushButton_2.clicked.connect(self.on_add_button_clicked)
        self.toolButton.clicked.connect(self.on_manage_button_clicked)
        self.checkBox.clicked.connect(self.on_check_all_cities)
        self.checkBox_2.clicked.connect(self.on_check_all_cities_2)
        self.edit_used = False

    def initListView(self):
        ''''''
        index = self.comboBox.currentIndex()
        # print(list(self.model.getProvinceItems()))
        if index == -1 :
            return
        self.current_province_code = list(self.model.getProvinceItems())[index][0]
        self.cities = list(self.model.getCityItems(province_code=self.current_province_code))#城市代码与名称对
        self.listModel.clear()
        for i, city in enumerate(self.cities):
            # self.city_codes.append(city[0])
            self.listModel.setItem(i,0,QStandardItem(city[1]))
            self.listModel.item(i,).setCheckState(QtCore.Qt.Unchecked)
            self.listModel.item(i,).setEditable(False)

    def initListView_2(self):
        current_index = self.comboBox_2.currentIndex()
        if current_index == -1:
            return
        self.locate = self.comboBox_2.currentText()
        # self.locate_city_codes = copy.deepcopy(city_codes)
        self.locate_city_codes = self.model.client_dict[self.locate]
        for i, code in enumerate(self.locate_city_codes):
            if isinstance(code, (tuple, list)):
                country_code , province_code, city_code = code
            else:
                country_code, province_code, city_code = self.model.geo.country_code, None, code
            city_name = self.model.getCityNameFromCode(city_code, province_code=province_code, country_code=country_code)
            if not city_name:
                continue
            self.listModel_2.setItem(i,0,QStandardItem(city_name))
            self.listModel_2.item(i,).setCheckState(QtCore.Qt.Unchecked)
            self.listModel_2.item(i, ).setEditable(False)
        pass

    def resetListView_2(self):
        self.listModel_2.clear()
        self.locate = self.comboBox_2.currentText()
        #重置
        if not self.locate:
            self.locate_city_codes = None
            return
        else:
            self.locate_city_codes = self.model.client_dict[self.locate]
        # index = self.comboBox.currentIndex()
        # province_code = list(self.model.getProvinceItems())[index][0]
        row_index = 0
        for i, code in enumerate(self.locate_city_codes):
            if isinstance(code, (tuple, list)):
                country_code , province_code, city_code = code
            else:
                country_code, province_code, city_code = self.model.geo.country_code, None, code
            city_name = self.model.getCityNameFromCode(city_code, province_code=province_code, country_code=country_code)
            if not city_name:
                continue
            self.listModel_2.setItem(row_index,0,QStandardItem(city_name))
            self.listModel_2.item(row_index,).setCheckState(QtCore.Qt.Unchecked)
            self.listModel_2.item(i, ).setEditable(False)
            row_index += 1
        self.listView_2.setModel(self.listModel_2)
        pass

    def on_add_button_clicked(self):
        if not self.cities or self.locate_city_codes is None:
            return
        len_before = len(self.locate_city_codes)#
        for i in range(self.listModel.rowCount()):
            if self.listModel.item(i).checkState() == QtCore.Qt.Checked:
                target_city = (self.model.geo.country_code, self.current_province_code, self.cities[i][0])
                if target_city in self.locate_city_codes:#已经存在的不添加
                    continue
                else:
                    self.locate_city_codes.append(target_city)
        len_after = len(self.locate_city_codes)
        if len_before == len_after:#没有添加城市
            return
        # print('self.locate_city_codes_after', self.locate_city_codes)
        self.saveAndApplyChanges()
        self.resetListView_2()
        pass

    def on_delete_button_clicked(self):
        if not self.locate_city_codes:
            return
        len_before = len(self.locate_city_codes)
        for i in range(self.listModel_2.rowCount()-1, -1, -1):
            if self.listModel_2.item(i).checkState() == QtCore.Qt.Checked:
                self.locate_city_codes.pop(i)
        len_after = len(self.locate_city_codes)
        if len_before == len_after:
            return
        self.saveAndApplyChanges()
        self.resetListView_2()
        pass

    def saveAndApplyChanges(self):
        success = self.model.saveUserClientFilter()
        if not success:
            QMessageBox.about(self, '保存失败', '保存修改失败，请重试。')
            return
        # self.edit_used = True
        self.model = GeoModel()
        self.model.loadUserClientFilter()
        self.locate_city_codes = self.model.client_dict[self.locate]

    def on_manage_button_clicked(self):
        dialog = GeoLocateManage(self)
        locate_edited = dialog.exec_()
        if locate_edited:
            self.model = GeoModel()
            self.comboBox_2.clear()
            self.comboBox_2.addItems(self.model.locates)
            # self.locate = self.comboBox_2.currentText()
            # self.locate_city_codes = self.model.client_dict[self.locate]
            self.resetListView_2()
            self.edit_used = True#修改已经发生

    def on_check_all_cities(self):
        if self.checkBox.isChecked():
            for i in range(self.listView.model().rowCount()):
                self.listModel.item(i).setCheckState(QtCore.Qt.Checked)
        else:
            for i in range(self.listView.model().rowCount()):
                self.listModel.item(i).setCheckState(QtCore.Qt.Unchecked)

    def on_check_all_cities_2(self):
        if self.checkBox_2.isChecked():
            for i in range(self.listView_2.model().rowCount()):
                self.listModel_2.item(i).setCheckState(QtCore.Qt.Checked)
        else:
            for i in range(self.listView_2.model().rowCount()):
                self.listModel_2.item(i).setCheckState(QtCore.Qt.Unchecked)
        pass

    def handleItemPressed(self, *args):
        index = args[0]
        # print(index.model())
        # print(args)
        item = index.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def closeEvent(self, QCloseEvent):
        if self.edit_used:
            self.accept()
        else:
            self.reject()
        pass


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mainwindow = QMainWindow(parent=None)
    mainwindow.setObjectName("MainWindow")
    mainwindow.resize(887, 600)
    centralwidget = QWidget(mainwindow)
    centralwidget.setObjectName("centralwidget")
    mainwindow.show()
    dialog = GeoFilterEditor(parent=mainwindow)

    dialog.exec_()
    sys.exit(app.exec_())
