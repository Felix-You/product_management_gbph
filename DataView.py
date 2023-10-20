import json
import logging
import math
from typing import Union
from core.GlobalListener import global_logger
import openpyxl, ctypes
from ID_Generate import ID_Generator
# import AppKit
# [(screen.frame().size.width, screen.frame().size.height) for screen in AppKit.NSScreen.screens()] # MacOs

import DataCenter
from DataCenter import *
from GColour import *
from projectTabBar import ProjectTabBar
from OverviewTabBar import OverviewTabBar
from DetailViewTabBar import DetailViewTabBar
from GeoFilterEditor import GeoFilterEditor
from CompanyEditorTabBar import CompanyEditorTabBar
from CompanyFilterEditor import CompanyFilterEditor
import projectCalculation, RedefinedWidget, time,GColour,ConnSqlite,FilePathInit
from PyQt5.QtWidgets import QApplication,QMainWindow,QTextEdit,QTextBrowser,QComboBox,QPushButton,QTabBar,QFrame, \
    QCheckBox,QWidget,QMessageBox,QFileDialog
from PyQt5.QtCore import Qt, QEvent, pyqtSignal,QSize,QUrl
from PyQt5.QtGui import QIcon, QPixmap, QStandardItemModel, QFontMetrics, QFont, QColor, QPalette, QPainter, QPen
from PyQt5 import QtWidgets,QtGui,QtCore
from RedefinedWidget import MySlider,StatusCheckFrame,ToDoUnitCreateDialog,ToDoUnitWidget
import csv,datetime,types, copy, win32con, win32api, win32gui, win32print
from collections import namedtuple
from operator import mul
from functools import reduce, partial

import winreg
import wmi
#
# PATH = "SYSTEM\\ControlSet001\\Enum\\"
#
# w = wmi.WMI()
# print(w)
# # 获取屏幕信息
# monitors = w.Win32_DesktopMonitor()

# for m in monitors:
#     print(m)
#     subPath = m.PNPDeviceID  #
#     # 可能有多个注册表
#     # print(m.)
#     if subPath == None:
#         continue
#     # 这个路径这里就是你的显示器在注册表中的路径
#     infoPath = PATH + subPath + "\\Device Parameters"
#     key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, infoPath)
#     # 屏幕信息按照一定的规则保存（EDID）
#     value = winreg.QueryValueEx(key, "EDID")[0]
#     winreg.CloseKey(key)
#
#     # 屏幕实际尺寸
#     width, height = value[21], value[22]
#     # 推荐屏幕分辨率
#     widthResolution = value[56] + (value[58] >> 4) * 256
#     heightResolution = value[59] + (value[61] >> 4) * 256
#     # 屏幕像素密度（Pixels Per Inch）
#     widthDensity = widthResolution / (width / 2.54)
#     heightDensity = heightResolution / (height / 2.54)
#
#     print("屏幕宽度：", width, " (厘米)")
#     print("屏幕高度：", height, " (厘米)")
#     print("水平分辩率: ", widthResolution, " (像素)")
#     print("垂直分辩率: ", heightResolution, " (像素)")
#     # 保留小数点固定位数的两种方法
#     print("水平像素密度: ", round(widthDensity, 2), " (PPI)")
#     print("垂直像素密度: ", "%2.f" % heightDensity, " (PPI)")

class int_yield_num(float):
    '''int type that yields int type when put into +, -, *, / operations'''
    def __mul__(self, other):
        r = super().__mul__(other)
        return int(r)

    def __rmul__(self, other):
        return self.__mul__(other)

# 开发时所默认的空间大小，由开发时的实际屏幕尺寸和DPI决定。控件尺寸 = 像素数/DPI。
# 控件按实际显示尺寸的策略，分为物理尺寸固定控件和可缩放控件。在设备的类型（比如都是电脑）不变，即用户使用时设备放置距离
# 不变的情况下，物理尺寸固定空间的实际显示尺寸不随屏幕物理大小改变。
def sigmoid(x):
    return 1/(1+math.exp(-x))
