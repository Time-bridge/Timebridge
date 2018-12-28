from collections import Iterable, namedtuple


class ReadOnlyIterable(Iterable):
    """
    用于访问列表、字典、元组等的只读接口，
    可进行迭代、计算长度
    """

    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return self.iterable.__iter__()

    def __len__(self):
        return self.iterable.__len__()

    def __getitem__(self, item):
        return self.iterable.__getitem__(item)
        # value = self.iterable.__getitem__(item)
        # if isinstance(value, Iterable) and not isinstance(value, str) \
        #         and not isinstance(item, slice) \
        #         and not isinstance(value, ReadOnlyIterable):
        #     return ReadOnlyIterable(value)
        # else:
        #     return value


BidResult = namedtuple('BidResult', ['number', 'color'])
PASS = BidResult(0, None)
MAX_BID_RESULT = BidResult(7, 4)


def bid_greater(b1, b2):
    return b1.number > b2.number or (
        b1.number == b2.number and
        b1.number != 0 and b1.color > b2.color)
