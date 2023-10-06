import json
import math
import os
import threading

import types
from copy import deepcopy
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QStyle, QStyleOption
from PyQt5.QtCore import pyqtSignal, QEvent, Qt, QUrl, QRect, QSize, QTimer
from RedefinedWidget import ToDoUnitWidget
from abc import ABC, abstractmethod
import PyQt5
from PyQt5.QtWidgets import QMessageBox


class WidgetGroupFrame(QtWidgets.QFrame):
    USE_V_EXPAND = 11
    USE_H_EXPAND = 12
    EXPAND_LEFT = 21
    EXPAND_RIGHT = 22
    EXPAND_UP= 23
    EXPAND_DOWN = 24

    def __init__(self, parent_view, parent_widget):
        super().__init__(parent_widget)
        self.parent_view = parent_view
        self.expand_policy = WidgetGroupFrame.USE_V_EXPAND
        self.v_expand_direction = WidgetGroupFrame.EXPAND_DOWN
        self.h_expand_direction = WidgetGroupFrame.EXPAND_RIGHT
        self.external_v_spacing = 0
        self.external_h_spacing = 0
        self.mouse_at_direction = 0
        self.nested_mode = True
        self.ignore_leave = False
        self.setMouseTracking(True)
        self.nested_style_sheet = '#group_frame{background-color: rgba(149,152,135,255);margin:1px; border-width: 1px;'\
                           'border-radius:7px; border-style: dashed;border-color: '\
                           'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), ' \
                                  'stop:1 rgba(171, 221, 252, 205));}'
        self.expanded_style_sheet = '#group_frame{background-color: rgba(169,172,185,205);margin:1px; border-width: 1px;'\
                           'border-radius:7px; border-style: dashed;border-color: qlineargradient(spread:pad, x1:0.5, ' \
                                    'y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}'
        self.timer = QTimer(self)
        self.timerId = self.timer.timerId()
        self.timer.timeout.connect(self.showExpand)


    def addWidgets(self, widgets:list[list[QWidget]]):
        """the first list in widgets contains the widgets to be always shown, the second contains the widgets that can
         be hidden in nested mode."""
        self.standing_widgets = widgets[0]
        self.hiding_widgets = widgets[1]

    def setMetrics(self, geo_X:int, geo_Y:int, margin:int, inner_spacing:int,
                   external_h_spacing:int, external_v_spacing:int, widget_height:int, widget_width:int):
        self.default_geo_X = geo_X
        self.default_geo_Y = geo_Y
        self.margin = margin
        self.inner_spacing = inner_spacing
        self.external_v_spacing = external_v_spacing
        self.external_h_spacing = external_h_spacing
        self.widget_height = widget_height
        self.widget_width = widget_width
        self.rect_left = QtCore.QRect()
        self.rect_right = QtCore.QRect()
        self.rect_top = QtCore.QRect()
        self.rect_buttom = QtCore.QRect()

    def setExpandScale(self,n_col, n_row ):
        if self.expand_policy == WidgetGroupFrame.USE_V_EXPAND:
            self.set_width = self.widget_width * n_col + self.external_v_spacing * (n_col-1) + self.margin * 2
            self.set_height = self.widget_height * n_row + self.external_h_spacing * (n_row - 1) + self.margin * 2

            # self.set_height = self.widget_height * (len(self.standing_widgets)+len(self.hiding_widgets)) + \
            #               self.external_v_spacing * ((len(self.standing_widgets)+len(self.hiding_widgets)) - 1) + self.margin * 2
        else:
            self.set_width = self.widget_width * n_col + self.external_v_spacing * (n_col - 1) + self.margin * 2
            self.set_height = self.widget_height * n_row + self.external_h_spacing * (n_row - 1) + self.margin * 2

            # self.set_width = self.widget_width * (len(self.standing_widgets)+len(self.hiding_widgets))+  \
            #               self.external_h_spacing * ((len(self.standing_widgets)+len(self.hiding_widgets)) - 1) + self.margin * 2
            # self.set_height = self.widget_height + self.margin * 2

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        self.timer.start(300)

    def setStetchScale(self):
        self.set_width = self.widget_width + self.margin * 2
        self.set_height = self.widget_height * (len(self.standing_widgets)+len(self.hiding_widgets)) + \
                      self.external_v_spacing * (len(self.standing_widgets)+len(self.hiding_widgets) - 1) + self.margin * 2

    def setNestedScale(self, n_exposure: int = 1):
        self.set_width = self.widget_width + self.margin * 2
        self.set_height = self.widget_height * len(self.standing_widgets) + (self.external_v_spacing + self.margin * 2) \
                          * (len(self.standing_widgets) - 1) + self.margin * 2

    def stretchFull(self):
        self.nested_mode = False
        self.setStetchScale()
        self.setFixedSize(self.set_width, self.set_height)

    def showExpand(self):
        self.timer.stop()
        if len(self.hiding_widgets) == 0:
            return
        self.nested_mode = False
        self.entered_by_intention = False
        n_widgets = len(self.standing_widgets) + len(self.hiding_widgets)
        n_col = math.ceil(math.sqrt(n_widgets))
        n_row = math.ceil(n_widgets/n_col)
        old_width = self.set_width
        old_height = self.set_height
        self_X = self.geometry().x()
        self_Y = self.geometry().y()
        X = self_X
        Y = self_Y
        view_port_size:QSize = self.parent_view.tab_bar.todoPanelScroll.viewport().size()
        parent_width = view_port_size.width()
        parent_height = view_port_size.height()
        self.setExpandScale(n_col, n_row)

        if self_X > parent_width  - self.set_width :
            self.h_expand_direction = WidgetGroupFrame.EXPAND_LEFT
        if self_X < self.set_width - old_width:
            self.h_expand_direction = WidgetGroupFrame.EXPAND_RIGHT

        if self_Y > parent_height - self.set_height:
            self.v_expand_direction = WidgetGroupFrame.EXPAND_UP
        if self_Y < self.set_height - old_height:
            self.v_expand_direction = WidgetGroupFrame.EXPAND_DOWN

        self.setFixedSize(self.set_width, self.set_height)


        if self.h_expand_direction == WidgetGroupFrame.EXPAND_LEFT:
            X = X + old_width - self.set_width
        if self.v_expand_direction == WidgetGroupFrame.EXPAND_UP:
            Y = Y + old_height - self.set_height

        self.setGeometry(QRect(X, Y, self.set_width, self.set_height))
        self.raise_()
        self.setStyleSheet(self.expanded_style_sheet)
        self.setupWidgets(n_col)
        self.hideExpandButtons()

    def showNested(self, n_exposure=1):
        self.nested_mode = True
        self.setNestedScale(n_exposure)
        self.setFixedSize(self.set_width, self.set_height)
        self.setupWidgets(n_col=1)
        self.createExpandButtons()
        self.showExpandButtons()
        self.setStyleSheet(self.nested_style_sheet)
        # self.setGeometry(QRect(self.default_geo_X, self.default_geo_Y, self.set_width, self.set_height))

    def collapseFromExpand(self):
        for widget in self.findChildren(ToDoUnitWidget):
            widget.hide()
        self.move(self.old_positon)
        self.showNested()

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        POld = a0.oldPos()
        PNew = a0.pos()
        if self.nested_mode == True:
            self.old_positon = POld

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        width = a0.size().width()
        height = a0.size().height()
        self.rect_left = QtCore.QRect(0, self.margin*2, self.margin*2, height - self.margin*4)
        self.rect_right = QtCore.QRect(width - self.margin*2, self.margin*2, self.margin*2, height-self.margin*4)
        self.rect_top = QtCore.QRect(self.margin*2, 0, width-self.margin*4, self.margin*2)
        self.rect_buttom = QtCore.QRect(self.margin*2, height-self.margin*2, width-self.margin*4 ,height - self.margin*4)

    def setupWidgets(self, n_col):
        X = self.margin
        Y = self.margin
        x_factor = 0
        y_factor = 0
        if self.nested_mode:
            y_factor = 1
            use_widgets = self.standing_widgets
        else:
            use_widgets = self.standing_widgets + self.hiding_widgets
            if self.expand_policy == WidgetGroupFrame.USE_V_EXPAND:
                y_factor = 1
            else:
                x_factor = 1

        for i, id in enumerate(use_widgets):
            unit_view = self.parent_view.todo_id_view_dict[id]
            if unit_view.parent_widget is not self or unit_view.todoWidget is None:
                unit_view.todoWidget = None
                unit_view.setWidget(self)
            widget = unit_view.todoWidget
            widget.setFixedSize(self.widget_width, self.widget_height)
            widget.move(X, Y)
            widget.show()
            X += (self.inner_spacing + self.widget_width)
            if (i+1)% n_col == 0:
                X =  self.margin
                Y += self.inner_spacing + self.widget_height
            # X += (self.inner_spacing + self.widget_width) * x_factor
            # Y += (self.inner_spacing + self.widget_height) * y_factor

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if self.is_cursor_within():
            return

        self.timer.stop()
        if self.nested_mode == False and self.entered_by_intention == True:
            self.collapseFromExpand()

    def is_cursor_within(self):
        parent_widget = self.parentWidget()
        cursor = parent_widget.mapFromGlobal(QtGui.QCursor().pos())
        geo = self.geometry()
        return geo.contains(cursor)

    # def enterEvent(self, a0: QtCore.QEvent) -> None:
    #
    #     if self.nested_mode == False:
    #         self.entered_by_intention = True


    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.nested_mode == False:
            self.entered_by_intention = True
        return super().mouseMoveEvent(a0)
        if not self.nested_mode :
            return super(WidgetGroupFrame, self).mouseMoveEvent(a0)
        cursor_pos = a0.pos()
        self_rect = self.geometry()
        print('cursor_pos',cursor_pos)
        print('self_rect', self.geometry())
        print('set_width', self.set_width)
        print('set_height', self.set_height)
        print('rect_left',self.rect_left)
        print('rect_right', self.rect_right)
        print('rect_top', self.rect_top)
        print('rect_buttom', self.rect_buttom)

        direction = 0
        if self.rect_left.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_LEFT
        elif self.rect_right.contains(cursor_pos):
            print('rect_right', self.rect_right, 'contains cursor_pos', cursor_pos)
            direction = WidgetGroupFrame.EXPAND_RIGHT
        elif self.rect_top.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_UP
        elif self.rect_buttom.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_DOWN
        else:
            direction = 0
        print('direction = ',direction)
        if direction :
            self.createExpandButtons()
            self.showExpandButtons()
        elif direction == 0:
            self.hideExpandButtons()
        else:
            pass
        self.mouse_at_direction = direction
        super().mouseMoveEvent(a0)

    def on_expand_button_clicked(self):
        if self.sender() is self.button_left:
            self.expand_policy = WidgetGroupFrame.USE_H_EXPAND
            self.v_expand_direction = WidgetGroupFrame.EXPAND_LEFT
        elif self.sender() is self.button_right:
            self.expand_policy = WidgetGroupFrame.USE_H_EXPAND
            self.v_expand_direction = WidgetGroupFrame.EXPAND_RIGHT
        elif self.sender() is self.button_top:
            self.expand_policy = WidgetGroupFrame.USE_V_EXPAND
            self.h_expand_direction = WidgetGroupFrame.EXPAND_UP
        elif self.sender() is self.button_buttom:
            self.expand_policy = WidgetGroupFrame.USE_V_EXPAND
            self.h_expand_direction = WidgetGroupFrame.EXPAND_DOWN
        else:
            pass
        self.showExpand()

    def createExpandButtons(self):
        if hasattr(self, 'expand_button_created'):
            if self.expand_button_created == True:
                return
        icon_half_length = 0
        icon_width = 0
        self.expand_button_created = True
        button_long_edge = self.margin * 4
        button_short_edge = self.margin * 2
        # button_style = '{{border-style: solid;border-top-color: ' \
        #                'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), '\
        #                 'stop:1 rgb(222, 222, 222));	border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5,'\
        #                    'x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'\
        #                    'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '\
        #                    'stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'\
        #                    'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '\
        #                    'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'\
        #                               'border-width: 0px;border-radius: 0px;color: #202020;text-align: '\
        #                               'padding: 0px;background-color: rgba(220,220,220,0);}'\
        #                     'hover{border-style: solid;'\
        #                    'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '\
        #                    'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));	'\
        #                    'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '\
        #                    'stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'\
        #                    'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, '\
        #                    'stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'\
        #                    'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, '\
        #                    'stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'\
        #                     'border-width: 1px;border-radius: 5px;color: #202020;text-align: left;'\
        #                     'padding: 0px;background-color: rgb(200,225,255);} '
        button_style = "background:transparent; border-width: 0px;"
        self.button_left = QtWidgets.QPushButton(self)
        self.button_left.setFixedSize(button_short_edge, button_long_edge)
        self.button_left.setIcon(QtGui.QIcon(''))
        self.button_left.setStyleSheet(button_style)
        self.button_left.move(0, int(self.set_height/2 - button_long_edge/2))

        self.button_right = QtWidgets.QPushButton(self)
        self.button_right.setFixedSize(button_short_edge, button_long_edge)
        self.button_right.setStyleSheet(button_style)
        self.button_right.setIcon(QtGui.QIcon(''))
        self.button_right.move(self.set_width - button_short_edge, int(self.set_height/2 - button_long_edge/2))


        self.button_top = QtWidgets.QPushButton(self)
        self.button_top.setFixedSize(button_long_edge, button_short_edge)
        self.button_top.setStyleSheet(button_style)
        self.button_top.setIcon(QtGui.QIcon(''))
        self.button_top.move(int(self.set_width/2 - button_long_edge/2), 0)

        self.button_buttom = QtWidgets.QPushButton(self)
        self.button_buttom.setFixedSize(button_long_edge, button_short_edge)
        self.button_buttom.setStyleSheet(button_style)
        self.button_buttom.setIcon(QtGui.QIcon(''))
        self.button_buttom.move(int(self.set_width/2 - button_long_edge/2), self.set_height-button_short_edge)

        self.button_left.clicked.connect(self.on_expand_button_clicked)
        self.button_right.clicked.connect(self.on_expand_button_clicked)
        self.button_top.clicked.connect(self.on_expand_button_clicked)
        self.button_buttom.clicked.connect(self.on_expand_button_clicked)
        self.hideExpandButtons()

    def destroy_expand_buttons(self):
        button_names = ['button_left', 'button_right', 'button_top', 'button_buttom']
        for name in button_names:
            self.__setattr__(name, None)

    def showExpandButtons(self):
        if len(self.hiding_widgets) == 0:
            return

        settings = {
        'left_icon': './images/left_arrow.png',
        'right_icon' : './images/right_arrow.png',
        'top_icon' : './images/up_arrow.png',
        'buttom_icon' : './images/down_arrow.png',}
        map = {
            WidgetGroupFrame.EXPAND_UP: 'top_icon',
            WidgetGroupFrame.EXPAND_DOWN: 'buttom_icon',
            WidgetGroupFrame.EXPAND_RIGHT: 'right_icon',
            WidgetGroupFrame.EXPAND_LEFT: 'left_icon',
        }

        # settings[map[direction]] += '_highlight'
        self.button_left.setIcon(QtGui.QIcon(settings[map[WidgetGroupFrame.EXPAND_LEFT]]))
        self.button_right.setIcon(QtGui.QIcon(settings[map[WidgetGroupFrame.EXPAND_RIGHT]]))
        self.button_top.setIcon(QtGui.QIcon(settings[map[WidgetGroupFrame.EXPAND_UP]]))
        self.button_buttom.setIcon(QtGui.QIcon(settings[map[WidgetGroupFrame.EXPAND_DOWN]]))
        button_names = ['button_left', 'button_right', 'button_top', 'button_buttom']
        for name in button_names:
            self.__getattribute__(name).show()

    def hideExpandButtons(self):
        n = 0
        if not hasattr(self, 'expand_button_created'):
            return
        button_names = ['button_left', 'button_right', 'button_top', 'button_buttom']
        for name in button_names:
            self.__getattribute__(name).hide()


