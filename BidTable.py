class BidTable(object):
    def __init__(self):
        super().__init__()
        self.History = [[4, 4, 4, 4, 4] for _ in range(6)]
        # 4 for blank player
        self.Top = 0

    def add_bid(self, BidPlayer, BidResult):
        """
        :param BidPlayer: 叫牌的玩家
        :param BidResult: 叫牌结果
        :return: None
        """
        # 假定叫牌结果不是pass
        self.History[BidResult // 10][BidResult % 10] = BidPlayer
        self.Top = BidResult
        return [BidResult // 10, BidResult % 10, BidPlayer]
