import json

from PyQt5.QtGui import QFontMetrics

import DataCenter
from TodoViewTabBarUi import Ui_Form
from RedefinedWidget import CheckableComboBox
from PyQt5.QtWidgets import QTabBar
from PyQt5 import QtGui,QtWidgets,QtCore,Qt
from PyQt5.QtCore import pyqtSignal
import GColour, types , DataView


def styleColour(colour:tuple) :
    return "background:rgb%s"%str(colour)

class TodoViewTabBar(QTabBar,Ui_Form):
    checkStatusChanged = pyqtSignal(tuple)
    def __init__(self, parent = None):
        super(TodoViewTabBar,self).__init__(parent)
        self.setupUi(self)

        self.parent = parent
        todo_category = ['合作执行', '预期订单', '明确机会','高亮关注', '上线跟进', '普通项目', '独立任务']
        timespace_category = ['近时','中期', '远期']
        arrange_strategies = DataCenter.todo_arrange_strategies
        #替换下拉菜单
        from DataView import DF_Ratio, FIX_SIZE_WIDGET_SCALING
        self.comboBox = CheckableComboBox(parent=self, item_list=todo_category)
        self.comboBox.setMinimumSize(90 * DataView.FIX_SIZE_WIDGET_SCALING, 24* DataView.FIX_SIZE_WIDGET_SCALING)
        self.comboBox.setStyleSheet('font-size:11px')
        self.horizontalLayout_2.replaceWidget(self.comboBox_cata, self.comboBox)
        self.comboBox_cata.deleteLater()
        self.comboBox_order.setMinimumSize(QtCore.QSize(90* DataView.FIX_SIZE_WIDGET_SCALING, 24* DataView.FIX_SIZE_WIDGET_SCALING))
        self.comboBox_order.setStyleSheet('font-size:11px')
        self.comboBox_order.addItems(arrange_strategies)

        self.comboBox_timespace_ = CheckableComboBox(parent=self, item_list=timespace_category)
        self.comboBox_timespace_.setMinimumSize(90 * DataView.FIX_SIZE_WIDGET_SCALING, 24 * DataView.FIX_SIZE_WIDGET_SCALING)
        self.comboBox_timespace_.setStyleSheet('font-size:11px')
        self.horizontalLayout_2.replaceWidget(self.comboBox_timespace, self.comboBox_timespace_)
        self.comboBox_timespace.deleteLater()

        # self.setAcceptDrops(True)
        self.setUpColourLable()
        self.comboBox.checkStatusChanged.connect(self.on_comboBox_change)
        self.comboBox_timespace_.checkStatusChanged.connect(self.on_timespace_chance)
        self.radioButton.clicked.connect(self.on_mission_range_change)
        self.radioButton_2.clicked.connect(self.on_mission_range_change)
        self.radioButton_3.clicked.connect(self.on_mission_range_change)
        # self.radioButton_2.toggled.connect(self.on_mission_range_change)
        self.checkBox_3.clicked.connect(self.on_mission_range_change)
        self.checkBox.clicked.connect(self.on_urgence_range_change)
        self.checkBox_2.clicked.connect(self.on_urgence_range_change)
        self.checkBox_4.clicked.connect(self.on_progress_check_status)
        self.checkBox_5.clicked.connect(self.on_progress_check_status)
        self.checkBox_6.clicked.connect(self.on_progress_check_status)

        #selection status
        self.mission_range = self.get_mission_range()
        self.urgence_range = self.get_urgence_range()
        self.progress_check_status = self.get_progess_check_status()
        self.comboBox_check_status  = self.comboBox.getCheckStatus()
        self.timespace_distance_checked = self.comboBox_timespace_.getCheckIndex()
        self.check_status = (self.mission_range, self.progress_check_status, self.urgence_range, self.comboBox_check_status,
                             self.timespace_distance_checked)
        #禁用tableWigdet自身的鼠标事件
        self.tableWidget.mouseDoubleClickEvent = types.MethodType(self.tbw_mouseClickEvent, self.tableWidget)
        self.tableWidget.mousePressEvent = types.MethodType(self.tbw_mouseClickEvent, self.tableWidget)
        self.tableWidget.mouseMoveEvent = types.MethodType(lambda obj,e :e.ignore(),self.tableWidget)
        self.tableWidget.enterEvent = types.MethodType(lambda obj, e :e.ignore(),self.tableWidget)
        # DataView.ResAdaptor.init_ui_size(self)
        self.groupBox.setFixedSize(352*FIX_SIZE_WIDGET_SCALING, 36*FIX_SIZE_WIDGET_SCALING)
        self.groupBox.setStyleSheet('QGroupBox{font-size:%spx}'%int(12*FIX_SIZE_WIDGET_SCALING))
        self.groupBox_2.setFixedSize(130*FIX_SIZE_WIDGET_SCALING, 36*FIX_SIZE_WIDGET_SCALING)
        self.groupBox_2.setStyleSheet('QGroupBox{font-size:%spx}'%int(12*FIX_SIZE_WIDGET_SCALING))
        self.groupBox_3.setFixedSize(230*FIX_SIZE_WIDGET_SCALING, 36*FIX_SIZE_WIDGET_SCALING)
        # for button in self.findChildren((QtWidgets.QCheckBox, QtWidgets.QRadioButton)):
        #     fM = QFontMetrics(button.font())
        #     text_wid = fM.boundingRect(button.text()).width()


    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        a0.accept()

    def tbw_mouseClickEvent(self, widget:QtWidgets.QTableWidget, e):
        pass

    def setUpColourLable(self):
        self.label.setText('紧急')
        self.label.setStyleSheet(styleColour(GColour.TaskColour.TaskIsCritial))

        self.label_2.setText('预期订单')
        self.label_2.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectOrderTobe))

        self.label_3.setText('明确机会')
        self.label_3.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectClearChance))

        self.label_4.setText('高亮关注')
        self.label_4.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectHighlight))

        self.label_5.setText('上线跟进')
        self.label_5.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectInAct))

    def on_comboBox_change(self, check_status):
        # print('sender',self.sender())
        self.comboBox_check_status = check_status
        self.on_check_status_change()

    def on_timespace_chance(self, check_status):
        self.timespace_distance_checked = [i for i, ch in enumerate(check_status) if ch]
        self.on_check_status_change()

    def on_mission_range_change(self):
        # print('sender',self.sender())
        self.mission_range = self.get_mission_range()
        self.on_check_status_change()

    def get_mission_range(self):
        for i,radioButton in enumerate(self.groupBox.findChildren(QtWidgets.QRadioButton)):
            if radioButton.isChecked():
                mission_time_range = i#0代表返回非pending，1代表返回pending，2代表返回全部
        mission_destroyed = self.checkBox_3.isChecked()
        return ((mission_time_range,mission_destroyed ))

    def on_progress_check_status(self):
        self.progress_check_status = self.get_progess_check_status()
        self.on_check_status_change()

    def get_progess_check_status(self):
        check_status = []
        for i , checkBox in enumerate(self.groupBox_3.findChildren(QtWidgets.QCheckBox)):
            check_status.append(checkBox.isChecked())
        return tuple(check_status)

    def on_urgence_range_change(self):
        # print('sender',self.sender())
        self.urgence_range = self.get_urgence_range()
        self.on_check_status_change()

    def get_urgence_range(self):
        urgence_range = []
        for i, checkBox in enumerate(self.groupBox_2.findChildren(QtWidgets.QCheckBox)):
            urgence_range.append(checkBox.isChecked())
        return tuple(urgence_range)

    def getCheckStatus(self):
        return self.check_status

    def on_check_status_change(self):
        self.check_status = (self.mission_range, self.progress_check_status, self.urgence_range, self.comboBox_check_status,
                             self.timespace_distance_checked)
        self.checkStatusChanged.emit(self.check_status)
        pass

    def event(self, a0: QtCore.QEvent) -> bool:
        if a0.type() == QtCore.QEvent.HoverEnter:
            return False
        return super(TodoViewTabBar, self).event(a0)