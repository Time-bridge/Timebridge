import unittest
from player import findTeammate, Player
from card import fiftyTwoCards
from enums import Position
import random


class playerTestCase(unittest.TestCase):
    def testFindTeammate(self):
        for myPosition in range(4):
            if myPosition == Position.North.value:
                foolResult = Position.South.value
            elif myPosition == Position.West.value:
                foolResult = Position.East.value
            elif myPosition == Position.South.value:
                foolResult = Position.North.value
            elif myPosition == Position.East.value:
                foolResult = Position.West.value
            else:
                foolResult = None
            self.assertEqual(0 <= foolResult < 4, True)
            self.assertEqual(foolResult, findTeammate(myPosition))

    def _testGetCard(self):
        random.shuffle(self.cardHeap)
        for i, card in enumerate(self.cardHeap):
            playerIndex = i % 4
            self.players[playerIndex].getCard(card)
            self.testCardLists[playerIndex].append(card)
            self.testCardLists[playerIndex].sort()
            self.assertEqual(self.testCardLists[playerIndex],
                             self.players[playerIndex].cards, 'getCard failed')
        for player in self.players:
            self.assertEqual(len(player.cards), 13)

    def _testLoseCard(self):
        # testLostCardLists = [], [], [], []
        playerIndices = list(range(4))
        for _ in range(13):
            # 13轮
            random.shuffle(playerIndices)
            for playerIndex in range(4):
                # 以随机的顺序出牌
                card = random.choice(self.testCardLists[playerIndex])
                self.testCardLists[playerIndex].remove(card)
                self.players[playerIndex].loseCard(card)
                self.assertEqual(self.players[playerIndex].cards, self.testCardLists[playerIndex], 'loseCard failed')

    def testGetAndLose(self):
        self.players = [Player(position) for position in range(4)]
        self.cardHeap = list(fiftyTwoCards)
        self.testCardLists = [], [], [], []

        self._testGetCard()

        for player in self.players:
            player.initAI()

        self._testLoseCard()


if __name__ == '__main__':
    unittest.main()
