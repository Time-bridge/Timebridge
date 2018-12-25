#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enums import Suit
from itertools import chain


def color2str(color):
    return ('♣', '♦', '♥', '♠', 'NT')[color]


class Card(int):
    # suit为花色，是枚举类型，建议仅GUI使用
    color = property(lambda self: self // 13)
    number = property(lambda self: self % 13)
    suit = property(lambda self: Suit(self // 13))
    str_color = property(lambda self: color2str(self // 13))


def card2str(card):
    number, str_color = card.number, card.str_color
    # number2str = {i: str(i+2) for i in range(9)}
    # number2str[9] = 'J'
    # number2str[10] = 'Q'
    # number2str[11] = 'K'
    # number2str[12] = 'A'
    number2str = dict(zip(range(13), chain(map(str, range(2, 11)), 'JQKA')))
    return str_color + number2str[number]


def create_card(color, number):
    return Card(13 * color + number)


# 一副牌，设定成元组是不希望被修改
fifty_two_cards = tuple([Card(i) for i in range(52)])
