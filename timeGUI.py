#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from enums import State, DateInfo
from controller import Controller
import os


class Poker(QLabel):
    """
    扑克，继承自QLabel，是牌的图形显示
    """
    def __init__(self, parent, number, visible=False, *args, **kwargs):
        """
        :param parent: 父窗口
        :param number: 牌,0~52，52表示牌的背面
        :param visible: 是否可见
        :param args: 传递给QLabel的位置参数
        :param kwargs: 传递给QLabel的关键字参数
        """
        super().__init__(parent, *args, **kwargs)
        self.setPixmap(QPixmap('cards' + os.path.sep + str(number) + '.png'))
        self.resize(57, 87)
        self.setVisible(visible)
        self.x, self.y = 0, 0


class QPlayer(object):
    """
    玩家类，记录玩家手牌应当显示的位置
    """
    def __init__(self, position, beginpointx, beginpointy, playpointx,
                 playpointy):
        self.hand_pokers = []  # 手牌
        self.played_poker = None  # 刚出的牌
        self.bpx = beginpointx  # 手牌位置
        self.bpy = beginpointy
        self.px = playpointx  # 刚出的牌的位置
        self.py = playpointy
        self.interval = 20  # 间隔
        self.position = position

    def update(self, hand_pokers, played_poker):
        """
        更新手牌及打出的牌的显示
        :param hand_pokers: 手牌，Poker组成的list
        :param played_poker: 刚出的牌，Poker
        :return: None
        """
        self.clear()
        self.hand_pokers = hand_pokers
        self.played_poker = played_poker
        self.move()

    def clear(self):
        """将所有牌移除（设为不可见）"""
        for poker in self.hand_pokers:
            poker.setVisible(False)
        self.hand_pokers.clear()
        if self.played_poker:
            self.played_poker.setVisible(False)
            self.played_poker = None

    def move_horizontal(self):
        """使手牌沿水平方向摆放"""
        for i, poker in enumerate(self.hand_pokers):
            poker.move(self.bpx + self.interval * i, self.bpy)
            poker.setVisible(True)

    def move_vertical(self):
        """使手牌沿竖直方向摆放"""
        for i, poker in enumerate(self.hand_pokers):
            poker.move(self.bpx, self.bpy + (self.interval + 15) * i)
            poker.setVisible(True)

    def move(self):
        """将牌摆放到合适的位置"""
        if self.position == 1 or self.position == 3:
            self.move_vertical()
        else:
            self.move_horizontal()
        if self.played_poker:
            self.played_poker.move(self.px, self.py)
            self.played_poker.setVisible(True)


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


class TimeBridgeGUI(QWidget):
    def __init__(self, parent=None, controller=None):
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
        # 桥牌游戏可能使用的全部牌的图像形式，包括52张正面向上的牌与52张背面向上的牌
        self._pokers = [Poker(self, i) for i in range(52)] + \
                       [Poker(self, 52) for _ in range(52)]

        points = [(240, 612, 371.5, 520), (739, 100, 643, 306.5),
                  (240, 4, 371.5, 93), (4, 100, 100, 306.5)] # 玩家手牌放置位置
        self.players = [QPlayer(i, *(points[i])) for i in range(4)]  # 界面中玩家采用逆时针的顺序显示
        ###################################################

        self.resize(800, 700)
        self.setFixedSize(800, 700)
        #self.setStyleSheet("background: black")

        self.controller = Controller() if controller is None else controller
        self.connect_with_controller()

    def connect_with_controller(self):
        """将controller内的view_update_signal连接至两个更新函数"""
        # 信号的连接
        self.controller.view_update_signal.connect(self.update_players)
        self.controller.view_update_signal.connect(self.update)
        self.controller.output_signal.connect(self.pmLabel.setText)

    def get_poker(self, card):
        """
        根据数字形式的牌，找到对应的图像形式的牌
        :param card: 牌, Card类型
        :return:
        """
        # 注意参数和返回值都可能是None
        if card is None:
            return None
        return self._pokers[card]

    def update_players(self):
        """
        更新玩家手牌的显示
        :return:
        """
        for i, player in enumerate(self.players):
            hand_cards, played_card, is_visible = self.controller.get_player_info(i)
            played_poker = self.get_poker(played_card)
            if is_visible:
                hand_pokers = [self.get_poker(card) for card in hand_cards]
            else:
                hand_pokers = [self.get_poker(52 + 13 * i + j) for j in
                               range(len(hand_cards))]
            player.update(hand_pokers, played_poker)

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

        if len(player.hand_pokers) > 0 and (player.bpx <= e.x() <= player.bpx + (len(player.hand_pokers) - 1) * player.interval + 57):
            # 计算选中牌的下标
            clicklength = e.x() - player.bpx
            if clicklength <= player.interval * len(player.hand_pokers):
                card_index = clicklength // player.interval
            else:
                card_index = len(player.hand_pokers) - 1

            # print(card_index)
            self.controller.send(card_index, info)

    def paintEvent(self, e):
        # print('paintEvent')
        qp = QPainter()
        qp.begin(self)
        self.draw_player_area(qp)

        # print(self.controller.state)
        if self.controller.state in (State.Play, State.End):
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
        elif self.controller.state == State.Biding:
            self.draw_bid_update(qp)
            self.draw_bid_area(qp)
            self.draw_bid_text(qp)
        # print('draw end')
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

        # 横线之间间隔48, 竖线之间间隔80
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
        cp = self.controller.current_player_position
        if cp is None:
            return

        # 下面的代码我注释掉了，
        # 在界面显示轮到谁出牌、叫牌是由Controller决定
        # controller有一个信号output_signal，被连接到pmLabel的setText函数
        # pmLabel打算给Controller输出信息用，当然GUI如果有某些信息也可以用它输出，
        # 但轮到谁叫牌、轮到谁出牌，还是由Controller决定
        # self.pmText = '轮到{0}叫牌'.format(cp)
        # self.pmLabel.setText(self.pmText)
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


class MainWindow(QMainWindow):
    close_event = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('时光桥牌')
        self.setWindowIcon(QIcon('time.png'))
        self.controller = Controller()
        widget = TimeBridgeGUI(self, controller=self.controller)
        self.setCentralWidget(widget)
        # self.show()

        # 菜单项
        # TODO: 添加其他的菜单项
        self.bar = self.menuBar()

        self.item = self.bar.addMenu('选项')
        self.new_game = QAction(self, text='新游戏')
        self.item.addAction(self.new_game)

        self.connect_with_controller()

    def connect_with_controller(self):
        """
        将菜单项与controller中的槽函数连接起来
        :return:
        """
        self.new_game.triggered.connect(self.controller.new_game)

    def closeEvent(self, event):
        #是否确认退出
        reply = QMessageBox.question(self, 'Message', "是否确认退出?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    main = MainWindow()
    # main.show()
    ex = WelcomePage()
    ex.btn.clicked.connect(main.show)
    ex.btn.clicked.connect(main.controller.new_game)
    ex.btn.clicked.connect(ex.hide)
    ex.close_signal.connect(ex.close)
    ex.show()
    sys.exit(App.exec_())