def _get_terminal_size_windows():

    # try:
    if True:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-11)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        print('res:', res)
    # except (AttributeError, ValueError):
    #     return None
    if True:
        import struct
        (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx,
         maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def get_scr_size():
    return [int(x) for x in os.popen("stty size", "r").read().split()]

BASE_H_RESOLUTION = 1600
BASE_V_RESOLUTION = 900
BASE_DPI = 96
hDC = win32gui.GetDC(0)
screen_real_hResolution = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
screen_real_vResolution = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
# screen_use_vResolution = win32api.GetSystemMetrics(0)
# screen_use_hResolution = win32api.GetSystemMetrics(1)
# size_h , size_v = get_scr_size()

DF_Ratio = win32api.GetSystemMetrics(0)/BASE_H_RESOLUTION # 开发时使用的屏幕分辨率为1600*900,缩放比1.0
FIX_SIZE_WIDGET_SCALING = 1
CONTENT_TEXT_SCALING = 1
# DF_Ratio = int_yield_num(DF_Ratio) # python3.10 does not cast float to int

USER_COMPANY_NAME = '广州国标检验检测有限公司'
USER_COMPANY_SHORT_NAME = '国标'
global_logger.debug('screen_real_hResolution={}'.format(screen_real_hResolution))
global_logger.debug('screen_real_vResolution={}'.format(screen_real_vResolution))
# global_logger.debug('screen_use_vResolution={}'.format(screen_use_vResolution))
# global_logger.debug('DF_Ratio={}'.format( DF_Ratio))

class ResolutionAdaptor():

    def __init__(self):
        # ...........
        self.app = QApplication.instance()  # Calculate the ratio.
        # self.widget = widget
        # screen_resolution = self.app.desktop().screenGeometry()
        # width, height = screen_resolution.width(), screen_resolution.height()
        screen_count = self.app.desktop().screenCount()
        # self.app.desktop().screen(-1).setGeometry(0,0,screen_real_hResolution, screen_real_vResolution)
        DPI = self.app.screens()[0].logicalDotsPerInch()
        # scaleRate = self.app.screens()[0].logicalDotsPerInch()/96 # Windows系统缩放比，此比例由操作系统产生，若要消除其影响，则需预先除掉
        #但实际上Qt有自己独立的缩放方法，虽然Windows有多级缩放，但Qt并不完全与Windows的缩放比例同步


        screen_resolution = self.app.desktop().screenGeometry() # logical resolution
        screen_logical_width = screen_resolution.width()
        screen_logical_height = screen_resolution.height()
        scaleRate = screen_real_hResolution/screen_resolution.width()
        LOGICAL_METRIC_RATIO = screen_logical_width / BASE_H_RESOLUTION
        self.hw_ratio = 900 / 1600  # height / width
        global_logger.debug('screen_count={}'.format( screen_count))
        global_logger.debug('DPI={}'.format(DPI))
        global_logger.debug('scaleRate={}'.format( scaleRate))
        global_logger.debug('screen_width={}'.format( screen_resolution.width()))
        global_logger.debug('screen_hight={}'.format(screen_resolution.height()))
        # self.ratio_wid = int_yield_num((screen_real_hResolution / 1600) /scaleRate)
        self.ratio_wid = int_yield_num(screen_logical_width / BASE_H_RESOLUTION)
        # self.ratio_wid = screen_real_hResolution / 1600
        global DF_Ratio, FIX_SIZE_WIDGET_SCALING, CONTENT_TEXT_SCALING
        DF_Ratio = int_yield_num(self.ratio_wid)
        HARD_FIX_SIZE_WIDGET_SCALING = DPI / BASE_DPI # the scaling factor to keep widget in identical physical metrics

        # FIX_SIZE_WIDGET_SCALING is used for widgets that should basically keep their physical metrics on different devices,
        # while some moderate adjust is advisable. Thus, the scaling is designed non_linear, using a

        # FIX_SIZE_WIDGET_SCALING is caculated from an adjusted sigmoid curve which has the maximum slope .
        # when _DF_Ratio == 1, and a symmetry center at (1, 1), and value range(0, 2)

        _DF_Ratio = float(DF_Ratio) * HARD_FIX_SIZE_WIDGET_SCALING
        # _DF_Ratio = 3
        if _DF_Ratio >= 1:
            x_1 = _DF_Ratio - 1 # Symmetry center at (1, 1), when _DF_Ratio == 1
            x_2 = x_1 * (0.8 * math.exp(-2 * abs(x_1)) + 0.2) # non-linear scaling of the x-axis, making the slope of the
                                                            # sigmoid curve flatter , except for the symmetry center.
            FIX_SIZE_WIDGET_SCALING = 4 * (sigmoid(1 * x_2) - 0.5) + 1 # Adjusted sigmoid curve, which has a maximum slope of 1
                                                                       # when _DF_Ratio == 1, and a symmetry center at (1, 1), and value range(0, 2)
        else:
            FIX_SIZE_WIDGET_SCALING = 0.5 + 0.5 * _DF_Ratio**2
        FIX_SIZE_WIDGET_SCALING = int_yield_num(FIX_SIZE_WIDGET_SCALING)
        CONTENT_TEXT_SCALING = max(0.9, FIX_SIZE_WIDGET_SCALING)
        CONTENT_TEXT_SCALING = int_yield_num(CONTENT_TEXT_SCALING)
        global_logger.debug('FIX_SIZE_WIDGET_SCALING={}'.format(FIX_SIZE_WIDGET_SCALING))
        # self.ratio_wid = screen_real_hResolution / 1600
        # if self.ratio_wid < 1:
        #     self.ratio_wid = 1
        self.ratio_height = int_yield_num(screen_logical_height / BASE_V_RESOLUTION )
        default_font = QFont()
        default_font.setFamily("Microsoft YaHei UI")
        default_font.setPointSize(10 * FIX_SIZE_WIDGET_SCALING)
        QApplication.setFont(default_font)
        n = 0
        # self.ratio_height = screen_real_vResolution / 900
        # self.ratio_height = screen_real_vResolution / 900
        # if self.ratio_height < 1:
        #     self.ratio_height = 1

    def init_ui_size(self, widget = None):
        """ Travel all the widgets and resize according to the ratio """
        self._resize_with_ratio(widget)
        for q_widget in widget.findChildren(QWidget):
            # print q_widget.objectName()
            self._resize_with_ratio(q_widget)
            self._move_with_ratio(q_widget)

            # Don't deal with the text browser
            # for q_widget in self.findChildren(QAbstractScrollArea):
            #     print q_widget.objectName()
            #     self._resize_with_ratio(q_widget)
            #     self._move_with_ratio(q_widget)

    def _resize_with_ratio(self, input_ui):
        input_ui.resize(input_ui.width() * self.ratio_wid, input_ui.height() * self.ratio_height)
        # input_ui.setFixedWidth(input_ui.width() * self.ratio_wid)
        # input_ui.setFixedHeight(input_ui.height() * self.ratio_height)
        pass

    def _move_with_ratio(self, input_ui):
        input_ui.move(input_ui.geometry().x() * self.ratio_wid, input_ui.geometry().y() * self.ratio_height)
        pass

ResAdaptor = ResolutionAdaptor()

clipboard = QApplication.clipboard()

# def on_clipboard_change():
#     data = clipboard.mimeData()
#     if data.hasFormat('text/uri-list'):
#         for path in data.urls():
#             print path
#     if data.hasText():
#         print data.text()
#
# clipboard.dataChanged.connect(on_clipboard_change)



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

class View(object):
    tablet_index = 0
    contain_root_item = None#界面的根节点类型，
    contain_root_ids = []#包含的根节点类型的id
    def __init__(self):

        pass

    def setDataModel(self,condition:dict):

        pass

    def setBoundWidget(self, sheet_widget, sheet_widget_header = None):
        self.bound_widget = sheet_widget

    # def renderWidget(self):
    #     pass

    def Accept(self,cmd):
        '''首先应该查找cmd中的数据是否在自己的DataModel中,如果不存在则直接抛弃。
        判断的过程是一个搜索过程
        如果是project类型的数据，一步直接搜索_id; 如果是log类型的数据，则要到project类的属性下面去搜索，task，memo，meeting分别对应各自的搜
        索空间。
        搜索到了数据之后再判断所对应的控件位置
        '''

        pass

class OverView(View):
    '''概览模式视图'''
    contain_root_item = 'client'

    def __init__(self,parent = None):
        super(OverView, self).__init__()
        self.clients = [] #
        self.secondary_clients = []
        self.filepath_model = FilePathInit.userDir
        self.current_clients = self.clients
        self.parent = parent
        self.accept_state = AccceptState()
        self.nCompany = 0
        self.nIsDeal = 0
        self.nProject = 0
        self.nOrderTobe = 0
        self.nToVisit = 0
        self.nClearChance = 0
        self.nInAct = 0
        self.nHighlight = 0

    def searchCondition(self, condition):
        self.condition = condition
        # self.tab_bar.checkLabel.clearCheckStatuses()
        before_model = time.perf_counter()
        self.setDataModel(self.condition)
        end_model = time.perf_counter()
        checked_attribute = self.tab_bar.checkLabel.getCheckedNames()
        if checked_attribute:
            self.setFilteredModel(checked_attribute)
        self.renderWidget()
        # print('time_for_model:',end_model - before_model)

    def initAllData(self):
        self.setDataModel(self.condition)
        self.renderWidget()

    def setDataModel(self, condition:dict):
        '''根据主窗口的搜索条件来创建DataModel'''
        #获取所有符合条件的项目_id，client组合
        # if 'status_code' in condition.keys():
        #     status_codes = condition.pop('status_code')
        #
        #     chose_project_ids = CS.getLinesFromTable('proj_status_log',conditions= {'status_code':status_codes},
        #                                              columns_required=['conn_project_id'])
        #     chose_project_ids.pop()
        #     condition['_id'] = chose_project_ids
        self.clients.clear()
        self.current_clients = self.clients
        self.nCompany = 0
        self.nProject = 0
        self.nOrderTobe = 0
        self.nToVisit = 0
        self.nClearChance = 0
        self.nInAct = 0
        self.nHighlight = 0
        #查找到所搜索项目的id,客户名称，客户id
        # before_make_proj_ids = time.perf_counter()

        project_fields = Project.getDataFields()
        client_fields = Client.getDataFields()
        project_status_fields = ['status_code']
        project_client_status_join_data = CS.triple_innerJoin_withList_getLines(
            table_a='proj_list', table_b='clients', table_c='proj_status_log',
            joint_key_a_b=('client_id', '_id'), joint_key_a_c=('_id', 'conn_project_id'),
            condition_a=condition,
            target_colums_a=project_fields, target_colunms_b= client_fields, target_colunms_c=project_status_fields,
            method='left join'
        )
        if not project_client_status_join_data:
            QMessageBox.about(self.parent, '未找到', '没有符合条件的项目！')
            return

        # project_fields_index = {key:i for i, key in enumerate(project_fields)}
        # client_fields_index = {key: i + len(project_fields) for i ,key in enumerate(client_fields)}
        project_fields_len = len(project_fields)
        client_fields_len = len(client_fields)
        dict_client_id_instance ={}
        dict_proj_id_instance = {}
        time_before_making_project_client = time.perf_counter()
        for item in project_client_status_join_data:
            project = Project()
            project.assign_data(project_fields, item[:project_fields_len])
            project.status_code = item[-1]
            project.has_active_task_critical = False
            dict_proj_id_instance[project._id] = project
            client_id = project.client_id
            if not client_id in dict_client_id_instance:
                client = Client()
                client.assign_data(client_fields, item[project_fields_len: project_fields_len+client_fields_len])
                dict_client_id_instance[client_id] = client
                self.clients.append(client)
            dict_client_id_instance[client_id].projects.append(project)
        time_after_making_project_client = time.perf_counter()
        print('time for making_project_client_instances',time_after_making_project_client - time_before_making_project_client)
        client_ids = list(dict_client_id_instance.keys())
        project_ids = list(dict_proj_id_instance.keys())

        proj_task_in_act = CS.innerJoin_withList_getLines('tasks', 'todo_log', '_id', 'conn_task_id',
                                                          ['conn_project_id', 'is_critical'], ['status', 'destroyed'],
                                                          {'conn_project_id': project_ids, 'is_critical': 1},
                                                          {'destroyed': 0, 'status': [0, 1]},
                                                          method='left join')
        for conn_project_id, is_critical, status, destroyed in proj_task_in_act:
            dict_proj_id_instance[conn_project_id].has_active_task_critical = True

        client_log_datas = CS.getLinesFromTable('client_log', conditions={'company_id': client_ids},
                                    order=['create_time'], ascending=True)
        client_log_fields = client_log_datas.pop()
        # client_log_fields_index = {key:i for i, key in enumerate(client_log_fields)}

        for item in client_log_datas:
            company_log = CompanyLog()
            company_log.assign_data(client_log_fields, item)
            # company_id = item[client_log_fields_index['company_id']]
            company_id = company_log.company_id
            client = dict_client_id_instance[company_id]
            client.logs.append(company_log)

    def secondaryShowRender(self, attribute_name):
        """根据页面勾选的次级筛选条件，重新渲染页面"""
        if attribute_name:
            self.setFilteredModel(attribute_name)
            self.current_clients = self.secondary_clients
        else:
            self.current_clients = self.clients
        self.renderWidget()

    def clearStatistics(self):

        self.nCompany = 0
        self.nProject = 0
        self.nOrderTobe = 0
        self.nToVisit = 0
        self.nClearChance = 0
        self.nInAct = 0
        self.nHighlight = 0

    def setFilteredModel(self,attribute_name:list):
        '''根据次级筛选条件来创建次级DataModel'''
        self.secondary_clients.clear()
        self.current_clients = self.secondary_clients
        self.clearStatistics()
        for i, client in enumerate(self.clients):
            secondary_client = copy.deepcopy(client)
            is_client_select = 0
            for j in reversed(range(len(secondary_client.projects))):
                project = secondary_client.projects[j]
                is_project_select = 0
                for attribute in attribute_name:
                    is_ok = project.__getattribute__(attribute)
                    is_client_select += is_ok
                    is_project_select += is_ok
                if not is_project_select:
                    secondary_client.projects.pop(j)
            if is_client_select:
                self.secondary_clients.append(secondary_client)
                pass

    def showStatistics(self):
        """显示当前页的统计信息"""
        dialog = QtWidgets.QDialog(self.parent)
        dialog.setWindowFlags(Qt.WindowCloseButtonHint|Qt.Popup)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.setWindowTitle('统计信息')
        dialog.setFixedWidth(200*DF_Ratio)
        VLayout = QtWidgets.QVBoxLayout(dialog)
        label_nCompany = QtWidgets.QLabel('公司数量:%s' % self.nCompany, dialog)
        VLayout.addWidget(label_nCompany)
        label_nProject = QtWidgets.QLabel('项目数量:%s' % self.nProject, dialog)
        VLayout.addWidget(label_nProject)
        for i, mode_label_set in enumerate(projectCalculation.PROJECT_MODE_SET):
            label_n = QtWidgets.QLabel('%s数量:  %s'%(mode_label_set[1],self.__getattribute__(mode_label_set[4])))
            VLayout.addWidget(label_n)
        dialog.show()

    def on_exportData(self):
        ok = QMessageBox.question(self.parent, '导出数据', '是否导出当前概览页？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.No:
            return
        date = datetime.datetime.today().date()
        filename = date.strftime("%Y%m%d") + '-概览'
        fname, ftype = QFileDialog.getSaveFileName(self.parent, '保存文件',
                                                   self.filepath_model.get_last_save() + '\\' + filename,
                                                   "ExcelFile (*.xlsx)")
        if fname:
            exported_list = self.clients if len(self.clients) > len(self.secondary_clients) else self.secondary_clients
            #保存本次选择的路径
            (filepath, tempfilename) = os.path.split(fname)
            self.filepath_model.save_last_save(filepath)
            #保存xlsx文件
            work_book = openpyxl.Workbook()
            work_sheet = work_book.active
            work_sheet.append(['客户名称', '项目名称', '机会状态', '推进状态'])
            for i, client in enumerate(exported_list):
                for j , project in enumerate(client.projects):
                    project_mode_label, _ , status_desc = projectCalculation.get_project_brief(project)
                    row = [client.enterprise_name if client.enterprise_name else client.short_name,  project.product, project_mode_label, status_desc]
                    work_sheet.append(row)#openpyxl从1开始计数，并且默认没有表头
            try:
                work_book.save(fname)
            except PermissionError as e:
                QMessageBox.about(self.tab_bar, '保存失败', '文件覆盖失败，请检查文件\n是否被其他程序占用！')
                global_logger.exception(e)
        else:
            pass


    def setUi(self,parent_widget):
        self.tab_bar = OverviewTabBar(parent=parent_widget)
        self.tab_bar.setStyleSheet('QTextEdit {'
                                   'border-width: 3px;'
                                   'border-style: dashed;'
                                   'border-color: qlineargradient(spread:pad, x1:0.5, y1:3, x2:0.5, y2:0, '
                                   'stop:1 rgba(100, 163, 255, 255), stop:0 rgba(91, 171, 252, 105));}'
                                   "QToolTip{border: 0px solid black;background:rgba(250,245,210,200);width:300px;}"
                                   "QTextEdit:hover{border-style: solid;}"
                                   "QTableView::item:hover{background:#F4F4F4;}")

        tab_header = '概览模式'
        self.tab_bar.btn_showStatistics.clicked.connect(self.showStatistics)
        self.tab_bar.btn_exportData.clicked.connect(self.on_exportData)
        self.tab_bar.checkLabel.statusClicked.connect(self.secondaryShowRender)
        parent_widget.addTab(self.tab_bar,tab_header)
        self.setBoundWidget(self.tab_bar.tableWidget)

    def Accept(self,cmd):
        global_logger.debug('overview accept')
        #根据接收到的命令，判断本次广播的接受状态
        if cmd.broadcast_space is None:
            #如果收到的广播命令没有绑定广播域，则将接收状态重置，并设定到接收完成状态
            self.accept_state.__init__()
            self.accept_state.acceptComplete()
        elif self.accept_state.accept_ID != cmd.broadcast_space.broadcast_ID:#接收到了新的广播域
            #重置接收状态
            self.accept_state.__init__(cmd.broadcast_space.broadcast_ID, cmd.broadcast_space.broadcast_names)
            self.accept_state.argAccepted(cmd._id)
        else:
            self.accept_state.argAccepted(cmd._id)
        #分发命令
        target_flag = cmd.flag#目标数据类的类型
        if target_flag  == 1:#project
            self.acceptProjectCmd(cmd)
        elif target_flag == 2:#task
            self.acceptTaskCmd(cmd)
        else:
            return

    def acceptTaskCmd(self,cmd):
        global_logger.debug('OverView accepted task')
        client_name = cmd.conn_company_name
        project_id = cmd.fields_values['conn_project_id']
        task_id = cmd._id
        source_widget = cmd.source_widget
        # 查找被修改的task
        for i, client in enumerate(self.current_clients):
            if client_name == client.short_name or client_name == client._id:
                for j, project in enumerate(client.projects):
                    if project_id == project._id:
                        #根据operation flag选择操作
                        if cmd.operation == 3:#insert
                            new_task = Task(task_id,project_id)
                            new_task.assign_data(list(cmd.fields_values.keys()),list(cmd.fields_values.values()))
                            project.tasks.insert(new_task.inter_order_weight - 1, new_task)
                            if self.accept_state.accept_complete:
                                project.resetWeight()#重置project权重
                            if source_widget is self.bound_widget or self.accept_state.accept_complete == False:
                                return
                            else:
                                if self.accept_state.accept_complete:
                                    self.renderUnit(i, link_statistics=False)
                                return
                        else:
                            pass
                        for k, task in enumerate(project.tasks):
                            if task_id == task._id:
                                if cmd.operation == 1:#update
                                    task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                                elif cmd.operation == 4:#delete
                                    del project.tasks[k]
                                if self.accept_state.accept_complete:
                                    project.resetWeight()#重置project权重
                                if source_widget is self.bound_widget:
                                    return
                                else:
                                    if self.accept_state.accept_complete:
                                        self.renderUnit(i, link_statistics=False)
                                    return
                    else:
                        pass
            else:
                pass

    def acceptProjectCmd(self, cmd):
        global_logger.debug('overview accepted project')
        client_name = cmd.conn_company_name
        project_id = cmd._id
        source_widget = cmd.source_widget
        # 查找被修改的task
        for i, client in enumerate(self.current_clients):
            if client_name == client.short_name:
                #根据operation flag选择操作
                if cmd.operation == 3:#insert
                    new_project = Project()
                    new_project.assign_data(tuple(cmd.fields_values.keys()),tuple(cmd.fields_values.values()))
                    new_project.resetWeight()#重置project权重
                    new_project.status_code = cmd.status_code
                    new_project.has_active_task_critical = False
                    client.projects.append(new_project)
                    if source_widget is self.bound_widget:
                        return
                    else:
                        self.renderUnit(i, link_statistics=False)
                else:
                    for j, project in enumerate(client.projects):
                        if project_id == project._id:
                            if cmd.operation == 1:#update
                                project.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                                if self.accept_state.accept_complete:
                                    project.resetWeight()#project权重
                            elif cmd.operation == 4:#delete
                                del client.projects[j]
                            if source_widget is self.bound_widget or self.accept_state.accept_complete == False:
                                return
                            else:
                                self.renderUnit(i)
                            return

        else:
            return

    def renderWidget(self):
        render_start = time.perf_counter()
        self.bound_widget.clear()
        self.clearStatistics()
        row_count = len(self.current_clients) // 5 if len(self.current_clients) % 5 == 0 else len(self.current_clients)//5 +1
        self.bound_widget.setColumnCount(5)
        self.bound_widget.setRowCount(row_count)
        self.bound_widget.horizontalHeader().setDefaultSectionSize(int(300*DF_Ratio))
        self.bound_widget.verticalHeader().setDefaultSectionSize(int(200*DF_Ratio))
        self.bound_widget.horizontalHeader().setVisible(False)
        self.bound_widget.verticalHeader().setVisible(False)
        #生成要展示的信息
        # customer_text_logs = []
        self.current_clients.sort(key= lambda client: client.short_name)
        # for client in self.clients:
        #     client.projects = sorted(client.projects,key= lambda project: project.weight if project.weight is not None else 0, reverse=True)#按weight排序
        #     #此时project
        #     text_log = projectCalculation.projectTextRender_add(client)
        #     customer_text_logs.append(text_log)
        #在tableWidget里展示信息
        main_loop_start = time.perf_counter()
        time_for_units_make_widget = 0
        time_for_unit_widgets_render_html = 0
        for i in range(len(self.current_clients)):
            loop_start = time.perf_counter()
            row_index = i // 5
            column_index = i % 5
            #创建单元格->TextBrowser的基本显示样式
            make_widget_start = time.perf_counter()
            textBrowser = MyQTextBrowser()
            textBrowser.index = i
            self.bound_widget.setCellWidget(row_index,column_index, textBrowser)
            make_widget_end = time.perf_counter()
            time_unit_make_widget = make_widget_end - make_widget_start
            time_for_units_make_widget += time_unit_make_widget
            # print('time for overview unit make widget', time_unit_make_widget)
            #设置单元格TextBrowser样式
            textBrowser.setStyleSheet("QTextEdit{"
                                           "background-color: rgb(248, 253, 252);"
                                            "margin:1px"
                                           "}")
            textBrowser.setFrameShadow(QFrame.Sunken)
            textBrowser.anchorClicked.connect(lambda url :self.customer_url_clicked(url))
            textBrowser.setOpenLinks(False)#禁止textBrowser自行加载被点击的链接
            #renderUnit的过程不重新创建textBrowser，保持其原有的scroll状态
            before_html_render = time.perf_counter()
            self.renderUnit(i, re_order_projects= True)
            html_render_end = time.perf_counter()
            time_unit_widget_render_html = html_render_end - before_html_render
            time_for_unit_widgets_render_html += time_unit_widget_render_html
            # print('time for overview unit html render', time_unit_widget_render_html)
            loop_end = time.perf_counter()
            # print('time for make widget%s:'%i, make_widget_end - loop_start)
            # print('time for html_render%s:'%i, html_render_end - before_html_render)
            # print('time for loop%s'%i,loop_end - loop_start)
        render_stop = time.perf_counter()
        print('time for overview render', render_stop - render_start)
        print('time_for_units_make_widget', time_for_units_make_widget)
        print('time_for_unit_widgets_render_html', time_for_unit_widgets_render_html)

    def renderUnit(self,i, re_order_projects = True, link_statistics = True):
        '''重新渲染client对应的单元格
        i:被改变的client的下标
        '''
        client = self.current_clients[i]
        # project = client[j]
        # project.resetWeight()
        if re_order_projects:
            client.reOrderProjects()
        text_log = self.calcClientProjects(client, link_statistics)
        row_index = i // 5
        column_index = i % 5
        cellWidget = self.bound_widget.cellWidget(row_index,column_index)
        cellWidget.setText(text_log)
        cellWidget.DoubleClicked.connect(lambda : self.customer_DBclicked_search(client.short_name))
        #添加右键菜单
        cellWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        cellWidget.customContextMenuRequested.connect(self.create_rightMemu)
        #tooltip
        latest_log = client.logs[-1] if client.logs else None
        tooltip = ''
        desc = client.desc
        if desc and len(client.desc) > 200:
            desc = desc[:200] + '...'
        if latest_log and len(latest_log.log_desc) > 100:
            log_desc = latest_log.log_desc[:100] + '...'
        elif latest_log:
            log_desc = latest_log.log_desc

        if desc and latest_log:
            tooltip = desc + '\n\n' + str(datetime.datetime.strptime(latest_log.create_time, '%Y-%m-%d %X').date()) +'\n' + log_desc
        elif desc:
            tooltip = desc
        elif latest_log:
            tooltip = str(datetime.datetime.strptime(latest_log.create_time, '%Y-%m-%d %X').date()) +'\n' + log_desc

        cellWidget.setToolTip(self.wrapTooltip(tooltip,25))
        # toolTip = QtWidgets.QToolTip()

    def calcClientProjects(self, client, link_statistics = True):
        text_log,nIsDeal,nProject,nOrderTobe,nClearChance,nHighlight,nInAct,nToVisit = \
            projectCalculation.projectTextRender_list(client)
        if link_statistics:
            self.nIsDeal += nIsDeal
            self.nOrderTobe += nOrderTobe
            self.nCompany += 1
            self.nProject += nProject
            self.nToVisit += bool(nToVisit)
            self.nClearChance += nClearChance
            self.nInAct += nInAct
            self.nHighlight += nHighlight
        return text_log

    def wrapTooltip(self, text:str,len_char:int):
        '''将文本变成一行长度不超过len_char'''
        if not text:
            return None
        runs = text.split('\n')
        get_runs = []
        for run in runs:
            if len(run) <= len_char:
                get_runs.append(run)
                continue
            nRow = len(run)//len_char
            nRemainder = len(run)%len_char
            for i in range(nRow):
                get_runs.append(run[i*len_char:(i+1)*len_char])
            if nRemainder:#如果余数不为0
                get_runs.append(run[nRemainder*-1:])
        strToolTip = '\n'.join(get_runs)
        return strToolTip

    def customer_url_clicked(self, url:QUrl):
        '''将overview页面的URL路由到不同的函数去显示'''
        target_id = url.adjusted(QUrl.RemoveFragment).url()
        # target_id = url.path()
        target = url.fragment()
        if target == 'project':
            self.parent.showProjectPerspective(target_id)
        elif target == 'client':
            self.parent.displayCompanyEditor(client_name=target_id)
        pass

    def customer_DBclicked_search(self, client_name):
        sender = self.bound_widget.sender()
        self.parent.lineEdit_2.setText(sender.toPlainText().split(None,1)[0])
        self.parent.radioButton_2.setChecked(True)
        self.parent.display_detailed()
        pass

    def create_rightMemu(self):
        '''自定义客户概览单元格的右键菜单'''
        self.cell_menu = QtWidgets.QMenu()
        x = self.bound_widget.currentRow()
        y = self.bound_widget.currentColumn()
        i = x*5 + y#当前客户的下标
        action_add_project = self.cell_menu.addAction('添加项目')
        action_add_todo = self.cell_menu.addAction('添加任务追踪')
        action_add_to_group = self.cell_menu.addMenu('加入分组')
        action_remove_from_group = self.cell_menu.addMenu('移出分组')
        groups = self.parent.companyFilterView.model.groups#使用主窗口的companyFilterView的model作为数据
        #分组操作菜单
        for group in groups:
            if self.clients[i]._id not in self.parent.companyFilterView.model.company_dict[group]:
                action_add = action_add_to_group.addAction(group)
                action_add.triggered.connect(partial(self.add_to_group, i , group))
            else:
                action_remove = action_remove_from_group.addAction(group)
                action_remove.triggered.connect(partial(self.remove_from_group, i, group))
        action_add_project.triggered.connect(lambda: self.add_project(i))
        action_add_todo.triggered.connect(lambda : ToDoView.add_todo_log(self.parent, self.clients[i]._id))
        self.cell_menu.popup(QtGui.QCursor.pos())

    def add_to_group(self, i, group):
        self.parent.companyFilterView.model.company_dict[group].append(self.clients[i]._id)
        self.parent.companyFilterView.model.saveCompanyGroupFilter()

    def remove_from_group(self, i, group):
        self.parent.companyFilterView.model.company_dict[group].remove(self.clients[i]._id)
        self.parent.companyFilterView.model.saveCompanyGroupFilter()

    def add_project(self, index):
        client_id = self.clients[index]._id
        self.parent.createNewProject(client_id=client_id)
        # self.renderUnit(i)

class DetailView(View):
    contain_root_item = 'project'

    def __init__(self, parent =None):
        super(DetailView, self).__init__()
        self.projects = []
        self.parent = parent
        self.accept_state = AccceptState()
        self.filepath_model = FilePathInit.userDir
        self.cols_names = ['项目名称', '客户名称', '会议记录', '状态标签','子任务', '状态设定' , '项目备注']
        self.cols_keys = ['product', 'client', 'meeting_log', 'status_code', 'tasks', '', 'memo_log']
        self.cols_index = list(range(len(self.cols_names)))
        self.cols_name_key_dict = dict(zip(self.cols_names,self.cols_keys))
        self.cols_name_index_dict = dict(zip(self.cols_names,self.cols_index))

    def setUi(self, parent_widget):
        self.tab_bar = DetailViewTabBar(parent=parent_widget)
        self.tab_bar.pushButton_export.clicked.connect(self.save_excel_file)
        # self.tab_bar.setStyleSheet('QTextEdit {'
        #                            'border-width: 1px;'
        #                            'border-style: dashed;'
        #                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                            'stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
        tab_header = '详情模式'
        parent_widget.addTab(self.tab_bar, tab_header)
        self.setBoundWidget(self.tab_bar.tableWidget)

    def searchCondition(self,condition:dict):
        self.condition = condition
        self.setDataModel(self.condition)
        self.renderWidget()

    def initAllData(self):
        self.setDataModel(self.condition)
        self.renderWidget()

    def exportData(self):
        sheet_body = []
        for i in range(self.tab_bar.tableWidget.rowCount()):
            row = []
            for j, header in enumerate(self.cols_names):
                if header in ['状态标签']:
                    row.append(self.tab_bar.tableWidget.cellWidget(i,j).currentText())
                elif header in ['状态设定']:
                    text = ', '.join(self.tab_bar.tableWidget.cellWidget(i,j).getCheckedLabels())
                    row.append(text)
                else:
                    row.append(self.tab_bar.tableWidget.cellWidget(i,j).toPlainText())
            sheet_body.append(row)
        return sheet_body

    def save_excel_file(self):
        date = datetime.datetime.today().date()
        filename =  date.strftime("%Y%m%d") + '-详情'
        fname, ftype = QFileDialog.getSaveFileName(self.parent, 'save file',
                                                   self.filepath_model.get_last_save() + '\\' + filename ,
                                                   "ExcelFile (*.xlsx)")
        if fname:
            #保存本次选择的路径
            (filepath, tempfilename) = os.path.split(fname)
            self.filepath_model.save_last_save(filepath)
            #保存xlsx文件
            work_book = openpyxl.Workbook()
            work_sheet = work_book.active
            work_sheet.append(self.cols_names)
            sheet_body = self.exportData()
            for i, row in enumerate(sheet_body):
                work_sheet.append(row)#openpyxl从1开始计数，并且默认没有表头
            try:
                work_book.save(fname)
            except PermissionError as e:
                global_logger.exception(e)
                QMessageBox.about(self, '保存失败', '检查文件是否被其他程序打开')
                return
        else:
            return

    def setDataModel(self,condition:dict):
        # if 'status_code' in condition.keys():
        #     status_codes = condition.pop('status_code')
        #     chose_project_ids = CS.getLinesFromTable('proj_status_log',conditions= {'status_code':status_codes},
        #                                              columns_required=['conn_project_id'])
        #     condition['_id'] = chose_project_ids
        self.projects.clear()
        # 首先获取到项目、客户 组对
        detail_proj_ids = CS.getLinesFromTable(table_name='proj_list', conditions=condition, columns_required=['_id', 'client', 'weight'],
                                          order=['client', 'weight'], ascending=False)
        detail_proj_ids.pop()
        if not detail_proj_ids:
            QMessageBox.about(self.parent, '未找到', '没有符合条件的项目！')
            return
        ids = []
        for item in detail_proj_ids:
            ids.append(item[0])
        for id in ids:
            project_tmp = Project()
            project_tmp.load_id_data(id)
            self.projects.append(project_tmp)
        pass

    def Accept(self,cmd):
        global_logger.debug('detailview accept')
        if cmd.broadcast_space is None:
            #如果收到的广播命令没有绑定广播域，则将接收状态重置，并设定到接收完成状态
            self.accept_state.__init__()
            self.accept_state.acceptComplete()
        elif self.accept_state.accept_ID != cmd.broadcast_space.broadcast_ID:#接收到了新的广播域
            #重置接收状态
            self.accept_state.__init__(cmd.broadcast_space.broadcast_ID, cmd.broadcast_space.broadcast_names)
            self.accept_state.argAccepted(cmd._id)
        else:
            self.accept_state.argAccepted(cmd._id)

        target_flag = cmd.flag
        source_widget = cmd.source_widget
        if source_widget is self.bound_widget:
            return
        #todo:分发命令
        if target_flag == 2:#task类型
            self.acceptTaskCmd(cmd)
        elif target_flag == 1:#project
            self.acceptProjectCmd(cmd)
        elif target_flag == 3:#meeting
            self.acceptMeetingCmd(cmd)
        elif target_flag == 4:#Memo
            self.acceptMemoCmd(cmd)
        else:
            pass

    def acceptProjectCmd(self, cmd):
        global_logger.debug('DetailView accepted project')
        project_id = cmd._id
        for i, project in enumerate(self.projects):
            if project_id == project._id:
                project.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                if self.accept_state.accept_complete == False:  # 如果改变的数据来自于自身的控件，则不需要重新渲染
                    return
                else:
                    self.renderUnit(i, None)
                    return
        else:
            return

    def acceptMemoCmd(self, cmd) ->None:
        memo_id = cmd._id
        global_logger.debug('DetailView accepted Memo')
        project_id = cmd.fields_values['conn_project_id']
        # 查找被修改的task
        for i, project in enumerate(self.projects):
            if project_id == project._id:
            # 根据operation flag选择操作
                if cmd.operation == 3:  # insert
                    new_memo = Memo(memo_id)
                    new_memo.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    project.memo_log.insert(new_memo.inter_order_weight-1, new_memo)
                    if self.accept_state.accept_complete == False:
                        return
                    else:
                        self.renderUnit(i, None)
                    return
                for k, memo in enumerate(project.memo_log) :
                    if memo_id == memo._id :
                        if cmd.operation == 1 :  # update
                            memo.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                        elif cmd.operation == 4 :  # delete
                            project.memo_log.pop(k)
                        if self.accept_state.accept_complete == False:
                            # print('memo accept not completed')
                            return
                        else :
                            # print('memo accept completed')
                            self.renderUnit(i,k)
                            return
                return

    def acceptMeetingCmd(self, cmd):
        global_logger.debug('DetailView accepted meeting')

        meeting_id = cmd._id
        project_id = cmd.fields_values['conn_project_id']
        # 查找被修改的meeting
        for i, project in enumerate(self.projects):
            if project_id == project._id:
            # 根据operation flag选择操作
                if cmd.operation == 3:  # insert
                    new_meeting = Meeting(meeting_id)
                    new_meeting.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    project.meeting_log.insert(new_meeting.inter_order_weight-1, new_meeting)
                    if self.accept_state.accept_complete == False:
                        global_logger.debug('meeting accept not complete')
                        return
                    else:
                        global_logger.debug('meeting accept completed')
                        self.renderUnit(i, None)
                    return
                for k, meeting in enumerate(project.meeting_log) :
                    if meeting_id == meeting._id :
                        if cmd.operation == 1 :  # update
                            meeting.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                        elif cmd.operation == 4 :  # delete
                            project.meeting_log.pop(k)
                        if self.accept_state.accept_complete == False:
                            global_logger.debug('meeting accept not complete')
                            return
                        else :
                            # print('meeting accept completed')
                            self.renderUnit(i,k)
                            return
                else:return

    def acceptTaskCmd(self,cmd):
        global_logger.debug('DetailView accepted task')
        project_id = cmd.fields_values['conn_project_id']
        task_id = cmd._id
        # 查找被修改的task
        for i, project in enumerate(self.projects):
            if project_id == project._id:
            #根据operation flag选择操作
                if cmd.operation == 3:  # insert
                    new_task = Task(task_id, project_id)
                    new_task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    project.tasks.insert(new_task.inter_order_weight-1, new_task)
                    if self.accept_state.accept_complete == False:
                        return
                    else:
                        self.renderUnit(i,None)
                    return
                for k, task in enumerate(project.tasks) :
                    if task_id == task._id :
                        if cmd.operation == 1 :  # update
                            task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                        elif cmd.operation == 4 :  # delete
                            project.tasks.pop(k)
                        if self.accept_state.accept_complete == False:
                            return
                        else :
                            self.renderUnit(i,k)
                            return

    def renderUnit(self,i, j):
        self.renderLine(i)

    def renderWidget(self):
        row_count = len(self.projects)

        cols_counts = len(self.cols_names)
        self.bound_widget.clear()
        self.bound_widget.setColumnCount(cols_counts)
        self.bound_widget.setRowCount(row_count)
        self.bound_widget.setHorizontalHeaderLabels(self.cols_names)
        self.bound_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget.verticalHeader().setDefaultSectionSize(int(130*DF_Ratio))
        self.bound_widget.setShowGrid(False)

        tags = list(self.parent.chanceStatusFilter.code_name_dict.items())#获取菜单项
        tags.sort(key =lambda item: item[0])
        tagss = [item[1] for item in tags]
        for i, project in enumerate(self.projects):#tableWidget单元格赋值
            for header in self.cols_names:
                #t3 = time.time()
                if header in ['会议记录', '子任务', '项目备注']:
                    textedit = MyQTextEdit()
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header],textedit)
                    content_data = getattr(project,self.cols_name_key_dict[header])
                    content_list = []
                    #生产单元格文本
                    for log_obj in reversed(content_data):# 倒序生成器
                        log_text = log_obj.getTextLog()
                        content_list.append(log_text)
                    content = '\n'.join(content_list)
                    textedit.setText(content)
                    textedit.setReadOnly(True)
                    # textedit.DoubleClicked.connect(lambda :self.parent.generalLogUnitEdit(
                    #         self.projects,self.bound_widget,allowInsert=True))
                elif header == '客户名称':
                    textedit = MyQTextEdit()
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header],textedit)
                    content = str(getattr(project,self.cols_name_key_dict[header]))
                    textedit.setText(content)
                    textedit.setReadOnly(True)

                elif header == '状态标签':
                    tag_comboBox = QComboBox()
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header],tag_comboBox)
                    tag_comboBox.addItems(tagss)
                    status_code = getattr(project,self.cols_name_key_dict[header])
                    if not isinstance(status_code, int):#查询不到status_code,得到的是字段名称
                        status_code = 0
                    tag_comboBox.setCurrentIndex(int(status_code))#不能用setCurrentText, 否则会触发无关的信号
                    tag_comboBox.currentIndexChanged.connect(self.on_project_chance_tag_changed)

                elif header == '状态设定':
                    status_set_frame = StatusCheckFrame(self.parent)
                    status_set_frame.setStyleSheet('QFrame{border-width: 1px; }')
                    status_set_frame.statusClicked.connect(self.on_project_status_changed)
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header], status_set_frame)
                    chk_status = [getattr(project,'in_act'),
                                  getattr(project,'highlight'),
                                  getattr(project,'clear_chance'),
                                  getattr(project,'order_tobe'),]
                    status_set_frame.setCheckedStatuses(chk_status)
                elif header == '项目名称':
                    textedit = MyQTextEdit()#第二次写到这里的时候改了一下CellWidget的构建方法
                    #t1 = time.time()
                    textedit.setStyleSheet('font: bold;font-family: Microsoft Yahei')
                    textedit.DoubleClicked.connect(self.showProjectPerspective)
                    textedit.project_id = project._id
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header], textedit)
                    textedit.setTabChangesFocus(True)
                    textedit.setReadOnly(True)
                    # textedit.DoubleClicked.connect(lambda : self.parent.detailToProjectPerspective(self.bound_widget, self.detailed_item_body))
                    # textedit.setStyleSheet('background:transparent;border-style:outset')
                    textedit.setText(str(getattr(project,'product')))

        # self.bound_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['会议记录'],360*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['状态标签'], 140*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['项目名称'], 100*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['客户名称'], 100*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['子任务'],360*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['状态设定'], 70*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['项目备注'], 360*DF_Ratio)

    def showProjectPerspective(self):
        _id = self.bound_widget.sender().project_id
        self.parent.showProjectPerspective(_id)

    def on_project_status_changed(self, checkStatus:tuple):
        current_row = self.bound_widget.currentRow()
        project = self.projects[current_row]
        in_act, highlight, clear_chance, order_tobe = checkStatus
        project.in_act = in_act
        project.highlight = highlight
        project.clear_chance = clear_chance
        project.order_tobe = order_tobe
        project.resetWeight()
        project_id = project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['in_act'] = in_act
        fields_values['highlight'] = highlight
        fields_values['clear_chance'] = clear_chance
        fields_values['order_tobe'] = order_tobe
        fields_values['weight'] = project.weight
        conn_company_name = project.client
        command = GProjectCmd('update', _id = project_id, fields_values = fields_values,
                              conn_company_name=conn_company_name,source_widget=self.bound_widget)
        self.parent.listener.accept(command)
        pass

    def on_project_chance_tag_changed(self, index:int):
        current_row = self.bound_widget.currentRow()
        project = self.projects[current_row]
        project_id = project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['status_code'] = index
        conn_company_name = project.client
        command = GProjectCmd('update', _id = project._id, fields_values = fields_values,
                              conn_company_name=conn_company_name,source_widget=self.bound_widget)
        command.need_to_dump_data = False
        self.parent.listener.accept(command)
        CS.upsertSqlite('proj_status_log',keys=['_id','conn_project_id','status_code'],
                        values = [project.status_id,project._id, index])
        # project.saveProjectUpdate()
        pass

    def renderLine(self,i):
        project = self.projects[i]
        cols_names = ['项目名称','客户名称', '会议记录', '状态标签','子任务', '状态设定' , '项目备注']
        cols_keys = ['product','client','meeting_log','status_code','tasks','','memo_log']
        cols_index = list(range(len(cols_names)))
        cols_name_key_dict = dict(zip(cols_names,cols_keys))
        cols_name_index_dict = dict(zip(cols_names,cols_index))
        cols_counts = len(cols_names)
        self.bound_widget.verticalHeader().setDefaultSectionSize(130)
        # tags = list(self.parent.chanceStatusFilter.code_name_dict.items())#获取菜单项
        # tags.sort(key =lambda item: item[0])
        # tagss = [item[1] for item in tags]  # 获取菜单项
        for header in cols_names :
            cell_widget = self.bound_widget.cellWidget(i, cols_name_index_dict[header])
            if header in ['会议记录', '子任务', '项目备注'] :
                textedit = cell_widget
                # textedit = self.bound_widget.cellWidget(i, cols_name_index_dict[header])
                content_data = getattr(project, cols_name_key_dict[header])
                content_list = []
                for log_obj in reversed(content_data):
                    log_text = log_obj.getTextLog()
                    content_list.append(log_text)
                content = '\n'.join(content_list)
                textedit.setText(content)
                textedit.setReadOnly(True)
                # textedit.DoubleClicked.connect(lambda :self.parent.generalLogUnitEdit(
                #         self.projects,self.bound_widget,allowInsert=True))
            elif header == '客户名称' :
                textedit = cell_widget
                # self.bound_widget.setCellWidget(i, cols_name_index_dict[header], textedit)
                content = str(getattr(project, cols_name_key_dict[header]))
                textedit.setText(content)
                textedit.setReadOnly(True)

            elif header == '状态标签' :
                tag_comboBox = cell_widget # 控件实际上是comboBox, 所以换一个名字
                # self.bound_widget.setCellWidget(i, cols_name_index_dict[header], tag_comboBox)
                # tag_comboBox.addItems(tagss)
                tag_comboBox.setCurrentIndex(int(getattr(project, 'status_code')))

            elif header == '状态设定' :
                status_set_frame = cell_widget
                # self.bound_widget.setCellWidget(i, cols_name_index_dict[header], status_set_frame)
                chk_status = [getattr(project, 'in_act'),
                              getattr(project, 'highlight'),
                              getattr(project, 'clear_chance'),
                              getattr(project, 'order_tobe'), ]
                status_set_frame.setCheckedStatuses(chk_status)
            elif header == '项目名称' :
                textedit = cell_widget
                textedit.DoubleClicked.connect(self.showProjectPerspective)
                textedit.project_id = project._id
                textedit.setTabChangesFocus(True)
                textedit.setReadOnly(True)
                # textedit.DoubleClicked.connect(lambda : self.parent.detailToProjectPerspective(self.bound_widget, self.detailed_item_body))
                textedit.setStyleSheet('font: bold;font-family: Microsoft Yahei')
                textedit.setText(str(getattr(project, 'product')))

