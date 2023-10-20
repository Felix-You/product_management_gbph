from CompanyEditorUi import Ui_CompanyEditorUi
from projectTabBar import ProjectTabBar
from PyQt5.QtWidgets import QTabBar, QTextEdit , QMessageBox,QTableWidget,QInputDialog,QDialog,QDialogButtonBox
from PyQt5.QtCore import pyqtSignal,Qt,QEvent,QObject , QAbstractTableModel,QModelIndex
from PyQt5.QtGui import QColor,QPainter,QPolygon,QMouseEvent,QStandardItemModel,QStandardItem
import ConnSqlite as CS
from PyQt5 import QtWidgets,QtGui,QtCore
import time,datetime,re, types,json
from DataCenter import GTaskCmd,TaskType,GMemoCmd,GProjectCmd,GMeetingCmd,BroadcastSpace,GeoModel, CompanyLog
from core.KitModels import Staff, Person
from core import KitModels
import DataCenter, RedefinedWidget, DataView
from ID_Generate import Snow


def new_wheelEvent(self,e):
    e.ignore()
    pass

class CompanyEditorTabBar(QTabBar,Ui_CompanyEditorUi):

    def __init__(self, company, parent , parent_widget = None):
        super(CompanyEditorTabBar, self).__init__(parent_widget)
        self.setupUi(self)
        self.parent = parent
        self.company = company
        self.geo_model = GeoModel()
        self.person_id = Snow('psn')
        self.log_id = Snow('clg')
        self.tableView_3.clicked.connect(self.handleItemPressed)
        self.tableView.clicked.connect(self.handleItemPressed)
        self.pushButton_2.clicked.connect(self.on_save_clicked)
        self.pushButton_8.clicked.connect(self.on_add_personnel_clicked)
        self.pushButton_7.clicked.connect(self.on_delete_personnel_clicked)
        self.pushButton_4.clicked.connect(self.on_add_log_clicked)
        self.pushButton_3.clicked.connect(self.on_delete_log_clicked)
        self.pushButton_6.clicked.connect(self.on_upload_file_clicked)
        self.pushButton_5.clicked.connect(self.on_delete_file_clicked)
        self.pushButton_9.clicked.connect(self.on_company_meeting_log)
        self.tableView.doubleClicked.connect(self.on_tableView_log_doubleClicked)
        self.comboBox_2.wheelEvent = types.MethodType(new_wheelEvent,self.comboBox_2)
        self.comboBox_2.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.comboBox_3.wheelEvent = types.MethodType(new_wheelEvent,self.comboBox_3)
        self.comboBox_3.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.comboBox_4.wheelEvent = types.MethodType(new_wheelEvent,self.comboBox_4)
        self.comboBox_4.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.comboBox_5.wheelEvent = types.MethodType(new_wheelEvent,self.comboBox_5)
        self.comboBox_5.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setCompanyName()
        self.initGeoWidgets()
        self.setGeoComboboxes()
        self.setPlainTextInfo()
        self.setPersonnelInfo()
        self.setLogInfo()

    def initAllData(self):
        #
        self.setGeoComboboxes()
        self.setCompanyName()
        self.setPlainTextInfo()
        self.setPersonnelInfo()
        self.setLogInfo()
        pass

    def setCompanyName(self):
        self.lineEdit.setText(self.company.short_name)
        if self.company.enterprise_name:
            self.textEdit.setText(self.company.enterprise_name)

    # def initGeoWidgets(self):

    def initGeoWidgets(self): # 此函数每次调用都会触发comboBox的currentIndexChanged信号，导致company类的有关属性被修改。
        self.comboBox_2.lineEdit().setPlaceholderText('国家/地区/Country')
        self.comboBox_3.lineEdit().setPlaceholderText('省/州/State')
        self.comboBox_4.lineEdit().setPlaceholderText('市/City')
        self.comboBox_5.lineEdit().setPlaceholderText('县/Town')
        self.comboBox_2.setCurrentIndex(-1)
        self.comboBox_3.setCurrentIndex(-1)
        self.comboBox_4.setCurrentIndex(-1)
        self.comboBox_5.setCurrentIndex(-1)
        self.comboBox_3.currentIndexChanged.connect(self.on_province_change)
        self.comboBox_4.currentIndexChanged.connect(self.on_city_change)
        self.comboBox_5.currentIndexChanged.connect(self.on_town_change)
        self.init_province = self.company.province
        self.init_city = self.company.city
        self.init_town = self.company.town
        self.provinces = self.geo_model.getProvinceItems()
        self.cities = None
        self.towns = None
        self.comboBox_3.addItems([province[1] for province in self.provinces])


    def setGeoComboboxes(self):
        if self.init_province :
            current_index = self.geo_model.getProvinceIndex(self.init_province)
            if current_index is None:
                self.comboBox_4.setCurrentIndex(-1)
                self.comboBox_5.setCurrentIndex(-1)
                return
            self.comboBox_3.setCurrentIndex(current_index)
            # self.cities = self.geo_model.getCityItems(self.init_province)
            # if self.cities:
            #     self.comboBox_4.addItems([city[1] for city in self.cities])
        else:
            self.comboBox_4.setCurrentIndex(-1)
            self.comboBox_5.setCurrentIndex(-1)
            return
        if self.init_city :
            current_index = self.geo_model.getCityIndex(self.init_city, province_code= self.init_province)
            if current_index is None:
                self.comboBox_5.setCurrentIndex(-1)
                return
            self.comboBox_4.setCurrentIndex(current_index)
            # self.towns = self.geo_model.getTownItems(self.init_city, self.init_province)
            # if self.towns:
            #     self.comboBox_5.addItems([town[1] for town in self.towns])
        else:
            self.comboBox_5.setCurrentIndex(-1)
            return
        if self.init_town:
            current_index = self.geo_model.getTownIndex(self.init_town,city_code=self.init_city,
                                                        province_code=self.init_province)
            if current_index is None:
                self.comboBox_5.setCurrentIndex(-1)
                return
            self.comboBox_5.setCurrentIndex(current_index)

    def on_province_change(self):
        print('wheel_changeP',self.comboBox_3.currentIndex())
        self.company.province = self.provinces[self.comboBox_3.currentIndex()][0]
        #清空后列数据
        self.company.city = None
        self.company.town = None
        #重置后列控件
        self.comboBox_4.clear()
        self.comboBox_5.clear()
        self.comboBox_4.setCurrentIndex(-1)
        self.comboBox_5.setCurrentIndex(-1)
        #初始化后列数据和控件
        self.cities = self.geo_model.getCityItems(self.company.province)
        if self.cities:
            self.comboBox_4.addItems([city[1] for city in self.cities])
        self.towns = None
        # self.setGeoComboboxes()

    def on_city_change(self):
        # print('wheel_changeC',self.comboBox_4.currentIndex())
        if self.comboBox_4.currentIndex() == -1:
            return
        self.company.city = self.cities[self.comboBox_4.currentIndex()][0]
        #清空后列数据
        self.company.town = None
        #重置后列控件
        self.comboBox_5.clear()
        self.comboBox_5.setCurrentIndex(-1)
        #初始化后列数据和控件
        self.towns = self.geo_model.getTownItems(self.company.city, province_code=self.company.province)
        # print('self.towns',self.towns)
        if self.towns:
            self.comboBox_5.addItems([town[1] for town in self.towns])

        # self.setGeoComboboxes()

    def on_town_change(self):

        index_set_new = self.comboBox_5.currentIndex()
        print('wheel_changeT',self.comboBox_5.currentIndex())
        if index_set_new == -1:
            return
        self.company.town = self.towns[index_set_new][0]

    def setPlainTextInfo(self):
        '''把纯文本的字段加载出来'''
        self.textEdit.setText(self.company.enterprise_name)
        self.textEdit_3.setText(self.company.detailed_location)
        self.textEdit_4.setText(self.company.telephone)
        self.textEdit_5.setText(self.company.email)
        self.textEdit_2.setText(self.company.desc)
        self.lineEdit_2.setText(self.company.person_responsible)

    def getPlainTextInfo(self):
        self.company.short_name = self.lineEdit.text()
        self.company.enterprise_name = self.textEdit.toPlainText() if self.textEdit.toPlainText().strip() else None
        self.company.detailed_location = self.textEdit_3.toPlainText() if self.textEdit_3.toPlainText().strip() else None
        self.company.telephone = self.textEdit_4.toPlainText() if self.textEdit_4.toPlainText().strip() else None
        self.company.email = self.textEdit_5.toPlainText() if self.textEdit_5.toPlainText().strip() else None
        self.company.desc = self.textEdit_2.toPlainText() if self.textEdit_2.toPlainText().strip() else None
        self.company.person_responsible = self.lineEdit_2.text() if self.lineEdit_2.text()  else None

    def setPersonnelInfo(self):
        self.listView_model = QStandardItemModel()
        self.listView_model.dataChanged.connect(self.on_personnel_changed)
        self.listView_model.rowsRemoved.connect(self.on_personnel_delete)
        self.listView_model.setHeaderData(0, Qt.Horizontal, '姓名', role=2)
        self.listView_model.setHeaderData(1, Qt.Horizontal, '职位', role=2)
        self.listView_model.setHeaderData(2, Qt.Horizontal, '电话', role=2)
        self.listView_model.setHorizontalHeaderLabels(['姓名', '职位', '电话'])
        # self.listView.
        for i, staff in enumerate(self.company.personnel_class.staff):
            staff.company = self.company.short_name
            staff.company_id = self.company._id
            self.listView_model.setItem(i,0,QStandardItem(staff.name))
            self.listView_model.setItem(i,1,QStandardItem(staff.tittle))
            self.listView_model.setItem(i,2,QStandardItem(staff.telephone))
            # self.listView_model.item(i, 1).setData(person.tittle)
            # self.listView_model.item(i, 2).setData(person.telephone)
            self.listView_model.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
            self.listView_model.item(i,0).setEditable(False)
            self.listView_model.item(i, 1).setCheckable(False)
            self.listView_model.item(i, 2).setCheckable(False)

        self.tableView_3.setModel(self.listView_model)
        header_view =  self.tableView_3.horizontalHeader()
        header_view.setStretchLastSection(True)
        pass

    def setLogInfo(self):
        self.tableView_log_model = QStandardItemModel()
        self.tableView_log_model.setHeaderData(0, Qt.Horizontal, '时间', role=2)
        self.tableView_log_model.setHeaderData(1, Qt.Horizontal, '记录', role=2)

        self.tableView_log_model.dataChanged.connect(self.on_log_changed)
        self.tableView_log_model.rowsRemoved.connect(self.on_log_deleted)

        # header_view.setS
        self.tableView_log_model.setHorizontalHeaderLabels(['时间', '记录'])
        for i, log in enumerate(self.company.logs):
            create_time = datetime.datetime.strptime(log.create_time[:19],'%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
            self.tableView_log_model.setItem(i,0,QStandardItem(create_time))
            self.tableView_log_model.setItem(i,1,QStandardItem(log.log_desc))
            self.tableView_log_model.item(i).setCheckState(QtCore.Qt.Unchecked)
            self.tableView_log_model.item(i,0).setEditable(False)
            self.tableView_log_model.item(i,1).setEditable(False)
        self.tableView.setModel(self.tableView_log_model)
        # self.tableView.setColumnWidth(0,900)
        header_view = self.tableView.horizontalHeader()
        # header_view.setSectionResizeMode(QHeaderView.Stretch)
        header_view.setStretchLastSection(True)
        # header_view.setSectionResizeMode()
        self.tableView.setColumnWidth(0, 200)
        pass

    def setFileInfo(self):
        pass

    def getFileInfo(self):
        pass

    def on_add_personnel_clicked(self):
        '''增加一个人员信息，必须先输入姓名'''
        name, ok  = QInputDialog.getText(self,'姓名', '请输入姓名:')
        if ok:
            is_new_person = True
            # self.listView_model.appendRow()
            find_person = Person.findPerson(name)
            if not find_person:
                person_id = self.person_id.get()
                pass
            else:
                name_with_log = ['以下都不是']
                ids = []
                for person_info in find_person:
                    find_person_log = KitModels.PersonLog.findPersonLog(person_info['_id'])#根据person_id查询记录
                    if find_person_log:
                        job_title = find_person_log[-1]['job_title'] if find_person_log[-1]['job_title'] else ''
                        log_text = name + '--' + find_person_log[-1]['conn_company_name'] + '--' + job_title
                        name_with_log.append(log_text)
                        ids.append(person_info['_id'])
                    else:
                        continue
                index, ok = RedefinedWidget.ComboBoxDialog.getIndex(self,'任职记录','发现同名人员任职记录，\n请确认是否为以下人员：',
                                                                    name_with_log)
                if not ok:
                    return
                if index == 0 or index == -1:#选择 以下都不是， 或者不选
                    person_id = self.person_id.get()
                else:
                    is_new_person = False
                    person_id = ids[index-1]
            new_person = Staff(person_id)
            new_person.name = name
            if not is_new_person:
                new_person.loadPersonInfo()
            new_person.company = self.company.short_name
            new_person.company_id = self.company._id
            # new_person.modified = True
            self.company.personnel_class.staff.append(new_person)
            #如果是删除之后又添加回来，则把删除记录去掉
            for i in reversed(range(len(self.company.personnel_class.staff_adjusted))):
                if person_id == self.company.personnel_class.staff_adjusted[i]._id:
                    self.company.personnel_class.staff_adjusted.pop(i)
            self.company.personnel_class.staff_adjusted.append(new_person)
            #这个地方，会产生一个dataChanged信号，通过槽函数来修改这个new_person实例的name属性
            self.listView_model.setItem(self.listView_model.rowCount(),0, QStandardItem(name))
            self.listView_model.setItem(self.listView_model.rowCount()-1,2, QStandardItem(new_person.telephone))
            self.listView_model.item(self.listView_model.rowCount()-1).setCheckState(Qt.Unchecked)
        pass

    def on_personnel_changed(self,qindex_topleft,qindex_bottomright,qvector):
        #跟人员相关的信息发生修改
        if not qvector:#qvector == []代表初始化model的时候
            return
        row = qindex_topleft.row()
        column  = qindex_topleft.column()
        text = qindex_topleft.data(role = 2)
        if column == 0:#name
            self.company.personnel_class.staff[row].name = text
        elif column == 1:#tittle
            self.company.personnel_class.staff[row].tittle = text
            self.company.personnel_class.staff[row].modified = True
        elif column == 2:#telephone
            if not text:#不允许删除联系方式
                return
            text = text.strip()
            #校验电话号码的合法性
            invalid_tel = text.lstrip('+')
            invalid_tel = re.sub('[0-9]','',invalid_tel)
            if invalid_tel and (invalid_tel[0] == '-' or invalid_tel[-1] == '-'):
                pass
            else:
                invalid_tel = re.sub('[ -]','', invalid_tel)
            if invalid_tel:
                QMessageBox.warning(self, '电话号码' , '请输入有效的电话号码！')
                item = qindex_topleft.model().item(row, column)
                item.setData(None, role = 2)##在dataChanged的槽内使用setData是危险操作

                return
            self.company.personnel_class.staff[row].telephone = text
            self.company.personnel_class.staff[row].modified = True

    def on_personnel_delete(self,qindex, first, last):
        print('personnel收到rowsremoved信号，Qindex.data(2)',qindex.data(role = 2))
        deleted = self.company.personnel_class.staff.pop(first)
        deleted_name = deleted.name
        not_in_service = QMessageBox.question(self,'离职','人员 %s 是否离职？'%deleted_name, QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
        if not_in_service == QMessageBox.Yes:
            deleted.in_service = False
        #如果发现删除的人员是刚刚添加的，则直接忽略
        for i in reversed(range(len(self.company.personnel_class.staff_adjusted))):
                if deleted._id == self.company.personnel_class.staff_adjusted[i]._id:
                    self.company.personnel_class.staff_adjusted.pop(i)
                    return
        self.company.personnel_class.staff_adjusted.append(deleted)

    def on_delete_personnel_clicked(self):
        delete = QMessageBox.question(self,'删除', '删除后不可恢复，\n确认删除？' , QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
        if delete == QMessageBox.No:
            return
        for i in reversed(range(self.listView_model.rowCount())):
            if self.listView_model.item(i).checkState() == QtCore.Qt.Checked:
                self.listView_model.removeRow(i)
        pass

    def on_add_log_clicked(self):
        text, ok = QInputDialog.getMultiLineText(self, '记录内容', '请输入记录内容')
        row_count = self.tableView_log_model.rowCount()
        datetime_now = datetime.datetime.now()
        if ok:
            new_log_id = self.log_id.get()
            new_log = CompanyLog(company_catelog='client')
            new_log._id = new_log_id
            new_log.create_time = datetime_now.strftime('%Y-%m-%d %H:%M:%S')[:19]
            new_log.log_desc = text
            new_log.company_id = self.company._id
            self.company.logs.append(new_log)
            item0 = QStandardItem(datetime_now.strftime("%Y-%m-%d"))
            item0.setEditable(False)
            item1 = QStandardItem(text)
            item1.setEditable(False)
            self.tableView_log_model.appendRow([item0,item1])
            self.tableView_log_model.item(row_count).setCheckState(Qt.Unchecked)
        pass

    def on_tableView_log_doubleClicked(self,qindex):
        row = qindex.row()
        column = qindex.column()
        if column != 1:#双击的不是记录文本单元格
            return
        item = qindex.model().item(row, column)
        former_text = qindex.data(role = 2)
        # dialog = QInputDialog(self,Qt.WindowCloseButtonHint)
        # dialog.setFixedWidth(400)
        # dialog.setInputMode(QInputDialog.TextInput)
        # new_text, ok = dialog.getMultiLineText(dialog,'记录内容','修改记录内容',flags=Qt.WindowCloseButtonHint, text=former_text,inputMethodHints=Qt.ImhMultiLine,)
        dialog = QDialog(self,Qt.WindowCloseButtonHint)
        dialog.setWindowTitle('记录内容')
        dialog.setMinimumSize(300,250)
        VLayout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel('修改公司记录：',dialog)
        TextEdit= QtWidgets.QPlainTextEdit(former_text,dialog)
        ok_cancel_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, dialog)
        ok_cancel_button.button(QDialogButtonBox.Cancel).setDefault(True)
        ok_cancel_button.accepted.connect(lambda : item.setData(TextEdit.toPlainText(),role = 2))
        ok_cancel_button.accepted.connect(dialog.accept)
        ok_cancel_button.rejected.connect(dialog.reject)
        VLayout.addWidget(label)
        VLayout.addWidget(TextEdit)
        VLayout.addWidget(ok_cancel_button)
        dialog.exec_()

    def on_log_changed(self,qindex_topleft,qindex_bottomright,qvector):
        if not qvector:#[]代表的是整个QStandarItem数据改变
            return
        row = qindex_topleft.row()
        column  = qindex_topleft.column()
        text = qindex_topleft.data(role = 2)
        if column == 0:#log_desc
            return
        elif column == 1:
            self.company.logs[row].log_desc = text

    def on_log_deleted(self, qindex, first, last):
        # print('logs收到rowsremoved信号，Qindex.data(2)',qindex.data(role = 2))
        print('qindex',qindex.row(),qindex.column())
        print('first=',first,'last=',last)
        self.company.logs.pop(first)

    def on_delete_log_clicked(self):
        delete = QMessageBox.question(self,'删除', '删除后不可恢复，\n确认删除？', QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
        if delete == QMessageBox.No:
            return
        for i in range(self.tableView_log_model.rowCount()-1, -1, -1):
            if self.tableView_log_model.item(i).checkState() == QtCore.Qt.Checked:
                self.tableView_log_model.removeRow(i)
        pass

    def on_upload_file_clicked(self):
        pass

    def on_delete_file_clicked(self):
        pass

    def on_save_clicked(self):
        #校验公司名称是否改变，以及改变后的命名是否合法
        do_change_company_short_name = False
        if self.lineEdit.text() != self.company.short_name:
            message = QMessageBox(self)
            message.setWindowFlags(Qt.WindowCloseButtonHint)
            change_name = message.question(self, '公司名称', '您确定要改变公司的名称吗？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
            if change_name == QMessageBox.No:
                self.lineEdit.setText(self.company.short_name)
                self.lineEdit.selectAll()
                return
            else:
                valid_company_name = re.sub('[\W-]' , '' , self.lineEdit.text())
                valid_company_name = re.sub('[0-9]','',valid_company_name)
                if not valid_company_name:# 去除所有非法符号后, 未输入有效字符
                    QtWidgets.QMessageBox.about(self , '无效名称' , '该公司名称无效，\n\n请重新输入！')
                    self.lineEdit.setText(self.company.short_name)
                    self.lineEdit.selectAll()
                    return
                else:
                    do_change_company_short_name = True
                    pass

        #判断行政区是否有输入错误或者不完整的情况。有输入字符，并且字符找不到-->检验失败
        if (self.comboBox_2.lineEdit().text() and
                self.comboBox_2.findText(self.comboBox_2.lineEdit().text(),flags=Qt.MatchExactly) < 0)\
            or (self.comboBox_3.lineEdit().text() and
                self.comboBox_3.findText(self.comboBox_3.lineEdit().text(),flags=Qt.MatchExactly) < 0)\
            or (self.comboBox_4.lineEdit().text() and
                 self.comboBox_4.findText(self.comboBox_4.lineEdit().text(), flags=Qt.MatchExactly) < 0)\
            or (self.comboBox_5.lineEdit().text() and
                 self.comboBox_5.findText(self.comboBox_5.lineEdit().text(), flags=Qt.MatchExactly) < 0):
            #判断行政区是否有输入错误或者不完整的情况。有输入字符，并且字符找不到-->检验失败
            message = QMessageBox(self)
            message.setWindowFlags(Qt.WindowCloseButtonHint)
            message.warning(self, '检查地址', '行政区信息有误，请检查！')
            return
        else:
            pass

        self.getPlainTextInfo()
        ok = self.company.saveAllData()
        if do_change_company_short_name:
            CS.updateSqliteCells('proj_list', conditions={'client_id': self.company._id},
                             update_fields={'client':self.company.short_name})
            self.parent.setClientCompleter()
        if ok :
            QMessageBox.about(self, '完成', '%s \n\n保存成功！'%self.company.short_name)
        self.company.personnel_class.staff_adjusted.clear()

        # todo:这里其实需要改进，把修改其他tabBar的命令封装起来
        cmd = DataCenter.GPersonnelCmd('update', self.company._id) # 对人员的修改
        self.parent.listener.accept(cmd)

        # for record in self.parent.tabBarAdded:
        #     if isinstance(record[1], ProjectTabBar) and record[1].project.client_id == self.company._id:
        #         record[1].initPersonnelSet()

    def on_cancel_clicked(self):
        pass

    def on_company_meeting_log(self):
        company_id = self.company._id
        compamy_meetings = CS.getLinesFromTable(self.company.meeting_log_table,
                                                conditions={'conn_company_id':company_id},order=['create_time'])
        fields = compamy_meetings.pop()
        if not compamy_meetings:
            QMessageBox.about(self, '未找到', '该公司暂无会议记录。')
            return
        meeting_dates = [str(i+1)+':'+meeting[fields.index('meeting_date')] for i, meeting in enumerate(compamy_meetings)]
        input_dialog = QInputDialog(self,QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)
        select , ok = input_dialog.getItem(self, '请选择', '会议日期', meeting_dates)
        if not ok :
            return
        index = int(select.split(':')[0]) - 1
        company_meeting = compamy_meetings[index]
        meeting_factors = dict(zip(fields,company_meeting))# 会议全部要素
        meeting_id = meeting_factors['_id']
        meeting_info = json.loads(meeting_factors['meeting_info'])# 会议人员和议题信息
        # if meeting_info['project_log'] and 'status_log_id' in meeting_info['project_log'][0].keys():#按照新的方式存储的会包含_id字段
        #     text = self.company_meeting_log_new_text( meeting_factors,meeting_info)
        # else:
        text = self.company_meeting_log_old_text( meeting_factors,meeting_info)
        self.dialog = QDialog(self,QtCore.Qt.Window|QtCore.Qt.WindowMinMaxButtonsHint|QtCore.Qt.WindowCloseButtonHint)
        self.dialog.setMinimumSize(800*DataView.DF_Ratio, 800*DataView.DF_Ratio)
        self.dialog.setWindowTitle('会议记录')
        layOut = QtWidgets.QGridLayout(self.dialog)
        self.dialog.setLayout(layOut)
        textBrowser = QtWidgets.QTextBrowser(self.dialog)
        layOut.addWidget(textBrowser)
        button = QtWidgets.QPushButton(self.dialog)
        button.setText('再次编辑')
        button.clicked.connect(lambda :self.edit_meeting(meeting_id))
        layOut.addWidget(button)
        textBrowser.setText(text)
        self.dialog.show()

    def edit_meeting(self, id):
        ok = QMessageBox.question(self,'再次编辑','确定再次编辑此次会议？',QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
        if ok == QMessageBox.No:
            return
        self.dialog.close()
        client_name = self.company.short_name
        client_id = self.company._id
        self.parent.showMeetingDialog(client_name, client_id, id)

    def company_meeting_log_new_text(self, meeting_factors,meeting_info):
        meeting_project_log = meeting_info['project_log']
        text = ''
        text += '<b>会议日期：</b>' + meeting_factors['meeting_date'] + '<br /><br />'
        if meeting_factors['company_desc']:
            text += '公司情况：<br />' + meeting_factors['company_desc'] + '<br /><br />'
        text += '<b>参会人员：\n'+meeting_info['visited_people'] +  '</b><br />'
        text += '%s人员：'%DataView.USER_COMPANY_SHORT_NAME + meeting_info['our_people'] + '<br />'
        pass

    def company_meeting_log_old_text(self, meeting_factors, meeting_info):
        meeting_project_log = meeting_info['project_log']
        text = ''
        text += '<b>会议日期：</b>' + meeting_factors['meeting_date'] + '<br /><br />'
        if meeting_factors['company_desc']:
            try:
                company_desc = json.loads(meeting_factors['company_desc'])
                company_desc_text = company_desc['text']
            except:
                company_desc_text = meeting_factors['company_desc']
            text += '公司情况：<br />' + company_desc_text + '<br /><br />'
        try:
            visited_people_data = json.loads(meeting_info['visited_people'])
            person_in_meeting = []
            person_id_in_meeting = []
            for i, personnel_data in enumerate(visited_people_data):
                person_in_meeting.append(personnel_data['name'] + ' ' +personnel_data['tittle'])
                person_id_in_meeting.append(personnel_data['_id'])
            person_in_meeting_text = '<br />'.join(person_in_meeting)
        except:
            person_in_meeting_text = meeting_info['visited_people']
        text += '<b>参会人员：<br />'+person_in_meeting_text +  '</b><br />'
        text += '%s人员：'%DataView.USER_COMPANY_SHORT_NAME + meeting_info['our_people'] + '<br />'
        for j, item in enumerate(meeting_project_log):
            text += '<br /><b>' + str(j + 1) +'. '+ item['product'] + '</b><br />【项目情况】<br />'
            text += item['meeting_desc'] + '<br />'
            if item['task_desc']:
                text += '【需跟进】<br />' + item['task_desc'] +'<br />'
            if item['memo_desc']:
                text += '【备注】<br />' + item['memo_desc'] +'<br />'
        return text.replace('\n', '<br />')

    def handleItemPressed(self, *args):
        index = args[0]#QIndex
        # print(index.model())
        # print(args)
        row = index.row()
        item = index.model().item(row, 0)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    # def Accept(self,cmd):
    #     if cmd.flag == 5 and cmd._id == self.company._id:
    #         self.initPersonnelSet()