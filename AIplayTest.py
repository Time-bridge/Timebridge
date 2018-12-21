# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 15:57:11 2018
AI based on Bridge Experience
AIplay Test

@author: hanyl
"""

from model import Model
from AIplay import AIplay,CTC
from random import shuffle

NullCTC=CTC(-1)

def Deal(M,N,w,x): 
    """
    发牌程序,Model,N:发牌方式，w:庄家位置，x:发几张牌
    """
    n = N  #只要取N与52互质，则能正好每人13张
    M.win_bid_position = (w)%4 #定义庄家的位置,win_bid_position是Dummy
    for i in range(4):
        for j in range(x):
            n=(n+N)%52
            M.players[i].get_card(Card(n))

def TestSetF(AI,M):
    """
    测试setCardTable(self,Model):在初始化发牌后，52张牌很好
    """
    CNT=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
    for w in Positions:
        N = 1
    #for N in [1,3,5,7,9,11,15,17,19,21,23,25,27,29]:
        Deal(M,N,w,13)   #发牌
        AI.setCardTable(M)  #set函数检验
        for c in Colors:
            for n in Nums:
                ctc = AI.CardTable.get(c*13+n,NullCTC) 
                if ctc is not NullCTC:
                    CNT[ctc.Player][c]+=1 #牌表
        tn=0
        for p in Players:
            for c in Colors:
                if AI.CardNumTable[p][c] is CNT[p][c]:
                    tn+=1
                    #牌张表
        print(tn,end=' ')
        print(CNT,end=' ')
        CNT=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
        AI.reset()
        M.reset()
        print("for N=",N)
    
def TestGetHF(AI,M):
    M.king_color = Club #方块
    M.play_order=2 #第几个出牌
    M.first_played_color=Diamond #梅花
    M.current_player_position=South #
    M.pie=5 #第6轮,已完成5轮
    for i in Positions:
        M.pie_history[i]=i+18
    M.current_player_position=2
    for i in range(M.pie):
        AI.TrickLeadingColors[i]=0 #之前的记录
        pie={0:0,1:1,2:2,3:3,'win':3}
        M.play_table.history.append(pie)
    for i in range(4):
        AI.CardTable[i]=CTC(AI.Position(i,DeclarerP))#伪造一个CardTable的前四项
        print(AI.CardTable[i].Player,end=' ')
    print()
    AI.CardTable[18]=CTC(-1)
    AI.CardTable[21]=CTC(-1)
    AI.getTrickHistory(M)
    TGHFPrint(AI,1)#打印结果函数
    print(AI.CardNumTable)
    AI.refreshCardTable(M)
    print(AI.CardNumTable)
    
    
    
    
def TGHFPrint(AI,bl=1):
    if bl:    
        print("AI.TrickPosition ",AI.TrickPosition) #=player_order+1
        print("AI.TrickLeadingColor ",AI.TrickLeadingColor) #first_played_color
        print("AI.LastTrickLeadingColor ",AI.LastTrickLeadingColor)
        print("AI.LeadingColors",AI.TrickLeadingColors)
        print("AI.TrickNow ",AI.TrickNow)#pie
        print("AI.PlayerNow ",AI.PlayerNow)#
        print("AI.Card ",AI.FirstCard,AI.SecondCard,AI.ThirdCard)
    

def AIPlaySet(AI):
    #发牌
    N = 52-12
    x=[i for i in range(N)]
    shuffle(x)
    for i in range(N):
        card = x[i]
        player = i%4
        color = int(card/13)
        AI.CardTable[card]=CTC(player)
        AI.CardNumTable[player][color]+=1
    for c in range(N,52):
        AI.CardTable[c]=CTC(NullPlayer) 
    for c in Colors:
        for n in Nums:
            print(AI.CardTable[AI.gCard(c,n)].Player,end=' ')
        print()
    for p in Players:
        print(AI.CardNumTable[p])
    ''' #cardsNumG(p,c)
    for p in Players:
        for c in Colors:
            print(AI.cardsNumG(p,c),end=' ')
        print()
    '''
    ''' #haveCardG(c,p)
    for c in range(N):
        print(AI.haveCardG(AI.CardTable[c].Player,c),end=' ')
    '''
    
    AI.PlayerNow = Declarer
    player = Declarer
    for c in range(N):
        print(AI.haveCard(AI.CardTable[c].Player,Card(c)),end=' ')
    
    


if __name__ == '__main__':
    AI =AIplay()
    #M = Model()
    #TestSetF(AI,M)  #检验setCardTable函数
    
    '''   #检验GetHistory,refreshCardTable函数
    DeclarerP = South #庄家位置，
    N = 5  #发牌因子
    Deal(M,N,DeclarerP,8) 
    AI.setCardTable(M)
    TestGetHF(AI,M)
    '''
    AIPlaySet(AI)
    
    
    