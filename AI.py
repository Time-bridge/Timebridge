import numpy as np
from card import createCard


class AI(object):
    def __init__(self):
        super().__init__()
        self.color = np.array(13, dtype=np.int)
        self.number = np.zeros(13, dtype=np.int)
        self.isPlayed = np.array(13, dtype=np.int)
        self.cardPoint = np.zeros(5)
        self.colorNumber = np.zeros(4)

    # 初始化AI
    def init(self, color, number):
        self.color = color
        self.number = number
        self.isPlayed = np.zeros(13, dtype=np.int)
        self.colorNumber = np.zeros(4)
        self.calculateCardPoint()

    # 计算不同花色牌点数
    def calculateCardPoint(self):
        for i in range(13):
            self.cardPoint[self.color[i]] += self.number[i]
            self.colorNumber[self.color[i]] += 1

    # 某花色手牌数
    def colorCardPoint(self, color):
        return self.cardPoint[color]

    # 顺序出牌法，给出AI推荐出的牌
    def AIPlay(self, lastPlayedNumber, lastplayedColor, order):
        if order == 0:
            for i in range(13):
                if self.isPlayed[i] == 0:
                    self.isPlayed[i] = 1
                    return createCard(self.color[i], self.number[i])

        for i in range(13):
            if (self.color[i] == lastplayedColor) and (self.isPlayed[i] == 0):
                self.isPlayed[i] = 1
                return createCard(lastplayedColor, self.number[i])

        for i in range(13):
            if self.isPlayed[i] == 0:
                self.isPlayed[i] = 1
                return createCard(self.color[i], self.number[i])

    # 出牌
    def remove(self, myColor, myNumber):
        for i in range(13):
            if (self.color[i] == myColor) and (self.number[i] == myNumber):
                self.isPlayed[i] = 1

    # 检验出牌合法性，待补充
    # 未测试，未使用
    def checkDisplayPrinciple(self, order, thisRoundColor, myColor, myNumber):
        if order == 0:
            return True
        if self.colorNumber[thisRoundColor] == 0:
            # 此回合颜色的牌没了，不管出什么都行
            return True
        if myColor != thisRoundColor:
            return False
        return True

    # 人类玩家出牌
    # 未测试，未使用
    def HunmanPlay(self, thisRoundColor, myColor, myNumber):
        if self.checkDisplayPrinciple(thisRoundColor, myColor, myNumber):
            self.remove(myColor, myNumber)
            return True
        else:
            return False