class PerspectiveView(View):
    contain_root_item = 'project'

    def __init__(self, parent =None):
        super(PerspectiveView, self).__init__()
        # print('PerspectiveView created')
        self.project = None
        self.parent = parent
        self.accept_state = AccceptState()#状态机，跟踪接收广播的情况

    def setDataModel(self, project_id):
        self.project_id = project_id
        self.project = Project()
        self.project.load_id_data(self.project_id)

    def initAllData(self):
        self.project = Project()
        self.project.load_id_data(self.project_id)
        self.tab_bar.initAllData()

    def Accept(self,cmd):
        if cmd.broadcast_space is None:
            #如果收到的广播命令没有绑定广播域，则将接收状态重置，并设定到接收完成状态
            self.accept_state.__init__()
            self.accept_state.acceptComplete()
        elif self.accept_state.accept_ID != cmd.broadcast_space.broadcast_ID:#接收到了新的广播域
            #重置接收状态
            self.accept_state.__init__(cmd.broadcast_space.broadcast_ID, cmd.broadcast_space.broadcast_names)
            self.accept_state.argAccepted(cmd._id)
        else:
            self.accept_state.argAccepted(cmd._id)

        global_logger.debug('perspective accepted')
        target_flag = cmd.flag
        if target_flag  == 1:#project
            self.acceptProjectCmd(cmd)
        elif target_flag == 2:#task
            self.acceptTaskCmd(cmd)
        elif target_flag == 3:#meeting
            self.acceptMeetingCmd(cmd)
        elif target_flag == 4:#memo
            self.acceptMemoCmd(cmd)
        elif target_flag == 5:#personnel
            self.acceptPersonnel(cmd)
        else:
            return

    def acceptTaskCmd(self,cmd):
        global_logger.debug('Perspective accepted task')
        client_name = cmd.conn_company_name
        project_id = cmd.fields_values['conn_project_id']
        pending_till_date = cmd.fields_values.get('pending_till_date', None)
        task_id = cmd._id
        source_widget = cmd.source_widget
        # 查找被修改的task
        if project_id != self.project._id:
            return
        if cmd.operation == 3:  # insert
            new_task = Task(task_id, project_id)
            new_task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
            new_task.pending_till_date = pending_till_date
            self.project.tasks.insert(new_task.inter_order_weight-1, new_task)
            if self.accept_state.accept_complete:
                self.project.resetWeight()
            if source_widget is self.tab_bar or self.accept_state.accept_complete == False:#接收未完成
                return
            else:
                self.renderTaskUnit()#接收完成
                return

        for k, task in enumerate(self.project.tasks):
            if task_id == task._id:
                if cmd.operation == 1 :  # update
                    task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    task.pending_till_date = pending_till_date
                    if self.accept_state.accept_complete:
                        self.project.resetWeight()
                elif cmd.operation == 4 :  # delete
                    del self.project.tasks[k]
                if source_widget is self.tab_bar or self.accept_state.accept_complete == False:
                    return
                else:
                    self.renderTaskUnit()
        else :
            return

    def acceptProjectCmd(self,cmd):
        global_logger.debug('perspective accepted project')
        project = self.project
        client_name = cmd.conn_company_name
        project_id = cmd._id
        source_widget = cmd.source_widget
        if project_id != self.project._id:
            return
        #根据operation flag选择操作
        if cmd.operation == 3 or cmd.operation == 4:#insert or delete
            pass
            raise PermissionError('operation type not applicable')
        elif cmd.operation == 1:#update
            project.assign_data(list(cmd.fields_values.keys()),list(cmd.fields_values.values()))
            project.resetWeight()
            if source_widget is self.tab_bar:
                return
            else:
                self.renderProjectUnit()
                # self.renderTaskUnit()
                return

    def acceptMeetingCmd(self,cmd):
        global_logger.debug('Perspective accepted task')
        client_name = cmd.conn_company_name
        project_id = cmd.fields_values['conn_project_id']
        meeting_id = cmd._id
        source_widget = cmd.source_widget
        # 查找被修改的task
        if project_id != self.project._id:
            return
        if cmd.operation == 3:  # insert
            new_meeting = Meeting()
            new_meeting._id = meeting_id
            new_meeting.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
            self.project.meeting_log.insert(new_meeting.inter_order_weight-1, new_meeting)#inter_order_weight是从1开始计数
            if source_widget is self.tab_bar:
                return
            else:
                self.renderMeetingUnit()
                return
        for k, meeting in enumerate(self.project.meeting_log) :
            if meeting_id == meeting._id :
                if cmd.operation == 1 :  # update
                    meeting.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                elif cmd.operation == 4 :  # delete
                    del self.project.meeting_log[k]
                if source_widget is self.tab_bar :
                    return
                else :
                    self.renderMeetingUnit()
                    return
        else :
            return

    def acceptMemoCmd(self,cmd):
        global_logger.debug('Perspective accepted task')
        client_name = cmd.conn_company_name
        project_id = cmd.fields_values['conn_project_id']
        memo_id = cmd._id
        source_widget = cmd.source_widget
        # 查找被修改的task
        if project_id != self.project._id:
            return
        if cmd.operation == 3:  # insert
            new_memo = Memo()
            new_memo._id = memo_id
            new_memo.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
            self.project.memo_log.insert(new_memo.inter_order_weight -1, new_memo)
            if source_widget is self.tab_bar:
                return
            else:
                self.renderMemoUnit()
                return
        for k, memo in enumerate(self.project.memo_log) :
            if memo_id == memo._id :
                if cmd.operation == 1 :  # update
                    memo.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                elif cmd.operation == 4 :  # delete
                    del self.project.memo_log[k]
                if source_widget is self.tab_bar :
                    return
                else :
                    self.renderMemoUnit()
                    return
        else :
            return

    def acceptPersonnel(self,cmd):
        if cmd._id == self.project.client_id:
            self.tab_bar.initPersonnelSet()

    def renderWidget(self, parent_widget):
        #parent_widget 是 主窗体
        self.tab_bar = ProjectTabBar(self.project, parent_widget)
        tab_header = self.project.product
        company_name = self.project.client
        project_name = self.project.product
        parent_widget.tabWidget.addTab(self.tab_bar,tab_header)
        # ResAdaptor.init_ui_size(self.tab_bar)
        self.tab_bar.label_4.setText(company_name+'--'+project_name)
        self.tab_bar.label_4.setStyleSheet('font-size: 6pix ')
        closeButton =QPushButton()
        closeButton.setFixedSize(13 * FIX_SIZE_WIDGET_SCALING, 13 * FIX_SIZE_WIDGET_SCALING)

        icon_close = QIcon()
        pix = QPixmap(f"{working_dir}/images/closeIcon13x13_1.png")
        # pix = pix.scaled(13,13, Qt.KeepAspectRatio)
        icon_close.addPixmap(pix, QIcon.Normal, QIcon.Off)

        closeButton.setIcon(icon_close)
        closeButton.clicked.connect(lambda: parent_widget.tabWidget.removeTab(parent_widget.tabWidget.indexOf(self.tab_bar)))
        closeButton.clicked.connect(self.releaseMemory)
        parent_widget.tabWidget.tabBar().setTabButton(parent_widget.tabWidget.tabBar().count()-1 ,QTabBar.RightSide,closeButton)
        parent_widget.tabWidget.setCurrentIndex(parent_widget.tabWidget.indexOf(self.tab_bar))

    def renderProjectUnit(self):
        self.tab_bar.initProjectSet()

    def renderTaskUnit(self):
        self.tab_bar.initTable()
        self.tab_bar.initCurrentTaskSet()
        self.tab_bar.initProjectSet()

    def renderMeetingUnit(self):
        self.tab_bar.initTable_2()

    def renderMemoUnit(self):
        self.tab_bar.initTable_3()

    def releaseMemory(self):
        self.parent.listener.removeObserver(self)
        for i, record in enumerate(self.parent.tabBarAdded):
            if self.project._id == record[0]:
                self.parent.tabBarAdded.pop(i)
        self.tab_bar.deleteLater()
        del self