class VirtualVBoxLayout(QtWidgets.QFrame):
    def __init__(self, parent):
        super(VirtualVBoxLayout, self).__init__(parent)
        self.parent = parent
        self.widgets = []
    def addWidget(self):
        pass

class GridPanel(QtWidgets.QScrollArea):
    USE_V_SCROLL = 11
    USE_H_SCROLL = 12

    def __init__(self, parent_view=None, parent_widget=None):
        super().__init__(parent=parent_widget)
        self.parent_view = parent_view
        self.parent_widget = parent_widget
        self.scroll_direction = self.USE_H_SCROLL
        # self.setAttribute(Qt.WA_StyledBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.grid_model = None
        self.unit_v_size = 0
        self.unit_h_size = 0
        self.margin = 2
        self.unit_spacing = 1
        self.group_spacing = 4
        self.grid_model = None
        # self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        # self.horizontalLayout.setAlignment(Qt.AlignLeft)
        # self.setStyleSheet('background:blue')
        # self.setLayout(self.horizontalLayout)
        self.setMetrics(2, 4, 4 ,4, 10, 10, 100, 250)
        self.lanes = []


    # def makeGroupFrames(self):
    #     for

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


    def setMetrics(self, margin:int, widget_spacing:int, group_h_spacing:int, group_v_spacing:int, group_h_margin:int,
                   group_v_margin:int, widget_height:int, widget_width:int):
        self.margin = margin
        self.widget_spacing = widget_spacing
        self.group_h_spacing = group_h_spacing
        self.group_v_spacing = group_v_spacing
        self.group_h_margin = group_h_margin
        self.group_v_margin = group_v_margin
        self.widget_height = widget_height
        self.widget_width = widget_width

    def clearLanes(self):
        for widget in self.findChildren(WidgetGroupFrame):
            widget.deleteLater()
        self.lanes.clear()

    def rearrange_lane(self):
        pass

    # def makeGroups(self):
    #     for lane in self.lanes:
    #
    #     pass

    def addLane(self, lane_widgets:list[QWidget]):
        self.lanes.append(lane_widgets)


    def lay_widgets(self):
        X = self.margin
        Y = self.margin
        group_widget: WidgetGroupFrame
        # Y = self.margin
        # for key, view in self.parent_view.todo_id_view_dict.items():
        #     view.setWidget(self)
        #     widget=view.todoWidget
        #     widget.move(X, Y)
        #     # widget.setFixedSize(widget.set_width, widget.widget_height)
        #     # widget.showNested(2)
        #     # button = QtWidgets.QPushButton(widget)
        #     # button.move(20, 20)
        #     # button.show()
        #     widget.setParent(self)
        #     widget.show()
        #     widget.repaint()
        #     # widget.update()
        #     Y += self.widget_height + self.group_v_spacing
        # X += self.widget_width + self.group_h_margin * 2 + self.group_h_spacing
        total_height_logger = 0
        for lane in self.lanes:
            Y = self.margin
            group_widget_set_width = 0
            for group_widget in lane:
                group_widget.setMetrics(X, Y, self.group_h_margin, 4, self.group_h_spacing, self.group_v_spacing,
                                  self.widget_height,self.widget_width)
                group_widget.move(X, Y)
                group_widget.showNested(2)
                group_widget.show()
                group_widget.setStyleSheet(
                    '#group_frame{background-color: rgba(149,152,135,255);margin:1px; border-width: 0px;'
                    'border-radius:7px; border-style: dashed;border-color: '
                    'qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(200, 220, 255, 155), stop:1 rgba(171, 221, 252, 205));}')
                group_widget_set_width = group_widget.set_width
                Y += group_widget.set_height + self.group_v_spacing
            else:
                total_height_logger  = Y if Y  > total_height_logger else total_height_logger
            X += group_widget_set_width + self.group_h_spacing
        self.setMinimumSize(X, total_height_logger)


    def widgetResizeEvent(self, source):

        pass

    def hide_widgets(self):

        pass

    def insert_widgets(self):
        pass
    def make_group(self):
        pass

    def on_group_button_fold(self):
        pass

    def on_group_button_expand(self):
        pass

    def on_widget_expand(self):
        pass