from DetailViewTabBarUi import Ui_DetailViewTabBar
from PyQt5.QtWidgets import QTabBar, QTextEdit , QMessageBox,QTableWidget,QMouseEventTransition
from PyQt5 import QtGui


class DetailViewTabBar(QTabBar,Ui_DetailViewTabBar):
    def __init__(self, parent = None):
        super(DetailViewTabBar,self).__init__(parent)
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.tableWidget.setStyleSheet('QFrame{border-radius:0px;border-style:solid;border-width:1px;border-color:rgba(175,186,220,125)}'
                                       'QComboBox{border-radius:2px;border-style:solid;border-width:1px;border-color:rgba(175,186,220,125)}')