class CompanyEidtorView(View):
    contain_root_item = 'company'

    def __init__(self,company_category = None, parent = None):
        '''company_category的值决定了使用哪一个类(Client，Supplier)作为数据模型'''
        super(CompanyEidtorView, self).__init__()
        self.parent = parent
        self.company_category = company_category

    def setDataModel(self, company_name:str = None, company_id:str = None):

        if self.company_category == 'client':
            self.company = Client(company_name=company_name,_id=company_id)
        elif self.company_category == 'supplier':
            # self.company == Supplier()
            pass
        elif not self.company_category:
            self.company = Company()
        self.company.loadBasicData()
        self.company.loadCompanyLogs()
        self.company.setPersonnelClass()

    def initAllData(self):
        self.company.loadBasicData()
        self.company.loadCompanyLogs()
        self.company.setPersonnelClass()
        self.tab_bar.initAllData()

    def saveDataModel(self):
        self.company.saveAllData()
        pass

    def Accept(self,cmd):
        if cmd.flag == TargetFlag.personnel:
            self.acceptPersonnel(cmd)

    def acceptPersonnel(self,cmd):
        if cmd._id == self.company._id:
            self.tab_bar.company.loadBasicData()
            self.tab_bar.company.setPersonnelClass()
            self.tab_bar.setPersonnelInfo()

    def modifyBasicData(self):
        pass

    def modifyCompanyLogs(self):
        pass

    def modifyPersonnelClass(self):
        pass

    def setupUi(self, parent_widget):
        #parent_widget 是 主窗体
        self.tab_bar = CompanyEditorTabBar(self.company, self.parent, parent_widget)
        # self.tab_bar.setStyleSheet('QTextEdit {'
        #                            'border-width: 1px;'
        #                            'border-style: dashed;'
        #                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                            'stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
        tab_header = self.company.short_name
        parent_widget.addTab(self.tab_bar,tab_header)
        closeButton =QPushButton()
        closeButton.setFixedSize(13*FIX_SIZE_WIDGET_SCALING, 13*FIX_SIZE_WIDGET_SCALING)
        icon_close = QIcon()
        pix = QPixmap(f"{working_dir}/images/closeIcon13x13_1.png")
        # pix = pix.scaled(13, 13, Qt.KeepAspectRatio)
        icon_close.addPixmap(pix, QIcon.Normal, QIcon.Off)
        closeButton.setIcon(icon_close)
        closeButton.clicked.connect(lambda :parent_widget.removeTab(parent_widget.indexOf(self.tab_bar)))
        closeButton.clicked.connect(self.releaseMemory)
        # closeButton.clicked.connect(self.releaseMemory)
        parent_widget.tabBar().setTabButton(parent_widget.tabBar().count()-1 ,QTabBar.RightSide,closeButton)
        parent_widget.setCurrentIndex(parent_widget.indexOf(self.tab_bar))

    def releaseMemory(self):
        for i, record in enumerate(self.parent.tabBarAdded):
            if self.company._id == record[0]:
                self.parent.tabBarAdded.pop(i)
        self.parent.listener.removeObserver(self)
        self.tab_bar.deleteLater()
        del self


