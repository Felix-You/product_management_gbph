import os
import types
from copy import deepcopy
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QEvent, Qt, QUrl
from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QMessageBox

import DataView
import FilePathInit
import RedefinedWidget
from RedefinedWidget import SliderButton
from core.KitModels import CheckPoint, FileArray, CheckItem
from core.GlobalListener import global_key_mouse_listener, KEY_MOUSE_EVENT
from FilePathInit import userDir, workingDir

class FileListBrowser(QtWidgets.QTextBrowser):
    '''承载的数据对象是FileArray，由于该数据类自身默认数据改变后同步到数据库，所以无需单独的保存步骤'''
    Edited = pyqtSignal(dict)
    File_Operations = (
        ('start_file', '打开文件'),
        ('copy_file', '复制文件'),
        ('open_file_dir', '打开文件位置')
    )
    def __init__(self, parent=None, file_array:dict = None ):
        super(FileListBrowser, self).__init__(parent = parent)
        self.file_array = deepcopy(file_array)
        self.parent = parent
        self.setOpenLinks(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showRightMenu)
        self.anchorClicked.connect(self.on_file_link_clicked)

    @classmethod
    def renderFileHtml(cls, file_array: dict):
        link_labels = []
        if file_array:
            working_path = workingDir.getWorkingDirectory()
            for i, file in enumerate(file_array['items']):
                file_name = file['file_name']
                suffix = os.path.splitext(file_name)[1][1:]
                #         f'href="{file["path"]}#{i}">{file["file_name"]} </a></td></tr>'
                label = f'<a style="color:#000000;font-size:9pt;text-decoration:none;" href="{file["path"]}#{i}">' \
                        f'<{working_path}/img src="images/file_icons64X64/{suffix}.png" alt="[{suffix}]" width="16" height="16">' \
                        f'{file["file_name"]} </a>'
                link_labels.append(label)
            return '<br>'.join(link_labels)
        else:
            return None

    def setDisplay(self, file_array: dict = None):
        if file_array:
            self.file_array =  deepcopy(file_array)
            file_html = self.renderFileHtml(file_array)
            self.setText(file_html)
        else:
            self.refresh()

    def refresh(self):
        file_html = self.renderFileHtml(self.file_array)
        self.setText(file_html)
        if not self.file_array :
            return
        ids = []
        for item in self.file_array['items']:
            ids.append(item['_id'])
        self.file_array['ids'] = ids

    def remove_file(self, index:int):
        if not self.file_array:return
        self.file_array['items'].pop(index)
        self.refresh()
        # self.Edited.emit(self.file_array)

    def add_file(self, file: dict):
        self.file_array['items'].append(file)
        self.refresh()
        # self.Edited.emit(self.file_array)

    def get_file_array(self):
        return self.file_array

    def on_file_link_clicked(self, *args ):
        url = args[0]
        file_index = url.fragment()
        rel_file_path:str = url.adjusted(QUrl.RemoveFragment).url()
        if rel_file_path.startswith('./files/'):
            rel_file_path = rel_file_path.removeprefix('./files/')
        user_document_dir = userDir.getUserFileDirectory()
        abs_file_path = f'{user_document_dir}/{rel_file_path}'
        self.parent.reverse_event_block()
        if not os.path.exists(abs_file_path):

            QtWidgets.QMessageBox.about(self, '未找到', '文件不存在。')
            self.parent.reverse_event_block()
            return
        ok, index_operation = RedefinedWidget.SingleSelectionDialog.getChoice([item[1] for item in self.File_Operations],'选择操作', self, first_choice_default=True)
        if not ok:
            self.parent.reverse_event_block()
            return
        self.parent.reverse_event_block()
        self.__getattribute__(self.File_Operations[index_operation][0])(abs_file_path)

    def copy_file(self, abs_file_path):
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(abs_file_path)
        data.setUrls([url])
        self.parent.reverse_event_block()
        try:
            DataView.clipboard.setMimeData(data)
            QtWidgets.QMessageBox.about(self, '复制成功', '已将文件复制到剪贴板。')
        except:
            QtWidgets.QMessageBox.about(self, '复制失败', '未找到文件。')
        self.parent.reverse_event_block()

    def open_file_dir(self, abs_file_path):
        dir = os.path.split(abs_file_path)[0]
        try:
            os.startfile(os.path.abspath(dir))
            return
        except:
            self.parent.reverse_event_block()
            QtWidgets.QMessageBox.about(self, '打开失败', '未找到文件路径。')
            self.parent.reverse_event_block()
            return

    def start_file(self, abs_file_path):
        try:
            os.startfile(os.path.abspath(abs_file_path))
            return
        except:
            self.parent.reverse_event_block()
            QtWidgets.QMessageBox.about(self, '打开失败', '未找到文件。')
            self.parent.reverse_event_block()
            return

    def showRightMenu(self):
        menu = QtWidgets.QMenu(parent=self.parent)
        action_paste = menu.addAction('粘贴文件')
        action_paste.triggered.connect(self.on_paste_files)
        menu.popup(QtGui.QCursor.pos())

    def on_paste_files(self):
        clipboard_data = DataView.clipboard.mimeData()
        # print(clipboard_data.formats())
        for url in clipboard_data.urls():
            print(url)
        if not clipboard_data.hasFormat('text/uri-list') or clipboard_data.hasFormat('text/plain'):
            self.parent.reverse_event_block()
            QtWidgets.QMessageBox.about(self, '粘贴失败', '剪贴板中没有可粘贴的文件。')
            self.parent.reverse_event_block()
            return

        self.Edited.emit(self.file_array if self.file_array else {})

