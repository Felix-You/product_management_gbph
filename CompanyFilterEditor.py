from CompanyFilterEditorUi import Ui_Dialog
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from ID_Generate import Snow
import sys,copy
import time
from CompanyGroupManage import CompanyGroupManage
from DataCenter import *
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5 import QtCore

class CompanyFilterEditor(QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        '''
        listView:行政区城市信息列表视图
        listView_2:自定义区域城市列表视图
        '''
        super(CompanyFilterEditor,self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.model = CompanyGroupModel()
        self.geo_model = GeoModel()
        self.setWindowTitle('自定义分组')
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)
        self.comboBox.setEditable(True)
        self.comboBox.lineEdit().setPlaceholderText('请选择省份')
        self.comboBox.setPlaceholderText('请选择省份')
        self.comboBox.setCurrentIndex(-1)
        self.comboBox.addItems(map(lambda X: X[1],self.geo_model.getProvinceItems()))
        self.comboBox_3.setEditable(True)
        self.comboBox_3.lineEdit().setPlaceholderText('城市')
        self.comboBox_3.setPlaceholderText('城市')
        self.comboBox_3.setCurrentIndex(-1)
        # self.comboBox_3.addItems(map(lambda X: X[1],self.geo_model.getCityItems()))

        self.group_company_ids = None
        self.comboBox_2.setEditable(True)
        self.comboBox_2.setCurrentIndex(-1)
        self.comboBox_2.lineEdit().setPlaceholderText(u'设置分组')
        self.comboBox_2.setPlaceholderText(u'设置分组')
        self.comboBox_2.addItems(self.model.groups)

        self.cities = None#行政区城市信息(代码，名称) 列表
        self.companies = []
        self.comboBox.currentIndexChanged.connect(self.on_province_change)
        self.comboBox_3.currentIndexChanged.connect(self.on_city_change)
        self.group_selected = self.comboBox_2.currentText()

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
        self.checkBox.clicked.connect(self.on_check_all_comapanies)
        self.checkBox_2.clicked.connect(self.on_check_all_comapanies_2)
        self.edit_used = False

    def on_province_change(self, index_1):
        '''如果设置了省份，则显示该省份的所有公司'''
        if index_1 == -1 :
            return
        self.current_province_code = list(self.geo_model.getProvinceItems())[index_1][0]
        self.cities = list(self.geo_model.getCityItems(province_code=self.current_province_code)) # 城市代码与名称对
        self.comboBox_3.setCurrentIndex(-1)
        self.comboBox_3.clear()
        self.comboBox_3.addItems([city[1] for city in self.cities])
        self.companies = self.model.getCompanyFromProvinceCode(self.current_province_code)
        self.initListView()

    def on_city_change(self, index):
        '''如果设置了城市，则单独显示该城市的所有公司'''
        if index == -1:
            return
        city_code = self.cities[index][0]
        self.companies = self.model.getCompanyFromCityCode(city_code=city_code,province_code=self.current_province_code)
        self.initListView()

    def initListView(self):
        self.listModel.clear()
        for i, company in enumerate(self.companies):
            # self.city_codes.append(city[0])
            self.listModel.setItem(i,0,QStandardItem(company[1]))
            self.listModel.item(i,).setCheckState(QtCore.Qt.Unchecked)
            self.listModel.item(i,).setEditable(False)

    def initListView_2(self):
        current_index = self.comboBox_2.currentIndex()
        if current_index == -1:
            return
        self.group = self.comboBox_2.currentText()
        # self.locate_city_codes = copy.deepcopy(city_codes)
        self.group_company_ids = self.model.company_dict[self.group]
        for i, _id in enumerate(self.group_company_ids):
            self.listModel_2.setItem(i,0,QStandardItem(self.model.getCompanyNameFromId(_id)))
            self.listModel_2.item(i,).setCheckState(QtCore.Qt.Unchecked)
        pass

    def resetListView_2(self):
        self.listModel_2.clear()
        self.group = self.comboBox_2.currentText()
        #重置
        if not self.group:
            self.group_company_ids = None
            return
        else:
            self.group_company_ids = self.model.company_dict[self.group]#列表地址引用
        for i, _id in enumerate(self.group_company_ids):
            self.listModel_2.setItem(i,0,QStandardItem(self.model.getCompanyNameFromId(_id)))
            self.listModel_2.item(i,).setCheckState(QtCore.Qt.Unchecked)
        self.listView_2.setModel(self.listModel_2)
        pass

    def on_add_button_clicked(self):
        if not self.companies or self.group_company_ids is None:
            return
        len_before = len(self.group_company_ids)#
        for i in range(self.listModel.rowCount()):
            if self.listModel.item(i).checkState() == QtCore.Qt.Checked:
                if self.companies[i][0] in self.group_company_ids:#已经存在的不添加
                    continue
                else:
                    self.group_company_ids.append(self.companies[i][0])
        len_after = len(self.group_company_ids)
        if len_before == len_after:#没有添加城市
            return
        # print('self.locate_city_codes_after', self.locate_city_codes)
        self.saveAndApplyChanges()
        self.resetListView_2()
        pass

    def on_delete_button_clicked(self):
        if not self.group_company_ids:
            return
        len_before = len(self.group_company_ids)
        for i in range(self.listModel_2.rowCount()-1, -1, -1):
            if self.listModel_2.item(i).checkState() == QtCore.Qt.Checked:
                self.group_company_ids.pop(i)
        len_after = len(self.group_company_ids)
        if len_before == len_after:
            return
        self.saveAndApplyChanges()
        self.resetListView_2()
        pass

    def saveAndApplyChanges(self):
        success = self.model.saveCompanyGroupFilter()
        if not success:
            QMessageBox.about(self, '保存失败', '保存修改失败，请重试。')
            return
        self.edit_used = True
        self.model = CompanyGroupModel()
        self.group_company_ids = self.model.company_dict[self.group]#列表地址引用

    def on_manage_button_clicked(self):
        dialog = CompanyGroupManage(self)
        group_edited = dialog.exec_()
        if group_edited:
            self.model = CompanyGroupModel()
            self.comboBox_2.clear()
            self.comboBox_2.addItems(self.model.groups)
            # self.locate = self.comboBox_2.currentText()
            # self.locate_city_codes = self.model.client_dict[self.locate]
            self.resetListView_2()
            self.edit_used = True#修改已经发生

    def on_check_all_comapanies(self):
        if self.checkBox.isChecked():
            for i in range(self.listView.model().rowCount()):
                self.listModel.item(i).setCheckState(QtCore.Qt.Checked)
        else:
            for i in range(self.listView.model().rowCount()):
                self.listModel.item(i).setCheckState(QtCore.Qt.Unchecked)

    def on_check_all_comapanies_2(self):
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

