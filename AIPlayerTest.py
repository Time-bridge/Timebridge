import unittest
from player import AIPlayer
from card import fiftyTwoCards
import random


class AIPlayerTestCase(unittest.TestCase):
    def testPlay(self):
        players = [AIPlayer(i) for i in range(4)]
        cards = list(fiftyTwoCards)
        random.shuffle(cards)
        for i, card in enumerate(cards):
            players[i % 4].getCard(card)

        for player in players:
            player.initAI()

        for i in range(13):
            firstStartPlayer = random.randint(0, 3)
            lastPlayedNumber, lastPlayedColor = None, None
            # playedCards = []
            for j in range(4):
                player = players[(j + firstStartPlayer) % 4]
                card = player.play(lastPlayedNumber, lastPlayedColor, j)
                lastPlayedNumber = card.number
                lastPlayedColor = card.color
                # playedCards.append(card)
            # winPlayer = playedCards
        for player in players:
            self.assertEqual(len(player.cards), 0)


if __name__ == '__main__':
    unittest.main()
