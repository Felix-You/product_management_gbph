# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CompanyEditorUi.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CompanyEditorUi(object):
    def setupUi(self, CompanyEditorUi):
        CompanyEditorUi.setObjectName("CompanyEditorUi")
        CompanyEditorUi.resize(837, 711)
        self.gridLayout_2 = QtWidgets.QGridLayout(CompanyEditorUi)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(CompanyEditorUi)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.lineEdit.setMaximumSize(QtCore.QSize(400, 16777215))
        self.lineEdit.setClearButtonEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.comboBox_2 = QtWidgets.QComboBox(CompanyEditorUi)
        self.comboBox_2.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox_2.setWhatsThis("")
        self.comboBox_2.setEditable(True)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.comboBox_3 = QtWidgets.QComboBox(CompanyEditorUi)
        self.comboBox_3.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox_3.setEditable(True)
        self.comboBox_3.setObjectName("comboBox_3")
        self.horizontalLayout.addWidget(self.comboBox_3)
        self.comboBox_4 = QtWidgets.QComboBox(CompanyEditorUi)
        self.comboBox_4.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox_4.setEditable(True)
        self.comboBox_4.setObjectName("comboBox_4")
        self.horizontalLayout.addWidget(self.comboBox_4)
        self.comboBox_5 = QtWidgets.QComboBox(CompanyEditorUi)
        self.comboBox_5.setMinimumSize(QtCore.QSize(0, 30))
        self.comboBox_5.setEditable(True)
        self.comboBox_5.setObjectName("comboBox_5")
        self.horizontalLayout.addWidget(self.comboBox_5)
        self.pushButton_9 = QtWidgets.QPushButton(CompanyEditorUi)
        self.pushButton_9.setMaximumSize(QtCore.QSize(50, 20))
        self.pushButton_9.setObjectName("pushButton_9")
        self.horizontalLayout.addWidget(self.pushButton_9)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 2)
        self.horizontalLayout.setStretch(3, 2)
        self.horizontalLayout.setStretch(4, 2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.textEdit_3 = QtWidgets.QTextEdit(CompanyEditorUi)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_3.sizePolicy().hasHeightForWidth())
        self.textEdit_3.setSizePolicy(sizePolicy)
        self.textEdit_3.setMaximumSize(QtCore.QSize(600, 60))
        self.textEdit_3.setTabChangesFocus(True)
        self.textEdit_3.setObjectName("textEdit_3")
        self.gridLayout_3.addWidget(self.textEdit_3, 0, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(CompanyEditorUi)
        self.label_6.setMinimumSize(QtCore.QSize(70, 0))
        self.label_6.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 0, 2, 1, 1)
        self.textEdit = QtWidgets.QTextEdit(CompanyEditorUi)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setMaximumSize(QtCore.QSize(600, 60))
        self.textEdit.setStyleSheet("")
        self.textEdit.setTabChangesFocus(True)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_3.addWidget(self.textEdit, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(CompanyEditorUi)
        self.label.setMaximumSize(QtCore.QSize(80, 60))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setVerticalSpacing(3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.textEdit_4 = QtWidgets.QTextEdit(CompanyEditorUi)
        self.textEdit_4.setMinimumSize(QtCore.QSize(0, 0))
        self.textEdit_4.setMaximumSize(QtCore.QSize(300, 28))
        self.textEdit_4.setTabChangesFocus(True)
        self.textEdit_4.setObjectName("textEdit_4")
        self.gridLayout_4.addWidget(self.textEdit_4, 0, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(CompanyEditorUi)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(CompanyEditorUi)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.textEdit_5 = QtWidgets.QTextEdit(CompanyEditorUi)
        self.textEdit_5.setMaximumSize(QtCore.QSize(300, 28))
        self.textEdit_5.setTabChangesFocus(True)
        self.textEdit_5.setObjectName("textEdit_5")
        self.gridLayout_4.addWidget(self.textEdit_5, 1, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_4, 0, 4, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 12)
        self.gridLayout_3.setColumnStretch(2, 1)
        self.gridLayout_3.setColumnStretch(3, 12)
        self.gridLayout_3.setColumnStretch(4, 10)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.scrollArea = QtWidgets.QScrollArea(CompanyEditorUi)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 788, 626))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_3.setMinimumSize(QtCore.QSize(70, 0))
        self.label_3.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.textEdit_2 = QtWidgets.QTextEdit(self.scrollAreaWidgetContents_3)
        self.textEdit_2.setTabChangesFocus(True)
        self.textEdit_2.setObjectName("textEdit_2")
        self.horizontalLayout_6.addWidget(self.textEdit_2)
        self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_2.setMaximumSize(QtCore.QSize(75, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.tableView_3 = QtWidgets.QTableView(self.scrollAreaWidgetContents_3)
        self.tableView_3.setObjectName("tableView_3")
        self.horizontalLayout_6.addWidget(self.tableView_3)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem)
        self.pushButton_8 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_8.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_8.setObjectName("pushButton_8")
        self.verticalLayout_6.addWidget(self.pushButton_8)
        self.pushButton_7 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_7.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_7.setObjectName("pushButton_7")
        self.verticalLayout_6.addWidget(self.pushButton_7)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem1)
        self.horizontalLayout_6.addLayout(self.verticalLayout_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_4.setMinimumSize(QtCore.QSize(70, 0))
        self.label_4.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_8.addWidget(self.label_4)
        self.tableView = QtWidgets.QTableView(self.scrollAreaWidgetContents_3)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_8.addWidget(self.tableView)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.pushButton_4 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_4.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout_4.addWidget(self.pushButton_4)
        self.pushButton_3 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_3.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_4.addWidget(self.pushButton_3)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem3)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_5 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_5.setMinimumSize(QtCore.QSize(70, 0))
        self.label_5.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_9.addWidget(self.label_5)
        self.tableView_2 = QtWidgets.QTableView(self.scrollAreaWidgetContents_3)
        self.tableView_2.setObjectName("tableView_2")
        self.horizontalLayout_9.addWidget(self.tableView_2)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem4)
        self.pushButton_6 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_6.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_6.setObjectName("pushButton_6")
        self.verticalLayout_5.addWidget(self.pushButton_6)
        self.pushButton_5 = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        self.pushButton_5.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_5.setObjectName("pushButton_5")
        self.verticalLayout_5.addWidget(self.pushButton_5)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem5)
        self.horizontalLayout_9.addLayout(self.verticalLayout_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_9)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem6)
        self.label_9 = QtWidgets.QLabel(CompanyEditorUi)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_10.addWidget(self.label_9)
        self.lineEdit_2 = QtWidgets.QLineEdit(CompanyEditorUi)
        self.lineEdit_2.setMaximumSize(QtCore.QSize(300, 30))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_10.addWidget(self.lineEdit_2)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem7)
        self.pushButton_2 = QtWidgets.QPushButton(CompanyEditorUi)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_10.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(CompanyEditorUi)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_10.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(2, 10)
        self.verticalLayout.setStretch(3, 1)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(CompanyEditorUi)
        QtCore.QMetaObject.connectSlotsByName(CompanyEditorUi)
        CompanyEditorUi.setTabOrder(self.lineEdit, self.comboBox_2)
        CompanyEditorUi.setTabOrder(self.comboBox_2, self.comboBox_3)
        CompanyEditorUi.setTabOrder(self.comboBox_3, self.comboBox_4)
        CompanyEditorUi.setTabOrder(self.comboBox_4, self.comboBox_5)
        CompanyEditorUi.setTabOrder(self.comboBox_5, self.textEdit)
        CompanyEditorUi.setTabOrder(self.textEdit, self.textEdit_3)
        CompanyEditorUi.setTabOrder(self.textEdit_3, self.textEdit_4)
        CompanyEditorUi.setTabOrder(self.textEdit_4, self.textEdit_5)
        CompanyEditorUi.setTabOrder(self.textEdit_5, self.textEdit_2)
        CompanyEditorUi.setTabOrder(self.textEdit_2, self.tableView_3)
        CompanyEditorUi.setTabOrder(self.tableView_3, self.tableView)
        CompanyEditorUi.setTabOrder(self.tableView, self.tableView_2)
        CompanyEditorUi.setTabOrder(self.tableView_2, self.lineEdit_2)
        CompanyEditorUi.setTabOrder(self.lineEdit_2, self.pushButton_2)
        CompanyEditorUi.setTabOrder(self.pushButton_2, self.pushButton)
        CompanyEditorUi.setTabOrder(self.pushButton, self.scrollArea)

    def retranslateUi(self, CompanyEditorUi):
        _translate = QtCore.QCoreApplication.translate
        CompanyEditorUi.setWindowTitle(_translate("CompanyEditorUi", "Form"))
        self.lineEdit.setPlaceholderText(_translate("CompanyEditorUi", "公司名称"))
        self.comboBox_2.setPlaceholderText(_translate("CompanyEditorUi", "国家/地区/Country"))
        self.comboBox_3.setPlaceholderText(_translate("CompanyEditorUi", "省/州/State"))
        self.comboBox_4.setPlaceholderText(_translate("CompanyEditorUi", "市/City"))
        self.comboBox_5.setPlaceholderText(_translate("CompanyEditorUi", "县/Town"))
        self.pushButton_9.setText(_translate("CompanyEditorUi", "会议.."))
        self.label_6.setText(_translate("CompanyEditorUi", "详细地址Location"))
        self.label.setText(_translate("CompanyEditorUi", "公司全名Enterprise Name"))
        self.label_7.setText(_translate("CompanyEditorUi", "Tel"))
        self.label_8.setText(_translate("CompanyEditorUi", "Email"))
        self.label_3.setText(_translate("CompanyEditorUi", "公司综述Describe"))
        self.label_2.setText(_translate("CompanyEditorUi", "有关人员Relative Personnel"))
        self.pushButton_8.setText(_translate("CompanyEditorUi", "新增"))
        self.pushButton_7.setText(_translate("CompanyEditorUi", "删除"))
        self.label_4.setText(_translate("CompanyEditorUi", "有关记录Records"))
        self.pushButton_4.setText(_translate("CompanyEditorUi", "新增"))
        self.pushButton_3.setText(_translate("CompanyEditorUi", "删除"))
        self.label_5.setText(_translate("CompanyEditorUi", "有关文件Files"))
        self.pushButton_6.setText(_translate("CompanyEditorUi", "上传"))
        self.pushButton_5.setText(_translate("CompanyEditorUi", "删除"))
        self.label_9.setText(_translate("CompanyEditorUi", "所有者"))
        self.pushButton_2.setText(_translate("CompanyEditorUi", "保存Ctrl+S"))
        self.pushButton_2.setShortcut(_translate("CompanyEditorUi", "Ctrl+S"))
        self.pushButton.setText(_translate("CompanyEditorUi", "取消"))
