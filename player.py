#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enums import Color
from utils import ReadOnlyIterable, PASS, BidResult
# from collections import namedtuple
from AI import AI


# 找队友，player初始化用
def find_teammate(my_position):
    assert 0 <= my_position < 4
    return (my_position + 2) % 4


# BidResult = namedtuple('BidResult', ['number', 'color'])
# PASS = BidResult(0, None)
# MAX_BID_RESULT = BidResult(7, 4)
#
#
# def bid_greater(b1, b2):
#     return b1.number > b2.number or (
#         b1.number == b2.number and
#         b1.number != 0 and b1.color > b2.color)


class Player(object):
    # class CardIterator(Iterable):
    #     """
    #     用于访问玩家手牌的只读接口
    #     """
    #     def __init__(self, player):
    #         self.__cards = player.cards
    #
    #     def __iter__(self):
    #         return self.__cards.__iter__()
    #
    #     def __len__(self):
    #         return self.__cards.__len__()
    #
    #     def __getitem__(self, item):
    #         return self.__cards.__getitem__(item)

    def __init__(self, position):
        super().__init__()
        self.cards = []  # 手牌
        self.color_num = [0, 0, 0, 0]  # 各花色手牌数量
        self.card_num = 0  # 手牌总数
        self.drink_tea = False  # 是否喝茶
        self.position = position  # 自己的位置
        self.teammate_position = find_teammate(position)  # 队友位置
        self.ai = AI()  # 每个玩家都有一个AI。AI只给出出牌建议，并不能决定出哪张牌
        # self.cards_iter = Player.CardIterator(self)  # 供UI访问的手牌的只读接口
        self.cards_iter = ReadOnlyIterable(self.cards)  # 供UI访问的手牌的只读接口

    def get_card(self, card):
        self.cards.append(card)
        self.cards.sort()
        self.color_num[card.color] += 1
        self.card_num += 1

    def lose_card(self, card):
        self.cards.remove(card)
        self.color_num[card.color] -= 1
        self.card_num -= 1
        self.ai.remove(card.color, card.number)  # 更新ai的数据
        return card

    def lose_card_by_index(self, card_index):
        assert 0 <= card_index < len(self.cards)
        return self.lose_card(self.cards[card_index])

    def bid(self, *args, **kwargs):
        pass

    def play(self, *args, **kwargs):
        pass

    def init_AI(self):
        # 将手牌信息传递给AI，需要在发牌后调用
        colors = [card.color for card in self.cards]
        numbers = [card.number for card in self.cards]
        self.ai.reset(colors, numbers)

    def reset(self):
        """
        重置数据成员，重新开始游戏时可以使用
        :return: None
        """
        self.cards.clear()  # 手牌
        self.color_num = [0, 0, 0, 0]  # 各花色手牌数量
        self.card_num = 0  # 手牌总数
        self.drink_tea = False  # 是否喝茶

    def get_candidates(self, first_played_color):
        return dict(filter(lambda x: (x[-1].color == first_played_color) or (
            first_played_color is None), enumerate(self.cards)))


class AIPlayer(Player):
    def __init__(self,  position, strategy=0):
        super().__init__(position)
        self.strategy = strategy
        self.controlled_by_human = False

    def reset(self):
        super().reset()
        self.controlled_by_human = False

    def bid_number(self, color):
        return int(self.ai.color_card_point(color) // 15 + 1)

    def bid(self, last_bid_number, last_bid_color, last_bid_player_position):
        """
        :param last_bid_number:
        :param last_bid_color:
        :param last_bid_player_position:
        :return: bidNumber, bidColor
        """
        if self.strategy == 0:
            # 如果是对家叫的牌，则不跟他抢, 0表示pass
            if last_bid_player_position is None:
                # return BidResult(0, color=None)
                PASS
            if last_bid_player_position == self.teammate_position:
                # return BidResult(0, color=None)
                PASS
            else:
                for name, color in Color.__members__.items():
                    number = self.bid_number(color.value)
                    if number > last_bid_number:
                        # return int(number * 10 + color.value)
                        return BidResult(number, color.value)
        # return BidResult(0, color=None)
        return PASS

    # 出牌
    def play(self, last_played_number, last_played_color, order, first_played_color):
        if self.strategy == 0:
            card = self.ai.ai_play(last_played_number, last_played_color, order, first_played_color)
            return self.lose_card(card)


class HumanPlayer(Player):
    def __init__(self, position):
        super().__init__(position)
        self.controlled_by_human = True

    def reset(self):
        # 尽管self.controlledByHuman不会变成False，但以防万一，我还是重写reset函数吧
        super().reset()
        self.controlled_by_human = True
