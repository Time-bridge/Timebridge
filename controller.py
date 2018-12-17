#!/usr/bin/python3
# -*- coding: utf-8 -*-

from model import Model
from card import fifty_two_cards, Card, card2str
from enums import State, DateInfo
from player import HumanPlayer
from PyQt5.QtCore import QObject, pyqtSignal
from queue import Queue
import threading
import random
import time


# class Pipe(Iterator):
#     # 废弃，功能已经转移到controller中
#     # 个人想法，HumanPlayer的出牌结果来自于真实用户点击
#     # 但真实用户点击是通过GUI，controller是无法预知用户何时会点击
#     # 虽然轮询也能使controll er获取用户输入，但我认为还是多线程好一些
#     # controller所在线程可被设置为后台线程，GUI所在线程为非后台线程
#     # 在controller需要获取用户输入时，线程暂停
#     # 直至用户在GUI点击，触发相应回调函数，唤醒controller所在线程，将数据传递过来
#     """管道
#      用于让一个线程给另一个数据传递数据
#     """
#     def __init__(self):
#         self.data = None
#         self.available = False
#         self.event = threading.Event()
#         self.event.clear()
#
#     def __iter__(self):
#         return self
#
#     def reset(self):
#         self.data = None
#         self.available = False
#         self.event.clear()
#
#     def __next__(self):
#         if not self.available:
#             self.event.wait()
#         ret = self.data
#         self.reset()
#         return ret
#
#     def send(self, data):
#         self.data = data
#         self.available = True
#         self.event.set()
def wrapper(fun):
    """装饰器，仅用于帮助分析函数调用时所在线程及运行时间，在最终版中应移去"""
    def inner(*args, **kwargs):
        t1 = time.time()
        res = fun(*args, **kwargs)
        t2 = time.time()
        print(threading.current_thread().name, fun.__name__, 'take %s seconds' % (t2 - t1))
        return res
    return inner


class GameAction(object):
    """游戏事件，并非指图形界面的鼠标点击之类的事件，而是后台线程中的事件。
    例如，游戏中，游戏进入新的阶段产生的事件；重新开始游戏的事件等。
    在事件中封装事件相关信息，包括针对事件进行处理的函数"""
    def __init__(self, name='', target=None, *args, **kwargs):
        """
        :param name:
        :param target: 处理事件的函数
        :param args: target的位置参数
        :param kwargs: target的关键字参数
        """
        self.name = name
        self.func = target
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        """
        执行事件回调函数
        :return: 返回self.func的返回值
        """
        if (self.func is not None) and callable(self.func):
            return self.func(*self.args, **self.kwargs)


