from functools import partial

import RedefinedWidget
from apps.ProjectPerspective import CheckPointEditor
from apps.ProjectPerspective.CheckPointEditor import CheckpointEditor
from apps.ProjectPerspective.CheckPointEditorView import CheckPointTableWidgetPop
from core.KitModels import CheckPoint, Person, PersonLog
from projectTabBarUi import Ui_projectTabBar
from PyQt5.QtWidgets import QTabBar, QTextEdit , QMessageBox,QTableWidget,QSlider,QItemDelegate,QRadioButton,QAction, QStyledItemDelegate,QWidget
from PyQt5.QtCore import pyqtSignal, Qt, QEvent, QObject, QTimer, QSize, QRect
from PyQt5.QtGui import QColor, QPainter, QPolygon, QMouseEvent, QFocusEvent, QKeyEvent, QStandardItemModel,\
    QStandardItem, QFontMetrics, QFont
from PyQt5 import QtGui
import ConnSqlite as CS
import math,time,types,datetime
from DataCenter import GTaskCmd,TaskType,GMemoCmd,GProjectCmd,GMeetingCmd,BroadcastSpace, progress_code ,progress_code_r

from ID_Generate import Snow
from projectTabBarUi import QtWidgets
from RedefinedWidget import VectorEditTable,ComboBoxDialog
import GColour, DataView,json,DataCenter
'''
#this part is for Ui # well, No longer needed

from PyQt5.QtCore import pyqtSignal
class MyTableWidget(QtWidgets.QTableWidget):
    FocusIn = pyqtSignal()
    def focusInEvent(self, e: QtGui.QFocusEvent) -> None:
        self.FocusIn.emit()'''
def styleBackgoundColour(colour:tuple) :
    return "background:rgb%s"%str(colour)

class MyTextEdit(QTextEdit):
    DoubleClicked = pyqtSignal(int)
    Clicked = pyqtSignal(int)
    LoseFocus = pyqtSignal(int,str)
    def __init__(self, txt=None,parent = None):
        super().__init__(parent)
        self.parent = parent
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
        self.has_focus = False#手动记录本控件在被点击前是否有焦点（setFocus函数会在mousePressEvent之前自动执行，所以会产生干扰）
        self.recatch_focus = False
        self._row_locate = None#自身所在行号
        self._log_id = None#自身内容所来自的记录的id
        self._log_type = None
        self._log_type_2 = None
        self.clicked = False
        self.edited = False# 每次给textEdit赋值之后都要恢复成False，因为这个参数是用来作为判断FocusOut信号的槽函数是否执行的的条件
        self.init_text = ''
        self.textChanged.connect(self.setEdited)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_rightMenu)

        if txt != None:
            self.setText(txt)

    def setEdited(self):
        if self.has_focus:#具有焦点，即主观认为焦点应该在当前控件上
            self.edited = True

    def setText(self, txt):
        self.init_text = txt
        if self._log_type_2 == 'task_update':
            txt = DataCenter.convert_date_log_json(txt)
        super(MyTextEdit, self).setText(txt)
        self.edited = False# 每次给textEdit赋值之后都要恢复成False，因为这个参数是用来作为判断FocusOut信号的槽函数是否执行的的条件

    @property
    def row_locate(self):
        return self._row_locate

    @row_locate.setter
    def row_locate(self, r: int):
        self._row_locate = r

    @property
    def log_id(self):
        return self._log_id

    @log_id.setter
    def log_id(self,_id):
        self._log_id = _id

    @property
    def log_type(self):
        return self._log_type

    @log_type.setter
    def log_type(self, t:str):
        self._log_type = t

    @property
    def log_type_2(self):
        return self._log_type_2

    @log_type_2.setter
    def log_type_2(self, t:str):
        self._log_type_2 = t

    def increaseRowLocate(self):
        self._row_locate += 1

    def decreaseRowLocate(self):
        self._row_locate -= 1

    def mouseDoubleClickEvent(self, e):  # 重写双击事件
        # print(e.type(),e.button())
        # self.edited = True
        self.DoubleClicked.emit(self._row_locate)
        pass

    def mousePressEvent(self, e):
        # print(e.type(),e.button())
        self.clicked = True#这个参数是要在mousePressEvent触发的发生focusOut的时候起作用，所以要在这个函数结束时复原
        #当上层控件在被点击前没有焦点时，焦点向下穿透再回来，这个时候has_focus为True
        if self.has_focus:#当前本控件已经在焦点上。此处的焦点为自定义的虚拟焦点，
            # print('穿透未执行,has_focus={},recatch_focus={}'.format(self.has_focus,self.recatch_focus))
            pass
        else:
            if self.parentWidget():
                self.parentWidget().setFocus()
                # parent = self.parent()
                # parent2 = self.nativeParentWidget()
                # parent3 = self.parentWidget()
                self.recatch_focus = False
        self.has_focus = True
        self.clicked = False
        # if self.parentWidget():
        #     self.parentWidget().setFocus()
        self.setFocus()
        self.Clicked.emit(self._row_locate)
        super(MyTextEdit, self).mousePressEvent(e)#mousePressEvent()和setFocus()是分开独立执行的，一次点击事件中，
        # if self.parentWidget():#将自己设为鼠标事件透明并重新搜索是否有后面的控件会响应鼠标事件。
        #     self.setAttribute(Qt.WA_TransparentForMouseEvents)
        #     point = self.mapTo(self.parentWidget(),e.pos())#将鼠标点击位置转变为相对父控件的位置
        #     w = self.parentWidget().childAt(point)#判断父控件在该位置是否还有其他控件
        #     if w:
        #         point  = w.mapFrom(self.parentWidget(),point)#将该控件相对于父控件的位置，转换为全局位置
        #         event = QtGui.QMouseEvent(e.type(), point, e.button(),e.buttons(),e.modifiers())#重新合成鼠标事件
        #         QtWidgets.QApplication.postEvent(w, event)
        #     self.setAttribute(Qt.WA_TransparentForMouseEvents,False)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Escape:
            self.setText(self.init_text)
            self.edited = False # 避免FocusOut信号触发保存操作
            self.clearFocus()
        QTextEdit.keyPressEvent(self, e)

    def event(self,e):
        # if isinstance(e,QMouseEvent):
        #     if e.button() == Qt.RightButton:
        #         print(e.type(),'rightbutton')
        #     self.setReadOnly(False)
        #     return True
        return QTextEdit.event(self,e)

    def focusOutEvent(self, e):  # 重写失去焦点事件
        if e.reason() == Qt.PopupFocusReason:
            return
        if self.clicked == False:# 失去焦点不是因为点击自身的焦点穿透事件造成，而是鼠标点击其他控件，has_focus置为False
            self.has_focus = False
        #信号返回自身所在行号
        self.LoseFocus.emit(self._row_locate,self._log_type)#用于保存当前修改
        self.edited = False
        QTextEdit.focusOutEvent(self, e)

    def show_rightMenu(self):
        self.showRightMenu()

    def showRightMenu(self):
        text = self.textCursor().selectedText()
        self.parent.showRightMenu(log_type=self.log_type, text=text, text_pad=self)
        # if not text:
        #     copyAction.setEnabled(False)
        # show the menu
        # res = menu.exec_(QtGui.QCursor.pos())
        # if res == copyAction:
        #     # if the menu has been triggered by the action, copy to the clipboard
        #     QtWidgets.QApplication.clipboard().setText(text)

chosen_task_style = 'QTextEdit{background:rgba(240,245,255,100);border-width:2;border-radius:6;border-color:rgb(100,110,120);border-style:outset}'

def _calcuRowHeight_old_(text:str,text_height: int=16, column_text_length:int = 21):
    '''
    根据需要输入的文本自动计算文字在表格中需要占据的行高
    :param text: 文本内容
    :param text_height:一行文字的高度
    :param column_text_length: 一行文字的字数
    :return:
    '''
    if not text :
        return 30# 最小高度
    text_rows = math.ceil(len(text) / column_text_length)
    br_rows = text.count('\n')
    if br_rows > text_rows :
        row_height = br_rows * text_height
    else:
        row_height = (br_rows+ (lambda: text_rows if br_rows == 0 else math.floor(1.2*text_rows/br_rows))()) * text_height#估算值
    row_height += 24 #高度基础修正值
    if row_height > 120 : row_height = 120
    return row_height

def calcuRowHeight(text_edit:MyTextEdit, text_width):
    # text_width_0 = text_edit.document().textWidth()
    init_width = text_edit.width()
    text = text_edit.toPlainText()
    document = QtGui.QTextDocument(text)
    document.setTextWidth(text_width)
    document_height = document.size().height()
    document_width = document.size().width()
    init_height = text_edit.height()
    text_edit.document().setTextWidth(100)
    text_width_1 = text_edit.document().textWidth()
    # text_height = text_edit.document()

    height = text_edit.document().size().height() + 3
    width = text_edit.document().size().width()
    return int(max(43*DataView.DF_Ratio,(min(document_height+ 3*DataView.DF_Ratio, 120*DataView.DF_Ratio))))# 行高应该介于45~120之间

def new_mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        QSlider.mousePressEvent(self, event )  # 调用父级的单击事件，听说这样能不影响进度条原来的拖动
        val_por = event.pos().x() / self.width()  # 获取鼠标在进度条的相对位置
        self.setValue( round(val_por * self.maximum()) )  # 改变进度条的值
        # self.cliecked.emit(self.value())	# 点击发送信号，这里可不要

