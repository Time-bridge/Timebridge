#!/usr/bin/python3
# -*- coding: utf-8 -*-


class BidTable(object):
    def __init__(self):
        super().__init__()
        self.history = []
        self.top = 0

    def add_bid(self, bid_player, bid_result):
        # 待修改
        """
        :param bid_player: 叫牌的玩家
        :param bid_result: 叫牌结果
        :return: None
        """
        if bid_result > self.top:
            self.top = bid_result
        # self.history[bid_result // 10][bid_result % 10] = bid_player
        self.history.append((bid_player, bid_result))
        return bid_result // 10, bid_result % 10, bid_player

    def check(self, bid_result):
        return bid_result > self.top

    def reset(self):
        # self.history = [[None, None, None, None, None] for _ in range(8)]
        self.history.clear()
        self.top = 0

    def get_bid_result(self, i):
        bid_result = dict(self.history[-4:]).get(i, None)
        if bid_result is None:
            return ''
        else:
            return ['♣', '♦', '♥', '♠', 'NT'][bid_result % 10] + str(bid_result // 10)