class CheckPointEditorView(ABC):

    @property
    @abstractmethod
    def check_point_presenter(self):
        pass

    @check_point_presenter.setter
    @abstractmethod
    def check_point_presenter(self, presenter):
        pass

    @abstractmethod
    def setupView(self, data: dict[str, [int,str, dict]], field_type:dict, fields_to_edit:list[str]):
        pass

    @abstractmethod
    def setItemDesc(self, index):
        pass

    @abstractmethod
    def setItemComleteLevel(self, index):
        pass

    @abstractmethod
    def handleFileUpload(self, arg_data: dict) -> tuple:
        file_data = arg_data.copy()
        pass
    @abstractmethod
    def receive_data_stream(self,data_stream:str):
        ...

    @abstractmethod
    def on_upload_files(self, index):
        pass

class CheckPointTableWidgetView(QtWidgets.QTableWidget):
    '''支持类型，b:booleen,sliderButton; t:text,plaintextedit; e:enum,combobox; f:filearray,fileBrowser+button
        此控件类的model应该解决数据保存的问题，目前checkpoint-checkitem-filearray-file 各级中，filearray-file的保存由自身触发。
        子控件的数据修改，其信号所使用的的方法应该和handler中的方法对应。字段名+字段类型 -> 方法。
        和presenter之间以json形式传递数据。
        [{field_name: str,
          presenter method:str,
          data_type: str},
        ]
        对于较大的控件，包括概括、记录、文件，应相邻排布，较小的控件也相邻排布，以此减小控件种类、数量变化带来的外观影响。
    '''
    EditingFinished = pyqtSignal(CheckPoint)

    widget_chooser = {
        'booleen': {
            'choice': SliderButton,
            'init_method': SliderButton.setFontText,
            'set_method': SliderButton.setChecked,
            'get_method': SliderButton.isChecked,
            'signal_name': 'toggled',
            'size': (50, 25),
        },
        'enum': {
            'choice': QtWidgets.QComboBox,
            'init_method': QtWidgets.QComboBox.addItems,
            'set_method': QtWidgets.QComboBox.setCurrentIndex,
            'get_method': QtWidgets.QComboBox.currentIndex,
            'signal_name': 'currentIndexChanged',
            'size': (70, 20),
        },
        'text': {
            'choice': QtWidgets.QPlainTextEdit,
            'init_method': QtWidgets.QPlainTextEdit.setPlainText,
            'set_method': QtWidgets.QPlainTextEdit.setPlainText,
            'get_method': QtWidgets.QPlainTextEdit.toPlainText,
            'signal_name': 'textChanged',
            'size': (130, 70),
        },
        'file': {
            'choice': FileListBrowser,
            'init_method': FileListBrowser.setDisplay,
            'set_method': FileListBrowser.setDisplay,
            'get_method': FileListBrowser.get_file_array,
            'signal_name': 'Edited',
            'size': (140, 70),
        },
        'log':{},
        'dependency':{}
    }

    data_type_edit_method = {
        'enum': 'setItemComleteLevel',
        'text': 'setItemDesc',
        'file': 'on_file_pasted',
    }

    data_field_type = {
    }


    def __init__(self,
                 column_widths: list = None,
                 attachedWidget: QtWidgets.QWidget = None,
                 parent=None):
        super(CheckPointTableWidgetView, self).__init__(parent)
        self.parent = parent
        self._check_point_presenter = None
        self.attachedWidget = attachedWidget
        self.column_widths = column_widths
        self.edited = False
        self.event_blocked = False
        self.setMouseTracking(True)
        self.mouseDoubleClickEvent = types.MethodType(lambda obj, e: e.ignore(), self)
        self.mousePressEvent = types.MethodType(lambda obj, e: e.ignore(), self)
        self.mouseMoveEvent = types.MethodType(lambda obj, e: e.ignore(), self)
        self.data_cache: dict[str, [int, str, list]]
        # global_key_mouse_listener.addObserver(self)

        # self.horizontalHeader().hide()
        # self.initWidgets()
        # self.parent.installEventFilter( self )
        # self.show()

    @classmethod
    def chooseWidget(cls, type_code: str):
        widget = cls.widget_chooser[type_code]['choice']
        widget_type = type_code
        return widget, widget_type

    @classmethod
    def chooseSize(cls, type_code: str):
        return cls.widget_chooser[type_code]['size']

    @classmethod
    def chooseSetMethod(cls, type_code: str):
        return cls.widget_chooser[type_code]['set_method']

    @classmethod
    def chooseGetMethod(cls, type_code: str):
        return cls.widget_chooser[type_code]['get_method']

    @classmethod
    def chooseInitMethod(cls, type_code: str):
        return cls.widget_chooser[type_code]['init_method']

    @classmethod
    def chooseSiganlName(cls, type_code: str):
        return cls.widget_chooser[type_code]['signal_name']

    @property
    def check_point_presenter(self):
        return self._check_point_presenter
        pass

    @check_point_presenter.setter
    def check_point_presenter(self, presenter):
        self._check_point_presenter = presenter
        pass


    def getWidgetData(self, widget:QtWidgets.QWidget):
        ...

    def registerDataType(self, data_type: dict)->None:
        '''
        a filed should be registered with 2 tings: its type, and the signature of the method for the presenter to update
         data.
        the types registerd with 2 things: name of the type - data_type, widget and corresponding widget methods.
        :return:
        '''
        self.widget_chooser.update(data_type)

    def registerDataField(self, field_type: dict) -> None:
        self.data_field_type.update(field_type)

    def setupView(self, data: dict[str, [int, str, dict]], field_type: dict, fields_to_edit: list[str]):
        self.data_cache = data.copy()
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 禁止编辑
        header = ['项目', '情况描述', '进度', '文件', '..']
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)
        # self.horizontalHeader().setMaximumHeight(25)
        nRow = len(data['children_items'])
        self.setRowCount(nRow)
        self.renderSelf()
        for i, width in enumerate(self.column_widths):
            self.setColumnWidth(i, width)
        self.verticalHeader().setDefaultSectionSize(75)
        self.set_geometry(nRow, 5, self.column_widths)
        for i, check_item in enumerate(data['children_items']):
            Qitem = QtWidgets.QTableWidgetItem(check_item['label'])
            Qitem.setTextAlignment(Qt.AlignRight)
            self.setItem(i, 0, Qitem)  # 项目标题
            for j, field in enumerate(fields_to_edit):
                widget_cls, widget_type = self.chooseWidget(field_type[field])
                widget = widget_cls(parent=self)
                widget.row_index = i
                widget.data_type = widget_type
                self.setCellWidget(i, j + 1, widget)  # 项目enum控件
                self.cellWidget(i, j + 1).wheelEvent = types.MethodType(lambda obj, e: e.ignore(),
                                                                        self.cellWidget(i, j + 1))  # 禁用wheel
                size = QtCore.QSize(*self.chooseSize(field_type[field]))
                self.cellWidget(i, j + 1).setFixedSize(size)

                if field == 'complete_level':
                    face = [x[1] for x in CheckItem.Completion_Level_Flag.items()]
                    value = check_item['complete_level']
                else:
                    face = value = check_item[field]  # 控件初始化所需的数据
                self.chooseInitMethod(field_type[field])(self.cellWidget(i, j + 1), face)  # 控件基本设置
                self.chooseSetMethod(field_type[field])(self.cellWidget(i, j + 1), value)  # 项目赋值
                self.cellWidget(i, j + 1).__getattribute__(self.chooseSiganlName(
                    field_type[field])).connect(self.setEdited)  # 绑定信号
            #todo: button should follow file_list_browser, or bound as one widget with it
            button = QtWidgets.QPushButton('上传')
            button.setFixedSize(50, 50)
            button.row_index = i
            button.clicked.connect(self.on_upload_button_clicked)
            self.setCellWidget(i, 4, button)
        self.show()

    def renderSelf(self):
        '''根据model给各个控件进行赋值'''
        DataView.ResAdaptor.init_ui_size(self)
        # self.todoWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.todoWidget.customContextMenuRequested.connect(self.showTodoMenu)
        self.setStyleSheet(
            'QFrame{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;border-radius:7px; border-style: dashed;'
            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}'

            'QTableView::item:selected{	color:#DCDCDC; background:rgba(255,255,255,0);}'

            'QLabel{border-width: 0px; background:transparent;}'

            'QTextEdit{font-family:Microsoft YaHei; border-width: 2px; border-style:dashed; border-color: rgba(150, 150, 150, 40)}'

            'QLineEdit{background:transparent;border-color: rgba(150, 150, 150, 150)}'

            'QScrollBar:vertical{width: 4px;background:transparent;border: 0px;margin: 0px 0px 0px 0px;}'
            'QScrollBar::handle:vertical{background:silver; border-radius:2px;}'
            'QScrollBar::handle:vertical:hover{background:lightskyblue; border-radius:2px;}'
            'QScrollBar::add-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:bottom;subcontrol-origin: margin;}'
            'QScrollBar::sub-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:top;subcontrol-origin: margin;}'

            'QPushButton{border-style: solid;border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
            'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, '
            'x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));border-left-color:'
            ' qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(247, 247, 247), stop:1 rgb(217, 217, 217));'
            'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '
            'stop:1 rgb(222, 222, 222));border-width: 1px;border-radius: 5px;color: #202020;text-align: center;font-family: '
            'Microsoft YaHei;font:bold;font-size:7pt;padding: 0px;background-color: rgba(250,250,250,255);}'

            'QPushButton:hover{border-style: solid;border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
            'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, '
            'x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));border-left-color: '
            'qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
            'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '
            'stop:1 rgb(222, 222, 222));border-width: 1px; border-radius: 5px;color: #202020;text-align: center;'
            'font-family: Microsoft YaHei;font:bold;font-size:7pt; padding: 0px;background-color: rgb(200,225,255);}')

    def setItemDesc(self, sender, *args):
        text = sender.toPlainText()
        index = sender.row_index
        self._check_point_presenter.setModelItemDesc(index, text)
        pass

    def on_edit_signal(self):
        sender = self.sender()
        sender_type = sender.widget_type

        ...

    def setItemComleteLevel(self, sender, *args):
        index = sender.row_index
        c_code = sender.currentIndex()
        self._check_point_presenter.setModelItemCompleteLevel(index, c_code)
        pass

    def on_file_pasted(self, sender, *args):
        index = sender.row_index
        clipboard_data = DataView.clipboard.mimeData()
        print(clipboard_data.formats())
        if not clipboard_data.hasFormat('text/uri-list'):
            self.reverse_event_block()
            QtWidgets.QMessageBox.about(self, '粘贴失败', '剪贴板中没有复制的文件。')
            self.reverse_event_block()
            return
        file_names = [url.fileName() for url in clipboard_data.urls()]
        message_body = '\n'.join(file_names)
        item_label = self.data_cache['children_items'][index]['label']
        self.reverse_event_block()
        ok = QMessageBox.question(self, '粘贴文件', f'是否粘贴以下文件：\n{message_body}\n到“{item_label}"?',
                                  QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.No)
        self.reverse_event_block()
        if ok == QMessageBox.No:
            return

        file_paths = [url.toLocalFile() for url in clipboard_data.urls()]
        self.on_upload_files(index, file_paths)
        pass

    def on_upload_files(self, index, file_paths: list[str] = None):
        if not file_paths:
            file_paths = self.handleFileUploadDialog()
        if not file_paths:
            return
        new_file_array_data = self._check_point_presenter.uploadFiles(index, file_paths)
        self.cellWidget(index, 3).setDisplay(new_file_array_data)

    def reverse_event_block(self):
        '''用于临时阻断自定义的键盘鼠标信号，反转阻断状态，一般成对使用以便在临时改变阻断状态后恢复之前状态'''
        self.event_blocked = not self.event_blocked

    # def AcceptMouseKeyEvent(self, event: int):
    #     if self.event_blocked:
    #         return
    #     if event == KEY_MOUSE_EVENT.MOUSE_LEFT_PRESS:
    #         self.handleMousePressEvent()
    #     else:
    #         pass

    def handleMousePressEvent(self):
        width = self.width()
        height = self.height()
        X = QtGui.QCursor().pos().x() - self.mapToGlobal(self.geometry().topLeft()).x() + self.geometry().x()
        Y = QtGui.QCursor().pos().y() - self.mapToGlobal(self.geometry().topLeft()).y() + self.geometry().y()
        '''print('self.cursorX=',self.cursor().pos().x())
        print('GX=',self.mapToGlobal(self.geometry().topLeft()).x(),'GY=',self.mapToGlobal(self.geometry().topLeft()).y())
        print('QX=',QCursor().pos().x(),'QY=',QCursor().pos().y())
        print('Width=',width,'Height=',height,)
        print('X=',X,'Y=',Y)'''
        if 0 < X < width and 0 < Y < height:
            pass
        else:
            self.playCloseAnimation()

    def handleFileUploadDialog(self) -> list[str]:
        # file_data = arg_data.copy()
        start_path = FilePathInit.userDir.get_last_open()
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self.parent, '选择要上传的文件', start_path)
        if not file_paths:
            return []
        return file_paths

    def setEdited(self, *arg):
        self.edited = True
        sender = self.sender()
        row_index = sender.row_index
        data_type = sender.data_type
        self.__getattribute__(self.data_type_edit_method[data_type])(sender, *arg)

    def on_upload_button_clicked(self):
        sender = self.sender()
        index = sender.row_index
        # print(index)
        self.on_upload_files(index)

    def playCloseAnimation(self):
        # self.setMinimumSize(0,0)
        self.closeAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        self.closeAnimation.setStartValue(self.geometry())
        self.closeAnimation.setEndValue(
            QtCore.QRect(self.geometry().x(), self.geometry().y() + self.height() / 2, self.width(), 0))
        self.closeAnimation.setDuration(150)
        self.closeAnimation.finished.connect(self.deleteSelf)
        self.setStyleSheet(
            'QScrollBar:vertical{width: 0px;background:transparent;border: 0px;margin: 0px 0px 0px 0px;}'
            'QScrollBar::handle:vertical{background:silver; border-radius:0px;}'
            'QScrollBar::handle:vertical:hover{background:lightskyblue; border-radius:0px;}'
            'QScrollBar::add-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:bottom;subcontrol-origin: margin;}'
            'QScrollBar::sub-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:top;subcontrol-origin: margin;}')
        self.closeAnimation.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        # super(VictorEditTable, self).closeEvent(a0)

    def set_geometry(self, y_r, x_c, column_widths):
        total_width = 0
        n_assigned_cols = len(column_widths) if column_widths else 0
        # 设置总宽度
        for i in range(x_c):
            if i < n_assigned_cols:
                if column_widths[i] > self.columnWidth(i):
                    self.setColumnWidth(i, column_widths[i])
                total_width += self.columnWidth(i) + 5
            else:  # 默认列宽80
                total_width += 80
        total_width += 10
        total_height = y_r * 75 + 50
        X = self.attachedWidget.geometry().x() + self.attachedWidget.geometry().width() / 2 - total_width / 2
        # 适应屏幕
        if X + total_width > self.parent.width():  # 适应屏幕宽度
            X = self.parent.width() - total_width
        elif X < 0:
            X = 0
        else:
            pass
        Y = self.attachedWidget.geometry().y() - total_height
        if Y <= 0:
            if total_height > self.parent.height():
                Y = 0
            else:
                Y = self.attachedWidget.geometry().y() + self.attachedWidget.geometry().height()
        # self.attachedView = attachedView
        self.setGeometry(X, Y, total_width, total_height)
        self.setFocus()

    def deleteSelf(self):
        global_key_mouse_listener.removeObserver(self)
        # self.close()
        self.deleteLater()

    # def eventFilter(self,object: QtCore.QObject,event: QtCore.QEvent) -> bool:
    #     if event.type() == QEvent.MouseButtonPress:
    #         self.clearFocus()
    #     return super().eventFilter( object,event )