class OutputMode(object):
    pass

class MultiSelectGroupBoxHandler(object):
    MARGIN_X = 5
    MARGIN_Y = 5
    col_between_width = 20
    row_between_width = 5
    col_content_base_width = 50
    check_item_empty_width = 10
    def __init__(self, bound_widget:QtWidgets.QGroupBox, model_list:list[str], n_rows = 4 ):
        self.bound_widget = bound_widget
        self.model_list = model_list
        self.n_rows = n_rows

    def setBoundWidget(self,bound_widget:QWidget):
        self.bound_widget = bound_widget

    def clearBoundWidget(self):
        btns = self.bound_widget.findChildren(QCheckBox)
        for btn in btns:
            btn.deleteLater()

    def getCheckedIndex(self):
        checked_Index = []
        for i , model in enumerate(self.model_list):
            checked = self.bound_widget.findChildren(QCheckBox)[i].isChecked()
            if checked:
                checked_Index.append(i)
        return checked_Index

    def setupWidget(self):
        '''传入父窗体中指定的groupBox, 对其进行绘制'''
        base_moveX = self.MARGIN_X
        base_moveY = self.MARGIN_Y + 10
        frame_base_width = self.MARGIN_X * 2
        frame_base_height = self.MARGIN_Y * 2
        col_between_width = self.col_between_width
        col_content_base_width = self.col_content_base_width
        frame_width = 0
        check_item_empty_width = self.check_item_empty_width
        check_item_width_max = 0
        i_row = 0
        moveY = base_moveY
        moveX = base_moveX
        tmp_frame_height = frame_base_height
        frame_height = 0
        for i, model in enumerate(self.model_list):
            if i_row >= self.n_rows:
                moveY = base_moveY
                moveX += max(check_item_width_max, col_content_base_width) + col_between_width
                frame_width += max(check_item_width_max, col_content_base_width) + col_between_width
                frame_height = max(frame_height,tmp_frame_height)
                tmp_frame_height = frame_base_height
                i_row = 0

            address = id(self.bound_widget)
            get_value = ctypes.cast(address, ctypes.py_object).value
            check_item = QCheckBox(get_value)

            check_item.setText(model)
            fM = QFontMetrics(check_item.font())
            text_wid = fM.boundingRect(check_item.text()).width()
            text_height = fM.boundingRect(check_item.text()).height()
            item_wid = text_wid + check_item_empty_width
            item_height = text_height + 3
            check_item_width_max = max(item_wid, check_item_width_max)
            tmp_frame_height += item_height + self.row_between_width
            check_item.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
            check_item.move(moveX ,  moveY)

            moveY += item_height + self.row_between_width
            i_row += 1
            check_item.show()

        frame_width += max(check_item_width_max, col_content_base_width) + col_between_width + frame_base_width
        frame_height = max(frame_height, tmp_frame_height)

        self.bound_widget.setMinimumSize(QSize(frame_width, frame_height))

