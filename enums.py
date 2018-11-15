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
