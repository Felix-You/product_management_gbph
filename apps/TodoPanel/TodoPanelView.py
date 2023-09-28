
import os
import types
from copy import deepcopy
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget
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


class WidgetGroupFrame(QWidget):
    USE_V_EXPAND = 11
    USE_H_EXPAND = 12
    EXPAND_LEFT = 21
    EXPAND_RIGHT = 22
    EXPAND_UP= 23
    EXPAND_DOWN = 24

    def __init__(self):
        super().__init__()
        self.expand_policy = WidgetGroupFrame.USE_V_EXPAND
        self.v_expand_direction = WidgetGroupFrame.EXPAND_DOWN
        self.h_expand_direction = WidgetGroupFrame.EXPAND_RIGHT
        self.external_v_spacing = 0
        self.external_h_spacing = 0
        self.mouse_at_direction = 0
        self.nested_mode = True
        self.setMouseTracking(True)

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

    def setExpandScale(self ):
        if self.expand_policy == WidgetGroupFrame.USE_V_EXPAND:
            self.width = self.widget_width + self.margin * 2
            self.height = self.widget_height * len(self.widgets) + \
                          self.external_v_spacing * (len(self.widgets) - 1) + self.margin * 2
        else:
            self.width = self.widget_width * len(self.widgets) +  \
                          self.external_h_spacing * (len(self.widgets) - 1) + self.margin * 2
            self.height = self.widget_height + self.margin * 2

    def setStetchScale(self):
        self.width = self.widget_width + self.margin * 2
        self.height = self.widget_height * len(self.widgets) + \
                      self.external_v_spacing * (len(self.widgets) - 1) + self.margin * 2

    def setNestedScale(self, n_exposure: int):
        self.width = self.widget_width + self.margin * 2
        self.height = self.widget_height * n_exposure + \
                      self.external_v_spacing * (n_exposure - 1) + self.margin * 2

    def stretchFull(self):
        self.setStetchScale()
        self.setFixedSize(self.width, self.height)

    def showExpand(self):
        old_width = self.width
        old_height = self.height
        self_X = self.geometry().x()
        self_Y = self.geometry().y()
        X = self_X
        Y = self_Y
        parent_width = self.parent().geometry().width()
        parent_height = self.parent().geometry().height()
        self.setExpandScale()
        if self_X < self.width - old_width:
            self.h_expand_direction = WidgetGroupFrame.EXPAND_RIGHT
        elif self_X > parent_width - self.width:
            self.h_expand_direction = WidgetGroupFrame.EXPAND_LEFT
        if self_Y < self.height - old_height:
            self.v_expand_direction = WidgetGroupFrame.EXPAND_DOWN
        elif self_Y > parent_height - self.height:
            self.v_expand_direction = WidgetGroupFrame.EXPAND_UP
        self.setFixedSize(self.width, self.height)

        if self.h_expand_direction == WidgetGroupFrame.EXPAND_LEFT:
            X = X + old_width - self.width
        if self.v_expand_direction == WidgetGroupFrame.EXPAND_UP:
            Y = Y + old_height - self.height
        self.setGeometry(X, Y, self.width, self.height)

    def showNested(self, n_exposure):
        self.setNestedScale(n_exposure)
        self.setupWidgets()
        self.setGeometry(self.default_geo_X, self.default_geo_Y, self.width, self.height)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        width = a0.size().width()
        height = a0.size().height()
        self.rect_left = QtCore.QRect(0, self.margin*2, self.margin*2, height - self.margin*4)
        self.rect_right = QtCore.QRect(width - self.margin*2, self.margin*2, self.margin*2, height-self.margin*4)
        self.rect_top = QtCore.QRect(self.margin*2, 0, width-self.margin*4, self.margin*2)
        self.rect_buttom = QtCore.QRect(self.margin*2, height-self.margin*2, width-self.margin*4 ,self.margin*2)
        pass

    def setGeometry(self, a0: QtCore.QRect) -> None:
        super().setGeometry(a0)

    def setupWidgets(self):
        if self.nested_mode:
            Y = self.margin
            for i, widget in enumerate(self.standing_widgets):
                Y += i * (self.margin+self.widget_height)
                widget.move(self.margin, Y)
        else:
            all_widgets = self.standing_widgets + self.hiding_widgets
            X = self.margin
            Y = self.margin
            x_factor = 0
            y_factor = 0
            if self.expand_policy == WidgetGroupFrame.USE_V_EXPAND:
                y_factor = 1
            else:
                x_factor = 1
            for i, widget in enumerate(all_widgets):
                X += i * (self.margin+self.widget_width) * x_factor
                Y += i * (self.margin + self.widget_height) * y_factor
                widget.move(X, Y)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        cursor_pos = a0.pos()
        direction = 0
        if self.rect_left.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_LEFT
        elif self.rect_right.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_RIGHT
        elif self.rect_top.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_UP
        elif self.rect_buttom.contains(cursor_pos):
            direction = WidgetGroupFrame.EXPAND_DOWN
        else:
            direction = 0
        if direction and direction != self.mouse_at_direction:
            self.createExpandButtons()
            self.showExpandButtons(direction)
        elif direction == 0:
            self.hideExpandButtions()
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
        icon_half_length = 0
        icon_width = 0
        self.button_left = QtWidgets.QPushButton(self)
        self.button_left.setIcon(QtGui.QIcon(''))
        self.button_left.move(0, int(self.height/2 - icon_half_length))
        self.button_right = QtWidgets.QPushButton(self)
        self.button_right.setIcon(QtGui.QIcon(''))
        self.button_right.move(self.width - icon_width, int(self.height/2 - icon_half_length) )
        self.button_top = QtWidgets.QPushButton(self)
        self.button_top.setIcon(QtGui.QIcon(''))
        self.button_top.move(int(self.width/2 - icon_half_length), 0)
        self.button_buttom = QtWidgets.QPushButton(self)
        self.button_buttom.setIcon(QtGui.QIcon(''))
        self.button_buttom.move(int(self.width/2 - icon_half_length), self.height-icon_width)
        self.button_left.clicked.connect(self.on_expand_button_clicked)
        self.button_right.clicked.connect(self.on_expand_button_clicked)
        self.button_top.clicked.connect(self.on_expand_button_clicked)
        self.button_buttom.clicked.connect(self.on_expand_button_clicked)
        self.hideExpandButtons()

    def showExpandButtons(self, direction:int ):
        settings = {
        'left_icon': '',
        'right_icon' : '',
        'top_icon' : '',
        'buttom_icon' : '',}
        map = {
            WidgetGroupFrame.EXPAND_UP:'top_icon',
            WidgetGroupFrame.EXPAND_DOWN: 'buttom_icon',
            WidgetGroupFrame.EXPAND_RIGHT: 'right_icon',
            WidgetGroupFrame.EXPAND_LEFT: 'left_icon',
        }
        settings[map[direction]] += '_highlight'
        self.button_left.setIcon(QtGui.QIcon(''))
        self.button_right.setIcon(QtGui.QIcon(''))
        self.button_top.setIcon(QtGui.QIcon(''))
        self.button_buttom.setIcon(QtGui.QIcon(''))
        button_names = ['button_left', 'button_right', 'button_top', 'button_buttom']
        for name in button_names:
            self.__getattribute__(name).show()

    def hideExpandButtons(self):
        button_names = ['button_left', 'button_right', 'button_top', 'button_buttom']
        for name in button_names:
            self.__getattribute__(name).hide()


class GridPanel(QtWidgets.QWidget):
    USE_V_SCROLL = 11
    USE_H_SCROLL = 12

    def __init__(self):
        super().__init__()
        self.scroll_direction = self.USE_H_SCROLL
        self.grid_model = None
        self.unit_v_size = 0
        self.unit_h_size = 0
        self.margin = 2
        self.unit_spacing = 1
        self.group_spacing = 4


    def makeGroupFrames(self):

    def set_unit_widget_size(self, v_size, h_size):
        # widget.setFixedSize(v_size, h_size)
        self.unit_h_size = h_size
        self.unit_v_size = v_size
        pass

    def rearrange_lane(self):
        pass

    def lay_widgets(self):
        lanes:list[list] = self.grid_model.lanes
        X = self.margin
        Y = self.margin
        for lane in lanes:
            for unit in lane:
                unit.widget.move(X, Y)
                Y += self.unit_v_size + self.spacing
            X += self.unit_h_size + self.spacing
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