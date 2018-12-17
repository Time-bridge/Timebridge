#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enums import State, DateInfo
from controller import Controller


App = QApplication(sys.argv)


#######################################
class Poker(object):
    # 一次加载全部图片，并保存在字典中
    card_pictures = {i: QPixmap('cards/' + str(i) + '.png') for i in range(53)}

    def __init__(self, window, number):
        self.number = number
        self.L = QLabel(window)
        # self.card = QPixmap('cards/'+str(self.number)+'.png')
        self.L.setPixmap(Poker.card_pictures[number])
        self.L.resize(57, 87)
        self.L.setVisible(True)
        self.x = 0
        self.y = 0

    def cardMove(self, x, y):
        self.x = x
        self.y = y
        self.L.move(self.x, self.y)

    def cardMoveY(y):
        self.y = self.y + y
        self.L.move(self.x, self.y)

    def delete(self):
        self.L.deleteLater()


class Player(object):
    def __init__(self):
        self.cardlist = []   # 牌的图像
        self.numberlist = []  # 牌的数据表示
        self.bpx = 0    # 手牌位置
        self.bpy = 0
        self.px = 0     # 刚出的牌的位置
        self.py = 0
        self.interval = 20  # 间隔
        self.position = None
        self.delcard = None # 刚出的牌，出牌后需要将对应的牌删除
        self.playcardnumber = 0

    def initialize(self, window, numberlist, beginpointx, beginpointy, playpointx, playpointy, position):
        # print('begin initial')
        self.numberlist = numberlist
        self.bpx = beginpointx
        self.bpy = beginpointy
        self.px = playpointx
        self.py = playpointy
        self.interval = 20 # 间隔
        self.position = position
        self.delete()
        for card in self.cardlist:
            card.delete()
        self.cardlist.clear()
        self.delcard = None
        for i in range(0, len(self.numberlist)):
            self.cardlist.append(Poker(window, self.numberlist[i]))

    def move(self):#把牌移动到显示区域
        for i in range(0, len(self.cardlist)):
            self.cardlist[i].cardMove(self.bpx + self.interval * i, self.bpy)

    # def play(self, number): #出牌，返回值为当前出牌的编号，number是牌在cardlist中的序号
    #     # play函数存在的原因在于GUI虽然不用管牌的数据信息，但要维护图像信息
    #     # 在出牌后，要移除这张牌的图像
    #     self.cardlist[number].cardMove(self.px, self.py)
    #     self.delcard = self.cardlist.pop(number)
    #     self.move_()
    #     return self.numberlist.pop(number)
    def play(self, card):
        """
        出牌
        :param card: 所出的牌
        :return: None
        """
        p = self.numberlist.index(card) #先找到该牌的序号
        self.delcard = self.cardlist.pop(p) # 从手牌删除
        self.delcard.cardMove(self.px, self.py) # 移动至出牌区
        self.numberlist.pop(p)
        self.move()
        return card

    def delete(self):
        if self.delcard is not None:
            self.delcard.delete() #将已经打出的牌删除，避免重叠
            self.delcard = None


