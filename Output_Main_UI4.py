# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Output_Main_UI4.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1622, 1126)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Layout_clock = QtWidgets.QHBoxLayout()
        self.Layout_clock.setObjectName("Layout_clock")
        self.horizontalLayout.addLayout(self.Layout_clock)
        spacerItem = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMaximumSize(QtCore.QSize(500, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_2.addWidget(self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(0, 0))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(500, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_2.addWidget(self.lineEdit_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        spacerItem2 = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setMinimumSize(QtCore.QSize(70, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.groupBox.setCheckable(True)
        self.groupBox.setObjectName("groupBox")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setGeometry(QtCore.QRect(6, 18, 141, 24))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.checkBox.setFont(font)
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_2.setGeometry(QtCore.QRect(6, 37, 111, 25))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_3.setGeometry(QtCore.QRect(6, 58, 111, 24))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setIconSize(QtCore.QSize(16, 16))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_4.setGeometry(QtCore.QRect(6, 78, 121, 24))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.checkBox_4.setFont(font)
        self.checkBox_4.setObjectName("checkBox_4")
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setCheckable(True)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout.addWidget(self.groupBox_4)
        spacerItem3 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QtCore.QSize(270, 35))
        self.groupBox_3.setMaximumSize(QtCore.QSize(180, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setContentsMargins(2, 0, 2, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.radioButton.setFont(font)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.horizontalLayout_2.addWidget(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.radioButton_2.setFont(font)
        self.radioButton_2.setObjectName("radioButton_2")
        self.horizontalLayout_2.addWidget(self.radioButton_2)
        self.radioButton_3 = QtWidgets.QRadioButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.radioButton_3.setFont(font)
        self.radioButton_3.setObjectName("radioButton_3")
        self.horizontalLayout_2.addWidget(self.radioButton_3)
        self.gridLayout_4.addWidget(self.groupBox_3, 0, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem4, 0, 4, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(82, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem5, 0, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setMinimumSize(QtCore.QSize(100, 30))
        self.pushButton.setMaximumSize(QtCore.QSize(200, 50))
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_4.addWidget(self.pushButton, 0, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_4, 1, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout_3, 2, 0, 1, 1)
        self.gridLayout_2.setRowStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1622, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menu)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(self.menu)
        self.menu_3.setObjectName("menu_3")
        self.menu_5 = QtWidgets.QMenu(self.menubar)
        self.menu_5.setObjectName("menu_5")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionGeoFilterSet = QtWidgets.QAction(MainWindow)
        self.actionGeoFilterSet.setObjectName("actionGeoFilterSet")
        self.actionMeetingRecord = QtWidgets.QAction(MainWindow)
        self.actionMeetingRecord.setObjectName("actionMeetingRecord")
        self.actionNewCompany = QtWidgets.QAction(MainWindow)
        self.actionNewCompany.setObjectName("actionNewCompany")
        self.actionNewProject = QtWidgets.QAction(MainWindow)
        self.actionNewProject.setObjectName("actionNewProject")
        self.actionCompany = QtWidgets.QAction(MainWindow)
        self.actionCompany.setObjectName("actionCompany")
        self.actionadd_TodoUnit = QtWidgets.QAction(MainWindow)
        self.actionadd_TodoUnit.setObjectName("actionadd_TodoUnit")
        self.actionCompanyGroupSet = QtWidgets.QAction(MainWindow)
        self.actionCompanyGroupSet.setObjectName("actionCompanyGroupSet")
        self.actionSetTheme = QtWidgets.QAction(MainWindow)
        self.actionSetTheme.setObjectName("actionSetTheme")
        self.actionSetDatabasePath = QtWidgets.QAction(MainWindow)
        self.actionSetDatabasePath.setObjectName("actionSetDatabasePath")
        self.actionEditOfficeJobType = QtWidgets.QAction(MainWindow)
        self.actionEditOfficeJobType.setObjectName("actionEditOfficeJobType")
        self.menu_2.addAction(self.actionGeoFilterSet)
        self.menu_2.addAction(self.actionCompanyGroupSet)
        self.menu_2.addAction(self.actionSetTheme)
        self.menu_2.addAction(self.actionSetDatabasePath)
        self.menu_2.addAction(self.actionEditOfficeJobType)
        self.menu_3.addAction(self.actionNewCompany)
        self.menu_3.addAction(self.actionNewProject)
        self.menu_3.addAction(self.actionadd_TodoUnit)
        self.menu.addAction(self.menu_2.menuAction())
        self.menu.addAction(self.menu_3.menuAction())
        self.menu.addAction(self.actionMeetingRecord)
        self.menu_5.addAction(self.actionCompany)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_5.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "广东国标医药项目管理"))
        self.label.setText(_translate("MainWindow", "项目名称"))
        self.label_2.setText(_translate("MainWindow", "客户名称"))
        self.groupBox.setTitle(_translate("MainWindow", "机会等级"))
        self.checkBox.setText(_translate("MainWindow", "1.活动"))
        self.checkBox_2.setText(_translate("MainWindow", "2.等待"))
        self.checkBox_3.setText(_translate("MainWindow", "3.潜在"))
        self.checkBox_4.setText(_translate("MainWindow", "4.停止"))
        self.groupBox_2.setTitle(_translate("MainWindow", "区域编组"))
        self.groupBox_4.setTitle(_translate("MainWindow", "自定编组"))
        self.groupBox_3.setTitle(_translate("MainWindow", "应用搜索条件："))
        self.radioButton.setText(_translate("MainWindow", "概览模式"))
        self.radioButton_2.setText(_translate("MainWindow", "详情模式"))
        self.radioButton_3.setText(_translate("MainWindow", "任务模式"))
        self.pushButton.setText(_translate("MainWindow", "查看"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menu.setTitle(_translate("MainWindow", "编辑"))
        self.menu_2.setTitle(_translate("MainWindow", "设置偏好"))
        self.menu_3.setTitle(_translate("MainWindow", "新建"))
        self.menu_5.setTitle(_translate("MainWindow", "查看"))
        self.actionGeoFilterSet.setText(_translate("MainWindow", "区域编组..."))
        self.actionGeoFilterSet.setShortcut(_translate("MainWindow", "Ctrl+G"))
        self.actionMeetingRecord.setText(_translate("MainWindow", "会议纪要..."))
        self.actionMeetingRecord.setIconText(_translate("MainWindow", "会议纪要"))
        self.actionNewCompany.setText(_translate("MainWindow", "客户..."))
        self.actionNewProject.setText(_translate("MainWindow", "项目..."))
        self.actionCompany.setText(_translate("MainWindow", "合作公司..."))
        self.actionadd_TodoUnit.setText(_translate("MainWindow", "任务..."))
        self.actionCompanyGroupSet.setText(_translate("MainWindow", "自定编组..."))
        self.actionCompanyGroupSet.setShortcut(_translate("MainWindow", "Ctrl+F"))
        self.actionSetTheme.setText(_translate("MainWindow", "界面风格..."))
        self.actionSetDatabasePath.setText(_translate("MainWindow", "数据路径..."))
        self.actionEditOfficeJobType.setText(_translate("MainWindow", "任务分类..."))

