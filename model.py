#!/usr/bin/python3
# -*- coding: utf-8 -*-

from player import AIPlayer, HumanPlayer
from enums import State
from bid_table import BidTable
from play_table import PlayTable


class Model(object):
    def __init__(self):
        self.players = [HumanPlayer(0), AIPlayer(1), AIPlayer(2),
                        AIPlayer(3)]  # 玩家
        self.current_player_position = None  # 当前应进行叫牌/出牌角色的位置
        self.state = State.Stop  # 游戏状态

        # 叫牌相关的变量
        self.king_color = None  # 将牌
        self.bid_table = BidTable()  # 叫牌表
        self.win_bid_position = None  # 叫牌获胜的玩家
        self.pass_num = 0  # pass数量
        self.last_bid_number = 0
        self.last_bid_color = None
        self.last_bid_player_position = None

        # 出牌相关的变量
        self.trick = None  # 轮数
        self.last_played_number = None  # 上一张出牌点数
        self.last_played_color = None  # 上一张出牌花色
        self.first_played_color = None  # 本轮出的第一张牌的花色
        self.play_order = None  # 出牌顺序，即当前出牌的人是本轮第几个出牌的
        self.win_player_position = None  # 某轮获胜角色
        self.drink_tea_player_position = None  # 喝茶角色位置
        self.trick_history = {}  # 记录本轮出牌结果
        self.play_table = PlayTable()  # 除本轮外,全部出牌记录

    current_player = property(
        lambda self: None if (self.current_player_position is None) else
        self.players[self.current_player_position])

    def reset(self):
        """
        重置所有变量
        :return:None
        """
        for player in self.players:
            player.reset()

        self.current_player_position = None
        self.state = State.Stop

        self.king_color = None
        self.bid_table.reset()
        self.win_bid_position = None
        self.pass_num = 0
        self.last_bid_number = 0
        self.last_bid_color = None
        self.last_bid_player_position = None

        self.trick = None
        self.last_played_number = None
        self.last_played_color = None
        self.first_played_color = None
        self.play_order = None
        self.win_player_position = None
        self.drink_tea_player_position = None
        self.trick_history = {}
        self.play_table.reset()
