import ConnSqlite as CS
from PyQt5 import QtWidgets

def bools2binary(bl_0):
    '''convert a sequence of booleans to a binary representation'''
    assert len(bl_0) > 0, 'The sequence bl_0 should not be empty'
    bl_0 = map(str, map(int, bl_0))
    b0 = int(''.join(bl_0), 2)
    return b0
    # for i in range(len(tp_0)):
    #     if tp_0[i] and tp_1[i]:
    #       return True
    # else:
    #     return False
class GridModel:
    def __init__(self):
        self.n_lane = 0
        self.id_unit_map = {}
    def set_lanes(self, lane_names: list):
        self.lane_names = lane_names
        self.lanes = [[] for i in range(len(lane_names))]

    def add_unit(self, id: str, unit, i_lane: int, i_pos: int):
        '''
        id: the id of the unit
        unit: unit should have its widget
        i_lane: index of the lane the unit is expected to be put in
        i_pos: the index the unit in the lane
        Return: None
        '''
        if i_pos > 0:
            if i_pos > len(self.lanes[i_lane]):
                raise IndexError('Index i_pos is out of range of list "lane"')
            elif i_pos == len(self.lanes[i_lane]):
                next_unit = None
            else:
                next_unit = self.lanes[i_lane][i_pos]
            former_unit = self.lanes[i_lane][i_pos - 1]
        else:
            former_unit = None
            next_unit = self.lanes[i_lane][0]

        self.id_unit_map.update({id: {'unit': unit,
                                      'former_unit': former_unit,
                                      'next_unit': next_unit,
                                      'i_lane': i_lane,
                                      'i_pos': i_pos}})
        if next_unit:
            self.id_unit_map[next_unit._id]['former_unit'] = unit
        if former_unit:
            self.id_unit_map[former_unit._id]['next_unit'] = unit
        self.lanes[i_lane].insert(i_pos, unit)

        while True:
            if not next_unit:
                break
            next_id = next_unit._id
            self.id_unit_map[next_id]['i_pos'] += 1
            next_unit = self.id_unit_map[next_id]['next_unit']

    def remove_unit(self, id: str):
        if not id in self.id_unit_map:
            print('the id does not exist in the current map')
            return
        i_lane = self.id_unit_map[id]['i_lane']
        i_pos = self.id_unit_map[id]['i_pos']

        if i_pos == 0:
            former_unit = None
        elif i_pos >= len(self.lanes[i_lane]):
            raise IndexError('Index i_pos is out of range of list "lane"')
        else:
            former_unit = self.lanes[i_lane][i_pos - 1]
        if i_pos == len(self.lanes[i_lane]) - 1:
            next_unit = None
        else:
            next_unit = self.lanes[i_lane][i_pos]

        if former_unit:
            if next_unit:
                self.id_unit_map[former_unit._id]['next_unit'] = next_unit
                self.id_unit_map[next_unit._id]['former_unit'] = former_unit
            else:
                self.id_unit_map[former_unit._id]['next_unit'] = None
        else:
            if next_unit:
                self.id_unit_map[next_unit._id]['former_unit'] = None
            else:
                pass

        while True:
            if not next_unit:
                break
            next_id = next_unit._id
            self.id_unit_map[next_id]['i_pos'] += 1
            next_unit = self.id_unit_map[next_id]['next_unit']

    def get_unit(self, id: str):
        return self.id_unit_map[id]['unit']

    def get_unit_coord(self, id: str):
        return self.id_unit_map[id]['i_lane'], self.id_unit_map[id]['i_pos']

    def setup_unit_widget(self, id:str):
        unit = self.id_unit_map[id]['unit']
        unit.setWidget()

    def get_unit_wigdet(self, id:str):
        unit = self.id_unit_map[id]['unit']
        if not unit.widget:
            unit.setWidget()
        return unit.widget

    def make_groups(self):

        pass


