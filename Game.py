import random
import TimeBridgeGUI
import TimeBridgeAI

class Player:
	
	def __init__(self):
		self.Card = []
		self.ColorNum = [0, 0, 0, 0]
		self.CardNum = 0
		self.DrinkTea = 0
	
	def get_card(self, iCard):
		self.Card.append(iCard)
		self.Card.sort()
		self.ColorNum[iCard / 13] += 1
		self.CardNum += 1
	
	def lose_card(self, iCard):
		self.Card.remove(iCard)
		self.ColorNum[iCard / 13] -= 1
		self.CardNum -= 1
	
	def bid(self, CurrentBid):
		return ai_bid(self, CurrentBid)
	
	def play(self, CurrentPlay, iPier, GameGUI):
		PlayResult = ai_play(self, CurrentPlay, iPier)
		self.lose_card(PlayResult)
		return PlayResult
		
	def play_for_drink_tea(self, CurrentPlay, iPier, Mate, GameGUI):
		PlayResult = ai_play_for_drink_tea(self, CurrentPlay, iPier, Mate)
		Mate.lose_card(PlayResult)
		return PlayResult
	
class HumanPlayer(Player):
	
	def bid(CurrentBid):
		HighlightResult = -1
		while HighlightResult <= CurrentBid.Top:
			HighlightResult = GameGUI.highlight_quest(0)
		return HighlightResult:
	
	def play(self, CurrentPlay, iPier, GameGUI):
		HighlightLegal = 0
		while HighlightLegal == 0:
			HighlightIndex = GameGUI.highlight_quest(1)
			HighlightResult = self.Card[HighlightIndex]
			if self.ColorNum[CurrentPlay.JudgeColorHistory[iPier]] == 0 or HighlightResult / 13 == CurrentPlay.JudgeColorHistory[iPier]:
				HighlightLegal += 1
				GameGUI.highlight_to_green(1, HighlightIndex)
				if GameGUI.highlight_click_quest(1, HighlightIndex) == 0:
					HighlightLegal -= 1
					GameGUI.highlight_to_none(1, HighlightIndex)
			elif HightIndex != -1:
				GameGUI.highlight_to_red(1, HighlightIndex)
		self.lose_card(HighlightResult)
		return HighlightResult
		
	def play_for_drink_tea(self, CurrentPlay, iPier, Mate, GameGUI):
		HighlightLegal = 0
		while HighlightLegal == 0:
			HighlightIndex = GameGUI.highlight_quest(2)
			HighlightResult = Mate.Card[HighlightIndex]
			if Mate.ColorNum[CurrentPlay.JudgeColorHistory[iPier]] == 0 or HighlightResult / 13 == CurrentPlay.JudgeColorHistory[iPier]:
				HighlightLegal += 1
				GameGUI.highlight_to_green(2, HighlightIndex)
				if GameGUI.highlight_click_quest(2, HighlightIndex) == 0:
					HighlightLegal -= 1
					GameGUI.highlight_to_none(2, HighlightIndex)
			elif HightIndex != -1:
				GameGUI.highlight_to_red(2, HighlightIndex)
		Mate.lose_card(HighlightResult)
		return HighlightResult
	
class BidTable:
	
	def __init__(self):
		self.History = [[4, 4, 4, 4, 4] for x in range(6)]
		#4 for blank player
		self.Top = 0
	
	def add_bid(self, BidPlayer, BidResult):
		self.History[BidResult / 10][BidResult % 10] = BidPlayer
		self.Top = BidResult
		return [BidResult / 10, BidResult % 10, BidPlayer]

class PlayTable:
	
	def __init__(self, StartPlayer, aWinNum, aKingColor):
		self.CardHistory = [[52, 52, 52, 52] for x in range(13)]
		#52 for blank card
		self.StartPlayerHistory = [4 for x in range(13)]
		self.WinPlayerHistory = [4 for x in range(13)]
		#4 for blank player
		self.JudgeColorHistory = [4 for x in range(13)]
		#4 for blank color
		self.StartPlayerHistory[0] = StartPlayer
		self.WinNum = aWinNum
		self.KingColor = aKingColor
	
	def add_play(self, iPier, j, PlayResult):
		self.CardHistory[iPier][j] = PlayResult
		if j == 0:
			self.JudgeColorHistory[iPier] = PlayResult / 13
	
	def judge(self, iPier):
		JudgeCard = self.CardHistory[iPier]
		for x in JudgeCard:
			if x / 13 == self.KingColor:
				x += 200
			elif x / 13 == self.JudgeColorHistory[iPier]:
				x += 100
		WinPlayer = JudgeCard.index(max(JudgeCard))
		self.WinPlayerHistory[iPier] = WinPlayer
		if iPier < 12:
			self.StartPlayerHistory[iPier + 1] = WinPlayer
		
	def reverse(self, iPier):
		if iPier < 12
			self.StartPlayerHistory[iPier + 1] = 4
		self.WinPlayerHistory[iPier] = 4
		self.JudgeColorHistory[iPier] = 4
		self.CardHistory[iPier] = [52, 52, 52, 52]
	

