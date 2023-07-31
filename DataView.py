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
from TodoViewTabBar import TodoViewTabBar
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

def new_dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        a0.accept()
        pass

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
        proj_ids_with_clients = CS.getLinesFromTable('proj_list',conditions=condition,
                                                     columns_required=['_id','client_id'])
        proj_ids_with_clients.pop()

        if not proj_ids_with_clients:
            QMessageBox.about(self.parent, '未找到', '没有符合条件的项目！')
            return
        # before_make_client_ids = time.perf_counter()
        #获取符合条件的client列表
        client_ids = []
        for item in proj_ids_with_clients:
            client_ids.append(item[1])
        client_ids = list(set(client_ids))
        #
        # temp.sort(key=client_ids.index)
        # client_short_names = temp
        #初始化client_proj字典, 每个client的project集合构成一个列表
        client_proj_ids = {}
        for client_id in client_ids:
            client_proj_ids[client_id] = []
        #
        #生成client_proj字典
        for item in proj_ids_with_clients:
            client_proj_ids[item[1]].append(item[0])
        before_make_clients = time.perf_counter()
        #形成clients数据信息
        ConnSqlite.cor.execute('BEGIN')
        for i, client_id in enumerate(client_ids):
            proj_ids = client_proj_ids[client_id]#客户的所有相关proj_id
            client_tmp = Client(_id=client_id)#生成一个client类实例
            before_make_projects = time.perf_counter()

            status_code_info = CS.getLinesFromTable(table_name='proj_status_log',
                                                    conditions={'conn_project_id': proj_ids},
                                                    columns_required=['conn_project_id','status_code'])
            status_code_info.pop()
            proj_status_code = dict(status_code_info)

            proj_task_in_act = CS.innerJoin_withList_getLines('tasks', 'todo_log', '_id', 'conn_task_id',
                                                          ['conn_project_id', 'is_critical'], ['status', 'destroyed'],
                                                          {'conn_project_id': proj_ids, 'is_critical': 1}, {'destroyed':0, 'status': [0, 1]},
                                                          method='left join')
            proj_task_critical = {}
            for conn_project_id, is_critical, status, destroyed in proj_task_in_act:
                if is_critical and status is not None and status < 2 and not destroyed:
                    proj_task_critical.update({conn_project_id: True})

            for id in proj_ids:
                project_tmp = Project(id)#生成一个project类实例
                project_tmp.load_basic_data()
                project_tmp.status_code = proj_status_code.get(id, 0)
                project_tmp.has_active_task_critical = proj_task_critical.get(id, False)
                #此时的project包含了memo、meeting信息
                client_tmp.addProject(project_tmp)
            end_make_projects = time.perf_counter()
            # print('time_for_make_client_projects:',end_make_projects - before_make_projects)
            client_tmp.loadCompanyLogs()
            # print(client_tmp)
            # print(client_tmp.projects)
            self.clients.append(client_tmp)
        ConnSqlite.cor.execute('COMMIT')
        end_function = time.perf_counter()
        # print('time_for_proj_ids:',before_make_client_ids - before_make_proj_ids)
        # print('time_for_client_ids:',before_make_clients - before_make_client_ids)
        # print('time_for_clients:', end_function - before_make_clients)
        # print('time_for_overviewModel:',end_function - before_make_proj_ids)

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
        for i , client in enumerate(self.clients):
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
        for i in range(len(self.current_clients)):
            loop_start = time.perf_counter()
            row_index = i // 5
            column_index = i % 5
            #创建单元格->TextBrowser的基本显示样式
            textBrowser = MyQTextBrowser()
            textBrowser.index = i
            self.bound_widget.setCellWidget(row_index,column_index, textBrowser)
            make_widget_end = time.perf_counter()
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
            loop_end = time.perf_counter()
            # print('time for make widget%s:'%i, make_widget_end - loop_start)
            # print('time for html_render%s:'%i, html_render_end - before_html_render)
            # print('time for loop%s'%i,loop_end - loop_start)
        render_stop = time.perf_counter()

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
        self.bound_widget.cellWidget(row_index,column_index).setText(text_log)
        self.bound_widget.cellWidget(row_index,column_index).DoubleClicked.connect(lambda : self.customer_DBclicked_search(client.short_name))
        #添加右键菜单
        self.bound_widget.cellWidget(row_index,column_index).setContextMenuPolicy(Qt.CustomContextMenu)
        self.bound_widget.cellWidget(row_index,column_index).customContextMenuRequested.connect(self.create_rightMemu)
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

        self.bound_widget.cellWidget(row_index,column_index).setToolTip(self.wrapTooltip(tooltip,25))
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

        for k, task in enumerate(self.project.tasks) :
            if task_id == task._id :
                if cmd.operation == 1 :  # update
                    task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    task.pending_till_date = pending_till_date
                    if self.accept_state.accept_complete:
                        self.project.resetWeight()
                elif cmd.operation == 4 :  # delete
                    del self.project.tasks[k]
                if source_widget is self.tab_bar or self.accept_state.accept_complete == False:
                    return
                else :
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

