from copy import deepcopy

import DataView
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QTextEdit, QSlider, QLineEdit, QCheckBox, QFrame, QDialogButtonBox, QCompleter,\
    QAbstractButton,\
    QItemDelegate
from PyQt5.QtCore import QStringListModel, Qt, QAbstractProxyModel, QModelIndex, QItemSelection, QRectF, QPointF, QTime,\
    QUrl
from PyQt5.QtGui import QBitmap, QPainter, QColor, QKeyEvent, QStandardItem, QStandardItemModel, QPixmap
from PyQt5.Qt import QCursor, pyqtSignal, QEvent, QMouseEvent, QPoint
from ID_Generate import Snow
import ConnSqlite as CS
import DataCenter, GColour, ToDoUnitUi
import sys, types, os, re, time, csv, datetime, json
from core.KitModels import CheckItem, FileArray, File, CheckPoint
from core.GlobalListener import global_logger
from DataCenter import office_job_dict

def new_wheelEvent(self, e):
    e.ignore()
    pass


def new_focusOutEvent(self, e):
    '''重写lineEdit的focusOut事件'''
    if e.reason() == Qt.ActiveWindowFocusReason:
        return
    else:
        QLineEdit.focusOutEvent(self, e)


def textEdit_focusOutEvent(self, e):
    ##这里因为parent的传递不好处理，所有就没有在这个模块使用该函数
    self.parent.textEditingFinshed(self)

    QTextEdit.focusOutEvent(self, e)


def new_doubleClickEvent(self, e):
    self.setReadOnly(False)
    # QTextEdit.mouseDoubleClickEvent(self,e)


class QTextEdit(QTextEdit):
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


class MyQTextEdit(QTextEdit):  # 自定义textEdit的鼠标双击事件

    # 自定义单击信号
    # clicked = pyqtSignal()
    # 自定义双击信号
    DoubleClicked = pyqtSignal()
    LoseFocus = pyqtSignal()
    EditFinished = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_text = ''
        self.edited = False  # 每次给textEdit赋值之后都要恢复成False，因为这个参数是用来作为判断FocusOut信号的槽函数是否执行的的条件
        self.textChanged.connect(self.setEdited)
        self.setReadOnly(True)

    # 重写鼠标双击事件
    def mouseDoubleClickEvent(self, e):  # 重写双击事件
        self.DoubleClicked.emit()

    '''def focusOutEvent(self,e):#重写失去焦点事件
        self.LoseFocus.emit()'''

    def setEdited(self, edited = True):
        self.edited = edited

    def setText(self, txt):
        self.init_text = txt
        QTextEdit.setText(self, txt)
        self.edited = False  # 每次给textEdit赋值之后都要恢复成False，因为这个参数是用来作为判断FocusOut信号的槽函数是否执行的的条件

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Escape:
            self.setText(self.init_text)
            # self.edited = False # 避免FocusOut信号触发保存操作
            self.clearFocus()
        QTextEdit.keyPressEvent(self, e)

class SemiEditableTextEdit(MyQTextEdit):
    def __init__(self):
        super().__init__()

    def mouseDoubleClickEvent(self, e):  # 重写双击事件
        self.DoubleClicked.emit()
        self.setReadOnly(False)
    def focusOutEvent(self, e):  # 重写失去焦点事件
        if e.reason() == Qt.PopupFocusReason:
            return
        #信号返回自身所在行号
        self.setReadOnly(True)
        if self.edited:
            self.EditFinished.emit(self.toPlainText())
        self.edited = False
        QTextEdit.focusOutEvent(self, e)

    def reverseEdit(self):
        self.setText(self.init_text)
        self.setReadOnly(False)


class FileListBrowser(QtWidgets.QTextBrowser):
    '''承载的数据对象是FileArray，由于该数据类自身默认数据改变后同步到数据库，所以无需单独的保存步骤'''
    Edited = pyqtSignal(dict)

    def __init__(self, parent=None, file_array: dict = None):
        super(FileListBrowser, self).__init__(parent=parent)
        self.file_array = deepcopy(file_array)
        self.parent = parent
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.on_file_link_clicked)

    @classmethod
    def renderFileHtml(cls, file_array: dict):
        link_labels = []
        if file_array:
            for i, file in enumerate(file_array['items']):
                file_name = file['file_name']
                suffix = os.path.splitext(file_name)[1][1:]
                # label = f'<tr><td><img src="./images/file_icons64X64/{suffix}.png" alt="[{suffix}]" width="16" height="16"></td><td><a style="color:#000000;font-size:9pt;text-decoration:none;" ' \
                #         f'href="{file["path"]}#{i}">{file["file_name"]} </a></td></tr>'
                label = f'<a style="color:#000000;font-size:9pt;text-decoration:none;" href="{file["path"]}#{i}">'\
                        f'<img src="./images/file_icons64X64/{suffix}.png" alt="[{suffix}]" width="16" height="16">'\
                        f'{file["file_name"]} </a>'
                link_labels.append(label)
            return '<br>'.join(link_labels)
        else:
            return None

    def setDisplay(self, file_array: dict = None):
        if file_array:
            self.file_array = deepcopy(file_array)
            file_html = self.renderFileHtml(file_array)
            self.setText(file_html)
        else:
            self.refresh()

    def refresh(self):
        file_html = self.renderFileHtml(self.file_array)
        self.setText(file_html)
        if not self.file_array:
            return
        ids = []
        for item in self.file_array['items']:
            ids.append(item['_id'])
        self.file_array['ids'] = ids

    def remove_file(self, index: int):
        if not self.file_array: return
        self.file_array['items'].pop(index)
        self.refresh()
        self.Edited.emit(self.file_array)

    def add_file(self, file: dict):
        self.file_array['items'].append(file)
        self.refresh()
        self.Edited.emit(self.file_array)

    def get_file_array(self):
        return self.file_array

    def on_file_link_clicked(self, *args):
        url = args[0]
        file_path = url.adjusted(QUrl.RemoveFragment).url()
        file_index = url.fragment()
        try:
            os.startfile(os.path.abspath(file_path))
            return
        except:
            self.parent.reverse_event_block()
            QtWidgets.QMessageBox.about(self, '打开失败', '未找到文件。')
            self.parent.reverse_event_block()
            return

    def setDisplay(self, file_array: FileArray = None):
        if file_array:
            self.file_array = file_array
            file_html = self.renderFileHtml(file_array)
            self.setText(file_html)
        else:
            self.refresh()

    def refresh(self):
        file_html = self.renderFileHtml(self.file_array)
        self.setText(file_html)

    def remove_file(self, index: int):
        self.file_array.pop_item(index)
        self.refresh()
        self.Edited.emit()

    def add_file(self, file: File):
        self.file_array.add_item(file)
        self.refresh()
        self.Edited.emit()

    def get_file_array(self):
        return self.file_array


class MySlider(QSlider):
    def __init__(self, attachedWidget, attachedView, parent=None):
        super(MySlider, self).__init__(parent)
        self.parent = parent
        print('attachedWidget.geometry()', attachedWidget.geometry())
        X = attachedWidget.geometry().x() - 60
        Y = attachedWidget.geometry().y() + 20
        self.attachedView = attachedView
        self.setGeometry(X, Y, 220, 20)
        self.setOrientation(Qt.Horizontal)
        self.setFocus()

    def focusOutEvent(self, a0: QtGui.QFocusEvent):
        if hasattr(self.attachedView, 'on_slider_close'):
            self.attachedView.on_slider_close()
        self.close()


class StatusCheckFrame(QFrame):
    chk_names = ['上线', '关注', '机会', '订单']  # 复选按钮名称
    statusClicked = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(StatusCheckFrame, self).__init__(parent)
        # 生成按钮
        self.resize(70, 100)
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        for i, name in enumerate(self.chk_names):
            new_name = f'chk_{i}'
            exec(new_name + '=QCheckBox("%s",self)' % (name), globals(), locals())
            exec(new_name + '.move(4,25*i +3)')
        # print('globals',globals())
        # print('locals',locals())
        # 上线
        # check_in_act = SliderButton(parent=parent,fontText='上线',colorChecked=GColour.ProjectRGBColour.ProjectInAct)

    def statusClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.setFocus()
        self.statusClicked.emit(self.getCheckedStatuses())

    def focusInEvent(self, a0: QtGui.QFocusEvent) -> None:
        self.setFocus()

    def setCheckedStatuses(self, init_check_status: list):
        if len(init_check_status) != len(self.chk_names):
            try:
                raise ValueError("numbers of check_states and chk_names don't match. "
                                 "check_names are {}".format(self.chk_names))
            except ValueError as e:
                print(e)
        for i, name in enumerate(self.chk_names):
            bo = self.findChildren(QCheckBox)[i]
            bo.setChecked(init_check_status[i])
            bo.clicked.connect(self.statusClickEvent)

    def getCheckedStatuses(self):
        check_bools = []
        for i in range(len(self.chk_names)):
            bo = self.findChildren(QCheckBox)[i].isChecked()
            check_bools.append(bo)
        return tuple(check_bools)

    def getCheckedLabels(self):
        check_labels = []
        for i in range(len(self.chk_names)):
            bo = self.findChildren(QCheckBox)[i].isChecked()
            if bo:
                check_labels.append(self.chk_names[i])
        return tuple(check_labels)


class ProxyModel(QAbstractProxyModel):

    def __init__(self, model, placeholderText='---', parent=None):
        super().__init__(parent)
        self._placeholderText = placeholderText
        self.setSourceModel(model)

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        return self.createIndex(row, column)

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        return QModelIndex()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return self.sourceModel().rowCount() + 1 if self.sourceModel() else 0

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return self.sourceModel().columnCount() if self.sourceModel() else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if index.row() == 0 and role == Qt.DisplayRole:
            return self._placeholderText
        elif index.row() == 0 and role == Qt.EditRole:
            return None
        else:
            return super().data(index, role)

    def mapFromSource(self, sourceIndex: QModelIndex):
        return self.index(sourceIndex.row() + 1, sourceIndex.column())

    def mapToSource(self, proxyIndex: QModelIndex):
        return self.sourceModel().index(proxyIndex.row() - 1, proxyIndex.column())

    def mapSelectionFromSource(self, sourceSelection: QItemSelection):
        return super().mapSelection(sourceSelection)

    def mapSelectionToSource(self, proxySelection: QItemSelection):
        return super().mapSelectionToSource(proxySelection)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if not self.sourceModel():
            return None
        if orientation == Qt.Vertical:
            return self.sourceModel().headerData(section - 1, orientation, role)
        else:
            return self.sourceModel().headerData(section, orientation, role)

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        return self.sourceModel().removeRows(row, count - 1)

class CompanyCreateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, company_name: str = None, company_name_exist: list = None):
        super(CompanyCreateDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        self.company_name_exist = company_name_exist
        self.country = None
        self.company_name = None
        self.province = None
        self.city = None
        self.town = None
        self.setWindowTitle('公司基本信息')
        # 主表单
        self.mainLayout = QtWidgets.QFormLayout(self)
        self.mainLayout.setSpacing(16)
        minWidth = 120

        lable = QtWidgets.QLabel(self)
        lable.setText('公司名称(简称)')
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.focusOutEvent = types.MethodType(new_focusOutEvent, self.lineEdit)
        self.mainLayout.addRow(lable, self.lineEdit)
        self.lineEdit.editingFinished.connect(self.checkLineInputValidation)
        self.comp_model_1 = QStringListModel(self.company_name_exist)
        self.m_completer = QCompleter(self.comp_model_1, self)
        self.m_completer.setFilterMode(QtCore.Qt.MatchContains)
        self.lineEdit.setCompleter(self.m_completer)
        if company_name:
            self.lineEdit.setText(company_name)

        lable_country = QtWidgets.QLabel(self)
        lable_country.setText('国家/country')
        # lable_country.setAlignment
        self.combo_country = QtWidgets.QComboBox(self)
        # self.combo_country.setEditable(True)
        self.mainLayout.addRow(lable_country, self.combo_country)
        # self.combo_country.currentIndexChanged.connect(s)

        lable_province = QtWidgets.QLabel(self)
        lable_province.setText('省份/state')
        self.combo_province = QtWidgets.QComboBox(self)
        self.combo_province.currentIndexChanged.connect(self.on_province_change)
        self.mainLayout.addRow(lable_province, self.combo_province)
        # self.combo_province.setEditable(True)
        # self.combo_province.lineEdit().setPlaceholderText('省份/state')

        lable_city = QtWidgets.QLabel(self)
        lable_city.setText('城市/city')
        self.combo_city = QtWidgets.QComboBox(self)
        self.combo_city.currentIndexChanged.connect(self.on_city_change)
        self.mainLayout.addRow(lable_city, self.combo_city)
        # self.combo_city.setEditable(True)
        # self.combo_city.lineEdit().setPlaceholderText('城市/city')

        label_town = QtWidgets.QLabel(self)
        label_town.setText('县/town')
        self.combo_town = QtWidgets.QComboBox(self)
        self.combo_town.currentIndexChanged.connect(self.on_town_change)
        self.mainLayout.addRow(label_town, self.combo_town)
        # self.combo_town.setEditable(True)
        # self.combo_town.lineEdit().setPlaceholderText('县/town')

        self.bbOkCancel = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setDefault(True)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setEnabled(False)
        self.bbOkCancel.accepted.connect(self.accept)
        self.bbOkCancel.rejected.connect(self.reject)
        self.mainLayout.addRow(self.bbOkCancel)

        self.geo_model = DataCenter.GeoModel()
        self.combo_country.wheelEvent = types.MethodType(new_wheelEvent, self.combo_country)
        self.combo_country.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.combo_province.wheelEvent = types.MethodType(new_wheelEvent, self.combo_province)
        self.combo_province.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.combo_city.wheelEvent = types.MethodType(new_wheelEvent, self.combo_city)
        self.combo_city.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.combo_town.wheelEvent = types.MethodType(new_wheelEvent, self.combo_town)
        self.combo_town.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.combo_province.setCurrentIndex(-1)
        # self.combo_city.setCurrentIndex(-1)
        # self.combo_town.setCurrentIndex(-1)
        self.combo_province.setPlaceholderText(u'省份')
        self.combo_city.setPlaceholderText(u'城市')
        self.combo_town.setPlaceholderText(u'县')
        self.combo_town.setEditText('县')
        # self.combo_town.

        self.provinces = self.geo_model.getProvinceItems()
        self.cities = None
        self.towns = None
        self.combo_province.addItems([province[1] for province in self.provinces])

    def checkLineInputValidation(self):
        if not self.lineEdit.text():
            return

        valid_company_name = re.sub('[\W-]', '', self.lineEdit.text())
        valid_company_name = re.sub('[0-9]', '', valid_company_name)
        if not valid_company_name:  # 去除所有非法符号后, 未输入有效字符
            QtWidgets.QMessageBox.about(self, '无效名称', '该公司名称无效，\n\n请重新输入！')
            self.lineEdit.clear()
            self.lineEdit.setFocus()
            return

        if self.company_name_exist and self.lineEdit.text() in self.company_name_exist:
            QtWidgets.QMessageBox.about(self, '命名重复', '该客户名称已经存在，\n请重新输入！')
            self.lineEdit.setFocus()
            self.lineEdit.selectAll()
            return

        self.company_name = self.lineEdit.text()
        if self.city:
            self.bbOkCancel.button(QDialogButtonBox.Ok).setEnabled(True)

    def on_province_change(self, index):
        if index == -1:
            return
        print(index)
        print('wheel_changeP', self.combo_province.currentIndex())
        self.province = self.provinces[self.combo_province.currentIndex()][0]  # 省份代码
        # 清空后列数据
        self.city = None
        self.town = None
        # 重置后列控件
        self.combo_city.clear()
        self.combo_town.clear()
        self.combo_town.setCurrentIndex(-1)
        self.combo_city.setCurrentIndex(-1)
        # 初始化后列数据和控件
        self.cities = self.geo_model.getCityItems(self.province)
        if self.cities:
            self.combo_city.addItems([city[1] for city in self.cities])

        self.towns = None
        # self.setGeoComboboxes()

    def on_city_change(self):
        print('wheel_changeC', self.combo_city.currentIndex())
        if self.combo_city.currentIndex() == -1:
            return
        self.city = self.cities[self.combo_city.currentIndex()][0]
        # 清空后列数据
        self.town = None
        # 重置后列控件
        self.combo_town.clear()
        self.combo_town.setCurrentIndex(-1)
        # 初始化后列数据和控件
        self.towns = self.geo_model.getTownItems(self.city, self.province)
        if self.towns:
            self.combo_town.addItems([town[1] for town in self.towns])
        if self.company_name:
            self.bbOkCancel.button(QDialogButtonBox.Ok).setEnabled(True)

        # self.setGeoComboboxes()

    def on_town_change(self):
        print('wheel_changeT', self.combo_town.currentIndex())
        if self.combo_town.currentIndex() == -1:
            return
        self.town = self.towns[self.combo_town.currentIndex()][0]

    @staticmethod
    def getAllInput(parent=None, company_name: str = None, company_name_exist: list = None):
        dialog = CompanyCreateDialog(parent=parent, company_name=company_name, company_name_exist=company_name_exist)
        result = dialog.exec_()
        company_name = dialog.company_name
        country = dialog.country
        province = dialog.province
        city = dialog.city
        town = dialog.town
        return (company_name, country, province, city, town, result == QtWidgets.QDialog.Accepted)

class JobTypeEditDialog(QtWidgets.QDialog):
    def __init__(self, parent=None ):
        super(JobTypeEditDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle('编辑任务分类名称')
        # 主表单
        self.mainLayout = QtWidgets.QFormLayout(self)
        self.mainLayout.setSpacing(16)
        minWidth = 120

        self.edits=[]
        for type_code, type_name in office_job_dict.items():
            lable = QtWidgets.QLabel(self)
            lable.type_code = type_code
            lable.setText('%s：'%type_code)
            text_edit = SemiEditableTextEdit()
            text_edit.setFixedHeight(30 * DataView.FIX_SIZE_WIDGET_SCALING)
            text_edit.setText(type_name)
            text_edit.type_code = type_code
            text_edit.EditFinished.connect(self.saveEdit)
            self.edits.append((lable, text_edit))

        for lable, edit in self.edits:
            self.mainLayout.addRow(lable, edit)

        self.bbOkCancel = QDialogButtonBox(QDialogButtonBox.Ok , QtCore.Qt.Horizontal, self)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setDefault(True)
        self.bbOkCancel.accepted.connect(self.accept)
        self.mainLayout.addRow(self.bbOkCancel)
    def saveEdit(self, name):
        sender = self.sender()
        type_code = sender.type_code
        _, message = DataCenter.update_office_job_types(type_code, name)
        if not _ == 0:
            QtWidgets.QMessageBox.about(self, '输入错误', message)
            sender.reverseEdit()


    @staticmethod
    def start(parent=None):
        dialog = JobTypeEditDialog(parent=parent)
        result = dialog.exec_()

class ComboBoxDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, title: str = None, item_name=None, items=None, Editable=True):
        super(ComboBoxDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        self.items = items
        self.item = None
        self.setWindowTitle(title)
        # 主表单
        self.mainLayout = QtWidgets.QFormLayout(self)
        self.mainLayout.setSpacing(16)
        self.label = QtWidgets.QLabel(self)
        self.label.setText(item_name)
        self.label.setAlignment(QtCore.Qt.AlignRight)
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.addItems(self.items)
        self.comboBox.setEditable(Editable)
        if Editable:
            self.comboBox.lineEdit().completer().setFilterMode(QtCore.Qt.MatchContains)
            self.comboBox.lineEdit().completer().setCompletionMode(QCompleter.PopupCompletion)
            if self.items:
                self.comboBox.lineEdit().setPlaceholderText(self.items[0])
        self.comboBox.setCurrentIndex(-1)
        self.comboBox.currentIndexChanged.connect(self.setItem)
        self.mainLayout.addRow(self.label, self.comboBox)
        self.bbOkCancel = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setDefault(True)
        # self.bbOkCancel.button(QDialogButtonBox.Ok).setEnabled(False)
        self.bbOkCancel.accepted.connect(self.accept)
        self.bbOkCancel.rejected.connect(self.reject)
        self.mainLayout.addRow(self.bbOkCancel)
        # self.comboBox.showPopup()

    def setItem(self, i):
        if self.comboBox.lineEdit():
            if self.comboBox.lineEdit().text() in self.items:
                self.item = self.items[i]
        else:
            self.item = self.items[i]

    @staticmethod
    def getItem(parent=None, title: str = None, item_name=None, items=None, Editable=True):
        dialog = ComboBoxDialog(parent=parent, title=title, item_name=item_name, items=items, Editable=True)
        result = dialog.exec_()
        item = dialog.comboBox.lineEdit().text()
        return (item, result)

    @staticmethod
    def getIndex(parent=None, title: str = None, item_name=None, items=None, Editable=False):
        dialog = ComboBoxDialog(parent=parent, title=title, item_name=item_name, items=items, Editable=False)
        result = dialog.exec_()
        index = dialog.comboBox.currentIndex()
        return (index, result)


class DirectorChooseBox(QtWidgets.QDialog):
    '''初次启动设置个人文件目录的对话框'''

    def __init__(self, title: str, hint_text: str = None, parent=None):
        super(DirectorChooseBox, self).__init__(parent)
        self.title = title
        self.hint_text = hint_text
        # self.setWindowFlags(QtCore.Qt.Window|Qt.WindowCloseButtonHint)
        self.setWindowTitle(self.title)
        self.setFixedSize(800, 300)

        self.HLayOut = QtWidgets.QHBoxLayout(self)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setPlaceholderText(self.hint_text)
        self.lineEdit.setFixedSize(200, 30)
        self.HLayOut.addWidget(self.lineEdit)

        self.path_button = QtWidgets.QPushButton(self)
        self.path_button.setText('目录..')
        self.path_button.clicked.connect(self.on_select_button_clicked)
        self.path_button.setMaximumWidth(40)
        self.HLayOut.addWidget(self.path_button)

        self.dialog_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.dialog_button.button(QDialogButtonBox.Ok).setDefault(True)
        self.dialog_button.button(QDialogButtonBox.Ok).setEnabled(False)
        self.dialog_button.accepted.connect(self.accept)
        self.dialog_button.rejected.connect(self.reject)
        self.HLayOut.addWidget(self.dialog_button)

    def on_select_button_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, '选择个人数据存放路径', 'C:/')
        if os.path.isdir(path):
            self.dialog_button.button(QDialogButtonBox.Ok).setEnabled(True)
        self.lineEdit.setText(path)

    @staticmethod
    def getDirectory(title: str, hint_text: str = None, parent=None):
        dialog = DirectorChooseBox(title=title, hint_text=hint_text, parent=parent)
        result = dialog.exec_()
        directory = dialog.lineEdit.text()
        return (directory, result == QtWidgets.QDialog.Accepted)


class SliderButton(QAbstractButton):

    def __init__(self, fontText: str = None, parent=None, colorChecked: tuple = None,
                 outer_unchecked_alpha=50, outer_checked_alpha=110, inner_alpha=200):
        super(SliderButton, self).__init__(parent)
        # 内部圆直径
        # self.innerDiameter = self.height() -2
        # 是否选中标志位
        self.checked = False
        # 鼠标形状
        self.setCursor(Qt.PointingHandCursor)
        # 设置遮罩，固定形状
        # bitmap = QBitmap('./images/btnMask.png')
        # self.resize(bitmap.width(),bitmap.height())
        # self.setMask(bitmap)
        # 内边距
        self.innerMargin = 2
        # x坐标偏移量
        self.offset = self.innerMargin
        # 内部圆背景色
        self.innerColor = QColor(240, 240, 250)
        # 内部圆背景色选中
        self.innerColorChecked = QColor(255, 255, 255, inner_alpha)
        # 外部背景色
        self.outerColor = QColor(170, 170, 170, outer_unchecked_alpha)
        # 外部背景色选中
        if colorChecked:
            self.outerColorChecked = QColor(*colorChecked, outer_checked_alpha)
        else:
            self.outerColorChecked = QColor(51, 153, 255, outer_checked_alpha)

        self.fontText = fontText

        # 定时器ID
        self.timeId = None

    def setFontText(self, fontText: str):
        self.fontText = fontText

    def setColourChecked(self, colourChecked: tuple):
        self.outerColorChecked = QColor(*colourChecked)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(SliderButton, self).resizeEvent(a0)
        width = a0.size().width()
        height = a0.size().height()
        self.innerDiameter = int(height * 0.8)

    def setFixedSize(self, a0: QtCore.QSize) -> None:
        super(SliderButton, self).setFixedSize(a0)
        width = a0.width()
        height = a0.height()
        self.innerDiameter = int(height * 0.8)

    def setGeometry(self, a0: QtCore.QRect) -> None:
        super(SliderButton, self).setGeometry(a0)
        width = a0.width()
        height = a0.height()
        self.innerDiameter = int(height * 0.8)

    def setFixedHeight(self, h: int) -> None:
        super(SliderButton, self).setFixedHeight(h)
        self.innerDiameter = int(h * 0.8)

    def paintEvent(self, event):
        self.innerDiameter = int(self.height() * 0.8)
        self.innerMargin = int(self.height() * 0.1)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)

        # 开启抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)

        # 根据不同的选中状态切换内外颜色
        if self.checked:
            innerColor = self.innerColorChecked
            outerColor = self.outerColorChecked
            textColor = QColor(0, 0, 0, 180)
        else:
            innerColor = self.innerColor
            outerColor = self.outerColor
            textColor = QColor(0, 0, 0, 120)

        # 画外部圆角矩形
        painter.setBrush(outerColor)
        painter.drawRoundedRect(self.rect(), self.height() / 2, self.height() / 2)

        # 画内部圆形
        painter.setBrush(innerColor)
        painter.drawEllipse(QRectF(self.offset, self.innerMargin, self.innerDiameter, self.innerDiameter))
        # 画文字
        if self.fontText:
            painter.setPen(textColor)
            painter.setBrush(QColor(0, 0, 0, 255))
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(int(min(self.height() * 0.6, self.width() * 0.35)))
            painter.setFont(font)
            painter.drawText(QRectF(QPointF(int((self.width() - font.pixelSize() * len(self.fontText)) * 0.5),
                                            int((self.height() - font.pixelSize()) * 0.5)),
                                    QPointF(self.width() - self.innerMargin, self.height() - self.innerMargin)),
                             str(self.fontText))
        # painter.drawText()
        # painter.restore()

    def timerEvent(self, event):
        # 根据选中状态修改x坐标偏移值
        if self.checked:
            self.offset += 1
            if self.offset >= (self.width() - self.innerDiameter - self.innerMargin):
                self.killTimer(self.timeId)
        else:
            self.offset -= 1
            if self.offset <= self.innerMargin:
                self.killTimer(self.timeId)
        # 调用update，进行重绘
        self.update()

    def killTimer(self, timeId):
        # 删除定时器的同时，将timeId置为None
        super(SliderButton, self).killTimer(timeId)
        self.timeId = None

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            # print(event.pos().x())
            self.checked = not self.checked
            self.toggled.emit(self.checked)
            if self.timeId:
                self.killTimer(self.timeId)
            self.timeId = self.startTimer(5)

    def setChecked(self, checkState):  #
        # 如果状态没有变，不做处理
        if not checkState == self.checked:
            # 调用此方法改变状态不会触发动画，而是直接改变状态
            self.checked = checkState
            # self.toggled.emit(checkState)
            if checkState:
                # 选中状态，偏移值设为最大值
                self.offset = self.width() - self.innerDiameter - self.innerMargin
            else:
                # 非选中状态，偏移值设置最小值
                self.offset = self.innerMargin
            # 更新界面
            self.update()

    def isChecked(self):
        return self.checked


