#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""此模块包含一些桥牌游戏可能用到的枚举值"""
# 实际写程序时，可能不会用到

from enum import Enum, unique


@unique
class Color(Enum):
    """花色"""
    Club = 0  # 梅花
    Diamond = 1  # 方块
    Heart = 2  # 红桃
    Spade = 3  # 黑桃
    NoTrump = 4  # 无将


Suit = Color


@unique
class Position(Enum):
    """位置"""
    North = 0
    West = 1
    South = 2
    East = 3


@unique
class State(Enum):
    """游戏状态"""
    Stop = 'Stop'
    Biding = 'Biding'
    Play = 'Play'
    End = 'End'


@unique
class DateInfo(Enum):
    """GUI会将鼠标点击转化为出牌、叫牌信息传递给controller，此类型用于标识传递信息内容"""
    Bid = 0
    HumanPlay = 1
    AIPlay = 2