class TodoUnitView(View):
    def __init__(self, parent = None,  parent_view = None):
        super(TodoUnitView, self).__init__()
        self.parent = parent
        self.parent_view = parent_view# todo_view
        self.todoWidget = None
        self.model = ToDo()
        self.Todo_Font_Style = 'font-family:Microsoft YaHei; font-weight:405; font-size: %spt'%(9*CONTENT_TEXT_SCALING)

    def conclusionDoubleClickEvent(self, obj, e):
        data_json = self.model.conclusion_desc
        log_eidt_table = RedefinedWidget.JsonLogEditTable(self.parent, data = data_json, attachedWidget=obj,
                                                          column_widths=[80*ResAdaptor.ratio_wid,200*ResAdaptor.ratio_wid])
        log_eidt_table.show()
        log_eidt_table.EditingFinished.connect(self.on_conclusion_desc_update)

    def textEdit_focusOutEvent(self, textEdit:QTextEdit, e):
        reason = e.reason()
        if e.reason() == Qt.PopupFocusReason:
            return
        if textEdit.edited == False:
            textEdit.setReadOnly(True)
            pass
        else:
            self.textEditingFinished(textEdit)
        if hasattr(self,'edited'):
            self.edited = False
        textEdit.setText(textEdit.toPlainText())
        QTextEdit.focusOutEvent(textEdit,e)

    def setDataModel(self, _id:str):
        self.model.load_basic_data(_id)
        self.model.loadConnProjectInfo()

    def setWidget(self):
        self.todoWidget = RedefinedWidget.ToDoUnitWidget(self.parent, self.model, self.parent_view.drag_drop_enabled)
        # self.todoWidget.setUpdatesEnabled(False)
        # self.todoWidget.lineEdit.setMinimumWidth(40)
        ResAdaptor.init_ui_size(self.todoWidget)
        self.todoWidget.setObjectName('todo_widget')
        self.todoWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.customContextMenuRequested.connect(self.showTodoMenu)
        self.todoWidget.setStyleSheet(
                           '#todo_widget{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;'
                           'border-radius:7px; border-style: dashed;border-color: '
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}'
                           '#todo_widget:hover{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;'
                           'border-radius:7px; border-style: solid;border-color: '
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(180, 220, 255, 205), stop:1 rgba(151, 201, 252, 205));}'
                           'QLabel{border-width: 0px; background:transparent;}'
                           'QTextEdit{font-family:Microsoft YaHei; font-size: %spt;border-width: 2px; border-style:dashed; border-color: rgba(150, 150, 150, 40)}'
                           'QLineEdit{background:transparent;border-color: rgba(150, 150, 150, 150)}'
                           'QScrollBar:vertical{width: 4px;background:transparent;border: 0px;margin: 0px 0px 0px 0px;}'
                           'QScrollBar::handle:vertical{background:transparent; border-radius:2px;}'
                           'QScrollBar::handle:vertical:hover{background:lightskyblue; border-radius:2px;}'
                           'QScrollBar::add-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
                                      'height:0px;width:0px;subcontrol-position:bottom;subcontrol-origin: margin;}'
                           'QScrollBar::sub-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
                                      'height:0px;width:0px;subcontrol-position:top;subcontrol-origin: margin;}'
                           '#pushButton_company,#pushButton_project{border-style: solid;border-top-color: '
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '
                           'stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, '
                           'x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
                           'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '
                           'stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
                           'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
                           'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
                                      'border-width: 0px;border-radius: 0px;color: #202020;text-align: '
                           'left;font-family: Microsoft YaHei;font:bold;font-size:%spt;'
                                      'padding: 0px;background-color: rgba(220,220,220,0);}'
                            '#pushButton_company:hover,#pushButton_project:hover{border-style: solid;'
                           'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
                           'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	'
                           'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '
                           'stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
                           'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '
                           'stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
                           'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
                           'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
                            'border-width: 1px;border-radius: 5px;color: #202020;text-align: left;'
                           'font-family: Microsoft YaHei;font:bold;font-size:%spt;'


                                      'padding: 0px;background-color: rgb(200,225,255);}'%(8*CONTENT_TEXT_SCALING, 7*CONTENT_TEXT_SCALING, 7*FIX_SIZE_WIDGET_SCALING))

        #buttons signal
        if self.model.conn_company_name:
            self.todoWidget.pushButton_company.setText(self.model.conn_company_name)
        else:
            self.todoWidget.pushButton_company.setText('')
            self.todoWidget.pushButton_company.setEnabled(False)
        # self.todoWidget.setObjectName('todo_unit')
        if self.model.conn_project_name :
            self.todoWidget.pushButton_project.setText(self.model.conn_project_name)
        else:
            self.todoWidget.pushButton_project.setText('')
            self.todoWidget.pushButton_project.setEnabled(False)
        self.todoWidget.pushButton_company.clicked.connect(self.on_company_clicked)
        # self.todoWidget.commandLinkButton.setDescription()
        self.todoWidget.pushButton_project.clicked.connect(self.on_project_clicked)
        self.todoWidget.isCritial_slideButton.toggled.connect(self.on_isCritial_slideButton_clicked)
        self.todoWidget.todoTimeSpaceDistance_triSliderButton.toggled.connect(self.on_todoTimeSpaceDistance_triSlideButton_toggled)
        self.todoWidget.todoStatus_triSlideButton.toggled.connect(self.on_todoStatus_triSlideButton_toggled)
        self.todoWidget.pushButton_4.setStyleSheet('QPushButton:checked{background:lightblue}')
        self.todoWidget.pushButton_4.clicked.connect(self.on_pending_activated)
        self.todoWidget.pushButton_5.setEnabled(False)
        self.todoWidget.pushButton_5.clicked.connect(self.on_pending_deactivated)
        self.todoWidget.pushButton_6.clicked.connect(self.on_delete_clicked)
        #textEdits signal
        self.todoWidget.textEdit.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit)
        # self.todoWidget.textEdit_2.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit_2)
        self.todoWidget.textEdit_2.mouseDoubleClickEvent = types.MethodType(self.conclusionDoubleClickEvent, self.todoWidget.textEdit_2)
        self.todoWidget.textEdit.setText(self.model.todo_desc)
        self.todoWidget.textEdit_2.setText(DataCenter.convert_date_log_json(self.model.conclusion_desc))
        self.todoWidget.textEdit.setContentsMargins(1, 1, 1, 1)
        self.todoWidget.textEdit_2.setContentsMargins(1, 1, 1, 1)
        self.todoWidget.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.textEdit.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit))
        self.todoWidget.textEdit_2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.textEdit_2.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit_2))
        self.todoWidget.lineEdit.editingFinished.connect(self.on_slider_close)
        self.todoWidget.lineEdit.setEnabled(False)
        #根据字段参数初始化各个参数控件
        # today = datetime.datetime.today().date()
        if self.model.on_pending:
            self.todoWidget.pushButton_4.setChecked(True)
        if self.model.pending_till_date:
            pending_days = (datetime.datetime.strptime(str(self.model.pending_till_date), '%Y-%m-%d').date()\
                            - datetime.datetime.today().date()).days
            #datetime两个日期相减得到的数字是实际数字相减的结果
            if pending_days > 0:
                self.todoWidget.lineEdit.setText(str(pending_days))
                self.todoWidget.label.setText(self.model.pending_till_date)
                self.todoWidget.lineEdit.setEnabled(True)
                self.todoWidget.pushButton_5.setEnabled(True)
            else:
                self.todoWidget.lineEdit.setText('')
                self.todoWidget.label.setText('')
        else:
            self.todoWidget.lineEdit.setText('')
            self.todoWidget.label.setText('')
        self.todoWidget.isCritial_slideButton.setChecked(self.model.is_critical)
        self.todoWidget.todoStatus_triSlideButton.setCheckstatus(self.model.status)
        self.todoWidget.todoTimeSpaceDistance_triSliderButton.setCheckstatus(self.model.timespace_distance)
        self.style = ''
        if self.model.conn_project_id:
            if self.model.conn_project_order_tobe:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectOrderTobe),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.model.conn_project_clear_chance:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectClearChance),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.model.conn_project_highlight:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectHighlight),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.model.conn_project_in_act:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectInAct),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            else:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{%s}'%self.Todo_Font_Style)
                self.style = self.todoWidget.textEdit.styleSheet()
                pass
        else:
            self.todoWidget.textEdit.setStyleSheet('#textEdit{%s}'%self.Todo_Font_Style)
            self.style = self.todoWidget.textEdit.styleSheet()
        if self.model.is_critical:
            self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                   '%s}'%(str(getAlphaColor(GColour.TaskColour.TaskIsCritial, 180)),self.Todo_Font_Style))
        # self.todoWidget.setUpdatesEnabled(True)

    def setOfficejobType(self,X:str):
        if self.model.officejob_type == X:
            return
        self.model.officejob_type = X
        if self.model.conn_task_id:
            self.model.conn_task_cat = X
        self.updateConnData()

    def textEditingFinished(self,textEditWidget:QTextEdit):
        if textEditWidget.isReadOnly():#未进行内容修改
            return
        textEditWidget.setReadOnly(True)
        if textEditWidget is self.todoWidget.textEdit:
            self.model.todo_desc = textEditWidget.toPlainText()
            # textEditWidget.setText(self.model.todo_desc)
        elif textEditWidget is self.todoWidget.textEdit_2:#conclusion
            self.model.conclusion_desc = textEditWidget.toPlainText()
            # textEditWidget.setText()
        self.updateConnData()

    def on_conclusion_desc_update(self, json_data:str):
        self.model.conclusion_desc = json_data
        log_text = DataCenter.convert_date_log_json(json_data)
        self.todoWidget.textEdit_2.setText(log_text)
        self.updateConnData()

    def updateConnData(self):
        self.model.saveBasicData()
        if self.model.conn_task_id:
            fields_values = {}
            fields_values['_id'] = self.model.conn_task_id
            fields_values['task_desc'] = self.model.todo_desc
            fields_values['update_desc_list'] = self.model.conclusion_desc
            fields_values['conn_project_id'] = self.model.conn_project_id
            if self.model.officejob_type:#
                fields_values['officejob_type'] = self.model.officejob_type#not Null constrain
            #如果关联的task已经被删除，则发送出去的更新命令查找不到目标task，accept函数执行后轮空，数据库无更改
            cmd = GTaskCmd('update',_id=self.model.conn_task_id, conn_company_name=self.model.conn_company_id,
                           source_widget=self.parent.todo_view.tab_bar,fields_values=fields_values)
            self.parent.listener.accept(cmd)

    def on_company_clicked(self):
        self.parent.displayCompanyEditor(client_id=self.model.conn_company_id)

    def on_project_clicked(self):
        self.parent.showProjectPerspective(project_id=self.model.conn_project_id)

    def on_isCritial_slideButton_clicked(self):
        if self.todoWidget.isCritial_slideButton.isChecked():
            self.model.is_critical = True
            self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                   '%s}'%(str(getAlphaColor(GColour.TaskColour.TaskIsCritial,180)),self.Todo_Font_Style))
        else:
            self.model.is_critical = False
            self.todoWidget.textEdit.setStyleSheet(self.style)
        self.model.saveBasicData()
        if self.model.conn_task_id:#如果todo是和task相关联的，则要对相应的task进行处理
            fields_values = {}
            fields_values['_id'] = self.model.conn_task_id
            fields_values['is_critical'] = self.model.is_critical
            fields_values['conn_project_id'] = self.model.conn_project_id
            cmd = GTaskCmd('update',_id=self.model.conn_task_id, conn_company_name=self.model.conn_company_id,
                           source_widget=self.parent.todo_view.tab_bar,fields_values=fields_values)
            self.parent.listener.accept(cmd)

    def on_todoTimeSpaceDistance_triSlideButton_toggled(self, distance):
        self.model.timespace_distance = distance
        self.model.saveBasicData()

    def on_todoStatus_triSlideButton_toggled(self, status):
        # status = self.todoWidget.todoStatus_triSlideButton.checkStatus
        if status == 2:
            ok = self.pushFoward()
        self.model.status = status
        self.model.saveBasicData()

    def on_pending_activated(self):
        self.slider = RedefinedWidget.MySlider(attachedWidget=self.todoWidget.pushButton_4,
                                               attachedView=self,parent=self.todoWidget.groupBox)
        self.slider.setRange(1,35)
        self.todoWidget.pushButton_4.setChecked(True)
        if self.todoWidget.lineEdit.text() == '':
            self.todoWidget.lineEdit.setText(str(0))
        self.slider.valueChanged.connect(self.on_pending_date_changed)
        self.slider.show()
        self.todoWidget.lineEdit.setEnabled(True)
        self.todoWidget.pushButton_5.setEnabled(True)

    def on_pending_deactivated(self):
        '''适用于“取消”按钮的槽函数, 以及手动将延期天数设置为0的情况的处理'''
        ok = QMessageBox.question(self.todoWidget, '取消延期', '确定取消延期？',
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ok == QMessageBox.No:
            return
        self.todoWidget.pushButton_4.setChecked(False)
        self.model.on_pending = False
        self.todoWidget.lineEdit.setText('')
        self.todoWidget.lineEdit.setEnabled(False)
        self.todoWidget.label.setText('')
        self.todoWidget.pushButton_5.setEnabled(False)
        self.model.pending_till_date = None
        self.model.saveBasicData()

    def on_pending_date_changed(self):
        pending_days = round(1.15**self.slider.value())
        self.todoWidget.lineEdit.setText(str(pending_days))
        today = datetime.datetime.today().date()
        #datetime日期加一个数字，得到的结果是日期直接加这个数字的值，与两个日期相减的逆运算是对称的
        pending_till_date = today + datetime.timedelta(days=(pending_days))
        self.todoWidget.label.setText(str(pending_till_date))

    def direct_set_pending_date(self, days):
        self.model.on_pending = True
        today = datetime.datetime.today().date()
        pending_till_date = today + datetime.timedelta(days=(days))
        self.todoWidget.lineEdit.setText(str(days))
        self.todoWidget.label.setText(str(pending_till_date))
        self.todoWidget.pushButton_4.setChecked(True)
        self.todoWidget.pushButton_5.setEnabled(True)
        self.model.pending_till_date = str(pending_till_date)
        self.model.saveBasicData()

    def on_slider_close(self):
        if not self.todoWidget.lineEdit.text():# 未输入数字的时候，出现editingFinished信号，直接忽略
            return
        if self.todoWidget.lineEdit.hasFocus():# 如果焦点是从slider直接跳转到了lineEdit，即说明输入尚未完成
            return
        self.model.on_pending = True
        pending_days = int(self.todoWidget.lineEdit.text())
        if pending_days == 0:
            self.todoWidget.lineEdit.setEnabled(False)
            self.todoWidget.lineEdit.setText('')
            self.todoWidget.label.setText('')
            self.todoWidget.pushButton_5.setEnabled(False)
            self.todoWidget.pushButton_4.setChecked(False)
            self.model.on_pending = False
            self.model.pending_till_date = None
            self.model.saveBasicData()
            return
        today = datetime.datetime.today().date()
        pending_till_date = today + datetime.timedelta(days=(pending_days))
        self.todoWidget.label.setText(str(pending_till_date))
        self.model.pending_till_date = str(pending_till_date)
        self.model.saveBasicData()

    def on_delete_clicked(self):
        ok = QMessageBox.question(self.todoWidget, '删除','删除此任务？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.No :
            return
        # self.todoWidget.pushButton_4.setChecked(False)
        self.model.destroyed = True
        self.model.saveBasicData()
        self.parent_view.on_delete_todo(self.model._id)

    def pushFoward(self):
        ok  = QMessageBox.question(self.parent,'下推', '完成当前任务\n是否创建并下推到新任务？',
                                   QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.Yes:
            ok = self.parent_view.push_todo_unit_forward(self.model._id)
            return ok
        else:
            return False

    def showRightMenu(self,text = None,text_pad = None):
        text = text_pad.textCursor().selectedText()
        menu = QtWidgets.QMenu(parent=self.parent)
        if text_pad:
            allText = text_pad.toPlainText()
            copyAction = menu.addAction('复制')
            copyAction.triggered.connect(lambda :QtWidgets.QApplication.clipboard().setText(text))
            if not text:
                copyAction.setEnabled(False)
            copyAllAction = menu.addAction('复制全部')
            copyAllAction.triggered.connect(lambda : QtWidgets.QApplication.clipboard().setText(allText))
            if not allText:
                copyAllAction.setEnabled(False)
            pasteAction = menu.addAction('粘贴')
            clipboard_text = QtWidgets.QApplication.clipboard().text()
            pasteAction.triggered.connect(lambda :text_pad.textCursor().insertText(clipboard_text))
            pasteAction.triggered.connect(lambda :text_pad.setEdited())
            if text_pad.isReadOnly() or not clipboard_text:
                pasteAction.setEnabled(False)
        menu.popup(QtGui.QCursor.pos())

    def showTodoMenu(self):
        day = datetime.datetime.now().weekday()
        menu = QtWidgets.QMenu(parent=self.parent)
        one_day_delay = menu.addAction('延后1天')
        three_day_delay = menu.addAction('延后3天')
        next_week_delay = menu.addAction('延至下周')
        seven_day_delay = menu.addAction('延后7天')
        fifteen_day_delay = menu.addAction('延后15天')
        thirty_day_delay = menu.addAction('延后30天')
        one_day_delay.triggered.connect(lambda :self.direct_set_pending_date(1))
        three_day_delay.triggered.connect(lambda :self.direct_set_pending_date(3))
        next_week_delay.triggered.connect(lambda :self.direct_set_pending_date(7-day))
        fifteen_day_delay.triggered.connect(lambda :self.direct_set_pending_date(15))
        seven_day_delay.triggered.connect(lambda :self.direct_set_pending_date(7))
        thirty_day_delay.triggered.connect(lambda :self.direct_set_pending_date(30))
        #绑定聚合信号
        unite_menu = menu.addMenu('聚合')
        unite_task = unite_menu.addAction('同类任务')
        if self.model.officejob_type:
            unite_task.triggered.connect(lambda :self.parent_view.uniteByTodoType(self.model.officejob_type))
        elif self.model.conn_task_id:
            unite_task.triggered.connect(lambda :self.parent_view.uniteByTodoType(self.model.conn_task_cat))
        menu.popup(QtGui.QCursor.pos())
        for X in office_job_dict.keys():
            unite_task_X = unite_menu.addAction(office_job_dict[X])
            unite_task_X.triggered.connect(partial(self.parent_view.uniteByTodoType,X))
        #设置任务分类
        type_set_menu = menu.addMenu('修改类型')
        for T in office_job_dict.keys():
            type_set_X = type_set_menu.addAction(office_job_dict[T])
            type_set_X.triggered.connect(partial(self.setOfficejobType, T))

def bools2binary(bl_0):
    '''convert a sequence of booleans to a binary representation'''
    assert len(bl_0) > 0, 'The sequence bl_0 should not be empty'
    bl_0 = map(str, map(int, bl_0))
    b0 = int(''.join(bl_0), 2)
    return b0
    # for i in range(len(tp_0)):
    #     if tp_0[i] and tp_1[i]:
    #       return True
    # else:
    #     return False


class ToDoView(View):
    ARRANGE_WEIGHT = 0
    ARRANGE_COMPANY = 1
    ARRANGE_PROJECT = 2
    ARRANGE_OFFI_TYPE = 0
    COMPANY_KEY_ALIAS_FIELD = ('conn_company_id', 'conn_company_name')
    JOBTYPE_KEY_ALIAS_FIELD = ('officejob_type', None)
    PROJECT_KEY_ALIAS_FIELD = ('conn_project_name', 'conn_project_name')


    def __init__(self,parent=None, parent_widget = None):
        super(ToDoView, self).__init__()
        self.parent = parent
        self.parent_widget = parent_widget
        self.units = []
        self.units_for_render = [] ## units_for_render来自于units的浅拷贝，并对元素进行重组值。
        self.todo_id_map = {} # todo_id_map记录的是ToDoUnit在tableWidget中的坐标，相当于是对于其在todo_view_matrix中的坐标进行了转置
        self.todo_view_matrix = None
        self.todo_view_header_array = []
        self.arrange_strategy = self.ARRANGE_WEIGHT
        self.drag_drop_enabled = True
        self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]
        self.accept_state = AccceptState()
        self.bound_widget = None
        self.bound_widget_header = None
        self.tab_bar = TodoViewTabBar(parent=parent_widget)
        # self.tab_bar.setStyleSheet('QTextEdit {'
        #                            'border-width: 1px;'
        #                            'border-style: dashed;'
        #                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                            'stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
        self.tab_bar.checkStatusChanged.connect(self.on_check_status_changed)
        self.tab_bar.pushButton.clicked.connect(self.on_add_new_todo)

        self.check_status = self.tab_bar.getCheckStatus()
        self.tab_bar.comboBox_order.currentIndexChanged.connect(self.on_comboBox_order)

    def updateControl(func):
        '''Stop updating widgets while making big changes to them'''
        def wrapper(*args, **kwargs):
            self = args[0]
            self.bound_widget.setUpdatesEnabled(False)
            ret = func(*args, **kwargs)
            self.bound_widget.setUpdatesEnabled(True)
            return ret
        return wrapper

    def initAllData(self):
        pass

    def setDataModel(self, condition: dict=None):
        self.units.clear() # self.units就是最后准备渲染的全部单元
        self.units_for_render.clear()
        self.units_for_render = self.units
        get_pending = self.check_status[0][0] # to_do.pending_date - today
        timespace_distance_wanted = self.check_status[4]
        mask = self.check_status[3]
        mask_b = bools2binary(mask) # 将系列bool值转换成二进制掩码，用于筛选comboBox所选的类型 # project
        condition = self.handleSearchCondition(condition)
        todo_fields = ['_id', 'conn_task_id', 'todo_desc', 'status','on_pending', 'pending_till_date', 'is_critical',
                       'conclusion_desc', 'waiting_desc', 'create_time', 'destroyed', 'inter_order_weight',
                       'conn_project_id', 'conn_company_id', 'officejob_type']
        project_fields = ['product', 'client', 'client_id', 'order_tobe', 'weight', 'in_act', 'clear_chance',
                          'highlight']
        company_fields = ['short_name']
        task_fields = ['officejob_type']
        todo_logs = CS.getLinesFromTable('todo_log', conditions=condition, order=['inter_order_weight'])
        combined_todo_logs = CS.triple_innerJoin_withList_getLines(
            'todo_log', 'proj_list', 'clients',
            target_colums_a=todo_fields, target_colunms_b=project_fields, target_colunms_c=company_fields,
            joint_key_a_b=('conn_project_id', '_id'), joint_key_a_c=('conn_company_id', '_id'),
            condition_a=condition, method='left join')
        keys = todo_logs.pop()

        # load extra information about todo_units
        index_todo_id = keys.index('_id')
        index_project_id = keys.index('conn_project_id')
        index_company_id = keys.index('conn_company_id')
        index_task_id = keys.index('conn_task_id')
        dict_todo_project = {}
        dict_todo_company = {}
        dict_todo_task = {}

        for log in todo_logs:
            if conn_project_id := log[index_project_id] :
                dict_todo_project[log[index_todo_id]] = conn_project_id
            if conn_company_id := log[index_company_id]:
                dict_todo_company[log[index_todo_id]] = conn_company_id
            if conn_task_id := log[index_task_id] :
                dict_todo_task[log[index_todo_id]] = conn_task_id

        project_ids = list(dict_todo_project.values())
        company_ids = list(dict_todo_company.values())
        task_ids = list(dict_todo_task.values())

        project_fields = ['_id','product', 'client', 'client_id', 'order_tobe', 'weight', 'in_act','is_deal', 'clear_chance', 'highlight']
        project_logs  = CS.getLinesFromTable('proj_list', conditions = {'_id': project_ids}, columns_required= project_fields)
        project_dict = {}
        for project_log in project_logs:
            project_dict[project_log[0]] = project_log

        company_fields = ['_id', 'short_name']
        company_logs = CS.getLinesFromTable('clients', conditions = {'_id': company_ids}, columns_required=company_fields)
        company_dict = {}
        for company_log in company_logs:
            company_dict[company_log[0]] = company_log

        task_fields = ['_id', 'officejob_type']
        task_logs = CS.getLinesFromTable('tasks', {'_id': task_ids}, columns_required=task_fields)
        task_dict = {}
        for task_log in task_logs:
            task_dict[task_log[0]] = task_log

        # indexes = range(len(keys))
        # 根据get_pending 和延期到的日期来确定要保留的任务
        j = 0
        before_create_units = time.perf_counter()
        for i, log in enumerate(todo_logs):
            todo_id = log[index_todo_id]
            pending_till_date = log[keys.index('pending_till_date')]
            if get_pending == 0:# 获取到期的任务
                if not pending_till_date:# 不存在延期，保留
                    pass
                else:
                    pending_days = (datetime.datetime.strptime(str(pending_till_date), '%Y-%m-%d').date()\
                                - datetime.datetime.today().date()).days
                    if pending_days > 0: # 还未到期，跳过
                        continue
                    else:# 已到期，保留
                        pass
            elif get_pending == 1:# 获取未到期的任务
                if not pending_till_date:# 不存在延期
                    continue
                else:
                    pending_days = (datetime.datetime.strptime(str(pending_till_date), '%Y-%m-%d').date()\
                                - datetime.datetime.today().date()).days
                    if pending_days > 0: # 还未到期
                        pass
                    else:# # 已到期，跳过
                        continue
            elif get_pending == 2:# 获取全部任务
                pass
            before_create_unit = time.perf_counter()
            todo_unit = TodoUnitView(parent=self.parent, parent_view=self)
            todo_unit.model.assign_data(keys=keys, values=log)

            if todo_id in dict_todo_project.keys():
                conn_project_id = dict_todo_project[todo_id]
                project_log = project_dict[conn_project_id]
                project = dict(zip(project_fields, project_log))
                todo_unit.model.conn_project_name = project['product']
                todo_unit.model.conn_company_name = project['client']
                todo_unit.model.conn_company_id = project['client_id']
                todo_unit.model.conn_project_order_tobe = project['order_tobe']
                todo_unit.model.conn_project_weight = project['weight']
                todo_unit.model.conn_project_in_act = project['in_act']
                todo_unit.model.conn_project_clear_chance = project['clear_chance']
                todo_unit.model.conn_project_highlight = project['highlight']
                todo_unit.model.conn_project_is_deal = project['is_deal']

            if todo_id in dict_todo_company and todo_unit.model.conn_company_name is None:
                conn_company_id = dict_todo_company[todo_id]
                company_log = company_dict[conn_company_id]
                todo_unit.model.conn_company_name = company_log[1]

            if todo_id in dict_todo_task.keys():
                conn_task_id = dict_todo_task[todo_id]
                task_log = task_dict.get(conn_task_id, None)
                if task_log is not None:
                    todo_unit.model.conn_task_cat = task_log[1]

            if todo_unit.model.timespace_distance not in timespace_distance_wanted:
                continue

            if not mask:
                pass
            elif mask and reduce(mul, mask) == 1:
                pass
            else:
                maskee = (todo_unit.model.conn_project_is_deal,
                          todo_unit.model.conn_project_order_tobe,
                          todo_unit.model.conn_project_clear_chance,
                          todo_unit.model.conn_project_highlight,
                          todo_unit.model.conn_project_in_act,
                          not (todo_unit.model.conn_project_is_deal or
                               todo_unit.model.conn_project_order_tobe or
                               todo_unit.model.conn_project_clear_chance or
                               todo_unit.model.conn_project_highlight or
                               todo_unit.model.conn_project_in_act or
                               not bool(todo_unit.model.conn_project_id)),
                          not bool(todo_unit.model.conn_project_id))
                maskee = bools2binary(maskee)
                # global_logger.debug('maskee:{}'.format(maskee))
                # global_logger.debug('mask:{}'.format(mask))
                if not mask_b & maskee: # if only one positional condition matches
                    continue
            j += 1
            before_todo_unitWidget = time.perf_counter()
            todo_unit.setWidget()
            after_todo_unitWidget = time.perf_counter()
            # print('time_for_render_todowidget:', after_todo_unitWidget - before_todo_unitWidget)
            self.units.append(todo_unit)
        after_create_units = time.perf_counter()
        # print('time for creating all units:', after_create_units - before_create_units)
        # self.sortUnits()

        # for i, unit in enumerate(self.units):
        #     unit.model.inter_order_weight = i + 1 # 每次读取出来的todo_unit, 都赋予新的inter_order_weight

    def setUnitsForRender(self):
        if self.units_for_render == self.units:
            return

    def on_comboBox_order(self, index):
        self.arrange_strategy = index
        self.setDragDropEnabled(False)
        if self.arrange_strategy == self.ARRANGE_COMPANY:
            self.leveled_key_alias_fields = [self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD]
        elif self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]
            self.setDragDropEnabled()
        else:
            self.leveled_key_alias_fields = [self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD]
        if not self.units:
            return
        self.renderWidget()

    @staticmethod
    def setTableCellWidget(tablewidget:QtWidgets.QTableWidget, row, column, widget:QWidget):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        layout = frame.layout()
        item = layout.itemAt(0)
        if item is not None:
            _widget = item.widget()
            layout.removeItem(item)
            _widget.setParent(None)
        layout.addWidget(widget)

        # print('time_for_set_todowidget:', after_setCellWidget - before_setCellWidget)

    @staticmethod
    def tableCellWidget(tablewidget:QtWidgets.QTableWidget, row, column):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        return frame.findChildren(RedefinedWidget.ToDoUnitWidget)[0]

    @staticmethod
    def paintEvent(device, e):
        width = device.width()
        # m_nPTargetPixmap = QPixmap(1,1)
        painter = QPainter(device)
        pen = QPen(Qt.white)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.begin(device)
        painter.drawLine(1, 1, width, 1)
        painter.end()
        # time_before_update = time.perf_counter()
        QFrame.paintEvent(device, e)
        # time_after_update = time.perf_counter()
        # print('time_for_update = ', time_after_update - time_before_update)

    @staticmethod
    def setTableCellAppearance(tablewidget:QtWidgets.QTableWidget, row, column, color, is_switching:bool):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        frame.setStyleSheet('#outer_frame{background-color: rgba(%s,%s,%s, 200)}' % color)
        if is_switching:
            frame.layout().setContentsMargins(4, 3, 4, 1)
        # line = QtWidgets.QGraphicsLineItem()
            frame.paintEvent = types.MethodType(ToDoView.paintEvent, frame)

        # line.setLine(0,0,0,width)
        # frame.layout().insertWidget(0,line)


        # frame.setBackgroundRole(color)

    def sortUnits(self):
        self.units.sort(key= lambda unit: unit.model.conn_project_weight + unit.model.is_critical * 5 if \
                unit.model.conn_project_weight else unit.model.is_critical * 5, reverse=True)
        if self.units_for_render == self.units:
            return
        self.units_for_render.sort(key= lambda unit: unit.model.conn_project_weight + unit.model.is_critical * 5 if \
                unit.model.conn_project_weight else unit.model.is_critical * 5, reverse=True)

    def arrangeUnitsIntoLanes(self)->dict:
        '''
        todo卡片的组织策略，具有默认排序策略和指定排序策略这两级
        默认排序策略是基础，指定排序策略则将其中某项策略的优先级提高。
        在不同列间，存在列长度相差过大的情况，可适当进行合并，使得显示结果尽可能接近矩形。
        0: 权重优先
        1：客户优先
        2：项目优先
        3: 类型优先
        4: 主线支线--需明确主线和支线的定义
        '''
        # self.arrange_strategy = self.tab_bar.comboBox_order.currentIndex()

        self.sortUnits() # 使用weight做整体初步排序

        cat_map = self.classify(self.units_for_render, self.leveled_key_alias_fields)

        return cat_map

    @classmethod
    def classify(cls, source_model_list:list[TodoUnitView], leveled_key_fields:list[tuple])->dict:
        '''按照key_field对todo unit的列表分类，以key_field的值为键值的map形式返回'''
        cat_map = {}
        n_model = 0
        for i, unit in enumerate(source_model_list):
            n_model += 1
            key_name = getattr(unit.model, leveled_key_fields[0][0])
            if key_name:
                if key_name in cat_map:
                    cat_map[key_name].append(unit)
                else:
                    cat_map[key_name] = [unit]
            else:
                if '__' in cat_map:
                    cat_map['__'].append(unit)
                else:
                    cat_map['__'] = [unit]

        if len(leveled_key_fields) > 1:
            next_leveled_key_fields = leveled_key_fields[1:]
            for key, model_list in cat_map.items():
                value = cls.classify(model_list, next_leveled_key_fields)
                cat_map.update({key:value})

        cat_map['n_model'] = n_model
        return cat_map

    def handleSearchCondition(self, condition:dict):
        if not condition:
            project_ids = []
        else:
            project_id_get = CS.getLinesFromTable('proj_list',conditions=condition,columns_required=['_id'])
            project_id_get.pop()
            project_ids = [item[0] for item in project_id_get]
        condition = {}
        if project_ids:
            condition['conn_project_id'] = project_ids
        get_pending = self.check_status[0][0]#to_do.pending_date-today
        get_destroyed = self.check_status[0][1]#to_do类属性
        get_progress = self.check_status[1]
        get_critical = self.check_status[2][0]#to_do类属性
        get_normal = self.check_status[2][1]#to_do类属性
        # mask = self.check_status[2]#掩码用于筛选comboBox所选的类型#project
        #对is_critical的筛选
        if get_critical ^ get_normal:
            if get_critical:
                condition['is_critical'] = True
            else:
                condition['is_critical'] = False
        #对destroyed删选
        if get_destroyed:
            condition['destroyed'] = True
        else:
            condition['destroyed'] = False
        # 对status筛选
        progress_checked = []
        for i, bo in enumerate(get_progress):#status包括0,1,2三种状态分别代表未进行，进行中，已完成
            if bo:
                progress_checked.append(i)
        if len(progress_checked) == 0 or len(progress_checked) == 3:
            pass
        else:
            condition['status'] = progress_checked
        return condition

    def setBoundWidget(self, content_table_widget, header_table_widget = None):

        super(ToDoView, self).setBoundWidget(content_table_widget)
        self.bound_widget_header = header_table_widget

    def setDragDropEnabled(self, d0 = True):
        self.drag_drop_enabled = d0

    def setupUi(self):
        tab_header = '追踪模式'
        self.parent_widget.addTab(self.tab_bar, tab_header)
        self.setBoundWidget(self.tab_bar.tableWidget, self.tab_bar.tableWidget_header)
        # self.bound_widget.setAcceptDrops(True)
        self.bound_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget.dragEnterEvent = types.MethodType(new_dragEnterEvent, self.bound_widget)
        self.bound_widget.cellWidget = types.MethodType(self.tableCellWidget, self.bound_widget)
        self.bound_widget.setCellWidget = types.MethodType(self.setTableCellWidget, self.bound_widget)
        self.bound_widget.setTableCellAppearance = types.MethodType(self.setTableCellAppearance, self.bound_widget)
        self.bound_widget_header.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget_header.setFixedHeight(30 * FIX_SIZE_WIDGET_SCALING)

    def resetUnitWidgets(self, start:int = 0, stop:int = None):
        if not stop:
            stop = len(self.units_for_render)
        else:
            stop += 1
        for i in range(start, stop):
            self.units_for_render[i].setWidget()

    # def renderWidget(self):
    #     self.bound_widget.clear()
    #     row_count = len(self.units_for_render) // 5 if len(self.units_for_render) % 5 == 0 else len(
    #         self.units_for_render) // 5 + 1
    #     self.bound_widget.setColumnCount(5)
    #     self.bound_widget.setRowCount(row_count)
    #
    #     # Qt在屏幕上显示的尺寸大小，只和设置的屏幕分辨率有关，会自动消除Windows的scaling所带来的尺寸变化，直接使用的是真实像素
    #     self.bound_widget.horizontalHeader().setDefaultSectionSize(int(300 * DF_Ratio))
    #     self.bound_widget.verticalHeader().setDefaultSectionSize(int(200 * DF_Ratio))
    #     self.bound_widget.horizontalHeader().setVisible(False)
    #     self.bound_widget.verticalHeader().setVisible(False)
    #     # self.bound_widget.setStyleSheet("QTableWidget::item{border-style:dashed; border-width:4px; border-color: PaleGreen ;}")
    #     self.bound_widget.setShowGrid(False)
    #     # 对todo_units进行排序
    #     self.units_for_render.sort(key = lambda unit: unit.model.inter_order_weight)
    #
    #     # 在tableWidget里展示信息
    #     before_todo_view = time.perf_counter()
    #     for i, unit in enumerate(self.units_for_render):
    #         row_index = i // 5
    #         column_index = i % 5
    #         self.bound_widget.setCellWidget(row_index, column_index, unit.todoWidget)
    #         # self.bound_widget.cellWidget(row_index,column_index).renderSelf()
    #     print('time_for_todo_view_widget:', time.perf_counter() - before_todo_view)

    @classmethod
    def extractDict(cls, cat_map:dict):
        '''
        将dict形式的树转变为list形式
        cat_map: 字典形式的树状分类
        '''
        lst = []
        cat_map.pop('n_model', None)
        for key, value in cat_map.items():
            if isinstance(value, dict):
                lst.extend(cls.extractDict(value))
            else:
                lst.extend(value)
        return lst

    def renderMatrixColum(self, column_index: int):
        col_mark = column_index % 2 # 标记是否换行
        key_field_value_old = ''
        sequence_mark = False
        for i, unit in enumerate(self.todo_view_matrix[column_index]):
            # unit.setWidget()
            self.todo_id_map.update({unit.model._id: (i, column_index)})
            before_in = time.perf_counter()
            self.bound_widget.setCellWidget(i, column_index, unit.todoWidget)
            after_set = time.perf_counter()
            # global_logger.debug("time_for_insert_todowidget{}".format(after_set-before_in))
            unit.todoWidget.setUpdatesEnabled(True)
            if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
                secondary_key_field = self.leveled_key_alias_fields[1][0]
            else:
                secondary_key_field = self.leveled_key_alias_fields[0][0]
            key_field_value_new = getattr(unit.model, secondary_key_field)

            if not key_field_value_new == key_field_value_old:
                sequence_mark = not sequence_mark
                switching = True
            else:
                switching = False
            key_field_value_old = key_field_value_new
            if col_mark:
                rgb = ((225 - int(sequence_mark) * 15),
                       (200 + int(sequence_mark) * 20),
                       (195 + int(sequence_mark) * 0))
            else:
                rgb = ((185 + int(sequence_mark) * 0),
                       (200 + int(sequence_mark) * 30),
                       (235 - int(sequence_mark) * 10))
            self.bound_widget.setTableCellAppearance(i, column_index, rgb, is_switching=switching)

    @updateControl
    def reRenderMatrixColumn(self, column_index:int):
        # shape of former table
        former_len_col = self.bound_widget.rowCount()
        former_len_row = self.bound_widget.columnCount()
        # shape of new table
        len_col = len(self.todo_view_matrix[column_index])
        new_len_col = max(former_len_col, len_col)

        if len_col > former_len_col:
            self.bound_widget.setRowCount(len_col)
            for i in range(former_len_col, new_len_col):
                for j in range(former_len_row): # 填充新的空行
                    empty_frame = self.createEmptyFrame(i, j)
                    QtWidgets.QTableWidget.setCellWidget(self.bound_widget, i, j, empty_frame)

        for i in range(new_len_col): # 清空并填充列
            empty_frame = self.createEmptyFrame(i, column_index)
            QtWidgets.QTableWidget.setCellWidget(self.bound_widget, i, column_index, empty_frame)

        self.renderMatrixColum(column_index)

    def initCellWidget(self, row:int, column:int):
        empty_frame = self.createEmptyFrame(row, column)
        QtWidgets.QTableWidget.setCellWidget(self.bound_widget, row, column, empty_frame)

    @updateControl
    def renderTableWidget(self, todo_view_matrix:list[list]):
        row_count = 0
        for col in todo_view_matrix:
            len_col = len(col)
            if len_col > row_count: row_count = len_col
        col_count = len(todo_view_matrix)
        self.bound_widget.clear()
        self.bound_widget.setColumnCount(col_count)
        self.bound_widget.setRowCount(row_count)
        for i in range(row_count):
            for j in range(col_count):
                self.initCellWidget(i, j)
                # self.bound_widget.setCellWidget(i, j, empty_frame)
        # Qt在屏幕上显示的尺寸大小，只和设置的屏幕分辨率有关，会自动消除Windows的scaling所带来的尺寸变化，直接使用的是真实像素
        scale_ratio = FIX_SIZE_WIDGET_SCALING
        self.bound_widget.horizontalHeader().setDefaultSectionSize(int(300 * scale_ratio))
        self.bound_widget.verticalHeader().setDefaultSectionSize(int(170 * scale_ratio))
        self.bound_widget.horizontalHeader().setVisible(False)
        self.bound_widget.verticalHeader().setVisible(False)
        self.bound_widget.horizontalScrollBar().valueChanged.connect(self.set_bound_widget_header_scroll_value)
        self.bound_widget.setShowGrid(False)
        self.bound_widget.setStyleSheet("QTableView::item {padding-left: 2px;  padding-bottom: 0px;"
                                        "padding-right: 2px;border: none;}")

        # 在tableWidget里展示信息
        before_todo_insert = time.perf_counter()
        self.todo_id_map.clear() # todo_id_map记录的是ToDoUnit在tableWidget中的坐标，相当于是对于其在todo_view_matrix中的坐标进行了转置
        # self.bound_widget.setUpdatesEnabled(False)
        for i, col in enumerate(todo_view_matrix):
            self.renderMatrixColum(i)
        after_insert= time.perf_counter()
        # self.bound_widget.setUpdatesEnabled(True)
        print('time for all insert:', after_insert-before_todo_insert)

    def set_bound_widget_header_scroll_value(self, value=None):
        self.bound_widget_header.horizontalScrollBar().setValue(value)

    def renderTableWidget_header(self, header_items:list[list[str]]):
        # if self.arrange_strategy == self.ARRANGE_COMPANY:
        #     self.bound_widget_header.hide()
        self.bound_widget_header.clear()
        self.bound_widget_header.setRowCount(1)
        self.bound_widget_header.setColumnCount(len(header_items))
        scale_ratio = FIX_SIZE_WIDGET_SCALING
        self.bound_widget_header.horizontalHeader().setDefaultSectionSize(int(300 * scale_ratio))
        self.bound_widget_header.horizontalHeader().setVisible(False)
        self.bound_widget_header.verticalHeader().setVisible(False)
        # self.bound_widget_header.horizontalScrollBar().setVisible(False)
        # self.bound_widget_header.verticalScrollBar().setVisible(False)
        self.bound_widget_header.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bound_widget_header.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.bound_widget.setStyleSheet("QTableWidget::item{border-style:dashed; border-width:4px; border-color: PaleGreen ;}")
        self.bound_widget_header.setShowGrid(False)
        if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            header_items = [office_job_dict.get(header[0], '未分组') for header in header_items]
            # self.bound_widget_header.setFixedHeight(30 * FIX_SIZE_WIDGET_SCALING)
        elif self.arrange_strategy == self.ARRANGE_COMPANY or self.arrange_strategy == self.ARRANGE_PROJECT:
            # self.bound_widget_header.verticalHeader().setDefaultSectionSize(int(50 * scale_ratio))
            header_items = [' | '.join(header) for header in header_items]
        else:
            return
        max_header_text_height = 0
        for i, header in enumerate(header_items):
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            font = QFont()
            font.setBold(True)
            font.setFamily("微软雅黑")
            font.setPointSize(int(9 * min(FIX_SIZE_WIDGET_SCALING, DF_Ratio)))
            self.bound_widget_header.setCellWidget(0, i, text_edit)
            text_edit.setText(header)
            text_edit.setFont(font)
            text_edit.setAlignment(Qt.AlignCenter)
            # text_edit.document().adjustSize()
            # height = text_edit.verticalScrollBar().maximum() - text_edit.verticalScrollBar().minimum() + text_edit.verticalScrollBar().pageStep()
            text_edit.document().setDocumentMargin(0)
            height = text_edit.document().size().height()
            width = text_edit.document().size().width()
            layout_width = text_edit.document().documentLayout().documentSize().width()
            layout_height = text_edit.document().documentLayout().documentSize().height()
            text_width = text_edit.document().textWidth()
            ideal_width = text_edit.document().idealWidth()

            # text_edit.document().setTextWidth(width)
            # height = text_edit.document().size().height()
            page_width = text_edit.document().pageSize().width()
            page_height = text_edit.document().pageSize().height()
            block_count = text_edit.document().blockCount()
            line_count = text_edit.document().lineCount()
            text_edit.document().useDesignMetrics()
            height = text_edit.document().size().height()
            width = text_edit.document().size().width()
            layout_width = text_edit.document().documentLayout().documentSize().width()
            layout_height = text_edit.document().documentLayout().documentSize().height()
            text_width = text_edit.document().textWidth()
            ideal_width = text_edit.document().idealWidth()
            # text_edit.document().setTextWidth(width)
            # height = text_edit.document().size().height()
            page_width = text_edit.document().pageSize().width()
            page_height = text_edit.document().pageSize().height()

            # print(height)
            max_header_text_height = max(max_header_text_height, height)
            n = 0
        self.bound_widget_header.setFixedHeight(int(max_header_text_height + 1))
        self.bound_widget_header.verticalHeader().setDefaultSectionSize(int(max_header_text_height + 2))

    def makeTodoViewMatrix(self) ->(list[list],list[str]):
        '''
        :return: (headers of columns, colums)
        '''
        cat_map = self.arrangeUnitsIntoLanes()
        cat_map.pop('n_model', None)
        header_cols = list(cat_map.items())
        if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            header_cols.sort(key=lambda item: item[0])
            todo_view_matrix = [self.extractDict(header_col[1]) for header_col in header_cols]
            todo_view_headers = [[header_col[0]] for header_col in header_cols]
        else:
            header_cols.sort(key=lambda item: item[1]['n_model'])
            n_cat = len(header_cols)
            max_len_col = header_cols[-1][1]['n_model']
            nest_threshold_n_col = 5
            allowed_min_len_col = 5
            max_len_col = max(max_len_col, allowed_min_len_col) #todo: para to be extracted
            # 构造todo_view布局
            todo_view_headers = []

            if n_cat <= nest_threshold_n_col:
                todo_view_matrix = [self.extractDict(header_col[1]) for header_col in header_cols]
                todo_view_headers = []
                for i, col_list in enumerate(todo_view_matrix):
                    header = header_cols[i][0]
                    if self.leveled_key_alias_fields[0][1]:
                        header_alias = getattr(col_list[0].model, self.leveled_key_alias_fields[0][1])
                    else:
                        header_alias = header
                    todo_view_headers.append([header_alias])
            else:
                todo_view_matrix = [[]]
                todo_view_headers = [[]]
                len_counter = 0
                for header_col in header_cols:
                    col = header_col[1]
                    header = header_col[0]
                    len_col = col.pop('n_model')
                    if len_counter + len_col >= max_len_col or len_col >= max_len_col / 2:
                        todo_view_matrix.append([])
                        todo_view_headers.append([])
                        len_counter = 0
                    else:
                        # if not len(todo_view_matrix[0]) == 0:
                        #     todo_view_matrix[-1].append(None)
                        # len_counter += 1
                        pass

                    col_list = self.extractDict(col)
                    todo_view_matrix[-1].extend(col_list)
                    header_alias = getattr(col_list[0].model, self.leveled_key_alias_fields[0][1]) if \
                        self.leveled_key_alias_fields[0][1] else header
                    header_alias = header_alias if header_alias is not None else '__'
                    todo_view_headers[-1].append(header_alias)
                    len_counter += len_col
            todo_view_matrix.reverse()
            todo_view_headers.reverse()
        self.todo_view_matrix = todo_view_matrix
        return todo_view_matrix, todo_view_headers

    def renderWidget(self):
        # 对todo_units进行分类整理
        self.resetUnitWidgets()
        if not self.units_for_render:
            QMessageBox.about(self.parent, "未找到", "未找到符合的待办事项")
            return
        self.todo_view_header_array.clear()
        todo_view_matrix, self.todo_view_header_array = self.makeTodoViewMatrix()
        self.renderTableWidget(todo_view_matrix)
        self.renderTableWidget_header(self.todo_view_header_array)

    def uniteByTodoType(self, type:str):
        """根据待办事项的类型进行选择"""
        tmp_units = self.units.copy()
        for i in reversed(range(len(tmp_units))):
            if tmp_units[i].model.officejob_type:
                if tmp_units[i].model.officejob_type != type:
                    tmp_units.pop(i)
                else:
                    tmp_units[i].setWidget()
            elif tmp_units[i].model.conn_task_id:
                if tmp_units[i].model.conn_task_cat != type:
                    tmp_units.pop(i)
                else:
                    tmp_units[i].setWidget()
            else:
                tmp_units.pop(i)
        self.units_for_render = tmp_units
        if not self.units_for_render:
            return
        self.resetWeight()
        self.renderWidget()

    def removeWidgets(self, _id:Union[list[str],str]):
        if isinstance(_id,str):
            ids = [_id]
        else:
            ids = _id
        for id in ids:
            row_index, column_index = self.todo_id_map[id]
            # self.bound_widget.removeCellWidget(row_index, column_index) # todo:rewrite
            # item = self.createEmptyFrame(row_index, column_index)
            self.initCellWidget(row_index, column_index)

    def createEmptyFrame(self, row_index:int, column_index:int):
        frame = RedefinedWidget.EmptyDropFrame(self)
        frame.coord = (row_index, column_index)
        if self.drag_drop_enabled == False:
            frame.setAcceptDrops(False)
        return frame

    def setCellUnitWidget(self, row, col, todo_unit_view):
        todo_unit_view.setWidget()
        self.todo_view_matrix[col][row] = todo_unit_view
        self.bound_widget.setCellWidget(row, col, todo_unit_view.todoWidget)

    def reRenderWidget(self, row_index:int, column_index:int, todo_unit_view):
        '''参数start和stop表示的是闭区间'''
        # row_count = len(self.units_for_render) // 5 if len(self.units_for_render) % 5 == 0 else len(self.units_for_render)//5 +1
        # self.bound_widget.setColumnCount(5)
        # self.bound_widget.setRowCount(row_count)
        # self.bound_widget.horizontalHeader().setDefaultSectionSize(300 * FIX_SIZE_WIDGET_SCALING)
        # self.bound_widget.verticalHeader().setDefaultSectionSize(200 * FIX_SIZE_WIDGET_SCALING)
        self.bound_widget.horizontalHeader().setVisible(False)
        self.bound_widget.verticalHeader().setVisible(False)
        self.bound_widget.setCellWidget(row_index,column_index, todo_unit_view.todoWidget)

    def resetWeight(self, start = 0, stop=None):
        if not stop:
            stop = len(self.units_for_render)
        else:
            stop += 1
        for i in range(start, stop):
            unit = self.units_for_render[i]
            unit.model.inter_order_weight = i+1
            unit.model.saveBasicData()

    def removeUnitsFromCache(self,_id:Union[list[str],str]):
        if isinstance(_id,str):
            ids = [_id]
        else:
            ids = _id

        for i in reversed(range(len(self.units))):
            unit = self.units[i]
            if unit.model._id in ids:
                self.units.pop(i)
                self.todo_id_map.pop(unit.model._id, None)

        if self.units_for_render == self.units:
            return
        for i in reversed(range(len(self.units_for_render))):
            unit = self.units_for_render[i]
            if unit.model._id in ids:
                self.units_for_render.pop(i)

    def replaceUnit(self, todo_id:str, new_todo_unit):

        for i in reversed(range(len(self.units))):
            unit = self.units[i]
            if unit.model._id == todo_id:
                self.units.pop(i)
                self.units.insert(i, new_todo_unit)

        if self.units_for_render is self.units:
            return

        for i in reversed(range(len(self.units_for_render))):
            unit = self.units_for_render[i]
            if unit.model._id == todo_id:
                self.units_for_render.pop(i)
                self.units_for_render.insert(i, new_todo_unit)

    def on_check_status_changed(self, check_status):
        before_load_todo = time.perf_counter()
        self.check_status = check_status
        condition = self.parent.overall_project_search(2) # todo: 不适用基于project的搜索，否则无法加载未关联项目的
        self.setDataModel(condition)
        self.renderWidget()
        after_load_todo = time.perf_counter()
        # print('time for loading todo:', after_load_todo - before_load_todo)

    def on_delete_todo(self, id:str):
        '''
        :param id: id of ToDoUnit
        :return:None
        '''
        self.removeWidgets(id)
        self.removeUnitsFromCache(id)

    def on_add_new_todo(self, parent:QWidget = None, conn_company_id:str = None,
                        conn_project_id:str=None, conn_task_id:str=None):
        if not parent:
            parent = self.parent
        ok = self.add_todo_log(parent,conn_company_id, conn_project_id,conn_task_id)
        if not ok:
            return
        self.setDataModel()
        self.renderWidget()

    def push_todo_unit_forward(self, todo_id:str):
        row, col = self.todo_id_map[todo_id]
        todo_view = self.todo_view_matrix[col][row]
        ok, todo_model = self.add_todo_log(parent= self.parent, conn_company_id = todo_view.model.conn_company_id,
                                             conn_project_id = todo_view.model.conn_project_id)
        if ok:
            new_todo_view = TodoUnitView(parent=self.parent, parent_view=self)
            new_todo_view.model = todo_model
            todo_model.loadConnProjectInfo()
            self.removeWidgets(todo_id)
            self.todo_id_map.pop(todo_id)
            self.todo_id_map[new_todo_view.model._id] = (row, col)
            self.replaceUnit(todo_id, new_todo_view)
            self.setCellUnitWidget(row, col, new_todo_view)
            new_todo_view.todoWidget.setUpdatesEnabled(True)
            return True
        else:
            return False

    def Accept(self, cmd):
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

        global_logger.debug('todo_view accepted')
        target_flag = cmd.flag
        if target_flag  == 1:#project
           return
        elif target_flag == 2:#task
            self.acceptTaskCmd(cmd)
        else:
            return

    # def acceptTaskCmd(self,cmd):
    #     print('Todo accepted task')
    #     # client_name = cmd.conn_company_name
    #     conn_task_id = cmd._id
    #     source_widget = cmd.source_widget
    #     if source_widget is self.tab_bar:
    #         return
    #     # 查找被修改的todo_unit的位置
    #
    #     index_in_units = None
    #     index_in_units_for_render = None
    #     for k, todo_unit in enumerate(self.units) :
    #         if conn_task_id == todo_unit.model.conn_task_id :
    #             index_in_units = k
    #             break
    #     else:
    #         return
    #     for i, todo_unit in enumerate(self.units_for_render):
    #         if conn_task_id == todo_unit.model.conn_task_id:
    #             index_in_units_for_render = i
    #             break
    #     else:
    #         pass
    #
    #     if cmd.operation == 4:  # delete
    #         if not index_in_units_for_render is None:# 如果操作是删除，先单独对units_for_render列表执行pop()
    #             self.units_for_render.pop(index_in_units_for_render)
    #         self.units.pop(index_in_units)
    #         for i, unit in enumerate(self.units):
    #             unit.model.inter_order_weight = i + 1
    #         if self.accept_state.accept_complete:
    #             self.renderWidget()
    #     elif cmd.operation == 1:  # update
    #         todo_unit = self.units[index_in_units]
    #         if 'task_desc' in cmd.fields_values.keys():
    #             todo_unit.model.conn_task_desc = cmd.fields_values['task_desc']
    #             todo_unit.model.todo_desc = cmd.fields_values['task_desc']
    #             todo_unit.model.conclusion_desc = cmd.fields_values['update_desc_list']
    #         if 'is_critical' in cmd.fields_values.keys():
    #             todo_unit.model.is_critical = cmd.fields_values['is_critical']
    #         if 'officejob_type' in cmd.fields_values.keys():
    #             todo_unit.model.officejob_type = cmd.fields_values['officejob_type']
    #
    #         if self.accept_state.accept_complete and not index_in_units_for_render is None:
    #             todo_unit.setWidget()
    #             self.reRenderWidget(index_in_units_for_render, index_in_units_for_render)
    def removeUnitFromTodoviewMatrix(self,coord:tuple):
        unit = self.todo_view_matrix[coord[1]].pop(coord[0])
        # self.todo_view_matrix[coord[1]][coord[0]] = None
        return unit

    def handleTodoUnitDrop(self, source_id: str, target_id: str):
        # find units according to id
        source_unit_coord = self.todo_id_map[source_id]
        target_unit_coord = self.todo_id_map[target_id]
        source_unit = self.todo_view_matrix[source_unit_coord[1]][source_unit_coord[0]]
        target_unit = self.todo_view_matrix[target_unit_coord[1]][target_unit_coord[0]]
        source_col = source_unit_coord[1]
        target_col = target_unit_coord[1]
        target_row = target_unit_coord[0]
        # modify officejob_type
        old_type = source_unit.model.officejob_type
        new_type = target_unit.model.officejob_type
        if old_type == new_type:
            return
        source_unit.setOfficejobType(new_type)
        # relocate unit in todo_view_matrix
        self.removeUnitFromTodoviewMatrix(source_unit_coord)
        self.todo_view_matrix[target_col].insert(target_row, source_unit)
        # rerender
        self.reRenderMatrixColumn(source_col)
        self.reRenderMatrixColumn(target_col)
        pass

    def on_empty_frame_drop(self, source_id:str, frame:RedefinedWidget.EmptyDropFrame):
        source_unit_coord = self.todo_id_map[source_id]
        source_unit = self.todo_view_matrix[source_unit_coord[1]][source_unit_coord[0]]
        source_col = source_unit_coord[1]
        target_col = frame.coord[1]
        target_row = frame.coord[0]
        old_type = source_unit.model.officejob_type
        # new_type = self.todo_view_matrix[target_col][0].model.officejob_type
        new_type =self.todo_view_header_array[target_col][0]
        if old_type == new_type:
            return
        self.removeUnitFromTodoviewMatrix(source_unit_coord)
        source_unit.setOfficejobType(new_type)
        if target_row < len(self.todo_view_matrix[target_col]):
            self.todo_view_matrix[target_col].insert(target_row, source_unit)
        # elif target_row == len(self.todo_view_matrix[target_col]):

        else:
            self.todo_view_matrix[target_col].append(source_unit)
        self.reRenderMatrixColumn(source_col)
        self.reRenderMatrixColumn(target_col)

    def acceptTaskCmd(self,cmd):
        global_logger.debug('Todo accepted task')
        # client_name = cmd.conn_company_name
        conn_task_id = cmd._id
        source_widget = cmd.source_widget
        if source_widget is self.tab_bar:
            return
        # 查找被修改的todo_unit的位置

        index_in_units = None
        index_in_units_for_render = None
        for k, todo_unit in enumerate(self.units) :
            if conn_task_id == todo_unit.model.conn_task_id :
                index_in_units = k
                break
        else:
            return
        for i, todo_unit in enumerate(self.units_for_render):
            if conn_task_id == todo_unit.model.conn_task_id:
                index_in_units_for_render = i
                break
        else:
            pass

        if cmd.operation == 4:  # delete
            if not index_in_units_for_render is None:# 如果操作是删除，先单独对units_for_render列表执行pop()
                self.units_for_render.pop(index_in_units_for_render)
            self.units.pop(index_in_units)
            for i, unit in enumerate(self.units):
                unit.model.inter_order_weight = i + 1
            if self.accept_state.accept_complete:
                self.renderWidget()
        elif cmd.operation == 1:  # update
            todo_unit = self.units[index_in_units]
            if 'task_desc' in cmd.fields_values.keys():
                todo_unit.model.conn_task_desc = cmd.fields_values['task_desc']
                todo_unit.model.todo_desc = cmd.fields_values['task_desc']
                todo_unit.model.conclusion_desc = cmd.fields_values['update_desc_list']
            if 'is_critical' in cmd.fields_values.keys():
                todo_unit.model.is_critical = cmd.fields_values['is_critical']
            if 'officejob_type' in cmd.fields_values.keys():
                todo_unit.model.officejob_type = cmd.fields_values['officejob_type']

            if self.accept_state.accept_complete and not index_in_units_for_render is None:
                todo_unit.setWidget()
                coord = self.todo_id_map[self.units_for_render[index_in_units_for_render].model._id]
                self.reRenderWidget(*coord, todo_unit)

    @staticmethod
    def add_todo_log(parent:QWidget,conn_company_id:str = None, conn_project_id:str=None,conn_task_id:str=None):
        creator = ToDoUnitCreator(company_id=conn_company_id, conn_project_id=conn_project_id,
                                      conn_task_id=conn_task_id,parent_widget=parent)
        ok, todo_model = creator.createWithDialog()
        return ok, todo_model

class ToDoUnitCreator():
    def __init__(self, company_id: str = None, conn_project_id: str = None, conn_task_id: str = None,
                 parent_widget=None,parent_presentor = None):
        self.parent_widget = parent_widget
        self.parent_presenter = parent_presentor
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

    def createWithDialog(self):
        self.dialog = RedefinedWidget.ToDoUnitCreateDialog(parent=self.parent_widget, presenter=self)

        ok = self.dialog.exec()
        if ok :
            return ok, self.model
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

    def broadCastTaskUpdate(self, as_new_task:bool):
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
                source_widget = self.parent_widget.todo_view.tab_bar  # 来源仅仅是追踪模式的tab_bar
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
            source_widget = self.parent_widget.todo_view.tab_bar  # 来源仅仅是追踪模式的tab_bar
            cmd = DataCenter.GTaskCmd('insert', _id=task_fields_values['_id'], fields_values=task_fields_values,
                                      source_widget=source_widget,
                                      conn_company_name=self.model.conn_company_id)
        self.parent_widget.listener.accept(cmd)

    def setModelFieldsValues(self, fields_values:dict):
        '''

        :param json_fields_values: a python dict
        :return:
        '''
        for field, value in fields_values.items():
            setattr(self.model, field, value)

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

        find_companies1 = CS.multiConditionsGetLinesFromSqlite('clients', condition_keys=condition_keys,condition_values=condition_values,columns_required=['_id'])
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
