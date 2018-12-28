from player import AIPlayer, HumanPlayer
from card import create_card
from enums import Position,Color
import random

f_card = open("AI_test_card.txt",'w')
FakeToRealNumber = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1]
RealToFakeNumber = [0, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
bidTableColor = []
bidTableNumber = []
for i in range(30):
    bidTableColor.append([])
    bidTableNumber.append([])
    for j in range(4):
        bidTableColor[i].append(0)
        bidTableNumber[i].append(0)

def getRandom(min, max):
    return random.randint(min, max)

def getPlayerCard(player, posString):
    f_card.writelines("Cards of :" + posString + '\n')
    #print(posString + " card:")
    #print("     Culb :", end=" ")
    f_card.writelines("     Culb : ")
    for cardNumber in range(13):
        if player.cards[cardNumber].color == Color.Club.value:
            #print(FakeToRealNumber[player.cards[cardNumber].number], end=" ")
            f_card.write(str(FakeToRealNumber[player.cards[cardNumber].number]) + ' ')
    f_card.write("\n")
    #print("")
    #print("     Diamond :", end=" ")
    f_card.writelines("     Diamond : ")
    for cardNumber in range(13):
        if player.cards[cardNumber].color == Color.Diamond.value:
            #print(FakeToRealNumber[player.cards[cardNumber].number], end=" ")
            f_card.write(str(FakeToRealNumber[player.cards[cardNumber].number]) + ' ')
    f_card.write("\n")
    #print(" ")
    #print("     Heart :", end=" ")
    f_card.writelines("     Heart : ")
    for cardNumber in range(13):
        if player.cards[cardNumber].color == Color.Heart.value:
            #print(FakeToRealNumber[player.cards[cardNumber].number], end=" ")
            f_card.write(str(FakeToRealNumber[player.cards[cardNumber].number]) + ' ')
    f_card.write("\n")
    #print(" ")
    #print("     Spade :", end=" ")
    f_card.writelines("     Spade : ")
    for cardNumber in range(13):
        if player.cards[cardNumber].color == Color.Spade.value:
            #print(FakeToRealNumber[player.cards[cardNumber].number], end=" ")
            f_card.write(str(FakeToRealNumber[player.cards[cardNumber].number]) + ' ')
    f_card.write("\n")
    #print('')

def getColorString(color):
    if color == Color.Club.value: return 'C'
    if color == Color.Diamond.value: return 'D'
    if color == Color.Heart.value: return 'H'
    if color == Color.Spade.value: return 'S'
    if color == Color.NoTrump.value: return 'NT'

def getNumberString(number):
    if number == 0: return 'pass'
    return str(number)

def getPosStr(po):
    if po == 0 : return 'North'
    if po == 1:  return 'West'
    if po == 2:  return 'South'
    if po == 3:  return 'East'

def bidTest0(north, west, south, east):
    f_bid0 = open('AI_test_bid0.txt','w')
    f_bid0.writelines('Bidding logs \n')
    f_bid0.writelines('     north        west        south       east \n')
    Round = 0
    ifEnd = False
    passTimes = 0
    BidColor = 0
    BidNumber = 0
    po = 0
    while ifEnd == False :
        player = north
        lastPlayer = east
        nextPlayer = west
        for p in range(4):
            if player.position == Position.North.value:
                lastPlayer = east
                nextPlayer = west
            elif player.position == Position.West.value:
                lastPlayer = north
                nextPlayer = south
            elif player.position == Position.South.value:
                lastPlayer = west
                nextPlayer = east
            elif player.position == Position.East.value:
                lastPlayer = south
                nextPlayer = north
            if player.position != Position.South.value:
                number, color = player.bid(last_bid_number = BidNumber,
                                        last_bid_color = BidColor,
                                        last_bid_player_position = None)

            else:
                number, color = 0, 0

            if number > 0:
                if (number > BidNumber):
                    BidNumber = number
                    BidColor = color
                    po = player.position
                elif (number == BidNumber and color > BidColor):
                    BidColor = color
                    BidNumber = number
                    po = player.position

            bidTableNumber[Round + 1][player.position] = number
            bidTableColor[Round + 1][player.position] = color
            coStr = getColorString(color)
            numStr = getNumberString(number)
            #print('position is '+str(player.position) + '  bid result is '+numStr + coStr + '    ')
            if number > 0:
                f_bid0.write('      '+numStr + coStr + '    ')
            else:
                f_bid0.write('      ' + numStr +  '    ')
            player = nextPlayer
            if number == 0:
                passTimes += 1
            else: passTimes = 0
            if passTimes >= 3:
                ifEnd = True
                break
        Round += 1
        f_bid0.write('\n')
    coStr = getColorString(BidColor)
    numStr = getNumberString(BidNumber)
    poStr = getPosStr(po)
    f_bid0.write('Result of bidding: ' + poStr + ' ' + numStr + coStr)
    f_bid0.close()
    return po, BidNumber, BidColor

def playTest(north, west, south, east, bankerPos, Trump):
    Round = 0
    thisRoundColor = 0
    maxNum = 0
    maxColor = 0
    if bankerPos == 0: winPlayer = north
    if bankerPos == 1: winPlayer = west
    if bankerPos == 2: winPlayer = south
    if bankerPos == 3: winPlayer = east

    southCardPlayed = []
    f_play = open('AI_test_play.txt','w')
    f_play.writelines('Playing logs , Trump is ' + getColorString(Trump) +'\n')
    for i in range(13):
        southCardPlayed.append(False)

    for r in range(13):
        f_play.writelines('Round ' + str(r) + ':  \n            ')
        if winPlayer == north: firstPlayer = west
        if winPlayer == west: firstPlayer = south
        if winPlayer == south: firstPlayer = east
        if winPlayer == east: firstPlayer = north
        if firstPlayer != south:
            playedCard = firstPlayer.play(last_played_number = None, last_played_color = None, order = 0, first_played_color = None)
        else:
            for c in range(13):
                if southCardPlayed[c] == False:
                    playedCard = firstPlayer.cards[c]
                    southCardPlayed[c] = True
                    break
        maxNum = FakeToRealNumber[playedCard.number]
        maxColor = playedCard.color
        thisRoundColor = playedCard.color
        winPlayer = firstPlayer
        coStr = getColorString(playedCard.color)
        numStr = getNumberString(FakeToRealNumber[playedCard.number])
        posStr = getPosStr(firstPlayer.position)
        f_play.write('(' + posStr + ')' + numStr + coStr + '  ,   ')


        for p in range(firstPlayer.position + 1, firstPlayer.position + 4):
            po = p % 4
            if po == 0: thisPlayer = north
            if po == 1: thisPlayer = west
            if po == 2: thisPlayer = south
            if po == 3: thisPlayer = east
            if thisPlayer != south:
                playedCard = thisPlayer.play(last_played_number=None,
                                              last_played_color=None,
                                              order=p - firstPlayer.position,
                                              first_played_color=thisRoundColor)
            else:
            #South出牌
                 hasThisColor = False
                 for c in range(13):
                     if (southCardPlayed[c] == False and thisPlayer.cards[c].color == thisRoundColor):
                        playedCard = thisPlayer.cards[c]
                        southCardPlayed[c] == True
                        hasThisColor = True
                        break
                 if hasThisColor == False:
                     for c in range(13):
                         if (southCardPlayed[c] == False):
                             playedCard = thisPlayer.cards[c]
                             southCardPlayed[c] == True
            coStr = getColorString(playedCard.color)
            numStr = getNumberString(FakeToRealNumber[playedCard.number])
            posStr = getPosStr(thisPlayer.position)
            f_play.write('(' + posStr + ')' + numStr + coStr + '  ,   ')
            if (playedCard.color == maxColor and FakeToRealNumber[playedCard.number] > maxNum):
                maxColor = playedCard.color
                maxNum = FakeToRealNumber[playedCard.number]
                winPlayer = thisPlayer
            elif (playedCard.color == Trump and maxColor != Trump):
                maxColor = playedCard.color
                maxNum = FakeToRealNumber[playedCard.number]
                winPlayer = thisPlayer
        f_play.write('    Winner is ' + getPosStr(winPlayer.position) + '\n')
    f_play.close()

if __name__ == '__main__':


    pokerCard = []
    c = []
    for co in range(4):
        pokerCard.append([])
        for num in range(13):
            pokerCard[co].append(True)


    east = AIPlayer(Position.East.value)
    north = AIPlayer(Position.North.value)
    west = AIPlayer(Position.West.value)
    south = HumanPlayer(Position.South.value)

    #card for north
    for cardNumber in range(13):
        co = getRandom(0,3)
        num = getRandom(0,12)
        while pokerCard[co][num] != True:
            co = getRandom(0, 3)
            num = getRandom(0, 12)
        aCard = create_card(co, num)
        north.get_card(aCard)
        pokerCard[co][num] = False

    # card for west
    for cardNumber in range(13):
        co = getRandom(0,3)
        num = getRandom(0,12)
        while pokerCard[co][num] != True:
            co = getRandom(0, 3)
            num = getRandom(0, 12)
        aCard = create_card(co, num)
        west.get_card(aCard)
        pokerCard[co][num] = False

    # card for east
    for cardNumber in range(13):
        co = getRandom(0,3)
        num = getRandom(0,12)
        while pokerCard[co][num] != True:
            co = getRandom(0, 3)
            num = getRandom(0, 12)
        aCard = create_card(co, num)
        east.get_card(aCard)
        pokerCard[co][num] = False

    # card for south
    for cardNumber in range(13):
        co = getRandom(0,3)
        num = getRandom(0,12)
        while pokerCard[co][num] != True:
            co = getRandom(0, 3)
            num = getRandom(0, 12)
        aCard = create_card(co, num)
        south.get_card(aCard)
        pokerCard[co][num] = False

    east.init_AI()
    west.init_AI()
    north.init_AI()
    south.init_AI()

    getPlayerCard(north, 'north')
    getPlayerCard(west, 'west')
    getPlayerCard(south, 'south')
    getPlayerCard(east, 'east')
    f_card.close()

    #bidding test
    bankerPos, BidNumber, Trump = bidTest0(north, west, south, east)

    #playing test
    playTest(north, west, south, east, bankerPos, Trump)