class ProjectTabBar(QTabBar,Ui_projectTabBar):
    tableWidgetFocusIn = pyqtSignal()
    tableWidgetFocusOut = pyqtSignal()
    STATUS = {0:'未办',
              1:'进行',
              2:'完成',
              3:'关闭'}
    def tableWidgetFocusInEvent(self, child, e: QFocusEvent) -> None:
        #此方法用于覆盖子控件类的类方法。self是主窗口类，child是被覆盖的类
        self.tableWidgetFocusIn.emit()
        # print('child',child,'self.focusTable',self.focusTable)
        if not self.focusTable is child:
            self.focusTable.selectionModel().clearSelection()
        self.focusTable = child
        QTableWidget.focusInEvent(child,e)

    def setFocusWidget(self, child):
        if not self.focusTable is child:
            self.focusTable.selectionModel().clearSelection()
        self.focusTable = child

    def tableWidgetFocusOutEvent(self, child, e: QFocusEvent) -> None:
        #此方法用于覆盖子控件类的类方法。self是主窗口类，child是被覆盖的类
        self.tableWidgetFocusOut.emit()
        # child.clearSelection()
        QTableWidget.focusOutEvent(child,e)

    def __init__(self,project,parent = None):
        super(ProjectTabBar,self).__init__(parent)
        self.setupUi(self)
        # self.setStyleSheet('QTextEdit {'
        #                            'border-width: 1px;'
        #                            'border-style: dashed;'
        #                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                            'stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
        self.project = project
        self.parent = parent
        self.logHeader = ['当前任务', '任务内容', '任务进展']
        self.logHeader_2 = ['', '记录内容']
        self.logHeader_3 = ['', '记录内容']
        # self.project.current_task_num = CS.getLinesFromTable('proj_list',conditions={'_id':self.project_id},columns_required=['current_task_num'])[0][0]
        # self.tableWidget.installEventFilter(self)  # 把自己当成一个过滤器安装到儿子身上
        # self.tableWidget_2.installEventFilter(self)
        # self.tableWidget_3.installEventFilter(self)
        self.comboBox_personnel.wheelEvent = types.MethodType(lambda cls,e : e.ignore(), self.comboBox_personnel)
        self.tableWidget.focusInEvent = types.MethodType(self.tableWidgetFocusInEvent, self.tableWidget)
        self.tableWidget_2.focusInEvent = types.MethodType(self.tableWidgetFocusInEvent, self.tableWidget_2)
        self.tableWidget_3.focusInEvent = types.MethodType(self.tableWidgetFocusInEvent, self.tableWidget_3)
        self.tableWidget.setFocusWidget = types.MethodType(self.setFocusWidget, self.tableWidget)
        self.tableWidget_2.setFocusWidget = types.MethodType(self.setFocusWidget, self.tableWidget_2)
        self.tableWidget_3.setFocusWidget = types.MethodType(self.setFocusWidget, self.tableWidget_3)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(lambda: self.showRightMenu('task'))
        self.tableWidget_2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget_2.customContextMenuRequested.connect(lambda: self.showRightMenu('meeting'))
        self.tableWidget_3.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget_3.customContextMenuRequested.connect(lambda: self.showRightMenu('memo'))
        self.tableWidget.cellClicked.connect(self.changeTableFocus)
        self.tableWidget_2.cellClicked.connect(self.changeTableFocus)
        self.tableWidget_3.cellClicked.connect(self.changeTableFocus)

        self.groupBox_6.setStyleSheet('#groupBox_6{border-radius:7;border-width:1;border-style:solid;border-color:rgb(200,200,200);background-color :rgb(235, 235, 200);}'
                                      'QGroupBox{border-radius:10;border-width:1;border-style:solid;border-color:rgb(210,210,220);}')
        self.verticalGroupBox.setStyleSheet('#verticalGroupBox{border-radius:7;border-width:1;border-color:rgb(200,200,200);background-color :rgb(220, 235, 235);}'
                                            'QGroupBox{border-radius:10;border-width:1;border-style:solid;border-color:rgb(210,210,220);}')
        self.groupBox_deal.setStyleSheet('border-radius:10;border-width:1;border-style:solid;border-color:rgb(210,210,220);')

        self.pushButton.clicked.connect(self.addNewLog)
        self.pushButton_2.clicked.connect(self.insertNewLog)
        # self.pushButton_3.clicked.connect(self.deleteLog)
        # self.add_todo_action = QAction(self)
        # self.add_todo_action.setText('新追踪事项..')
        # self.add_todo_action.triggered.connect(self.add_todo_unit)
        # self.toolButton.addAction(self.add_todo_action)
        # self.toolButton.clicked.connect(self.toolButton.showMenu)
        #控制面板信号组
        self.button_order_tobe = RedefinedWidget.SliderButton('预期订单', self.verticalGroupBox,outer_unchecked_alpha=25,
                                                         colorChecked=GColour.ProjectRGBColour.ProjectOrderTobe,outer_checked_alpha=160)
        self.button_in_act = RedefinedWidget.SliderButton('上线跟进', self.verticalGroupBox,outer_unchecked_alpha=25,
                                                     colorChecked=GColour.ProjectRGBColour.ProjectInAct,outer_checked_alpha=160)
        self.button_highlight = RedefinedWidget.SliderButton('高亮关注', self.verticalGroupBox,outer_unchecked_alpha=25,
                                                        colorChecked=GColour.ProjectRGBColour.ProjectHighlight,outer_checked_alpha=160)
        self.button_to_visit = RedefinedWidget.SliderButton('需拜访', self.verticalGroupBox,outer_unchecked_alpha=25,
                                                        colorChecked=GColour.ProjectRGBColour.ProjectToVisit,outer_checked_alpha=160)
        self.button_clear_chance = RedefinedWidget.SliderButton('明确机会', self.verticalGroupBox,outer_unchecked_alpha=25,
                                                        colorChecked=GColour.ProjectRGBColour.ProjectClearChance,outer_checked_alpha=160)
        self.button_task_urgent = RedefinedWidget.SliderButton('紧急', self.groupBox_6,outer_unchecked_alpha=25,
                                                           colorChecked=GColour.TaskColour.TaskIsCritial,outer_checked_alpha=160)
        self.button_is_deal = RedefinedWidget.SliderButton('已成交', None,colorChecked=GColour.ProjectRGBColour.ProjecIsDeal,
                                                           outer_unchecked_alpha=25,outer_checked_alpha=160)
        # self.button_order_tobe.setGeometry(QRect(2, 5, 40 * DataView.FIX_SIZE_WIDGET_SCALING, 20*DataView.FIX_SIZE_WIDGET_SCALING))
        # # self.button_order_tobe.setFixedSize(QSize(40, 20))
        # self.button_in_act.setGeometry(QRect(2, 27, 40, 20))
        # self.button_highlight.setGeometry(QRect(2, 49, 40, 20))
        # self.button_to_visit.setGeometry(QRect(2, 71, 40, 20))
        # self.button_clear_chance.setGeometry(QRect(2, 93, 40, 20))
        # self.button_task_urgent.setGeometry(QRect(2, 5, 40, 20))
        # self.button_is_deal.setGeometry(QRect(2, 5, 40, 20))
        # self.button_order_tobe.setGeometry(QRect(2, 5, 40 * DataView.FIX_SIZE_WIDGET_SCALING, 20*DataView.FIX_SIZE_WIDGET_SCALING))
        from DataView import DF_Ratio
        button_size = QSize(70 * DF_Ratio, 20 * DF_Ratio)
        self.button_order_tobe.setFixedSize(button_size)
        self.button_in_act.setFixedSize(button_size)
        self.button_highlight.setFixedSize(button_size)
        self.button_to_visit.setFixedSize(button_size)
        self.button_clear_chance.setFixedSize(button_size)
        self.button_task_urgent.setFixedSize(button_size)
        self.label_task_status = QtWidgets.QLabel()
        font = QFont()
        # font.setBold(True)
        font.setPointSize(int(8*DF_Ratio))
        font.setFamily('MICROSOFT YAHEI')
        # font.setUnderline(True)
        self.label_task_status.setFont(font)
        self.button_is_deal.setFixedSize(QSize(70 * DF_Ratio, 30 * DF_Ratio))

        self.label_pending_till_date = QtWidgets.QLabel()
        font = QFont()
        font.setPointSize(int(7 * DF_Ratio))
        font.setFamily('MICROSOFT YAHEI')
        self.label_pending_till_date.setFont(font)

        self.button_is_deal.setFixedSize(QSize(70 * DF_Ratio, 30 * DF_Ratio))


        self.verticalGroupBox.layout().insertWidget(0,self.button_order_tobe, 0, Qt.AlignCenter)
        self.verticalGroupBox.layout().insertWidget(1,self.button_clear_chance, 0, Qt.AlignCenter)
        self.verticalGroupBox.layout().insertWidget(2,self.button_in_act, 0, Qt.AlignCenter)
        self.verticalGroupBox.layout().insertWidget(3,self.button_highlight, 0, Qt.AlignCenter)
        self.verticalGroupBox.layout().insertWidget(4,self.button_to_visit, 0, Qt.AlignCenter)
        self.groupBox_status.layout().insertWidget(1,self.label_task_status,0,Qt.AlignCenter)
        self.groupBox_status.layout().insertWidget(2, self.label_pending_till_date, 0, Qt.AlignCenter)
        self.groupBox_status.layout().insertWidget(3, self.button_task_urgent, 0, Qt.AlignCenter)

        self.groupBox_deal.layout().addWidget(self.button_is_deal)
        self.groupBox_deal.layout().setAlignment(self.button_is_deal,Qt.AlignCenter)
        self.button_order_tobe.toggled.connect(self.on_order_tobe)
        self.button_clear_chance.toggled.connect(self.on_clear_chance)
        self.button_in_act.toggled.connect(self.on_in_act)
        self.button_highlight.toggled.connect(self.on_highlight)
        self.button_to_visit.toggled.connect(self.on_to_visit)
        self.verticalLayout_3.setAlignment(self.verticalGroupBox, Qt.AlignCenter)

        self.button_task_urgent.toggled.connect(self.on_task_urgent)
        self.button_is_deal.toggled.connect(self.on_is_deal)

        radioButtons = self.groupBox_7.findChildren(QRadioButton)
        office_job_types = list(DataCenter.office_job_dict.values())
        width = 0
        for i, radioButton in enumerate(radioButtons):
            radioButton.setText(office_job_types[i])

            fM = QFontMetrics(radioButton.font())
            # wid = fM.width()
            wid = fM.boundingRect(radioButton.text()).width()
            width = max(wid, width)
            print(office_job_types[i])
            print(fM)
            print(wid)
            # radioButton.setFixedWidth(wid)

        self.groupBox_7.setMinimumWidth(width + 25)
        self.groupBox_6.setMinimumWidth(width + 35)
        self.verticalGroupBox.setMinimumWidth(width + 35)
        self.radioButton.clicked.connect(self.on_officejob_type)#待办类型
        self.radioButton_2.clicked.connect(self.on_officejob_type)#待办类型
        self.radioButton_3.clicked.connect(self.on_officejob_type)#待办类型
        self.radioButton_4.clicked.connect(self.on_officejob_type)#待办类型
        self.radioButton_5.clicked.connect(self.on_officejob_type)#待办类型


        # self.button_task_urgent.clicked.connect(self.on_)#pending
        # self.lineEdit.editingFinished.connect()
        #ID生成器
        self.LOG_ID = {'task':Snow('ts'),
                       'memo':Snow('mm'),
                       'meeting':Snow('mt')}
        self.BROADCAST_ID = Snow('br')

        self.focusTable = self.tableWidget
        # self.tableWidget = MyTableWidget(self)
        # self.tableWidget_2 = MyTableWidget(self)
        # self.tableWidget_3 =MyTableWidget(self)
        self.initTable()
        self.initTable_2()
        self.initTable_3()
        self.initProjectSet()
        self.initCurrentTaskSet()
        DataView.ResAdaptor.init_ui_size(self)
        # self.groupBox_7.setMaximumHeight(120*DataView.DF_Ratio)
        # self.groupBox_8.setFixedHeight(38 * DataView.ResAdaptor.ratio_height)
        # print('before timer create')

    def eventFilter(self, obj:QtWidgets.QWidget, event):
        #print('event_object',obj)
        #if event.type() == QEvent.MouseButtonPress:

        #if event.type() == QEvent.MouseButtonPress :
        #print('event_in',event.type(),obj.objectName())
        if obj == self.tableWidget or obj == self.tableWidget_2 or obj == self.tableWidget_3:
            if event.type() == QEvent.MouseButtonPress :#and event.key() == Qt.LeftButton:
                obj.setFocus()
                self.focusTable = obj
                print('event_caught')
                # return True  # 说明这个事件已被处理，其他控件别插手
        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def initAllData(self):
        self.initTable()
        self.initTable_2()
        self.initTable_3()
        self.initProjectSet()
        self.initCurrentTaskSet()

    def initTable(self):
        '''tasks读写初始化'''
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(self.logHeader)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0, 84*DataView.DF_Ratio)
        self.tableWidget.setColumnWidth(1, math.floor(295*DataView.DF_Ratio))
        header_view = self.tableWidget.horizontalHeader()
        header_view.setStretchLastSection(True)
        # self.tableWidget.setColumnWidth(2, 180)
        # self.tableWidget.verticalHeader().setDefaultSectionSize(120)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.scrollToBottom()
        # self.task_logs = CS.PdFrame(CS.getLinesFromTable('tasks', conditions={'conn_project_id': self.project_id},order=['inter_order_weight'],ascending=True))
        if not self.project.tasks :
            return
        self.tableWidget.setRowCount(len(self.project.tasks))
        # self.tableWidget.setShowGrid(False)
        # 绘制表格界面
        for i, task in enumerate(self.project.tasks):
            time_text = '<span style="font-size:8pt;"> %s </span>' % task.create_time
            textedit1 = MyTextEdit(time_text,self)
            textedit1.setReadOnly(True)
            textedit1.Clicked.connect(self.changeCurrentTaskNum)
            textedit2 = MyTextEdit(task.task_desc,self)

            textedit2.setReadOnly(True)
            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit2.LoseFocus.connect(self.wrapTaskTextUpdate)
            textedit3 = MyTextEdit(parent=self.tableWidget)
            textedit3.showRightMenu = types.MethodType(lambda tedt3: self.showRightMenu(
                tedt3.log_type, tedt3.textCursor().selectedText(), tedt3), textedit3)
            # textedit3.setText(task.update_desc_list)
            textedit3.setReadOnly(True)
            textedit3.DoubleClicked.connect(self.on_task_update_call)

            # textedit3.showRightMenu = types.MethodType(lambda instance, pos: None , textedit3)

            # textedit3.LoseFocus.connect(self.set_ReadOnly)
            # textedit3.LoseFocus.connect(self.wrapTaskTextUpdate)
            # textedit1.setAttribute(Qt.WA_TransparentForMouseEvents)
            # textedit2.setAttribute(Qt.WA_TransparentForMouseEvents)
            # textedit3.setAttribute(Qt.WA_TransparentForMouseEvents)

            textedit1.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')
            textedit2.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')
            textedit3.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')
            self.tableWidget.setCellWidget(i, 0, textedit1)
            self.tableWidget.setCellWidget(i, 1, textedit2)
            self.tableWidget.setCellWidget(i, 2, textedit3)
            row_height = calcuRowHeight(textedit2, (295-3)*DataView.DF_Ratio)
            self.tableWidget.setRowHeight(i, row_height )
            # 给textEdit的属性赋值
            for j in range(self.tableWidget.columnCount()):
                setattr(self.tableWidget.cellWidget(i,j),'row_locate', i)
                setattr(self.tableWidget.cellWidget(i,j),'log_id', task._id)
                setattr(self.tableWidget.cellWidget(i,j),'log_type', 'task')
                if j == 2:
                    setattr(self.tableWidget.cellWidget(i,j),'log_type_2', 'task_update')
                    self.tableWidget.cellWidget(i,j).setText(task.update_desc_list)
        #设置当前任务为黄色
        self.tableWidget.scrollToBottom()
        if self.project.current_task_num and self.project.tasks:
            if self.project.current_task_num > len(self.project.tasks):
                self.project.current_task_num = len(self.project.tasks)
            self.tableWidget.cellWidget(self.project.current_task_num - 1, 0).setStyleSheet(chosen_task_style)

    def initTable_2(self):
        self.tableWidget_2.clear()
        self.tableWidget_2.setColumnCount(2)
        self.tableWidget_2.setHorizontalHeaderLabels(self.logHeader_2)
        self.tableWidget_2.verticalHeader().setVisible(False)
        self.tableWidget_2.setColumnWidth(0, 84*DataView.DF_Ratio)
        self.tableWidget_2.setColumnWidth(1, 330*DataView.DF_Ratio)
        header_view = self.tableWidget_2.horizontalHeader()
        header_view.setStretchLastSection(True)
        # self.tableWidget_2.verticalHeader().setDefaultSectionSize(120)
        # self.meeting_logs = CS.PdFrame(CS.getLinesFromTable('project_meeting_log', conditions={'conn_project_id': self.project_id},
        #                                                     order=['inter_order_weight'],ascending=True))
        self.tableWidget_2.setRowCount(len(self.project.meeting_log))
        self.tableWidget_2.scrollToBottom()
        # self.tableWidget.setShowGrid(False)
        # 绘制表格界面
        for i, meeting in enumerate(self.project.meeting_log):
            time_text = '<span style="font-size:8pt;"> %s </span>' % meeting.create_time[:19]
            textedit1 = MyTextEdit(time_text,self)
            textedit1.setReadOnly(True)
            textedit2 = MyTextEdit(parent=self)
            textedit2.setReadOnly(True)
            textedit2.setText(meeting.meeting_desc)
            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit2.LoseFocus.connect(self.wrapMeetingTextUpdate)
            # textedit1.setAttribute(Qt.WA_TransparentForMouseEvents)
            # textedit2.setAttribute(Qt.WA_TransparentForMouseEvents)
            textedit1.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')
            textedit2.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')

            self.tableWidget_2.setCellWidget(i, 0, textedit1)
            self.tableWidget_2.setCellWidget(i, 1, textedit2)
            for j in range(self.tableWidget_2.columnCount()):
                setattr(self.tableWidget_2.cellWidget(i,j),'row_locate', i)
                setattr(self.tableWidget_2.cellWidget(i,j),'log_id', meeting._id)
                setattr(self.tableWidget_2.cellWidget(i,j),'log_type', 'meeting')
            row_height = calcuRowHeight(textedit2, (330-3)*DataView.DF_Ratio)
            self.tableWidget_2.setRowHeight(i, row_height if row_height <= 120 else 120)

    def initTable_3(self):
        self.tableWidget_3.clear()
        self.tableWidget_3.setColumnCount(2)
        self.tableWidget_3.setHorizontalHeaderLabels(self.logHeader_3)
        self.tableWidget_3.verticalHeader().setVisible(False)
        self.tableWidget_3.setColumnWidth(0, 84*DataView.DF_Ratio)
        self.tableWidget_3.setColumnWidth(1, 330*DataView.DF_Ratio)
        self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_3.setRowCount(len(self.project.memo_log))
        self.tableWidget_3.scrollToBottom()
        # self.tableWidget.setShowGrid(False)
        # 绘制表格界面
        for i, memo in enumerate(self.project.memo_log):
            time_text = '<span style="font-size:8pt;"> %s </span>' % memo.create_time
            textedit1 = MyTextEdit(time_text,self)
            textedit1.setReadOnly(True)

            textedit2 = MyTextEdit(memo.memo_desc,self)
            textedit2.setReadOnly(True)

            textedit2.DoubleClicked.connect(self.set_Editable)
            textedit2.LoseFocus.connect(self.set_ReadOnly)
            textedit2.LoseFocus.connect(self.wrapMemoTextUpdate)
            # textedit1.setAttribute(Qt.WA_TransparentForMouseEvents)
            # textedit2.setAttribute(Qt.WA_TransparentForMouseEvents)
            textedit1.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')
            textedit2.setStyleSheet('QTextEdit{background:transparent;border-width:0;border-style:outset}')

            self.tableWidget_3.setCellWidget(i, 0, textedit1)
            self.tableWidget_3.setCellWidget(i, 1, textedit2)
            for j in range(self.tableWidget_3.columnCount()):
                setattr(self.tableWidget_3.cellWidget(i,j),'row_locate', i)
                setattr(self.tableWidget_3.cellWidget(i,j),'log_id', memo._id)
                setattr(self.tableWidget_3.cellWidget(i,j),'log_type', 'memo')
            row_height = calcuRowHeight(textedit2, (330-3)*DataView.DF_Ratio)
            self.tableWidget_3.setRowHeight(i, row_height if row_height <= 120 else 120)

    def initProjectSet(self):
        self.button_order_tobe.setChecked(self.project.order_tobe)
        self.button_clear_chance.setChecked(self.project.clear_chance)
        self.button_in_act.setChecked(self.project.in_act)
        self.button_highlight.setChecked(self.project.highlight)
        self.button_to_visit.setChecked(self.project.to_visit)
        self.button_is_deal.setChecked(self.project.is_deal)
        # print('before set')
        self.hSlider_progress.setTickInterval(1)
        self.hSlider_progress.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.hSlider_progress.blockSignals(True)
        self.hSlider_progress.setValue(progress_code[self.project.current_progress])
        self.hSlider_progress.mousePressEvent = types.MethodType(new_mousePressEvent,self.hSlider_progress)
        self.hSlider_progress.setTracking(False)
        self.hSlider_progress.valueChanged.connect(self.on_progress)#机会等级
        self.hSlider_progress.blockSignals(False)
        self.hSlider_progress.wheelEvent = types.MethodType(lambda cls,e : e.ignore(), self.hSlider_progress)
        #初始化机会标签
        tags = list(self.parent.chanceStatusFilter.code_name_dict.items())#获取菜单项
        tags.sort(key =lambda item: item[0])
        tagss = [item[1] for item in tags]
        self.comboBox_chance.blockSignals(True)
        self.comboBox_chance.addItems(tagss)
        self.comboBox_chance.setCurrentIndex(self.project.status_code)
        self.comboBox_chance.wheelEvent = types.MethodType(lambda cls,e : e.ignore(), self.comboBox_chance)
        self.comboBox_chance.currentIndexChanged.connect(self.on_chance_status)#机会等级
        self.comboBox_chance.blockSignals(False)
        #
        self.pushButton_files.clicked.connect(self.on_pushButton_files)
        #
        self.initPricingSet()
        self.initPersonnelSet()
        self.setProjectColour()
        print('after set')
        # self.button_task_urgent.setChecked(self.project.to)
        pass

    def initPricingSet(self):
        self.lineEdit_pricing1.editingFinished.connect(self.on_pricing_edit)
        self.lineEdit_pricing1.setValidator(QtGui.QIntValidator ())
        self.lineEdit_pricing1.setAlignment(Qt.AlignRight)
        p1 = self.project.status.current_pricing
        self.lineEdit_pricing1.setText(str(p1) if p1 else None)

        self.lineEdit_pricing2.editingFinished.connect(self.on_pricing_edit)
        self.lineEdit_pricing2.setValidator(QtGui.QIntValidator ())
        p2 = self.project.status.rival_pricing
        self.lineEdit_pricing2.setText(str(p2) if p2 else None)
        self.lineEdit_pricing2.setAlignment(Qt.AlignRight)
        p3 = self.project.status.deal_price

        self.lineEdit_pricing3.editingFinished.connect(self.on_pricing_edit)
        self.lineEdit_pricing3.setValidator(QtGui.QIntValidator ())
        self.lineEdit_pricing3.setText(str(p3) if p3 else  None)
        # s1 = self.project.status.current_demand
        # self.lineEdit_scale1.setText(str(s1) if s1 else None)
        self.lineEdit_pricing3.setAlignment(Qt.AlignRight)


        self.pushButton_demand.clicked.connect(self.on_pushButton_demand)
        # self.pushButton_ladderpricing.clicked.connect(self.on_pushButton_ladderpricing)
        self.pushButton_rival_disk.clicked.connect(self.on_pushButton_rival_disk)

    def initPersonnelSet(self):
        personnel = CS.getLinesFromTable('clients',{'_id':self.project.client_id},['_id','personnel'])
        personnel.pop()
        if personnel:
            personnel_json = personnel[0][1]
            personnel_data = json.loads(personnel_json) if personnel_json else []
        else:
            personnel_data = []
        self.set_comboBox_personnel(personnel_data)
        self.pushButton_new.clicked.connect(lambda : self.on_editing_personnel(personnel_data))

    def set_comboBox_personnel(self, personnel_data, is_renew = False):
        person_names = []
        person_ids = []
        for item in personnel_data:
            person_names.append(item['name'])
            person_ids.append(item['_id'])
        self.comboBox_personnel.blockSignals(True)
        self.comboBox_personnel.clear()
        self.comboBox_personnel.addItems(person_names)
        #设置负责人
        index = person_ids.index(self.project.status.person_in_charge) if \
            self.project.status.person_in_charge in person_ids else -1#此处校验了list的包含性
        self.comboBox_personnel.setCurrentIndex(index)
        self.comboBox_personnel.blockSignals(False)
        try:#todo:为什么会有异常
            self.comboBox_personnel.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.comboBox_personnel.currentIndexChanged.connect(lambda X: self.on_person_in_charge(X, person_ids))#todo:为什么lambda的参数值不能更新

    def setProjectColour(self):
        # base_background = 'background:transparent'
        # if self.project.order_tobe:
        #     self.groupBox.setStyleSheet(styleBackgoundColour(GColour.ProjectRGBColour.ProjectOrderTobe))
        # else:
        #     self.groupBox.setStyleSheet(base_background)
        # if self.project.clear_chance:
        #     self.groupBox_2.setStyleSheet(styleBackgoundColour(GColour.ProjectRGBColour.ProjectClearChance))
        # else:
        #     self.groupBox_2.setStyleSheet(base_background)
        # if self.project.in_act:
        #     self.groupBox_3.setStyleSheet(styleBackgoundColour(GColour.ProjectRGBColour.ProjectInAct))
        # else:
        #     self.groupBox_3.setStyleSheet(base_background)
        # if self.project.highlight:
        #     self.groupBox_4.setStyleSheet(styleBackgoundColour(GColour.ProjectRGBColour.ProjectHighlight))
        # else:
        #     self.groupBox_4.setStyleSheet(base_background)
        # if self.project.to_visit:
        #     self.groupBox_5.setStyleSheet(styleBackgoundColour(GColour.ProjectRGBColour.ProjectToVisit))
        # else:
        #     self.groupBox_5.setStyleSheet(base_background)
        # if self.project.is_deal:
        #     self.groupBox_deal.setStyleSheet(styleBackgoundColour(GColour.ProjectRGBColour.ProjecIsDeal))
        # else:
        #     self.groupBox_deal.setStyleSheet(base_background)
        pass

    def initCurrentTaskSet(self):
        if not self.project.current_task_num or not self.project.tasks:# 常理来说，这两者应该保持一致，但是在数据库转换过程中可能产生不一致
            return
        current_task = self.project.tasks[self.project.current_task_num - 1]
        is_critical = current_task.is_critical
        status = current_task.status
        destroyed = current_task.destroyed
        pending_till_date = current_task.pending_till_date
        if destroyed:
            status = 3
        # status = current_task.
        if current_task.officejob_type in DataCenter.office_job_dict.keys():
            i = 'ABCDE'.index(current_task.officejob_type)
        else:
            i = 0
        self.groupBox_7.findChildren(QRadioButton)[i].setChecked(True)
        self.button_task_urgent.setChecked(is_critical)
        status_desc = self.STATUS[status] if status else '--'
        self.label_task_status.setText(f'进展：{status_desc}')
        pending_till_date = pending_till_date if pending_till_date else '--'
        self.label_pending_till_date.setText(f'提醒：{pending_till_date}')

    def addNewLog(self):
        tableRowCount = self.focusTable.rowCount()
        log_type = 'task'
        if self.focusTable is self.tableWidget:
            log_type = 'task'
        elif self.focusTable is self.tableWidget_2:
            log_type = 'meeting'
        elif self.focusTable is self.tableWidget_3:
            log_type = 'memo'
        self.focusTable.insertRow(tableRowCount)
        #如果当前增加的task为第一条task，则其成为current_task
        if log_type == 'task' and tableRowCount == 0:
            self.radioButton.setChecked(True)
            self.button_task_urgent.setChecked(False)
        # 获取当前时间
        now = time.time()
        time_local = time.localtime(now)
        time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 转换成新的时间格式
        # 文本框设定
        time_text = '<span style="font-size:13px;"> %s </span>' % time0
        textedit1 = MyTextEdit(time_text,self)
        textedit2 = MyTextEdit(parent=self)
        textedit1.setReadOnly(True)
        textedit2.setReadOnly(True)
        textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        if self.focusTable is self.tableWidget:
            textedit1.Clicked.connect(self.changeCurrentTaskNum)
            if tableRowCount == 0:
                textedit1.setStyleSheet(chosen_task_style)
        textedit2.DoubleClicked.connect(self.set_Editable)
        textedit2.LoseFocus.connect(self.set_ReadOnly)


        self.focusTable.setCellWidget(tableRowCount, 0, textedit1)
        self.focusTable.setCellWidget(tableRowCount, 1, textedit2)

        #如果是tableWidget
        if self.focusTable is self.tableWidget:

            textedit3 = MyTextEdit(parent=self)
            textedit3.setReadOnly(True)
            textedit3.DoubleClicked.connect(self.set_Editable)
            textedit3.LoseFocus.connect(self.set_ReadOnly)
            textedit3.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            self.focusTable.setCellWidget(tableRowCount, 2, textedit3)

        #绑定信号
        for j in range(self.focusTable.columnCount()):
            setattr(self.focusTable.cellWidget(tableRowCount,j),'row_locate', tableRowCount)
            setattr(self.focusTable.cellWidget(tableRowCount,j),'log_id', self.LOG_ID[log_type].get())
            setattr(self.focusTable.cellWidget(tableRowCount,j),'log_type', log_type)
            if j > 0:
                self.focusTable.cellWidget(tableRowCount,j).LoseFocus.connect(self.wrapLogTextUpdate)

        #对后台数据进行修改
        self.wrapLogInsert(tableRowCount, log_type)

    def insertNewLog(self):
        i = self.focusTable.currentRow()
        log_type = 'task'
        if self.focusTable is self.tableWidget:
            log_type = 'task'
        elif self.focusTable is self.tableWidget_2:
            log_type = 'meeting'
        elif self.focusTable is self.tableWidget_3:
            log_type = 'memo'
        now = time.time()
        if i == -1:#未有选中的行
            return
        self.focusTable.insertRow(i)
        #如果当前增加的task为第一条task，则其成为current_task
        if log_type == 'task' and i == 0:
            self.radioButton.setChecked(True)

        time_local = time.localtime(now)
        # 转换成新的时间格式
        time0 = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        #绘制行
        time_text = '<span style="font-size:13px;"> %s </span>' % time0
        textedit1 = MyTextEdit(time_text,self)
        textedit2 = MyTextEdit(parent=self)
        textedit1.setReadOnly(True)
        textedit2.setReadOnly(True)
        textedit1.row_locate = i
        textedit2.row_locate = i
        if self.focusTable is self.tableWidget:
             textedit1.Clicked.connect(self.changeCurrentTaskNum)
        textedit2.DoubleClicked.connect(self.set_Editable)
        textedit2.LoseFocus.connect(self.set_ReadOnly)
        textedit1.setStyleSheet('background:transparent;border-width:0;border-style:outset')
        textedit2.setStyleSheet('background:transparent;border-width:0;border-style:outset')

        self.focusTable.setCellWidget(i, 0, textedit1)
        self.focusTable.setCellWidget(i, 1, textedit2)
        if self.focusTable is self.tableWidget:
            textedit3 = MyTextEdit(parent=self)
            textedit3.setReadOnly(True)
            textedit3.row_locate = i
            textedit3.DoubleClicked.connect(self.set_Editable)
            textedit3.LoseFocus.connect(self.set_ReadOnly)
            textedit3.setStyleSheet('background:transparent;border-width:0;border-style:outset')
            self.focusTable.setCellWidget(i, 2, textedit3)
        #绑定信号
        for j in range(self.focusTable.columnCount()):
            setattr(self.focusTable.cellWidget(i,j),'row_locate', i)
            setattr(self.focusTable.cellWidget(i,j),'log_id', self.LOG_ID[log_type].get())
            setattr(self.focusTable.cellWidget(i,j),'log_type', log_type)
            if j > 0:
                self.focusTable.cellWidget(i,j).LoseFocus.connect(self.wrapLogTextUpdate)
        #修改后台数据,包括数据库数据和view对象数据
        self.wrapLogInsert(i, log_type)
        #所有处于插入行后面的行的row值+1
        for j in range(i+1, self.focusTable.rowCount()):
            self.focusTable.cellWidget(j, 0).increaseRowLocate()
            self.focusTable.cellWidget(j, 1).increaseRowLocate()
            if self.focusTable is self.tableWidget :
                self.focusTable.cellWidget(j, 2).increaseRowLocate()
            # self.wrapLogInterOrderWeight(j, log_type)

    def deleteLog(self):
        i = self.focusTable.currentRow()
        log_type = 'task'
        if self.focusTable is self.tableWidget:
            log_type = 'task'
        elif self.focusTable is self.tableWidget_2:
            log_type = 'meeting'
        elif self.focusTable is self.tableWidget_3:
            log_type = 'memo'
        if i == -1: return#没有记录
        del_or_not = QMessageBox.question(self, "删除记录", "提示：是否删除记录？\n删除后不可恢复！",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        # print(save_or_not)
        if del_or_not == 65536:
            return
        else:
            if self.focusTable is self.tableWidget and self.project.current_task_num:
                self.focusTable.cellWidget(self.project.current_task_num - 1, 0).setStyleSheet(
                    'background:transparent;border-width:0;border-style:outset')
            #修改被影响的inter_order_weight值，并发出删除log数据命令
            self.wrapLogDelete(i, log_type)
            #先删除后台数据，再删除页面信息，因为删除步骤会依赖页面的信息
            self.focusTable.removeRow(i)
            #删除行后面的行的row值-1，inter_
            for j in range(i, self.focusTable.rowCount()):
                self.focusTable.cellWidget(j, 0).decreaseRowLocate()
                self.focusTable.cellWidget(j, 1).decreaseRowLocate()
                if self.focusTable is self.tableWidget :
                    self.focusTable.cellWidget(j, 2).decreaseRowLocate()
            # 处理currentPoint。注意currentPoint/currentNum是从1开始的
            if self.focusTable is not self.tableWidget:
                return
            if self.project.current_task_num == 0:
                pass
            else:
                self.focusTable.cellWidget(self.project.current_task_num - 1, 0).setStyleSheet(chosen_task_style)
            self.on_current_task_num(self.project.current_task_num)

    def changeTableFocus(self):
        if self.focusTable is not self.sender():
            self.focusTable.selectionModel().clearSelection()
        self.focusTable = self.sender()
        print('focus_to', self.focusTable)

    def set_Editable(self):
        sender = self.sender()
        #print(sender)
        sender.setReadOnly(False)

        # sender.setFocus()

    def set_ReadOnly(self):
        sender = self.sender()
        #print(self.tableWidget.hasFocus())
        sender.setReadOnly(True)

    def changeCurrentTaskNum(self, row):  # 重设当前任务标号
        # 将原任务改透明
        if self.project.current_task_num < 1:
            self.project.current_task_num = 1
        elif self.project.current_task_num > len(self.project.tasks):
            self.project.current_task_num = len(self.project.tasks)
        self.tableWidget.cellWidget(self.project.current_task_num - 1, 0).setStyleSheet('background:transparent;border-width:0;border-style:outset')
        # 获取当前任务标号。注意current_task_num从1开始。
        self.project.current_task_num = row + 1
        self.on_current_task_num(self.project.current_task_num)
        # 将当前任务标黄
        self.tableWidget.cellWidget(row, 0).setStyleSheet(chosen_task_style)
        self.initCurrentTaskSet()

    def on_task_update_call(self, row):
        data_json = self.tableWidget.cellWidget(row,2).init_text
        log_eidt_table = RedefinedWidget.JsonLogEditTable(self.parent, data = data_json,
                                                          attachedWidget=self.tableWidget.cellWidget(row,2),
                                                          column_widths=[80*DataView.ResAdaptor.ratio_wid,200*DataView.ResAdaptor.ratio_wid])
        log_eidt_table.EditingFinished.connect(partial(self.on_task_progress_updated, row))
        log_eidt_table.show()

    def wrapProjectUpdate(self,fields_values:dict):
        project_id = self.project._id
        fields_values['_id'] = project_id
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,source_widget=self,
                              conn_company_name=self.project.client)
        self.parent.listener.accept(command)

    def wrapTaskTextUpdate(self,row):
        if hasattr(self.sender(),'edited') and self.sender().edited == False:
            return
        create_time = self.tableWidget.cellWidget(row,0).toPlainText()
        task_desc = self.tableWidget.cellWidget(row,1).toPlainText()
        #
        update_desc_list = self.tableWidget.cellWidget(row,2).init_text
        log_id = self.tableWidget.cellWidget(row, 0).log_id
        project_id = self.project._id
        conn_company_name = self.project.client
        source_widget = self
        log_table = 'tasks'
        fields_values = {}
        fields_values['_id'] = log_id
        fields_values['conn_project_id'] = project_id
        fields_values['create_time'] = create_time
        fields_values['task_desc'] = task_desc
        fields_values['update_desc_list'] = update_desc_list
        # update_type = TaskType(_id=log_id,task_desc=task_desc,update_desc_list=task_update_list,
        #                        conn_project_id=project_id,create_time=create_time,inter_order_weight=index)
        #将更新的数据打包发送给监听器
        command = GTaskCmd('update', _id=log_id,fields_values=fields_values,source_widget=source_widget,
                           conn_company_name=conn_company_name)
        #先更新todo的数据，再发送cmd
        todo_update = {'todo_desc': task_desc, 'conclusion_desc':update_desc_list}
        CS.updateSqliteCells('todo_log',{'conn_task_id':log_id},todo_update)

        self.parent.listener.accept(command)
        self.initTable()
        pass

    def wrapMemoTextUpdate(self,row):
        if self.sender().edited == False:
            return
        create_time = self.tableWidget_3.cellWidget(row,0).toPlainText()
        memo_desc = self.tableWidget_3.cellWidget(row,1).toPlainText()
        log_id = self.tableWidget_3.cellWidget(row, 0).log_id
        project_id = self.project._id
        conn_company_name = self.project.client
        source_widget = self
        log_table = 'project_memo_log'
        fields_values = {}
        fields_values['_id'] = log_id
        fields_values['conn_project_id'] = project_id
        fields_values['create_time'] = create_time
        fields_values['memo_desc'] = memo_desc
        # update_type = TaskType(_id=log_id,task_desc=task_desc,update_desc_list=task_update_list,
        #                        conn_project_id=project_id,create_time=create_time,inter_order_weight=index)
        #将更新的数据打包发送给监听器
        command = GMemoCmd('update', _id=log_id,fields_values=fields_values,source_widget=source_widget,
                           conn_company_name=conn_company_name)
        self.parent.listener.accept(command)
        self.initTable_3()

    def wrapMeetingTextUpdate(self,row):
        if self.sender().edited == False:
            return
        create_time = self.tableWidget_2.cellWidget(row,0).toPlainText()
        meeting_desc = self.tableWidget_2.cellWidget(row,1).toPlainText()
        log_id = self.tableWidget_2.cellWidget(row, 0).log_id
        project_id = self.project._id
        conn_company_name = self.project.client
        source_widget = self
        log_table = 'project_meeting_log'
        fields_values = {}
        fields_values['_id'] = log_id
        fields_values['conn_project_id'] = project_id
        fields_values['create_time'] = create_time
        fields_values['meeting_desc'] = meeting_desc
        # update_type = TaskType(_id=log_id,task_desc=task_desc,update_desc_list=task_update_list,
        #                        conn_project_id=project_id,create_time=create_time,inter_order_weight=index)
        #将更新的数据打包发送给监听器
        command = GMeetingCmd('update', _id=log_id,fields_values=fields_values,source_widget=source_widget,
                           conn_company_name=conn_company_name)
        self.parent.listener.accept(command)
        self.initTable_2()

    def wrapLogDelete(self,row,log_type:str):
        fields_values = {}
        #第一步修改row后面的行的inter_order_weight值
        #确定被修改的log类型
        log = [self.project.tasks,self.project.meeting_log, self.project.memo_log][['task','meeting','memo'].index(log_type)]
        for i in range(row+1, len(log)):
            fields_values.clear()
            log_id = log[i]._id
            log_inter_order_weight = i #全部比原来-1
            project_id = self.project._id
            conn_company_name = self.project.client
            fields_values['_id'] = log_id
            fields_values['inter_order_weight'] = log_inter_order_weight
            fields_values['conn_project_id'] = project_id
            cmd = [GTaskCmd, GMeetingCmd, GMemoCmd][['task', 'meeting', 'memo'].index(log_type)]
            command = cmd(operation='update', _id=log_id, conn_company_name=conn_company_name, source_widget= self,
                          fields_values=fields_values)
            self.parent.listener.accept(command)

        ##定义广播事件域，对于第二步和第三步做一个集体广播
        broadcast_space = BroadcastSpace(self.BROADCAST_ID.get())
        if log_type == 'task':
            broadcast_space.argNameToBroadcast({self.focusTable.cellWidget(row, 0).log_id, self.project._id})
        else:
            broadcast_space.argNameToBroadcast({self.focusTable.cellWidget(row, 0).log_id})

        #第二步，删除log数据库和view类数据
        log_id = log[row]._id
        project_id = self.project._id
        conn_company_name = self.project.client
        fields_values = {}
        fields_values['_id'] = log_id
        fields_values['conn_project_id'] = project_id
        cmd = [GTaskCmd, GMeetingCmd, GMemoCmd][['task', 'meeting', 'memo'].index(log_type)]
        command = cmd(operation='delete', _id=log_id, conn_company_name=conn_company_name, fields_values= fields_values, source_widget= self)
        command.setBroadcastSpace(broadcast_space=broadcast_space)
        self.parent.listener.accept(command)
        #第三步，如果类型是task，修改project的current_task_num值
        if log_type == 'task':
            if self.project.current_task_num and self.project.current_task_num <= row:
                pass
            else:
                current_task_num = 1#默认初始化为1
                if self.project.current_task_num:
                    if self.project.current_task_num == row+1: #被删除的即是current行
                        if self.tableWidget.rowCount() > self.project.current_task_num:#rowCount现在已经被-1了，要在减之前current行后面还有行
                            current_task_num = self.project.current_task_num
                        else:#
                            current_task_num = self.project.current_task_num - 1
                    else:
                        current_task_num = self.project.current_task_num - 1
                fields_values.clear()
                fields_values['_id'] = self.project._id
                fields_values['current_task_num'] = current_task_num
                print('on_delete_send',fields_values)
                command =GProjectCmd(operation='update', _id=self.project._id , conn_company_name=self.project.client,
                                     source_widget=self, fields_values= fields_values)
                command.setBroadcastSpace(broadcast_space=broadcast_space)
                self.parent.listener.accept(command)
        pass

    def wrapLogInsert(self,row, log_type:str):
        '''
        增加一条用于在指定行号位置上增加一条记录的对应数据记录
        这条数据刚创建出来，是一条没有内容的空数据，一些对参数会对其他对象有影响，但是还没有进行设置，因此应该尽量避免马上和其他对象
        关联起来。
        受这条新数据影响的对象包括：project.current_task_num, project.weight，log.inter_order_weight，
        :param row:
        :param log_type:
        :return:
        '''
        fields_values = {}
        #第一步修改row后面的行的inter_order_weight值
        #确定被修改的log类型
        log = [self.project.tasks,self.project.meeting_log, self.project.memo_log][['task','meeting','memo'].index(log_type)]
        log_tableWidget = [self.tableWidget,self.tableWidget_2, self.tableWidget_3][['task','meeting','memo'].index(log_type)]
        for i in range(row, len(log)):
            fields_values.clear()
            log_id = log[i]._id
            log_inter_order_weight = i + 2#原来是row+1，现在全部比原来+1
            project_id = self.project._id
            conn_company_name = self.project.client
            # create_time = log_tableWidget.cellWidget(i,0).toPlainText()#
            fields_values['_id'] = log_id
            fields_values['inter_order_weight'] = log_inter_order_weight
            fields_values['conn_project_id'] = project_id
            # fields_values['create_time'] = create_time
            if log_type == 'task':
                fields_values['officejob_type'] = 'A'
                fields_values['is_critical'] = False
                # self.radioButton.setChecked(True)
                self.button_task_urgent.setChecked(False)
            cmd = [GTaskCmd, GMeetingCmd, GMemoCmd][['task', 'meeting', 'memo'].index(log_type)]
            command = cmd(operation='update', _id=log_id, conn_company_name=conn_company_name, source_widget= self,
                          fields_values=fields_values)
            self.parent.listener.accept(command)

        #定义广播事件域，对于第二步和第三步做一个集体广播
        broadcast_space = BroadcastSpace(self.BROADCAST_ID.get())
        if log_type == 'task':
            broadcast_space.argNameToBroadcast({self.focusTable.cellWidget(row, 0).log_id, self.project._id})
        else:
            broadcast_space.argNameToBroadcast({self.focusTable.cellWidget(row, 0).log_id})

        #第二步，对这一条记录进行封装并发送
        log_id = self.focusTable.cellWidget(row, 0).log_id
        fields_values.clear()
        fields_values['_id'] = log_id
        fields_values['conn_project_id'] = self.project._id
        fields_values['create_time'] = self.focusTable.cellWidget(row, 0).toPlainText()
        fields_values['inter_order_weight'] = row + 1
        conn_company_name = self.project.client
        cmd = [GTaskCmd, GMeetingCmd, GMemoCmd][['task', 'meeting', 'memo'].index(log_type)]
        command = cmd(operation='insert', _id=log_id, conn_company_name=conn_company_name,
                      source_widget= self, fields_values=fields_values)
        command.setBroadcastSpace(broadcast_space=broadcast_space)
        self.parent.listener.accept(command)

        #第三步，如果类型是task，修改project的current_task_num值
        if log_type == 'task':
            if self.project.current_task_num and self.project.current_task_num <= row:
                pass
            else:
                current_task_num = 1#默认初始化为1
                if self.project.current_task_num:
                    current_task_num = self.project.current_task_num + 1
                fields_values.clear()
                fields_values['_id'] = self.project._id
                fields_values['current_task_num'] = current_task_num
                print('on_insert_send',fields_values)
                command =GProjectCmd(operation='update', _id=self.project._id , conn_company_name=self.project.client,
                                     source_widget=self, fields_values= fields_values)
                command.setBroadcastSpace(broadcast_space=broadcast_space)
                self.parent.listener.accept(command)

        pass

    def wrapLogTextUpdate(self,row, log_type:str):
        #确定被修改的log类型
        # pass_to = [ProjectTabBar.wrapTaskTextUpdate, ProjectTabBar.wrapMeetingTextUpdate, ProjectTabBar.wrapMemoTextUpdate]\
        #     [['task','meeting','memo'].index(log_type)]
        # pass_to(self, row)
        sender = self.sender()
        if sender.edited == False:
            return
        if log_type == 'task':
            self.wrapTaskTextUpdate(row)
        elif log_type == 'meeting':
            self.wrapMeetingTextUpdate(row)
        elif log_type == 'memo':
            self.wrapMemoTextUpdate(row)
        pass

    def wrapLogInterOrderWeight(self, row, log_type:str):
        #确定被修改的log类型
        log = [self.project.tasks,self.project.meeting_log, self.project.memo_log][['task','meeting','memo'].index(log_type)]
        # table = [self.tableWidget, self.tableWidget_2, self.tableWidget_3][['task','meeting','memo'].index(log_type)]
        log_id = log[row]._id
        conn_company_name = self.project.client
        fields_values = {}
        fields_values['_id'] = log_id
        fields_values['inter_order_weight'] = log[row].inter_order_weight
        command = GMeetingCmd('update', _id= log_id, fields_values=fields_values, source_widget=self,
                              conn_company_name= conn_company_name)
        self.parent.listener.accept(command)

    def on_order_tobe(self):
        order_tobe = self.sender().isChecked()
        self.project.order_tobe = order_tobe
        self.project.resetWeight()
        project_id = self.project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['order_tobe'] = order_tobe
        self.project.order_tobe = order_tobe
        self.project.resetWeight()
        fields_values['weight'] = self.project.weight
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)
        self.setProjectColour()
        pass

    def on_clear_chance(self):
        clear_chance = self.sender().isChecked()
        project_id = self.project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['clear_chance'] = clear_chance
        self.project.clear_chance = clear_chance
        self.project.resetWeight()
        fields_values['weight'] = self.project.weight
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)
        self.setProjectColour()
        pass

    def on_in_act(self):
        in_act = self.sender().isChecked()
        project_id = self.project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['in_act'] = in_act
        self.project.in_act = in_act
        self.project.resetWeight()
        fields_values['weight'] = self.project.weight
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)
        self.setProjectColour()

    def on_highlight(self):
        highlight = self.sender().isChecked()
        project_id = self.project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['highlight'] = highlight
        self.project.highlight = highlight
        self.project.resetWeight()
        fields_values['weight'] = self.project.weight
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)
        self.setProjectColour()

    def on_to_visit(self):
        to_visit = self.sender().isChecked()
        project_id = self.project._id
        self.project.to_visit = to_visit
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['to_visit'] = to_visit
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,
                              conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)
        self.setProjectColour()
        pass

    def on_is_deal(self):
        sender = self.sender()
        is_deal = sender.isChecked()
        project_id = self.project._id
        self.project.is_deal = is_deal
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['is_deal'] = is_deal
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,
                              conn_company_name=conn_company_name, source_widget=self)
        self.parent.listener.accept(command)
        self.setProjectColour()

    def on_progress(self, val):
        project_id = self.project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['current_progress'] = progress_code_r[val]
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)

    def on_pricing_edit(self):
        p1 = self.lineEdit_pricing1.text()
        p2 = self.lineEdit_pricing2.text()
        p3 = self.lineEdit_pricing3.text()
        self.project.status.current_pricing = int(p1) if p1 else None
        self.project.status.rival_pricing = int(p2) if p2 else None
        self.project.status.deal_price = int(p3) if p3 else None
        self.project.status.saveBasicData()
        pass

    def on_pushButton_demand(self):
        '''弹出菜单，显示并编辑需求量信息'''
        # stage_demand_json = self.project.status.stage_demand
        # stage_demand_data = json.loads(stage_demand_json) if stage_demand_json else []
        # fields = ['stage', 'quantity']#字段名
        # stage_demand_list = []
        # for row in stage_demand_data:
        #     tempList = []
        #     for key in fields:
        #         tempList.append(row[key])
        #     stage_demand_list.append(tempList)
        # self.stage_demand_table = VictorEditTable(self,['阶段','需求/kg'],stage_demand_list,[' 阶段',' kg'],self.pushButton_demand)
        # self.stage_demand_table.EditingFinished.connect(self.on_commit_stage_demand_data)
        # self.stage_demand_table.show()
        # print(self.hSlider_progress.geometry().width())
        # print(self.hSlider_progress.geometry().x())
        pass

    def on_commit_stage_demand_data(self, data:list):
        '''commit ladder-pricing data, input should be a 2-D list'''
        fields = ['stage', 'quantity']#字段名
        stage_demand_data = []
        for row in data:
            tempDict = {}
            # for val in row:
            tempDict['stage'] = row[0]
            tempDict['quantity'] = row[1]
            stage_demand_data.append(tempDict)
        stage_demand_json = json.dumps(stage_demand_data)
        self.project.status.stage_demand = stage_demand_json
        self.project.status.saveBasicData()

    def on_editing_personnel(self,data:list):
        '''编辑人员信息，data是字典组成的列表'''
        personnel_data = []
        personnel_ids = []
        fields = ['name', 'tittle','telephone']
        for row in data:
            tempList = []
            for key in fields:
                tempList.append(row[key])
            personnel_data.append(tempList)
            personnel_ids.append(row['_id'])
        personnel_table = VectorEditTable(self,['姓名','职位','电话'], personnel_data, ['姓名','职位','电话'],
                                          self.pushButton_new,column_widths=[58,65,80],old_data_editable=False)
        personnel_table.EditingFinished.connect(lambda new_personnel_data: self.on_personnel_edited(new_personnel_data, data))
        personnel_table.show()

    def on_personnel_edited(self, new_personnel_data:list, old_personnel_data:list):
        fields = ['name', 'tittle','telephone']
        # old_names = [person['name'] for person in old_personnel_data]
        len_old = len(old_personnel_data)
        psn_id = Snow('psn')
        psl_id = Snow('psl')
        old_names = []
        for i, row in enumerate(new_personnel_data):
            if i < len_old:
                old_names.append(old_personnel_data[i]['name'])
            if i >= len_old:
                if row[0] in old_names:
                    QMessageBox.about(self,'重复添加','%s已存在，将不添加！'%row[0])
                    continue
                tmp_id = psn_id.get()#临时_id
                #查找已有人名
                find_person = self.checkNewPerson(tmp_id, row[0], row[2])
                person_log = PersonLog()
                if find_person:#如果查找到了现有的人名
                    person_id = self.handleNewPerson(find_person,row[0])
                    if person_id is None:#用户取消操作，跳过该人员
                        continue
                    elif person_id:
                        get_id = person_id
                    else:
                        get_id = tmp_id
                else:
                    get_id = tmp_id
                #获取到了id,继续执行
                person_log.conn_person_id = get_id
                person_log._id = psl_id.get()
                person_log.conn_company_id = self.project.client_id
                person_log.conn_company_name = self.project.client
                person_log.job_title = row[1]
                person_log.name = row[0]
                person_log.in_service = True
                person_log.addPersonLog()
                old_personnel_data.append({})#原来的personnel_data的基础上追加
                old_personnel_data[i]['_id'] = get_id
                old_personnel_data[i]['email'] = None
                for j, key in enumerate(fields):
                    old_personnel_data[i][key] = row[j]

        new_personnel_json = json.dumps(old_personnel_data,ensure_ascii=False)
        new_data = old_personnel_data
        CS.upsertSqlite('clients', ['_id', 'short_name', 'personnel'],[self.project.client_id,self.project.client, new_personnel_json])
        self.set_comboBox_personnel(new_data,is_renew = True)
        #
        #todo:这里其实需要改进，把修改其他tabBar的命令封装起来
        # for record in self.parent.tabBarAdded:
        #     if self.project.client_id == record[0]:
        #         record[1].company.loadBasicData()
        #         record[1].company.setPersonnelClass()
        #         record[1].setPersonnelInfo()
        cmd = DataCenter.GPersonnelCmd('update', self.project.client_id)
        self.parent.listener.accept(cmd)

    def checkNewPerson(self,_id, name, telephone):
        person_get = Person.findPerson(name)
        if not person_get:
            new_person = Person()
            new_person._id = _id
            new_person.name = name
            new_person.telephone = telephone
            new_person.addPerson()
            return None
        else:
            return person_get

    def handleNewPerson(self,find_person, name):
        name_with_log = ['以下都不是']
        ids = []
        for person_info in find_person:
            find_person_log = PersonLog.findPersonLog( person_info['_id'] )  # 根据person_id查询记录
            if find_person_log:
                log_text = name + '--' + find_person_log[-1]['conn_company_name'] + '--' + find_person_log[-1][
                    'job_title']
                name_with_log.append( log_text )
                ids.append( person_info['_id'] )
            else:
                continue
        index,ok = ComboBoxDialog.getIndex( self,'重名人员','发现同名记录，\n请确认是否为以下人员：',
                                            name_with_log )
        if not ok:
            return None
        if index == 0:
            return []
        else:
            return ids[index - 1]

    def on_person_in_charge(self, index, ids:list):
        if index == -1:
            return
        self.project.status.person_in_charge = ids[index]
        self.project.status.saveBasicData()

    def on_chance_status(self, index):
        project_id = self.project._id
        self.project.status_code = index
        self.project.status.status_code = index
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['status_code'] = index
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,
                              conn_company_name=conn_company_name,source_widget=self)
        command.need_to_dump_data = False
        self.parent.listener.accept(command)
        CS.upsertSqlite('proj_status_log',keys=['_id','conn_project_id','status_code'],
                        values = [self.project.status_id,project_id, index])

    def on_officejob_type(self):
        print('toggle signal')
        sender = self.sender()
        # print(sender)
        officejob_type = 'A'
        for i , child in enumerate(self.groupBox_7.findChildren(QRadioButton)):
            if child.isChecked():
                officejob_type = 'ABCDE'[i]
        print('officejob_type',officejob_type)
        if not self.project.tasks:
            return
        task_id = self.project.tasks[self.project.current_task_num-1]._id
        project_id = self.project._id
        fields_values = {}
        fields_values['conn_project_id'] = project_id
        fields_values['_id'] = task_id
        fields_values['officejob_type'] = officejob_type
        conn_company_name = self.project.client
        print('fields_values',fields_values)
        #先更新todo的数据，再发送cmd
        todo_update = {'officejob_type': officejob_type}
        CS.updateSqliteCells('todo_log',{'conn_task_id':task_id},todo_update)
        command = GTaskCmd('update', _id = task_id, conn_company_name = conn_company_name,
                           fields_values = fields_values, source_widget = self)
        self.parent.listener.accept(command)
        pass

    def on_task_progress_updated(self, row,json_data):
        self.tableWidget.cellWidget(row,2).init_text = json_data
        self.tableWidget.cellWidget(row,2).setText(json_data)
        self.wrapTaskTextUpdate(row)

    def on_task_urgent(self):
        sender = self.sender()
        is_critical = sender.isChecked()
        if not self.project.tasks:
            return
        task = self.project.tasks[self.project.current_task_num-1]
        task.is_critical = is_critical
        task_id = self.project.tasks[self.project.current_task_num-1]._id
        self.project.resetWeight()
        self.project.saveBasicData()
        project_id = self.project._id
        fields_values = {}
        fields_values['conn_project_id'] = project_id
        fields_values['_id'] = task_id
        fields_values['is_critical'] = is_critical
        conn_company_name = self.project.client
        # print('fields_values',fields_values)
        command = GTaskCmd('update', _id = task_id, conn_company_name = conn_company_name,
                           fields_values = fields_values, source_widget = self)
        self.parent.listener.accept(command)
        pass

    def on_current_task_num(self, n):
        '''接收参数n并保存'''
        project_id = self.project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['current_task_num'] = n
        conn_company_name = self.project.client
        command = GProjectCmd('update',_id= project_id,fields_values=fields_values,conn_company_name=conn_company_name,source_widget=self)
        self.parent.listener.accept(command)
        pass

    def on_pushButton_ladderpricing(self):
        '''弹出菜单，显示并编辑阶梯报价'''
        pricing_json = self.project.status.ladder_pricing
        pricing_data = json.loads(pricing_json) if pricing_json else []
        fields = ['price', 'quantity']#字段名
        pricing_list = []
        for row in pricing_data:
            tempList = []
            for key in fields:
                tempList.append(row[key])
            pricing_list.append(tempList)
        self.pricing_table = VectorEditTable(self,['报价/元','数量/kg'],pricing_list,[' 元/kg',' kg'],self.pushButton_ladderpricing)
        self.pricing_table.EditingFinished.connect(self.on_commit_pricing_data)
        self.pricing_table.show()
        pass

    def on_commit_pricing_data(self, data: list):
        '''commit ladder-pricing data, input should be a 2-D list'''
        fields = ['price', 'quantity']#字段名
        pricing_data = []
        for row in data:
            tempDict = {}
            tempDict['price'] = row[0]
            tempDict['quantity'] = row[1]
            pricing_data.append(tempDict)
        pricing_json = json.dumps(pricing_data,ensure_ascii=False)
        self.project.status.ladder_pricing = pricing_json
        self.project.status.saveBasicData()

    def on_pushButton_rival_disk(self):
        '''弹出菜单，显示并编辑阶梯报价'''
        rival_disk_json = self.project.status.rival_disk
        rival_disk_data = json.loads(rival_disk_json) if rival_disk_json else []
        fields = ['date', 'price','quantity','rival_information']#字段名
        rival_disk_list = []
        for row in rival_disk_data:
            tempList = []
            for key in fields:
                tempList.append(row[key])
            rival_disk_list.append(tempList)
        self.rival_disk_table = VectorEditTable(self,['创建日期','报价/元','数量/kg','对手信息'],rival_disk_list,['',' 元/kg',' kg','对手信息'],
                                             self.pushButton_rival_disk,column_widths=[95,70,60,150],editable_columns=[1,2,3])
        self.rival_disk_table.EditingFinished.connect(self.on_commit_rival_disk_data)
        self.rival_disk_table.show()

    def on_commit_rival_disk_data(self, data:list):
        '''commit rival_disk data, input should be a 2-D list'''
        fields = ['date', 'price','quantity','rival_information']#字段名
        rival_disk_data = []
        for row in data:
            tempDict = {}
            for i, key in enumerate(fields):
                tempDict[key] = row[i]
                if not row[0]:#date不存在，即为新输入的信息
                    # tempDict['date'] = time.strftime("%Y-%m-%d",time.localtime(time.time()))
                    tempDict['date'] = datetime.datetime.today().strftime("%Y-%m-%d")
            rival_disk_data.append(tempDict)
        rival_disk_json = json.dumps(rival_disk_data,ensure_ascii=False)
        self.project.status.rival_disk = rival_disk_json
        self.project.status.saveBasicData()

    def on_pushButton_files(self):
        check_point = self.project.status.check_point
        self.check_point_editor = CheckpointEditor(check_point)
        self.fileMenuWindow = CheckPointTableWidgetPop([70, 140, 80, 150, 50], self.pushButton_files, self)
        self.check_point_editor.checkPointView = self.fileMenuWindow
        self.fileMenuWindow.check_point_presenter = self.check_point_editor
        self.check_point_editor.display()
        # self.fileMenuWindow.EditingFinished.connect(self.on_file_condition_edited)
        pass

    def on_file_condition_edited(self, check_point: CheckPoint):
        check_point.saveAllData()
        self.project.status.saveBasicData()

    def showRightMenu(self, log_type, text = None,text_pad = None):
        menu = QtWidgets.QMenu(parent=self.parent)
        if text_pad:
            allText = text_pad.toPlainText()
            copyAction = menu.addAction('复制')
            copyAction.triggered.connect(lambda :QtWidgets.QApplication.clipboard().setText(text))
            if not text:
                copyAction.setEnabled(False)
            copyAllAction = menu.addAction('复制全部')
            copyAllAction.triggered.connect(lambda : QtWidgets.QApplication.clipboard().setText(allText))
            if not allText:
                copyAllAction.setEnabled(False)
            pasteAction = menu.addAction('粘贴')
            clipboard_text = QtWidgets.QApplication.clipboard().text()
            pasteAction.triggered.connect(lambda :text_pad.textCursor().insertText(clipboard_text))
            pasteAction.triggered.connect(lambda :text_pad.setEdited())
            if text_pad.isReadOnly() or not clipboard_text:
                pasteAction.setEnabled(False)
            if log_type == 'task':
                addTodoAction = menu.addAction('添加追踪')
                addTodoAction.triggered.connect(lambda :self.add_todo_unit(text_pad.row_locate))
            deleteRowAction = menu.addAction('删除行')
            insertRowAction = menu.addAction('插入行')
            deleteRowAction.triggered.connect(self.deleteLog)
            insertRowAction.triggered.connect(self.insertNewLog)

        addRowAction = menu.addAction('添加行')
        addRowAction.triggered.connect(self.addNewLog)
        menu.popup(QtGui.QCursor.pos())

    def add_todo_unit(self, nTaskNum = None):
        if not self.project.tasks:
            QtWidgets.QMessageBox.about(self , '未设置任务' , '请先给当前项目添加需要跟踪的任务！')
            return False

        #如果跳过新增task，直接新增todo, 可以通过启动广播来新增task
        if not nTaskNum :
            nTaskNum = self.project.current_task_num-1 if self.project.tasks else None
        DataView.ToDoView.add_todo_log(self.parent, conn_company_id=self.project.client_id,conn_project_id=self.project._id,
                                       conn_task_id=self.project.tasks[nTaskNum]._id if nTaskNum is not None else None)