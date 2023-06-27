from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import QPoint,QTime,Qt,QRectF,QPointF,QObject
from PyQt5.QtGui import QColor,QPainter,QPolygon,QMouseEvent
import DataView
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class AnalogClock(QWidget):

    def __init__(self,parent = None):
        super(AnalogClock,self).__init__(parent)
        self.time = QtCore.QTimer(self)
        self.time.timeout.connect(self.update)
        self.time.start(1000)
        # self.setWindowTitle('AnalogClock')
        # self.resize(400,400)
        # self.setMinimumSize(105*DataView.DF_Ratio, 105*DataView.DF_Ratio)

    def paintEvent(self,a0: QtGui.QPaintEvent) -> None :

        self.side = min(self.width(),self.height())
        self.painter = QPainter(self)

        self.painter.setRenderHint(QPainter.Antialiasing)

        self.painter.translate(self.width() / 2,self.height() / 2)
        self.painter.scale(self.side / 200.0,self.side / 200.0)

        hourHand = [QPoint(7,8),QPoint(-7,8),QPoint(0,-40)]
        minuteHand = [QPoint(7,8),QPoint(-7,8),QPoint(0,-70)]
        hourColor = QColor(127,0,127)
        minuteColor = QColor(0,127,127,191)
        secondColor = QColor(0,127,12,191)
        time = QTime.currentTime()

        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(hourColor)
        self.painter.save()

        self.painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        self.painter.drawConvexPolygon(QPolygon(hourHand))
        self.painter.restore()

        self.painter.setPen(hourColor)
        for i in range(12) :
            self.painter.drawLine(88,0,96,0)
            self.painter.rotate(30.0)

        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(minuteColor)

        self.painter.save()
        self.painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        self.painter.drawConvexPolygon(QPolygon(minuteHand))
        self.painter.restore()

        # self.painter.setPen(secondColor)
        # self.painter.setBrush(secondColor)
        # font = self.painter.font()
        # font.setBold(True)
        # self.painter.setFont(font)
        #
        # self.painter.drawText(QRectF(QPointF(-88,-14),QPointF(-40,14)),Qt.AlignCenter,str(time.second()))
        # self.painter.restore()

        self.painter.setPen(minuteColor)
        self.painter.save()
        for i in range(60) :
            if i % 5 != 0 :
                self.painter.drawLine(92,0,96,0)
            self.painter.rotate(6.0)
        self.painter.restore()
        self.painter.end()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainwindow = AnalogClock()
    mainwindow.show()
    sys.exit(app.exec_())






