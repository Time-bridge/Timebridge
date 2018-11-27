import numpy as np
import random
from card import createCard

def randInt(min, max):
    return random.randint(min, max)

class AI(object):
    def __init__(self):
        super().__init__()
        self.color = np.array(13, dtype=np.int)
        self.number = np.zeros(13, dtype=np.int)
        self.isPlayed = np.array(13, dtype=np.int) #0代表没出过
        self.cardPoint = np.zeros(5)
        self.BIGCardPoints = 0
        self.colorNumber = np.zeros(4)
        self.DiffColorBIGCardPoints = np.zeros(4, dtype=np.int)
        self.DiffColorCardNumber = np.zeros(4, dtype=np.int)
        # 初始化手牌对象

    def init(self, color, number):
        self.color = color
        # 0~12对应2~A
        self.number = number
        self.isPlayed = np.zeros(13, dtype=np.int)
        self.colorNumber = np.zeros(4)
        self.DiffColorBIGCardPoints = np.zeros(4, dtype=np.int)
        self.DiffColorCardNumber = np.zeros(4, dtype=np.int)
        self.statCardInfo()

    def statCardInfo(self):
        # 计算大牌点数（J~A），好的AI会用到
        self.BIGCardPoints = 0
        for i in range(13):
            if self.number[i] > 8:
                self.BIGCardPoints += (self.number[i] - 8)
                self.DiffColorBIGCardPoints[self.color[i]] += (self.number[i] - 8)


    #傻瓜出牌方式
    def AIBid0(self, lastBidNumber, lastBidColor, lastBidPlayer):
        number = self.BIGCardPoints // 7 + 1;
        points = 0
        color = 0
        for i in range (4):
            if self.DiffColorBIGCardPoints[i] > points:
                points = self.DiffColorBIGCardPoints[i];
                color = i;
        if self.checkBidPrinciple(lastBidNumber, lastBidColor, number, color):
            return int(color * 13 + number)
        return 0

    def checkBidPrinciple(self, lastBidNumber, lastBidColor, number, color):
        if number > lastBidNumber: return True
        if (number == lastBidNumber and color > lastBidColor): return True
        return False

    # 某花色手牌数
    def colorCardPoint(self, color):
        return self.cardPoint[color]

    # 顺序出牌法
    def AIPlay(self, lastPlayedNumber, lastplayedColor, order):
        if order == 0:
            for i in range(13):
                if self.isPlayed[i] == 0:
                    self.isPlayed[i] = 1
                    return int(createCard(self.color[i], self.number[i]))

        for i in range(13):
            if (self.color[i] == lastplayedColor) and (self.isPlayed[i] == 0):
                self.isPlayed[i] = 1
                return int(createCard(lastplayedColor, self.number[i]))

        for i in range(13):
            if self.isPlayed[i] == 0:
                self.isPlayed[i] = 1
                return int(createCard(self.color[i], self.number[i]))

    # 检验出牌合法性，待补充
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
    def HunmanPlay(self, thisRoundColor, myColor, myNumber):
        if self.checkDisplayPrinciple(thisRoundColor, myColor, myNumber):
            self.remove(myColor, myNumber)
            return True
        else:
            return False

    def remove(self, myColor, myNumber):
        for i in range(13):
            if (self.color[i] == myColor) and (self.number[i] == myNumber):
                self.isPlayed[i] = 1


    #叫牌2.0
    #开叫
    def firstBid(self, order):
        number = 0
        color = 0
        if (order == 1 or order ==2):
            if randInt(1,2) > 1:
                if self.BIGCardPoints >= 12:
                    #自然开叫
                    number = 1
                    color = 0
            else:
                if self.BIGCardPoints >= 11:
                    #提示首攻
                    for i in range (4):
                        if (self.DiffColorBIGCardPoint[i] >= 6 and self.DiffColorCardNumber[i] >= 4):
                            number = 1
                            color = 4
                            break

        if order == 3:
            pass

        if order ==3:
            pass

        return number, color

if __name__ == '__main__':
    for i in range (10):
        print(randInt(1, 3))