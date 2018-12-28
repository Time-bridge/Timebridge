import unittest
import random
import re
import traceback
from controller import Controller
from enums import State, DateInfo
from collections import OrderedDict
from card import card2str, create_card


# view层需要向controller传递出牌、叫牌结果
# 因此下面定义了一系列生成器（大多基于随机数），用于生成出牌、叫牌结果
def random_color():
    """随机选择一种颜色"""
    return random.choice(range(5))


def bid_result_generator0():
    """生成器，随机叫0~7之间的数字，随机颜色"""
    while True:
        yield random.choice(range(8)), random_color()


def bid_result_generator1():
    """生成器，永远pass"""
    while True:
        yield 0, random_color()


def bid_result_generator2(controller):
    """生成器，叫牌结果比之前的结果大一点"""
    while True:
        yield controller.max_bid[0] + 1, random_color()


def bid_result_generator3(controller):
    """生成器，随机选择前3个生成器生成的值"""
    g0 = bid_result_generator0()
    g1 = bid_result_generator1()
    g2 = bid_result_generator2(controller)
    try:
        while True:
            yield next(random.choice((g0, g1, g2)))
    finally:
        g0.close()
        g1.close()
        g2.close()


def bid_result_generator(controller):
    """随机返回一个生成器"""
    idx = random.randrange(0, 4)
    if 0 <= idx < 2:
        return random.choice((bid_result_generator0, bid_result_generator1))()
    else:
        return random.choice((bid_result_generator2, bid_result_generator3))(controller)


def play_result_generator0():
    """生成器，永远选择最前一张牌"""
    while True:
        yield 0


def play_result_generator1():
    """生成器，返回[0, 20)之间的随机整数"""
    while True:
        yield random.randrange(0, 20)


def play_result_generator2(card_list):
    """生成器，选择最后一张牌"""
    while True:
        yield len(card_list) - 1


def play_result_generator3(card_list):
    """生成器，随机选择一张牌"""
    while True:
        try:
            yield random.randrange(0, len(card_list))
        except ValueError:
            yield None


def play_result_generator(controller, i):
    """使用前面定义的四个生成器，依次生成一个值，可模拟人类玩家出牌"""

    player_info = controller.get_player_info(i)

    g0, g1, g2, g3 = play_result_generator0(), \
        play_result_generator1(), \
        play_result_generator2(player_info.cards), \
        play_result_generator3(player_info.cards)

    try:
        while True:
            yield next(g0)
            yield next(g1)
            yield next(g2)
            yield next(g3)
    finally:
        g0.close()
        g1.close()
        g2.close()
        g3.close()


