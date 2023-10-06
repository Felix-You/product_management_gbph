import json,jsonschema
import time
import types
from functools import reduce
from operator import mul
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QPen
from PyQt5.QtWidgets import QMessageBox, QTextEdit, QFrame, QWidget

import ConnSqlite as CS
from PyQt5 import QtWidgets, QtGui

import RedefinedWidget
from DataCenter import AccceptState, office_job_dict
from DataView import FIX_SIZE_WIDGET_SCALING, DF_Ratio
from apps.TodoPanel.TodoViewTabBar import TodoViewTabBar
from apps.TodoPanel.TodoPanelWidget import GridPanel, WidgetGroupFrame
from apps.TodoPanel.TodoUnitView import TodoUnitView
from apps.TodoPanel.ElementPresenters import ToDoUnitCreator
from core.GlobalListener import global_logger


def new_dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
    a0.accept()
    pass

def non_focusNextPrevChild(cls, b):

    return False

class ToDoPanelView():
    ARRANGE_WEIGHT = 0
    ARRANGE_COMPANY = 1
    ARRANGE_PROJECT = 2
    ARRANGE_OFFI_TYPE = 0
    COMPANY_KEY_ALIAS_FIELD = ('conn_company_id', 'conn_company_name') # (field_name_of_database, field_to_show_user)
    JOBTYPE_KEY_ALIAS_FIELD = ('officejob_type', None)
    PROJECT_KEY_ALIAS_FIELD = ('conn_project_name', 'conn_project_name')


    def __init__(self,parent=None, parent_widget = None):
        super(ToDoPanelView, self).__init__()
        # self.parent = parent
        # self.parent_widget = parent_widget
        self.parent = parent
        self.parent_widget = parent_widget
        self.arrange_strategy = self.ARRANGE_WEIGHT
        self.drag_drop_enabled = True
        self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]
        self.accept_state = AccceptState()
        self.presenter = None
        self.tab_bar = TodoViewTabBar(parent=parent_widget)
        self.todo_panel = GridPanel(parent_view=self, parent_widget = self.tab_bar)
        # self.todo_panel_layout = QtWidgets.QVBoxLayout(self.todo_panel)
        self.tab_bar.todoPanelScroll.setWidget(self.todo_panel)
        self.tab_bar.todoPanelScroll.setStyleSheet('background:transparent')
        self.tab_bar.todoPanelScroll.focusNextPrevChild = types.MethodType(non_focusNextPrevChild, self.tab_bar.todoPanelScroll)
        # self.tab_bar.verticalLayout.replaceWidget(self.tab_bar.todoPanelScroll, self.todo_panel)
        # self.tab_bar.todoPanelScroll.deleteLater()
        self.group_widget_ignore_leave = False
        self.tab_bar.checkStatusChanged.connect(self.on_check_status_changed)
        self.tab_bar.pushButton.clicked.connect(self.on_add_new_todo)
        self.check_status = self.tab_bar.getCheckStatus()
        self.tab_bar.comboBox_order.currentIndexChanged.connect(self.on_arrange_strategy_change)
        self.todo_id_view_dict = {}
        self.group_info = None


    def updateControl(func):
        '''Stop updating widgets while making big changes to them'''
        def wrapper(*args, **kwargs):
            self = args[0]
            self.bound_widget.setUpdatesEnabled(False)
            ret = func(*args, **kwargs)
            self.bound_widget.setUpdatesEnabled(True)
            return ret
        return wrapper

    def initAllData(self):
        pass

    def setPresenter(self, presenter):
        self.presenter = presenter

    def acceptModelData(self, json_data: str):
        '''Accepts data of unit models, as a list.'''
        data = json.loads(json_data)
        for item in data:
            self.updateCache(item)

    def updateCache(self, model_data: dict):
        if '_id' not in model_data:
            raise ValueError('There should be a _id field.')
        id = model_data['_id']
        if id not in self.todo_id_view_dict:
            unit_view = TodoUnitView(parent_view=self)
            unit_view.data.update(model_data)
            self.todo_id_view_dict.update({id:unit_view})
        else:
            self.todo_id_view_dict[id].data.update(model_data)

    def setupUI(self, parent_widget):
        tab_header = '追踪模式'
        parent_widget.addTab(self.tab_bar, tab_header)

    def setupPanel(self):
        self.todo_panel.clearLanes()
        for lane_name, lane in self.group_info.items():
            lane_groups = []
            for group in lane:
                group_frame = WidgetGroupFrame(self, self.todo_panel)
                group_frame.setObjectName('group_frame')
                widgets = [[],[]]
                for id, hidden in group:
                    unit_view = self.todo_id_view_dict[id]
                    unit_view.presenter = self.presenter.todoUnitPresentor

                    if not hidden:
                        widgets[0].append(id)
                    else:
                        widgets[1].append(id)
                group_frame.addWidgets(widgets)
                lane_groups.append(group_frame)
            self.todo_panel.addLane(lane_groups)
        self.todo_panel.lay_widgets()
        self.todo_panel.show()


    def acceptRefresh(self, json_group_info:str):
        group_info = json.loads(json_group_info)
        self.group_info = group_info
        self.setupPanel()


    def on_arrange_strategy_change(self, index):
        self.arrange_strategy = index
        self.setDragDropEnabled(False)
        if self.arrange_strategy == self.ARRANGE_COMPANY:
            self.leveled_key_alias_fields = [self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD]
        elif self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]
            self.setDragDropEnabled()
        else:
            self.leveled_key_alias_fields = [self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD]

        self.on_check_status_changed(self.check_status)


    # @staticmethod
    # def paintEvent(device, e):
    #     width = device.width()
    #     # m_nPTargetPixmap = QPixmap(1,1)
    #     painter = QPainter(device)
    #     pen = QPen(Qt.white)
    #     pen.setWidth(3)
    #     painter.setPen(pen)
    #     painter.begin(device)
    #     painter.drawLine(1, 1, width, 1)
    #     painter.end()
    #     # time_before_update = time.perf_counter()
    #     QFrame.paintEvent(device, e)

    @staticmethod
    def setTableCellAppearance(tablewidget:QtWidgets.QTableWidget, row, column, color, is_switching:bool):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        frame.setStyleSheet('#outer_frame{background-color: rgba(%s,%s,%s, 200)}' % color)
        if is_switching:
            frame.layout().setContentsMargins(4, 3, 4, 1)
        # line = QtWidgets.QGraphicsLineItem()
            frame.paintEvent = types.MethodType(ToDoPanelView.paintEvent, frame)

    def setBoundWidget(self, content_table_widget, header_table_widget = None):
        self.bound_widget = content_table_widget
        # super(ToDoPanelView, self).setBoundWidget(content_table_widget)
        self.bound_widget_header = header_table_widget

    def setDragDropEnabled(self, d0 = True):
        self.drag_drop_enabled = d0

    def setupUi(self):
        tab_header = '追踪模式'
        self.parent_widget.addTab(self.tab_bar, tab_header)
        self.setBoundWidget(self.todo_panel, self.tab_bar.tableWidget_header)
        self.bound_widget.dragEnterEvent = types.MethodType(new_dragEnterEvent, self.bound_widget)
        self.bound_widget_header.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget_header.setFixedHeight(30 * FIX_SIZE_WIDGET_SCALING)

    @updateControl
    def renderTableWidget(self, todo_view_matrix:list[list]):
        row_count = 0
        for col in todo_view_matrix:
            len_col = len(col)
            if len_col > row_count: row_count = len_col
        col_count = len(todo_view_matrix)
        self.bound_widget.clear()
        self.bound_widget.setColumnCount(col_count)
        self.bound_widget.setRowCount(row_count)
        for i in range(row_count):
            for j in range(col_count):
                self.initCellWidget(i, j)
                # self.bound_widget.setCellWidget(i, j, empty_frame)
        # Qt在屏幕上显示的尺寸大小，只和设置的屏幕分辨率有关，会自动消除Windows的scaling所带来的尺寸变化，直接使用的是真实像素
        scale_ratio = FIX_SIZE_WIDGET_SCALING
        self.bound_widget.horizontalHeader().setDefaultSectionSize(int(300 * scale_ratio))
        self.bound_widget.verticalHeader().setDefaultSectionSize(int(170 * scale_ratio))
        self.bound_widget.horizontalHeader().setVisible(False)
        self.bound_widget.verticalHeader().setVisible(False)
        self.bound_widget.horizontalScrollBar().valueChanged.connect(self.set_bound_widget_header_scroll_value)
        self.bound_widget.setShowGrid(False)
        self.bound_widget.setStyleSheet("QTableView::item {padding-left: 2px;  padding-bottom: 0px;"
                                        "padding-right: 2px;border: none;}")

        # 在tableWidget里展示信息
        before_todo_insert = time.perf_counter()
        self.todo_id_map.clear() # todo_id_map记录的是ToDoUnit在tableWidget中的坐标，相当于是对于其在todo_view_matrix中的坐标进行了转置
        # self.bound_widget.setUpdatesEnabled(False)
        for i, col in enumerate(todo_view_matrix):
            self.renderMatrixColum(i)
        after_insert= time.perf_counter()
        # self.bound_widget.setUpdatesEnabled(True)
        print('time for all insert:', after_insert-before_todo_insert)

    def set_bound_widget_header_scroll_value(self, value=None):
        self.bound_widget_header.horizontalScrollBar().setValue(value)

    def renderTableWidget_header(self, header_items:list[list[str]]):
        # if self.arrange_strategy == self.ARRANGE_COMPANY:
        #     self.bound_widget_header.hide()
        self.bound_widget_header.clear()
        self.bound_widget_header.setRowCount(1)
        self.bound_widget_header.setColumnCount(len(header_items))
        scale_ratio = FIX_SIZE_WIDGET_SCALING
        self.bound_widget_header.horizontalHeader().setDefaultSectionSize(int(300 * scale_ratio))
        self.bound_widget_header.horizontalHeader().setVisible(False)
        self.bound_widget_header.verticalHeader().setVisible(False)
        # self.bound_widget_header.horizontalScrollBar().setVisible(False)
        # self.bound_widget_header.verticalScrollBar().setVisible(False)
        self.bound_widget_header.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bound_widget_header.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.bound_widget.setStyleSheet("QTableWidget::item{border-style:dashed; border-width:4px; border-color: PaleGreen ;}")
        self.bound_widget_header.setShowGrid(False)
        if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            header_items = [office_job_dict.get(header[0], '未分组') for header in header_items]
            # self.bound_widget_header.setFixedHeight(30 * FIX_SIZE_WIDGET_SCALING)
        elif self.arrange_strategy == self.ARRANGE_COMPANY or self.arrange_strategy == self.ARRANGE_PROJECT:
            # self.bound_widget_header.verticalHeader().setDefaultSectionSize(int(50 * scale_ratio))
            header_items = [' | '.join(header) for header in header_items]
        else:
            return
        max_header_text_height = 0
        for i, header in enumerate(header_items):
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            font = QFont()
            font.setBold(True)
            font.setFamily("微软雅黑")
            font.setPointSize(int(9 * min(FIX_SIZE_WIDGET_SCALING, DF_Ratio)))
            self.bound_widget_header.setCellWidget(0, i, text_edit)
            text_edit.setText(header)
            text_edit.setFont(font)
            text_edit.setAlignment(Qt.AlignCenter)
            # text_edit.document().adjustSize()
            # height = text_edit.verticalScrollBar().maximum() - text_edit.verticalScrollBar().minimum() + text_edit.verticalScrollBar().pageStep()
            text_edit.document().setDocumentMargin(0)
            height = text_edit.document().size().height()
            width = text_edit.document().size().width()
            layout_width = text_edit.document().documentLayout().documentSize().width()
            layout_height = text_edit.document().documentLayout().documentSize().height()
            text_width = text_edit.document().textWidth()
            ideal_width = text_edit.document().idealWidth()

            # text_edit.document().setTextWidth(width)
            # height = text_edit.document().size().height()
            page_width = text_edit.document().pageSize().width()
            page_height = text_edit.document().pageSize().height()
            block_count = text_edit.document().blockCount()
            line_count = text_edit.document().lineCount()
            text_edit.document().useDesignMetrics()
            height = text_edit.document().size().height()
            width = text_edit.document().size().width()
            layout_width = text_edit.document().documentLayout().documentSize().width()
            layout_height = text_edit.document().documentLayout().documentSize().height()
            text_width = text_edit.document().textWidth()
            ideal_width = text_edit.document().idealWidth()
            # text_edit.document().setTextWidth(width)
            # height = text_edit.document().size().height()
            page_width = text_edit.document().pageSize().width()
            page_height = text_edit.document().pageSize().height()

            # print(height)
            max_header_text_height = max(max_header_text_height, height)
            n = 0
        self.bound_widget_header.setFixedHeight(int(max_header_text_height + 1))
        self.bound_widget_header.verticalHeader().setDefaultSectionSize(int(max_header_text_height + 2))


    def renderWidget(self):
        # 对todo_units进行分类整理
        self.resetUnitWidgets()
        if not self.units_for_render:
            QMessageBox.about(self.parent, "未找到", "未找到符合的待办事项")
            return
        self.todo_view_header_array.clear()
        todo_view_matrix, self.todo_view_header_array = self.makeTodoViewMatrix()
        self.renderTableWidget(todo_view_matrix)
        self.renderTableWidget_header(self.todo_view_header_array)


    def on_check_status_changed(self, check_status):
        before_load_todo = time.perf_counter()
        self.check_status = check_status.copy()
        check_status['arrange_strategy'] = self.arrange_strategy
        json_check_status = json.dumps(check_status)
        json_model_group_info = self.presenter.handleSettingChange(json_check_status)
        model_group_info = json.loads(json_model_group_info)
        self.group_info = model_group_info['group_info']
        model_data = model_group_info['model_data']
        for log in model_data:
            self.updateCache(log)
        self.setupPanel()

    def refresh(self):
        self.on_check_status_changed(self.check_status)

    def on_delete_todo(self, todo_id:str):
        '''
        :param id: id of ToDoUnit
        :return:None
        '''
        target_todo_view = self.todo_id_view_dict[todo_id]

        # self.removeWidgets(id)
        # self.removeUnitsFromCache(id)

    def on_add_new_todo(self, parent:QWidget = None, conn_company_id:str = None,
                        conn_project_id:str=None, conn_task_id:str=None):
        if not parent:
            parent = self.parent
        ok, json_todo_model = self.add_todo_log(parent, conn_company_id, conn_project_id, conn_task_id,
                                                parent_presenter=self.presenter)
        if not ok:
            return

    def push_todo_unit_forward(self, todo_id:str):
        todo_view = self.todo_id_view_dict[todo_id]
        ok, json_todo_model = self.add_todo_log(parent_widget= self.parent,parent_presenter=self.presenter,
                                                conn_company_id = todo_view.data['conn_company_id'],
                                             conn_project_id = todo_view.data['conn_project_id'])
        if ok:
            data = json.loads(json_todo_model)
            todo_view.updateData(data)
            todo_view.updateWidget()
            return True
        else:
            return False

    # def acceptTaskCmd(self,cmd):
    #     print('Todo accepted task')
    #     # client_name = cmd.conn_company_name
    #     conn_task_id = cmd._id
    #     source_widget = cmd.source_widget
    #     if source_widget is self.tab_bar:
    #         return
    #     # 查找被修改的todo_unit的位置
    #
    #     index_in_units = None
    #     index_in_units_for_render = None
    #     for k, todo_unit in enumerate(self.units) :
    #         if conn_task_id == todo_unit.model.conn_task_id :
    #             index_in_units = k
    #             break
    #     else:
    #         return
    #     for i, todo_unit in enumerate(self.units_for_render):
    #         if conn_task_id == todo_unit.model.conn_task_id:
    #             index_in_units_for_render = i
    #             break
    #     else:
    #         pass
    #
    #     if cmd.operation == 4:  # delete
    #         if not index_in_units_for_render is None:# 如果操作是删除，先单独对units_for_render列表执行pop()
    #             self.units_for_render.pop(index_in_units_for_render)
    #         self.units.pop(index_in_units)
    #         for i, unit in enumerate(self.units):
    #             unit.model.inter_order_weight = i + 1
    #         if self.accept_state.accept_complete:
    #             self.renderWidget()
    #     elif cmd.operation == 1:  # update
    #         todo_unit = self.units[index_in_units]
    #         if 'task_desc' in cmd.fields_values.keys():
    #             todo_unit.model.conn_task_desc = cmd.fields_values['task_desc']
    #             todo_unit.model.todo_desc = cmd.fields_values['task_desc']
    #             todo_unit.model.conclusion_desc = cmd.fields_values['update_desc_list']
    #         if 'is_critical' in cmd.fields_values.keys():
    #             todo_unit.model.is_critical = cmd.fields_values['is_critical']
    #         if 'officejob_type' in cmd.fields_values.keys():
    #             todo_unit.model.officejob_type = cmd.fields_values['officejob_type']
    #
    #         if self.accept_state.accept_complete and not index_in_units_for_render is None:
    #             todo_unit.setWidget()
    #             self.reRenderWidget(index_in_units_for_render, index_in_units_for_render)
    def removeUnitFromTodoviewMatrix(self,coord:tuple):
        unit = self.todo_view_matrix[coord[1]].pop(coord[0])
        # self.todo_view_matrix[coord[1]][coord[0]] = None
        return unit

    def handleTodoUnitDrop(self, source_id: str, target_id: str):
        target_unit = self.todo_id_view_dict[target_id]
        source_unit = self.todo_id_view_dict[source_id]
        old_type = source_unit.data['officejob_type']
        new_type = target_unit.data['officejob_type']
        if old_type == new_type:
            return

    def uniteByTodoType(self, type:str):
        """根据待办事项的类型进行选择"""
        tmp_units = self.units.copy()
        for i in reversed(range(len(tmp_units))):
            if tmp_units[i].model.officejob_type:
                if tmp_units[i].model.officejob_type != type:
                    tmp_units.pop(i)
                else:
                    tmp_units[i].setWidget()
            elif tmp_units[i].model.conn_task_id:
                if tmp_units[i].model.conn_task_cat != type:
                    tmp_units.pop(i)
                else:
                    tmp_units[i].setWidget()
            else:
                tmp_units.pop(i)
        self.units_for_render = tmp_units
        if not self.units_for_render:
            return
        self.resetWeight()
        self.renderWidget()

    @staticmethod
    def add_todo_log(parent_widget:QWidget, conn_company_id:str = None, conn_project_id:str=None,conn_task_id:str=None,
                     parent_presenter = None):


        creator = ToDoUnitCreator(company_id=conn_company_id, conn_project_id=conn_project_id,
                                    parent_presenter = parent_presenter, conn_task_id=conn_task_id)
        ok, json_model_data = creator.createWithDialog(parent_widget)
        return ok, json_model_data