class AIplayer(object):
    def __init__(self):
        self.cardlist = []#记录玩家要展示的所有牌
        self.numberlist = []#记录玩家所拥有的所有牌的编号
        self.bpx = 0
        self.bpy = 0
        self.px = 0
        self.py = 0
        # self.interval = 20
        self.delcard = None #出牌后需要将对应的牌删除
        # self.playcardnumber = 0
        self.facecards = 0 #此变量记录是否要明牌
        self.AInumber = 0  # AI编号，与位置相同

    def initialize(self, window, numberlist, beginpointx, beginpointy, playpointx, playpointy, AInumber):
        self.numberlist = numberlist
        self.bpx = beginpointx
        self.bpy = beginpointy
        self.px = playpointx
        self.py = playpointy
        self.interval = 20
        self.AInumber = AInumber
        self.delete()
        for card in self.cardlist:
            card.delete()
        self.cardlist.clear()
        self.delcard = None
        for i in range(0, len(self.numberlist)):#AI的牌首先都只对玩家展示背面
            self.cardlist.append(Poker(window, 52))
        # print('initial over')

    def moveHorizontal(self):  # 把牌移动到显示区域, 水平摆放
        # print('moveHorizontal')
        for i in range(0, len(self.cardlist)):
            self.cardlist[i].cardMove(self.bpx + self.interval * i, self.bpy)

    def moveVertical(self):#把牌移动到显示区域，竖直摆放
        # print('moveVertical')
        for i in range(0, len(self.cardlist)):
            self.cardlist[i].cardMove(self.bpx,
                                      self.bpy + (self.interval + 15) * i)

    def move(self):
        if self.AInumber == 1 or self.AInumber == 3:
            self.moveVertical()
        else:
            self.moveHorizontal()

    def play(self, number): #出牌，返回值为当前出牌的编号，AIplayer的number与player的number不同，为牌的编号
        p = self.numberlist.index(number)  # 先找到该牌的序号
        # self.cardlist[p] = poker(window, number)  # 重新赋值为要显示的牌
        # self.cardlist[p].cardMove(self.px, self.py)#将这张牌移动到出牌区
        self.delcard = self.cardlist.pop(p)
        self.delcard.cardMove(self.px, self.py)
        self.numberlist.pop(p)
        self.move()
        return number

    def delete(self):
        if self.delcard is not None:
            self.delcard.delete() #将已经打出的牌删除，避免重叠 出牌之前需要先调用此函数
            self.delcard = None

    def face_cards(self, w): #如果需要明牌，调用此函数
        for i in range(0, len(self.numberlist)):
            temp = self.cardlist.pop()
            temp.delete()
        for i in range(0, len(self.numberlist)):#将扑克牌全部替换为正常模式
            self.cardlist.append(Poker(w, self.numberlist[i]))

        if self.AInumber == 1 or self.AInumber == 3:
            self.moveVertical()
        elif self.AInumber == 2:
            self.moveHorizontal()


