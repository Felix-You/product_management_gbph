import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from MissionDialog import Ui_Dialog
from RedefinedWidget import  MySlider

class QTextEdit(QTextEdit):
    DoubleClicked = pyqtSignal()
    LoseFocus = pyqtSignal()

    def __init__(self, txt=None):
        super().__init__()
        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical {"
                                               "width: 4px;"
                                               "background: transparent;"
                                               "border: 0px;"
                                               "margin: 0px 0px 0px 0px;"
                                               "}"
                                               "QScrollBar::handle:vertical"
                                               "{"
                                               "background:silver;"
                                               "border-radius:2px;"
                                               "}"
                                               "QScrollBar::handle:vertical:hover"
                                               "{"
                                               "background:lightskyblue;"
                                               "border-radius:2px;"
                                               "}"
                                               "QScrollBar::add-line:vertical"
                                               "{"
                                               "background: transparent;"
                                               "margin: 0px;"
                                               "border-width: 0px;"
                                               "height:0px;width:0px;"
                                               "subcontrol-position:bottom;"
                                               "subcontrol-origin: margin;"
                                               "}"
                                               "QScrollBar::sub-line:vertical"
                                               "{"
                                               "background: transparent;"
                                               "margin: 0px;"
                                               "border-width: 0px;"
                                               "height:0px;width:0px;"
                                               "subcontrol-position:top;"
                                               "subcontrol-origin: margin;"
                                               "}")
        if txt != None:
            self.setText(txt)

    # 重写鼠标双击事件
    def mouseDoubleClickEvent(self, e):  # 重写双击事件
        self.DoubleClicked.emit()

    def focusOutEvent(self, e):  # 重写失去焦点事件
        self.LoseFocus.emit()


