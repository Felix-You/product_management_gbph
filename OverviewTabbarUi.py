# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OverviewTabBarUi.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OverviewTabBar(object):
    def setupUi(self, OverviewTabBar):
        OverviewTabBar.setObjectName("OverviewTabBar")
        OverviewTabBar.resize(809, 517)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(OverviewTabBar.sizePolicy().hasHeightForWidth())
        OverviewTabBar.setSizePolicy(sizePolicy)
        OverviewTabBar.setMaximumSize(QtCore.QSize(16999, 16999))
        self.gridLayout_3 = QtWidgets.QGridLayout(OverviewTabBar)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableWidget = QtWidgets.QTableWidget(OverviewTabBar)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(OverviewTabBar)
        QtCore.QMetaObject.connectSlotsByName(OverviewTabBar)

    def retranslateUi(self, OverviewTabBar):
        _translate = QtCore.QCoreApplication.translate
        OverviewTabBar.setWindowTitle(_translate("OverviewTabBar", "Form"))