class ToDoView(View):
    ARRANGE_WEIGHT = 0
    ARRANGE_COMPANY = 1
    ARRANGE_PROJECT = 2
    ARRANGE_OFFI_TYPE = 0
    COMPANY_KEY_ALIAS_FIELD = ('conn_company_id', 'conn_company_name')
    JOBTYPE_KEY_ALIAS_FIELD = ('officejob_type', None)
    PROJECT_KEY_ALIAS_FIELD = ('conn_project_name', 'conn_project_name')


    def __init__(self,parent=None, parent_widget = None):
        super(ToDoView, self).__init__()
        # self.parent = parent
        # self.parent_widget = parent_widget
        self.units = []
        self.units_for_render = [] ## units_for_render来自于units的浅拷贝，并对元素进行重组值。
        self.todo_id_map = {} # todo_id_map记录的是ToDoUnit在tableWidget中的坐标，相当于是对于其在todo_view_matrix中的坐标进行了转置
        self.grid = GridModel()
        self.todo_view_matrix = None
        self.todo_view_header_array = []
        self.arrange_strategy = self.ARRANGE_WEIGHT
        self.drag_drop_enabled = True
        self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]
        self.accept_state = AccceptState()
        self.bound_widget = None
        self.bound_widget_header = None
        self.tab_bar = TodoViewTabBar(parent=parent_widget)
        # self.tab_bar.setStyleSheet('QTextEdit {'
        #                            'border-width: 1px;'
        #                            'border-style: dashed;'
        #                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                            'stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
        self.tab_bar.checkStatusChanged.connect(self.on_check_status_changed)
        self.tab_bar.pushButton.clicked.connect(self.on_add_new_todo)

        self.check_status = self.tab_bar.getCheckStatus()
        self.tab_bar.comboBox_order.currentIndexChanged.connect(self.on_comboBox_order)

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

    def setDataModel(self, condition: dict=None):
        self.units.clear() # self.units就是最后准备渲染的全部单元
        self.units_for_render.clear()
        self.units_for_render = self.units
        get_pending = self.check_status[0][0] # to_do.pending_date - today

        timespace_distance_wanted = self.check_status[4]
        mask = self.check_status[3]
        mask_b = bools2binary(mask) # 将系列bool值转换成二进制掩码，用于筛选comboBox所选的类型 # project
        condition = self.handleSearchCondition(condition)
        todo_fields = ['_id', 'conn_task_id', 'todo_desc', 'status','on_pending', 'pending_till_date', 'is_critical',
                       'conclusion_desc', 'waiting_desc', 'create_time', 'destroyed', 'inter_order_weight',
                       'conn_project_id', 'conn_company_id', 'officejob_type']
        project_fields = ['product', 'client', 'client_id', 'order_tobe', 'weight', 'in_act', 'clear_chance',
                          'highlight']
        company_fields = ['short_name']
        task_fields = ['officejob_type']
        todo_logs = CS.getLinesFromTable('todo_log', conditions=condition, order=['inter_order_weight'])
        combined_todo_logs = CS.triple_innerJoin_withList_getLines(
            'todo_log', 'proj_list', 'clients',
            target_colums_a=todo_fields, target_colunms_b=project_fields, target_colunms_c=company_fields,
            joint_key_a_b=('conn_project_id', '_id'), joint_key_a_c=('conn_company_id', '_id'),
            condition_a=condition, method='left join')
        keys = todo_logs.pop()

        # load extra information about todo_units
        index_todo_id = keys.index('_id')
        index_project_id = keys.index('conn_project_id')
        index_company_id = keys.index('conn_company_id')
        index_task_id = keys.index('conn_task_id')
        dict_todo_project = {}
        dict_todo_company = {}
        dict_todo_task = {}

        for log in todo_logs:
            if conn_project_id := log[index_project_id] :
                dict_todo_project[log[index_todo_id]] = conn_project_id
            if conn_company_id := log[index_company_id]:
                dict_todo_company[log[index_todo_id]] = conn_company_id
            if conn_task_id := log[index_task_id] :
                dict_todo_task[log[index_todo_id]] = conn_task_id

        project_ids = list(dict_todo_project.values())
        company_ids = list(dict_todo_company.values())
        task_ids = list(dict_todo_task.values())

        project_fields = ['_id','product', 'client', 'client_id', 'order_tobe', 'weight', 'in_act','is_deal', 'clear_chance', 'highlight']
        project_logs  = CS.getLinesFromTable('proj_list', conditions = {'_id': project_ids}, columns_required= project_fields)
        project_dict = {}
        for project_log in project_logs:
            project_dict[project_log[0]] = project_log

        company_fields = ['_id', 'short_name']
        company_logs = CS.getLinesFromTable('clients', conditions = {'_id': company_ids}, columns_required=company_fields)
        company_dict = {}
        for company_log in company_logs:
            company_dict[company_log[0]] = company_log

        task_fields = ['_id', 'officejob_type']
        task_logs = CS.getLinesFromTable('tasks', {'_id': task_ids}, columns_required=task_fields)
        task_dict = {}
        for task_log in task_logs:
            task_dict[task_log[0]] = task_log

        # indexes = range(len(keys))
        # 根据get_pending 和延期到的日期来确定要保留的任务
        j = 0
        before_create_units = time.perf_counter()
        for i, log in enumerate(todo_logs):
            todo_id = log[index_todo_id]
            pending_till_date = log[keys.index('pending_till_date')]
            if get_pending == 0:# 获取到期的任务
                if not pending_till_date:# 不存在延期，保留
                    pass
                else:
                    pending_days = (datetime.datetime.strptime(str(pending_till_date), '%Y-%m-%d').date()\
                                - datetime.datetime.today().date()).days
                    if pending_days > 0: # 还未到期，跳过
                        continue
                    else:# 已到期，保留
                        pass
            elif get_pending == 1:# 获取未到期的任务
                if not pending_till_date:# 不存在延期
                    continue
                else:
                    pending_days = (datetime.datetime.strptime(str(pending_till_date), '%Y-%m-%d').date()\
                                - datetime.datetime.today().date()).days
                    if pending_days > 0: # 还未到期
                        pass
                    else:# # 已到期，跳过
                        continue
            elif get_pending == 2:# 获取全部任务
                pass
            before_create_unit = time.perf_counter()
            todo_unit = TodoUnitView(parent=self.parent, parent_view=self)
            todo_unit.model.assign_data(keys=keys, values=log)

            if todo_id in dict_todo_project.keys():
                conn_project_id = dict_todo_project[todo_id]
                project_log = project_dict[conn_project_id]
                project = dict(zip(project_fields, project_log))
                todo_unit.model.conn_project_name = project['product']
                todo_unit.model.conn_company_name = project['client']
                todo_unit.model.conn_company_id = project['client_id']
                todo_unit.model.conn_project_order_tobe = project['order_tobe']
                todo_unit.model.conn_project_weight = project['weight']
                todo_unit.model.conn_project_in_act = project['in_act']
                todo_unit.model.conn_project_clear_chance = project['clear_chance']
                todo_unit.model.conn_project_highlight = project['highlight']
                todo_unit.model.conn_project_is_deal = project['is_deal']

            if todo_id in dict_todo_company and todo_unit.model.conn_company_name is None:
                conn_company_id = dict_todo_company[todo_id]
                company_log = company_dict[conn_company_id]
                todo_unit.model.conn_company_name = company_log[1]

            if todo_id in dict_todo_task.keys():
                conn_task_id = dict_todo_task[todo_id]
                task_log = task_dict.get(conn_task_id, None)
                if task_log is not None:
                    todo_unit.model.conn_task_cat = task_log[1]

            if todo_unit.model.timespace_distance not in timespace_distance_wanted:
                continue

            if not mask:
                pass
            elif mask and reduce(mul, mask) == 1:
                pass
            else:
                maskee = (todo_unit.model.conn_project_is_deal,
                          todo_unit.model.conn_project_order_tobe,
                          todo_unit.model.conn_project_clear_chance,
                          todo_unit.model.conn_project_highlight,
                          todo_unit.model.conn_project_in_act,
                          not (todo_unit.model.conn_project_is_deal or
                               todo_unit.model.conn_project_order_tobe or
                               todo_unit.model.conn_project_clear_chance or
                               todo_unit.model.conn_project_highlight or
                               todo_unit.model.conn_project_in_act or
                               not bool(todo_unit.model.conn_project_id)),
                          not bool(todo_unit.model.conn_project_id))
                maskee = bools2binary(maskee)
                # global_logger.debug('maskee:{}'.format(maskee))
                # global_logger.debug('mask:{}'.format(mask))
                if not mask_b & maskee: # if only one positional condition matches
                    continue
            j += 1
            before_todo_unitWidget = time.perf_counter()
            todo_unit.setWidget()
            after_todo_unitWidget = time.perf_counter()
            # print('time_for_render_todowidget:', after_todo_unitWidget - before_todo_unitWidget)
            self.units.append(todo_unit)
        after_create_units = time.perf_counter()
        # print('time for creating all units:', after_create_units - before_create_units)
        # self.sortUnits()

        # for i, unit in enumerate(self.units):
        #     unit.model.inter_order_weight = i + 1 # 每次读取出来的todo_unit, 都赋予新的inter_order_weight

    def setUnitsForRender(self):
        if self.units_for_render == self.units:
            return

    def on_comboBox_order(self, index):
        self.arrange_strategy = index
        self.setDragDropEnabled(False)
        if self.arrange_strategy == self.ARRANGE_COMPANY:
            self.leveled_key_alias_fields = [self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD]
        elif self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            self.leveled_key_alias_fields = [self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD, self.PROJECT_KEY_ALIAS_FIELD]
            self.setDragDropEnabled()
        else:
            self.leveled_key_alias_fields = [self.PROJECT_KEY_ALIAS_FIELD, self.JOBTYPE_KEY_ALIAS_FIELD, self.COMPANY_KEY_ALIAS_FIELD]
        if not self.units:
            return
        self.renderWidget()

    @staticmethod
    def setTableCellWidget(tablewidget:QtWidgets.QTableWidget, row, column, widget:QWidget):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        layout = frame.layout()
        item = layout.itemAt(0)
        if item is not None:
            _widget = item.widget()
            layout.removeItem(item)
            _widget.setParent(None)
        layout.addWidget(widget)

        # print('time_for_set_todowidget:', after_setCellWidget - before_setCellWidget)

    @staticmethod
    def tableCellWidget(tablewidget:QtWidgets.QTableWidget, row, column):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        return frame.findChildren(RedefinedWidget.ToDoUnitWidget)[0]

    @staticmethod
    def paintEvent(device, e):
        width = device.width()
        # m_nPTargetPixmap = QPixmap(1,1)
        painter = QPainter(device)
        pen = QPen(Qt.white)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.begin(device)
        painter.drawLine(1, 1, width, 1)
        painter.end()
        # time_before_update = time.perf_counter()
        QFrame.paintEvent(device, e)
        # time_after_update = time.perf_counter()
        # print('time_for_update = ', time_after_update - time_before_update)

    @staticmethod
    def setTableCellAppearance(tablewidget:QtWidgets.QTableWidget, row, column, color, is_switching:bool):
        frame = QtWidgets.QTableWidget.cellWidget(tablewidget, row, column)
        frame.setStyleSheet('#outer_frame{background-color: rgba(%s,%s,%s, 200)}' % color)
        if is_switching:
            frame.layout().setContentsMargins(4, 3, 4, 1)
        # line = QtWidgets.QGraphicsLineItem()
            frame.paintEvent = types.MethodType(ToDoView.paintEvent, frame)

        # line.setLine(0,0,0,width)
        # frame.layout().insertWidget(0,line)


        # frame.setBackgroundRole(color)

    def sortUnits(self):
        self.units.sort(key= lambda unit: unit.model.conn_project_weight + unit.model.is_critical * 5 if \
                unit.model.conn_project_weight else unit.model.is_critical * 5, reverse=True)
        if self.units_for_render == self.units:
            return
        self.units_for_render.sort(key= lambda unit: unit.model.conn_project_weight + unit.model.is_critical * 5 if \
                unit.model.conn_project_weight else unit.model.is_critical * 5, reverse=True)

    def arrangeUnitsIntoLanes(self)->dict:
        '''
        todo卡片的组织策略，具有默认排序策略和指定排序策略这两级
        默认排序策略是基础，指定排序策略则将其中某项策略的优先级提高。
        在不同列间，存在列长度相差过大的情况，可适当进行合并，使得显示结果尽可能接近矩形。
        0: 权重优先
        1：客户优先
        2：项目优先
        3: 类型优先
        4: 主线支线--需明确主线和支线的定义
        '''
        # self.arrange_strategy = self.tab_bar.comboBox_order.currentIndex()

        self.sortUnits() # 使用weight做整体初步排序

        cat_map = self.classify(self.units_for_render, self.leveled_key_alias_fields)

        return cat_map

    @classmethod
    def classify(cls, source_model_list:list[TodoUnitView], leveled_key_fields:list[tuple])->dict:
        '''按照key_field对todo unit的列表分类，以key_field的值为键值的map形式返回'''
        cat_map = {}
        n_model = 0
        for i, unit in enumerate(source_model_list):
            n_model += 1
            key_name = getattr(unit.model, leveled_key_fields[0][0])
            if key_name:
                if key_name in cat_map:
                    cat_map[key_name].append(unit)
                else:
                    cat_map[key_name] = [unit]
            else:
                if '__' in cat_map:
                    cat_map['__'].append(unit)
                else:
                    cat_map['__'] = [unit]

        if len(leveled_key_fields) > 1:
            next_leveled_key_fields = leveled_key_fields[1:]
            for key, model_list in cat_map.items():
                value = cls.classify(model_list, next_leveled_key_fields)
                cat_map.update({key:value})

        cat_map['n_model'] = n_model
        return cat_map

    def handleSearchCondition(self, condition:dict):
        if not condition:
            project_ids = []
        else:
            project_id_get = CS.getLinesFromTable('proj_list',conditions=condition,columns_required=['_id'])
            project_id_get.pop()
            project_ids = [item[0] for item in project_id_get]
        condition = {}
        if project_ids:
            condition['conn_project_id'] = project_ids
        get_pending = self.check_status[0][0]#to_do.pending_date-today
        get_destroyed = self.check_status[0][1]#to_do类属性
        get_progress = self.check_status[1]
        get_critical = self.check_status[2][0]#to_do类属性
        get_normal = self.check_status[2][1]#to_do类属性
        # mask = self.check_status[2]#掩码用于筛选comboBox所选的类型#project
        #对is_critical的筛选
        if get_critical ^ get_normal:
            if get_critical:
                condition['is_critical'] = True
            else:
                condition['is_critical'] = False
        #对destroyed删选
        if get_destroyed:
            condition['destroyed'] = True
        else:
            condition['destroyed'] = False
        # 对status筛选
        progress_checked = []
        for i, bo in enumerate(get_progress):#status包括0,1,2三种状态分别代表未进行，进行中，已完成
            if bo:
                progress_checked.append(i)
        if len(progress_checked) == 0 or len(progress_checked) == 3:
            pass
        else:
            condition['status'] = progress_checked
        return condition

    def setBoundWidget(self, content_table_widget, header_table_widget = None):

        super(ToDoView, self).setBoundWidget(content_table_widget)
        self.bound_widget_header = header_table_widget

    def setDragDropEnabled(self, d0 = True):
        self.drag_drop_enabled = d0

    def setupUi(self):
        tab_header = '追踪模式'
        self.parent_widget.addTab(self.tab_bar, tab_header)
        self.setBoundWidget(self.tab_bar.tableWidget, self.tab_bar.tableWidget_header)
        # self.bound_widget.setAcceptDrops(True)
        self.bound_widget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget.dragEnterEvent = types.MethodType(new_dragEnterEvent, self.bound_widget)
        self.bound_widget.cellWidget = types.MethodType(self.tableCellWidget, self.bound_widget)
        self.bound_widget.setCellWidget = types.MethodType(self.setTableCellWidget, self.bound_widget)
        self.bound_widget.setTableCellAppearance = types.MethodType(self.setTableCellAppearance, self.bound_widget)
        self.bound_widget_header.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.bound_widget_header.setFixedHeight(30 * FIX_SIZE_WIDGET_SCALING)

    def resetUnitWidgets(self, start:int = 0, stop:int = None):
        if not stop:
            stop = len(self.units_for_render)
        else:
            stop += 1
        for i in range(start, stop):
            self.units_for_render[i].setWidget()

    # def renderWidget(self):
    #     self.bound_widget.clear()
    #     row_count = len(self.units_for_render) // 5 if len(self.units_for_render) % 5 == 0 else len(
    #         self.units_for_render) // 5 + 1
    #     self.bound_widget.setColumnCount(5)
    #     self.bound_widget.setRowCount(row_count)
    #
    #     # Qt在屏幕上显示的尺寸大小，只和设置的屏幕分辨率有关，会自动消除Windows的scaling所带来的尺寸变化，直接使用的是真实像素
    #     self.bound_widget.horizontalHeader().setDefaultSectionSize(int(300 * DF_Ratio))
    #     self.bound_widget.verticalHeader().setDefaultSectionSize(int(200 * DF_Ratio))
    #     self.bound_widget.horizontalHeader().setVisible(False)
    #     self.bound_widget.verticalHeader().setVisible(False)
    #     # self.bound_widget.setStyleSheet("QTableWidget::item{border-style:dashed; border-width:4px; border-color: PaleGreen ;}")
    #     self.bound_widget.setShowGrid(False)
    #     # 对todo_units进行排序
    #     self.units_for_render.sort(key = lambda unit: unit.model.inter_order_weight)
    #
    #     # 在tableWidget里展示信息
    #     before_todo_view = time.perf_counter()
    #     for i, unit in enumerate(self.units_for_render):
    #         row_index = i // 5
    #         column_index = i % 5
    #         self.bound_widget.setCellWidget(row_index, column_index, unit.todoWidget)
    #         # self.bound_widget.cellWidget(row_index,column_index).renderSelf()
    #     print('time_for_todo_view_widget:', time.perf_counter() - before_todo_view)

    @classmethod
    def extractDict(cls, cat_map:dict):
        '''
        将dict形式的树转变为list形式
        cat_map: 字典形式的树状分类
        '''
        lst = []
        cat_map.pop('n_model', None)
        for key, value in cat_map.items():
            if isinstance(value, dict):
                lst.extend(cls.extractDict(value))
            else:
                lst.extend(value)
        return lst

    def renderMatrixColum(self, column_index: int):
        col_mark = column_index % 2 # 标记是否换行
        key_field_value_old = ''
        sequence_mark = False
        for i, unit in enumerate(self.todo_view_matrix[column_index]):
            # unit.setWidget()
            self.todo_id_map.update({unit.model._id: (i, column_index)})
            before_in = time.perf_counter()
            self.bound_widget.setCellWidget(i, column_index, unit.todoWidget)
            after_set = time.perf_counter()
            # global_logger.debug("time_for_insert_todowidget{}".format(after_set-before_in))
            unit.todoWidget.setUpdatesEnabled(True)
            if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
                secondary_key_field = self.leveled_key_alias_fields[1][0]
            else:
                secondary_key_field = self.leveled_key_alias_fields[0][0]
            key_field_value_new = getattr(unit.model, secondary_key_field)

            if not key_field_value_new == key_field_value_old:
                sequence_mark = not sequence_mark
                switching = True
            else:
                switching = False
            key_field_value_old = key_field_value_new
            if col_mark:
                rgb = ((225 - int(sequence_mark) * 15),
                       (200 + int(sequence_mark) * 20),
                       (195 + int(sequence_mark) * 0))
            else:
                rgb = ((185 + int(sequence_mark) * 0),
                       (200 + int(sequence_mark) * 30),
                       (235 - int(sequence_mark) * 10))
            self.bound_widget.setTableCellAppearance(i, column_index, rgb, is_switching=switching)

    @updateControl
    def reRenderMatrixColumn(self, column_index:int):
        # shape of former table
        former_len_col = self.bound_widget.rowCount()
        former_len_row = self.bound_widget.columnCount()
        # shape of new table
        len_col = len(self.todo_view_matrix[column_index])
        new_len_col = max(former_len_col, len_col)

        if len_col > former_len_col:
            self.bound_widget.setRowCount(len_col)
            for i in range(former_len_col, new_len_col):
                for j in range(former_len_row): # 填充新的空行
                    empty_frame = self.createEmptyFrame(i, j)
                    QtWidgets.QTableWidget.setCellWidget(self.bound_widget, i, j, empty_frame)

        for i in range(new_len_col): # 清空并填充列
            empty_frame = self.createEmptyFrame(i, column_index)
            QtWidgets.QTableWidget.setCellWidget(self.bound_widget, i, column_index, empty_frame)

        self.renderMatrixColum(column_index)

    def initCellWidget(self, row:int, column:int):
        empty_frame = self.createEmptyFrame(row, column)
        QtWidgets.QTableWidget.setCellWidget(self.bound_widget, row, column, empty_frame)

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

    def makeTodoViewMatrix(self) ->(list[list],list[str]):
        '''
        :return: (headers of columns, colums)
        '''
        cat_map = self.arrangeUnitsIntoLanes()
        cat_map.pop('n_model', None)
        header_cols = list(cat_map.items())
        if self.arrange_strategy == self.ARRANGE_OFFI_TYPE:
            header_cols.sort(key=lambda item: item[0])
            todo_view_matrix = [self.extractDict(header_col[1]) for header_col in header_cols]
            todo_view_headers = [[header_col[0]] for header_col in header_cols]
        else:
            header_cols.sort(key=lambda item: item[1]['n_model'])
            n_cat = len(header_cols)
            max_len_col = header_cols[-1][1]['n_model']
            nest_threshold_n_col = 5
            allowed_min_len_col = 5
            max_len_col = max(max_len_col, allowed_min_len_col) #todo: para to be extracted
            # 构造todo_view布局
            todo_view_headers = []

            if n_cat <= nest_threshold_n_col:
                todo_view_matrix = [self.extractDict(header_col[1]) for header_col in header_cols]
                todo_view_headers = []
                for i, col_list in enumerate(todo_view_matrix):
                    header = header_cols[i][0]
                    if self.leveled_key_alias_fields[0][1]:
                        header_alias = getattr(col_list[0].model, self.leveled_key_alias_fields[0][1])
                    else:
                        header_alias = header
                    todo_view_headers.append([header_alias])
            else:
                todo_view_matrix = [[]]
                todo_view_headers = [[]]
                len_counter = 0
                for header_col in header_cols:
                    col = header_col[1]
                    header = header_col[0]
                    len_col = col.pop('n_model')
                    if len_counter + len_col >= max_len_col or len_col >= max_len_col / 2:
                        todo_view_matrix.append([])
                        todo_view_headers.append([])
                        len_counter = 0
                    else:
                        # if not len(todo_view_matrix[0]) == 0:
                        #     todo_view_matrix[-1].append(None)
                        # len_counter += 1
                        pass

                    col_list = self.extractDict(col)
                    todo_view_matrix[-1].extend(col_list)
                    header_alias = getattr(col_list[0].model, self.leveled_key_alias_fields[0][1]) if \
                        self.leveled_key_alias_fields[0][1] else header
                    header_alias = header_alias if header_alias is not None else '__'
                    todo_view_headers[-1].append(header_alias)
                    len_counter += len_col
            todo_view_matrix.reverse()
            todo_view_headers.reverse()
        self.todo_view_matrix = todo_view_matrix
        return todo_view_matrix, todo_view_headers

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

    def removeWidgets(self, _id:Union[list[str],str]):
        if isinstance(_id,str):
            ids = [_id]
        else:
            ids = _id
        for id in ids:
            row_index, column_index = self.todo_id_map[id]
            # self.bound_widget.removeCellWidget(row_index, column_index) # todo:rewrite
            # item = self.createEmptyFrame(row_index, column_index)
            self.initCellWidget(row_index, column_index)

    def createEmptyFrame(self, row_index:int, column_index:int):
        frame = RedefinedWidget.EmptyDropFrame(self)
        frame.coord = (row_index, column_index)
        if self.drag_drop_enabled == False:
            frame.setAcceptDrops(False)
        return frame

    def setCellUnitWidget(self, row, col, todo_unit_view):
        todo_unit_view.setWidget()
        self.todo_view_matrix[col][row] = todo_unit_view
        self.bound_widget.setCellWidget(row, col, todo_unit_view.todoWidget)

    def reRenderWidget(self, row_index:int, column_index:int, todo_unit_view):
        '''参数start和stop表示的是闭区间'''
        # row_count = len(self.units_for_render) // 5 if len(self.units_for_render) % 5 == 0 else len(self.units_for_render)//5 +1
        # self.bound_widget.setColumnCount(5)
        # self.bound_widget.setRowCount(row_count)
        # self.bound_widget.horizontalHeader().setDefaultSectionSize(300 * FIX_SIZE_WIDGET_SCALING)
        # self.bound_widget.verticalHeader().setDefaultSectionSize(200 * FIX_SIZE_WIDGET_SCALING)
        self.bound_widget.horizontalHeader().setVisible(False)
        self.bound_widget.verticalHeader().setVisible(False)
        self.bound_widget.setCellWidget(row_index,column_index, todo_unit_view.todoWidget)

    def resetWeight(self, start = 0, stop=None):
        if not stop:
            stop = len(self.units_for_render)
        else:
            stop += 1
        for i in range(start, stop):
            unit = self.units_for_render[i]
            unit.model.inter_order_weight = i+1
            unit.model.saveBasicData()

    def removeUnitsFromCache(self,_id:Union[list[str],str]):
        if isinstance(_id,str):
            ids = [_id]
        else:
            ids = _id

        for i in reversed(range(len(self.units))):
            unit = self.units[i]
            if unit.model._id in ids:
                self.units.pop(i)
                self.todo_id_map.pop(unit.model._id, None)

        if self.units_for_render == self.units:
            return
        for i in reversed(range(len(self.units_for_render))):
            unit = self.units_for_render[i]
            if unit.model._id in ids:
                self.units_for_render.pop(i)

    def replaceUnit(self, todo_id:str, new_todo_unit):

        for i in reversed(range(len(self.units))):
            unit = self.units[i]
            if unit.model._id == todo_id:
                self.units.pop(i)
                self.units.insert(i, new_todo_unit)

        if self.units_for_render is self.units:
            return

        for i in reversed(range(len(self.units_for_render))):
            unit = self.units_for_render[i]
            if unit.model._id == todo_id:
                self.units_for_render.pop(i)
                self.units_for_render.insert(i, new_todo_unit)

    def on_check_status_changed(self, check_status):
        before_load_todo = time.perf_counter()
        self.check_status = check_status
        condition = self.parent.overall_project_search(2) # todo: 不适用基于project的搜索，否则无法加载未关联项目的
        self.setDataModel(condition)
        self.renderWidget()
        after_load_todo = time.perf_counter()
        # print('time for loading todo:', after_load_todo - before_load_todo)

    def on_delete_todo(self, id:str):
        '''
        :param id: id of ToDoUnit
        :return:None
        '''
        self.removeWidgets(id)
        self.removeUnitsFromCache(id)

    def on_add_new_todo(self, parent:QWidget = None, conn_company_id:str = None,
                        conn_project_id:str=None, conn_task_id:str=None):
        if not parent:
            parent = self.parent
        ok = self.add_todo_log(parent,conn_company_id, conn_project_id,conn_task_id)
        if not ok:
            return
        self.setDataModel()
        self.renderWidget()

    def push_todo_unit_forward(self, todo_id:str):
        row, col = self.todo_id_map[todo_id]
        todo_view = self.todo_view_matrix[col][row]
        ok, todo_model = self.add_todo_log(parent= self.parent, conn_company_id = todo_view.model.conn_company_id,
                                             conn_project_id = todo_view.model.conn_project_id)
        if ok:
            new_todo_view = TodoUnitView(parent=self.parent, parent_view=self)
            new_todo_view.model = todo_model
            todo_model.loadConnProjectInfo()
            self.removeWidgets(todo_id)
            self.todo_id_map.pop(todo_id)
            self.todo_id_map[new_todo_view.model._id] = (row, col)
            self.replaceUnit(todo_id, new_todo_view)
            self.setCellUnitWidget(row, col, new_todo_view)
            new_todo_view.todoWidget.setUpdatesEnabled(True)
            return True
        else:
            return False

    def Accept(self, cmd):
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

        global_logger.debug('todo_view accepted')
        target_flag = cmd.flag
        if target_flag  == 1:#project
           return
        elif target_flag == 2:#task
            self.acceptTaskCmd(cmd)
        else:
            return

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
        # find units according to id
        source_unit_coord = self.todo_id_map[source_id]
        target_unit_coord = self.todo_id_map[target_id]
        source_unit = self.todo_view_matrix[source_unit_coord[1]][source_unit_coord[0]]
        target_unit = self.todo_view_matrix[target_unit_coord[1]][target_unit_coord[0]]
        source_col = source_unit_coord[1]
        target_col = target_unit_coord[1]
        target_row = target_unit_coord[0]
        # modify officejob_type
        old_type = source_unit.model.officejob_type
        new_type = target_unit.model.officejob_type
        if old_type == new_type:
            return
        source_unit.setOfficejobType(new_type)
        # relocate unit in todo_view_matrix
        self.removeUnitFromTodoviewMatrix(source_unit_coord)
        self.todo_view_matrix[target_col].insert(target_row, source_unit)
        # rerender
        self.reRenderMatrixColumn(source_col)
        self.reRenderMatrixColumn(target_col)
        pass

    def on_empty_frame_drop(self, source_id:str, frame:RedefinedWidget.EmptyDropFrame):
        source_unit_coord = self.todo_id_map[source_id]
        source_unit = self.todo_view_matrix[source_unit_coord[1]][source_unit_coord[0]]
        source_col = source_unit_coord[1]
        target_col = frame.coord[1]
        target_row = frame.coord[0]
        old_type = source_unit.model.officejob_type
        # new_type = self.todo_view_matrix[target_col][0].model.officejob_type
        new_type =self.todo_view_header_array[target_col][0]
        if old_type == new_type:
            return
        self.removeUnitFromTodoviewMatrix(source_unit_coord)
        source_unit.setOfficejobType(new_type)
        if target_row < len(self.todo_view_matrix[target_col]):
            self.todo_view_matrix[target_col].insert(target_row, source_unit)
        # elif target_row == len(self.todo_view_matrix[target_col]):

        else:
            self.todo_view_matrix[target_col].append(source_unit)
        self.reRenderMatrixColumn(source_col)
        self.reRenderMatrixColumn(target_col)

    def acceptTaskCmd(self,cmd):
        global_logger.debug('Todo accepted task')
        # client_name = cmd.conn_company_name
        conn_task_id = cmd._id
        source_widget = cmd.source_widget
        if source_widget is self.tab_bar:
            return
        # 查找被修改的todo_unit的位置

        index_in_units = None
        index_in_units_for_render = None
        for k, todo_unit in enumerate(self.units) :
            if conn_task_id == todo_unit.model.conn_task_id :
                index_in_units = k
                break
        else:
            return
        for i, todo_unit in enumerate(self.units_for_render):
            if conn_task_id == todo_unit.model.conn_task_id:
                index_in_units_for_render = i
                break
        else:
            pass

        if cmd.operation == 4:  # delete
            if not index_in_units_for_render is None:# 如果操作是删除，先单独对units_for_render列表执行pop()
                self.units_for_render.pop(index_in_units_for_render)
            self.units.pop(index_in_units)
            for i, unit in enumerate(self.units):
                unit.model.inter_order_weight = i + 1
            if self.accept_state.accept_complete:
                self.renderWidget()
        elif cmd.operation == 1:  # update
            todo_unit = self.units[index_in_units]
            if 'task_desc' in cmd.fields_values.keys():
                todo_unit.model.conn_task_desc = cmd.fields_values['task_desc']
                todo_unit.model.todo_desc = cmd.fields_values['task_desc']
                todo_unit.model.conclusion_desc = cmd.fields_values['update_desc_list']
            if 'is_critical' in cmd.fields_values.keys():
                todo_unit.model.is_critical = cmd.fields_values['is_critical']
            if 'officejob_type' in cmd.fields_values.keys():
                todo_unit.model.officejob_type = cmd.fields_values['officejob_type']

            if self.accept_state.accept_complete and not index_in_units_for_render is None:
                todo_unit.setWidget()
                coord = self.todo_id_map[self.units_for_render[index_in_units_for_render].model._id]
                self.reRenderWidget(*coord, todo_unit)

    @staticmethod
    def add_todo_log(parent:QWidget,conn_company_id:str = None, conn_project_id:str=None,conn_task_id:str=None):
        creator = ToDoUnitCreator(company_id=conn_company_id, conn_project_id=conn_project_id,
                                      conn_task_id=conn_task_id,parent_widget=parent)
        ok, todo_model = creator.createWithDialog()
        return ok, todo_model
