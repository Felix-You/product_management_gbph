# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MeetingModeDialogUi.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1281, 758)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.formLayout_4 = QtWidgets.QFormLayout()
        self.formLayout_4.setVerticalSpacing(7)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_10 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_10.setToolTipDuration(0)
        self.label_10.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 35))
        self.lineEdit.setMaximumSize(QtCore.QSize(300, 35))
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label_16 = QtWidgets.QLabel(Dialog)
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_16)
        self.dateEdit = QtWidgets.QDateEdit(Dialog)
        self.dateEdit.setMinimumSize(QtCore.QSize(0, 25))
        self.dateEdit.setMaximumSize(QtCore.QSize(120, 16777215))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDate(QtCore.QDate(1998, 1, 1))
        self.dateEdit.setObjectName("dateEdit")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.dateEdit)
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_11.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_11.setObjectName("label_11")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.textEdit_5 = QtWidgets.QTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_5.sizePolicy().hasHeightForWidth())
        self.textEdit_5.setSizePolicy(sizePolicy)
        self.textEdit_5.setMaximumSize(QtCore.QSize(300, 16777215))
        self.textEdit_5.setTabChangesFocus(True)
        self.textEdit_5.setObjectName("textEdit_5")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.textEdit_5)
        self.verticalLayout_6.addLayout(self.formLayout_4)
        self.gridLayout_10 = QtWidgets.QGridLayout()
        self.gridLayout_10.setHorizontalSpacing(4)
        self.gridLayout_10.setVerticalSpacing(3)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setMaximumSize(QtCore.QSize(80, 300))
        self.pushButton_5.setFocusPolicy(QtCore.Qt.TabFocus)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_10.addWidget(self.pushButton_5, 2, 2, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMaximumSize(QtCore.QSize(80, 40))
        self.pushButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_10.addWidget(self.pushButton, 2, 3, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setMaximumSize(QtCore.QSize(80, 100))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setFocusPolicy(QtCore.Qt.TabFocus)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout_10.addWidget(self.pushButton_2, 1, 3, 1, 1)
        self.pushButton_down = QtWidgets.QPushButton(Dialog)
        self.pushButton_down.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_down.setObjectName("pushButton_down")
        self.gridLayout_10.addWidget(self.pushButton_down, 2, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setMaximumSize(QtCore.QSize(80, 100))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setFocusPolicy(QtCore.Qt.TabFocus)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_10.addWidget(self.pushButton_4, 1, 2, 1, 1)
        self.pushButton_up = QtWidgets.QPushButton(Dialog)
        self.pushButton_up.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_up.setObjectName("pushButton_up")
        self.gridLayout_10.addWidget(self.pushButton_up, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_10.addItem(spacerItem, 1, 1, 1, 1)
        self.gridLayout_10.setRowStretch(0, 1)
        self.verticalLayout_6.addLayout(self.gridLayout_10)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 0))
        self.scrollArea.setStyleSheet("#scrollAreaWidgetContents{background:lightgrey}")
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 509, 399))
        self.scrollAreaWidgetContents.setStyleSheet("QScrollArea{background:yellow}")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(8)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_12 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_3.addWidget(self.label_12)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(0, 35))
        self.lineEdit_2.setMaximumSize(QtCore.QSize(350, 35))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_3.addWidget(self.lineEdit_2)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem2)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 20)
        self.horizontalLayout_3.setStretch(2, 5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_15 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_15.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_5.addWidget(self.label_15)
        self.textEdit_3 = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_3.sizePolicy().hasHeightForWidth())
        self.textEdit_3.setSizePolicy(sizePolicy)
        self.textEdit_3.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit_3.setMaximumSize(QtCore.QSize(350, 400))
        self.textEdit_3.setLineWidth(11)
        self.textEdit_3.setMidLineWidth(5)
        self.textEdit_3.setAutoFormatting(QtWidgets.QTextEdit.AutoBulletList)
        self.textEdit_3.setTabChangesFocus(True)
        self.textEdit_3.setLineWrapColumnOrWidth(0)
        self.textEdit_3.setObjectName("textEdit_3")
        self.horizontalLayout_5.addWidget(self.textEdit_3)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.comboBox_progress = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_progress.setMaximumSize(QtCore.QSize(70, 16777215))
        self.comboBox_progress.setObjectName("comboBox_progress")
        self.verticalLayout_3.addWidget(self.comboBox_progress)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_10.addLayout(self.verticalLayout_3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_10.addItem(spacerItem4)
        self.horizontalLayout_10.setStretch(0, 1)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 20)
        self.horizontalLayout_5.setStretch(2, 5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_14 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_14.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_6.addWidget(self.label_14)
        self.textEdit_4 = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_4.sizePolicy().hasHeightForWidth())
        self.textEdit_4.setSizePolicy(sizePolicy)
        self.textEdit_4.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit_4.setMaximumSize(QtCore.QSize(350, 200))
        self.textEdit_4.setAutoFormatting(QtWidgets.QTextEdit.AutoBulletList)
        self.textEdit_4.setTabChangesFocus(True)
        self.textEdit_4.setObjectName("textEdit_4")
        self.horizontalLayout_6.addWidget(self.textEdit_4)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_todo = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_todo.sizePolicy().hasHeightForWidth())
        self.checkBox_todo.setSizePolicy(sizePolicy)
        self.checkBox_todo.setMaximumSize(QtCore.QSize(70, 16777215))
        self.checkBox_todo.setObjectName("checkBox_todo")
        self.verticalLayout.addWidget(self.checkBox_todo)
        self.horizontalLayout_8.addLayout(self.verticalLayout)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_8.addItem(spacerItem5)
        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 20)
        self.horizontalLayout_6.setStretch(2, 5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_13 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_7.addWidget(self.label_13)
        self.textEdit_6 = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        self.textEdit_6.setMaximumSize(QtCore.QSize(350, 200))
        self.textEdit_6.setTabChangesFocus(True)
        self.textEdit_6.setObjectName("textEdit_6")
        self.horizontalLayout_7.addWidget(self.textEdit_6)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_9.addItem(spacerItem6)
        self.pushButton_6 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_6.setMinimumSize(QtCore.QSize(60, 35))
        self.pushButton_6.setMaximumSize(QtCore.QSize(70, 16777215))
        self.pushButton_6.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.pushButton_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton_6.setCheckable(False)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_9.addWidget(self.pushButton_6)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 20)
        self.horizontalLayout_7.setStretch(2, 5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 5)
        self.verticalLayout_2.setStretch(3, 2)
        self.verticalLayout_2.setStretch(4, 2)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        spacerItem7 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem7)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout_2.setObjectName("formLayout_2")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setMaximumSize(QtCore.QSize(250, 90))
        self.textEdit.setTabChangesFocus(True)
        self.textEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textEdit.setObjectName("textEdit")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.textEdit)
        self.label_18 = QtWidgets.QLabel(Dialog)
        self.label_18.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_18.setObjectName("label_18")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_18)
        self.textEdit_2 = QtWidgets.QTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy)
        self.textEdit_2.setMaximumSize(QtCore.QSize(250, 65))
        self.textEdit_2.setTabChangesFocus(True)
        self.textEdit_2.setObjectName("textEdit_2")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.textEdit_2)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout_2.setItem(3, QtWidgets.QFormLayout.LabelRole, spacerItem8)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_2.setItem(4, QtWidgets.QFormLayout.FieldRole, spacerItem9)
        self.label_17 = QtWidgets.QLabel(Dialog)
        self.label_17.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_17.setObjectName("label_17")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_17)
        self.pushButton_personnel = QtWidgets.QPushButton(Dialog)
        self.pushButton_personnel.setMaximumSize(QtCore.QSize(35, 20))
        self.pushButton_personnel.setObjectName("pushButton_personnel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.pushButton_personnel)
        self.comboBox_personnel = QtWidgets.QComboBox(Dialog)
        self.comboBox_personnel.setMaximumSize(QtCore.QSize(250, 16777215))
        self.comboBox_personnel.setObjectName("comboBox_personnel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_personnel)
        self.horizontalLayout.addLayout(self.formLayout_2)
        self.horizontalLayout.setStretch(0, 6)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 10)
        self.horizontalLayout.setStretch(3, 1)
        self.horizontalLayout.setStretch(4, 6)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 200))
        self.tableWidget.setMaximumSize(QtCore.QSize(16777215, 2000))
        self.tableWidget.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_5.addWidget(self.tableWidget)
        self.verticalLayout_5.setStretch(0, 5)
        self.verticalLayout_5.setStretch(1, 4)
        self.verticalLayout_4.addLayout(self.verticalLayout_5)
        self.gridLayout_3.addLayout(self.verticalLayout_4, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEdit, self.dateEdit)
        Dialog.setTabOrder(self.dateEdit, self.textEdit_5)
        Dialog.setTabOrder(self.textEdit_5, self.textEdit)
        Dialog.setTabOrder(self.textEdit, self.textEdit_2)
        Dialog.setTabOrder(self.textEdit_2, self.pushButton_6)
        Dialog.setTabOrder(self.pushButton_6, self.lineEdit_2)
        Dialog.setTabOrder(self.lineEdit_2, self.textEdit_3)
        Dialog.setTabOrder(self.textEdit_3, self.textEdit_4)
        Dialog.setTabOrder(self.textEdit_4, self.textEdit_6)
        Dialog.setTabOrder(self.textEdit_6, self.comboBox_progress)
        Dialog.setTabOrder(self.comboBox_progress, self.checkBox_todo)
        Dialog.setTabOrder(self.checkBox_todo, self.pushButton_5)
        Dialog.setTabOrder(self.pushButton_5, self.pushButton_4)
        Dialog.setTabOrder(self.pushButton_4, self.pushButton)
        Dialog.setTabOrder(self.pushButton, self.pushButton_2)
        Dialog.setTabOrder(self.pushButton_2, self.pushButton_up)
        Dialog.setTabOrder(self.pushButton_up, self.pushButton_down)
        Dialog.setTabOrder(self.pushButton_down, self.scrollArea)
        Dialog.setTabOrder(self.scrollArea, self.tableWidget)
        Dialog.setTabOrder(self.tableWidget, self.pushButton_personnel)
        Dialog.setTabOrder(self.pushButton_personnel, self.comboBox_personnel)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "会议纪要"))
        self.label_10.setText(_translate("Dialog", "客户名称:"))
        self.label_16.setText(_translate("Dialog", "会议日期:"))
        self.dateEdit.setDisplayFormat(_translate("Dialog", "yyyy/M/d"))
        self.label_11.setText(_translate("Dialog", "客户情况:"))
        self.pushButton_5.setText(_translate("Dialog", "生成Word"))
        self.pushButton.setText(_translate("Dialog", "保存记录"))
        self.pushButton_2.setText(_translate("Dialog", "导出Excel"))
        self.pushButton_down.setText(_translate("Dialog", "▼"))
        self.pushButton_4.setText(_translate("Dialog", "删除选中行"))
        self.pushButton_up.setText(_translate("Dialog", "▲"))
        self.label.setText(_translate("Dialog", "项目信息"))
        self.label_12.setText(_translate("Dialog", "项目名称:"))
        self.label_15.setText(_translate("Dialog", "项目情况:"))
        self.label_2.setText(_translate("Dialog", "管线进度"))
        self.label_14.setText(_translate("Dialog", "需跟进:"))
        self.checkBox_todo.setText(_translate("Dialog", "CheckBox"))
        self.label_13.setText(_translate("Dialog", "备注:"))
        self.pushButton_6.setText(_translate("Dialog", "+添加"))
        self.pushButton_6.setShortcut(_translate("Dialog", "Ctrl+J"))
        self.label_18.setText(_translate("Dialog", "我方人员:"))
        self.label_17.setText(_translate("Dialog", "客户人员:"))
        self.pushButton_personnel.setText(_translate("Dialog", "+.."))

