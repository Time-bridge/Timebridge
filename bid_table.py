#!/usr/bin/python3
# -*- coding: utf-8 -*-
from utils import ReadOnlyIterable, PASS, bid_greater


class BidTable(object):
    def __init__(self):
        super().__init__()
        self.history = []
        self.top = PASS
        self.history_iter = ReadOnlyIterable(self.history)

    def add_bid(self, bid_player, bid_result):
        # 待修改
        """
        :param bid_player: 叫牌的玩家
        :param bid_result: 叫牌结果
        :return: None
        """
        # if bid_result > self.top:
        #     self.top = bid_result
        # self.history[bid_result // 10][bid_result % 10] = bid_player
        if self.check(bid_result):
            self.top = bid_result
        self.history.append((bid_player, bid_result))
        return bid_player, bid_result

    # def check(self, bid_result):
    #     return bid_result.number > self.top.number or (
    #         bid_result.number == self.top.number and
    #         bid_result.number != 0 and bid_result.color > self.top.color)
    def check(self, bid_result):
        """检测"""
        return bid_greater(bid_result, self.top)

    def reset(self):
        self.history.clear()
        self.top = PASS

    def get_bid_result(self, i):
        bid_result = dict(self.history[-4:]).get(i, None)
        if bid_result is None:
            return ''
        if bid_result.number == 0:
            return 'PASS'
        else:
            return ['♣', '♦', '♥', '♠', 'NT'][bid_result.color] + str(bid_result.number)
