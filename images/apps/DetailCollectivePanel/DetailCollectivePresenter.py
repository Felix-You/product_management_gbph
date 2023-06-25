import datetime, os

import openpyxl
from PyQt5.QtWidgets import QFileDialog

import FilePathInit
from DataCenter import AccceptState
from core.Presenter import Presenter
from . import DetailViewTabBar

class DetailCollectivePresenter(Presenter):
    contain_root_item = 'project'

    def __init__(self, parent =None):
        super(DetailCollectivePresenter, self).__init__()
        self.projects = []
        self.parent = parent
        self.accept_state = AccceptState()
        self.filepath_model = FilePathInit.userDir
        self.cols_names = ['项目名称', '客户名称', '会议记录', '状态标签','子任务', '状态设定' , '项目备注']
        self.cols_keys = ['product', 'client', 'meeting_log', 'status_code', 'tasks', '', 'memo_log']
        self.cols_index = list(range(len(self.cols_names)))
        self.cols_name_key_dict = dict(zip(self.cols_names,self.cols_keys))
        self.cols_name_index_dict = dict(zip(self.cols_names,self.cols_index))

    def setUi(self, parent_widget):
        self.tab_bar = DetailViewTabBar(parent=parent_widget)
        self.tab_bar.pushButton_export.clicked.connect(self.save_excel_file)
        # self.tab_bar.setStyleSheet('QTextEdit {'
        #                            'border-width: 1px;'
        #                            'border-style: dashed;'
        #                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                            'stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
        tab_header = '详情模式'
        parent_widget.addTab(self.tab_bar, tab_header)
        self.setBoundWidget(self.tab_bar.tableWidget)

    def searchCondition(self,condition:dict):
        self.condition = condition
        self.setDataModel(self.condition)
        self.renderWidget()

    def initAllData(self):
        self.setDataModel(self.condition)
        self.renderWidget()

    def exportData(self):
        sheet_body = []
        for i in range(self.tab_bar.tableWidget.rowCount()):
            row = []
            for j, header in enumerate(self.cols_names):
                if header in ['状态标签']:
                    row.append(self.tab_bar.tableWidget.cellWidget(i,j).currentText())
                elif header in ['状态设定']:
                    text = ', '.join(self.tab_bar.tableWidget.cellWidget(i,j).getCheckedLabels())
                    row.append(text)
                else:
                    row.append(self.tab_bar.tableWidget.cellWidget(i,j).toPlainText())
            sheet_body.append(row)
        return sheet_body

    def save_excel_file(self):
        date = datetime.datetime.today().date()
        filename =  date.strftime("%Y%m%d") + '-详情'
        fname, ftype = QFileDialog.getSaveFileName(self.parent, 'save file',
                                                   self.filepath_model.get_last_save() + '\\' + filename ,
                                                   "ExcelFile (*.xlsx)")
        print(fname, ftype)
        if fname:
            #保存本次选择的路径
            (filepath, tempfilename) = os.path.split(fname)
            self.filepath_model.save_last_save(filepath)
            #保存xlsx文件
            work_book = openpyxl.Workbook()
            work_sheet = work_book.active
            work_sheet.append(self.cols_names)
            sheet_body = self.exportData()
            for i, row in enumerate(sheet_body):
                work_sheet.append(row)#openpyxl从1开始计数，并且默认没有表头
            try:
                work_book.save(fname)
            except PermissionError as e:
                print(e)
                QMessageBox.about(self, '保存失败', '检查文件是否被其他程序打开')
                return
        else:
            return

    def setDataModel(self,condition:dict):
        # if 'status_code' in condition.keys():
        #     status_codes = condition.pop('status_code')
        #     chose_project_ids = CS.getLinesFromTable('proj_status_log',conditions= {'status_code':status_codes},
        #                                              columns_required=['conn_project_id'])
        #     condition['_id'] = chose_project_ids
        self.projects.clear()
        # 首先获取到项目、客户 组对
        detail_proj_ids = CS.getLinesFromTable(table_name='proj_list', conditions=condition, columns_required=['_id', 'client', 'weight'],
                                          order=['client', 'weight'], ascending=False)
        # print('detail_proj_ids',detail_proj_ids)
        detail_proj_ids.pop()
        if not detail_proj_ids:
            QMessageBox.about(self.parent, '未找到', '没有符合条件的项目！')
            return
        ids = []
        for item in detail_proj_ids:
            ids.append(item[0])
        for id in ids:
            project_tmp = Project()
            project_tmp.load_id_data(id)
            self.projects.append(project_tmp)
        pass

    def Accept(self,cmd):
        print('detailview accept')
        if cmd.broadcast_space is None:
            #如果收到的广播命令没有绑定广播域，则将接收状态重置，并设定到接收完成状态
            self.accept_state.__init__()
            self.accept_state.acceptComplete()
        elif self.accept_state.accept_ID != cmd.broadcast_space.broadcast_ID:#接收到了新的广播域
            #重置接收状态
            self.accept_state.__init__(cmd.broadcast_space.broadcast_ID, cmd.broadcast_space.broadcast_names)
            self.accept_state.argAccepted(cmd._id)
        else:
            self.accept_state.argAccepted(cmd._id)

        target_flag = cmd.flag
        source_widget = cmd.source_widget
        if source_widget is self.bound_widget:
            return
        #todo:分发命令
        if target_flag == 2:#task类型
            self.acceptTaskCmd(cmd)
        elif target_flag == 1:#project
            self.acceptProjectCmd(cmd)
        elif target_flag == 3:#meeting
            self.acceptMeetingCmd(cmd)
        elif target_flag == 4:#Memo
            self.acceptMemoCmd(cmd)
        else:
            pass

    def acceptProjectCmd(self, cmd):
        print('DetailView accepted project')
        project_id = cmd._id
        for i, project in enumerate(self.projects):
            if project_id == project._id:
                project.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                if self.accept_state.accept_complete == False:  # 如果改变的数据来自于自身的控件，则不需要重新渲染
                    return
                else:
                    self.renderUnit(i, None)
                    return
        else:
            return

    def acceptMemoCmd(self, cmd) ->None:
        memo_id = cmd._id
        print('DetailView accepted Memo')
        project_id = cmd.fields_values['conn_project_id']
        # 查找被修改的task
        for i, project in enumerate(self.projects):
            if project_id == project._id:
            # 根据operation flag选择操作
                if cmd.operation == 3:  # insert
                    new_memo = Memo(memo_id)
                    new_memo.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    project.memo_log.insert(new_memo.inter_order_weight-1, new_memo)
                    if self.accept_state.accept_complete == False:
                        return
                    else:
                        self.renderUnit(i, None)
                    return
                for k, memo in enumerate(project.memo_log) :
                    if memo_id == memo._id :
                        if cmd.operation == 1 :  # update
                            memo.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                        elif cmd.operation == 4 :  # delete
                            project.memo_log.pop(k)
                        if self.accept_state.accept_complete == False:
                            print('memo accept not completed')
                            return
                        else :
                            print('memo accept completed')
                            self.renderUnit(i,k)
                            return
                return

    def acceptMeetingCmd(self, cmd):
        print('DetailView accepted meeting')

        meeting_id = cmd._id
        project_id = cmd.fields_values['conn_project_id']
        # 查找被修改的meeting
        for i, project in enumerate(self.projects):
            if project_id == project._id:
            # 根据operation flag选择操作
                if cmd.operation == 3:  # insert
                    new_meeting = Meeting(meeting_id)
                    new_meeting.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    project.meeting_log.insert(new_meeting.inter_order_weight-1, new_meeting)
                    if self.accept_state.accept_complete == False:
                        print('meeting accept not complete')
                        return
                    else:
                        print('meeting accept completed')
                        self.renderUnit(i, None)
                    return
                for k, meeting in enumerate(project.meeting_log) :
                    if meeting_id == meeting._id :
                        if cmd.operation == 1 :  # update
                            meeting.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                        elif cmd.operation == 4 :  # delete
                            project.meeting_log.pop(k)
                        if self.accept_state.accept_complete == False:
                            print('meeting accept not complete')
                            return
                        else :
                            print('meeting accept completed')
                            self.renderUnit(i,k)
                            return
                else:return

    def acceptTaskCmd(self,cmd):
        print('DetailView accepted task')
        project_id = cmd.fields_values['conn_project_id']
        task_id = cmd._id
        # 查找被修改的task
        for i, project in enumerate(self.projects):
            if project_id == project._id:
            #根据operation flag选择操作
                if cmd.operation == 3:  # insert
                    new_task = Task(task_id, project_id)
                    new_task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                    project.tasks.insert(new_task.inter_order_weight-1, new_task)
                    if self.accept_state.accept_complete == False:
                        return
                    else:
                        self.renderUnit(i,None)
                    return
                for k, task in enumerate(project.tasks) :
                    if task_id == task._id :
                        if cmd.operation == 1 :  # update
                            task.assign_data(list(cmd.fields_values.keys()), list(cmd.fields_values.values()))
                        elif cmd.operation == 4 :  # delete
                            project.tasks.pop(k)
                        if self.accept_state.accept_complete == False:
                            return
                        else :
                            self.renderUnit(i,k)
                            return

    def renderUnit(self,i, j):
        self.renderLine(i)

    def renderWidget(self):
        row_count = len(self.projects)

        cols_counts = len(self.cols_names)
        self.bound_widget.clear()
        self.bound_widget.setColumnCount(cols_counts)
        self.bound_widget.setRowCount(row_count)
        self.bound_widget.setHorizontalHeaderLabels(self.cols_names)
        self.bound_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget.verticalHeader().setDefaultSectionSize(int(130*DF_Ratio))
        self.bound_widget.setShowGrid(False)

        tags = list(self.parent.chanceStatusFilter.code_name_dict.items())#获取菜单项
        tags.sort(key =lambda item: item[0])
        tagss = [item[1] for item in tags]
        for i, project in enumerate(self.projects):#tableWidget单元格赋值
            for header in self.cols_names:
                #t3 = time.time()
                if header in ['会议记录', '子任务', '项目备注']:
                    textedit = MyQTextEdit()
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header],textedit)
                    content_data = getattr(project,self.cols_name_key_dict[header])
                    content_list = []
                    #生产单元格文本
                    for log_obj in reversed(content_data):# 倒序生成器
                        log_text = log_obj.getTextLog()
                        content_list.append(log_text)
                    content = '\n'.join(content_list)
                    textedit.setText(content)
                    textedit.setReadOnly(True)
                    # textedit.DoubleClicked.connect(lambda :self.parent.generalLogUnitEdit(
                    #         self.projects,self.bound_widget,allowInsert=True))
                elif header == '客户名称':
                    textedit = MyQTextEdit()
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header],textedit)
                    content = str(getattr(project,self.cols_name_key_dict[header]))
                    textedit.setText(content)
                    textedit.setReadOnly(True)

                elif header == '状态标签':
                    tag_comboBox = QComboBox()
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header],tag_comboBox)
                    tag_comboBox.addItems(tagss)
                    status_code = getattr(project,self.cols_name_key_dict[header])
                    if not isinstance(status_code, int):#查询不到status_code,得到的是字段名称
                        status_code = 0
                    tag_comboBox.setCurrentIndex(int(status_code))#不能用setCurrentText, 否则会触发无关的信号
                    tag_comboBox.currentIndexChanged.connect(self.on_project_chance_tag_changed)

                elif header == '状态设定':
                    status_set_frame = StatusCheckFrame(self.parent)
                    status_set_frame.setStyleSheet('QFrame{border-width: 1px; }')
                    status_set_frame.statusClicked.connect(self.on_project_status_changed)
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header], status_set_frame)
                    chk_status = [getattr(project,'in_act'),
                                  getattr(project,'highlight'),
                                  getattr(project,'clear_chance'),
                                  getattr(project,'order_tobe'),]
                    status_set_frame.setCheckedStatuses(chk_status)
                elif header == '项目名称':
                    textedit = MyQTextEdit()#第二次写到这里的时候改了一下CellWidget的构建方法
                    #t1 = time.time()
                    textedit.setStyleSheet('font: bold;font-family: Microsoft Yahei')
                    textedit.DoubleClicked.connect(self.showProjectPerspective)
                    textedit.project_id = project._id
                    self.bound_widget.setCellWidget(i,self.cols_name_index_dict[header], textedit)
                    textedit.setTabChangesFocus(True)
                    textedit.setReadOnly(True)
                    # textedit.DoubleClicked.connect(lambda : self.parent.detailToProjectPerspective(self.bound_widget, self.detailed_item_body))
                    # textedit.setStyleSheet('background:transparent;border-style:outset')
                    textedit.setText(str(getattr(project,'product')))

        # self.bound_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['会议记录'],360*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['状态标签'], 140*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['项目名称'], 100*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['客户名称'], 100*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['子任务'],360*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['状态设定'], 70*DF_Ratio)
        self.bound_widget.setColumnWidth(self.cols_name_index_dict['项目备注'], 360*DF_Ratio)

    def showProjectPerspective(self):
        _id = self.bound_widget.sender().project_id
        self.parent.showProjectPerspective(_id)

    def on_project_status_changed(self, checkStatus:tuple):
        current_row = self.bound_widget.currentRow()
        project = self.projects[current_row]
        in_act, highlight, clear_chance, order_tobe = checkStatus
        project.in_act = in_act
        project.highlight = highlight
        project.clear_chance = clear_chance
        project.order_tobe = order_tobe
        project.resetWeight()
        project_id = project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['in_act'] = in_act
        fields_values['highlight'] = highlight
        fields_values['clear_chance'] = clear_chance
        fields_values['order_tobe'] = order_tobe
        fields_values['weight'] = project.weight
        conn_company_name = project.client
        command = GProjectCmd('update', _id = project_id, fields_values = fields_values,
                              conn_company_name=conn_company_name,source_widget=self.bound_widget)
        self.parent.listener.accept(command)
        pass

    def on_project_chance_tag_changed(self, index:int):
        current_row = self.bound_widget.currentRow()
        project = self.projects[current_row]
        project_id = project._id
        fields_values = {}
        fields_values['_id'] = project_id
        fields_values['status_code'] = index
        conn_company_name = project.client
        command = GProjectCmd('update', _id = project._id, fields_values = fields_values,
                              conn_company_name=conn_company_name,source_widget=self.bound_widget)
        command.need_to_dump_data = False
        self.parent.listener.accept(command)
        CS.upsertSqlite('proj_status_log',keys=['_id','conn_project_id','status_code'],
                        values = [project.status_id,project._id, index])
        # project.saveProjectUpdate()
        pass

    def renderLine(self,i):
        project = self.projects[i]
        cols_names = ['项目名称','客户名称', '会议记录', '状态标签','子任务', '状态设定' , '项目备注']
        cols_keys = ['product','client','meeting_log','status_code','tasks','','memo_log']
        cols_index = list(range(len(cols_names)))
        cols_name_key_dict = dict(zip(cols_names,cols_keys))
        cols_name_index_dict = dict(zip(cols_names,cols_index))
        cols_counts = len(cols_names)
        self.bound_widget.verticalHeader().setDefaultSectionSize(130)
        # tags = list(self.parent.chanceStatusFilter.code_name_dict.items())#获取菜单项
        # tags.sort(key =lambda item: item[0])
        # tagss = [item[1] for item in tags]  # 获取菜单项
        for header in cols_names :
            cell_widget = self.bound_widget.cellWidget(i, cols_name_index_dict[header])
            if header in ['会议记录', '子任务', '项目备注'] :
                textedit = cell_widget
                # textedit = self.bound_widget.cellWidget(i, cols_name_index_dict[header])
                content_data = getattr(project, cols_name_key_dict[header])
                content_list = []
                for log_obj in reversed(content_data):
                    log_text = log_obj.getTextLog()
                    content_list.append(log_text)
                content = '\n'.join(content_list)
                textedit.setText(content)
                textedit.setReadOnly(True)
                # textedit.DoubleClicked.connect(lambda :self.parent.generalLogUnitEdit(
                #         self.projects,self.bound_widget,allowInsert=True))
            elif header == '客户名称' :
                textedit = cell_widget
                # self.bound_widget.setCellWidget(i, cols_name_index_dict[header], textedit)
                content = str(getattr(project, cols_name_key_dict[header]))
                textedit.setText(content)
                textedit.setReadOnly(True)

            elif header == '状态标签' :
                tag_comboBox = cell_widget # 控件实际上是comboBox, 所以换一个名字
                # self.bound_widget.setCellWidget(i, cols_name_index_dict[header], tag_comboBox)
                # tag_comboBox.addItems(tagss)
                tag_comboBox.setCurrentIndex(int(getattr(project, 'status_code')))

            elif header == '状态设定' :
                status_set_frame = cell_widget
                # self.bound_widget.setCellWidget(i, cols_name_index_dict[header], status_set_frame)
                chk_status = [getattr(project, 'in_act'),
                              getattr(project, 'highlight'),
                              getattr(project, 'clear_chance'),
                              getattr(project, 'order_tobe'), ]
                status_set_frame.setCheckedStatuses(chk_status)
            elif header == '项目名称' :
                textedit = cell_widget
                textedit.DoubleClicked.connect(self.showProjectPerspective)
                textedit.project_id = project._id
                textedit.setTabChangesFocus(True)
                textedit.setReadOnly(True)
                # textedit.DoubleClicked.connect(lambda : self.parent.detailToProjectPerspective(self.bound_widget, self.detailed_item_body))
                textedit.setStyleSheet('font: bold;font-family: Microsoft Yahei')
                textedit.setText(str(getattr(project, 'product')))