class logEditDialog(QDialog, Ui_Dialog):
    mySignal = pyqtSignal(tuple)

    def reject(self):  # QDialog在Esc按键后调用的函数
        if False:
            QDialog.reject()

    def __init__(self, argv:tuple,textBody='', currentPoint: int = 0, parent=None):
        super(logEditDialog, self).__init__(parent)
        self.allowInsert = True
        self.combinedStatus = argv#获取任务的status元组
        self.currentPoint_cache = currentPoint
        self.currentPoint = currentPoint
        self.Log = logBody(textBody)
        self.Log.parseText()
        self.setupUi(self)
        if self.combinedStatus[0] == 2:#状态2代表预期订单
            self.checkBox.setChecked(True)
            self.groupBox_4.setStyleSheet("background:rgb(250,220,200)")
        self.checkBox.clicked.connect(self.setOrderColour)
        self.checkBox_2.setChecked(self.combinedStatus[1])
        self.checkBox_3.setChecked(self.combinedStatus[3])
        self.pushButton.clicked.connect(self.addNewLog)
        self.pushButton_2.clicked.connect(self.deleteLog)
        self.pushButton_3.setEnabled(self.allowInsert)
        self.pushButton_3.clicked.connect(self.insertNewLog)
        self.pushButton_4.clicked.connect(self.resetAll)

        self.is_mission_mode = True
        if self.currentPoint > len(self.Log.history_log):  # 修正currentPoint越界错误
            print('Error: currentPoint越界')
            #print(self.Log.history_log)
            self.currentPoint = len(self.Log.history_log)
            self.currentPoint_cache = self.currentPoint
        else:
            pass
        #设置单选框
        switchCase = {'A':lambda :self.radioButton.setChecked(True),
                     'B':lambda :self.radioButton_2.setChecked(True),
                     'C':lambda :self.radioButton_3.setChecked(True),
                     'D':lambda :self.radioButton_4.setChecked(True),
                     'E':lambda :self.radioButton_5.setChecked(True)}
        switchCase[self.combinedStatus[2]]()
        self.initTable()

    def setOrderColour(self):
        if self.checkBox.isChecked():
            self.groupBox_4.setStyleSheet('background:rgb(250,220,200)')
        else:
            self.groupBox_4.setStyleSheet('background:transparent')

    def initTable(self):
        logHeader = ['记录时间', '记录内容']
        self.tableWidget.setRowCount(len(self.Log.history_log))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(logHeader)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 380)
        self.tableWidget.verticalHeader().setDefaultSectionSize(70)
        self.tableWidget.scrollToBottom()
        # self.tableWidget.setShowGrid(False)
        # 绘制表格界面
        for i in range(len(self.Log.history_log)):
            time_text = '<span style="font-size:13px;"> %s </span>' % self.Log.history_log[i][0]
            textedit1 = QTextEdit(time_text)
            textedit1.setReadOnly(True)
            if self.is_mission_mode:
                textedit1.DoubleClicked.connect(self.changeCurrentPoint)
            textedit2 = QTextEdit(self.Log.history_log[i][1])
            textedit2.setReadOnly(True)
            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            self.tableWidget.setCellWidget(i, 0, textedit1)
            self.tableWidget.setCellWidget(i, 1, textedit2)
        if self.is_mission_mode:
            try:
                self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet('background:yellow')
            except:  # 任务记录不存在的情况
                pass

    def closeEvent(self, QCloseEvent):
        # 处理当前正在编辑状态的文本框
        i = self.tableWidget.currentRow()
        if i == -1:
            pass
        else:
            time0 = self.Log.history_log[i][0]
            logUnit_text = self.tableWidget.cellWidget(i, 1).toPlainText()
            self.Log.history_log[i] = (time0, logUnit_text)
        X = ''#获取单选框的值
        for j in range(5):
            if self.groupBox_2.findChildren(QRadioButton)[j].isChecked():
                X = "ABCDE"[j]
        #print(self.groupBox_2.findChildren(QRadioButton))
        self.combinedStatus = (2 if self.checkBox.isChecked() else self.combinedStatus[0],#状态2代表预期订单
                               self.checkBox_2.isChecked(),
                               X,
                               self.checkBox_3.isChecked())
        self.sendLogTextBody()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def sendLogTextBody(self):  # 向上级窗体传值
        self.Log.newTextBody()
        content = (self.Log.textBody, self.currentPoint, self.combinedStatus)
        self.mySignal.emit(content)  # 发射信号

    def changeCurrentPoint(self):  # 重设当前任务标号
        self.pushButton_4.setEnabled(True)
        # 将原任务改透明
        self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet('background:transparent')
        # 获取当前任务标号
        self.currentPoint = self.tableWidget.currentRow() + 1
        # 将当前任务标黄
        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 0).setStyleSheet('background:yellow')

    def setPostponeEdit(self):
        textedit = QTextEdit(self.groupBox_3)
        textedit.setGeometry(10,10,20,20)
        slider = MySlider(self)
        slider.setGeometry()

    def set_Editable(self):
        sender = self.sender()
        sender.setReadOnly(False)

    def set_ReadOnly(self):
        self.pushButton_4.setEnabled(True)
        i = self.tableWidget.currentRow()
        if i == -1: return
        sender = self.sender()
        print(sender)
        sender.setReadOnly(True)
        time0 = self.Log.history_log[i][0]
        logUnit_text = self.tableWidget.cellWidget(i, 1).toPlainText()
        self.Log.history_log[i] = (time0, logUnit_text)

    def insertNewLog(self):
        i = self.tableWidget.currentRow()
        if i == -1:#未有选中的行
            return
        self.pushButton_4.setEnabled(True)
        if self.is_mission_mode and i < self.currentPoint:
            self.currentPoint += 1
        self.tableWidget.insertRow(i)
        now = time.time()
        time_local = time.localtime(now)
        # 转换成新的时间格式
        time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        new_log = (time0, '')
        time_text = '<span style="font-size:13px;"> %s </span>' % time0
        textedit1 = QTextEdit(time_text)
        textedit2 = QTextEdit()
        textedit1.setReadOnly(True)
        textedit2.setReadOnly(True)
        if self.is_mission_mode:
            textedit1.DoubleClicked.connect(self.changeCurrentPoint)
        textedit2.DoubleClicked.connect(self.set_Editable)
        textedit2.LoseFocus.connect(self.set_ReadOnly)
        textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        self.tableWidget.setCellWidget(i, 0, textedit1)
        self.tableWidget.setCellWidget(i, 1, textedit2)
        self.Log.insertLog(i, new_log)

    def addNewLog(self):
        self.pushButton_4.setEnabled(True)
        tableRowCount = self.tableWidget.rowCount()
        self.tableWidget.insertRow(tableRowCount)
        # 获取当前时间
        now = time.time()
        time_local = time.localtime(now)
        time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式
        # 文本框设定
        new_log = (time0, '')
        time_text = '<span style="font-size:13px;"> %s </span>' % time0
        textedit1 = QTextEdit(time_text)
        textedit2 = QTextEdit()
        textedit1.setReadOnly(True)
        textedit2.setReadOnly(True)
        if self.is_mission_mode:
            textedit1.DoubleClicked.connect(self.changeCurrentPoint)
            if len(self.Log.history_log) == 0:  # 原先没有任务记录的情况
                self.currentPoint = 1
                textedit1.setStyleSheet('background:yellow;border-width:0;border-style:outset')
        else:
            textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        textedit2.DoubleClicked.connect(self.set_Editable)
        textedit2.LoseFocus.connect(self.set_ReadOnly)
        textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')

        self.tableWidget.setCellWidget(tableRowCount, 0, textedit1)
        self.tableWidget.setCellWidget(tableRowCount, 1, textedit2)
        self.Log.newLog(new_log)

    def resetAll(self):
        do_or_not = QMessageBox.question(self, "复位", "提示：是否复位记录？\n该动作不可撤销！",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # print(save_or_not)
        if do_or_not == 65536:
            return
        self.pushButton_4.setEnabled(False)
        self.currentPoint = self.currentPoint_cache
        self.Log.history_log = []
        self.Log.parseText()
        self.tableWidget.setRowCount(len(self.Log.history_log))
        for i in range(len(self.Log.history_log)):
            time_text = '<span style="font-size:13px;"> %s </span>' % self.Log.history_log[i][0]
            textedit1 = QTextEdit(time_text)
            textedit1.setReadOnly(True)
            if self.is_mission_mode:
                textedit1.DoubleClicked.connect(self.changeCurrentPoint)
            textedit2 = QTextEdit(self.Log.history_log[i][1])
            textedit2.setReadOnly(True)
            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            self.tableWidget.setCellWidget(i, 0, textedit1)
            self.tableWidget.setCellWidget(i, 1, textedit2)

        if self.is_mission_mode:
            try:
                self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet('background:yellow')
            except:  # 任务记录不存在的情况
                pass

    def deleteLog(self):
        self.pushButton_4.setEnabled(True)
        i = self.tableWidget.currentRow()
        if i == -1: return
        del_or_not = QMessageBox.question(self, "删除记录", "提示：是否删除记录？\n该动作不可撤销！",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # print(save_or_not)
        if del_or_not == 65536:
            return
        else:

            self.tableWidget.removeRow(i)
            self.Log.history_log.pop(i)
            # 处理currentPoint
            if self.is_mission_mode == False:
                return
            if i < self.currentPoint - 1:  # 删currentPoint前面的记录
                self.currentPoint -= 1
            elif i == self.currentPoint - 1 and self.currentPoint - 1 == len(
                    self.Log.history_log):  # currentPoint成为显示表格最后一行
                self.currentPoint -= 1
            else:
                pass
            if self.currentPoint == 0:
                return
            else:
                self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet(
                    'background:yellow;border-width:0;border-style:outset')


class logBody(object):
    def __init__(self, textBody: str):
        self.textBody = textBody
        self.history_log = []

    def newLog(self, logUnit: tuple):  # 在记录中增加一条新记录
        self.history_log.append(logUnit)

    def insertLog(self, index: int, logUnit: tuple):
        self.history_log.insert(index, logUnit)

    def newLogBody(self, tableWidget: QTableWidget):  # 从对话框中的表格新内容更新记录信息
        new_log_body = []
        rowCount = tableWidget.rowCount()
        for i in range(rowCount):
            time0 = tableWidget.cellWidget(i, 0).toPlainText()
            logUnit_text = tableWidget.cellWidget(i, 1).toPlainText()
            new_log_body.append((time0, logUnit_text))
        self.history_log = new_log_body

    def newTextBody(self):
        text_body = ''
        for logUnit in self.history_log:
            timeArray = time.strptime(logUnit[0], "%Y-%m-%d %H:%M:%S")  # 转化成时间数组
            timestamp = time.mktime(timeArray)
            logUnit_text = '<log>' + '<ts>' + str(timestamp) + '</ts>' + str(logUnit[1]) + '</log>'
            text_body = text_body + logUnit_text
        self.textBody = text_body

    def parseText(self):  # 解析单元格内容
        text = str(self.textBody)
        # print('读取', text)
        tmp_list = text.split('<log>')
        # print('分割记录', tmp_list)
        for tmp in tmp_list:  # 遍历初步分割的记录列表
            if tmp in ['', 'nan']: continue
            tmp_1 = tmp.replace('</log>', '')  # 清理单条记录
            if tmp_1.find('<ts>') == -1:  # 处理没有时间的记录
                self.history_log.append(('2020-01-01 00:00:00', tmp_1))
            else:  # 处理包含时间的记录
                tmp_1_list = tmp_1.split('</ts>')
                timestamp0 = float(tmp_1_list[0].replace('<ts>', ''))
                time_local = time.localtime(timestamp0)
                # 转换成新的时间格式
                time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                self.history_log.append((time0, tmp_1_list[1]))


class logEditSimpleDialog(QDialog):
    mySignal = pyqtSignal(tuple)

    def reject(self):  # QDialog在Esc按键后调用的函数
        if False:
            QDialog.reject()

    def __init__(self, textBody='', allowInsert=False, currentPoint: int = None, parent=None):
        super(logEditSimpleDialog, self).__init__(parent)
        self.Log = logBody(textBody)
        self.allowInsert = allowInsert
        self.currentPoint_cache = currentPoint
        self.currentPoint = currentPoint
        self.Log.parseText()
        if self.currentPoint == None:  # 判断是否是在任务模式下调用此对话窗口
            self.is_mission_mode = False
        else:
            self.is_mission_mode = True
            if self.currentPoint > len(self.Log.history_log):  # 修正currentPoint越界错误
                print('Error: currentPoint越界')
                print(self.Log.history_log)
                self.currentPoint = len(self.Log.history_log)
                self.currentPoint_cache = self.currentPoint
            else:
                pass

        self.initUI()

    def initUI(self):
        self.move(560, 200)
        self.setMinimumSize(480, 450)
        self.setWindowTitle('历史记录')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.tableWidget = QTableWidget()
        self.tableWidget.verticalHeader().setVisible(False)
        self.layout.addWidget(self.tableWidget, 1)
        self.layout_1 = QGridLayout()
        self.layout_1.setHorizontalSpacing(2)
        self.layout_1.setVerticalSpacing(2)
        self.layout.addLayout(self.layout_1)
        self.btn1 = QPushButton('新增记录')
        self.btn1.setFixedSize(150, 30)
        self.btn1.clicked.connect(self.addNewLog)
        self.btn2 = QPushButton('插入记录')
        self.btn2.setFixedSize(150, 30)
        self.btn2.setEnabled(self.allowInsert)
        self.btn2.clicked.connect(self.insertNewLog)
        self.btn3 = QPushButton('删除记录')
        self.btn3.setFixedSize(150, 30)
        self.btn3.clicked.connect(self.deleteLog)
        self.btn4 = QPushButton('复位')
        self.btn4.setFixedSize(150, 30)
        self.btn4.clicked.connect(self.resetAll)
        self.btn4.setEnabled(False)
        self.layout_1.addWidget(self.btn1, 0, 0, 1, 1)
        self.layout_1.addWidget(self.btn2, 0, 1, 1, 1)
        self.layout_1.addWidget(self.btn3, 1, 0, 1, 1)
        self.layout_1.addWidget(self.btn4, 1, 1, 1, 1)
        logHeader = ['记录时间', '记录内容']
        # print(self.Log.history_log)
        self.tableWidget.setRowCount(len(self.Log.history_log))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(logHeader)
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 350)
        self.tableWidget.verticalHeader().setDefaultSectionSize(70)
        self.tableWidget.scrollToBottom()
        # self.tableWidget.setShowGrid(False)
        # 绘制表格界面
        for i in range(len(self.Log.history_log)):
            time_text = '<span style="font-size:13px;"> %s </span>' % self.Log.history_log[i][0]
            textedit1 = QTextEdit(time_text)
            textedit1.setReadOnly(True)
            if self.is_mission_mode:
                textedit1.DoubleClicked.connect(self.changeCurrentPoint)
            textedit2 = QTextEdit(self.Log.history_log[i][1])
            textedit2.setReadOnly(True)
            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            self.tableWidget.setCellWidget(i, 0, textedit1)
            self.tableWidget.setCellWidget(i, 1, textedit2)
        if self.is_mission_mode:
            try:
                self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet('background:yellow')
            except:  # 任务记录不存在的情况
                pass

    def closeEvent(self, QCloseEvent):
        # 处理当前正在编辑状态的文本框
        i = self.tableWidget.currentRow()
        if i == -1:
            pass
        else:
            time0 = self.Log.history_log[i][0]
            logUnit_text = self.tableWidget.cellWidget(i, 1).toPlainText()
            self.Log.history_log[i] = (time0, logUnit_text)
        self.sendLogTextBody()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def sendLogTextBody(self):  # 向上级窗体传值
        self.Log.newTextBody()
        content = (self.Log.textBody, self.currentPoint)
        self.mySignal.emit(content)  # 发射信号

    def changeCurrentPoint(self):  # 重设当前任务标号
        self.btn4.setEnabled(True)
        # 将原任务改透明
        self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet('background:transparent')
        # 获取当前任务标号
        self.currentPoint = self.tableWidget.currentRow() + 1
        # 将当前任务标黄
        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 0).setStyleSheet('background:yellow')

    def set_Editable(self):
        sender = self.sender()
        sender.setReadOnly(False)

    def set_ReadOnly(self):
        self.btn4.setEnabled(True)
        i = self.tableWidget.currentRow()
        if i == -1: return
        sender = self.sender()
        print(sender)
        sender.setReadOnly(True)
        time0 = self.Log.history_log[i][0]
        logUnit_text = self.tableWidget.cellWidget(i, 1).toPlainText()
        self.Log.history_log[i] = (time0, logUnit_text)

    def insertNewLog(self):
        i = self.tableWidget.currentRow()
        self.btn4.setEnabled(True)
        if self.is_mission_mode and i < self.currentPoint:
            self.currentPoint += 1
        self.tableWidget.insertRow(i)
        now = time.time()
        time_local = time.localtime(now)
        # 转换成新的时间格式
        time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        new_log = (time0, self.textedit.toPlainText())
        time_text = '<span style="font-size:13px;"> %s </span>' % time0
        textedit1 = QTextEdit(time_text)
        textedit2 = QTextEdit()
        textedit1.setReadOnly(True)
        textedit2.setReadOnly(True)
        if self.is_mission_mode:
            textedit1.DoubleClicked.connect(self.changeCurrentPoint)
        textedit2.DoubleClicked.connect(self.set_Editable)
        textedit2.LoseFocus.connect(self.set_ReadOnly)
        textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        self.tableWidget.setCellWidget(i, 0, textedit1)
        self.tableWidget.setCellWidget(i, 1, textedit2)
        self.Log.insertLog(i, new_log)

    def addNewLog(self):
        self.btn4.setEnabled(True)
        tableRowCount = self.tableWidget.rowCount()
        self.tableWidget.insertRow(tableRowCount)
        # 获取当前时间
        now = time.time()
        time_local = time.localtime(now)
        time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式
        # 文本框设定
        new_log = (time0, '')
        time_text = '<span style="font-size:13px;"> %s </span>' % time0
        textedit1 = QTextEdit(time_text)
        textedit2 = QTextEdit()
        textedit1.setReadOnly(True)
        textedit2.setReadOnly(True)
        if self.is_mission_mode:
            textedit1.DoubleClicked.connect(self.changeCurrentPoint)
            if len(self.Log.history_log) == 0:  # 原先没有任务记录的情况
                self.currentPoint = 1
                textedit1.setStyleSheet('background:yellow;border-width:0;border-style:outset')
        else:
            textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        textedit2.DoubleClicked.connect(self.set_Editable)
        textedit2.LoseFocus.connect(self.set_ReadOnly)
        textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')

        self.tableWidget.setCellWidget(tableRowCount, 0, textedit1)
        self.tableWidget.setCellWidget(tableRowCount, 1, textedit2)
        self.Log.newLog(new_log)

    def resetAll(self):
        do_or_not = QMessageBox.question(self, "复位", "提示：是否复位记录？\n该动作不可撤销！",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # print(save_or_not)
        if do_or_not == 65536:
            return
        self.btn4.setEnabled(False)
        self.currentPoint = self.currentPoint_cache
        self.Log.history_log = []
        self.Log.parseText()
        self.tableWidget.setRowCount(len(self.Log.history_log))
        for i in range(len(self.Log.history_log)):
            time_text = '<span style="font-size:13px;"> %s </span>' % self.Log.history_log[i][0]
            textedit1 = QTextEdit(time_text)
            textedit1.setReadOnly(True)
            if self.is_mission_mode:
                textedit1.DoubleClicked.connect(self.changeCurrentPoint)
            textedit2 = QTextEdit(self.Log.history_log[i][1])
            textedit2.setReadOnly(True)
            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            self.tableWidget.setCellWidget(i, 0, textedit1)
            self.tableWidget.setCellWidget(i, 1, textedit2)

        if self.is_mission_mode:
            try:
                self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet('background:yellow')
            except:  # 任务记录不存在的情况
                pass

    def deleteLog(self):
        self.btn4.setEnabled(True)
        i = self.tableWidget.currentRow()
        if i == -1: return
        del_or_not = QMessageBox.question(self, "删除记录", "提示：是否删除记录？\n该动作不可撤销！",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # print(save_or_not)
        if del_or_not == 65536:
            return
        else:

            self.tableWidget.removeRow(i)
            self.Log.history_log.pop(i)
            # 处理currentPoint
            if self.is_mission_mode == False:
                return
            if i < self.currentPoint - 1:  # 删currentPoint前面的记录
                self.currentPoint -= 1
            elif i == self.currentPoint - 1 and self.currentPoint - 1 == len(
                    self.Log.history_log):  # currentPoint成为显示表格最后一行
                self.currentPoint -= 1
            else:
                pass
            if self.currentPoint == 0:
                return
            else:
                self.tableWidget.cellWidget(self.currentPoint - 1, 0).setStyleSheet(
                    'background:yellow;border-width:0;border-style:outset')

def getDialogSignal(content):#接收下级窗体的返回值
    dialog_return_content = content
    print(content)
if __name__ == "__main__":
    mission = '<log><ts>1613727811.0</ts>一次性进口批件拿到;>fff</log><log><ts>1613727667.0</ts>长期供货协议弄好</log>'
    combinedStatus = (True,False,'B',False)
    app = QApplication(sys.argv)
    mainwindow = QMainWindow(parent=None)
    mainwindow.setObjectName("MainWindow")
    mainwindow.resize(887, 600)
    centralwidget = QWidget(mainwindow)
    centralwidget.setObjectName("centralwidget")
    mainwindow.show()
    dialog = logEditDialog(combinedStatus,textBody=mission,currentPoint=2,parent=mainwindow)
    #dialog.show()
    dialog.mySignal.connect(getDialogSignal)
    dialog.exec_()
    sys.exit(app.exec_())