class GeoFilterEditorView(object):

    def __init__(self, parent = None):
        self.model = GeoModel()
        self.parent = parent
        self.bound_wigdet = None

    def setDialogUi(self):
        self.model = GeoModel()
        self.dialog = GeoFilterEditor(parent=self.parent)
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        edit_used = self.dialog.exec()
        if edit_used:
            self.model = GeoModel()
            self.model.loadUserClientFilter()
            self.clearBoundWidget()
            self.setupWidget()

    def setBoundWidget(self, bound_widget:QWidget):
        self.bound_widget = bound_widget
        self.bound_widget_handler = MultiSelectGroupBoxHandler(bound_widget, self.model.locates)

    def setupWidget(self):
        self.bound_widget_handler.model_list = self.model.locates
        self.bound_widget_handler.setupWidget()

    def clearBoundWidget(self):
        self.bound_widget_handler.clearBoundWidget()

    def getCheckedLocates(self):
        checked_indexes = self.bound_widget_handler.getCheckedIndex()
        checked_locates = [self.model.locates[i] for i in checked_indexes]
        return checked_locates

    def getCheckedCities(self):
        if not self.bound_widget.isChecked():
            return None
        '''根据父窗体中的groupBox中的CheckBox的选中状态，返回被选中的城市'''
        checked_locates = self.getCheckedLocates()
        if not checked_locates:
            return None
        check_city_codes = []
        for i, locate in enumerate(checked_locates):
            check_city_codes.extend(self.model.client_dict[locate])
        return check_city_codes

    def getCompanyInCheckedCities(self):
        #todo 在正式上线版本中，只有一种行政区域编码方式，且不应该使用这种先通过city查company再查project的方式，而是inner join方式
        checked_cities = self.getCheckedCities()
        if checked_cities is None:
            return None
        condition_keys = ('province','city')
        condition_values = []
        conditions2 = {'city':[]}
        for city in checked_cities:
            country, province, city = city
            condition_values.append((province, city))
            city = str(city)
            if len(city) == 1:
                city = '0'+city
            print(province)
            full_city_code = str(province) + str(city)
            # full_city_code = convertInt(full_city_code)
            conditions2['city'].append(full_city_code)
        # 此处对于新旧两种行政区域编码方式做了适应
        find_companies1 = CS.multiConditionsGetLinesFromSqlite('clients', condition_keys=condition_keys,
                                                               condition_values=condition_values,columns_required=['_id'])
        find_companies1.pop()
        find_companies2 = CS.getLinesFromTable('clients', conditions=conditions2, columns_required=['_id'])
        find_companies2.pop()
        checked_companies = [found[0] for found in find_companies1]
        set1 = set(checked_companies)
        checked_companies = [found[0] for found in find_companies2]
        set2 = set(checked_companies)
        find_companies = set1.union(set2)

        return list(find_companies)