class CheckPointTableWidgetPop(QtWidgets.QTableWidget):
    '''支持类型，b:booleen,sliderButton; t:text,plaintextedit; e:enum,combobox; f:filearray,fileBrowser+button
        此控件类的model应该解决数据保存的问题，目前checkpoint-checkitem-filearray-file 各级中，filearray-file的保存由自身触发。
        check
    '''
    EditingFinished = pyqtSignal(CheckPoint)

    widget_chooser= {
        'booleen': {
            'choice':SliderButton,
            'init_method': SliderButton.setFontText,
            'set_method':SliderButton.setChecked,
            'get_method':SliderButton.isChecked,
            'signal_name':'toggled',
            'size':  (50, 25),
            },
        'enum':{
            'choice': QtWidgets.QComboBox,
            'init_method': QtWidgets.QComboBox.addItems,
            'set_method': QtWidgets.QComboBox.setCurrentIndex,
            'get_method': QtWidgets.QComboBox.currentIndex,
            'signal_name': 'currentIndexChanged',
            'size': (70, 20),
        },
        'text':{
            'choice': QtWidgets.QPlainTextEdit,
            'init_method': QtWidgets.QPlainTextEdit.setPlainText,
            'set_method': QtWidgets.QPlainTextEdit.setPlainText,
            'get_method': QtWidgets.QPlainTextEdit.toPlainText,
            'signal_name': 'textChanged',
            'size': (130, 70),
        },
        'file':{
            'choice': FileListBrowser,
            'init_method': FileListBrowser.setDisplay,
            'set_method': FileListBrowser.setDisplay,
            'get_method': FileListBrowser.get_file_array,
            'signal_name': 'Edited',
            'size': (140, 70),
        }

    }
    data_type_edit_method = {
        'enum':'setItemComleteLevel',
        'text':'setItemDesc',
        'file': 'on_file_pasted',
    }

    def __init__(self,
                 column_widths: list = None,
                 attachedWidget: QtWidgets.QWidget = None,
                 parent = None):
        super(CheckPointTableWidgetPop,self ).__init__( parent )
        self.parent = parent
        # self.model = check_point
        self._check_point_presenter = None
        self.attachedWidget = attachedWidget
        self.column_widths = column_widths

        self.edited = False
        self.event_blocked  = False
        self.setMouseTracking(True)
        self.mouseDoubleClickEvent = types.MethodType(lambda obj, e: e.ignore(), self)
        self.mousePressEvent = types.MethodType(lambda obj, e: e.ignore(), self)
        self.mouseMoveEvent = types.MethodType(lambda obj, e: e.ignore(), self)
        self.data_cache :dict[str,[int,str,list]]
        global_key_mouse_listener.addObserver(self)

        # self.horizontalHeader().hide()
        # self.initWidgets()
        # self.parent.installEventFilter( self )
        # self.show()

    @classmethod
    def chooseWidget(cls, type_code: str):
        widget = cls.widget_chooser[type_code]['choice']
        widget_type = type_code
        return widget, widget_type

    @classmethod
    def chooseSize(cls, type_code: str):
        return cls.widget_chooser[type_code]['size']

    @classmethod
    def chooseSetMethod(cls, type_code: str):
        return cls.widget_chooser[type_code]['set_method']

    @classmethod
    def chooseGetMethod(cls, type_code: str):
        return cls.widget_chooser[type_code]['get_method']

    @classmethod
    def chooseInitMethod(cls, type_code: str):
        return cls.widget_chooser[type_code]['init_method']

    @classmethod
    def chooseSiganlName(cls, type_code: str):
        return cls.widget_chooser[type_code]['signal_name']

    @property
    def check_point_presenter(self):
        return self._check_point_presenter
        pass

    @check_point_presenter.setter
    def check_point_presenter(self, presenter):
        self._check_point_presenter = presenter
        pass

    def setupView(self, data: dict[str, [int,str, dict]], field_type:dict, fields_to_edit:list[str]):
        '''

        '''
        self.data_cache = data.copy()
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 禁止编辑
        header = ['项目', '情况描述', '进度', '文件','..']
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)
        # self.horizontalHeader().setMaximumHeight(25)
        nRow = len(data['children_items'])
        self.setRowCount(nRow)
        self.renderSelf()
        for i, width in enumerate(self.column_widths):
            self.setColumnWidth( i, width )
        self.verticalHeader().setDefaultSectionSize(75)
        self.set_geometry(nRow, 5, self.column_widths)
        for i, check_item in enumerate(data['children_items']):
            Qitem = QtWidgets.QTableWidgetItem(check_item['label'])
            Qitem.setTextAlignment(Qt.AlignRight)
            self.setItem(i, 0, Qitem)  # 项目标题
            for j, field in enumerate(fields_to_edit):
                widget_class, widget_type =  self.chooseWidget(field_type[field])
                widget = widget_class(parent = self)
                widget.row_index = i
                widget.data_type = widget_type
                self.setCellWidget(i, j+1, widget)  # 项目enum控件
                self.cellWidget(i, j+1).wheelEvent = types.MethodType(lambda obj, e: e.ignore(),
                                                                    self.cellWidget(i, j+1))  # 禁用wheel
                size = QtCore.QSize(*self.chooseSize(field_type[field]))
                self.cellWidget(i, j+1).setFixedSize(size)

                if field == 'complete_level':
                    face =[x[1] for x in CheckItem.Completion_Level_Flag.items()]
                    value = check_item['complete_level']
                else:
                    face = value = check_item[field] # 控件初始化所需的数据
                self.chooseInitMethod(field_type[field])(self.cellWidget(i, j+1), face)  # 控件基本设置
                self.chooseSetMethod(field_type[field])(self.cellWidget(i, j+1), value)  # 项目赋值
                self.cellWidget(i, j+1).__getattribute__(self.chooseSiganlName(
                    field_type[field])).connect(self.setEdited)  # 绑定信号
            button = QtWidgets.QPushButton('上传')
            button.setFixedSize(50,50)
            button.row_index = i
            button.clicked.connect(self.on_upload_button_clicked)
            self.setCellWidget(i, 4, button)
        self.show()

    def renderSelf(self):
        '''根据model给各个控件进行赋值'''
        DataView.ResAdaptor.init_ui_size( self )
        # self.todoWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.todoWidget.customContextMenuRequested.connect(self.showTodoMenu)
        self.setStyleSheet(
            'QFrame{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;border-radius:7px; border-style: dashed;'
            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}'
            
            'QTableView::item:selected{	color:#DCDCDC; background:rgba(255,255,255,0);}'
            
            'QLabel{border-width: 0px; background:transparent;}'
            
            'QTextEdit{font-family:Microsoft YaHei; border-width: 2px; border-style:dashed; border-color: rgba(150, 150, 150, 40)}'
            
            'QLineEdit{background:transparent;border-color: rgba(150, 150, 150, 150)}'
            
            'QScrollBar:vertical{width: 4px;background:transparent;border: 0px;margin: 0px 0px 0px 0px;}'
            'QScrollBar::handle:vertical{background:silver; border-radius:2px;}'
            'QScrollBar::handle:vertical:hover{background:lightskyblue; border-radius:2px;}'
            'QScrollBar::add-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:bottom;subcontrol-origin: margin;}'
            'QScrollBar::sub-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:top;subcontrol-origin: margin;}'
            
            'QPushButton{border-style: solid;border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
            'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, '
            'x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));border-left-color:'
            ' qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(247, 247, 247), stop:1 rgb(217, 217, 217));'
            'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '
            'stop:1 rgb(222, 222, 222));border-width: 1px;border-radius: 5px;color: #202020;text-align: center;font-family: '
            'Microsoft YaHei;font:bold;font-size:7pt;padding: 0px;background-color: rgba(250,250,250,255);}'
            
            'QPushButton:hover{border-style: solid;border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
            'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, '
            'x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));border-left-color: '
            'qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
            'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '
            'stop:1 rgb(222, 222, 222));border-width: 1px; border-radius: 5px;color: #202020;text-align: center;'
            'font-family: Microsoft YaHei;font:bold;font-size:7pt; padding: 0px;background-color: rgb(200,225,255);}' )

    def setItemDesc(self, sender, *args):
        text = sender.toPlainText()
        index = sender.row_index
        self._check_point_presenter.setModelItemDesc(index, text)
        pass
        ...

    def setItemComleteLevel(self, sender, *args):
        index = sender.row_index
        c_code = sender.currentIndex()
        self._check_point_presenter.setModelItemCompleteLevel(index, c_code)
        pass

    def on_file_pasted(self, sender, *args):
        index = sender.row_index
        clipboard_data = DataView.clipboard.mimeData()
        print(clipboard_data.formats())
        if not clipboard_data.hasFormat('text/uri-list'):
            self.reverse_event_block()
            QtWidgets.QMessageBox.about(self, '粘贴失败', '剪贴板中没有复制的文件。')
            self.reverse_event_block()
            return
        file_names = []
        for Qurl in clipboard_data.urls():
            url = Qurl.toLocalFile()
            url = "{}".format(url)
            if os.path.isdir(url):
                self.reverse_event_block()
                QMessageBox.warning(self,'粘贴错误', '请选择文件！不允许粘贴拷贝目录！')
                self.reverse_event_block()
                return
            file_names.append(Qurl.fileName())
        message_body = '\n'.join(file_names)
        item_label = self.data_cache['children_items'][index]['label']
        self.reverse_event_block()
        ok = QMessageBox.question(self, '粘贴文件', f'是否粘贴以下文件：\n{message_body}\n到“{item_label}"?',
                                  QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.No)
        self.reverse_event_block()
        if ok == QMessageBox.No:
            return

        file_paths = ["{}".format(url.toLocalFile()) for url in clipboard_data.urls()]
        self.on_upload_files(index, file_paths)
        pass

    def on_data_change(self, data_stream):
        ...

    def on_upload_files(self, index, file_paths: list[str] = None):
        if not file_paths:
            file_paths = self.handleFileUploadDialog()
        if not file_paths:
            return
        new_file_array_data = self._check_point_presenter.uploadFiles(index, file_paths)
        self.cellWidget(index, 3).setDisplay(new_file_array_data)

    def raiseFileExist(self,file_name:str):
        self.reverse_event_block()
        ok = QMessageBox.question(self, '文件已存在', f'文件:\n{file_name}\n已存在，是否覆盖原有文件？', QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.No)
        self.reverse_event_block()
        if ok == ok == QMessageBox.Yes:
            return True
        else:
            return False

    def raiseSrcFileNotExist(self, file_name:str):
        self.reverse_event_block()
        QMessageBox.about(self, '目标文件不存在', f'被拷贝的文件\n{file_name}\n不存在，或已被移动。')
        self.reverse_event_block()

    def reverse_event_block(self):
        '''用于临时阻断自定义的键盘鼠标信号，反转阻断状态，一般成对使用以便在临时改变阻断状态后恢复之前状态'''
        self.event_blocked = not self.event_blocked

    def AcceptMouseKeyEvent(self, event: int):
        if self.event_blocked:
            return
        if event == KEY_MOUSE_EVENT.MOUSE_LEFT_PRESS:
            self.handleMousePressEvent()
        else:
            pass

    def handleMousePressEvent(self):
        width = self.width()
        height = self.height()
        X = QtGui.QCursor().pos().x() - self.mapToGlobal(self.geometry().topLeft()).x() + self.geometry().x()
        Y = QtGui.QCursor().pos().y() - self.mapToGlobal(self.geometry().topLeft()).y() + self.geometry().y()
        '''print('self.cursorX=',self.cursor().pos().x())
        print('GX=',self.mapToGlobal(self.geometry().topLeft()).x(),'GY=',self.mapToGlobal(self.geometry().topLeft()).y())
        print('QX=',QCursor().pos().x(),'QY=',QCursor().pos().y())
        print('Width=',width,'Height=',height,)
        print('X=',X,'Y=',Y)'''
        if 0 < X < width and 0 < Y < height:
            pass
        else:
            self.playCloseAnimation()

    def handleFileUploadDialog(self) -> list[str]:
        # file_data = arg_data.copy()
        start_path = FilePathInit.userDir.get_last_open()
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self.parent, '选择要上传的文件', start_path)
        if not file_paths:
            return []
        return file_paths

    def setEdited(self, *arg):
        self.edited = True
        sender = self.sender()
        row_index = sender.row_index
        data_type = sender.data_type
        self.__getattribute__(self.data_type_edit_method[data_type])(sender, *arg)

    def on_upload_button_clicked(self):
        sender = self.sender()
        index = sender.row_index
        # print(index)
        self.on_upload_files(index)
    #
    # def mouseMoveEvent(self,e: QtGui.QMouseEvent) -> None:
    #     if self.hasFocus():
    #         pass
    #     else:
    #         self.setFocus()
    #
    # def focusOutEvent(self,e: QtGui.QFocusEvent) -> None:
    #     width = self.width()
    #     height = self.height()
    #     X = QtGui.QCursor().pos().x() - self.mapToGlobal( self.geometry().topLeft() ).x() + self.geometry().x()
    #     Y = QtGui.QCursor().pos().y() - self.mapToGlobal( self.geometry().topLeft() ).y() + self.geometry().y()
    #     '''print('self.cursorX=',self.cursor().pos().x())
    #     print('GX=',self.mapToGlobal(self.geometry().topLeft()).x(),'GY=',self.mapToGlobal(self.geometry().topLeft()).y())
    #     print('QX=',QCursor().pos().x(),'QY=',QCursor().pos().y())
    #     print('Width=',width,'Height=',height,)
    #     print('X=',X,'Y=',Y)'''
    #     if 0 < X < width and 0 < Y < height:
    #         # if self.view().hasMouse() :
    #         QtWidgets.QTableView.focusOutEvent( self,e )
    #     else:
    #         # if self.edited:
    #         #     data = self.getTableData()
    #         #     self.EditingFinished.emit( data )
    #         self.playCloseAnimation()
    #         QtWidgets.QTableWidget.focusOutEvent( self,e )

    def playCloseAnimation(self):
        # self.setMinimumSize(0,0)
        self.closeAnimation = QtCore.QPropertyAnimation( self, b'geometry' )
        self.closeAnimation.setStartValue( self.geometry() )
        self.closeAnimation.setEndValue(
            QtCore.QRect( self.geometry().x(),self.geometry().y() + self.height() / 2,self.width(),0 ) )
        self.closeAnimation.setDuration( 150 )
        self.closeAnimation.finished.connect( self.deleteSelf )
        self.setStyleSheet(
            'QScrollBar:vertical{width: 0px;background:transparent;border: 0px;margin: 0px 0px 0px 0px;}'
            'QScrollBar::handle:vertical{background:silver; border-radius:0px;}'
            'QScrollBar::handle:vertical:hover{background:lightskyblue; border-radius:0px;}'
            'QScrollBar::add-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:bottom;subcontrol-origin: margin;}'
            'QScrollBar::sub-line:vertical{background: transparent;margin: 0px;border-width: 0px;'
            'height:0px;width:0px;subcontrol-position:top;subcontrol-origin: margin;}')
        self.closeAnimation.start( QtCore.QAbstractAnimation.DeleteWhenStopped )

        # super(VictorEditTable, self).closeEvent(a0)

    def set_geometry(self,y_r, x_c, column_widths):
        total_width = 0
        n_assigned_cols = len( column_widths ) if column_widths else 0
        # 设置总宽度
        for i in range( x_c ):
            if i < n_assigned_cols:
                if column_widths[i] > self.columnWidth( i ):
                    self.setColumnWidth( i,column_widths[i] )
                total_width += self.columnWidth( i ) + 5
            else:  # 默认列宽80
                total_width += 80
        total_width += 10
        total_height = y_r * 75 + 50
        X = self.attachedWidget.geometry().x() + self.attachedWidget.geometry().width() / 2 - total_width / 2
        # 适应屏幕
        if X + total_width > self.parent.width():  # 适应屏幕宽度
            X = self.parent.width() - total_width
        elif X < 0:
            X = 0
        else:
            pass
        Y = self.attachedWidget.geometry().y() - total_height
        if Y <= 0:
            if total_height > self.parent.height():
                Y = 0
            else:
                Y = self.attachedWidget.geometry().y() + self.attachedWidget.geometry().height()
        # self.attachedView = attachedView
        self.setGeometry( X,Y,total_width,total_height )
        self.setFocus()

    def deleteSelf(self):
        global_key_mouse_listener.removeObserver(self)
        # self.close()
        self.deleteLater()

    # def eventFilter(self,object: QtCore.QObject,event: QtCore.QEvent) -> bool:
    #     if event.type() == QEvent.MouseButtonPress:
    #         self.clearFocus()
    #     return super().eventFilter( object,event )
