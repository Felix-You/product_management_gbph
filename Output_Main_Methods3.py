import FilePathInit
from Output_Main_UI4 import Ui_MainWindow
from Input_Main_Methods import MeetingRecordDialog
import math, time ,datetime, RedefinedWidget, threading,types,re
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
import ConnSqlite as CS
from PyQt5.QtCore import Qt, QEvent, pyqtSignal,QStringListModel,QFile
from PyQt5 import QtGui
from FilePathInit import workingDir, userDir
from functools import wraps
from ID_Generate import Snow
from RedefinedWidget import MySlider,StatusCheckFrame,CompanyCreateDialog, DirectoryChooseBox
from Clock import AnalogClock
import DataView, DataCenter
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

class QComboBox(QComboBox):#重写鼠标滚轮事件，禁用滚轮
    def wheelEvent(self, QWheelEvent):
        pass

class QTextEdit(QTextEdit):
    def __init__(self,txt = None):
        super().__init__()
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {"
                                                                         "width: 4px;"
                                                                   "background: transparent;"
                                                                   "border: 0px;"
                                                                   "margin: 0px 0px 0px 0px;"
                                                                   "}"
                                                                   "QScrollBar::handle:vertical"
                                                                   "{"
                                                                   "background:silver;"
                                                                   "border-radius:2px;"
                                                                   "}"
                                                                   "QScrollBar::handle:vertical:hover"
                                                                   "{"
                                                                   "background:lightskyblue;"
                                                                   "border-radius:2px;"
                                                                   "}"
                                                                   "QScrollBar::add-line:vertical"
                                                                   "{"
                                                                   "background: transparent;"
                                                                   "margin: 0px;"
                                                                   "border-width: 0px;"
                                                                   "height:0px;width:0px;"
                                                                   "subcontrol-position:bottom;"
                                                                   "subcontrol-origin: margin;"
                                                                   "}"
                                                                   "QScrollBar::sub-line:vertical"
                                                                   "{"
                                                                    "background: transparent;"
                                                                   "margin: 0px;"
                                                                   "border-width: 0px;"
                                                                   "height:0px;width:0px;"
                                                                   "subcontrol-position:top;"
                                                                   "subcontrol-origin: margin;"
                                                                   "}")
        if txt != None:
            self.setText(txt)

class MyQTextEdit(QTextEdit):#自定义textEdit的鼠标双击事件

    # 自定义单击信号
    #clicked = pyqtSignal()
    # 自定义双击信号
    DoubleClicked = pyqtSignal()
    LoseFocus = pyqtSignal()
    def __int__(self):
        super().__init__()

    # 重写鼠标双击事件
    def mouseDoubleClickEvent(self, e):  # 重写双击事件
        self.DoubleClicked.emit()

    '''def focusOutEvent(self,e):#重写失去焦点事件
        self.LoseFocus.emit()'''

class MyQTextBrowser(QTextBrowser):
    DoubleClicked = pyqtSignal()
    def __init__(self,txt = None):
        super().__init__()
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {"
                                                                         "width: 4px;"
                                                                   "background: transparent;"
                                                                   "border: 0px;"
                                                                   "margin: 0px 0px 0px 0px;"
                                                                   "}"
                                                                   "QScrollBar::handle:vertical"
                                                                   "{"
                                                                   "background:silver;"
                                                                   "border-radius:2px;"
                                                                   "}"
                                                                   "QScrollBar::handle:vertical:hover"
                                                                   "{"
                                                                   "background:lightskyblue;"
                                                                   "border-radius:2px;"
                                                                   "}"
                                                                   "QScrollBar::add-line:vertical"
                                                                   "{"
                                                                   "background: transparent;"
                                                                   "margin: 0px;"
                                                                   "border-width: 0px;"
                                                                   "height:0px;width:0px;"
                                                                   "subcontrol-position:bottom;"
                                                                   "subcontrol-origin: margin;"
                                                                   "}"
                                                                   "QScrollBar::sub-line:vertical"
                                                                   "{"
                                                                    "background: transparent;"
                                                                   "margin: 0px;"
                                                                   "border-width: 0px;"
                                                                   "height:0px;width:0px;"
                                                                   "subcontrol-position:top;"
                                                                   "subcontrol-origin: margin;"
                                                                   "}")
        if txt != None:
            self.setText(txt)
    def mouseDoubleClickEvent(self, e):  # 重写双击事件
        self.DoubleClicked.emit()

