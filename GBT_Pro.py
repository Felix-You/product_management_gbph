# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 00:19:03 2020

@author: Felix
"""

import sys,os, traceback, ctypes
working_path = os.path.dirname(os.path.realpath(__file__))
os.environ['working_path'] = working_path
sys.path.append(working_path)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
# if is_admin():
#     os.chroot(working_path)
# else:
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
#     os.chroot(working_path)

# print(os.environ['HOME'])
import win32com.client
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QGuiApplication, QMouseEvent,QKeyEvent
from PyQt5.QtWidgets import QApplication, QMainWindow,QDialogButtonBox,QMessageBox
from PyQt5.QtCore import Qt, QSharedMemory, QEvent
from FilePathInit import workingDir, userDir, get_desktop
from core.GlobalListener import KEY_MOUSE_EVENT, global_key_mouse_listener, global_logger
from time import sleep
from registration.Register import Register

class DirectoryChooseBox(QtWidgets.QDialog):
    def __init__(self, title:str ,hint_text:str = None,parent = None):
        super(DirectoryChooseBox, self).__init__(parent)
        self.title = title
        self.hint_text = hint_text
        # self.setWindowFlags(QtCore.Qt.Window|Qt.WindowCloseButtonHint)
        self.setWindowTitle(self.title)
        self.setFixedSize(580, 220)
        self.VLayOut = QtWidgets.QVBoxLayout(self)
        self.lable  = QtWidgets.QLabel(self)
        self.lable.setText('欢迎使用！\n\n请设置您的个人数据和文件的保存文件夹,以英文命名。\n千万不要放在解压出来的那个程序文件夹里！'
                           '\n\n在连接到服务器之前，删除这个文件夹和里面的文件，会导致所有记录丢失。\n最好不要将个人文件放在C盘，以免重装系统导致文件丢失。')
        self.lable.setWordWrap(True)
        self.VLayOut.addWidget(self.lable)
        self.HLayOut = QtWidgets.QHBoxLayout(self)
        self.VLayOut.addLayout(self.HLayOut)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setPlaceholderText(self.hint_text)
        self.lineEdit.setFixedSize(500 , 30)
        self.HLayOut.addWidget(self.lineEdit)

        self.path_button = QtWidgets.QPushButton(self)
        self.path_button.setText('目录..')
        self.path_button.clicked.connect(self.on_select_button_clicked)
        self.path_button.setMaximumWidth(50)
        self.HLayOut.addWidget(self.path_button)

        self.dialog_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel , Qt.Horizontal , self)
        self.dialog_button.button(QDialogButtonBox.Ok).setDefault(True)
        self.dialog_button.button(QDialogButtonBox.Ok).setEnabled(False)
        self.dialog_button.accepted.connect(self.accept)
        self.dialog_button.rejected.connect(self.reject)
        self.VLayOut.addWidget(self.dialog_button)

    def on_select_button_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, '选择个人数据存放路径', os.path.expanduser('~')+'\Documents')
        if os.path.isdir(path):
            self.dialog_button.button(QDialogButtonBox.Ok).setEnabled(True)
        self.lineEdit.setText(path)

    @staticmethod
    def getDirectory(title:str ,hint_text:str = None,parent = None):
        dialog = DirectoryChooseBox(title=title,hint_text=hint_text,parent=parent)
        result = dialog.exec_()
        directory = dialog.lineEdit.text()
        return (directory, result == QtWidgets.QDialog.Accepted)

def checkInitFiles():

    if workingDir.hasUserDirectory():
        workingDir.initUserFiles()
        userDir.reloadDir()
        return True
        pass
    else:
        path ,ok = DirectoryChooseBox.getDirectory(title='选择个人文件存放目录' ,
                                                                  hint_text='最好不要将个人文件放在C盘，以免重装系统导致丢失' )
        if not ok:
            return False
        else:
            workingDir.createUserDirctory(path)
            workingDir.initUserFiles()
            sleep(2)
            userDir.reloadDir()
            return True

def handleDesktopShortcut():
    desktop = get_desktop()
    app_file_name = 'GBT_Pro.exe'
    working_path = os.path.dirname(os.path.realpath(__file__))
    app_file_path = os.path.join(working_path, app_file_name)
    shell = win32com.client.Dispatch('WScript.shell')
    for file_name in os.listdir(desktop):
        if file_name.endswith('.lnk'):
            link = os.path.join(desktop, file_name)
            _shortcut = shell.CreateShortCut(link)
            real_path = _shortcut.Targetpath
            working_directory = _shortcut.WorkingDirectory
            if real_path == app_file_path and working_directory==working_path:
                return
            if real_path.endswith(app_file_name):
                path = link
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = app_file_path  # 指定路径
                shortcut.WorkingDirectory  = working_path
                shortcut.IconLocation = app_file_path  # 指定图标
                shortcut.save()
                return
    else:
        path = os.path.join(desktop, app_file_name) + '.lnk'
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = app_file_path  # 指定路径
        shortcut.IconLocation = app_file_path  # 指定图标
        shortcut.WorkingDirectory = working_path
        shortcut.save()
        return

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    elif issubclass(exc_type,Exception):
        global_logger.exception("Excepthook caught exception", exc_info=(exc_type, exc_value, exc_traceback))  # 重点
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    else:
        global_logger.error("Excepthook caught error", exc_info=(exc_type, exc_value, exc_traceback)) # 重点
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    sys.exit(exc_value)

sys.excepthook = handle_exception # 重点

def close_window(window):
    """关闭友好提示"""
    if QMessageBox().information(None, "标题", "不能重复开启",
                                 QMessageBox.Ok) == QMessageBox.Ok:
        window.close()


class GlobalApplication(QApplication):
    def notify(self, a0: QtCore.QObject, a1: QtCore.QEvent) -> bool:
        # objMeta = a0.metaObject()
        # clName = objMeta.className()
        event_code: int = 0
        if a1.type() == QEvent.MouseButtonPress:
            mouse_event_code:int
            mouseEvent = QMouseEvent(a1)
            if mouseEvent.button() == Qt.RightButton:
                event_code = KEY_MOUSE_EVENT.MOUSE_RIGHT_PRESS
            elif mouseEvent.button() == Qt.LeftButton:
                event_code = KEY_MOUSE_EVENT.MOUSE_LEFT_PRESS
            else:
                pass
        elif a1.type() ==QEvent.MouseButtonRelease:
            mouseEvent = QMouseEvent(a1)
            if mouseEvent.button() == Qt.RightButton:
                event_code = KEY_MOUSE_EVENT.MOUSE_RIGHT_RELEASE
            elif mouseEvent.button() == Qt.LeftButton:
                event_code = KEY_MOUSE_EVENT.MOUSE_LEFT_RELEASE
            else:
                pass
        elif a1.type() == QEvent.KeyPress:
            keyEvent = QKeyEvent(a1)
            if keyEvent.key() == Qt.Key_Escape:
                event_code = KEY_MOUSE_EVENT.KEY_ESCAPE_PRESS
            elif keyEvent.key() == Qt.Key_Control:
                event_code = KEY_MOUSE_EVENT.KEY_CONTROL_PRESS
            else:
                event_code = KEY_MOUSE_EVENT.KEY_ANY_PRESS
        elif a1.type() == QEvent.KeyRelease:
            keyEvent = QKeyEvent(a1)
            if keyEvent.key() == Qt.Key_Control:
                event_code = KEY_MOUSE_EVENT.KEY_CONTROL_RELEASE
            else:
                pass
        else:
            pass
        global_key_mouse_listener.accept(event_code)
        return super(GlobalApplication, self).notify(a0, a1)


def main():
# if __name__ == '__main__':

    # global_logger.debug('debug级别，一般用来打印一些调试信息，级别最低')
    # global_logger.info('info级别，一般用来打印一些正常的操作信息')
    # global_logger.warning('waring级别，一般用来打印警告信息')
    # global_logger.error('error级别，一般用来打印一些错误信息')
    # global_logger.critical('critical级别，一般用来打印一些致命的错误信息，等级最高')
    handleDesktopShortcut()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    #     GlobalApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # os.environ["QT_SCALE_FACTOR"] = '1'
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    # os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Floor)
    app = GlobalApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app.setWindowIcon(QIcon(os.path.join(working_path, 'icons/main.ico')))
    share = QSharedMemory()
    share.setKey("greencrm_mainwindow")#
    if share.attach():
        msg_box = QMessageBox()
        msg_box.setWindowTitle("提示")
        msg_box.setText("软件已在运行 ^_^")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.addButton("确定", QMessageBox.YesRole)
        msg_box.exec()
        sys.exit(-1)
    if share.create(1):
        translator = QtCore.QTranslator()
        translator.load('qt_zh_CN.qm')
        app.installTranslator(translator)
        success = checkInitFiles()
        if not success:
            app.exit(0)
            sys.exit(0)
        reg = Register()
        ok = reg.checkAuthored()
        if not ok:
            app.exit(0)
            sys.exit(0)
        from Output_Main_Methods3 import OutputMainWindow
        mainwindow = OutputMainWindow()
        mainwindow.show()
        # print('here')
        sys.exit(app.exec_())


if __name__ == '__main__':
    '''while True:
        Y = input('是否启动项目管理窗口？\n确认请输入Y\n')
        if Y == 'N': exit()
        elif Y == 'Y': break
        else:
            print('输入错误，确认请输入Y')
            continue'''
    try:
        main()
    except SystemExit as s:
        print('SystemExit:',s)
        # global_logger.exception("使用logging exception 函数直接输出异常堆栈:\n {}\n".format(s))
    except KeyboardInterrupt:
        raise
    except Exception as e:
        s = traceback.format_exc()
        print('Exception caught')
        # 使用 logging + traceback 模块输出异常
        global_logger.info("使用 traceback 输出异常:\n {}".format(s))
        # 使用 logging 自定义参数输出异常
        # global_logger.error("使用 logging error 参数 exc_info=True 输出异常:", exc_info=True)
        # 也可以直接使用 logging 的 exception 函数输出异常堆栈信息
        # global_logger.exception("使用logging exception 函数直接输出异常堆栈:\n {}\n".format(e))
    except:
        print('Error caught')
        s = traceback.format_exc()
        # 使用 logging + traceback 模块输出异常
        global_logger.info("仅 traceback 捕获异常:\n {}".format(s))
    finally:
        print('Error caught but unhandled')
