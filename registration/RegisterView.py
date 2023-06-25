from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QDialogButtonBox


class RegisterDialog(QDialog):

    def __init__(self,controller, machine_code,access_email):
        super(RegisterDialog, self).__init__(parent=None)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle('激活软件')
        self.setFixedSize(400, 300)
        self.mainLayout = QtWidgets.QFormLayout(self)
        self.mainLayout.setSpacing(16)
        self.label_combin = QtWidgets.QLabel('请发送本机机器码：')
        self.line_combin = QtWidgets.QLineEdit(self)
        self.line_combin.setText(machine_code)
        self.line_combin.setReadOnly(True)
        self.label_email = QtWidgets.QLabel('到邮箱：')
        self.line_email = QtWidgets.QLineEdit(self)
        self.line_email.setText(access_email)
        self.line_email.setReadOnly(True)
        self.label_register_code = QtWidgets.QLabel('获取并输入激活码：')
        self.text_edit = QtWidgets.QPlainTextEdit(self)
        self.bbOkCancel = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setDefault(True)
        self.bbOkCancel.button(QDialogButtonBox.Ok).clicked.connect(self.on_register_button)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setText('激活')
        self.bbOkCancel.button(QDialogButtonBox.Cancel).setText('取消')
        self.bbOkCancel.button(QDialogButtonBox.Cancel).clicked.connect(self.on_cancel_button)
        self.mainLayout.addRow(self.label_combin, self.line_combin)
        self.mainLayout.addRow(self.label_email, self.line_email)
        self.mainLayout.addRow(self.label_register_code, self.text_edit)
        self.mainLayout.addRow(self.bbOkCancel)
        self.controller = controller
        # self.show()

    def setController(self, controller):
        self.controller = controller

    def on_register_button(self):
        text = self.text_edit.toPlainText()
        ok = self.controller.register(text)
        if ok :
            QtWidgets.QMessageBox.about(self, '成功', '激活成功！')
            self.close()
            self.accept()
        else:
            QtWidgets.QMessageBox.about(self,'失败', '激活失败！')
            return

    def on_cancel_button(self):
        self.close()
        self.reject()

    @staticmethod
    def doRegistration(controller,machine_code:str , access_email:str):
        dialog = RegisterDialog(controller,machine_code,access_email)
        ok  = dialog.exec_()
        return ok