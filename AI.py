#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
from card import create_card


class AI(object):
    def __init__(self):
        super().__init__()
        self.color = np.array(13, dtype=np.int)
        self.number = np.zeros(13, dtype=np.int)
        self.isPlayed = np.array(13, dtype=np.int)
        self.cardPoint = np.zeros(5)
        self.colorNumber = np.zeros(4)

    # 重置AI
    def reset(self, color, number):
        self.color = color
        self.number = number
        self.isPlayed = np.zeros(13, dtype=np.int)
        self.colorNumber = np.zeros(4)
        self.cardPoint = np.zeros(5)
        self.calculate_card_point()

    # 计算不同花色牌点数
    def calculate_card_point(self):
        for i in range(13):
            self.cardPoint[self.color[i]] += self.number[i]
            self.colorNumber[self.color[i]] += 1

    # 某花色手牌数
    def color_card_point(self, color):
        return self.cardPoint[color]

    # 顺序出牌法，给出AI推荐出的牌
    def ai_play(self, lastPlayedNumber, lastplayedColor, order, firstPlayedColor):
        if order == 0:
            for i in range(13):
                if self.isPlayed[i] == 0:
                    self.isPlayed[i] = 1
                    return create_card(self.color[i], self.number[i])

        for i in range(13):
            if (self.color[i] == firstPlayedColor) and (self.isPlayed[i] == 0):
                self.isPlayed[i] = 1
                return create_card(firstPlayedColor, self.number[i])

        for i in range(13):
            if self.isPlayed[i] == 0:
                self.isPlayed[i] = 1
                return create_card(self.color[i], self.number[i])

    # 出牌
    def remove(self, myColor, myNumber):
        for i in range(13):
            if (self.color[i] == myColor) and (self.number[i] == myNumber):
                self.isPlayed[i] = 1
