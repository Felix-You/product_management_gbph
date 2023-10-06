import datetime
import sys
import types
from functools import partial

from PyQt5.QtGui import QGuiApplication

from DataCenter import office_job_dict
import DataCenter
import GColour
from DataView import View, ResAdaptor, CONTENT_TEXT_SCALING, FIX_SIZE_WIDGET_SCALING
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QMessageBox, QApplication
import RedefinedWidget
from apps.TodoPanel.Interface import ModelPresenter


class TodoUnitView(View):
    def __init__(self, parent_widget = None,  parent_view = None):
        super(TodoUnitView, self).__init__()
        self.parent_widget = parent_widget
        self.parent_view = parent_view# todo_view
        self.presenter:ModelPresenter = None
        self.todoWidget: RedefinedWidget.ToDoUnitWidget = None
        self.data = {}
        self.Todo_Font_Style = 'font-family:Microsoft YaHei; font-weight:405; font-size: %spt'%(9 * CONTENT_TEXT_SCALING)

    # @property
    # def widget(self):
    #     if not self.todoWidget:
    #         self.setWidget()
    #     return self.todoWidget

    def intit_data(self, data):
        self.data = data

    def updateData(self, data):
        self.data.update(data)

    def conclusionDoubleClickEvent(self, obj, e):

        data_json = self.data['conclusion_desc']
        log_edit_table = RedefinedWidget.JsonLogEditTable(self.parent_view.parent_widget, data = data_json, attachedWidget=obj,
                                                          column_widths=[80*ResAdaptor.ratio_wid,200*ResAdaptor.ratio_wid])
        log_edit_table.show()
        log_edit_table.EditingFinished.connect(self.on_conclusion_desc_update)
        # self.set_ignore_leave()
        # log_edit_table.MouseEnter.connect(self.set_ignore_leave)
        # log_edit_table.Close.connect(partial(self.set_ignore_leave, False))
        self.parent_widget.installEventFilter(log_edit_table) # monitor group_widget

    def set_ignore_leave(self, ignore=True):
        self.parent_widget.ignore_leave = ignore

    def textEdit_focusOutEvent(self, textEdit:QTextEdit, e):
        reason = e.reason()
        if reason == Qt.PopupFocusReason:
            return
        if textEdit.edited == False:
            textEdit.setReadOnly(True)
            pass
        else:
            self.textEditingFinished(textEdit)
        if hasattr(self,'edited'):
            self.edited = False
        textEdit.setText(textEdit.toPlainText())
        QTextEdit.focusOutEvent(textEdit,e)

    def updateWidget(self):
        self.todoWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.customContextMenuRequested.connect(self.showTodoMenu)
        self.todoWidget.setStyleSheet(
                           '#todo_widget{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;'
                           'border-radius:7px; border-style: dashed;border-color: '
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}'
                           '#todo_widget:hover{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;'
                           'border-radius:7px; border-style: solid;border-color: '
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(180, 220, 255, 205), stop:1 rgba(151, 201, 252, 205));}'
                           'QLabel{border-width: 0px; background:transparent;}'
                           'QTextEdit{font-family:Microsoft YaHei; font-size: %spt;border-width: 2px; border-style:dashed; border-color: rgba(150, 150, 150, 40)}'
                           'QLineEdit{background:transparent;border-color: rgba(150, 150, 150, 150)}'
                           'QScrollBar:vertical{width: 4px;background:transparent;border: 0px;margin: 0px 0px 0px 0px;}'
                           'QScrollBar::handle:vertical{background:transparent; border-radius:2px;}'
                           'QScrollBar::handle:vertical:hover{background:lightskyblue; border-radius:2px;}'
                           'QScrollBar::add-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
                                      'height:0px;width:0px;subcontrol-position:bottom;subcontrol-origin: margin;}'
                           'QScrollBar::sub-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
                                      'height:0px;width:0px;subcontrol-position:top;subcontrol-origin: margin;}'
                           '#pushButton_company,#pushButton_project{border-style: solid;border-top-color: '
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '
                           'stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, '
                           'x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
                           'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '
                           'stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
                           'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
                           'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
                                      'border-width: 0px;border-radius: 0px;color: #202020;text-align: '
                           'left;font-family: Microsoft YaHei;font:bold;font-size:%spt;'
                                      'padding: 0px;background-color: rgba(220,220,220,0);}'
                            '#pushButton_company:hover,#pushButton_project:hover{border-style: solid;'
                           'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
                           'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	'
                           'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '
                           'stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
                           'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '
                           'stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
                           'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
                           'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
                            'border-width: 1px;border-radius: 5px;color: #202020;text-align: left;'
                           'font-family: Microsoft YaHei;font:bold;font-size:%spt;'
                                      'padding: 0px;background-color: rgb(200,225,255);}'%(8*CONTENT_TEXT_SCALING, 7*CONTENT_TEXT_SCALING, 7*FIX_SIZE_WIDGET_SCALING))

        if self.data['conn_company_name']:
            self.todoWidget.pushButton_company.setText(self.data['conn_company_name'])
        else:
            self.todoWidget.pushButton_company.setText('')
            self.todoWidget.pushButton_company.setEnabled(False)
        # self.todoWidget.setObjectName('todo_unit')
        if self.data['conn_project_name'] :
            self.todoWidget.pushButton_project.setText(self.data['conn_project_name'])
        else:
            self.todoWidget.pushButton_project.setText('')
            self.todoWidget.pushButton_project.setEnabled(False)
        self.todoWidget.pushButton_company.clicked.connect(self.on_company_clicked)
        # self.todoWidget.commandLinkButton.setDescription()
        self.todoWidget.pushButton_project.clicked.connect(self.on_project_clicked)
        self.todoWidget.control_panel.isCritial_slideButton.toggled.connect(self.on_isCritial_slideButton_clicked)
        self.todoWidget.control_panel.todoTimeSpaceDistance_triSliderButton.toggled.connect(self.on_todoTimeSpaceDistance_triSlideButton_toggled)
        self.todoWidget.control_panel.todoStatus_triSlideButton.toggled.connect(self.on_todoStatus_triSlideButton_toggled)
        self.todoWidget.control_panel.pushButton_4.setStyleSheet('QPushButton:checked{background:lightblue}')
        self.todoWidget.control_panel.pushButton_4.clicked.connect(self.on_pending_activated)
        self.todoWidget.control_panel.pushButton_5.setEnabled(False)
        self.todoWidget.control_panel.pushButton_5.clicked.connect(self.on_pending_deactivated)
        self.todoWidget.control_panel.pushButton_6.clicked.connect(self.on_delete_clicked)
        #textEdits signal
        self.todoWidget.textEdit.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit)
        # self.todoWidget.textEdit_2.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit_2)
        self.todoWidget.textEdit_2.mouseDoubleClickEvent = types.MethodType(self.conclusionDoubleClickEvent, self.todoWidget.textEdit_2)
        self.todoWidget.textEdit.setText(self.data['todo_desc'])
        self.todoWidget.textEdit_2.setText(DataCenter.convert_date_log_json(self.data['conclusion_desc']))
        self.todoWidget.textEdit.setContentsMargins(1, 1, 1, 1)
        self.todoWidget.textEdit_2.setContentsMargins(1, 1, 1, 1)
        self.todoWidget.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.textEdit.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit))
        self.todoWidget.textEdit_2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.textEdit_2.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit_2))
        self.todoWidget.control_panel.lineEdit.editingFinished.connect(self.on_slider_close)
        self.todoWidget.control_panel.lineEdit.setEnabled(False)
        #根据字段参数初始化各个参数控件
        # today = datetime.datetime.today().date()
        if self.data['on_pending']:
            self.todoWidget.control_panel.pushButton_4.setChecked(True)
        if self.data['pending_till_date']:
            pending_days = (datetime.datetime.strptime(str(self.data['pending_till_date']), '%Y-%m-%d').date()\
                            - datetime.datetime.today().date()).days
            #datetime两个日期相减得到的数字是实际数字相减的结果
            if pending_days > 0:
                self.todoWidget.lineEdit.setText(str(pending_days))
                self.todoWidget.label.setText(self.data['pending_till_date'])
                self.todoWidget.lineEdit.setEnabled(True)
                self.todoWidget.pushButton_5.setEnabled(True)
            else:
                self.todoWidget.control_panel.lineEdit.setText('')
                self.todoWidget.control_panel.label.setText('')
        else:
            self.todoWidget.control_panel.lineEdit.setText('')
            self.todoWidget.control_panel.label.setText('')
        self.todoWidget.control_panel.isCritial_slideButton.setChecked(self.data['is_critical'])
        self.todoWidget.control_panel.todoStatus_triSlideButton.setCheckstatus(self.data['status'])
        self.todoWidget.control_panel.todoTimeSpaceDistance_triSliderButton.setCheckstatus(self.data['timespace_distance'])
        self.style = ''
        if self.data['conn_project_id']:
            if self.data['conn_project_order_tobe']:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectOrderTobe),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.data['conn_project_clear_chance']:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectClearChance),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.data['conn_project_highlight']:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectHighlight),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.data['conn_project_in_act']:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectInAct),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            else:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{%s}'%self.Todo_Font_Style)
                self.style = self.todoWidget.textEdit.styleSheet()
                pass
        else:
            self.todoWidget.textEdit.setStyleSheet('#textEdit{%s}'%self.Todo_Font_Style)
            self.style = self.todoWidget.textEdit.styleSheet()
        if self.data['is_critical']:
            self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                   '%s}' % (str(
                GColour.getAlphaColor(GColour.TaskColour.TaskIsCritial, 180)), self.Todo_Font_Style))
        self.todoWidget.setUpdatesEnabled(True)

    def setWidget(self, parent_widget = None):
        if parent_widget :
            self.parent_widget = parent_widget
        if self.todoWidget and self.todoWidget.parent_widget is parent_widget:
            return self.todoWidget

        self.todoWidget = RedefinedWidget.ToDoUnitWidget(self.parent_widget, self, self.parent_view.drag_drop_enabled)
        ResAdaptor.init_ui_size(self.todoWidget)
        self.todoWidget.setObjectName('todo_widget')
        self.updateWidget()


    def setOfficejobType(self, X:str):
        if self.data['officejob_type'] == X:
            return
        self.data['officejob_type'] = X
        self.presenter.update_basic_field(self.data['_id'], {'officejob_type': X})
        if self.data['conn_task_id']:
            self.data['conn_task_cat'] = X
            self.updateConnData()

    def textEditingFinished(self,textEditWidget:QTextEdit):
        if textEditWidget.isReadOnly():#未进行内容修改
            return
        textEditWidget.setReadOnly(True)
        if textEditWidget is self.todoWidget.textEdit:
            self.data['todo_desc'] = textEditWidget.toPlainText()
        self.presenter.update_basic_field(self.data['_id'], {'todo_desc': self.data['todo_desc']})
        self.updateConnData()

    def updateConnData(self):
        if self.data['conn_task_id']:
            fields_values = {}
            fields_values['_id'] = self.data['conn_task_id']
            fields_values['task_desc'] = self.data['todo_desc']
            fields_values['update_desc_list'] = self.data['conclusion_desc']
            fields_values['conn_project_id'] = self.data['conn_project_id']
            if self.data['officejob_type']:#
                fields_values['officejob_type'] = self.data['officejob_type'] #not Null constrain
            #如果关联的task已经被删除，则发送出去的更新命令查找不到目标task，accept函数执行后轮空，数据库无更改
            cmd = DataCenter.GTaskCmd('update', _id=self.data['conn_task_id'],
                                      conn_company_name=self.data['conn_company_id'],
                                      source_widget=self.parent_view.tab_bar, fields_values=fields_values)
            self.presenter.listener.accept(cmd)

    def on_company_clicked(self):
        self.presenter.handleShowOtherModel('clients', model_id=self.data['conn_company_id'])

    def on_project_clicked(self):
        self.presenter.handleShowOtherModel('project', model_id=self.data['conn_project_id'])

    def on_isCritial_slideButton_clicked(self):
        if self.todoWidget.control_panel.isCritial_slideButton.isChecked():
            self.data['is_critical'] = True
            self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                   '%s}' % (str(
                GColour.getAlphaColor(GColour.TaskColour.TaskIsCritial, 180)), self.Todo_Font_Style))
        else:
            self.data['is_critical'] = False
            self.todoWidget.textEdit.setStyleSheet(self.style)
        self.presenter.update_basic_field(self.data['_id'], {'is_critical':self.data['is_critical']})
        if self.data['conn_task_id']:#如果todo是和task相关联的，则要对相应的task进行处理
            fields_values = {}
            fields_values['_id'] = self.data['conn_task_id']
            fields_values['is_critical'] = self.data['is_critical']
            fields_values['conn_project_id'] = self.data['conn_project_id']
            # self.presenter.update_other_model('tasks', fields_values)
            update_cmd = DataCenter.GTaskCmd('update', _id=self.data['conn_task_id'], conn_company_name=self.data['conn_company_id'],
                                      source_widget=self.parent_view.tab_bar, fields_values=fields_values)
            self.presenter.update_other_model('tasks', update_cmd)

    def on_todoTimeSpaceDistance_triSlideButton_toggled(self, distance):
        self.data['timespace_distance'] = distance
        self.presenter.update_basic_field(self.data['_id'], {'timespace_distance':distance})

    def on_todoStatus_triSlideButton_toggled(self, status):
        # status = self.todoWidget.todoStatus_triSlideButton.checkStatus
        if status == 2:
            ok = self.pushFoward()
        self.data['status'] = status
        self.presenter.update_basic_field(self.data['_id'], {'status':status})

    def on_conclusion_desc_update(self, json_data:str):
        self.data['conclusion_desc'] = json_data
        log_text = DataCenter.convert_date_log_json(json_data)
        self.todoWidget.textEdit_2.setText(log_text)
        self.presenter.update_basic_field(id = self.data['_id'],
                                          field_values = {'conclusion_desc': self.data['conclusion_desc']})
        # self.updateConnData()

    def on_pending_activated(self):
        self.slider = RedefinedWidget.MySlider(attachedWidget=self.todoWidget.pushButton_4,
                                               attachedView=self, parent=self.todoWidget.groupBox)
        self.slider.setRange(1,35)
        self.todoWidget.control_panel.pushButton_4.setChecked(True)
        if self.todoWidget.control_panel.lineEdit.text() == '':
            self.todoWidget.control_panel.lineEdit.setText(str(0))
        self.slider.valueChanged.connect(self.on_pending_date_changed)
        self.slider.show()
        self.todoWidget.control_panel.lineEdit.setEnabled(True)
        self.todoWidget.control_panel.pushButton_5.setEnabled(True)

    def on_pending_deactivated(self):
        '''适用于“取消”按钮的槽函数, 以及手动将延期天数设置为0的情况的处理'''
        ok = QMessageBox.question(self.todoWidget, '取消延期', '确定取消延期？',
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ok == QMessageBox.No:
            return
        self.todoWidget.control_panel.pushButton_4.setChecked(False)
        self.data['on_pending'] = False
        self.todoWidget.control_panel.lineEdit.setText('')
        self.todoWidget.control_panel.lineEdit.setEnabled(False)
        self.todoWidget.control_panel.label.setText('')
        self.todoWidget.control_panel.pushButton_5.setEnabled(False)
        self.data['pending_till_date'] = None
        self.presenter.update_basic_field(self.data['_id'], {'on_pending':False, 'pending_till_date':None})

    def on_pending_date_changed(self):
        pending_days = round(1.15**self.slider.value())
        self.todoWidget.control_panel.lineEdit.setText(str(pending_days))
        today = datetime.datetime.today().date()
        #datetime日期加一个数字，得到的结果是日期直接加这个数字的值，与两个日期相减的逆运算是对称的
        pending_till_date = today + datetime.timedelta(days=(pending_days))
        self.todoWidget.control_panel.label.setText(str(pending_till_date))

    def direct_set_pending_date(self, days):
        self.data['on_pending'] = True
        today = datetime.datetime.today().date()
        pending_till_date = today + datetime.timedelta(days=(days))
        self.todoWidget.control_panel.lineEdit.setText(str(days))
        self.todoWidget.control_panel.label.setText(str(pending_till_date))
        self.todoWidget.control_panel.pushButton_4.setChecked(True)
        self.todoWidget.control_panel.pushButton_5.setEnabled(True)
        self.data['pending_till_date'] = str(pending_till_date)
        self.presenter.update_basic_field(self.data['_id'], {'on_pending': True, 'pending_till_date': str(pending_till_date)})

    def on_slider_close(self):
        if not self.todoWidget.lineEdit.text():# 未输入数字的时候，出现editingFinished信号，直接忽略
            return
        if self.todoWidget.lineEdit.hasFocus():# 如果焦点是从slider直接跳转到了lineEdit，即说明输入尚未完成
            return
        self.data['on_pending'] = True
        pending_days = int(self.todoWidget.lineEdit.text())
        if pending_days == 0:
            self.todoWidget.lineEdit.setEnabled(False)
            self.todoWidget.lineEdit.setText('')
            self.todoWidget.label.setText('')
            self.todoWidget.pushButton_5.setEnabled(False)
            self.todoWidget.pushButton_4.setChecked(False)
            self.data['on_pending'] = False
            self.data['pending_till_date'] = None
            self.presenter.update_basic_field(self.data['_id'], {'on_pending': False, 'pending_till_date':None})
            return
        today = datetime.datetime.today().date()
        pending_till_date = today + datetime.timedelta(days=(pending_days))
        self.todoWidget.label.setText(str(pending_till_date))
        self.data['pending_till_date'] = str(pending_till_date)
        self.presenter.update_basic_field(self.data['_id'], {'on_pending': self.data['on_pending'],
                                           'pending_till_date': self.data['pending_till_date']})

    def on_delete_clicked(self):
        ok = QMessageBox.question(self.todoWidget, '删除','删除此任务？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.No :
            return
        # self.todoWidget.pushButton_4.setChecked(False)
        self.data['destroyed'] = True
        # self.presenter.update_basic_field(self.data['_id'], {'destroyed': self.data['destroyed']})
        self.parent_view.on_delete_todo(self.data['_id'])
        self.presenter.handleDeleteModel(self.data['_id'])

    def handleTodoUnitDrop(self, source_id, target_id):
        target_unit = self.parent_view.todo_id_view_dict[target_id]
        source_unit = self.parent_view.todo_id_view_dict[source_id]
        new_type = target_unit.data['officejob_type']
        old_type = source_unit.data['officejob_type']
        if new_type == old_type:
            return
        # self.parent_view.handleTodoUnitDrop(source_id, target_id)
        self.presenter.update_basic_field(source_id, {'officejob_type': new_type})
        self.parent_view.refresh()

    def pushFoward(self):
        source_location = self.todoWidget.geometry().topLeft()
        target_location = self.todoWidget.parentWidget().mapToGlobal(source_location)
        relative_location = self.parent_view.parent_widget.mapFromGlobal(target_location)
        Message = QMessageBox(self.parent_view.parent_widget)
        # main_window = QApplication.window
        # location = main_window.geometry().topLeft()
        Message.setIcon(QMessageBox.Question)
        Message.setWindowTitle('下推')
        Message.setText('完成当前任务\n是否创建并下推到新任务？')
        # Message.setDetailedText()
        Message.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        Message.setDefaultButton(QMessageBox.No)
        Message.setGeometry(target_location.x(), target_location.y(), 150, 100)
        print('pop out message')
        ok = Message.exec()
        # Message.move(target_location)
        # ok  = Message.question(self.parent_view.parent_widget,'下推', '完成当前任务\n是否创建并下推到新任务？',
        #                            QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.Yes:
            ok = self.parent_view.push_todo_unit_forward(self.data['_id'])
            return ok
        else:
            return False

    def showRightMenu(self,text = None,text_pad = None):
        text = text_pad.textCursor().selectedText()
        menu = QtWidgets.QMenu(parent=self.parent_view.parent_widget)
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
        menu.popup(QtGui.QCursor.pos())

    def showTodoMenu(self):
        day = datetime.datetime.now().weekday()
        menu = QtWidgets.QMenu(parent=self.parent_view.parent_widget)
        print('visibility:',self.todoWidget.isVisible())
        self.todoWidget.raise_()
        one_day_delay = menu.addAction('延后1天')
        three_day_delay = menu.addAction('延后3天')
        next_week_delay = menu.addAction('延至下周')
        seven_day_delay = menu.addAction('延后7天')
        fifteen_day_delay = menu.addAction('延后15天')
        thirty_day_delay = menu.addAction('延后30天')
        one_day_delay.triggered.connect(lambda :self.direct_set_pending_date(1))
        three_day_delay.triggered.connect(lambda :self.direct_set_pending_date(3))
        next_week_delay.triggered.connect(lambda :self.direct_set_pending_date(7-day))
        fifteen_day_delay.triggered.connect(lambda :self.direct_set_pending_date(15))
        seven_day_delay.triggered.connect(lambda :self.direct_set_pending_date(7))
        thirty_day_delay.triggered.connect(lambda :self.direct_set_pending_date(30))
        #绑定聚合信号
        unite_menu = menu.addMenu('聚合')
        unite_task = unite_menu.addAction('同类任务')
        if self.data['officejob_type']:
            unite_task.triggered.connect(lambda :self.parent_view.uniteByTodoType(self.data['officejob_type']))
        elif self.data['conn_task_id']:
            unite_task.triggered.connect(lambda :self.parent_view.uniteByTodoType(self.data['conn_task_cat']))
        menu.popup(QtGui.QCursor.pos())
        for X in office_job_dict.keys():
            unite_task_X = unite_menu.addAction(office_job_dict[X])
            unite_task_X.triggered.connect(partial(self.parent_view.uniteByTodoType,X))
        #设置任务分类
        type_set_menu = menu.addMenu('修改类型')
        for T in office_job_dict.keys():
            type_set_X = type_set_menu.addAction(office_job_dict[T])
            type_set_X.triggered.connect(partial(self.setOfficejobType, T))



