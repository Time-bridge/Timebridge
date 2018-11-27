from model import Model
from card import fiftyTwoCards
import random
from collections import Iterator
import time
import threading
from enums import State
from player import HumanPlayer


class Pipe(Iterator):
    # 个人想法，HumanPlayer的出牌结果来自于真实用户点击
    # 但真实用户点击是通过GUI，controller是无法预知用户何时会点击
    # 虽然轮询也能使controller获取用户输入，但我认为还是多线程好一些
    # controller所在线程可被设置为后台线程，GUI所在线程为非后台线程
    # 在controller需要获取用户输入时，线程暂停
    # 直至用户在GUI点击，触发相应回调函数，唤醒controller所在线程，将数据传递过来
    """管道
     用于让一个线程给另一个数据传递数据
    """
    def __init__(self):
        self.data = None
        self.available = False
        self.event = threading.Event()
        self.event.clear()

    def __iter__(self):
        return self

    def reset(self):
        self.data = None
        self.available = False

    def __next__(self):
        while not self.available:
            time.sleep(0.001)
            self.event.wait()
        ret = self.data
        self.reset()
        return ret

    def send(self, data):
        self.data = data
        self.available = True
        self.event.set()


class Controller(object):
    def __init__(self, model=None):
        if model is None:
            self.model = Model()
        else:
            self.model = model
        self.pipe = Pipe()

    def deal(self, startPlayerPosition=None):
        """
        发牌
        :param startPlayerPosition: 初始发牌玩家位置
        :return: None
        """
        cards = list(fiftyTwoCards)
        random.shuffle(cards)
        if isinstance(startPlayerPosition,
                      int) and 0 <= startPlayerPosition < 4:
            self.model.currentPlayerPosition = startPlayerPosition
        else:
            self.model.currentPlayerPosition = random.randint(0, 3)
        for card in cards:
            self.model.players[self.model.currentPlayerPosition].getCard(card)
            self.model.currentPlayerPosition = (self.model.currentPlayerPosition + 1) % 4
        for player in self.model.players:
            player.initAI()

    def bid(self, startPlayerPosition=None):
        """
        叫牌
        :param startPlayerPosition: 初始叫牌玩家位置
        :return: 庄家位置
        """
        # TODO: 增加叫牌合法性检验
        # TODO: 增加最大叫牌结果(7NT)检验

        # 此函数会检查用户叫牌结果，不合法的叫牌结果会被当做pass
        # 因此最好在GUI回调函数里对用户叫牌点击做出检查
        if isinstance(startPlayerPosition,
                      int) and 0 <= startPlayerPosition < 4:
            self.model.currentPlayerPosition = startPlayerPosition
        else:
            self.model.currentPlayerPosition = random.randint(0, 3)
        self.model.kingColor = None

        passNum = 0
        lastBidNumber, lastBidColor, lastBidPlayerPosition = None, None, None
        winPlayer = None
        while True:
            if self.model.players[self.model.currentPlayerPosition].controlledByHuman:
                # bidResult = next(self.pipe)
                bidResult = self.model.players[self.model.currentPlayerPosition].bid(lastBidNumber, lastBidColor, lastBidPlayerPosition)
            else:
                bidResult = self.model.players[self.model.currentPlayerPosition].bid(lastBidNumber, lastBidColor, lastBidPlayerPosition)

            if not self.model.bidTable.check(bidResult):
                # 不合法的叫牌被转换成pass
                bidResult = 0

            if bidResult == 0:
                passNum += 1
            else:
                self.model.bidTable.add_bid(self.model.currentPlayerPosition, bidResult)
                passNum = 0
                lastBidNumber, lastBidColor, lastBidPlayerPosition = bidResult//10, bidResult % 10, self.model.currentPlayerPosition
                winPlayer = self.model.currentPlayerPosition

            print(self.model.currentPlayerPosition)
            print('bidResult', bidResult)

            if (winPlayer is None) and passNum == 4:
                break
            if (winPlayer is not None) and passNum == 3:
                break
            if self.model.bidTable.Top == 74:
                # 7无将
                break
            self.model.currentPlayerPosition = (self.model.currentPlayerPosition + 1) % 4
            # GameGUI.bid_update(BidPlayer, BidResult)

        if winPlayer is None:
            return None

        self.model.kingColor = lastBidColor
        return winPlayer

    def playPie(self, pie, startPlayerPosition):
        # TODO: 出牌合法性验证，假定由上层回调函数验证
        if pie == 0:
            drinkTeaPlayerPosition = (startPlayerPosition + 1) % 4
        lastPlayedNumber, lastPlayedColor = None, None
        history = []
        for i in range(4):
            if pie == 0 and self.model.currentPlayerPosition == drinkTeaPlayerPosition:
                self.model.players[self.model.currentPlayerPosition].drinkTea = True
                teammatePosition = self.model.players[self.model.currentPlayerPosition].teammatePosition
                teammate = self.model.players[teammatePosition]
                if isinstance(self.model.players[self.model.currentPlayerPosition], HumanPlayer) or isinstance(teammate, HumanPlayer):
                    teammate.controlledByHuman = True
                    self.model.players[self.model.currentPlayerPosition].controlledByHuman = True
            if self.model.players[self.model.currentPlayerPosition].controlledByHuman:
                # idx = next(pipe)
                card = self.model.players[self.model.currentPlayerPosition].play(lastPlayedNumber, lastPlayedColor, i)
            else:
                card = self.model.players[self.model.currentPlayerPosition].play(lastPlayedNumber, lastPlayedColor, i)
            if card.color == self.model.kingColor:
                v = 200 + card
            elif i == 0:
                v = 100 + card
            history.append((self.model.currentPlayerPosition, v))

            self.model.currentPlayerPosition = (self.model.currentPlayerPosition + 1) % 4
        history.sort(key=lambda x: x[-1])
        return history[-1][0]

    def play(self, startPlayerPosition):
        """
        出牌
        :param startPlayerPosition:
        :return:
        """
        assert isinstance(startPlayerPosition,
                          int) and 0 <= startPlayerPosition < 4
        self.model.currentPlayerPosition = startPlayerPosition
        self.model.pie = 0

        # for pie in range(13):
        while self.model.pie < 13:
            winPlayerPosition = self.playPie(self.model.pie, startPlayerPosition)
            self.model.pie += 1
            startPlayerPosition = winPlayerPosition
        return

    def reset(self):
        self.model.reset()
        # self.pipe = Pipe()   # 也许这个会有效
        self.pipe.reset()

    def run(self):
        self.reset()
        self.model.state = State.Begin
        self.deal()
        self.model.state = State.Bid
        winBidPosition = self.bid()
        if winBidPosition is None:
            raise TypeError('all players pass!')
        self.model.state = State.Play
        self.play((winBidPosition + 1) % 4)
        self.calculate()
        self.model.state = State.Stop

    def calculate(self):
        pass


if __name__ == '__main__':
    controller = Controller()
    controller.run()
