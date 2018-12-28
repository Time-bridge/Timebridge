import unittest
from player import AIPlayer
from card import fifty_two_cards
import random


class AIPlayerTestCase(unittest.TestCase):
    def test_play(self):
        players = [AIPlayer(i) for i in range(4)]
        cards = list(fifty_two_cards)
        random.shuffle(cards)
        for i, card in enumerate(cards):
            players[i % 4].get_card(card)

        for player in players:
            player.init_AI()

        for i in range(13):
            first_start_player = random.randint(0, 3)
            last_played_number, last_played_color, first_played_color = None, None, None
            for j in range(4):
                player = players[(j + first_start_player) % 4]
                card = player.play(last_played_number, last_played_color, j, first_played_color)
                last_played_number = card.number
                last_played_color = card.color
                if j == 0:
                    first_played_color = card.color
        for player in players:
            self.assertEqual(len(player.cards), 0)


if __name__ == '__main__':
    unittest.main()
