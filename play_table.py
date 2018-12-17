#!/usr/bin/python3
# -*- coding: utf-8 -*-

class PlayTable(object):
    def __init__(self):
        self.history = []

    def add(self, pie):
        """
        :param pie: 字典，包含一轮出牌信息；包含5个键0,1,2,3,'win'，值分别4个玩家的出牌以及本轮胜者
        :return:
        """
        self.history.append(pie)

    def reset(self):
        self.history.clear()