class Controller(QObject):
    """
    Controller主要包括后台线程和供UI调用的函数，内部实现了桥牌游戏的全部逻辑。
    后台线程实现借鉴了状态机思想（不过似乎并不是标准的状态机），其中状态是model.state，
    后台线程可能处于三种稳定状态Stop，Biding，Play（稳定是指这三种状态可长时间保持，在这三个状态下，后台线程可能阻塞）。
    在不同状态下，后台线程产生不同行为；在相同状态下，后台线程产生同样的行为。
    后台线程同时使用了事件机制，不同状态间的转换采用事件实现
    """
    # 引入事件，主要是考虑到游戏进行到新的阶段（比如叫牌结束），
    # 以及UI鼠标点击事件（如点击“新游戏”按钮）都能导致游戏状态及model中数据的改变，
    # 且两种改变来自两个线程。
    # 我希望能将两种“改变”同等对待，采样同样的方法处理。不论事件来自何处，都是在后台线程处理
    # 只有后台线程能够改变model中的数据

    # __init__函数之前的，都是为UI提供的接口
    # 信号
    deal_end_signal = pyqtSignal(list)
    bid_signal = pyqtSignal()
    bid_end_signal = pyqtSignal()
    play_begin_signal = pyqtSignal()
    play_signal = pyqtSignal(int, Card)
    play_end_signal = pyqtSignal()

    state = property(lambda self: self._model.state)
    max_bid = property(lambda self: self._model.bid_table.top)
    win_bid_position = property(lambda self: self._model.win_bid_position)
    king_color = property(lambda self: self._model.king_color)

    def send(self, data=None, info=None):
        """供GUI调用，用于给controller发送叫牌、出牌结果。"""
        if info == DateInfo.Bid:
            # 来自GUI叫牌区的用户点击（叫牌结果）
            if self._model.state == State.Biding and (
                        self._model.current_player is not None) and \
                    self._model.current_player.controlled_by_human and (
                        data is not None):
                # and (data == 0 or self.check_bid_valid(data)):
                if self.check_bid_valid(data):
                    self._received_data = data
                else:
                    self._received_data = 0
                self._thread_event.set()
        elif info == DateInfo.HumanPlay:
            # 来自GUI人类玩家出牌
            if self._model.state == State.Play and\
                self._model.current_player_position == 0 and \
                    (data is not None):
                # 此时接收的data是牌的序号
                card = self._model.current_player.cards[data]
                # 出牌合法性检查
                if self.check_play_valid(card):
                    self._received_data = data
                    self._thread_event.set()
        elif info == DateInfo.AIPlay:
            # GUI队友AI出牌
            if self._model.state == State.Play and \
                    self._model.current_player_position == 2 and \
                    self._model.current_player.controlled_by_human and \
                    (data is not None):
                # 此时接收的data是牌的序号
                card = self._model.current_player.cards[data]
                # 出牌合法性检查
                if self.check_play_valid(card):
                    self._received_data = data
                    self._thread_event.set()
        elif info is None:
            # 仅用于唤醒后台线程
            self._received_data = None
            self._thread_event.set()

    def get_bid_result(self, i):
        """
        :param i:玩家位置
        :return: 第i名玩家的叫牌结果（字符串形式）
        """
        return self._model.bid_table.get_bid_result(i) if self._model.state == State.Biding else ''

    def get_cards_iter(self, i):
        # 暂未使用
        """
        :param i: 玩家序号（位置）
        :return: 第i个玩家的手牌的迭代器，可通过调用len获取手牌数，for循环进行迭代，通过下标读取元素
        """
        return self._model.players[i].cards_iterator

    def new_game(self):
        """
        UI“新游戏”按钮的槽函数
        :return:
        """
        print('new game', threading.current_thread().name)
        self._action_queue.put_nowait(self.begin_game_action)
        self.notify()

    def __init__(self, model=None):
        super().__init__()
        if model is None:
            self._model = Model()
        else:
            self._model = model

        # 状态转移采用事件机制，Queue存储了未处理的事件
        self.on_state_functions = {}
        self._action_queue = Queue()

        # 线程相关
        self._thread = threading.Thread(target=self.run)
        self._thread.setDaemon(True)
        self._received_data = None
        self._thread_event = threading.Event()  # 用于控制线程同步，同时也是接收到数据的标志
        self._thread_event.clear()
        self.notify = lambda: self.send()
        self._thread.start()

        # 预定义的GameAction
        self.begin_game_action = GameAction('begin game action', target=self.begin_game)
        self.bid_end_action = GameAction('bid end action', target=self.bid_end)
        self.trick_begin_action = GameAction('trick begin action', target=self.trick_begin)
        self.trick_end_action = GameAction('trick end action', target=self.trick_end)
        self.calculate_score_action = GameAction('calculate score action', target=self.calculate_score)

        self.play_end_signal.connect(lambda: print('play_end_signal'))

    def _get_data(self):
        """
        后台线程取得来自UI的数据，与send函数配合，实现同步
        :return:来自UI的数据
        """
        if not self._thread_event.is_set():
            self._thread_event.wait()
        data = self._received_data
        self._received_data = None
        self._thread_event.clear()
        return data

    def check_bid_valid(self, bid_result):
        """
        检测叫牌合法性
        :param bid_result:叫牌结果
        :return: 布尔值
        """
        return self._model.bid_table.check(bid_result)

    def check_play_valid(self, card):
        """检测出牌合法性"""
        if self._model.first_played_color is None:
            # 第一个出牌
            return True
        if card.color == self._model.first_played_color:
            # 花色与第一个出牌花色相同
            return True
        if self._model.current_player.color_num[self._model.first_played_color] == 0:
            # 第一个出牌的花色已经没了
            return True
        return False

    def deal(self, start_player_position=None):
        """
        发牌
        :param start_player_position: 初始发牌玩家位置
        :return: None
        """
        cards = list(fifty_two_cards)
        random.shuffle(cards)
        if isinstance(start_player_position,
                      int) and 0 <= start_player_position < 4:
            self._model.current_player_position = start_player_position
        else:
            self._model.current_player_position = random.randint(0, 3)
        for card in cards:
            self._model.current_player.get_card(card)
            self._model.current_player_position = (self._model.current_player_position + 1) % 4
        for player in self._model.players:
            player.init_AI()

        print('发牌结束')
        self.deal_end_signal.emit([player.cards for player in self._model.players])

    def bid_begin(self, start_player_position=None):
        """
        做一些叫牌开始前的准备工作，初始化叫牌相关的变量
        :param start_player_position:
        :return: None
        """
        if isinstance(start_player_position,
                      int) and 0 <= start_player_position < 4:
            self._model.current_player_position = start_player_position
        else:
            self._model.current_player_position = random.randint(0, 3)
        # self._model.king_color = None
        # self._model.pass_num = 0
        # self._model.last_bid_number, self._model.last_bid_color, self._model.last_bid_player_position = None, None, None

        print('叫牌开始')
        self._model.state = State.Biding
        self.bid_signal.emit()

    def _reset(self):
        """
        重置所有数据，清空事件队列
        :return:
        """
        self._model.reset()
        self._thread_event.clear()
        self._received_data = None
        while self._action_queue.qsize() > 0:
            self._action_queue.get_nowait()

    @wrapper
    def begin_game(self, deal_start_position=None, bid_start_position=None):
        """
        开始游戏事件的回调函数
        :param deal_start_position: 开始发牌的玩家位置
        :param bid_start_position: 开始叫牌的玩家位置
        :return:
        """
        # print('begin game', threading.current_thread().name)
        print('begin game')
        self._reset()

        self.deal(deal_start_position)

        if isinstance(bid_start_position,
                      int) and 0 <= bid_start_position < 4:
            self._model.current_player_position = bid_start_position
        else:
            self._model.current_player_position = random.randint(0, 3)

        print('叫牌开始')
        self._model.state = State.Biding
        self.bid_signal.emit()

    def biding(self):
        """
        叫牌，此函数的一次执行对应一名玩家的一次叫牌.
        叫牌结束，将产生bid_end事件
        :return:
        """

        # 没有人叫牌，或有一人叫、连续三人pass，或叫牌叫到了7无将
        # 跳转至下一状态
        if (self._model.win_bid_position is None) and self._model.pass_num == 4:
            self._action_queue.put_nowait(self.bid_end_action)
            return
        if (self._model.win_bid_position is not None) and self._model.pass_num == 3:
            self._action_queue.put_nowait(self.bid_end_action)
            return
        if self._model.bid_table.top == 74:  # 7无将
            self._action_queue.put_nowait(self.bid_end_action)
            return

        print(f'轮到{self._model.current_player_position}叫牌')

        if self._model.current_player.controlled_by_human:
            bid_result = self._get_data()
        else:
            bid_result = self._model.current_player.bid(self._model.last_bid_number, self._model.last_bid_color, self._model.last_bid_player_position)

        if bid_result is None:
            return

        if not self._model.bid_table.check(bid_result):
            # 不合法的叫牌被转换成pass
            # 实际上合法性检验是由其他地方完成的
            # 比如，对应人类叫牌结果，是由GUI通过send函数传递的，在这个函数内部会进行检查
            # 而AI的叫牌结果，AI自己应当保证叫牌合法；若AI给出了不合法的结果，认为是AI设计有疏漏，controller不会帮忙解决，只会将不合法的叫牌转化为pass
            bid_result = 0
        if bid_result > 74:
            # 限定bid_result最大为7无将
            bid_result = 74

        if bid_result == 0:
            self._model.pass_num += 1
        else:
            self._model.pass_num = 0
            self._model.last_bid_number, self._model.last_bid_color, self._model.last_bid_player_position = bid_result // 10, bid_result % 10, self._model.current_player_position
            self._model.win_bid_position = self._model.current_player_position
        self._model.bid_table.add_bid(self._model.current_player_position, bid_result)

        print(self._model.current_player_position, 'bidResult:', bid_result)

        self._model.current_player_position = (self._model.current_player_position + 1) % 4
        self.bid_signal.emit()

    def bid_end(self):
        """
        叫牌结束后的处理，确定将牌
        若没有出现4人全pass，则产生trick_begin事件；否则，跳转至Stop状态
        :return:
        """
        self._model.king_color = self._model.last_bid_color
        print('叫牌结束')
        if self._model.king_color is not None:
            # 进入出牌状态，同时设置current_player_position为第一个出牌的人
            # self._model.state = State.PlayBegin
            self._model.state = State.Play
            self._model.trick = 0
            self._action_queue.put_nowait(self.trick_begin_action)
            print('win bid position: {0}, king color: {1}'.format(
                self._model.win_bid_position,
                ['♣', '♦', '♥', '♠', 'NT'][self._model.king_color]))
        else:
            print('无人叫牌')
            self._model.state = State.Stop
        self.bid_end_signal.emit()

    def trick_begin(self):
        """
        开始出牌前进行一些准备工作，c初始化一些变量，在新一轮出牌开始时调用
        :return:
        """
        if self._model.trick == 0:
            self._model.current_player_position = (
                                                  self._model.win_bid_position + 1) % 4
            self._model.drink_tea_player_position = (
                                                    self._model.win_bid_position + 2) % 4
        else:
            self._model.current_player_position = self._model.win_player_position

        self._model.play_order = 0
        self._model.last_played_number, self._model.last_played_color, self._model.first_played_color = None, None, None
        self._model.state = State.Play
        print('第{0}轮出牌开始'.format(self._model.trick))
        self.play_begin_signal.emit()

    def play(self):
        """
        出牌
        此函数的一次执行对应一轮出牌
        :return:
        """
        if self._model.play_order == 4:
            self._action_queue.put_nowait(self.trick_end_action)
            return

        if self._model.trick == 0 and self._model.current_player_position == self._model.drink_tea_player_position:
            self._model.current_player.drink_tea = True
            teammate_position = self._model.current_player.teammate_position
            teammate = self._model.players[teammate_position]
            if isinstance(self._model.current_player, HumanPlayer) or isinstance(
                    teammate, HumanPlayer):
                # 人类玩家或人类玩家的队友明牌，则二者都由人类控制
                teammate.controlled_by_human = True
                self._model.current_player.controlled_by_human = True

        print(
            f'第{self._model.trick}轮，轮到玩家{self._model.current_player_position}出牌')

        if self._model.current_player.controlled_by_human:
            card_index = self._get_data()
            if card_index is None:
                return
            card = self._model.current_player.lose_card_by_index(card_index)
        else:
            card = self._model.current_player.play(self._model.last_played_number,
                                                   self._model.last_played_color,
                                                   self._model.trick,
                                                   self._model.first_played_color)
        self._model.last_played_color, self._model.last_played_number = card.number, card.color

        if self._model.play_order == 0:
            self._model.first_played_color = card.color

        print(f'第{self._model.trick}轮，玩家{self._model.current_player_position}出牌{card2str(card)}')

        self._model.trick_history[self._model.current_player_position] = card
        self._model.play_order += 1
        self.play_signal.emit(self._model.current_player_position, card)
        self._model.current_player_position = \
            (self._model.current_player_position + 1) % 4

    def trick_end(self):
        """
        一轮出牌结束后调用，在此函数中计算此轮胜者
        :return:
        """
        for (player, card) in sorted(list(self._model.trick_history.items()),
                                     key=lambda x: x[0]):
            print(player, ':', card2str(card), end=', ')
        print('将牌', self.king_color, 'first_played_color', self._model.first_played_color)
        values = []
        for position, card in self._model.trick_history.items():
            if card.color == self._model.king_color:
                v = 200 + card
            elif card.color == self._model.first_played_color:
                v = 100 + card
            else:
                v = card
            values.append((position, v))
        values.sort(key=lambda x: x[-1])
        print(values)
        self._model.win_player_position = values[-1][0]
        self._model.trick_history['win'] = self._model.win_player_position
        self._model.play_table.add(self._model.trick_history)
        self._model.trick_history = {}
        print(f'第{self._model.trick}轮，玩家{self._model.win_player_position}获胜')

        self._model.trick += 1
        if self._model.trick == 13:
            # 出牌结束，产生计分事件
            self._action_queue.put_nowait(self.calculate_score_action)
        else:
            # 否则产生trick_begin事件
            self._action_queue.put_nowait(self.trick_begin_action)
            self.play_end_signal.emit()

    def _on_state(self):
        """当处于某个状态时，调用相应函数。
        若始终处于其中一个状态，则相应函数会被反复调用。
        因而应保证下列每个函数多次调用不会使数据出错。
        """
        functions = {State.Stop: self._thread_event.wait,
                     State.Biding: self.biding, State.Play: self.play}
        return functions.get(self._model.state, lambda: None)()  # 实际上所有函数都返回None

    def _process_game_action(self, game_action):
        """处理事件，事件可能使状态发生变化，事实上状态的转移也采用了事件机制"""
        return game_action.execute()  # 实际返回值不会被利用

    def run(self):
        """
        后台线程run函数
        :return: None
        """
        while True:
            while self._action_queue.qsize() > 0:
                game_event = self._action_queue.get()
                self._process_game_action(game_event)
            self._on_state()

    def calculate_score(self):
        # TODO: 完成分值的计算
        # 假设有些数据需要存放在Model中，可以往Model里添加成员，
        # 但请确保新增成员有合适初值（一般为None），且在reset中重置
        pass

        self._model.state = State.Stop
