from enum import Enum
import numpy as np
from utils import Card

class Position(Enum):
    North = 0
    West = 1
    South = 2
    East = 3

class Color(Enum):
    Club = 0
    Diamond = 1
    Heart = 2
    Spade = 3
    NoTrump = 4

# 找队友，player初始化用
def findTeammate(myPosition):
    if myPosition == Position.North.value:
        return Position.South.value
    if myPosition == Position.West.value:
        return Position.East.value
    if myPosition == Position.South.value:
        return Position.North.value
    if myPosition == Position.East.value:
        return Position.West.value

#检验叫牌合法性
def checkBidPrinciple(lastBidNumber, lastBidColor, color, number):
    if number>lastBidNumber: return True
    if number<lastBidNumber: return False
    if color>lastBidColor: return True
    return False


class Player:
    #构造函数
    def __init__(self, position):
        self.colorNumber = 13
        self.position = position
        self.score = 0
        self.existedNumberOfpiers = 0
        self.neededNumberOfpiers = 0
        self.teammatePosition = findTeammate(self.position)
        self.card = Card()
        self.bidResult = np.zeros(2)

    #记录叫牌结果,需要牌局控制程序调用
    def RecordBidResult(self, bidColor, bidNumber, bidPosition):
        """

        :param bidColor:
        :param bidNumber:
        :param bidPosition: 哪个位置叫的
        :return:
        """
        self.bidResult[0] = bidColor
        self.bidResult[1] = bidPosition
        if (bidPosition == self.position) or ( (bidPosition + 2) % 4 == self.position):
            self.neededNumberOfpiers = bidNumber
        else:
            self.neededNumberOfpiers = 13 - bidNumber

    #发牌, color, number需要牌局控制程序给出
    def displayCard(self, color, number):
        """

        :param color:a 13-size tuple
        :param number:a 13-size tuple
        :return:
        """
        self.card.init(color, number)

    #计算分数
    def updateScore(self):
        return
    #叫牌
    def bid(self):
        return
    #出牌
    def play(self):
        return

class Aiplayer(Player):
    def __init__(self,  position, strategy=0):
        Player.__init__(self, position)
        self.strategy = strategy

    def bidNumber(self, color):
        return self.card.colorCardNumber(color)//15 +1;

    def bid(self, lastBidNumber, lastBidColor, lastBidPlayer):
        BidResult = 0
        if self.strategy == 0:
            #如果是对家叫的牌，则不跟他抢, 0表示pass
            if ( lastBidPlayer == self.teammatePosition ):
                return 0, 0
            else:
                for name, color in Color.__members__.items():
                    number = self.bidNumber(color.value)
                    if number > lastBidNumber:
                        return number, color.value
        return 0, 0

    #返回的是
    def play(self, lastPlayedNumber, lastPlayedColor, order):
        if self.strategy == 0:
            return self.card.AIPlay(lastPlayedNumber, lastPlayedColor, order)

    def helpedToPlay(self, thisRoundColor, myColor, myNumber, order):
        """

        :param thisRoundColor:本轮率先出牌的花色
        :param myColor:出牌的颜色
        :param Number:出牌的数字
        :param order:出牌次序
        :return:my
        """
        if order == 1: return 'Legally'
        if self.card.HunmanPlay(thisRoundColor, myColor, myNumber):
            return 'Legally'
        else:
            s = ''
            if thisRoundColor == Color.Club.value: s = 'Club'
            if thisRoundColor == Color.Diamond.value: s = 'Diamond'
            if thisRoundColor == Color.Spade.value: s = 'Spade'
            if thisRoundColor == Color.Heart.value: s = 'Heart'
            return 'You must diaplay a ' + s +' card!'

class HumanPlayer(Player):
    def __init__(self, position):
        Player.__init__(self, position)
        print(type(self.card))

    #叫牌  四个参数均需牌局控制程序给出， 0代表当前还没人叫过牌
    def bid(self, color, number, lastBidNumber=0, lastBidColor=0):
        if checkBidPrinciple(lastBidNumber, lastBidColor, color, number):
            return True
        return False

    # 玩家自己打牌
    def play(self, thisRoundColor, myColor, myNumber, order):
        """

        :param thisRoundColor:本轮率先出牌的花色
        :param myColor:出牌的颜色
        :param Number:出牌的数字
        :param order:出牌次序
        :return:my
        """
        if order == 1: return 'Legally'
        if self.card.HunmanPlay(thisRoundColor, myColor, myNumber):
            return 'Legally'
        else:
            s = ''
            if thisRoundColor == Color.Club.value: s = 'Club'
            if thisRoundColor == Color.Diamond.value: s = 'Diamond'
            if thisRoundColor == Color.Spade.value: s = 'Spade'
            if thisRoundColor == Color.Heart.value: s = 'Heart'
            return 'You must diaplay a ' + s +' card!'

    #帮队友打
    def helpTeammatePlay(self, aiplayer, thisRoundColor, myColor, Number):
        if aiplayer.helpedToPlay(thisRoundColor, myColor, Number):
            return 'Legally'
        else:
            s = ''
            if thisRoundColor == Color.Club.value: s = 'Club'
            if thisRoundColor == Color.Diamond.value: s = 'Diamond'
            if thisRoundColor == Color.Spade.value: s = 'Spade'
            if thisRoundColor == Color.Heart.value: s = 'Heart'
            return 'You must diaplay a ' + s + ' card!'

if __name__ == '__main__':
    color = np.ones(13, dtype=np.int)
    number = np.array([10,2,3,4,5,1,7,6,9,10,11,12,13])
    #player = HumanPlayer(position=2)
    #player.displayCard(color, number)
    #print(player.bid(color=1, number=2, lastBidNumber=1, lastBidColor=5))
    #print(player.play(thisRoundColor=1, myColor=2, myNumber=1, order=1))
    ai = Aiplayer(position = 0, strategy=0)
    ai.displayCard(color, number)
    print(ai.card.number)
    print(ai.card.color)
    #print(ai.bid(lastBidNumber=7, lastBidColor=5, lastBidPlayer=1))
    print(ai.play(lastPlayedNumber=7, lastPlayedColor=1, order=2))
    #print(player.helpTeammatePlay(thisRoundColor=1, myColor=2, myNumber=1, order=1))