#######################################
class WelcomePage(QMainWindow):
    close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('时光桥牌')
        # 设置窗口的图标，引用当前目录下的time.png图片
        self.setWindowIcon(QIcon('time.png'))
        self.setGeometry(300, 300, 600, 600)

        self.btn = QToolButton(self)
        self.btn.setText("开始游戏")
        self.btn.resize(100, 60)
        self.btn.move(250, 400)
        self.show()

    def closeEvent(self, event):
        #是否确认退出
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class TimeBridgeGUI(QMainWindow):
    def __init__(self, parent=None):
        super(TimeBridgeGUI, self).__init__(parent)
        #坐标指示器
        grid = QGridLayout()
        x = 1
        y = 0
        grid.setHorizontalSpacing(1)
        grid.setVerticalSpacing(1)
        grid.setContentsMargins(10, 10, 700, 600)
        self.cText = "x: {0},  y: {1}".format(x, y)
        self.pmText = "提示信息"
        #self.setMouseTracking(True)
        self.cLabel = QLabel(self.cText, self)
        self.pmLabel = QLabel(self.pmText, self)
        grid.addWidget(self.cLabel, 0, 0, Qt.AlignTop)
        grid.addWidget(self.pmLabel, 1, 0, Qt.AlignTop)
        
        #grid_2 = QGridLayout()
        #grid_2.setContentsMargins(60, 90, 60, 90)
        self.text0 = "N"
        self.text1 = "W"
        self.text3 = "E"
        self.text2 = "S"
        self.label0 = QLabel(self.text0, self)
        self.label1 = QLabel(self.text1, self)
        self.label3 = QLabel(self.text3, self)
        self.label2 = QLabel(self.text2, self)
        self.label0.move(350, 120)
        self.label1.move(80, 340)
        self.label3.move(640, 340)
        self.label2.move(350, 580)
        
        self.setLayout(grid)

        ##############################################
        #player
        self.players = [Player(), AIplayer(), AIplayer(), AIplayer()]#界面中玩家采用逆时针的顺序显示
        ###################################################

        self.resize(800, 700)
        self.setFixedSize(800, 700)
        #self.setStyleSheet("background: black")

        ############################################
        # 具体菜单项设置可修改
        # TODO: 添加菜单项
        self.bar = self.menuBar()

        self.item = self.bar.addMenu('选项')
        self.new_game = QAction(self, text='新游戏')
        self.item.addAction(self.new_game)
        ######################################

        self.controller = Controller()
        self.connect_with_controller()

    def connect_with_controller(self):
        # 信号的连接
        self.controller.deal_end_signal.connect(self.initializePlayer)
        # self.controller.biding_signal.connect(self.update)
        self.controller.bid_signal.connect(self.update)
        self.controller.bid_end_signal.connect(self.update)
        self.controller.play_begin_signal.connect(self.delete)
        self.controller.play_signal.connect(self.play)

        # 菜单项的连接
        self.new_game.triggered.connect(self.controller.new_game)

    def delete(self):
        # 删除刚刚打出的牌
        for player in self.players:
            player.delete()

    def initializePlayer(self, numberlists):
        # print(numberlists)
        points = [(240, 612, 371.5, 520), (739, 100, 643, 306.5),
                  (240, 4, 371.5, 93), (4, 100, 100, 306.5)]

        for i, numberlist in enumerate(numberlists):
            self.players[i].initialize(self, numberlist, *(points[i]), i)
            self.players[i].move()

        self.AIplayer1facecard()
        self.AIplayer2facecard()
        self.AIplayer3facecard()
        # print('getPlayer over')
        return

    def play(self, playerPosition, card):
        self.players[playerPosition].play(card)

    def faceCard(self, i):
        self.players[i].face_cards(self)

    def AIplayer1facecard(self):#AI玩家1翻牌
        self.players[1].face_cards(self)

    def AIplayer2facecard(self):#AI玩家2翻牌
        self.players[2].face_cards(self)

    def AIplayer3facecard(self):#AI玩家3翻牌
        self.players[3].face_cards(self)
    ##################################################################################

    def mousePressEvent(self, e):
        # TODO: 在之后的版本中，下面的print函数可删除
        print(e.x(), e.y())

        if 200 <= e.x() <= 600 and 180 <= e.y() <= 520:
            # 叫牌区域
            x = int((e.x() - 200) / 80)
            y = int((e.y() - 180) / 48)
            text = "x: {0},  y: {1}".format(x, y)
            self.cLabel.setText(text)
            if 0 <= x < 5 and 0 <= y < 7:
                bid_result = 10 * (y + 1) + x
                self.controller.send(bid_result, DateInfo.Bid)

        # 手牌区
        if self.players[0].bpy <= e.y() <= self.players[0].bpy + 87:
            # 人类手牌区
            player = self.players[0]
            info = DateInfo.HumanPlay
        elif self.players[2].bpy <= e.y() <= self.players[2].bpy + 87:
            # AI2 手牌区
            player = self.players[2]
            info = DateInfo.AIPlay
        else:
            return

        if len(player.cardlist) > 0 and (player.bpx <= e.x() <= player.bpx + (len(player.cardlist) - 1) * player.interval + 57):
            # 计算选中牌的下标
            clicklength = e.x() - player.bpx
            if clicklength <= player.interval * len(player.cardlist):
                card_index = clicklength // player.interval
            else:
                card_index = len(player.cardlist) - 1

            # print(card_index)
            self.controller.send(card_index, info)

    def paintEvent(self, e):
        print('paintEvent')
        qp = QPainter()
        qp.begin(self)
        self.draw_player_area(qp)

        # if self.controller.state in (State.Play, State.PlayEnd):
        print(self.controller.state)
        if self.controller.state == State.Play:
            self.draw_play_area(qp)
            self.draw_play_text(qp)
            # print('play draw')
        # elif self.controller.state == State.BidEnd:
        #     #目前存在Bug
        #     #有时候这里的代码没被全部调用
        #     self.label0.deleteLater()
        #     self.label1.deleteLater()
        #     self.label3.deleteLater()
        #     self.label2.deleteLater()
        # elif self.controller.state in (State.BidBegin, State.Biding):
        elif self.controller.state == State.Biding:
            self.draw_bid_update(qp)
            self.draw_bid_area(qp)
            self.draw_bid_text(qp)
            print('biding draw')
        print('draw end')
        qp.end()
        return

    def draw_player_area(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)
        #基础区域
        qp.setBrush(QColor(180, 180, 180))
        qp.drawRect(240, 4, 297, 87)
        qp.drawRect(240, 609, 297, 87)
        qp.drawRect(4, 100, 57, 507)
        qp.drawRect(739, 100, 57, 507)

        # qp.drawRect(200, 180, 400, 336)


    def draw_bid_area(self, qp):
        #叫牌区域
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)

        # 横线之间间隔48
        # 竖线之间间隔80
        delta_x, delta_y = 80, 48
        # 画横线
        for i in range(0, 8):
            qp.drawLine(200, 180 + i * delta_y, 600, 180 + i * delta_y)
        # 画竖线
        for i in range(0, 6):
            qp.drawLine(200 + i * delta_x, 180, 200 + i * delta_x, 516)

    def draw_bid_text(self, qp):
        colorList = ['♣', '♦', '♥', '♠', 'NT']
        qp.setPen(QColor(71, 53, 135))
        qp.setFont(QFont('', 20))
        for x in range(0, 5):
            for y in range(1, 8):
                text = '{0} {1}'.format(y, colorList[x])
                qp.drawText(223 + 80 * x, 162 + 48 * y, text)
        #左上角提示区更新
        cp = self.controller._model.current_player_position
        if cp is None:
            return
        self.pmText = '轮到{0}叫牌'.format(cp)
        self.pmLabel.setText(self.pmText)
        #time.sleep(1)
        #玩家叫牌提示信息更新

        text = self.controller.get_bid_result(cp)
        if cp == 0:
            self.label0.setText(text)
        elif cp == 1:
            self.label1.setText(text)
        elif cp == 2:
            self.label2.setText(text)
        elif cp == 3:
            self.label3.setText(text)

    def bid_map(self, x, y):
        # 将叫牌区格位映射到坐标
        return 80 * x + 200, 48 * y + 180, 80, 48

    def draw_bid_update(self, qp):
        if not self.controller.max_bid:
            return
        xb = self.controller.max_bid % 10
        yb = self.controller.max_bid // 10 - 1
        if self.controller.win_bid_position is None:
            return
        #叫牌表更新
        qp.setBrush(QColor(self.controller.win_bid_position * 20, 100 + self.controller.win_bid_position * 10, 230 - self.controller.win_bid_position * 15))#皮这一下就很开心
        qp.drawRect(*self.bid_map(xb, yb))
        qp.setBrush(QColor(200, 200, 200))#把失效区域涂灰
        for y in range(0, 7):
            for x in range(0, 5):
                if y < yb or (y == yb and x < xb):
                    qp.drawRect(*self.bid_map(x, y))
                else:
                    return

    def draw_play_area(self, qp):
        qp.setBrush(QColor(180, 180, 180))
        qp.drawRect(371.5, 93, 57, 87)
        qp.drawRect(371.5, 520, 57, 87)
        qp.drawRect(100, 306.5, 57, 87)
        qp.drawRect(643, 306.5, 57, 87)
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
        player_list = ['N', 'W', 'S', 'E']
        color_list = ['♣', '♦', '♥', '♠', 'NT']
        if self.controller.win_bid_position is not None:
            contract = '契约:{0}由{1}叫出'.format(str(self.controller.max_bid // 10) + color_list[self.controller.max_bid % 10], player_list[self.controller.win_bid_position])
        qp.drawText(355, 193, contract)
        text_list = ['轮次', 'N出牌', 'W出牌', 'S出牌', 'E出牌', '获胜方']
        for x in range(0, 6):
            qp.drawText(50 * x + 230, 215, text_list[x])
        for y in range(1, 13):
            qp.drawText(246.5, 20 * y + 215, str(y))
            qp.drawText(535, 20 * y + 215, '回溯')
        qp.drawText(232, 495, '总胜场')
        qp.drawText(237, 515, '总分')

    def handle_click(self):
        if not self.isVisible():
            self.show()

    def handle_close(self):
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "是否确认退出?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


# if __name__ == "__main__":
ex = WelcomePage()
s = TimeBridgeGUI()
ex.btn.clicked.connect(s.handle_click)
ex.btn.clicked.connect(s.controller.new_game)
ex.btn.clicked.connect(ex.hide)
ex.close_signal.connect(ex.close)
ex.show()
sys.exit(App.exec_())
