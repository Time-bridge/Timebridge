import numpy as np

#手牌类
class Card:
    def __init__(self):
        self.color = np.array(13, dtype=np.int)
        self.number = np.zeros(13, dtype=np.int)
        self.isPlayed = np.array(13, dtype=np.int)
        self.cardNumber = np.zeros(5)

    #初始化手牌对象
    def init(self, color, number):
        self.color = color
        self.number = number
        self.isPlayed = np.zeros(13, dtype=np.int)
        self.calculateCardNumber()

    #计算不同花色牌点数
    def calculateCardNumber(self):
        for i in range(13):
            if self.number[i] == 1:
                self.cardNumber[self.color[i]] +=14
            else:
                self.cardNumber[self.color[i]] += self.number[i]

    #某花色手牌数
    def colorCardNumber(self, color):
        return self.cardNumber[color]

    #顺序出牌法
    def AIPlay(self, lastPlayedNumber, lastplayedColor, order):
        if order == 1:
            for i in range(13):
                if self.isPlayed[i] == 0:
                    self.isPlayed[i] == 1
                    return self.number[i], self.color[i]

        for i in range(13):
            if (self.color[i] == lastplayedColor) and ( self.isPlayed[i] == 0 ):
                self.isPlayed[i] == 1
                return self.number[i], lastplayedColor

        for i in range(13):
            if self.isPlayed[i] == 0 :
                self.isPlayed[i] == 1
                return self.number[i], self.color[i]

    #检验出牌合法性，待补充
    def checkDisplayPrinciple(self,thisRoundColor, myColor, myNumber):
        if self.cardNumber[thisRoundColor] == 0: return True
        if myColor != thisRoundColor: return False
        return True

    #人类玩家出牌
    def HunmanPlay(self, thisRoundColor, myColor, myNumber):
        if self.checkDisplayPrinciple(thisRoundColor, myColor, myNumber):
            self.remove( myColor, myNumber)
            return True
        else:
            return False

    def remove(self, myColor, myNumber):
        for i in range(13):
            if self.color[i] == myColor and self.number == myNumber:
                self.isPlayed[i] = 0

if __name__ == '__main__':

    a = 1
