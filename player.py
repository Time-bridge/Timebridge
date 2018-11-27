from enums import Position, Color
from AI import AI


# 找队友，player初始化用
def findTeammate(myPosition):
    assert 0 <= myPosition < 4
    return (myPosition + 2) % 4


# 检验叫牌合法性
def checkBidValid(lastBidNumber, lastBidColor, color, number):
    if number > lastBidNumber:
        return True
    if number < lastBidNumber:
        return False
    if color > lastBidColor:
        return True
    return False


checkBidPrinciple = checkBidValid


class Player(object):
    def __init__(self, position):
        super().__init__()
        self.cards = []  # 手牌
        self.colorNum = [0, 0, 0, 0]  # 各花色手牌数量
        self.cardNum = 0  # 手牌总数
        self.drinkTea = False  # 是否喝茶
        self.position = position  # 自己的位置
        self.teammatePosition = findTeammate(position)  # 队友位置
        self.ai = AI()  # 每个玩家都有一个AI。AI只给出出牌建议，并不能决定出哪张牌

    def getCard(self, card):
        self.cards.append(card)
        self.cards.sort()
        self.colorNum[card.color] += 1
        self.cardNum += 1

    def loseCard(self, card):
        self.cards.remove(card)
        self.colorNum[card.color] -= 1
        self.cardNum -= 1
        self.ai.remove(card.color, card.number)  # 更新ai的数据
        return card

    def bid(self, *args, **kwargs):
        pass

    def play(self, *args, **kwargs):
        pass

    def initAI(self):
        # 将手牌信息传递给AI，需要在发牌后调用
        colors = [card.color for card in self.cards]
        numbers = [card.number for card in self.cards]
        self.ai.init(colors, numbers)


class AIPlayer(Player):
    def __init__(self,  position, strategy=0):
        super().__init__(position)
        self.strategy = strategy

    def bidNumber(self, color):
        return self.ai.colorCardPoint(color) // 15 + 1

    def bid(self, lastBidNumber, lastBidColor, lastBidPlayer):
        """
        :param lastBidNumber:
        :param lastBidColor:
        :param lastBidPlayer:
        :return: bidNumber, bidColor
        """
        BidResult = 0
        if self.strategy == 0:
            #如果是对家叫的牌，则不跟他抢, 0表示pass
            if lastBidPlayer == self.teammatePosition:
                return 0
            else:
                for name, color in Color.__members__.items():
                    number = self.bidNumber(color.value)
                    if number > lastBidNumber:
                        return number * 10 + color.value
        return 0

    # 出牌
    def play(self, lastPlayedNumber, lastPlayedColor, order):
        # if self.drinkTea and self.Te
        if self.strategy == 0:
            card = self.ai.AIPlay(lastPlayedNumber, lastPlayedColor, order)
            return self.loseCard(card)


class HumanPlayer(Player):
    def bid(self, *args, **kwargs):
        return int(input('请输入一个数字'))

    def play(self, *args, **kwargs):
        while True:
            idx = input('请输入一个数字')
            if 0 <= idx < len(self.cards):
                break
        card = self.cards[idx]
        self.loseCard(card)