class TypeAQTextEdit(QTextEdit):

    DoubleClicked = pyqtSignal()
    def __int__(self):
        super().__init__()

    # 重写鼠标单击事件
    #def mousePressEvent(self, QMouseEvent):  # 单击
    #    self.clicked.emit()

    # 重写鼠标双击事件
    def mouseDoubleClickEvent(self, e):  # 双击
        self.DoubleClicked.emit()

def new_focusOutEvent(self,e):
    '''重写lineEdit的focusOut事件'''
    if e.reason() == Qt.ActiveWindowFocusReason:
        return
    else:
        QLineEdit.focusOutEvent(self, e)

def time_wrapper(func):
  @wraps(func)
  def measure_time(*args, **kwargs):
    t1 = time.time()
    result = func(*args, **kwargs)
    t2 = time.time()
    t3 = float(t2) - float(t1)
    # print('t1=',t1,'t2=',t2)
    # print(f"{func.__name__} took {t3} seconds")seconds
    return result
  return measure_time

class OutputMainWindow(QtWidgets.QMainWindow, Ui_MainWindow, QComboBox):
    def __init__(self, parent=None):
        super(OutputMainWindow, self).__init__(parent)
        self.setupUi(self)
        icon = QtGui.QIcon('./icons/1_icon.png')
        # self.setWindowIcon(icon)
        self.checkDataBase()
        # self.event
        self.groupBox_3.setMinimumSize(270*DataView.DF_Ratio, 35*DataView.DF_Ratio)
        # # self.groupBox.setFixedHeight(100 * DataView.FIX_SIZE_WIDGET_SCALING)
        # self.groupBox_2.setFixedHeight(100 * DataView.FIX_SIZE_WIDGET_SCALING)
        # self.groupBox_4.setFixedHeight(100 * DataView.FIX_SIZE_WIDGET_SCALING)

        #文件路径函数
        self.working_dir = workingDir
        # self.checkInitFiles()
        self.initUserTheme(self)
        self.clock = AnalogClock()
        self.clock.setFixedSize(100*DataView.FIX_SIZE_WIDGET_SCALING, 100*DataView.FIX_SIZE_WIDGET_SCALING)
        self.clock.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        self.horizontalLayout.insertWidget(0,self.clock, 0, Qt.AlignCenter)
        # self.Layout_clock.addWidget(self.clock)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit_2.setClearButtonEnabled(True)
        self.lineEdit_2.editingFinished.connect(self.is_in_customer)
        self.lineEdit.editingFinished.connect(self.is_in_item)
        #重载focusOutEvent
        self.lineEdit_2.focusOutEvent = types.MethodType(new_focusOutEvent, self.lineEdit_2)
        self.lineEdit.focusOutEvent = types.MethodType(new_focusOutEvent, self.lineEdit)
        self.SortUporDown = True
        #按钮信号
        self.pushButton.clicked.connect(self.display_data)
        #删除原有的TabBar
        while True:
            nTab = self.tabWidget.tabBar().count()
            if nTab == 0 :
                break
            self.tabWidget.removeTab(nTab-1)
        self.over_view = DataView.OverView(self)
        self.over_view.setUi(self.tabWidget)
        self.detail_view = DataView.DetailView(self)
        self.detail_view.setUi(self.tabWidget)
        self.todo_view = DataView.ToDoView(self,self.tabWidget)
        self.todo_view.setupUi()
        # DataView.ResAdaptor.init_ui_size(self)
        self.tabWidget.setTabsClosable(True)

        self.companyFilterView = DataView.CompanyFilterView(self)
        self.companyFilterView.setBoundWidget(self.groupBox_4)
        self.companyFilterView.setupWidget()

        self.geoFilterEditorView = DataView.GeoFilterEditorView(self)#地理筛选器，用来筛选指定区域内的客户
        self.geoFilterEditorView.setBoundWidget(self.groupBox_2)
        self.geoFilterEditorView.setupWidget()


        self.chanceStatusFilter = DataView.ChanceStatusFilterView(self.groupBox)#机会标签筛选器
        self.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tabWidget.tabBar().setTabButton(1, QTabBar.RightSide, None)
        self.tabWidget.tabBar().setTabButton(2, QTabBar.RightSide, None)
        #标签复选框组信号
        self.checkBox.stateChanged.connect(self.tags_set)
        self.checkBox_2.stateChanged.connect(self.tags_set)
        self.checkBox_3.stateChanged.connect(self.tags_set)
        self.checkBox_4.stateChanged.connect(self.tags_set)
        self.tags_checked = []
        #菜单栏信号
        self.actionGeoFilterSet.triggered.connect(self.setGeoFilter)
        self.actionMeetingRecord.triggered.connect(self.startMeetingMode)
        self.actionNewCompany.triggered.connect(self.createNewCompany)
        self.actionNewProject.triggered.connect(self.createNewProject)
        self.actionCompany.triggered.connect(self.on_getCompany)
        self.actionadd_TodoUnit.triggered.connect(self.createNewTodoUnit)
        self.actionCompanyGroupSet.triggered.connect(self.setCompanyGroup)
        self.actionSetTheme.triggered.connect(self.setTheme)
        self.actionSetDatabasePath.triggered.connect(self.setDatabasePath)
        self.actionEditOfficeJobType.triggered.connect(self.editOfficeJobType)

        self.radioButton.setChecked(True)
        self.now = datetime.datetime.now()
        self.listener = DataView.Listener()
        self.listener.addObserver(self.todo_view)
        # self.radioButton_3.setEnabled(False)
        #completer
        self.setClientCompleter()
        self.setProjectCompleter()
        #检查准备打开的Tab是否已经打开
        self.tabBarAdded = []
        self.meetModeAdded = []
        self.lineEdit.setMaximumHeight(30*DataView.DF_Ratio)
        self.lineEdit_2.setMaximumHeight(30*DataView.DF_Ratio)
        self.resize(1078*DataView.DF_Ratio, 750*DataView.DF_Ratio)
        # self.setStyleSheet('QCheckBox::indicator{height:%s;width:%s;}'%(13 * DataView.DF_Ratio, 13 * DataView.DF_Ratio))
        #开启检查文件的线程
        # self.file_thread = threading.Thread(target=self.checkInitFiles())
        # self.file_thread.start()

    def checkInitFiles(self):
        if workingDir.hasUserDirectory():
            #completer
            self.setClientCompleter()
            self.setProjectCompleter()
            pass
        else:
            path, ok = RedefinedWidget.DirectorChooseBox.getDirectory(title='选择个人文件存放目录',
                                                                  hint_text='不要将个人文件放在C盘',parent=self)
            if not ok:
                return
            else:
                workingDir.createUserDirctory(path)
                workingDir.initUserFiles()
                userDir.reloadDir()
                #completer
                self.setClientCompleter()
                self.setProjectCompleter()

    #三个复选框组的槽函数
    def tags_set(self):
        self.tags_checked = []
        if self.checkBox.isChecked()==True : self.tags_checked.append('1')
        if self.checkBox_2.isChecked() == True: self.tags_checked.append('2')
        if self.checkBox_3.isChecked() == True: self.tags_checked.append('3')
        if self.checkBox_4.isChecked() == True: self.tags_checked.append('4')

    def setClientCompleter(self):
        customer_list = CS.getLinesFromTable('clients', columns_required=['short_name'],conditions={})
        customer_list.pop()
        self.customer_list = [item[0] for item in customer_list] 
        if not customer_list:
            return

        self.comp_model_1 = QStringListModel(self.customer_list)
        self.m_completer = QCompleter(self.comp_model_1, self)
        self.m_completer.setFilterMode(Qt.MatchContains)
        self.lineEdit_2.setCompleter(self.m_completer)

    def setProjectCompleter(self):
        # completer_project
        item_list = CS.getLinesFromTable('proj_list',conditions={},columns_required=['product'])
        item_list.pop()
        self.item_list = [item[0] for item in item_list]
        if not item_list:
            return
        
        self.comp_model_2 = QStringListModel(self.item_list)
        self.i_completer = QCompleter(self.comp_model_2, self)
        self.i_completer.setFilterMode(Qt.MatchContains)
        self.lineEdit.setCompleter(self.i_completer)

    def initUserTheme(self,cls:QWidget):
        theme = eval(userDir.getUserTheme())
        theme_dict = {0:'Aqua',1:'MacOS',2:'Ubuntu',3:'MaterialDark'}
        theme_name = theme_dict[theme]
        with open(f'{workingDir.getWorkingDirectory()}/QSS/%s.qss'%theme_name) as qssfile:
            qss = qssfile.readlines()
            qss = ''.join(qss).strip('\n')
        cls.setStyleSheet(str(qss))

    def setTheme(self):
        ok, theme = RedefinedWidget.ThemeChooseDialog.getTheme(self)
        if not ok:
            return
        userDir.saveUserTheme(str(theme))
        self.initUserTheme(self)
        for meetingDialog in self.meetModeAdded:
            self.initUserTheme(meetingDialog[1])
        # theme_dict = {0:'Aqua',1:'MacOS',2:'Ubuntu', 3:'MaterialDark'}
        # theme_name = theme_dict[theme]
        # with open('./QSS/%s.qss'%theme_name) as qssfile:
        #     qss = qssfile.readlines()
        #     qss = ''.join(qss).strip('\n')

    def setDatabasePath(self):
        path, ok = DirectoryChooseBox.getDirectory(title='切换文件存放目录' ,
                                                                  hint_text='最好不要将个人文件放在C盘，以免重装系统导致丢失')
        if not ok:
            return False
        else:
            FilePathInit.changeUserDir(path)
            self.restartWorkpad()
            return True

    def editOfficeJobType(self):
        RedefinedWidget.JobTypeEditDialog.start(self)

    def restartWorkpad(self):
        # self.working_dir.conf.read (self.working_dir.inipath, encoding="GBK")
        CS.initDatabase()
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        #检查数据库完整性
        self.checkDataBase()
        #删除原有的TabBar
        while True:
            nTab = self.tabWidget.tabBar().count()
            if nTab == 0 :
                break
            self.tabWidget.removeTab(nTab-1)
        self.tabBarAdded.clear()
        self.over_view = DataView.OverView(self)
        self.over_view.setUi(self.tabWidget)
        self.detail_view = DataView.DetailView(self)
        self.detail_view.setUi(self.tabWidget)
        self.todo_view = DataView.ToDoView(self,self.tabWidget)
        self.todo_view.setupUi()

        self.tabWidget.setTabsClosable(True)
        self.geoFilterEditorView.clearBoundWidget()
        self.geoFilterEditorView = DataView.GeoFilterEditorView(self)#地理筛选器，用来筛选指定区域内的客户
        self.geoFilterEditorView.setBoundWidget(self.groupBox_2)
        self.geoFilterEditorView.setupWidget()
        self.companyFilterView.clearBoundWidget()
        self.companyFilterView = DataView.CompanyFilterView(self)
        self.companyFilterView.setBoundWidget(self.groupBox_4)
        self.companyFilterView.setupWidget()

        self.chanceStatusFilter = DataView.ChanceStatusFilterView(self.groupBox)#机会标签筛选器
        self.tabWidget.tabBar().setTabButton(0 ,QTabBar.RightSide,None)
        self.tabWidget.tabBar().setTabButton(1 ,QTabBar.RightSide,None)
        self.tabWidget.tabBar().setTabButton(2 ,QTabBar.RightSide,None)
        #标签复选框组信号
        self.checkBox.stateChanged.connect(self.tags_set)
        self.checkBox_2.stateChanged.connect(self.tags_set)
        self.checkBox_3.stateChanged.connect(self.tags_set)
        self.checkBox_4.stateChanged.connect(self.tags_set)
        self.tags_checked = []

        self.radioButton.setChecked(True)
        self.now = datetime.datetime.now()
        self.listener.observers.clear()
        self.listener.addObserver(self.todo_view)#todoView单独处理
        # self.radioButton_3.setEnabled(False)
        #completer
        self.setClientCompleter()
        self.setProjectCompleter()
        #检查准备打开的Tab是否已经打开
        self.tabBarAdded.clear()
        self.meetModeAdded.clear()

    def note_set(self):
        """
        ”标记“复选框的状态改变事件
        不允许出现一个都不勾选的情形
        """
        self.note_checked = []
        if self.checkBox_12.isChecked() == True:
            self.note_checked.append('Y')#Y代表标记的
            if self.checkBox_13.isChecked() == False:
                self.checkBox_12.setEnabled(False)
            else:
                self.checkBox_12.setEnabled(True)
        if self.checkBox_13.isChecked() == True:
            self.note_checked.append('N')#N代表未标记的
            if self.checkBox_12.isChecked() == False:
                self.checkBox_13.setEnabled(False)
            else:
                self.checkBox_13.setEnabled(True)

    def set_sortByColumn(self, col):
        if self.SortUporDown:
            self.tableWidget.sortByColumn(col,Qt.AscendingOrder)
            self.SortUporDown =False
        else:
            self.tableWidget.sortByColumn(col, Qt.DescendingOrder)
            self.SortUporDown = True

    def is_in_customer(self):
        if self.lineEdit_2.text() in self.customer_list or self.lineEdit_2.text() == '':
            return
        else:

            QMessageBox.about(self, '客户名称', '查找的客户名称不存在')
            self.lineEdit_2.setFocus()
            self.lineEdit_2.clear()
            self.pushButton.releaseMouse()
            self.pushButton.repaint()

            return

    def is_in_item(self):
        if self.lineEdit.text() in self.item_list or self.lineEdit.text() == '':
            return
        else:

            QMessageBox.about(self, '项目名称', '查找的项目名称不存在')
            self.lineEdit.setFocus()
            self.lineEdit.clear()
            self.pushButton.releaseMouse()
            self.pushButton.repaint()

            return

    def showSlider(self, parent):
        """
        在主窗口的指定坐标画出slider,用以改变sender的数值,坐标由信号sender在父窗口的坐标来确定
        """
        sender = self.sender()
        X = sender.geometry().x()
        Y_0 = self.tabWidget.geometry().y()
        Y_1 = self.tableWidget_3.geometry().y()
        Y = sender.geometry().y() + Y_0+Y_1+80
        self.slider = MySlider(parent)
        #sender.installEventFilter()
        self.slider.setGeometry(X,Y,150,10)
        self.slider.setMaximum(35)
        self.slider.valueChanged.connect(lambda :sender.setText(str(round(1.15**self.slider.value()))))
        #self.slider.installEventFilter(self)
        self.slider.show()
        self.slider.setFocus()

    def setGeoFilter(self):
        self.geoFilterEditorView.setDialogUi()
    #@time_wrapper

    def setCompanyGroup(self):
        self.companyFilterView.setDialogUi()

    def overall_project_search(self, mode = None):
        '''根据主窗口全局限制条件的查找'''
        # before_make_condition = time.perf_counter()
        self.itemname = str(self.lineEdit.text())
        self.itemcustomer = str(self.lineEdit_2.text())

        ## 分组中选中的客户
        check_city_company_ids = self.geoFilterEditorView.getCompanyInCheckedCities()# 地理分组
        checked_group_company_ids = self.companyFilterView.getCheckedCompanies()# 自定义分组
        # 都没有勾选，认为分组筛选不适用
        if check_city_company_ids is None and checked_group_company_ids is None:
            checked_company_ids = None
        #只勾选了一组分组，即只有存在勾选的筛选组适用
        elif check_city_company_ids is None:
            checked_company_ids = set(checked_group_company_ids)
        elif checked_group_company_ids is None:
            checked_company_ids = set(check_city_company_ids)
        # 两组分组都有勾选，求交集
        else:
            check_city_company_ids_set = set(check_city_company_ids)
            checked_group_company_ids_set = set(checked_group_company_ids)
            checked_company_ids = check_city_company_ids_set & checked_group_company_ids_set
        ## 核验输入的客户条件
        # 根据输入的客户名称获取客户的id
        get_client_id = None# 未输入具体的客户名称
        if self.itemcustomer:
            client_get = CS.getLinesFromTable(table_name='clients', conditions={'short_name': self.itemcustomer},
                                              columns_required=['_id'])
            client_get.pop()
            if client_get:
                get_client_id = client_get[0][0]
            else:
                QMessageBox.about(self, "未找到", "输入的客户名称不存在！")
                return

        if checked_company_ids is None:# 未选择查找公司的条件
            pass
        elif not checked_company_ids:# 所选择的查找公司条件，最后得到空集
            QMessageBox.about(self, "未找到", "没有符合所设定的分组条件的客户！")
            return
        elif get_client_id and checked_company_ids and not get_client_id in checked_company_ids:#指定的分组条件内找不到输入的客户
            QMessageBox.about(self, "未找到", "所设定的分组条件下没有找到该客户！")
            return
        ## 分级标签选中的项目
        checked_sequence_code_project_ids = self.chanceStatusFilter.getCheckedProjects()
        ## 生成搜索条件
        condition = {}
        #未输入搜索条件
        if  not (self.itemname or self.itemcustomer  or checked_group_company_ids or
                 checked_sequence_code_project_ids or check_city_company_ids):
            #未指定任何搜索条件
            if self.radioButton_3.isChecked() or mode == 2:#todo_view
                return condition
            to_get_all = QMessageBox.question(self, "未输入内容", "提示：未输入查找条件，是否导入全部项目？",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if to_get_all == QMessageBox.No:
                return
            else:
                # end_make_condition = time.perf_counter()
                # print('time for make condition',end_make_condition - before_make_condition)
                return condition
        else:
            pass
        #搜索请求来自模式2（从todoView内部发起），但是当前选择的查看模式不在任务模式，此时搜索条件不发挥作用
        if not self.radioButton_3.isChecked() and mode == 2:#todo_view
                return None
        # 指定的项目名称
        if self.itemname:
            condition['product'] = self.itemname
        # 指定的项目条件
        if checked_sequence_code_project_ids:
            condition['_id'] = tuple(checked_sequence_code_project_ids)
        #指定的客户范围
        if self.itemcustomer != '' :
            condition['client_id'] = [get_client_id]
        elif self.itemcustomer == '' :
            if checked_company_ids :
                condition['client_id'] = tuple(checked_company_ids)
        # end_make_condition = time.perf_counter()
        # print('time for make condition',end_make_condition - before_make_condition)
        return (condition)

    def display_data(self):
        if self.radioButton.isChecked():
            self.displayClientOverview()
        elif self.radioButton_2.isChecked():
            self.display_detailed()
        elif self.radioButton_3.isChecked():
            self.display_toDo()

    def displayClientOverview(self):
        before_display = time.perf_counter()
        self.tabWidget.setCurrentIndex(0)
        condition = self.overall_project_search()
        if condition is None:
            return
        # self.overView = DataView.OverView(self)
        # self.overView.setBoundWidget(self.tableWidget)
        before_load = time.perf_counter()
        self.over_view.searchCondition(condition)
        end_display = time.perf_counter()
        # print('time for loading:', end_display - before_load)
        # print('time for overview:',end_display - before_display)
        self.listener.addObserver(self.over_view)

    def display_detailed(self):
        self.tabWidget.setCurrentIndex(1)
        # self.itemname = str(self.lineEdit.text())
        # self.itemcustomer = str(self.lineEdit_2.text())
        #首先检查是否没有输入查询条件
        self.check_city_codes = self.geoFilterEditorView.getCheckedCities()
        #
        # if self.itemname + self.itemcustomer + \
        #         ''.join(self.tags_checked) == '' and len(self.check_city_codes) == 0:
        #     QMessageBox.warning(self, '错误','详情模式下禁止加载全部数据，请输入查询条件！')
        #     return
        condition = self.overall_project_search()
        if condition is None:# 查找条件失败
            return
        if not condition:# 未输入查找条件
            QMessageBox.warning(self, '错误','详情模式下禁止加载全部数据，请输入查询条件！')
            return
        self.detail_view.searchCondition(condition = condition)
        self.listener.addObserver(self.detail_view)

    def displayCompanyEditor(self, client_name:str = None, client_id:str = None):
        client_view = DataView.CompanyEidtorView('client', self)
        client_view.setDataModel(company_name = client_name, company_id = client_id)
        client_id = client_view.company._id#获取client_view的_id
        for record in self.tabBarAdded:
            if client_id == record[0]:#该client_view已经打开
                del client_view
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(record[1]))
                return
        client_view.setupUi(parent_widget = self.tabWidget)
        client_view_tabBar = client_view.tab_bar
        client_view_tabBar_record = (client_id,client_view_tabBar)
        self.tabBarAdded.append(client_view_tabBar_record)
        self.listener.addObserver(client_view)
        #

    def showProjectPerspective(self, project_id):
        perspectiveView = DataView.PerspectiveView(self)
        perspectiveView.setDataModel(project_id=project_id)
        for record in self.tabBarAdded:
            if project_id == record[0]:#该perspectiveView已经打开
                del perspectiveView
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(record[1]))
                return
        perspectiveView.renderWidget(self)
        perspectiveView_tabBar = perspectiveView.tab_bar
        perspectiveView_tabBar_record = (project_id, perspectiveView_tabBar)
        self.tabBarAdded.append(perspectiveView_tabBar_record)
        self.listener.addObserver(perspectiveView)

    def display_toDo(self):
        condition = self.overall_project_search()
        self.todo_view.setDataModel(condition)
        self.todo_view.renderWidget()
        self.tabWidget.setCurrentIndex(2)
        self.listener.addObserver(self.todo_view)

    def startMeetingMode(self,):
        '''进入会议纪要模式'''
        while True:
            # inputDialog = QInputDialog(self,Qt.Dialog|Qt.WindowCloseButtonHint)

            name , ok = RedefinedWidget.ComboBoxDialog.getItem(self,'客户名称','请输入会议的客户名称',self.customer_list)
            if not ok :
                return
            get_client_id = CS.getLinesFromTable('clients',conditions={'short_name': name}, columns_required=['_id'])
            get_client_id.pop()
            if get_client_id:#获取到已有的客户
                client_id = get_client_id[0][0]
                client_name = name
                # self.lineEdit.setText(name)
                break
            else:
                create_new = QMessageBox.warning(self,'未找到','注意：\n输入的客户名称不存在，\n是否创建新的客户？', QMessageBox.Yes| QMessageBox.No, QMessageBox.No)
                if create_new == QMessageBox.Yes :#获取到新客户
                    self.createNewCompany(company_name=name)
                    self.startMeetingMode()
                    return 
                else:
                    continue
        self.showMeetingDialog(client_name=client_name , client_id=client_id )

    def showMeetingDialog(self, client_name, client_id, meeting_id:str = None):
        for record in self.meetModeAdded:
            if client_id == record[0]:
                QMessageBox.about(self,'重复打开', '该公司的会议纪要窗口已打开！')
                return
        dialog = MeetingRecordDialog(client_name=client_name , client_id=client_id ,company_meeting_id=meeting_id, parent=self)
        dialog.setWindowFlags(Qt.Window|Qt.WindowMinMaxButtonsHint|Qt.WindowCloseButtonHint)
        record = (client_id, dialog)
        self.meetModeAdded.append(record)
        self.listener.addObserver(dialog)
        dialog.show()

    def createNewCompany(self, company_name:str = None):
        company_name, country, province, city, town, ok = CompanyCreateDialog.getAllInput(company_name=company_name,company_name_exist=self.customer_list,parent=self)
        if ok:
            client_id = Snow('cl').get()
            CS.insertSqlite('clients', {'_id':client_id,'short_name':company_name,'country':country,'province':province,
                                        'city':city,'town':town})
            QMessageBox.about(self, '创建成功', '请在主界面搜索客户，\n'
                                            '并完善客户信息')
            self.setClientCompleter()
            self.displayCompanyEditor(client_name = company_name, client_id = client_id)

    #查看公司信息
    def on_getCompany(self):
        while True:
            # inputDialog = QInputDialog(self, Qt.Dialog|Qt.WindowCloseButtonHint)
            name , ok = RedefinedWidget.ComboBoxDialog.getItem(self,'客户', '客户名称：', self.customer_list)
            if not ok:
                return
            search_company = CS.getLinesFromTable('clients', conditions={'short_name': name},
                                               columns_required=['short_name', '_id'])
            search_company.pop()
            if search_company:
                break
            else:
                QMessageBox.about(self, '重复', '输入的公司名称不存在\n请重新输入！')
                continue
        client_id = search_company[0][1]
        self.displayCompanyEditor(client_id = client_id)
        pass

    def createNewProject(self, client_id = None):
        if not client_id:
            while True:#获取到客户的名称
                # inputDialog = QInputDialog(self,Qt.Dialog|Qt.WindowCloseButtonHint)
                # inputDialog.setMinimumSize(600, 300)
                # inputDialog.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
                client_name , ok = RedefinedWidget.ComboBoxDialog.getItem(self,'所属客户', '项目所属的客户名称:',
                                                       self.customer_list)
                if not ok:
                    return
                client_name = client_name.strip()
                if client_name not in self.customer_list:
                    create_new = QMessageBox.warning(self,'未找到','注意：\n输入的客户名称不存在，\n是否创建新的客户？',
                                                     QMessageBox.Yes| QMessageBox.No, QMessageBox.No)
                    if create_new == QMessageBox.Yes :#获取到新客户
                        self.createNewCompany(company_name=client_name)
                        self.createNewProject()
                        return
                    else:
                        continue
                else:
                    break
            #通过客户的名称获取到客户的id
            search_client = CS.getLinesFromTable('clients', conditions={'short_name': client_name},
                                                   columns_required=['short_name', '_id'])
        else:
            #通过客户的id获取到客户的名称
            search_client = CS.getLinesFromTable('clients', conditions={'_id': client_id},
                                                   columns_required=['short_name', '_id'])
        search_client.pop()
        client_name = search_client[0][0]
        client_id = search_client[0][1]
        project_id = Snow('a').get()
        #给指定客户id下面新建一个项目，生成项目id和项目名称
        while True:#
            inputDialog = QInputDialog(self,Qt.Dialog|Qt.WindowCloseButtonHint)
            project_name , ok = inputDialog.getItem(self,'项目名称', '为 %s 创建新项目\n\n请输入新项目名称：'%client_name,
                                                    self.item_list, editable = True)
            if not re.sub('[\W_]', '', project_name):#去除所有非法符号后，未输入其他字符
                QMessageBox.about(inputDialog, '错误', '请输入有效的名称!\n')
                continue
            if not ok:
                return
            search_project = CS.getLinesFromTable('proj_list',conditions={'client_id':client_id,'product':project_name.strip()},
                                                  columns_required=['_id', 'product','client'])
            search_project.pop()
            if search_project:
                QMessageBox.about(self, '已存在', '该客户已有此项目，\n'
                                        '请检查，或重新输入！')
                continue
            else:
                break
        in_act = False
        clear_chance = False
        order_tobe = False
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['product'] = project_name.strip()
        fields_values['client_id'] = client_id
        fields_values['in_act'] = in_act
        fields_values['clear_chance'] = clear_chance
        fields_values['order_tobe'] = order_tobe
        fields_values['client'] = client_name
        # fields_values['status_code'] = 0
        status_code = 0
        status_log_id = Snow('st').get()
        CS.upsertSqlite('proj_status_log',keys=['_id','status_code','conn_project_id'],
                       values=[status_log_id, status_code,project_id])
        command = DataCenter.GProjectCmd('insert', _id= project_id, fields_values=fields_values, source_widget=None,
                                         conn_company_name=client_name)
        command.status_code = status_code
        self.listener.accept(command)
        self.showProjectPerspective(project_id)
        # QMessageBox.about(self, '创建成功', '请在主界面搜索项目，\n并完善项目信息')
        self.setProjectCompleter()

    def createNewTodoUnit(self):
        DataView.ToDoView.add_todo_log(self)

    def checkDataBase(self):
        DataCenter.checkDatabase()



