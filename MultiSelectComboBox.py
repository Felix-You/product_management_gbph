
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QCursor
import  sys


class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, item_list:list,parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.setModel(QtGui.QStandardItemModel(self))
        self.view().pressed.connect(self.handleItemPressed)
        self.checkedItems = []
        self.parent=parent
        self.view().pressed.connect(self.get_all)
        self.view().pressed.connect(self.getCheckItem)
        self.addItem("全选")
        self.model().item(0).setCheckState(QtCore.Qt.Checked)
        for i in range(len(item_list)):
            #line = QtWidgets.QFrame.HLine
            self.addItem(str(item_list[i]))
            self.model().item(i+1).setCheckState(QtCore.Qt.Checked)
            #if i==4:self.model().item(i).setItemWidget(line)
        self.status = 1

    def hidePopup(self):
        width = self.view().width()
        height = self.view().height()+self.height()
        X = QCursor().pos().x()-self.mapToGlobal(self.geometry().topLeft()).x() +self.geometry().x()
        Y = QCursor().pos().y()-self.mapToGlobal(self.geometry().topLeft()).y()+self.geometry().y()
        '''print('self.cursorX=',self.cursor().pos().x())
        print('GX=',self.mapToGlobal(self.geometry().topLeft()).x(),'GY=',self.mapToGlobal(self.geometry().topLeft()).y())
        print('QX=',QCursor().pos().x(),'QY=',QCursor().pos().y())
        print('Width=',width,'Height=',height,)
        print('X=',X,'Y=',Y)'''
        if 0<X<width and self.height()<Y<height:
        #if self.view().hasMouse() :
            pass
        else:
            QtWidgets.QComboBox.hidePopup(self)

    def handleItemPressed(self, index):                            #这个函数是每次选择项目时判断状态时自动调用的，不用管（自动调用）
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    # def getCheckItem(self):
        # getCheckItem方法可以获得选择的项目列表，自动调用。
        for index in range(1,self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                if item.text() not in self.checkedItems:
                    self.checkedItems.append(item.text())
            else:
                if item.text() in self.checkedItems:
                    self.checkedItems.remove(item.text())
        print("self.checkedItems为：",self.checkedItems)
        #self.lineEdit().setText(','.join(self.checkedItems))
        # return self.checkedItems  #实例化的时候直接调用这个self.checkedItems就能获取到选中的值，不需要调用这个方法，方法会在选择选项的时候自动被调用。

    def get_all(self):  #实现全选功能的函数（自动调用）
        all_item = self.model().item(0)
        for index in range(1,self.count()):       #判断是否是全选的状态，如果不是，全选按钮应该处于未选中的状态
            if self.status ==1:
                if self.model().item(index).checkState() == QtCore.Qt.Unchecked:
                    all_item.setCheckState(QtCore.Qt.Unchecked)
                    self.status = 0
                    break

        if all_item.checkState() == QtCore.Qt.Checked:
            if self.status == 0 :
                for index in range(self.count()):
                    self.model().item(index).setCheckState(QtCore.Qt.Checked)
                    self.status = 1

        elif all_item.checkState() == QtCore.Qt.Unchecked:
            for index in range(self.count()):
                if  self.status == 1 :
                    self.model().item(index).setCheckState(QtCore.Qt.Unchecked)
            self.status = 0


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QMainWindow()
    mainWidget = QtWidgets.QWidget()
    dialog.setCentralWidget(mainWidget)
    ComboBox = CheckableComboBox(['1','2'],mainWidget)
    ComboBox.move(10,10)
    dialog.show()
    sys.exit(app.exec_())
