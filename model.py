from player import AIPlayer, HumanPlayer
from enums import State
from BidTable import BidTable


class Model(object):
    def __init__(self):
        self.players = [HumanPlayer(0), AIPlayer(1), AIPlayer(2), AIPlayer(3)]
        # self.currentPlayer = None
        self.currentPlayerPosition = None
        self.state = State.Stop
        self.kingColor = None
        self.bidTable = BidTable()
        self.pie = None

    def reset(self):
        """
        重置游戏，重新开始游戏时，可以使用
        :return:
        """
        # self.currentPlayer = None
        self.currentPlayerPosition = None
        self.state = State.Stop
        self.kingColor = None
        self.pie = None
        for player in self.players:
            player.reset()
        self.bidTable.reset()
