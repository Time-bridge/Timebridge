from enums import Suit


class Card(int):
    # suit为花色，是枚举类型，建议仅GUI使用
    color = property(lambda self: self // 13)
    number = property(lambda self: self % 13)
    suit = property(lambda self: Suit(self // 13))


def createCard(color, number):
    return Card(13 * color + number)


# 一副牌，设定成元组是不希望被修改
fiftyTwoCards = tuple([Card(i) for i in range(52)])