class CompanyFilterView(object):
    def __init__(self,parent = None):
        self.company_group_model = CompanyGroupModel()
        self.parent = parent
        self.model = CompanyGroupModel()
        self.bound_widget = None

    def setDialogUi(self):
        self.model = CompanyGroupModel()
        self.dialog = CompanyFilterEditor(parent=self.parent)
        # self.dialog.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        edit_used = self.dialog.exec()
        if edit_used:
            self.model = CompanyGroupModel()
            self.model.loadUserCompanyGroupFilter()
            self.clearBoundWidget()
            self.setupWidget()

    def setBoundWidget(self,bound_widget:QWidget):
        self.bound_widget = bound_widget
        self.bound_widget_handler = MultiSelectGroupBoxHandler(bound_widget,self.model.groups)

    def clearBoundWidget(self):
        self.bound_widget_handler.clearBoundWidget()

    def getCheckedGroups(self):
        check_indexes = self.bound_widget_handler.getCheckedIndex()
        checked_groups = [self.model.groups[i] for i in check_indexes]
        return checked_groups

    def setupWidget(self):
        '''传入父窗体中指定的groupBox, 对其进行绘制'''
        self.bound_widget_handler.model_list = self.model.groups
        self.bound_widget_handler.setupWidget()

    def getCheckedCompanies(self):
        if not self.bound_widget.isChecked():
            return None
        checked_groups = self.getCheckedGroups()
        if not checked_groups:
            return None
        checked_companies = []
        for group in checked_groups:
            companies = self.model.company_dict[group]
            checked_companies.extend(companies)
        return checked_companies

