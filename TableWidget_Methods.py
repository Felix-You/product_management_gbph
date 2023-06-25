from Feedback_Info_Main_UI import FeedbackMainWindow
from PyQt5.QtWidgets import *
import pandas as pd1
from numpy import *
from PyQt5.QtWidgets import QComboBox,QMessageBox
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtGui import  QStandardItemModel,QStandardItem
from PyQt5 import QtCore
from PyQt5.QtCore import QDateTime
import ReadWrite1 as RW
import numpy as np
import pandas as pd
from docx import Document
import time
import os
#class tablewidget_methods(QTableWidget):
#    def __init__(self):

def set_tablewidget(table_data, tablewidget:QTableWidget):
    col_count = table_data.shape[1]
    row_count = table_data.shape[0]
    table_header = table_data.horizontalHeader.tolist()
    tablewidget.setColumnCount(col_count)
    tablewidget.setRowCount(row_count)
    tablewidget.setHorizontalHeaderLabels(table_header)
    for i in range(row_count):
#        print('断点1\n', i)
        for j in range(len(table_header)):
#            print('断点2\n', i, j)
            text_edit = QTextEdit(str(table_data.iloc[i, j]))
            tablewidget.setCellWidget(i, j, text_edit)


def get_table_data(tablewidget: QTableWidget):
    row_count = tablewidget.rowCount()
    cols_count = tablewidget.columnCount()
    cols_headers = []
    cols_index = []
    for i in range(cols_count) :
        cols_headers.append(tablewidget.horizontalHeaderItem(i).text())
        cols_index.append(i)
    worker = zip(cols_headers,cols_index)
    col_name_index = dict(worker)#字典{表头名字:列数}
    #print(cols_names)
    table_data = pd.DataFrame(columns= cols_headers, index=range(row_count))

    for i in range(row_count):
        for header in cols_headers:
            try:
                table_data.loc[i, header] = tablewidget.cellWidget(i, col_name_index[header]).toPlainText()
            except:
                try:
                    table_data.loc[i, header] = tablewidget.cellWidget(i, col_name_index[header]).curretText()
                except:
                    table_data.loc[i, header] = tablewidget.item(i, col_name_index[header]).text()
    return table_data






