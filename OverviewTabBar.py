from OverviewTabbarUi import Ui_OverviewTabBar
from PyQt5.QtWidgets import QTabBar, QPushButton , QMessageBox,QTableWidget,QMouseEventTransition,QLabel,QSpacerItem,QSizePolicy
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from RedefinedWidget import CheckLableBox
import GColour, types

def styleColour(colour:tuple) :
    return "background:rgb%s"%str(colour)



class OverviewTabBar(QTabBar,Ui_OverviewTabBar):
    def __init__(self, parent = None):
        super(OverviewTabBar,self).__init__(parent)
        self.setupUi(self)
        self.setUpColourLable()
        self.tableWidget.setShowGrid(False)

        self.tableWidget.mouseDoubleClickEvent = types.MethodType(self.tbw_mouseClickEvent, self.tableWidget)
        self.tableWidget.mousePressEvent = types.MethodType(self.tbw_mouseClickEvent, self.tableWidget)
        self.tableWidget.mouseMoveEvent = types.MethodType(lambda obj,e :e.ignore(), self.tableWidget)

    def tbw_mouseClickEvent(self, widget:QTableWidget, e):
        pass

    def setUpColourLable(self):
        from DataView import DF_Ratio
        self.btn_showStatistics = QPushButton('统计信息..',self)
        self.btn_showStatistics.setFixedSize(80*DF_Ratio,25*DF_Ratio)
        font= QtGui.QFont()
        font.setPointSize(8)
        # font.setPixelSize(12)
        self.btn_showStatistics.setFont(font)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.addWidget(self.btn_showStatistics)

        self.btn_exportData = QPushButton('导出数据..', self)
        self.btn_exportData.setFixedSize(80*DF_Ratio,25*DF_Ratio)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.btn_exportData.setFont(font)
        self.horizontalLayout.addWidget(self.btn_exportData)

        rspacer = QSpacerItem(10,10,hPolicy=QSizePolicy.Expanding)
        self.horizontalLayout.addItem(rspacer)

        label_graphic = QLabel('图示:', self)
        label_graphic.setFixedSize(35*DF_Ratio,25*DF_Ratio)
        self.horizontalLayout.addWidget(label_graphic)

        label_is_critical = QLabel('紧急', self)
        label_is_critical.setStyleSheet(styleColour(GColour.TaskColour.TaskIsCritial))
        self.horizontalLayout.addWidget(label_is_critical)
        label_is_critical.setFixedSize(30*DF_Ratio,25*DF_Ratio)

        self.checkLabel = CheckLableBox([
            ('is_deal', '已成交', GColour.ProjectRGBColour.ProjecIsDeal, 255),
            ('order_tobe','预期订单',GColour.ProjectRGBColour.ProjectOrderTobe,255),
            ('clear_chance','明确机会',GColour.ProjectRGBColour.ProjectClearChance,255),
            ('highlight','高亮关注',GColour.ProjectRGBColour.ProjectHighlight,255),
            ('in_act','上线跟进',GColour.ProjectRGBColour.ProjectInAct,255),
            ('to_visit','◆需拜访',(0,0,0),0)
        ])

        self.horizontalLayout.addWidget(self.checkLabel)
        # lable_order_tobe = QLabel('预期订单',self)
        # lable_order_tobe.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectOrderTobe))
        # lable_order_tobe.setFixedSize(60*DF_Ratio,25*DF_Ratio)
        # self.horizontalLayout.addWidget(lable_order_tobe)
        #
        # lable_clear_chance = QLabel('明确机会',self)
        # lable_clear_chance.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectClearChance))
        # lable_clear_chance.setFixedSize(60*DF_Ratio,25*DF_Ratio)
        # self.horizontalLayout.addWidget(lable_clear_chance)
        #
        # lable_highlight = QLabel('高亮关注',self)
        # lable_highlight.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectHighlight))
        # lable_highlight.setFixedSize(60*DF_Ratio,25*DF_Ratio)
        # self.horizontalLayout.addWidget(lable_highlight)
        #
        # lable_in_act = QLabel('上线跟进',self)
        # lable_in_act.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectInAct))
        # lable_in_act.setFixedSize(60*DF_Ratio,25*DF_Ratio)
        # self.horizontalLayout.addWidget(lable_in_act)
        #
        # label_to_visit = QLabel('<b style="color:rgb%s">◆需拜访</b>'%str(GColour.ProjectRGBColour.ProjectToVisit), self)
        # # label_to_visit.setFont(QFont())
        # # label_to_visit.setStyleSheet(styleColour(GColour.ProjectRGBColour.ProjectToVisit))
        # self.horizontalLayout.addWidget(label_to_visit)