#Program Start

GameGUI = TimeBridgeGUI()

WantToExit = 0
while WantToExit < 1:
	
	Players = [HumanPlayer(), Player(), Player(), Player()]
	#Create Players
	
	GetCardPlayer = 0
	for iCard in range(52):
		#(i % 13) is the number of the card i,  and (i / 13) is the color of the card i 
		while Players[GetCardPlayer].CardNum >= 13:
			GetCardPlayer = random.randint(0, 3)
		Players[GetCardPlayer].get_card(iCard)
	BackUpPlayers = Players
	GameGUI.deal_update(Players[0].Card)
	#Deal
	
	WantOldGame = 0
	while WantOldGame < 1:
	
		BidPlayer = random.randint(0, 3)
		CurrentBid = BidTable()
		PassNum = 0
		while PassNum < 3:
			BidResult = Players[BidPlayer].bid(CurrentBid)
			if BidResult == 0:
				PassNum += 1
			else:
				CurrentBid.add_bid(BidPlayer, BidResult)
				PassNum = 0
			GameGUI.bid_update(BidPlayer, BidResult)
			BidPlayer = (BidPlayer + 1) % 4
		Players[(BidPlayer + 2) % 4].DrinkTea = 1
		#Bid
	
		CurrentPlay = PlayTable((BidPlayer + 1) % 4, CurrentBid.Top / 10, CurrentBid.Top % 10)
		GameGUI.bid_to_play(CurrentBid.Top / 10, CurrentBid.Top % 10)
		iPier = 0
		while iPier < 13:
	
			for j in range(4):
				PlayPlayer = (j + CurrentPlay.StartPlayerHistory[iPier]) % 4
				if Players[PlayPlayer].DrinkTea == 1:
					PlayResult = Players[(PlayPlayer + 2) % 4].play_for_drink_tea(CurrentPlay, iPier, Players[PlayPlayer], GameGUI)
					GameGUI.player_bright_update(PlayPlayer, Players[PlayPlayer].Card)
				else:
					PlayResult = Players[PlayPlayer].play(CurrentPlay, iPier, GameGUI)
					if PlayPlayer == 0:
						GameGUI.player_bright_update(PlayPlayer, Players[PlayPlayer].Card)
					else:
						GameGUI.player_dark_update(PlayPlayer, Players[PlayPlayer].CardNum)
				GameGUI.play_table_update(iPier, j, PlayPlayer, PlayResult)
				if iPier == 0 and j == 0:
					GameGUI.player_bright_update((PlayPlayer + 1) % 4, Players[(PlayPlayer + 1) % 4].Card)
			CurrentPlay.judge(iPier)
			GameGUI.play_table_judge(iPier, CurrentPlay.WinPlayerHistory[iPier])
			#Play
		
			ReverseTo = -1
			while ReverseTo < 0:
			GameGUI.reverse_quest()
			if ReverseTo != 13: 
				while iPier >= ReverseTo:
					for j in range(4):
						PlayPlayer = (j + CurrentPlay.StartPlayerHistory[iPier]) % 4
						Players[PlayPlayer].get_card(CurrentPlay.CardHistory[iPier][j])
						if PlayPlayer == 0 or Players[PlayPlayer].DrinkTea == 1:
							GameGUI.player_bright_update(PlayPlayer, Players[PlayPlayer].Card)
						else:
							GameGUI.player_dark_update(PlayPlayer, Players[PlayPlayer].CardNum)
						if iPier == 0 and j == 0:
							GameGUI.player_dark_update((PlayPlayer + 1) % 4, Players[(PlayPlayer + 1) % 4].CardNum)
					CurrentPlay.reverse(iPier)
					GameUI.play_table_reverse(iPier)
					iPier -= 1
			#Reverse
		
			iPier += 1

		#Score
		#TODO
		
		CurrentBid = 0
		CurrentPlay = 0
		GameGUI.reset()
		WantOldGame = GameGUI.want_old_game_quest()
		if WantOldGame == 1:
			Players = BackUpPlayers
			GameGUI.deal_update(Players[0].Card)
		else:
			Players = 0
			WantToExit = GameGUI.want_to_exit_quest()
		#old game and exit