class TriSliderButton(QAbstractButton):

    toggled = pyqtSignal(int)
    def __init__(self, fontText: list = None, colourStatus_1=None, colourStatus_2=None, parent=None):
        super(TriSliderButton, self).__init__(parent)
        # 内部滑块尺寸
        self.innerWidth = 24
        self.innerHeight = 12

        # 是否选中标志位
        self.checked = False
        # 选中位置
        self.checkStatus = 0
        self.formerCheckStatus = 0
        # 鼠标形状
        self.setCursor(Qt.PointingHandCursor)
        # 设置遮罩，固定形状
        self.resize(26, 38)
        # self.setFixedSize(26,38)
        # 内边距
        self.innerMargin = (self.width() - self.innerWidth) / 2
        # x坐标偏移量
        self.offset = self.innerMargin
        # 外部背景色
        self.outerColor = QColor(170, 170, 170, 50)
        # 内部背景色未选中
        self.colourStatus_0 = QColor(255, 255, 255, 250)
        # 内部背景色选中
        if colourStatus_1:
            self.colourStatus_1 = QColor(*colourStatus_1)
        else:
            self.colourStatus_1 = QColor(51, 153, 255)

        if colourStatus_2:
            self.colourStatus_2 = QColor(*colourStatus_2)
        else:
            self.colourStatus_2 = QColor(51, 255, 153)

        self.fontText = fontText if fontText else []

        # 定时器ID
        self.timeId = None

    def setFontText(self, fontText: list):
        if not isinstance(fontText, list):
            raise ValueError('fontText should be a list of strings')
        if len(fontText) > 3:
            raise ValueError('expect no more than 3 string components')
        self.fontText = fontText

    def setStatusColours(self, colourStatus_0: tuple = None, colourStatus_1: tuple = None,
                         colourStatus_2: tuple = None):
        if colourStatus_0:
            self.colourStatus_0 = QColor(*colourStatus_0)
        if colourStatus_1:
            self.colourStatus_1 = QColor(*colourStatus_1)
        if colourStatus_2:
            self.colourStatus_2 = QColor(*colourStatus_2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        # 开启抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)

        outerColor = self.outerColor
        # 根据不同的选中状态切换内外颜色
        if self.checkStatus == 0:
            innerColor = self.colourStatus_0
        elif self.checkStatus == 1:
            innerColor = self.colourStatus_1
        else:
            innerColor = self.colourStatus_2

        # 画外部圆角矩形
        painter.setBrush(outerColor)
        painter.drawRoundedRect(self.rect(), self.width() / 3, self.width() / 3)

        # 画内部圆角矩形
        painter.setBrush(innerColor)
        painter.drawRoundedRect(QRectF(self.innerMargin, self.offset, self.width() - 2, self.height() / 3 - 2),
                                self.width() / 3, self.width() / 3)
        # 画文字
        bias = 0
        for text in self.fontText:
            painter.setPen(QColor(0, 0, 0, 130))
            painter.setBrush(QColor(0, 0, 0, 130))
            font = painter.font()
            font.setBold(True)
            font.setUnderline(True)
            font.setPixelSize(int(min(self.width() * 0.35, self.height() * 0.25)))
            painter.setFont(font)
            painter.drawText(QRectF(QPointF(self.innerMargin, self.innerMargin + bias),
                                    QPointF(self.width() - self.innerMargin,
                                            (self.height() - 2) / 3 + self.innerMargin + bias)),
                             Qt.AlignCenter, str(text))
            bias += (self.height() - 2) / 3

        # painter.drawText()
        # painter.restore()

    def timerEvent(self, event):
        # 根据选中状态修改x坐标偏移值
        # print('self.checkStatus',self.checkStatus, 'self.formerCheckStatus',self.formerCheckStatus)

        direction = 1 if self.checkStatus > self.formerCheckStatus else -1
        # start = (self.height()-2)/3 * self.formerCheckStatus +1
        destination = ((self.height() - 2) / 3) * self.checkStatus + 1  # 移动目标位置
        # print('direction',direction,'destination',destination)
        self.offset += direction
        if self.offset * direction > destination * direction:
            self.killTimer(self.timeId)

        # 调用update，进行重绘
        self.update()

    def killTimer(self, timeId):
        # 删除定时器的同时，将timeId置为None
        super(TriSliderButton, self).killTimer(timeId)
        self.timeId = None

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            Y = event.pos().y()
            self.formerCheckStatus = self.checkStatus
            if Y < (self.height() - 2) / 3 + 1:  # 点击0区域
                self.checkStatus = 0
            elif Y >= (self.height() - 2) / 3 + 1 and Y < (self.height() - 2) * 2 / 3 + 1:  # 点击1区域
                self.checkStatus = 1
            else:
                self.checkStatus = 2

            if self.checkStatus == self.formerCheckStatus:
                event.ignore()
                return

            self.checked = True
            if self.checkStatus == 0:
                self.checked = False

            self.toggled.emit(self.checkStatus)
            if self.timeId:
                self.killTimer(self.timeId)
            self.timeId = self.startTimer(5)


    def setCheckstatus(self, checkStatus) -> None:
        # 调用此方法改变状态不会触发动画，而是直接改变状态
        if not self.checkStatus == checkStatus:
            self.checkStatus = checkStatus
            self.formerCheckStatus = checkStatus
            if checkStatus == 0:
                self.checked = False
            else:
                self.checked = True
            self.offset = ((self.height() - 2) / 3) * self.checkStatus + 1
        self.update()

    def getCheckStatus(self):
        return self.checkStatus

    def isChecked(self):
        return self.checked


class CheckableComboBox(QtWidgets.QComboBox):
    checkStatusChanged = pyqtSignal(tuple)

    def __init__(self, item_list: list = None, parent=None, init_all_checked=True):
        super(CheckableComboBox, self).__init__(parent)
        self.setModel(QtGui.QStandardItemModel(self))
        self.view().pressed.connect(self.handleItemPressed)
        # self.view().pressed.connect(self.on_checkStatusChanged)
        self.init_all_checked = init_all_checked
        self.parent = parent
        if item_list:
            self.addItems(item_list)
        self.changed = False
        self.checkedItems = []
        self.checkedIndexes = []
        self.checkStatus = []

    def addItems(self, item_list: list):
        if not item_list:
            super(CheckableComboBox, self).addItems(item_list)
            return

        self.checkedItems = []
        self.checkedIndexes = []
        self.view().pressed.connect(self.get_all)
        self.view().pressed.connect(self.getCheckItem)
        self.addItem("全选")
        if self.init_all_checked:
            self.model().item(0).setCheckState(QtCore.Qt.Checked)
        else:
            self.model().item(0).setCheckState(QtCore.Qt.Unchecked)

        for i in range(len(item_list)):
            # line = QtWidgets.QFrame.HLine
            self.addItem(str(item_list[i]))
            if self.init_all_checked:
                self.model().item(i + 1).setCheckState(QtCore.Qt.Checked)
            else:
                self.model().item(i + 1).setCheckState(QtCore.Qt.Unchecked)
            # if i==4:self.model().item(i).setItemWidget(line)
        self.status = 1
        self.changed = False  # 是否进行了勾选操作

    def hidePopup(self):
        width = self.view().width()
        height = self.view().height() + self.height()
        X = QCursor().pos().x() - self.mapToGlobal(self.geometry().topLeft()).x() + self.geometry().x()
        Y = QCursor().pos().y() - self.mapToGlobal(self.geometry().topLeft()).y() + self.geometry().y()
        '''print('self.cursorX=',self.cursor().pos().x())
        print('GX=',self.mapToGlobal(self.geometry().topLeft()).x(),'GY=',self.mapToGlobal(self.geometry().topLeft()).y())
        print('QX=',QCursor().pos().x(),'QY=',QCursor().pos().y())
        print('Width=',width,'Height=',height,)
        print('X=',X,'Y=',Y)'''
        if 0 < X < width and self.height() < Y < height:
            # if self.view().hasMouse() :
            pass
        else:
            QtWidgets.QComboBox.hidePopup(self)
            # self.getCheckItem()
            # lineText = ','.join(self.checkedItems)
            # # self.setCurrentText(lineText)
            # # self.lineEdit().setText(lineText)
            # print('triggered hide popup')
            self.on_checkStatusChanged()
            self.changed = False

    def handleItemPressed(self, index):  # 这个函数是每次选择项目时判断状态时自动调用的，不用管（自动调用）
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)
        self.changed = True

    def on_checkStatusChanged(self):
        if self.changed == False:
            return
        checkedStatus = self.getCheckStatus()
        self.checkStatusChanged.emit(checkedStatus)

    def getCheckItem(self):
        # getCheckItem方法可以获得选择的项目列表，自动调用。
        self.checkedItems = []
        checkIndex = self.getCheckIndex()
        for index in checkIndex:
            item = self.model().item(index)
            self.checkedItems.append(item.text())
        # print("self.checkedItems为：",self.checkedItems)
        # self.lineEdit().setText(','.join(self.checkedItems))
        return self.checkedItems  # 实例化的时候直接调用这个self.checkedItems就能获取到选中的值，不需要调用这个方法，方法会在选择选项的时候自动被调用。

    def getCheckIndex(self):
        # getCheckItem方法可以获得选择的项目列表，自动调用。
        self.checkedIndexes.clear()
        for index in range(1, self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                self.checkedIndexes.append(index - 1)
        print("self.checkedIndexes为：", self.checkedIndexes)
        # self.lineEdit().setText(','.join(self.checkedItems))
        return self.checkedIndexes

    def getCheckStatus(self):
        # 返回所有项目的勾选状态
        self.checkStatus.clear()
        check_index = self.getCheckIndex()
        if len(check_index) == 0:  # 全不选，视为放弃使用此筛选，返回空tuple
            return ()
        check_status = [0] * self.count()
        for index in check_index:
            check_status[index] = 1
        self.checkStatus = check_status
        return tuple(check_status)

    def setCheckStatus(self, check_status):
        for index in range(1, self.count()):
            item = self.model().item(index)
            if index - 1 < len(check_status) and check_status[index - 1]:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def get_all(self):  # 实现全选功能的函数（自动调用）
        all_item = self.model().item(0)

        for index in range(1, self.count()):  # 判断是否是全选的状态，如果不是，全选按钮应该处于未选中的状态
            if self.status == 1:
                if self.model().item(index).checkState() == QtCore.Qt.Unchecked:
                    all_item.setCheckState(QtCore.Qt.Unchecked)
                    self.status = 0
                    break

        if all_item.checkState() == QtCore.Qt.Checked:
            if self.status == 0:
                for index in range(self.count()):
                    self.model().item(index).setCheckState(QtCore.Qt.Checked)
                    self.status = 1

        elif all_item.checkState() == QtCore.Qt.Unchecked:
            for index in range(self.count()):
                if self.status == 1:
                    self.model().item(index).setCheckState(QtCore.Qt.Unchecked)
            self.status = 0


class LineEditDelegate(QItemDelegate):
    def __init__(self, parent=None, editable_columns: list = None, place_holders: list = None):
        super(LineEditDelegate, self).__init__(parent)
        self.place_holders = place_holders
        self.editable_columns = editable_columns
        self.parent = parent

    def paint(self, painter, option, index):
        if not self.editable_columns or index.column() in self.editable_columns:  # 未指定可编辑列，默认都可以编辑
            value = index.model().data(index, Qt.DisplayRole)
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
            self.drawDisplay(painter, option, option.rect, str(value) if value is not None else None)
            self.drawFocus(painter, option, option.rect)
        else:
            super(LineEditDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        if not self.editable_columns or index.column() in self.editable_columns:
            lineEdit = QtWidgets.QLineEdit(parent)
            if self.place_holders and index.column() < len(self.place_holders):
                placeHolderText = self.place_holders[index.column()]
                lineEdit.setPlaceholderText(placeHolderText)
            lineEdit.editingFinished.connect(self.commitAndCloseEditor)
            lineEdit.editingFinished.connect(lambda: self.parent.setFocus())
            lineEdit.editingFinished.connect(lambda: self.parent.setEdited())
            lineEdit.editingFinished.connect(lambda: self.parent.adjustRowCount(index.row()))
            return lineEdit
        else:
            return super(LineEditDelegate, self).createEditor(parent, option, index)

    def commitAndCloseEditor(self):
        lineEdit = self.sender()
        self.commitData.emit(lineEdit)
        self.closeEditor.emit(lineEdit)

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setText(value if value is not None else None)


class VectorEditTable(QtWidgets.QTableView):
    EditingFinished = pyqtSignal(list)

    def __init__(self, parent=None, h_header: list = None, data: list = None, place_holders: list = None,
                 attachedWidget: QtWidgets.QWidget = None, editable_columns: list = None, column_widths: list = None,
                 old_data_editable=True, min_row_count=4):
        super(VectorEditTable, self).__init__(parent)
        self.data = data
        self.h_header = h_header
        self.parent = parent
        self.attachedWidget = attachedWidget  # 位置上跟随的空间
        self.edited = False  # 状态机，记录是在发生过编辑
        # self.setWindowFlags(Qt.Popup|Qt.FramelessWindowHint)
        self.verticalHeader().setDefaultSectionSize(20)
        self.horizontalHeader().setDefaultSectionSize(80)
        self.horizontalHeader().setMaximumHeight(25)
        self.verticalHeader().hide()
        self.setData(self.h_header, self.data, place_holders, editable_columns, column_widths, old_data_editable,
                     min_row_count)
        self.parent.installEventFilter(self)

    def setEdited(self):
        self.edited = True

    def setData(self, h_header: list = None, data: list = None, place_holders: list = None,
                editable_columns: list = None,
                column_widths: list = None, old_data_editable=True, min_row_count=4):
        rowCount = len(data)

        columnCount = len(data[0]) if rowCount > 0 else 0
        self.model = QStandardItemModel(rowCount, columnCount)
        if h_header:
            self.model.setHorizontalHeaderLabels(h_header)
        row_n = rowCount + 1 if rowCount >= min_row_count else min_row_count
        column_n = max(columnCount, len(h_header))
        for i in range(row_n):  # 设置为最少4行
            for j in range(column_n):
                try:
                    val = data[i][j]
                except:
                    val = None
                if i < len(data) and j < len(data[i]) and val:
                    item = QStandardItem(str(val))
                else:
                    item = QStandardItem()
                editable = True
                if editable_columns and j not in editable_columns:  # 设置可编辑的列
                    editable = False
                if i < rowCount and not old_data_editable:  # 设置旧有的数据行不可编辑
                    editable = False
                item.setEditable(editable)
                self.model.setItem(i, j, item)
        self.setModel(self.model)
        lineEditDelegate = LineEditDelegate(self, place_holders=place_holders)
        self.setItemDelegate(lineEditDelegate)
        self.set_geometry(row_n, column_n, column_widths)

    def adjustRowCount(self, edited_row: int):
        if self.model.rowCount() == edited_row + 1:
            for j in range(len(self.h_header)):
                if self.model.item(edited_row, j).data(role=2):
                    for k in range(self.model.columnCount()):
                        item = QStandardItem()
                        self.model.setItem(edited_row + 1, k, item)
                    return

    def set_geometry(self, y_r, x_c, column_widths):
        total_width = 0
        l = len(column_widths) if column_widths else 0
        for i in range(x_c):
            if i < l:
                self.setColumnWidth(i, column_widths[i])
                total_width += column_widths[i] + 5
            else:
                total_width += 80
        total_width += 10
        total_height = y_r * 20 + 50
        X_child = self.attachedWidget.geometry().x() + self.attachedWidget.geometry().width() / 2 - total_width / 2
        Y_child = self.attachedWidget.geometry().y() - total_height
        parentAttr = self.attachedWidget.parent
        if isinstance(parentAttr, QtWidgets.QWidget):
            parent = parentAttr
        elif callable(parentAttr):
            parent = parentAttr()
        else:
            raise AttributeError('object has no parent')
        if hasattr(parent, 'horizontalHeader'):
            Y_child += parent.horizontalHeader().height()

        global_coord_zero = parent.mapToGlobal(QPoint(int(X_child), int(Y_child)))
        application_coord_zero = self.parent.mapFromGlobal(global_coord_zero)
        X = application_coord_zero.x()
        Y = application_coord_zero.y()
        if X + total_width > self.parent.width():  # 适应屏幕宽度
            X = self.parent.width() - total_width
        elif X < 0:
            X = 0
        else:
            pass
        if Y <= 0:
            if total_height > self.parent.height():
                Y = 0
            else:
                Y = self.attachedWidget.geometry().y() + self.attachedWidget.geometry().height()
        # self.attachedView = attachedView
        self.setGeometry(X, Y, total_width, total_height)
        self.setFocus()

    def getData(self):
        rowCount = self.model.rowCount() - 1
        columnCount = self.model.columnCount()
        data = []
        for i in range(rowCount):
            tempList = []
            is_empty_row = True  # 跳过空行
            for j in range(columnCount):
                val = self.model.item(i, j).data(role=2)
                if val:
                    is_empty_row = False
                # if val and val.isdigit() and len(val) <=7:
                #     val = float(val)
                tempList.append(val)
            if is_empty_row:  # 跳过空行
                continue
            data.append(tempList)
        return data

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
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
            # if self.view().hasMouse() :
            QtWidgets.QTableView.focusOutEvent(self, e)
        else:
            if self.edited:
                data = self.getData()
                self.EditingFinished.emit(data)
            self.playCloseAnimation()

            QtWidgets.QTableView.focusOutEvent(self, e)

    def playCloseAnimation(self):
        # self.setMinimumSize(0,0)
        self.closeAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        self.closeAnimation.setStartValue(self.geometry())
        self.closeAnimation.setEndValue(
            QtCore.QRect(self.geometry().x(), int(self.geometry().y() + self.height() / 2), self.width(), 0))
        self.closeAnimation.setDuration(150)
        self.closeAnimation.finished.connect(self.deleteSelf)
        self.closeAnimation.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        # super(VictorEditTable, self).closeEvent(a0)

    def deleteSelf(self):
        self.parent.removeEventFilter(self)
        self.close()
        self.deleteLater()

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            self.clearFocus()
        return super().eventFilter(object, event)

    '''
    def event(self, e:QEvent)->bool:
        #窗口生命周期事件 按顺序
        #窗口启动相关事件
        if e.type() in [QEvent.ChildPolished,QEvent.ChildAdded,QEvent.InputMethodQuery,QEvent.Polish,
                          QEvent.DynamicPropertyChange,QEvent.PaletteChange,QEvent.FontChange,QEvent.Move,QEvent.Resize,
                          QEvent.Show,QEvent.FocusIn,QEvent.ShowToParent,QEvent.PolishRequest,QEvent.MetaCall,QEvent.Timer,
                          QEvent.LayoutRequest,QEvent.UpdateLater,QEvent.Paint]:
            pass
        #窗口鼠标相关事件
        elif e.type() in [QEvent.Enter,QEvent.HoverEnter,QEvent.HoverMove,QEvent.Leave,QEvent.HoverLeave,
                          QEvent.FocusAboutToChange,QEvent.ToolTip,QEvent.Wheel]:
            n=2
        #窗口关闭相关事件
        elif e.type() in [QEvent.FocusOut,QEvent.Close,QEvent.Hide,
                          QEvent.HideToParent,QEvent.DeferredDelete]:
            pass
        #窗口子组件相关事件
        elif e.type() in [QEvent.ChildPolished,QEvent.WindowDeactivate]:
            pass
        else:
            t = e.type()
            print('窗口特殊事件:',t)
            n=1
        return  QtWidgets.QTableView.event(self,e)
    '''


class JsonLogEditTable(VectorEditTable):
    EditingFinished = pyqtSignal(str)

    def __init__(self, parent=None, data: str = None,
                 attachedWidget: QtWidgets.QWidget = None, column_widths: list = None, old_data_editable=True):
        if not data:
            data_list = []
        else:
            try:
                log_list = json.loads(data)
                data_list = [[log['date'], log['log_desc']] for log in log_list]
            except ValueError as e:
                data_list = [['2022之前', data]]

        super(JsonLogEditTable, self).__init__(parent=parent, h_header=['时间', '记录'], data=data_list,
                                               attachedWidget=attachedWidget
                                               , editable_columns=[1], column_widths=column_widths,
                                               old_data_editable=old_data_editable, min_row_count=1)

    def getData(self):
        data = super(JsonLogEditTable, self).getData()
        data_list = []
        for log in data:
            log_dict = {}
            if log[0] == '' or not log[0]:
                log_dict['date'] = datetime.datetime.today().strftime("%Y-%m-%d")
            else:
                log_dict['date'] = log[0]
            log_dict['log_desc'] = log[1]
            data_list.append(log_dict)
        data_json = json.dumps(data_list, ensure_ascii=False)
        return data_json


class TableMixedWidgetPop(QtWidgets.QTableWidget):
    '''支持类型，b:booleen,sliderButton; t:text,textedit;e:enum,combobox,f:filearray,fileBrowser+button'''
    EditingFinished = pyqtSignal(dict)
    widget_choice = {'b': SliderButton,
                     'e': QtWidgets.QComboBox,
                     't': QtWidgets.QPlainTextEdit}
    widget_init = {'b': SliderButton.setFontText,
                   'e': QtWidgets.QComboBox.addItems,
                   't': QtWidgets.QPlainTextEdit.setPlainText}
    widget_set = {'b': SliderButton.setChecked,
                  'e': QtWidgets.QComboBox.setCurrentIndex,
                  't': QtWidgets.QPlainTextEdit.setPlainText}
    widget_get = {'b': SliderButton.isChecked,
                  'e': QtWidgets.QComboBox.currentIndex,
                  't': QtWidgets.QPlainTextEdit.toPlainText}
    widdet_signal = {'b': 'toggled',
                     'e': 'currentIndexChanged',
                     't': 'textChanged'}
    widget_size = {'b': (50, 25),
                   'e': (100, 20),
                   't': (150, 50)}

    def __init__(self, template_file: str, fields_values: dict, column_widths: list = None,
                 attachedWidget: QtWidgets.QWidget = None, parent=None):
        super(TableMixedWidgetPop, self).__init__(parent)
        self.parent = parent
        self.fields_values = fields_values
        self.attachedWidget = attachedWidget
        self.column_widths = column_widths

        self.edited = False
        self.setMouseTracking(True)
        self.f_table_template = []
        with open(template_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.f_table_template.append(row)

        # self.fields = []

        # self.verticalHeader().setDefaultSectionSize(30)
        # self.horizontalHeader().hide()

        self.parent.installEventFilter(self)
        self.show()

    def initWidgets(self):
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 禁止编辑
        header = ['项目', '情况', '文件']
        self.setHorizontalHeaderLabels(header)
        self.horizontalHeader().setMaximumHeight(25)
        nRow = len(self.f_table_template)
        self.setRowCount(nRow)
        self.setColumnCount(len(header))
        for i, width in enumerate(self.column_widths):
            self.setColumnWidth(i, width)

        self.set_geometry(nRow, 2, self.column_widths)
        for i, row in enumerate(self.f_table_template):
            Qitem = QtWidgets.QTableWidgetItem(row[2])
            Qitem.setTextAlignment(Qt.AlignRight)
            self.setItem(i, 0, Qitem)  # 项目标题
            self.setCellWidget(i, 1, self.widget_choice[row[1]]())  # 项目控件
            self.cellWidget(i, 1).wheelEvent = types.MethodType(lambda obj, e: e.ignore(),
                                                                self.cellWidget(i, 1))  # 禁用wheel
            size = QtCore.QSize(*self.widget_size[row[1]])
            self.cellWidget(i, 1).setFixedSize(size)
            self.setRowHeight(i, self.widget_size[row[1]][1] + 5)  # 行高
            if self.widget_size[row[1]][0] > self.columnWidth(1) - 5:
                self.setColumnWidth(1, self.widget_size[row[1]][0] + 5)
            try:
                face = json.loads(row[3])
            except:
                face = DataCenter.convertInt(row[3])
            self.widget_init[row[1]](self.cellWidget(i, 1), face)  # 控件基本设置
            self.widget_set[row[1]](self.cellWidget(i, 1), self.fields_values[row[0]])  # 项目赋值
            self.cellWidget(i, 1).__getattribute__(self.widdet_signal[row[1]]).connect(self.setEdited)  # 绑定信号

    def setTableData(self, fields_values: dict):
        self.fields_values = fields_values
        for i, row in enumerate(self.f_table_template):
            self.widget_set[row[1]](self.cellWidget(i, 1), fields_values[row[0]])  # 项目赋值

    def setEdited(self):
        self.edited = True

    def getTableData(self):
        for i, row in enumerate(self.f_table_template):
            value = self.widget_get[row[1]](self.cellWidget(i, 1))
            self.fields_values[row[0]] = value  # 控件取值
        return self.fields_values

    # def event(self, e:QEvent)->bool:
    #     #窗口生命周期事件 按顺序
    #     #窗口启动相关事件
    #     if e.type() in [QEvent.ChildPolished,QEvent.ChildAdded,QEvent.InputMethodQuery,QEvent.Polish,
    #                       QEvent.DynamicPropertyChange,QEvent.PaletteChange,QEvent.FontChange,QEvent.Move,QEvent.Resize,
    #                       QEvent.Show,QEvent.FocusIn,QEvent.ShowToParent,QEvent.PolishRequest,QEvent.MetaCall,QEvent.Timer,
    #                       QEvent.LayoutRequest,QEvent.UpdateLater,QEvent.Paint]:
    #         pass
    #     #窗口鼠标相关事件
    #     elif e.type() in [QEvent.Enter,QEvent.HoverEnter,QEvent.HoverMove,QEvent.Leave,QEvent.HoverLeave,
    #                       QEvent.FocusAboutToChange,QEvent.ToolTip,QEvent.Wheel]:
    #         n=2
    #     #窗口关闭相关事件
    #     elif e.type() in [QEvent.FocusOut,QEvent.Close,QEvent.Hide,
    #                       QEvent.HideToParent,QEvent.DeferredDelete]:
    #         pass
    #     #窗口子组件相关事件
    #     elif e.type() in [QEvent.ChildPolished,QEvent.WindowDeactivate]:
    #         pass
    #     else:
    #         t = e.type()
    #         print('窗口特殊事件:',t)
    #         n=1
    #     return  QtWidgets.QTableView.event(self,e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if self.hasFocus():
            n = 0
            pass
        else:
            self.setFocus()

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
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
            # if self.view().hasMouse() :
            QtWidgets.QTableView.focusOutEvent(self, e)
        else:
            if self.edited:
                data = self.getTableData()
                self.EditingFinished.emit(data)
            self.playCloseAnimation()
            QtWidgets.QTableWidget.focusOutEvent(self, e)

    def playCloseAnimation(self):
        # self.setMinimumSize(0,0)
        self.closeAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        self.closeAnimation.setStartValue(self.geometry())
        self.closeAnimation.setEndValue(
            QtCore.QRect(self.geometry().x(), self.geometry().y() + self.height() / 2, self.width(), 0))
        self.closeAnimation.setDuration(150)
        self.closeAnimation.finished.connect(self.deleteSelf)
        self.closeAnimation.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        # super(VictorEditTable, self).closeEvent(a0)

    def set_geometry(self, y_r, x_c, column_widths):
        total_width = 0
        l = len(column_widths) if column_widths else 0
        # 设置总宽度
        for i in range(x_c):
            if i < l:
                if column_widths[i] > self.columnWidth(i):
                    self.setColumnWidth(i, column_widths[i])
                total_width += self.columnWidth(i) + 5
            else:  # 默认列宽80
                total_width += 80
        total_width += 10
        total_height = y_r * 30 + 50
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
        self.close()
        self.deleteLater()

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            self.clearFocus()
        return super().eventFilter(object, event)


class CheckPointTableWidgetPop(QtWidgets.QTableWidget):
    '''支持类型，b:booleen,sliderButton; t:text,plaintextedit; e:enum,combobox; f:filearray,fileBrowser+button
        此控件类的model应该解决数据保存的问题，目前checkpoint-checkitem-filearray-file 各级中，filearray-file的保存由自身触发。
        check
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
            'size': (100, 50),
        },
        'file': {
            'choice': FileListBrowser,
            'init_method': FileListBrowser.setDisplay,
            'set_method': FileListBrowser.setDisplay,
            'get_method': FileListBrowser.get_file_array,
            'signal_name': 'Edited',
            'size': (120, 50),
        }

    }

    def __init__(self,
                 check_point: CheckPoint,
                 column_widths: list = None,
                 attachedWidget: QtWidgets.QWidget = None,
                 parent=None):
        super(CheckPointTableWidgetPop, self).__init__(parent)
        self.parent = parent
        self.model = check_point
        self.attachedWidget = attachedWidget
        self.column_widths = column_widths
        self.edited = False
        self.setMouseTracking(True)
        self.verticalHeader().setDefaultSectionSize(70)
        # self.horizontalHeader().hide()
        self.initWidgets()
        self.parent.installEventFilter(self)
        self.show()

    @classmethod
    def chooseWidget(cls, type_code: str):
        return cls.widget_chooser[type_code]['choice']

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
    def chooseSignalName(cls, type_code: str):
        return cls.widget_chooser[type_code]['signal_name']

    def initWidgets(self):
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 禁止编辑
        header_labels = ['项目', '进度', '说明', '文件', '.']
        self.setHorizontalHeaderLabels(header_labels)
        # header = self.horizontalHeader()
        # header_items = self.horizontalHeaderItem(1)
        # print('header_items.text = ',header_items.text())
        # self.horizontalHeader().setMaximumHeight(25)
        nRow = len(self.model.children_items)
        self.setRowCount(nRow)
        self.setColumnCount(len(header_labels))
        for i, width in enumerate(self.column_widths):
            self.setColumnWidth(i, width)

        self.set_geometry(nRow, 5, self.column_widths)
        for i, check_item in enumerate(self.model.children_items):
            Qitem = QtWidgets.QTableWidgetItem(check_item.label)
            Qitem.setTextAlignment(Qt.AlignRight)
            self.setItem(i, 0, Qitem)  # 项目标题
            for j, field in enumerate(['desc', 'complete_level', 'file_array']):
                self.setCellWidget(i, j + 1, self.chooseWidget(check_item.field_type[field])())  # 项目enum控件
                self.cellWidget(i, j + 1).wheelEvent = types.MethodType(lambda obj, e: e.ignore(),
                                                                        self.cellWidget(i, j + 1))  # 禁用wheel
                size = QtCore.QSize(*self.chooseSize(check_item.field_type[field]))
                self.cellWidget(i, j + 1).setFixedSize(size)

                if field == 'complete_level':
                    face = [x[1] for x in check_item.Completion_Level_Flag.items()]
                    value = check_item.complete_level
                else:
                    face = value = check_item.__getattribute__(field)  # 控件初始化所需的数据
                self.chooseInitMethod(check_item.field_type[field])(self.cellWidget(i, j + 1), face)  # 控件基本设置
                self.chooseSetMethod(check_item.field_type[field])(self.cellWidget(i, j + 1), value)  # 项目赋值
                self.cellWidget(i, j + 1).__getattribute__(self.chooseSignalName(
                    check_item.field_type[field])).connect(self.setEdited)  # 绑定信号
            button = QtWidgets.QPushButton('上传')
            button.row_index = i
            button.clicked.connect(self.on_upload_button_clicked)
            self.setCellWidget(i, 4, button)

    def setTableData(self, check_point: CheckPoint):
        self.model = check_point
        for i, check_item in enumerate(self.model.children_items):
            for j, field in enumerate(['desc', 'complete_level', 'file_array']):
                self.chooseSetMethod(check_item.field_type[field])(self.cellWidget(i, j + 1),
                                                                   check_item.__getattribute__(field))  # 项目赋值

    def setEdited(self):
        self.edited = True

    def getTableData(self):
        for i, check_item in enumerate(self.model.children_items):
            for j, field in enumerate(['desc', 'complete_level', 'file_array']):
                check_item.__setattr__(field, self.chooseGetMethod(check_item.field_type[field])(
                    self.cellWidget(i, j + 1)))  # 项目赋值
        return self.model

    # def event(self, e:QEvent)->bool:
    #     #窗口生命周期事件 按顺序
    #     #窗口启动相关事件
    #     if e.type() in [QEvent.ChildPolished,QEvent.ChildAdded,QEvent.InputMethodQuery,QEvent.Polish,
    #                       QEvent.DynamicPropertyChange,QEvent.PaletteChange,QEvent.FontChange,QEvent.Move,QEvent.Resize,
    #                       QEvent.Show,QEvent.FocusIn,QEvent.ShowToParent,QEvent.PolishRequest,QEvent.MetaCall,QEvent.Timer,
    #                       QEvent.LayoutRequest,QEvent.UpdateLater,QEvent.Paint]:
    #         pass
    #     #窗口鼠标相关事件
    #     elif e.type() in [QEvent.Enter,QEvent.HoverEnter,QEvent.HoverMove,QEvent.Leave,QEvent.HoverLeave,
    #                       QEvent.FocusAboutToChange,QEvent.ToolTip,QEvent.Wheel]:
    #         n=2
    #     #窗口关闭相关事件
    #     elif e.type() in [QEvent.FocusOut,QEvent.Close,QEvent.Hide,
    #                       QEvent.HideToParent,QEvent.DeferredDelete]:
    #         pass
    #     #窗口子组件相关事件
    #     elif e.type() in [QEvent.ChildPolished,QEvent.WindowDeactivate]:
    #         pass
    #     else:
    #         t = e.type()
    #         print('窗口特殊事件:',t)
    #         n=1
    #     return  QtWidgets.QTableView.event(self,e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if self.hasFocus():
            pass
        else:
            self.setFocus()

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
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
            # if self.view().hasMouse() :
            QtWidgets.QTableView.focusOutEvent(self, e)
        else:
            if self.edited:
                data = self.getTableData()
                self.EditingFinished.emit(data)
            self.playCloseAnimation()
            QtWidgets.QTableWidget.focusOutEvent(self, e)

    def on_upload_button_clicked(self):
        sender = self.sender()
        index = sender.row_index
        print(index)

    def playCloseAnimation(self):
        # self.setMinimumSize(0,0)
        self.closeAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        self.closeAnimation.setStartValue(self.geometry())
        self.closeAnimation.setEndValue(
            QtCore.QRect(self.geometry().x(), self.geometry().y() + self.height() / 2, self.width(), 0))
        self.closeAnimation.setDuration(150)
        self.closeAnimation.finished.connect(self.deleteSelf)
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
        total_height = y_r * 50 + 50
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
        self.close()
        self.deleteLater()

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.MouseButtonPress:
            self.clearFocus()
        return super().eventFilter(object, event)

class CheckItemHorizontalPanel(QtWidgets.QScrollArea):
    def __init__(self, check_items: list[CheckItem], fields_values: dict, column_widths: list = None,
                 attachedWidget: QtWidgets.QWidget = None, parent=None):
        self.check_items = check_items
        self.parent = parent
        self.edited = False
        self.setMouseTracking(True)
        self.fields = []
        self.fields_values = fields_values
        self.attachedWidget = attachedWidget
        # self.verticalHeader().setDefaultSectionSize(30)
        # self.horizontalHeader().hide()
        header = ['项目', '情况']
        nRow = len(self.check_items)
        for i, width in enumerate(column_widths):
            self.setColumnWidth(i, width)
        # self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 禁止编辑
        for i, row in enumerate(self.f_table_template):
            Qitem = QtWidgets.QTableWidgetItem(row[2])
            Qitem.setTextAlignment(Qt.AlignRight)
            self.setItem(i, 0, Qitem)  # 项目标题
            self.setCellWidget(i, 1, self.widget_choice[row[1]]())  # 项目控件
            self.cellWidget(i, 1).wheelEvent = types.MethodType(lambda obj, e: e.ignore(),
                                                                self.cellWidget(i, 1))  # 禁用wheel
            size = QtCore.QSize(*self.widget_size[row[1]])
            self.cellWidget(i, 1).setFixedSize(size)
            self.setRowHeight(i, self.widget_size[row[1]][1] + 5)  # 行高
            if self.widget_size[row[1]][0] > self.columnWidth(1) - 5:
                self.setColumnWidth(1, self.widget_size[row[1]][0] + 5)
            try:
                face = json.loads(row[3])
            except:
                face = DataCenter.convertInt(row[3])
            self.widget_init[row[1]](self.cellWidget(i, 1), face)  # 控件基本设置
            self.widget_set[row[1]](self.cellWidget(i, 1), fields_values[row[0]])  # 项目赋值
            self.cellWidget(i, 1).__getattribute__(self.widdet_signal[row[1]]).connect(self.setEdited)  # 绑定信号
        self.set_geometry(nRow, 2, column_widths)
        self.parent.installEventFilter(self)
        self.show()

class CheckLableBox(QtWidgets.QFrame):
    statusClicked = pyqtSignal(tuple)

    @staticmethod
    def styleColour(colour: tuple, alpha=255):
        r, g, b = colour
        rgba = (r, g, b, alpha)
        return "background:rgba%s" % str(rgba)

    def __init__(self, lables: list, parent=None):
        '''lables[(name,text,GColor)]'''
        super(CheckLableBox, self).__init__(parent)
        # 生成按钮
        # self.resize(70,100
        self.setStyleSheet('margin: 0px 0px 0px 0px;padding:0px;border-width:0')
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Sunken)
        self.setMidLineWidth(0)
        # self.setMaximumHeight(27*DF_Ratio)
        self.setLineWidth(0)
        # self.setContentsMargins(1,1,1,1)
        self.HLayout = QtWidgets.QHBoxLayout(self)
        self.HLayout.setContentsMargins(0, 0, 0, 0)
        self.HLayout.setSpacing(1)
        self.labels = lables
        for i, label in enumerate(self.labels):
            ck = QCheckBox(self)
            ck.setText(label[1])
            ck.setMinimumHeight(25 * DataView.DF_Ratio)
            ck.clicked.connect(self.on_statusClicked)
            ck.setStyleSheet(self.styleColour(label[2], label[3]))
            self.HLayout.addWidget(ck)

    def on_statusClicked(self):
        self.setFocus()
        self.statusClicked.emit(self.getCheckedNames())

    def focusInEvent(self, a0: QtGui.QFocusEvent) -> None:
        self.setFocus()

    def setCheckedStatuses(self, init_check_status: list):
        if len(init_check_status) != len(self.chk_names):
            try:
                raise ValueError("numbers of check_states and chk_names don't match. "
                                 "check_names are {}".format(self.chk_names))
            except ValueError as e:
                print(e)
        for i, name in enumerate(self.chk_names):
            bo = self.findChildren(QCheckBox)[i]
            bo.setChecked(init_check_status[i])
            bo.clicked.connect(self.statusClickEvent)

    def clearCheckStatuses(self):
        for item in self.findChildren(QCheckBox):
            item.setChecked(False)

    def getCheckedNames(self):
        check_names = []
        for i in range(len(self.labels)):
            if self.findChildren(QCheckBox)[i].isChecked():
                check_names.append(self.labels[i][0])
        return tuple(check_names)

class ToDoUnitWidget(QtWidgets.QFrame, ToDoUnitUi.Ui_Form_1):
    def conclusionDoubleClickEvent(self, obj):
        data_json = self.model.conclusion_desc
        log_eidt_table = JsonLogEditTable(self.parent, data=data_json, attachedWidget=obj)
        log_eidt_table.EditingFinished.connect()

    def __init__(self, parent=None, model=None, drag_drop_enabled = True):
        super(ToDoUnitWidget, self).__init__(parent)
        self.setUpdatesEnabled(False)
        # self.setE()
        self.setupUi(self)
        self.setObjectName('todo_unit')
        # self.setStyleSheet('QFrame{background-color: rgba(245,248,160,105);'
        #                    'border-width: 1px;border-style: solid;'
        #                    'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '
        #                    'stop:0 rgba(200, 220, 255, 255), stop:1 rgba(171, 221, 252, 255));}'
        #                    'QLabel{border-width: 0px;background:transparent}'
        #                    'QCommandLinkButton:{background-color: rgba(220,220,220,0);}'
        #                    'QLineEdit:{background:transparent}')
        self.parent = parent
        self.model = model
        self.drag_drop_enabled = drag_drop_enabled
        self.isCritial_slideButton = SliderButton(parent=self, fontText='紧急')
        # scaling_ratio  = min(1, DataView.DF_Ratio)
        scaling_ratio = DataView.FIX_SIZE_WIDGET_SCALING
        size = QtCore.QSize(40 *scaling_ratio, 22 * scaling_ratio)
        self.isCritial_slideButton.setFixedSize(size)
        self.isCritial_slideButton.setColourChecked(GColour.getAlphaColor(GColour.TaskColour.TaskIsCritial, 180))
        self.verticalLayout_h_sliders.addWidget(self.isCritial_slideButton)

        self.todoStatus_triSlideButton = TriSliderButton(parent=self, fontText=['未办', '进行', '完成'],
                                                         colourStatus_1=(140, 150, 220, 150),
                                                         colourStatus_2=(140, 220, 150, 150))
        self.todoTimeSpaceDistance_triSliderButton = TriSliderButton(parent=self, fontText= ['近时','中期', '远期'],
                                                            colourStatus_1=(180, 180, 180, 150),
                                                            colourStatus_2=(150, 150, 150, 150)
                                                            )
        self.horizontalLayout_v_sliders.addWidget(self.todoTimeSpaceDistance_triSliderButton,0)
        self.horizontalLayout_v_sliders.addWidget(self.todoStatus_triSlideButton, 1)
        self.todoTimeSpaceDistance_triSliderButton.setFixedSize(30 * scaling_ratio, 46 * scaling_ratio)
        self.todoStatus_triSlideButton.setFixedSize(30 * scaling_ratio, 46 * scaling_ratio)
        self.lineEdit.setFixedSize(36 * scaling_ratio, 20 * scaling_ratio)
        font = QtGui.QFont()
        font.setPointSize(8 * scaling_ratio)
        self.label.setFont(font)
        self.label_2.setFont(font)
        self.textEdit.mouseDoubleClickEvent = types.MethodType(new_doubleClickEvent, self.textEdit)
        self.groupBox.setStyleSheet(
            'QGroupBox{border-radius:5;border-style:solid;border-width:1;border-color:rgb(230,230,230)}')
        # 绑定重写的方法和属性
        self.textEdit.edited = False
        self.textEdit.init_text = ''
        self.textEdit.keyPressEvent = types.MethodType(MyQTextEdit.keyPressEvent, self.textEdit)
        self.textEdit.setText = types.MethodType(MyQTextEdit.setText, self.textEdit)
        self.textEdit.setEdited = types.MethodType(MyQTextEdit.setEdited, self.textEdit)
        self.textEdit.textChanged.connect(self.textEdit.setEdited)
        self.textEdit_2.edited = False
        self.textEdit_2.init_text = ''
        self.textEdit_2.keyPressEvent = types.MethodType(MyQTextEdit.keyPressEvent, self.textEdit_2)
        self.textEdit_2.setText = types.MethodType(MyQTextEdit.setText, self.textEdit_2)
        self.textEdit_2.setEdited = types.MethodType(MyQTextEdit.setEdited, self.textEdit_2)
        self.textEdit_2.textChanged.connect(self.textEdit_2.setEdited)
        self.textEdit_2.setPlaceholderText('    --完成结果--')
        self.textEdit.setReadOnly(True)
        # self.textEdit.setStyleSheet('QTextEdit{font-family:Microsoft YaHei; font-weight:400; font-size: 15px}')
        self.textEdit_2.setReadOnly(True)
        self.setAcceptDrops(True)
        self.iniDragCor = [0, 0]
        # self.setUpdatesEnabled(True)
        # self.Todo_Font_Style = 'font-family:Microsoft YaHei; font-weight:400; font-size: 16px'

    def renderSelf(self):
        '''根据model给各个控件进行赋值'''
        DataView.ResAdaptor.init_ui_size(self)
        # self.todoWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.todoWidget.customContextMenuRequested.connect(self.showTodoMenu)
        self.setStyleSheet(
            'QFrame{background-color: rgba(249,252,235,255);margin:1px; border-width: 3px;border-radius:7px; border-style: dashed;'
            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}'
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
            '#pushButton_company,#pushButton_project{border-style: solid;border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
            'border-width: 0px;border-radius: 0px;color: #202020;text-align: left;font-family: Microsoft YaHei;font:bold;font-size:7pt;'
            'padding: 0px;background-color: rgba(220,220,220,0);}'
            '#pushButton_company:hover,#pushButton_project:hover{border-style: solid;border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
            'border-width: 1px;border-radius: 5px;color: #202020;text-align: left;font-family: Microsoft YaHei;font:bold;font-size:7pt;'
            'padding: 0px;background-color: rgb(200,225,255);}')
        # buttons signal
        if self.model.conn_company_name:
            self.pushButton_company.setText(self.model.conn_company_name)
        else:
            self.pushButton_company.setText('')
            self.pushButton_company.setEnabled(False)
        if self.model.conn_project_name:
            self.pushButton_project.setText(self.model.conn_project_name)
        else:
            self.pushButton_project.setText('')
            self.pushButton_project.setEnabled(False)
        # self.pushButton_company.clicked.connect(self.on_company_clicked)
        # self.pushButton_project.clicked.connect(self.on_project_clicked)
        # self.isCritial_slideButton.toggled.connect(self.on_isCritial_slideButton_clicked)
        # self.todoStatus_triSlideButton.toggled.connect(self.on_todoStatus_triSlideButton_toggled)
        self.pushButton_4.setStyleSheet('QPushButton:checked{background:lightblue}')
        # self.pushButton_4.clicked.connect(self.on_pending_activated)
        # self.pushButton_5.setEnabled(False)
        # self.pushButton_5.clicked.connect(self.on_pending_deactivated)
        # self.pushButton_6.clicked.connect(self.on_delete_clicked)

        # textEdits signal
        # self.textEdit.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit)
        # self.textEdit_2.focusOutEvent = types.MethodType(self.textEdit_focusOutEvent, self.todoWidget.textEdit_2)
        self.textEdit.setText(self.model.todo_desc)
        self.textEdit_2.setText(self.model.conclusion_desc)

        # self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.textEdit.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.textEdit))
        # self.textEdit_2.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.textEdit_2.customContextMenuRequested.connect(lambda :self.showRightMenu(text_pad=self.todoWidget.textEdit_2))
        # self.lineEdit.editingFinished.connect(self.on_slider_close)
        self.lineEdit.setEnabled(False)

        # 根据字段参数初始化各个参数控件
        # today = datetime.datetime.today().date()
        if self.model.on_pending:
            self.pushButton_4.setChecked(True)
        if self.model.pending_till_date:
            pending_days = (datetime.datetime.strptime(str(self.model.pending_till_date), '%Y-%m-%d').date()\
                            - datetime.datetime.today().date()).days
            # datetime两个日期相减得到的数字是实际数字相减的结果
            if pending_days > 0:
                self.lineEdit.setText(str(pending_days))
                self.label.setText(self.model.pending_till_date)
                self.lineEdit.setEnabled(True)
                self.pushButton_5.setEnabled(True)
            else:
                self.lineEdit.setText('')
                self.label.setText('')
        else:
            self.lineEdit.setText('')
            self.label.setText('')
        self.isCritial_slideButton.setChecked(self.model.is_critical)
        self.todoStatus_triSlideButton.setCheckstatus(self.model.status)
        self.style = ''
        if self.model.conn_project_id:
            if self.model.conn_project_order_tobe:
                self.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                            '%s}' % (
                                                str(GColour.ProjectRGBColour.ProjectOrderTobe), self.Todo_Font_Style))
                self.style = self.textEdit.styleSheet()
            elif self.model.conn_project_clear_chance:
                self.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                            '%s}' % (
                                                str(GColour.ProjectRGBColour.ProjectClearChance), self.Todo_Font_Style))
                self.style = self.textEdit.styleSheet()
            elif self.model.conn_project_highlight:
                self.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                            '%s}' % (
                                                str(GColour.ProjectRGBColour.ProjectHighlight), self.Todo_Font_Style))
                self.style = self.textEdit.styleSheet()
            elif self.model.conn_project_in_act:
                self.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                            '%s}' % (
                                                str(GColour.ProjectRGBColour.ProjectInAct), self.Todo_Font_Style))
                self.style = self.textEdit.styleSheet()
            else:
                self.textEdit.setStyleSheet('#textEdit{%s}' % self.Todo_Font_Style)
                self.style = self.textEdit.styleSheet()
                pass
        else:
            self.textEdit.setStyleSheet('#textEdit{%s}' % self.Todo_Font_Style)
            self.style = self.textEdit.styleSheet()

        if self.model.is_critical:
            self.textEdit.setStyleSheet('#textEdit{background:rgb%s; '
                                        '%s}' % (str(GColour.getAlphaColor(GColour.TaskColour.TaskIsCritial, 180)),
                                                 self.Todo_Font_Style))

    def setDragDropEnabled(self, d0 = True):
        self.drag_drop_enabled = d0

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        if not self.drag_drop_enabled:
            return
        a0.accept() # this event is propogated to the todounit_widget from the children widgets

    # def dropEvent(self, a0: QtGui.QDropEvent) -> None:
    #     pass

    def mousePressEvent(self, e):
        # print("ppp", e.pos())
        if self.drag_drop_enabled:
            self.iniDragCor[0] = e.x()
            self.iniDragCor[1] = e.y()
        # self.setFocus()
        super(ToDoUnitWidget, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):

        if e.buttons() == Qt.RightButton:
            return
        if not self.drag_drop_enabled:
            return
        # x=e.x()-self.iniDragCor[0]
        # y=e.y()-self.iniDragCor[1]
        # self.palette()
        # cor=QPoint(x,y)
        # coor = self.mapToParent(cor)
        # self.move(self.mapToParent(cor))
        # print("p_p", coor)
        mimeData = QtCore.QMimeData()
        mimeData.setText(str(self.model._id))
        image = self.grab()

        temp = QPixmap(image.size())
        temp.fill(Qt.transparent)
        p = QPainter(temp)
        p.setCompositionMode(QPainter.CompositionMode_Source)
        p.drawPixmap(0, 0, image)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        p.fillRect(temp.rect(), QColor(0, 0, 0, 80))  # 根据QColor中第四个参数设置透明度，0～255
        p.end()
        image = temp
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(image)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        # self.parentWidget().remo
        dropAction = drag.exec_(Qt.MoveAction)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super(ToDoUnitWidget, self).paintEvent(a0)

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        if not a0.source().__class__ is ToDoUnitWidget:
            return
        if a0.source() is self:
            return
        if not self.drag_drop_enabled:
            return
        source_id = a0.mimeData().text()
        target_id = self.model._id
        # a0.setDropAction(Qt.MoveAction)
        a0.acceptProposedAction()

        self.parent.todo_view.handleTodoUnitDrop(source_id, target_id)
        # self.parent.todo_view.removeWidgets(start=self_weight - 1, stop=source_weight - 1)
        # # self.parent.todo_view.bound_widget.clear()
        # self.parent.todo_view.resetUnitWidgets(start=self_weight - 1, stop=source_weight - 1)
        # self.parent.todo_view.reRenderWidget(start=self_weight - 1, stop=source_weight - 1)

    def focusOutEvent(self, a0: QtGui.QFocusEvent) -> None:
        pass

class EmptyDropFrame(QFrame):
    '''container for todo_widget'''
    def __init__(self, parent_view):
        super(EmptyDropFrame, self).__init__()
        self.setObjectName('outer_frame')
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(4, 1, 4, 1)
        self.setLayout(layout)
        self.parent_view = parent_view
        self.setAcceptDrops(True)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        a0.accept()
        pass

    def dropEvent(self, a0: QtGui.QDropEvent):
        if a0.source() is self:
            return
        # if not self.drag_drop_enabled:
        #     return
        mime_data = a0.mimeData().text()
        # a0.setDropAction(Qt.MoveAction)
        a0.acceptProposedAction()
        # self.parent.todo_view.handleTodoUnitDrop(source_id, target_id)
        self.parent_view.on_empty_frame_drop(mime_data, self)
        return

class ToDoUnitCreateDialog(QtWidgets.QDialog):
    def __init__(self, company_id: str = None, conn_project_id: str = None, conn_task_id: str = None,
                 parent=None, presenter = None):
        super(ToDoUnitCreateDialog, self).__init__(parent)
        self.parent = parent
        self.presenter = presenter
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        self.resize(450 * DataView.DF_Ratio, 300 * DataView.DF_Ratio)
        self.setWindowTitle('新建追踪')
        self.model = DataCenter.ToDo()

        self.initial_company_id = company_id
        self.initial_project_id = conn_project_id
        self.initial_task_id = conn_task_id

        self.company = company_id
        self.project= conn_project_id
        self.task = conn_task_id

        self.init_project = conn_project_id
        self.is_critical = False
        self.setInitIds()
        # 主表单
        self.mainLayout = QtWidgets.QFormLayout(self)
        self.mainLayout.setSpacing(16 * DataView.DF_Ratio)
        self.mainLayout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.mainLayout.setHorizontalSpacing(0)
        minWidth = 120
        lable = QtWidgets.QLabel(self)
        lable.setText('任务描述:')
        self.textEdit = QtWidgets.QTextEdit(self)
        # self.textEdit.focusOutEvent = types.MethodType(textEdit_focusOutEvent, self.textEdit)
        if self.initial_task_id:
            self.textEdit.setPlaceholderText('描述')
        else:
            self.textEdit.setPlaceholderText('追踪新任务：选择关联的项目，自动创建新任务\n\n追踪已有任务：'
                                             '选择关联已有的任务\n\n独立任务：不设置关联的项目')
        self.textEdit.setMinimumHeight(110 * DataView.DF_Ratio)
        self.mainLayout.addRow(lable, self.textEdit)

        lable_company = QtWidgets.QLabel(self)
        lable_company.setText('关联公司:')
        # lable_country.setAlignment
        self.combo_company = QtWidgets.QComboBox(self)
        self.combo_company.setEditable(True)
        self.combo_company.setMaximumWidth(200 * DataView.DF_Ratio)
        self.mainLayout.addRow(lable_company, self.combo_company)
        self.combo_company.currentIndexChanged.connect(self.on_company_change)
        self.combo_company.lineEdit().setPlaceholderText('公司')
        self.combo_company.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.combo_company.completer().setFilterMode(Qt.MatchContains)
        self.combo_company.completer().setCompletionMode(QCompleter.PopupCompletion)

        lable_project = QtWidgets.QLabel(self)
        lable_project.setText('关联项目:')
        self.combo_project = QtWidgets.QComboBox(self)
        self.combo_project.currentIndexChanged.connect(self.on_project_change)
        self.combo_project.setMaximumWidth(200 * DataView.DF_Ratio)
        self.mainLayout.addRow(lable_project, self.combo_project)
        self.combo_project.setEditable(True)
        self.combo_project.lineEdit().setPlaceholderText('项目')
        self.combo_project.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.combo_project.completer().setFilterMode(Qt.MatchContains)
        self.combo_project.completer().setCompletionMode(QCompleter.PopupCompletion)

        lable_type = QtWidgets.QLabel(self)
        lable_type.setText('任务类型:')
        self.combo_officejob_type = QtWidgets.QComboBox(self)
        self.combo_officejob_type.setMaximumWidth(200 * DataView.DF_Ratio)
        self.combo_officejob_type.currentIndexChanged.connect(self.on_officejob_type_change)
        self.mainLayout.addRow(lable_type, self.combo_officejob_type)

        self.combo_task = QtWidgets.QComboBox(self)
        self.combo_task.currentIndexChanged.connect(self.on_task_change)
        if not self.initial_task_id:
            lable_task = QtWidgets.QCheckBox('旧任务:', self)
            lable_task.setChecked(False)
            lable_task.toggled.connect(lambda B: self.combo_task.setEnabled(B))
            self.combo_task.setEnabled(False)
        else:
            lable_task = QtWidgets.QLabel(self)
            lable_task.setText('关联任务:')
        self.mainLayout.addRow(lable_task, self.combo_task)
        self.combo_task.setEditable(True)
        self.combo_task.lineEdit().setPlaceholderText('任务')
        self.combo_task.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.combo_task.completer().setFilterMode(Qt.MatchContains)

        lable_critical = QtWidgets.QLabel(self)
        lable_critical.setText('是否紧急:')
        self.btn_critical = SliderButton('紧急', colorChecked=GColour.TaskColour.TaskIsCritial)
        self.btn_critical.toggled.connect(self.on_critical_change)
        size = QtCore.QSize(50 * DataView.DF_Ratio, 25 * DataView.DF_Ratio)
        self.btn_critical.setFixedSize(size)
        self.mainLayout.addRow(lable_critical, self.btn_critical)
        # 禁用滚轮
        self.combo_company.wheelEvent = types.MethodType(new_wheelEvent, self.combo_company)
        self.combo_company.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.combo_project.wheelEvent = types.MethodType(new_wheelEvent, self.combo_project)
        self.combo_project.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.combo_task.wheelEvent = types.MethodType(new_wheelEvent, self.combo_task)
        self.combo_task.setFocusPolicy(QtCore.Qt.StrongFocus)
        # 设置延后
        self.lineEdit_pendingDays = QLineEdit(self)
        self.lineEdit_pendingDays.setEnabled(False)
        self.lineEdit_pendingDays.setPlaceholderText('天数')
        self.lineEdit_pendingDays.setMaximumWidth(40)
        lable_pending = QtWidgets.QCheckBox('延期:', self)
        lable_pending.setChecked(False)
        lable_pending.toggled.connect(lambda B: self.lineEdit_pendingDays.setEnabled(B))
        self.mainLayout.addRow(lable_pending, self.lineEdit_pendingDays)
        # 确定取消按钮
        self.bbOkCancel = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        self.bbOkCancel.button(QDialogButtonBox.Ok).setDefault(True)
        # self.bbOkCancel.button(QDialogButtonBox.Ok).setEnabled(False)
        self.bbOkCancel.accepted.connect(self.save_todo_unit)
        self.bbOkCancel.rejected.connect(self.reject)
        self.mainLayout.addRow(self.bbOkCancel)

        # self.combo_province.setCurrentIndex(-1)
        # self.combo_city.setCurrentIndex(-1)
        # self.combo_town.setCurrentIndex(-1)
        self.combo_company.setPlaceholderText(u'公司')
        self.combo_project.setPlaceholderText(u'项目')
        self.combo_task.setPlaceholderText(u'任务')
        self.initComboboxes()


        # self.company_completer = QCompleter(self.company_names, self)
        # self.company_completer.setFilterMode(Qt.MatchContains)
        # self.combo_company.lineEdit().setCompleter(self.company_completer)

        # 初始化下拉列表

    def initComboboxes(self):
        self.companies = self.getAllCompany()
        self.company_names = [company[1] for company in self.companies]
        self.projects = None
        self.tasks = None # tuple('_id', 'task_desc', 'officejob_type')
        office_job_dict = DataCenter.office_job_dict
        self.combo_officejob_type.addItems(list(office_job_dict.values()))
        self.combo_company.addItems(self.company_names)
        if self.initial_company_id:
            company_ids = [company[0] for company in self.companies]
            self.combo_company.setCurrentIndex(company_ids.index(self.initial_company_id))  # 触发信号，自动初始化后面的下拉按钮]

            if self.initial_project_id:
                self.projects = self.getCompanyProjects(self.initial_company_id)
                project_ids = [project[0] for project in self.projects]
                try:
                    project_id_index = project_ids.index(self.initial_project_id)
                except ValueError as e:
                    global_logger.info('initial_project_id does not exist ')
                    return
                self.combo_project.setCurrentIndex(project_id_index)  # 触发信号，自动初始化后面的下拉按钮

                if self.initial_task_id:
                    self.tasks = self.getProjectTasks(self.initial_project_id)
                    task_ids = [task[0] for task in self.tasks]
                    task_names = [task[1] for task in self.tasks]
                    if not self.initial_task_id in task_ids:
                        return
                    try:
                        task_index = task_ids.index(self.initial_task_id)
                    except ValueError:
                        return
                    task_office_job_type = self.tasks[task_index][2]
                    task_desc = task_names[task_index]
                    # self.combo_task.addItems(task_names)
                    self.combo_task.setCurrentIndex(task_index)
                    self.textEdit.setText(task_desc)
                    self.presenter.setModelOfficeJobType(task_office_job_type)
                    self.combo_officejob_type.setCurrentIndex(
                        list(office_job_dict.keys()).index(task_office_job_type))

    def checkInputValidation(self):
        if not self.textEdit.toPlainText().strip():
            QtWidgets.QMessageBox.about(self, '任务描述', '请输入任务描述！')
            return False

        if not (self.combo_company.lineEdit().text() or self.combo_project.lineEdit().text()):  # 未输入具体客户或项目
            return True

        if self.combo_company.lineEdit().text() and self.combo_company.lineEdit().text() not in self.company_names:
            QtWidgets.QMessageBox.about(self, '公司名称', '该公司名称不存在，\n请重新输入！')
            self.combo_company.lineEdit().setFocus()
            self.combo_company.lineEdit().selectAll()
            return False

        if self.combo_project.lineEdit().text() and self.combo_project.lineEdit().text() not in self.project_names:
            QtWidgets.QMessageBox.about(self, '无效名称', '该公司无此项目，\n\n请重新输入！')
            self.combo_project.lineEdit().clear()
            self.combo_project.lineEdit().setFocus()
            return False

        if self.task and self.presenter.checkTaskTodoExistance(self.task):
            QtWidgets.QMessageBox.about(self, '重复添加', '该任务已经添加追踪！')
            return False

        return True

    def on_company_change(self, index):
        if index == -1:
            return
        # print(index)
        # print('wheel_changeC', self.combo_company.currentIndex())
        # print('wheel_changeC', self.combo_company.count())
        self.company = self.companies[self.combo_company.currentIndex()][0]  # company_id
        # 清空后列数据
        self.project = None
        self.task = None
        # 重置后列控件
        self.combo_project.clear()
        self.combo_task.clear()
        self.combo_project.setCurrentIndex(-1)
        self.combo_task.setCurrentIndex(-1)
        # 初始化后列数据和控件
        self.projects = self.getCompanyProjects(self.company)
        self.project_names = [project[1] for project in self.projects]
        self.combo_project.addItems(self.project_names)
        # project_completer = QCompleter(self.combo_project.model(),self)
        # project_completer.setFilterMode(Qt.MatchContains)
        # self.combo_project.lineEdit().setCompleter(project_completer)
        self.tasks = None

    def on_project_change(self, index):
        if index == -1:
            return
        # print(index)
        # print('wheel_changeP', self.combo_project.currentIndex())
        self.project = self.projects[self.combo_project.currentIndex()][0]  # project_id
        # 清空后列数据
        self.task = None
        # 重置后列控件
        self.combo_task.clear()
        self.combo_task.setCurrentIndex(-1)
        # 初始化后列数据和控件
        self.tasks = self.getProjectTasks(self.project)
        self.combo_task.addItems([task[1] if task[1] and len(task[1]) < 20 else\
                                      task[1][:19] + '..' if task[1] else '..' for task in
                                  self.tasks])  # 需处理Null异常
        # task_completer = QCompleter(self.combo_task.model(), self)
        # task_completer.setFilterMode(Qt.MatchContains)
        # self.combo_task.lineEdit().setCompleter(task_completer)

    def on_task_change(self, index):
        print('wheel_changeT', self.combo_task.currentIndex())
        if self.combo_task.currentIndex() == -1:
            return
        self.task = self.tasks[index][0]
        self.textEdit.setText(self.tasks[index][1])
        self.officejob_type = self.tasks[index][2]
        self.combo_officejob_type.setCurrentIndex(
            list(DataCenter.office_job_dict.keys()).index(self.tasks[index][2]))

    def on_officejob_type_change(self, index):
        if index == -1:
            return
        self.officejob_type = list(DataCenter.office_job_dict.keys())[index]

    def on_critical_change(self, is_critical):
        self.is_critical = is_critical

    def save_todo_unit(self):
        ok = self.checkInputValidation()
        if not ok:
            return
        # _id = Snow('td').get()
        fields_values = {}
        fields_values['conn_project_id'] = self.project
        fields_values['conn_task_id'] = self.task
        fields_values['conn_company_id'] = self.company
        fields_values['todo_desc'] = self.textEdit.toPlainText()
        fields_values['is_critical'] = self.is_critical
        fields_values['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        fields_values['pending_days'] = self.lineEdit_pendingDays.text()
        fields_values['officejob_type'] = self.officejob_type
        fields_values['status'] = 0
        json_fields_values = json.dumps(fields_values)
        self.presenter.saveModel(json_fields_values)

        self.accept()


    def setInitIds(self):
        id_fields = ['initial_company_id', 'initial_project_id','initial_task_id']
        json_id_fields = json.dumps(id_fields)
        id_map_json = self.presenter.getInitFields(json_id_fields)
        id_map: dict = json.loads(id_map_json)
        for field, value in id_map.items():
            setattr(self, field, value)

    def getAllCompany(self):
        companies = self.presenter.getAllCompany()
        return companies

    def getCompanyProjects(self, company_id: str):
        projects = self.presenter.getCompanyProjects(company_id)
        return projects

    def getProjectTasks(self, project_id: str):
        tasks = self.presenter.getProjectTasks(project_id)
        return tasks

class SingleSelectionDialog(QtWidgets.QDialog):
    def __init__(self, parent = None, title:str = '', choices:list[str] = None, first_choice_default:bool = False):
        super(SingleSelectionDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        # self.setWindow()
        self.choices = choices
        self.index_choice = None
        self.first_choice_default = first_choice_default
        self.setChoices(self.choices)

    def setChoices(self, choices:list[str]) -> None:
        self.choices = choices
        if not self.choices:
            return
        n_choices = len(self.choices)
        self.groupbox = QtWidgets.QGroupBox(self)
        self.groupbox.setMinimumSize(50, 25 * n_choices + 10)
        Vlayout = QtWidgets.QVBoxLayout(self)

        pixes_move = 5
        for i, choice in enumerate(self.choices):
            radio_button = QtWidgets.QRadioButton(self.groupbox)
            radio_button.setText(choice)
            radio_button.move(5, pixes_move)
            radio_button.clicked.connect(self.on_set_choice)
            pixes_move += 25

        ok_cancel_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        ok_cancel_button.button(QDialogButtonBox.Ok).setDefault(True)
        # ok_cancel_button.button(QDialogButtonBox.Ok).setEnabled(False)
        ok_cancel_button.accepted.connect(self.accept)
        ok_cancel_button.rejected.connect(self.reject)
        Vlayout.addWidget(self.groupbox)
        Vlayout.addWidget(ok_cancel_button)
        if self.first_choice_default:
            self.groupbox.findChildren(QtWidgets.QRadioButton)[0].setChecked(True)
            self.index_choice = 0

    def on_set_choice(self):
        for i, radio in enumerate(self.groupbox.findChildren(QtWidgets.QRadioButton)):
            if radio.isChecked():
                self.index_choice = i
                return

    @classmethod
    def getChoice(cls, choices:list[str], title:str = '',  parent=None, first_choice_default:bool = False):
        dialog = cls(parent, title, choices,first_choice_default)
        ok = dialog.exec_()
        index_choice = dialog.index_choice
        del dialog
        return (ok, index_choice)

class ThemeChooseDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ThemeChooseDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setWindowTitle('界面风格')
        Vlayout = QtWidgets.QVBoxLayout(self)
        self.groupbox = QtWidgets.QGroupBox(self)
        self.groupbox.setMinimumSize(50, 105)
        win_theme_radio = QtWidgets.QRadioButton(self.groupbox)
        win_theme_radio.setText('Windows风格')
        win_theme_radio.setChecked(True)
        win_theme_radio.move(5, 5)
        win_theme_radio.clicked.connect(self.on_set_theme)
        mac_theme_radion = QtWidgets.QRadioButton(self.groupbox)
        mac_theme_radion.setText('MacOS风格')
        mac_theme_radion.move(5, 30)
        mac_theme_radion.clicked.connect(self.on_set_theme)
        linux_theme_radio = QtWidgets.QRadioButton(self.groupbox)
        linux_theme_radio.setText('Linux风格')
        linux_theme_radio.move(5, 55)
        linux_theme_radio.clicked.connect(self.on_set_theme)
        dark_theme_radio = QtWidgets.QRadioButton(self.groupbox)
        dark_theme_radio.setText('暗黑风格')
        dark_theme_radio.move(5, 80)
        dark_theme_radio.clicked.connect(self.on_set_theme)
        ok_cancel_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        ok_cancel_button.button(QDialogButtonBox.Ok).setDefault(True)
        # ok_cancel_button.button(QDialogButtonBox.Ok).setEnabled(False)
        ok_cancel_button.accepted.connect(self.accept)
        ok_cancel_button.rejected.connect(self.reject)
        Vlayout.addWidget(self.groupbox)
        Vlayout.addWidget(ok_cancel_button)
        self.theme = 0

    def on_set_theme(self):
        for i, radio in enumerate(self.groupbox.findChildren(QtWidgets.QRadioButton)):
            if radio.isChecked():
                self.theme = i

    @staticmethod
    def getTheme(parent=None):
        dialog = ThemeChooseDialog(parent)
        ok = dialog.exec_()
        theme = dialog.theme
        return (ok, theme)


class DirectoryChooseBox(QtWidgets.QDialog):
    def __init__(self, title: str, hint_text: str = None, parent=None):
        super(DirectoryChooseBox, self).__init__(parent)
        self.title = title
        self.hint_text = hint_text
        # self.setWindowFlags(QtCore.Qt.Window|Qt.WindowCloseButtonHint)
        self.setWindowTitle(self.title)
        self.setFixedSize(580, 320)
        self.VLayOut = QtWidgets.QVBoxLayout(self)
        self.lable = QtWidgets.QLabel(self)
        self.lable.setText('设置数据文件路径\n\n请重置您的个人数据和文件的保存文件夹,以英文命名。\n可以选择已经使用的路径，或创建新的路径。每个不同的文件路径代表着完全独立的用户，使用不同的路径意味着'
                           '与之前的记录完全隔离。\n\n不要放在解压出来的那个程序文件夹（\\GreenCRM）里！'
                           '\n\n在连接到服务器之前，删除这个文件夹和里面的文件，会导致所有记录丢失。\n最好不要将个人文件放在C盘，以免重装系统导致文件丢失。')
        self.lable.setWordWrap(True)
        self.VLayOut.addWidget(self.lable)
        self.HLayOut = QtWidgets.QHBoxLayout(self)
        self.VLayOut.addLayout(self.HLayOut)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setPlaceholderText(self.hint_text)
        self.lineEdit.setFixedSize(500, 30)
        self.HLayOut.addWidget(self.lineEdit)

        self.path_button = QtWidgets.QPushButton(self)
        self.path_button.setText('目录..')
        self.path_button.clicked.connect(self.on_select_button_clicked)
        self.path_button.setMaximumWidth(50)
        self.HLayOut.addWidget(self.path_button)

        self.dialog_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.dialog_button.button(QDialogButtonBox.Ok).setDefault(True)
        self.dialog_button.button(QDialogButtonBox.Ok).setEnabled(False)
        self.dialog_button.accepted.connect(self.accept)
        self.dialog_button.rejected.connect(self.reject)
        self.VLayOut.addWidget(self.dialog_button)

    def on_select_button_clicked(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, '选择个人数据存放路径',
                                                          os.path.expanduser('~') + '\Documents')
        if os.path.isdir(path):
            self.dialog_button.button(QDialogButtonBox.Ok).setEnabled(True)
        self.lineEdit.setText(path)

    @staticmethod
    def getDirectory(title: str, hint_text: str = None, parent=None):
        dialog = DirectoryChooseBox(title=title, hint_text=hint_text, parent=parent)
        result = dialog.exec_()
        directory = dialog.lineEdit.text()
        return (directory, result == QtWidgets.QDialog.Accepted)


class UI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent)
        self.resize(1200, 800)
        layout = QtWidgets.QVBoxLayout()
        self.tableWidget = QtWidgets.QTableWidget()
        layout.addWidget(self.tableWidget)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['1', '2'])

        for i in range(5):
            textedit = MyQTextEdit()
            self.tableWidget.setCellWidget(i, 3, textedit)
            textedit.DoubleClicked.connect(lambda: self.showSlider(self))
        self.setLayout(layout)

    def showSlider(self, parent):
        sender = self.sender()

        self.slider = MySlider(sender, parent)
        # sender.installEventFilter()
        # self.slider.installEventFilter(self)
        self.slider.show()
        # self.slider.setFocus()

    # def  eventFilter(self,obj, event):
    #     #if obj != self.slider:
    #     if event.type()==QEvent.MouseButtonPress:
    #         mouseEvent=QMouseEvent(event)
    #         if mouseEvent.buttons()==Qt.LeftButton:
    #             self.slider.close()
    #     return QtWidgets.QWidget.eventFilter(self,obj,event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    btn = ToDoUnitWidget()
    btn.isCritial_slideButton.setFontText('紧急')
    btn.todoStatus_triSlideButton.setFontText(['未办', '进行', '完成'])
    btn.show()
    sys.exit(app.exec_())