class ControllerTestCase(unittest.TestCase):
    """ 测试Controller是否能正确运行，方法是用自定义生成器代替人类玩家输入，
     截获Controller的输出信息，从输出信息中提取游戏记录，将提取的结果与Controller内
     存储的信息比较（实际是存储Model内，但Controller提供了访问接口，看上去是存储在
     Controller内），并检验记录是否符合游戏规则"""
    def check_played_card(self):
        """ 检验刚打出的牌 """
        for player in range(4):
            played_card = self.controller.get_player_info(player).played_card
            if played_card:
                self.assertIn(player, self.trick_history)
                self.assertEqual(self.trick_history[player][0], played_card.number)
                self.assertEqual(self.trick_history[player][1], played_card.color)

    def check_hand_cards(self, i):
        """ 检验controller是否正确存储手牌 """
        player_info = self.controller.get_player_info(i)
        self.assertListEqual(list(self.hand_cards[i].keys()), list(
            map(lambda card: (card.number, card.color), player_info.cards)))

    def check_trick_end(self):
        # print(self.trick_history)
        # self.fp.write(str(self.trick_history) + '\n')
        # self.fp.write(hand_cards_to_str([self.controller.get_player_info(i).cards for i in range(4)]))
        # return
        """ 在一轮结束后，检验此轮出牌是否符合游戏规则 """
        first_played_color = self.trick_history[self.first_player_position][-1]
        scores = []
        for player in range(4):
            number, color = self.trick_history[player]
            if color != first_played_color:
                # 确保没有相同颜色的牌，才能出其他牌
                try:
                    self.assertEqual(0, sum(map(
                        lambda card: (1 if card.color == first_played_color else 0),
                        self.controller.get_player_info(player).cards)))
                except AssertionError as e:
                    print('player', player)
                    print('history', self.trick_history)
                    print('first_played_color', first_played_color)
                    print('controller cards', list(map(card2str, self.controller.get_player_info(player).cards)))
                    print('self cards', list(map(lambda item: card2str(create_card(item[-1], item[0])), self.hand_cards[player])))
                    traceback.print_exc()
                    raise e

            score = 13 * color + number
            if color == self.king_color:
                score += 200
            elif color == first_played_color:
                score += 100
            scores.append((player, score))

        # 检验胜者是否正确
        win_player = max(scores, key=lambda x: x[-1])[0]
        self.assertEqual(win_player, self.trick_history['win'])
        self.first_player_position = self.trick_history['win']

    def extract(self, msg):
        """
        从controller输出的信息中，提取游戏记录，并与实际存储的数据对比，
        确保正确存储了游戏状态信息，且符合游戏规则
        :param msg: 字符串，controller在运行过程中输出的信息
        :return:
        """
        msg = msg.strip()
        bid_result_pattern = re.compile(
            r'^(\d)\s+BidResult\(number=(\d),\s+color=(\d|None)\)$')
        bid_end_pattern = re.compile(
            r'^win bid position:\s+(\d), king color:\s+([♠♥♦♣]|NT|nt)$')
        play_result_pattern = re.compile(
            r'^第(\d+)轮，玩家(\d)出牌([♠♥♦♣]|NT|nt)(\d+|[JQKA])$')
        play_win_pattern = re.compile(r'^第(\d+)轮，玩家(\d)获胜$')
        color_dict = dict(zip(list('♠♥♦♣') + ['NT', 'nt'], map(int, '321044')))
        number_dict = dict(zip(list('23456789') + ['10', 'J', 'Q', 'K', 'A'], range(13)))
        if msg == '发牌结束':
            # 记录初始手牌
            self.hand_cards = [OrderedDict(map(lambda card: ((card.number, card.color), None), self.controller.get_player_info(i).cards)) for i in range(4)]
            self.bid_history = []
            self.play_history = []
            self.trick_history = {}
        elif self.controller.state == State.Biding and bid_result_pattern.match(msg):
            # 提取叫牌信息
            res = bid_result_pattern.findall(msg)
            if len(res) != 1:
                return

            player, number, color = res[0]
            player = int(player)
            number = int(number)
            if color == 'None':
                color = None
            else:
                color = int(color)
            self.bid_history.append((player, (number, color)))
        elif self.controller.state == State.Biding and bid_end_pattern.match(msg):
            # 提取叫牌结束后，将牌、庄家信息
            res = bid_end_pattern.findall(msg)
            if len(res) != 1:
                return

            player, color = res[0]
            player = int(player)
            self.assertIn(color, color_dict)
            color = color_dict[color]
            self.win_bid_position = player
            self.king_color = color

            self.first_player_position = (1 + self.win_bid_position) % 4
            # self.max_bid = 0
        elif self.controller.state == State.Play and play_result_pattern.match(msg):
            # 提取出牌记录
            res = play_result_pattern.findall(msg)
            if len(res) != 1:
                return

            trick, player, color, number = res[0]
            trick = int(trick) - 1
            player = int(player)
            self.assertEqual(player, self.controller.current_player_position)
            self.assertIn(color, color_dict)
            color = color_dict[color]
            self.assertIn(number, number_dict)
            number = number_dict[number]
            self.trick_history[player] = (number, color)
            self.assertEqual(len(self.play_history), trick)

            self.hand_cards[player].pop((number, color))
            self.check_played_card()
            self.check_hand_cards(player)
        elif self.controller.state == State.Play and play_win_pattern.match(msg):
            # 一轮结束后，提取此轮胜者
            res = play_win_pattern.findall(msg)
            if len(res) != 1:
                return

            trick, player = res[0]
            trick = int(trick) - 1  # 输出信息中，轮数是从第1轮开始，但内部记录是从0开始
            player = int(player)
            self.trick_history['win'] = player
            self.assertEqual(len(self.play_history), trick)
            self.assertEqual(len(self.trick_history), 5)
            self.play_history.append(self.trick_history)
            self.check_trick_end()

            self.trick_history = {}
            self.check_play_history()

    def output(self, *args, sep=' ', end='\n'):
        """
        python是动态语言， 可以在运行时用此函数替换Controller的输出函数，
        截获Controller的输出，并从输出信息中提取游戏记录
        :param args: 输出的一系列变量
        :param sep: 各args之间的分隔符
        :param end: 结尾符
        :return:
        """
        # 下面会将信息输出到屏幕，也会写入文件，但这并不是必要的
        # self.extract函数的调用对于测试才是必要的
        msg = sep.join((str(item) for item in args)) + end
        self.extract(msg)
        if self.fp:
            self.fp.write(msg)
            self.fp.flush()
        print(msg, end='')

    def setUp(self):
        """ 创建controller，并替换controller的输出函数 """
        self.fp = open('game history.txt', 'w', encoding='utf-8')

        self.controller = Controller()
        # self.controller.output = output
        self.controller.output = self.output
        self.controller.set_delay_time(0)

        self.human_player_play_gen = None
        self.human_player_bid_gen = None
        self.ai_player_play_gen = None

    def check_bid_history(self):
        """ 检验叫牌结果正确性 """

        # 检验测试用例保存的叫牌结果和Controller保存的叫牌结果相同
        self.assertIsNotNone(self.bid_history)
        bid_table = self.controller.bid_table
        self.assertEqual(len(self.bid_history), len(bid_table.history))
        for self_bid_result, bid_result in zip(self.bid_history, bid_table.history):
            self.assertEqual(self_bid_result[0], bid_result[0])
            self.assertEqual(self_bid_result[1], bid_result[1])

        # 将叫牌记录映射为字符串（pass为字符0，否则为字符1）
        # 用正则表达式检查PASS次数是否符合规则
        str_ = ''.join(
            map(lambda x: ('0' if x[-1].number == 0 else '1'), bid_table.history))

        # 四人全pass
        if str_ == '0000':
            return

        # print(str_)
        if bid_table.history[-1][-1] != (7, 4):
            self.assertIsNotNone(re.match(r'^0{0,3}(1+0{1,3})*1+0{3}$', str_))
        else:
            self.assertIsNotNone(re.match(r'^0{0,3}(1+0{1,3})*1+$', str_))


        # 对于非PASS的叫牌，保证每个叫牌结果比之前的大
        cur_bid = (0, 0)
        for _, bid_result in filter(lambda x: x[-1].number > 0, bid_table.history):
            self.assertLess(cur_bid, bid_result)
            cur_bid = bid_result

        # 检验最终将牌，庄家，最大叫牌结果的正确性
        max_bid = max(map(lambda x: x[-1], self.bid_history[-4:]))
        self.assertEqual(max_bid[-1],
                         self.king_color)
        self.assertEqual(self.king_color, self.controller.king_color)
        self.assertEqual(dict(self.bid_history[-4:])[self.win_bid_position], max_bid)
        self.assertLessEqual(max_bid, (7, 4))

    def check_play_history(self):
        """ 检验出牌记录符合游戏规则 """
        if self.king_color is None:
            # 叫牌阶段全pass，没有出牌阶段
            return

        # 验证controller正确记录了出牌历史
        self.assertEqual(len(self.play_history),
                         len(self.controller.play_table))
        for self_trick_history, trick_history in zip(self.play_history, self.controller.play_table):
            self.assertEqual(len(self_trick_history), len(trick_history))
            self.assertEqual(self_trick_history['win'], trick_history['win'])
            for i in range(4):
                self.assertEqual(self_trick_history[i], (
                    trick_history[i].number, trick_history[i].color))

    def before(self, i):
        """ 在一局游戏开始前，创建生成器，触发controller开始游戏 """
        self.fp.write('第{}局游戏开始'.format(i) + '\n')

        # 开始新游戏
        self.controller.new_game()
        self.human_player_play_gen = play_result_generator(self.controller, 0)
        self.human_player_bid_gen = bid_result_generator(self.controller)

        self.ai_player_play_gen = play_result_generator(self.controller, 2)

    def after(self, i):
        """ 在一局游戏结束后，检测叫牌、出牌历史是否符合游戏规则 """
        self.human_player_bid_gen.close()
        self.human_player_play_gen.close()
        self.ai_player_play_gen.close()

        self.check_bid_history()
        self.check_play_history()

        # 这里我就不用json转化了
        str_ = str({key: self.__dict__.get(key, None) for key in
                    ['bid_history', 'play_history', 'trick_history']})
        self.fp.write(str_ + '\n')

        self.fp.write('第{}局游戏结束'.format(i) + '\n\n\n')
        self.fp.flush()

    def __bid_and_play(self):
        """ 模拟一局游戏 """
        while self.controller.state != State.Biding:
            pass

        while self.controller.state == State.Biding:
            if self.controller.current_player_position == 0:
                self.controller.send(next(self.human_player_bid_gen),
                                     DateInfo.Bid)

        while self.controller.state == State.Play and self.controller.trick < 13:
            # time.sleep(0.005)
            if self.controller.current_player_position == 0:
                self.controller.send(next(self.human_player_play_gen), DateInfo.HumanPlay)
            if self.controller.current_player_position == 2:
                self.controller.send(next(self.ai_player_play_gen), DateInfo.AIPlay)

    def test_several_times(self):
        # """ 进行多局游戏 """
        number = 50
        for i in range(number):
            self.before(i)
            self.__bid_and_play()
            self.after(i)


if __name__ == '__main__':
    try:
        from HtmlTestRunner import HTMLTestRunner
    except ImportError:
        unittest.main()
    else:
        suite = unittest.TestSuite()
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ControllerTestCase))
        # suite

        # 生成测试报告
        with open('HTMLReport.html', 'w') as f:
            runner = HTMLTestRunner(output='controller_test',
                                    report_title='Controller Test Report',
                                    descriptions='this is a report '
                                                 'generated by HTMLTestRunner, '
                                                 'which can be installed using '
                                                 '"pip install html-testrunner"',
                                    verbosity=2, stream=f)
            runner.run(suite)
            f.flush()
