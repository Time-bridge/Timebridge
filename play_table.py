#!/usr/bin/python3
# -*- coding: utf-8 -*-
from utils import ReadOnlyIterable


class PlayTable(object):
    def __init__(self):
        self.__history = []
        self.history = ReadOnlyIterable(self.__history)

    def add(self, trick):
        """
        :param trick: 字典，包含一轮出牌信息；包含5个键0,1,2,3,'win'，值分别4个玩家的出牌以及本轮胜者
        :return:
        """
        self.__history.append(trick)

    def reset(self):
        self.__history.clear()
