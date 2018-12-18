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
from collections import namedtuple


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


PlayerInfo = namedtuple('PlayerInfo',
                        ['cards', 'played_card', 'is_visible'])


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
    output_signal = pyqtSignal(str)
    view_update_signal = pyqtSignal()

    state = property(lambda self: self.__model.state)
    max_bid = property(lambda self: self.__model.bid_table.top)
    win_bid_position = property(lambda self: self.__model.win_bid_position)
    king_color = property(lambda self: self.__model.king_color)
    current_player_position = property(lambda self: self.__model.current_player_position)

    def send(self, data=None, info=None):
        """供GUI调用，用于给controller发送叫牌、出牌结果。"""
        if info == DateInfo.Bid:
            # 来自GUI叫牌区的用户点击（叫牌结果）
            if self.__model.state == State.Biding and (
                        self.__model.current_player is not None) and \
                    self.__model.current_player.controlled_by_human and (
                        data is not None):
                # and (data == 0 or self.check_bid_valid(data)):
                if self.check_bid_valid(data):
                    self._received_data = data
                else:
                    self._received_data = 0
                self._thread_event.set()
        elif info == DateInfo.HumanPlay:
            # 来自GUI人类玩家出牌
            if self.__model.state == State.Play and\
                self.__model.current_player_position == 0 and \
                    (data is not None):
                # 此时接收的data是牌的序号
                card = self.__model.current_player.cards[data]
                # 出牌合法性检查
                if self.check_play_valid(card):
                    self._received_data = data
                    self._thread_event.set()
        elif info == DateInfo.AIPlay:
            # GUI队友AI出牌
            if self.__model.state == State.Play and \
                    self.__model.current_player_position == 2 and \
                    self.__model.current_player.controlled_by_human and \
                    (data is not None):
                # 此时接收的data是牌的序号
                card = self.__model.current_player.cards[data]
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
        return self.__model.bid_table.get_bid_result(i) if self.__model.state == State.Biding else ''

    def get_player_info(self, i):
        """
        读取第i个玩家的信息的接口
        :param i: 玩家序号（位置）
        :return: 命名元组PlayerInfo，其包含手牌、刚出的牌、是否应当显示3个元素
        """
        played_card = self.__model.trick_history.get(i, None)
        player = self.__model.players[i]
        if player.controlled_by_human or player.drink_tea:
            return PlayerInfo(player.cards_iter, played_card, True)
        else:
            return PlayerInfo([None]*len(player.cards), played_card, False)

    def new_game(self):
        """
        UI“新游戏”按钮的槽函数
        :return:
        """
        # print('new game', threading.current_thread().name)
        self.__action_queue.put_nowait(self.begin_game_action)
        self.notify()

    def __init__(self, model=None):
        super().__init__()
        if model is None:
            self.__model = Model()
        else:
            self.__model = model

        # 状态转移采用事件机制，Queue存储了未处理的事件
        self.on_state_functions = {}
        self.__action_queue = Queue()

        # 线程相关
        self._thread = threading.Thread(target=self.__run)
        self._thread.setDaemon(True)
        self._received_data = None
        self._thread_event = threading.Event()  # 用于控制线程同步，同时也是接收到数据的标志
        self._thread_event.clear()
        self.notify = lambda: self.send()
        self._thread.start()

        # 预定义的GameAction
        self.begin_game_action = GameAction('begin game action', target=self.__begin_game)
        self.bid_end_action = GameAction('bid end action', target=self.__bid_end)
        self.trick_begin_action = GameAction('trick begin action', target=self.__trick_begin)
        self.trick_end_action = GameAction('trick end action', target=self.__trick_end)
        self.calculate_score_action = GameAction('calculate score action',
                                                 target=self.__calculate_score)

    def __get_data(self):
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

    def output(self, *messages, sep=' ', end='\n'):
        """
        输出消息。
        消息通过output_signal发出，若UI将此信号绑定至某个可显示组件上
        （将此信号连接至组件的setText函数），
        则可实现Controller向UI发送字符串信息。
        各参数含义与print函数相同。
        :param messages:待输出的信息，数组类型
        :param sep: 各消息之间的分隔符
        :param end: 结尾符号
        :return: None
        """
        # 可根据需要修改此函数实现，将消息发送至不同地方
        pass
        msg = sep.join((str(item) for item in messages)) + end
        self.output_signal.emit(msg)
        print(*messages, sep=sep, end=end)

    def check_bid_valid(self, bid_result):
        """
        检测叫牌合法性
        :param bid_result:叫牌结果
        :return: 布尔值
        """
        return self.__model.bid_table.check(bid_result)

    def check_play_valid(self, card):
        """检测出牌合法性"""
        if self.__model.first_played_color is None:
            # 第一个出牌
            return True
        if card.color == self.__model.first_played_color:
            # 花色与第一个出牌花色相同
            return True
        if self.__model.current_player.color_num[self.__model.first_played_color] == 0:
            # 第一个出牌的花色已经没了
            return True
        return False

    def __deal(self, start_player_position=None):
        """
        发牌
        :param start_player_position: 初始发牌玩家位置
        :return: None
        """
        cards = list(fifty_two_cards)
        random.shuffle(cards)
        if isinstance(start_player_position,
                      int) and 0 <= start_player_position < 4:
            self.__model.current_player_position = start_player_position
        else:
            self.__model.current_player_position = random.randint(0, 3)
        for card in cards:
            self.__model.current_player.get_card(card)
            self.__model.current_player_position = (self.__model.current_player_position + 1) % 4
        for player in self.__model.players:
            player.init_AI()

        self.output('发牌结束')

    def __bid_begin(self, start_player_position=None):
        """
        做一些叫牌开始前的准备工作，初始化叫牌相关的变量
        :param start_player_position:
        :return: None
        """
        if isinstance(start_player_position,
                      int) and 0 <= start_player_position < 4:
            self.__model.current_player_position = start_player_position
        else:
            self.__model.current_player_position = random.randint(0, 3)
        # self.__model.king_color = None
        # self.__model.pass_num = 0
        # self.__model.last_bid_number, self.__model.last_bid_color, self.__model.last_bid_player_position = None, None, None

        self.output('叫牌开始')
        self.__model.state = State.Biding

    def __reset(self):
        """
        重置所有数据，清空事件队列
        :return:
        """
        self.__model.reset()
        self._thread_event.clear()
        self._received_data = None
        while self.__action_queue.qsize() > 0:
            self.__action_queue.get_nowait()

    @wrapper
    def __begin_game(self, deal_start_position=None, bid_start_position=None):
        """
        开始游戏事件的回调函数
        :param deal_start_position: 开始发牌的玩家位置
        :param bid_start_position: 开始叫牌的玩家位置
        :return:
        """
        # print('begin game', threading.current_thread().name)
        self.output('begin game')
        self.__reset()

        self.__deal(deal_start_position)

        if isinstance(bid_start_position,
                      int) and 0 <= bid_start_position < 4:
            self.__model.current_player_position = bid_start_position
        else:
            self.__model.current_player_position = random.randint(0, 3)

        self.output('叫牌开始')
        self.__model.state = State.Biding
        self.view_update_signal.emit()

    def __biding(self):
        """
        叫牌，此函数的一次执行对应一名玩家的一次叫牌.
        叫牌结束，将产生bid_end事件
        :return:
        """

        # 没有人叫牌，或有一人叫、连续三人pass，或叫牌叫到了7无将
        # 跳转至下一状态
        if (self.__model.win_bid_position is None) and self.__model.pass_num == 4:
            self.__action_queue.put_nowait(self.bid_end_action)
            return
        if (self.__model.win_bid_position is not None) and self.__model.pass_num == 3:
            self.__action_queue.put_nowait(self.bid_end_action)
            return
        if self.__model.bid_table.top == 74:  # 7无将
            self.__action_queue.put_nowait(self.bid_end_action)
            return

        self.output('轮到{}叫牌'.format(self.__model.current_player_position))

        if self.__model.current_player.controlled_by_human:
            bid_result = self.__get_data()
        else:
            bid_result = self.__model.current_player.bid(self.__model.last_bid_number, self.__model.last_bid_color, self.__model.last_bid_player_position)

        if bid_result is None:
            return

        if not self.__model.bid_table.check(bid_result):
            # 不合法的叫牌被转换成pass
            # 实际上合法性检验是由其他地方完成的
            # 比如，对应人类叫牌结果，是由GUI通过send函数传递的，在这个函数内部会进行检查
            # 而AI的叫牌结果，AI自己应当保证叫牌合法；若AI给出了不合法的结果，认为是AI设计有疏漏，controller不会帮忙解决，只会将不合法的叫牌转化为pass
            bid_result = 0
        if bid_result > 74:
            # 限定bid_result最大为7无将
            bid_result = 74

        if bid_result == 0:
            self.__model.pass_num += 1
        else:
            self.__model.pass_num = 0
            self.__model.last_bid_number, self.__model.last_bid_color, self.__model.last_bid_player_position = bid_result // 10, bid_result % 10, self.__model.current_player_position
            self.__model.win_bid_position = self.__model.current_player_position
        self.__model.bid_table.add_bid(self.__model.current_player_position, bid_result)

        self.output(self.__model.current_player_position, 'bidResult:', bid_result)

        self.__model.current_player_position = (self.__model.current_player_position + 1) % 4
        self.view_update_signal.emit()

    def __bid_end(self):
        """
        叫牌结束后的处理，确定将牌
        若没有出现4人全pass，则产生trick_begin事件；否则，跳转至Stop状态
        :return:
        """
        self.__model.king_color = self.__model.last_bid_color
        self.output('叫牌结束')
        if self.__model.king_color is not None:
            # 进入出牌状态，同时设置current_player_position为第一个出牌的人
            self.__model.state = State.Play
            self.__model.trick = 0
            self.__action_queue.put_nowait(self.trick_begin_action)
            self.output('win bid position: {0}, king color: {1}'.format(
                self.__model.win_bid_position,
                ['♣', '♦', '♥', '♠', 'NT'][self.__model.king_color]))
        else:
            self.output('无人叫牌')
            self.__model.state = State.Stop
        self.view_update_signal.emit()

    def __trick_begin(self):
        """
        开始出牌前进行一些准备工作，c初始化一些变量，在新一轮出牌开始时调用
        :return:
        """
        if self.__model.trick == 0:
            self.__model.current_player_position = (
                                                       self.__model.win_bid_position + 1) % 4
            self.__model.drink_tea_player_position = (
                                                         self.__model.win_bid_position + 2) % 4
        else:
            self.__model.current_player_position = self.__model.win_player_position

        self.__model.play_order = 0
        self.__model.last_played_number, self.__model.last_played_color, self.__model.first_played_color = None, None, None
        self.__model.state = State.Play
        self.output('第{0}轮出牌开始'.format(self.__model.trick))
        self.view_update_signal.emit()

    def __play(self):
        """
        出牌
        此函数的一次执行对应一轮出牌
        :return:
        """
        if self.__model.play_order == 4:
            self.__action_queue.put_nowait(self.trick_end_action)
            return

        if self.__model.trick == 0 and self.__model.current_player_position == self.__model.drink_tea_player_position:
            self.__model.current_player.drink_tea = True
            teammate_position = self.__model.current_player.teammate_position
            teammate = self.__model.players[teammate_position]
            if isinstance(self.__model.current_player, HumanPlayer) or isinstance(
                    teammate, HumanPlayer):
                # 人类玩家或人类玩家的队友明牌，则二者都由人类控制
                teammate.controlled_by_human = True
                self.__model.current_player.controlled_by_human = True

        self.output('第{}轮，轮到玩家{}出牌'.format(self.__model.trick,
                                           self.__model.current_player_position))

        if self.__model.current_player.controlled_by_human:
            card_index = self.__get_data()
            if card_index is None:
                return
            card = self.__model.current_player.lose_card_by_index(card_index)
        else:
            card = self.__model.current_player.play(self.__model.last_played_number,
                                                    self.__model.last_played_color,
                                                    self.__model.trick,
                                                    self.__model.first_played_color)
        self.__model.last_played_color, self.__model.last_played_number = card.number, card.color

        if self.__model.play_order == 0:
            self.__model.first_played_color = card.color

        self.output('第{}轮，玩家{}出牌{}'.format(self.__model.trick,
                                           self.__model.current_player_position,
                                           card2str(card)))

        self.__model.trick_history[self.__model.current_player_position] = card
        self.__model.play_order += 1
        self.view_update_signal.emit()
        self.__model.current_player_position = \
            (self.__model.current_player_position + 1) % 4

    def __trick_end(self):
        """
        一轮出牌结束后调用，在此函数中计算此轮胜者
        :return:
        """
        for (player, card) in sorted(list(self.__model.trick_history.items()),
                                     key=lambda x: x[0]):
            self.output(player, ':', card2str(card), end=', ')
        self.output('将牌', self.king_color, 'first_played_color', self.__model.first_played_color)
        values = []
        for position, card in self.__model.trick_history.items():
            if card.color == self.__model.king_color:
                v = 200 + card
            elif card.color == self.__model.first_played_color:
                v = 100 + card
            else:
                v = card
            values.append((position, v))
        values.sort(key=lambda x: x[-1])
        self.output(values)
        self.__model.win_player_position = values[-1][0]
        self.__model.trick_history['win'] = self.__model.win_player_position
        self.__model.play_table.add(self.__model.trick_history)
        self.__model.trick_history = {}
        self.output('第{}轮，玩家{}获胜'.format(self.__model.trick,
                                         self.__model.win_player_position))

        self.__model.trick += 1
        if self.__model.trick == 13:
            # 出牌结束，产生计分事件
            self.__action_queue.put_nowait(self.calculate_score_action)
        else:
            # 否则产生trick_begin事件
            self.__action_queue.put_nowait(self.trick_begin_action)
            self.view_update_signal.emit()

    def __on_state(self):
        """当处于某个状态时，调用相应函数。
        若始终处于其中一个状态，则相应函数会被反复调用。
        因而应保证下列每个函数多次调用不会使数据出错。
        """
        functions = {State.Stop: self._thread_event.wait,
                     State.Biding: self.__biding, State.Play: self.__play,
                     State.End: self._thread_event.wait}
        return functions.get(self.__model.state, lambda: None)()  # 实际上所有函数都返回None

    def __process_game_action(self, game_action):
        """处理事件，事件可能使状态发生变化，事实上状态的转移也采用了事件机制"""
        return game_action.execute()  # 实际返回值不会被利用

    def __run(self):
        """
        后台线程run函数
        :return: None
        """
        while True:
            while self.__action_queue.qsize() > 0:
                game_event = self.__action_queue.get()
                self.__process_game_action(game_event)
            self.__on_state()

    def __calculate_score(self):
        # TODO: 完成分值的计算
        # 假设有些数据需要存放在Model中，可以往Model里添加成员，
        # 但请确保新增成员有合适初值（一般为None），且在reset中重置
        pass

        self.__model.state = State.End
        self.view_update_signal.emit()
