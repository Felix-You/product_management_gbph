class TodoUnitView(View):
    def __init__(self, parent = None,  parent_view = None):
        super(TodoUnitView, self).__init__()
        self.parent = parent
        self.parent_view = parent_view# todo_view
        self.todoWidget = None
        self.model = ToDo()
        self.Todo_Font_Style = 'font-family:Microsoft YaHei; font-weight:405; font-size: %spt'%(9*CONTENT_TEXT_SCALING)

    @property
    def widget(self):
        return self.todoWidget

    def conclusionDoubleClickEvent(self, obj, e):
        data_json = self.model.conclusion_desc
        log_eidt_table = RedefinedWidget.JsonLogEditTable(self.parent, data = data_json, attachedWidget=obj,
                                                          column_widths=[80*ResAdaptor.ratio_wid,200*ResAdaptor.ratio_wid])
        log_eidt_table.show()
        log_eidt_table.EditingFinished.connect(self.on_conclusion_desc_update)

    def textEdit_focusOutEvent(self, textEdit:QTextEdit, e):
        reason = e.reason()
        if e.reason() == Qt.PopupFocusReason:
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

    def setDataModel(self, _id:str):
        self.model.load_basic_data(_id)
        self.model.loadConnProjectInfo()

    def setWidget(self):
        self.todoWidget = RedefinedWidget.ToDoUnitWidget(self.parent, self.model, self.parent_view.drag_drop_enabled)
        # self.todoWidget.setUpdatesEnabled(False)
        # self.todoWidget.lineEdit.setMinimumWidth(40)
        ResAdaptor.init_ui_size(self.todoWidget)
        self.todoWidget.setObjectName('todo_widget')
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

        #buttons signal
        if self.model.conn_company_name:
            self.todoWidget.pushButton_company.setText(self.model.conn_company_name)
        else:
            self.todoWidget.pushButton_company.setText('')
            self.todoWidget.pushButton_company.setEnabled(False)
        # self.todoWidget.setObjectName('todo_unit')
        if self.model.conn_project_name :
            self.todoWidget.pushButton_project.setText(self.model.conn_project_name)
        else:
            self.todoWidget.pushButton_project.setText('')
            self.todoWidget.pushButton_project.setEnabled(False)
        self.todoWidget.pushButton_company.clicked.connect(self.on_company_clicked)
        # self.todoWidget.commandLinkButton.setDescription()
        self.todoWidget.pushButton_project.clicked.connect(self.on_project_clicked)
        self.todoWidget.isCritial_slideButton.toggled.connect(self.on_isCritial_slideButton_clicked)
        self.todoWidget.todoTimeSpaceDistance_triSliderButton.toggled.connect(self.on_todoTimeSpaceDistance_triSlideButton_toggled)
        self.todoWidget.todoStatus_triSlideButton.toggled.connect(self.on_todoStatus_triSlideButton_toggled)
        self.todoWidget.pushButton_4.setStyleSheet('QPushButton:checked{background:lightblue}')
        self.todoWidget.pushButton_4.clicked.connect(self.on_pending_activated)
        self.todoWidget.pushButton_5.setEnabled(False)
        self.todoWidget.pushButton_5.clicked.connect(self.on_pending_deactivated)
        self.todoWidget.pushButton_6.clicked.connect(self.on_delete_clicked)
        #textEdits signal
        self.todoWidget.textEdit.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit)
        # self.todoWidget.textEdit_2.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit_2)
        self.todoWidget.textEdit_2.mouseDoubleClickEvent = types.MethodType(self.conclusionDoubleClickEvent, self.todoWidget.textEdit_2)
        self.todoWidget.textEdit.setText(self.model.todo_desc)
        self.todoWidget.textEdit_2.setText(DataCenter.convert_date_log_json(self.model.conclusion_desc))
        self.todoWidget.textEdit.setContentsMargins(1, 1, 1, 1)
        self.todoWidget.textEdit_2.setContentsMargins(1, 1, 1, 1)
        self.todoWidget.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.textEdit.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit))
        self.todoWidget.textEdit_2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todoWidget.textEdit_2.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit_2))
        self.todoWidget.lineEdit.editingFinished.connect(self.on_slider_close)
        self.todoWidget.lineEdit.setEnabled(False)
        #根据字段参数初始化各个参数控件
        # today = datetime.datetime.today().date()
        if self.model.on_pending:
            self.todoWidget.pushButton_4.setChecked(True)
        if self.model.pending_till_date:
            pending_days = (datetime.datetime.strptime(str(self.model.pending_till_date), '%Y-%m-%d').date()\
                            - datetime.datetime.today().date()).days
            #datetime两个日期相减得到的数字是实际数字相减的结果
            if pending_days > 0:
                self.todoWidget.lineEdit.setText(str(pending_days))
                self.todoWidget.label.setText(self.model.pending_till_date)
                self.todoWidget.lineEdit.setEnabled(True)
                self.todoWidget.pushButton_5.setEnabled(True)
            else:
                self.todoWidget.lineEdit.setText('')
                self.todoWidget.label.setText('')
        else:
            self.todoWidget.lineEdit.setText('')
            self.todoWidget.label.setText('')
        self.todoWidget.isCritial_slideButton.setChecked(self.model.is_critical)
        self.todoWidget.todoStatus_triSlideButton.setCheckstatus(self.model.status)
        self.todoWidget.todoTimeSpaceDistance_triSliderButton.setCheckstatus(self.model.timespace_distance)
        self.style = ''
        if self.model.conn_project_id:
            if self.model.conn_project_order_tobe:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectOrderTobe),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.model.conn_project_clear_chance:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectClearChance),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.model.conn_project_highlight:
                self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                       '%s}'%(str(GColour.ProjectRGBColour.ProjectHighlight),self.Todo_Font_Style))
                self.style = self.todoWidget.textEdit.styleSheet()
            elif self.model.conn_project_in_act:
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
        if self.model.is_critical:
            self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                   '%s}'%(str(getAlphaColor(GColour.TaskColour.TaskIsCritial, 180)),self.Todo_Font_Style))
        # self.todoWidget.setUpdatesEnabled(True)

    def setOfficejobType(self,X:str):
        if self.model.officejob_type == X:
            return
        self.model.officejob_type = X
        if self.model.conn_task_id:
            self.model.conn_task_cat = X
        self.updateConnData()

    def textEditingFinished(self,textEditWidget:QTextEdit):
        if textEditWidget.isReadOnly():#未进行内容修改
            return
        textEditWidget.setReadOnly(True)
        if textEditWidget is self.todoWidget.textEdit:
            self.model.todo_desc = textEditWidget.toPlainText()
            # textEditWidget.setText(self.model.todo_desc)
        elif textEditWidget is self.todoWidget.textEdit_2:#conclusion
            self.model.conclusion_desc = textEditWidget.toPlainText()
            # textEditWidget.setText()
        self.updateConnData()

    def on_conclusion_desc_update(self, json_data:str):
        self.model.conclusion_desc = json_data
        log_text = DataCenter.convert_date_log_json(json_data)
        self.todoWidget.textEdit_2.setText(log_text)
        self.updateConnData()

    def updateConnData(self):
        self.model.saveBasicData()
        if self.model.conn_task_id:
            fields_values = {}
            fields_values['_id'] = self.model.conn_task_id
            fields_values['task_desc'] = self.model.todo_desc
            fields_values['update_desc_list'] = self.model.conclusion_desc
            fields_values['conn_project_id'] = self.model.conn_project_id
            if self.model.officejob_type:#
                fields_values['officejob_type'] = self.model.officejob_type#not Null constrain
            #如果关联的task已经被删除，则发送出去的更新命令查找不到目标task，accept函数执行后轮空，数据库无更改
            cmd = GTaskCmd('update',_id=self.model.conn_task_id, conn_company_name=self.model.conn_company_id,
                           source_widget=self.parent.todo_view.tab_bar,fields_values=fields_values)
            self.parent.listener.accept(cmd)

    def on_company_clicked(self):
        self.parent.displayCompanyEditor(client_id=self.model.conn_company_id)

    def on_project_clicked(self):
        self.parent.showProjectPerspective(project_id=self.model.conn_project_id)

    def on_isCritial_slideButton_clicked(self):
        if self.todoWidget.isCritial_slideButton.isChecked():
            self.model.is_critical = True
            self.todoWidget.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                                   '%s}'%(str(getAlphaColor(GColour.TaskColour.TaskIsCritial,180)),self.Todo_Font_Style))
        else:
            self.model.is_critical = False
            self.todoWidget.textEdit.setStyleSheet(self.style)
        self.model.saveBasicData()
        if self.model.conn_task_id:#如果todo是和task相关联的，则要对相应的task进行处理
            fields_values = {}
            fields_values['_id'] = self.model.conn_task_id
            fields_values['is_critical'] = self.model.is_critical
            fields_values['conn_project_id'] = self.model.conn_project_id
            cmd = GTaskCmd('update',_id=self.model.conn_task_id, conn_company_name=self.model.conn_company_id,
                           source_widget=self.parent.todo_view.tab_bar,fields_values=fields_values)
            self.parent.listener.accept(cmd)

    def on_todoTimeSpaceDistance_triSlideButton_toggled(self, distance):
        self.model.timespace_distance = distance
        self.model.saveBasicData()

    def on_todoStatus_triSlideButton_toggled(self, status):
        # status = self.todoWidget.todoStatus_triSlideButton.checkStatus
        if status == 2:
            ok = self.pushFoward()
        self.model.status = status
        self.model.saveBasicData()

    def on_pending_activated(self):
        self.slider = RedefinedWidget.MySlider(attachedWidget=self.todoWidget.pushButton_4,
                                               attachedView=self,parent=self.todoWidget.groupBox)
        self.slider.setRange(1,35)
        self.todoWidget.pushButton_4.setChecked(True)
        if self.todoWidget.lineEdit.text() == '':
            self.todoWidget.lineEdit.setText(str(0))
        self.slider.valueChanged.connect(self.on_pending_date_changed)
        self.slider.show()
        self.todoWidget.lineEdit.setEnabled(True)
        self.todoWidget.pushButton_5.setEnabled(True)

    def on_pending_deactivated(self):
        '''适用于“取消”按钮的槽函数, 以及手动将延期天数设置为0的情况的处理'''
        ok = QMessageBox.question(self.todoWidget, '取消延期', '确定取消延期？',
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ok == QMessageBox.No:
            return
        self.todoWidget.pushButton_4.setChecked(False)
        self.model.on_pending = False
        self.todoWidget.lineEdit.setText('')
        self.todoWidget.lineEdit.setEnabled(False)
        self.todoWidget.label.setText('')
        self.todoWidget.pushButton_5.setEnabled(False)
        self.model.pending_till_date = None
        self.model.saveBasicData()

    def on_pending_date_changed(self):
        pending_days = round(1.15**self.slider.value())
        self.todoWidget.lineEdit.setText(str(pending_days))
        today = datetime.datetime.today().date()
        #datetime日期加一个数字，得到的结果是日期直接加这个数字的值，与两个日期相减的逆运算是对称的
        pending_till_date = today + datetime.timedelta(days=(pending_days))
        self.todoWidget.label.setText(str(pending_till_date))

    def direct_set_pending_date(self, days):
        self.model.on_pending = True
        today = datetime.datetime.today().date()
        pending_till_date = today + datetime.timedelta(days=(days))
        self.todoWidget.lineEdit.setText(str(days))
        self.todoWidget.label.setText(str(pending_till_date))
        self.todoWidget.pushButton_4.setChecked(True)
        self.todoWidget.pushButton_5.setEnabled(True)
        self.model.pending_till_date = str(pending_till_date)
        self.model.saveBasicData()

    def on_slider_close(self):
        if not self.todoWidget.lineEdit.text():# 未输入数字的时候，出现editingFinished信号，直接忽略
            return
        if self.todoWidget.lineEdit.hasFocus():# 如果焦点是从slider直接跳转到了lineEdit，即说明输入尚未完成
            return
        self.model.on_pending = True
        pending_days = int(self.todoWidget.lineEdit.text())
        if pending_days == 0:
            self.todoWidget.lineEdit.setEnabled(False)
            self.todoWidget.lineEdit.setText('')
            self.todoWidget.label.setText('')
            self.todoWidget.pushButton_5.setEnabled(False)
            self.todoWidget.pushButton_4.setChecked(False)
            self.model.on_pending = False
            self.model.pending_till_date = None
            self.model.saveBasicData()
            return
        today = datetime.datetime.today().date()
        pending_till_date = today + datetime.timedelta(days=(pending_days))
        self.todoWidget.label.setText(str(pending_till_date))
        self.model.pending_till_date = str(pending_till_date)
        self.model.saveBasicData()

    def on_delete_clicked(self):
        ok = QMessageBox.question(self.todoWidget, '删除','删除此任务？',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.No :
            return
        # self.todoWidget.pushButton_4.setChecked(False)
        self.model.destroyed = True
        self.model.saveBasicData()
        self.parent_view.on_delete_todo(self.model._id)

    def pushFoward(self):
        ok  = QMessageBox.question(self.parent,'下推', '完成当前任务\n是否创建并下推到新任务？',
                                   QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if ok == QMessageBox.Yes:
            ok = self.parent_view.push_todo_unit_forward(self.model._id)
            return ok
        else:
            return False

    def showRightMenu(self,text = None,text_pad = None):
        text = text_pad.textCursor().selectedText()
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
        menu.popup(QtGui.QCursor.pos())

    def showTodoMenu(self):
        day = datetime.datetime.now().weekday()
        menu = QtWidgets.QMenu(parent=self.parent)
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
        if self.model.officejob_type:
            unite_task.triggered.connect(lambda :self.parent_view.uniteByTodoType(self.model.officejob_type))
        elif self.model.conn_task_id:
            unite_task.triggered.connect(lambda :self.parent_view.uniteByTodoType(self.model.conn_task_cat))
        menu.popup(QtGui.QCursor.pos())
        for X in office_job_dict.keys():
            unite_task_X = unite_menu.addAction(office_job_dict[X])
            unite_task_X.triggered.connect(partial(self.parent_view.uniteByTodoType,X))
        #设置任务分类
        type_set_menu = menu.addMenu('修改类型')
        for T in office_job_dict.keys():
            type_set_X = type_set_menu.addAction(office_job_dict[T])
            type_set_X.triggered.connect(partial(self.setOfficejobType, T))
