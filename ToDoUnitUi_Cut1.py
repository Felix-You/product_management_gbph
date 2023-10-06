# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ToDoUnitUi_Cut1.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form_1(object):
    def setupUi(self, Form_1):
        Form_1.setObjectName("Form_1")
        Form_1.resize(393, 164)
        Form_1.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(Form_1)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.gridLayout.setVerticalSpacing(11)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.textEdit = QtWidgets.QTextEdit(Form_1)
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_5.addWidget(self.textEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.pushButton_company = QtWidgets.QPushButton(Form_1)
        self.pushButton_company.setMaximumSize(QtCore.QSize(100, 25))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(8)
        self.pushButton_company.setFont(font)
        self.pushButton_company.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_company.setText("")
        self.pushButton_company.setIconSize(QtCore.QSize(1, 1))
        self.pushButton_company.setObjectName("pushButton_company")
        self.verticalLayout_6.addWidget(self.pushButton_company)
        self.pushButton_project = QtWidgets.QPushButton(Form_1)
        self.pushButton_project.setMaximumSize(QtCore.QSize(100, 25))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(8)
        font.setKerning(True)
        self.pushButton_project.setFont(font)
        self.pushButton_project.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_project.setText("")
        self.pushButton_project.setIconSize(QtCore.QSize(1, 1))
        self.pushButton_project.setObjectName("pushButton_project")
        self.verticalLayout_6.addWidget(self.pushButton_project)
        self.horizontalLayout_8.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.textEdit_2 = QtWidgets.QTextEdit(Form_1)
        self.textEdit_2.setMaximumSize(QtCore.QSize(16777215, 90))
        self.textEdit_2.setLineWidth(0)
        self.textEdit_2.setObjectName("textEdit_2")
        self.verticalLayout_7.addWidget(self.textEdit_2)
        self.horizontalLayout_8.addLayout(self.verticalLayout_7)
        self.horizontalLayout_8.setStretch(0, 2)
        self.horizontalLayout_8.setStretch(1, 5)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.verticalLayout.setStretch(0, 3)
        self.verticalLayout.setStretch(1, 2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form_1)
        QtCore.QMetaObject.connectSlotsByName(Form_1)

    def retranslateUi(self, Form_1):
        _translate = QtCore.QCoreApplication.translate
        Form_1.setWindowTitle(_translate("Form_1", "Form"))

