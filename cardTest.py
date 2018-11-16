from card import Card
from enums import Suit
import unittest


class CardTestCase(unittest.TestCase):
    def testColor(self):
        for i in range(52):
            self.assertEqual(i//13, Card(i).color, '不能正确获取color属性')

    def testNumber(self):
        for i in range(52):
            self.assertEqual(i % 13, Card(i).number, '不能正确获取number属性')

    def testSuit(self):
        for i in range(52):
            card = Card(i)
            suitIndex = card.color
            self.assertEqual(Suit(suitIndex), Card(i).suit, '不能正确获取number属性')


if __name__ == '__main__':
    unittest.main()
