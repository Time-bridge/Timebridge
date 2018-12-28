from card import Card
from enums import Suit
import unittest


class CardTestCase(unittest.TestCase):
    def test_color(self):
        for i in range(52):
            self.assertEqual(i//13, Card(i).color, '不能正确获取color属性')

    def test_number(self):
        for i in range(52):
            self.assertEqual(i % 13, Card(i).number, '不能正确获取number属性')

    def test_suit(self):
        for i in range(52):
            card = Card(i)
            suit_index = card.color
            self.assertEqual(Suit(suit_index), Card(i).suit, '不能正确获取number属性')


if __name__ == '__main__':
    unittest.main()
