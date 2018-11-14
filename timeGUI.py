#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enum import Enum

class welcomePage(QMainWindow):
    

    close_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):  
        self.setWindowTitle('时光桥牌')
        #设置窗口的图标，引用当前目录下的time.png图片
        self.setWindowIcon(QIcon('time.png'))        
        self.setGeometry(300, 300, 600, 600) 

        self.btn = QToolButton(self)
        self.btn.setText("开始游戏")
        self.btn.resize(100, 60)
        self.btn.move(250, 400)
        self.show()

    def closeEvent(self, event):
        #是否确认退出
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
 
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class TimeBridgeGUI(QWidget):
    def __init__(self, parent=None):
        super(TimeBridgeGUI, self).__init__(parent)
        #坐标指示器
        grid = QGridLayout()
        x = 0
        y = 0
        
        #配合highlight_quest使用
        self.quest_state_0 = 0
        self.quest_state_1 = 0
        self.quest_state_2 = 0

        self.quest_reseived = 0

        #用于调试绘图功能
        self.test_state = 1

        #用于确定paintEvent调用哪一部分绘图函数
        self.paint_stage = 1 #0叫牌，1打牌
        self.paint_flag = 0 #0重绘，1更新
        self.paint_beaker_1 = 0 #参见bid_update
        self.paint_beaker_2 = 0

        self.text = "x: {0},  y: {1}".format(x, y)
        #self.setMouseTracking(True)
        self.label = QLabel(self.text, self)
        grid.addWidget(self.label, 0, 0, Qt.AlignTop)
        self.setLayout(grid)
        
        self.resize(800, 700)
        #self.setStyleSheet("background: black")

    def mousePressEvent(self, e):
        if self.paint_stage == 0:
            x = int((e.x()-200)/80) 
            y = int((e.y()-180)/48)
            text = "x: {0},  y: {1}".format(x, y)
            self.label.setText(text)
            if ((e.x() >= 200 and e.x() <= 600) and (e.y() >=180 and e.y() <= 520) and self.quest_reseived == 1):
                self.quest_state_0 = 10 * y + x
                self.quest_reseived = 0;
        
        if self.paint_stage == 1:
            x = int((e.x()-225)/50) 
            y = int((e.y()-190)/20) 
            text = "x: {0},  y: {1}".format(x, y)
            self.label.setText(text)
        
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        if (self.paint_stage == 0 and self.paint_flag == 0):
            self.draw_player_area(qp)
            self.draw_bid_area(qp)
            self.draw_bid_text(qp)
        elif (self.paint_stage == 0 and self.paint_flag == 1):
            self.draw_bid_update(qp)
            self.draw_bid_text(qp)
        elif (self.paint_stage == 1 and self.paint_flag == 0):
            self.draw_player_area(qp)
            self.draw_play_area(qp)
            self.draw_play_text(qp)
        qp.end()

    def closeEvent(self, event):
        #是否确认退出
        reply = QMessageBox.question(self, 'Message',
            "是否确认退出?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
 
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def draw_player_area(self, qp):
      
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)
        #基础区域
        qp.setBrush(QColor(180, 180, 180))
        qp.drawRect(200, 0, 400, 91)
        qp.drawRect(371.5, 93, 57, 87)
        qp.drawRect(371.5, 520, 57, 87)
        qp.drawRect(200, 609, 400, 91)
        qp.drawRect(0, 150, 91, 400)
        qp.drawRect(709, 150, 91, 400)
        qp.drawRect(100, 306.5, 57, 87)
        qp.drawRect(643, 306.5, 57, 87)
        qp.drawRect(200, 180, 400, 336)

    def draw_bid_area(self, qp):
        #叫牌区域
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(200, 228, 600, 228)
        qp.drawLine(200, 276, 600, 276)
        qp.drawLine(200, 324, 600, 324)
        qp.drawLine(200, 372, 600, 372)
        qp.drawLine(200, 420, 600, 420)
        qp.drawLine(200, 468, 600, 468)
        #qp.drawLine(200, 516, 600, 516)
        qp.drawLine(280, 180, 280, 516)
        qp.drawLine(360, 180, 360, 516)
        qp.drawLine(440, 180, 440, 516)
        qp.drawLine(520, 180, 520, 516)

    def draw_bid_text(self, qp):
        colorList = ['♣', '♦', '♥', '♠', 'NT']
        qp.setPen(QColor(71, 53, 135))
        qp.setFont(QFont('', 20))
        for x in range(0, 5):
            for y in range(1, 7):
                text = '{0} {1}'.format(y, colorList[x])
                qp.drawText(223 + 80 * x, 162 + 48 * y, text)

    def draw_bid_update(self, qp):
        xb = self.paint_beaker_2 % 10
        yb = self.paint_beaker_2 / 10
        qp.setBrush(Qcolor(paint_beaker_1 * 20, 100 + paint_beaker_1 * 10, 230 - paint_beaker_1 * 15))#皮这一下就很开心
        qp.drawRect(bid_map(xb, yb))
        qp.setBrush(Qcolor(200, 200, 200))#把失效区域涂灰
        for x in range(0, 4):
            for y in range(0, 6):
                if (y < yb or (y == yb and x < xb)):
                    qp.drawRect(bid_map(x, y))
    
    def draw_play_area(self, qp):
        qp.setBrush(QColor(130, 130, 130))
        qp.drawRect(200, 180, 400, 340)
        qp.setBrush(QColor(201, 200, 205))
        qp.drawRect(225, 200, 350, 320)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(200, 180, 600, 180)
        qp.drawLine(200, 180, 200, 520)
        qp.drawLine(600, 180, 600, 520)
        qp.drawLine(200, 520, 600, 520)
        for x in range(1, 16):
            qp.drawLine(225, 20 * x + 200, 575, 20 * x + 200)
        for x in range(1, 7):
            qp.drawLine(50 * x + 225, 200, 50 * x + 225, 520)

    def draw_play_text(self, qp):
        playerList = ['N', 'W', 'S', 'E']
        colorList = ['♣', '♦', '♥', '♠', 'NT']
        contract = '契约:{0}由{1}叫出'.format(str(self.paint_beaker_1) + colorList[self.paint_beaker_2], playerList[0])
        qp.drawText(355, 193, contract)
        textList1 = ['轮次', 'N出牌', 'W出牌', 'S出牌', 'E出牌', '获胜方']
        for x in range(0,6):
            qp.drawText(50 * x + 245, 210, textList1[x])
        for y in range(1,13):
            qp.drawText(249.5, 20 * y + 210, str(y))
            qp.drawText(495, 20 * y + 210, '回溯')
        qp.drawText(245, 490, '总胜场')
        qp.drawText(245, 510, '总分')

    def bid_update(self, BidPlayer, BidResult):
        self.paint_beaker_1 = BidPlayer
        self.paint_beaker_2 = BidResult
        self.paint_stage = 0
        self.paint_flag = 1
        self.update()

    def bid_to_play(self, num, color):
        self.paint_stage = 1
        self.paint_flag = 0
        self.paint_beaker_1 = num
        self.paint_beaker_2 = color
        self.update()
        pass

    def bid_map(xb, yb):
    #将叫牌区格位映射到坐标
        return (80 * x + 200, 48 * y + 180, 80, 48)

    def highlight_quest(self, area):
        if area == 0:
            #self.quest_reseived = 1
            return self.quest_state_0
   
    def handle_click(self):
        if not self.isVisible():
            self.show()

    def handle_close(self):
        self.close()

    
        
if __name__ == "__main__":
    App = QApplication(sys.argv)
    ex = welcomePage()
    s = TimeBridgeGUI()
    ex.btn.clicked.connect(s.handle_click)
    ex.btn.clicked.connect(ex.hide)
    ex.close_signal.connect(ex.close)
    ex.show()
    sys.exit(App.exec_())