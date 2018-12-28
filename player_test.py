import unittest
from player import find_teammate, Player
from card import fifty_two_cards
from enums import Position
import random


class PlayerTestCase(unittest.TestCase):
    def test_find_teammate(self):
        for my_position in range(4):
            if my_position == Position.North.value:
                fool_result = Position.South.value
            elif my_position == Position.West.value:
                fool_result = Position.East.value
            elif my_position == Position.South.value:
                fool_result = Position.North.value
            elif my_position == Position.East.value:
                fool_result = Position.West.value
            else:
                fool_result = None
            self.assertEqual(0 <= fool_result < 4, True)
            self.assertEqual(fool_result, find_teammate(my_position))

    def _test_get_card(self):
        random.shuffle(self.card_heap)
        for i, card in enumerate(self.card_heap):
            player_index = i % 4
            self.players[player_index].get_card(card)
            self.card_lists[player_index].append(card)
            self.card_lists[player_index].sort()
            self.assertEqual(self.card_lists[player_index],
                             self.players[player_index].cards, 'getCard failed')
        for player in self.players:
            self.assertEqual(len(player.cards), 13)

    def _test_lose_card(self):
        # testLostCardLists = [], [], [], []
        player_indices = list(range(4))
        for _ in range(13):
            # 13轮
            random.shuffle(player_indices)
            for playerIndex in range(4):
                # 以随机的顺序出牌
                card = random.choice(self.card_lists[playerIndex])
                self.card_lists[playerIndex].remove(card)
                self.players[playerIndex].lose_card(card)
                self.assertEqual(self.players[playerIndex].cards, self.card_lists[playerIndex], 'loseCard failed')

    def test_get_and_lose(self):
        self.players = [Player(position) for position in range(4)]
        self.card_heap = list(fifty_two_cards)
        self.card_lists = [], [], [], []

        self._test_get_card()

        for player in self.players:
            player.init_AI()

        self._test_lose_card()


if __name__ == '__main__':
    unittest.main()