class ChanceStatusFilterView(object):
    '''从csv文件读取机会标签的信息，并根据主窗口groupBox控件的选择情况返回被选择的标签代码，全局单例'''
    _instance = None
    has_instance = False
    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        cls._instance = super(ChanceStatusFilterView, cls).__new__(cls)
        return cls._instance

    def __init__(self, bound_widget:QWidget = None):
        if self.has_instance:
            return
        self.has_instance = True
        self.change_tags = []
        self.bound_widget = bound_widget
        def convertInt(str:str):
            if str.isdigit():
                return int(str)
            else:
                return str
        with open(f'{working_dir}/tag_projection.csv') as f:
            f_tag_projection = csv.reader(f)
            headings = next(f_tag_projection)
            for r in f_tag_projection:
                Row = namedtuple('Row', headings)
                r = map(convertInt, r)
                row = Row(*r)
                self.change_tags.append(row)
        #创建两个字典：{sequence_code:chance_tag_name},{change_code:[sequence_code]}
        #csv模块读取到的都是字符串，数字需要转换
        change_codes = [row.chance_code for row in self.change_tags]
        change_codes = list(set(change_codes))
        self.chance_sequence_code_dict = {}
        for item in change_codes:
            self.chance_sequence_code_dict[item] = []
        self.code_name_dict = {}
        for row in self.change_tags:
            self.code_name_dict[row.sequence_code] =  row.chance_tag_name
            self.chance_sequence_code_dict[row.chance_code].append(row.sequence_code)

    def getTagName(self,sequence_code:int):
        return self.code_name_dict[sequence_code]

    def getCheckedChanceCode(self):
        check_chance_codes = []
        for i, check_box in enumerate(self.bound_widget.findChildren(QCheckBox)):
            if check_box.isChecked():
                check_chance_codes.append(i+1)
        return check_chance_codes

    def getCheckedSequenceCode(self):
        if not self.bound_widget.isChecked():
            return []
        checked_chance_codes = self.getCheckedChanceCode()
        checked_sequence_codes = []
        for code in checked_chance_codes:
            checked_sequence_codes.extend(self.chance_sequence_code_dict[code])
        return checked_sequence_codes

    def getCheckedProjects(self):
        if not self.bound_widget.isChecked():
            return []
        checked_sequence_codes = self.getCheckedSequenceCode()
        find_project = CS.getLinesFromTable('proj_status_log', conditions={'status_code':checked_sequence_codes},
                                            columns_required=['conn_project_id'])
        find_project.pop()
        checked_projects = [found[0] for found in find_project]
        return checked_projects

class Listener(object):
    #获取到命令后，判断，1.需要做什么操作，并操作数据库；2.判断是否需要将命令通知其他成员，需要的话就将命令传递给发布者
    #哪些命令是需要通知其他人的呢？

    def __init__(self):
        self.observers = []
        print(self.observers)

    def addObserver(self,obj):
        if obj not in self.observers:
            self.observers.append(obj)
    #数据会影响到谁：db,

    def removeObserver(self,obj):
        if obj in self.observers:
            self.observers.remove(obj)

    def accept(self,cmd):
        self.dumpCmdData(cmd)
        self.notify(cmd)

    def dumpCmdData(self,cmd):
        if not cmd.need_to_dump_data:
            return
        if cmd.flag == 5:
            return
        db_cmd = GDbCmd(cmd)
        db_cmd.dumpData()
        pass

    def notify(self,cmd):
        for obs in self.observers:
            obs.Accept(cmd)
        pass

    def rerender(self):
        for obs in self.observers:
            obs.initAllData()

if __name__ == '__main__':
    global_logger.debug('hDC={}'.format(hDC))
    global_logger.debug('screen_real_hResolution={}'.format(screen_real_hResolution))
    global_logger.debug('screen_real_VResolution={}'.format(screen_real_vResolution))

