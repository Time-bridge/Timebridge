# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 13:22:05 2018

@author: hanyl
"""
import unittest
import random
from AIplay import AIplay,CTC
from card import Card
from model import Model

NullColor,Club,Diamond,Heart,Spade=-1,0,1,2,3
OutHand,NullPlayer,Declarer,OL,Dummy,OLMate=-1,-1,0,1,2,3
North,West,South,East = 0,1,2,3
#Declarer_p,OL_p,OLMate_p=0,1,2
Colors=[Club,Diamond,Heart,Spade]
Players=[Declarer,OL,Dummy,OLMate]
Positions=[North,West,South,East]
Cards=range(52)
#Players_p=[Declarer_p,OL_p,OLMate_p]
Nums=range(13)
NullNum=-1
NullCard=Card(-1)
NullCTC=CTC(-1)


class AIplaytest_self(unittest.TestCase):
    def setUp(self):
        self.AI = AIplay()
        x = [i for i in range(52)]
        random.shuffle(x)  #发牌
        for i in range(52):
            card = x[i]
            player = int(i/13)
            color = int(card/13)
            self.AI.CardTable[card]=CTC(player)
            self.AI.CardNumTable[player][color]+=1 #把CT、CNT的内容写好
        
        
        Trick = 2   #墩数,可调整
        for t in range(Trick):
            c = random.choice(Colors)  #假设每一敦的主花色是这么随机选的
            for p in Players:
                for i in range(4):
                    self.AI.CardNumTable[p][(c+i)%4]-=1 #先把这个花色的牌出一张
                    if self.AI.CardNumTable[p][(c+i)%4] >= 0: #如果有就退出，否则换下一个花色
                        for card in Cards:
                            if int(card/13) is (c+i)%4 and self.AI.CardTable[card].Player is p:
                                self.AI.CardTable[card].Player = OutHand
                                break
                        break
                   
        '''       
        for c in Colors:
            for n in Nums:
                print(AI.CardTable[AI.gCard(c,n)].Player,end=' ')
            print()
        for p in Players:
            print(AI.CardNumTable[p])
        '''
        
    
    def tearDown(self):
        self.AI.reset()
    
    def testgCard(self):
        Cs=[]
        Cts=[]
        for c in Cards:
            Cs.append(Card(c))
        for c in Colors:
            for n in Nums:
                Cts.append(self.AI.gCard(c,n))
        self.assertEqual(Cs, Cts, 'test gCard fail')
    
    def testKnowElsePlayer(self):
        r = []
        for i in range(4):
            rj=[]
            for j in range(4):
                rk=[]
                for k in range(4):
                    rk.append(True)
                rj.append(rk)
            r.append(rj)
        for self.AI.PlayerNow in Players:
            for p in Players:
                for c in Colors:
                    r[self.AI.PlayerNow][p][c]=self.AI.KnowElsePlayers(p,c)
        print("Know else player.")
        for p1 in Players:
            for p2 in Players:
                print(r[p1][p2])
            print()
        print("Players NumTable")
        for p in Players:
            print(self.AI.CardNumTable[p])
    
    def testOutColorNum(self):
        t =[]
        for i in range(4):
            tj=[]
            for j in range(4):
                tj.append(0)
            t.append(tj)
        for p in Players:
            for c in Colors:
                t[p][c]=self.AI.OutColorNum(p,c)
        print("OutColorNum")
        for p in Players:
            print(t[p])
        print("Players NumTable")
        for p in Players:
            print(self.AI.CardNumTable[p])

    def testcardsNumG(self):
        t =[]
        for i in range(4):
            tj=[]
            for j in range(4):
                tj.append(0)
            t.append(tj)
        for p in Players:
            for c in Colors:
                t[p][c]=self.AI.cardsNumG(p,c)
        print("CardsNumG")
        for p in Players:
            print(t[p])
        print("Players NumTable")
        for p in Players:
            print(self.AI.CardNumTable[p])
        
    
    def testcardsNum(self):
        r = []
        for i in range(4):
            rj=[]
            for j in range(4):
                rk=[]
                for k in range(4):
                    rk.append(True)
                rj.append(rk)
            r.append(rj)
        for self.AI.PlayerNow in Players:
            for p in Players:
                for c in Colors:
                    r[self.AI.PlayerNow][p][c]=self.AI.cardsNum(p,c)
        print("cardsNum:")
        for p1 in Players:
            for p2 in Players:
                print(r[p1][p2])
            print()
        print("Players NumTable:")
        for p in Players:
            print(self.AI.CardNumTable[p])
    
    def testhaveCardG(self):
        print("haveCardG_GOD_TRUE:")
        for c in Colors:
            for n in Nums:
                print(self.AI.CardTable[self.AI.gCard(c,n)].Player,end=' ')
            print()
        print("haveCardG:")
        t =[]
        for i in range(4):
            tj=[]
            for j in range(52):
                tj.append(0)
            t.append(tj)
        for p in Players:
            for c in Colors:
                for n in Nums:
                    if(self.AI.haveCardG(p,self.AI.gCard(c,n))):
                        print(p,end=' ')
                    else:
                        print("*",end=' ')
                print()
            print()
        print("Players NumTable:")
        for p in Players:
            print(self.AI.CardNumTable[p])
        t =[]
        for i in range(4):
            tj=[]
            for j in range(4):
                tj.append(0)
            t.append(tj)    
        for c in Cards:
            if self.AI.CardTable[c].Player is not OutHand:
                t[self.AI.CardTable[c].Player][int(c/13)]+=1
        for p in Players:
            print(t[p])
    
    def testhaveCard(self):
        print("haveCardG_GOD_TRUE:")
        for c in Colors:
            for n in Nums:
                print(self.AI.CardTable[self.AI.gCard(c,n)].Player,end=' ')
            print()
        print("Players NumTable:")
        for p in Players:
            print(self.AI.CardNumTable[p])
        print("haveCard:")
        t =[]
        for i in range(4):
            tj=[]
            for j in range(52):
                tj.append(0)
            t.append(tj)
        for self.AI.PlayerNow in Players:
            for p in Players:
                for c in Colors:
                    for n in Nums:
                        if self.AI.haveCard(p,self.AI.gCard(c,n)) is -1:
                            print("*",end=' ')
                        elif self.AI.haveCard(p,self.AI.gCard(c,n)) is True:
                            print("1",end=' ')
                        else:
                            print("0",end=' ')
                    print()
                print()
        
    
    def testhaveCardOut(self):
        print("haveCardG_GOD_TRUE:")
        for c in Colors:
            for n in Nums:
                print(self.AI.CardTable[self.AI.gCard(c,n)].Player,end=' ')
            print()
        Cs=[]
        for ca in Cards:
            Cs.append(self.AI.haveCardOut(ca))
        kt = 0
        print("haveCardOut")
        for c in Colors:
            for n in Nums:
                if (Cs[self.AI.gCard(c,n)]):
                    kt+=1
                    print("-1",end=' ')
                else:
                    print("*",end=' ')
            print()
        print("kt=",kt)
    
    def testAvailableCards_1(self):
        pass
    """
        for self.AI.TrickLeadingColor in Colors:
            for self.AI.TrickPosition in range(1,5): 
                for self.AI.PlayerNow in Players:
                    self.AI.AvailableCards_1()
                    print("AvailableCardsList:",self.AI.TrickLeadingColor," ",self.AI.TrickPosition)
                    print(self.AI.CardsNow)
                    print()
                    """
        
    
    def testCardSelect(self):
        pass
    """
        for self.AI.TrickLeadingColor in Colors:
            for self.AI.TrickPosition in range(1,5): 
                for self.AI.PlayerNow in Players:
                    self.AI.CardSelect()
                    print("AfterCardSelect:",self.AI.TrickLeadingColor," ",self.AI.TrickPosition)
                    print(self.AI.CardsNow)
                    print()
                    """
    
    def testCardGet(self):
        for self.AI.TrickLeadingColor in Colors:
            for self.AI.TrickPosition in range(1,5): 
                for self.AI.PlayerNow in Players:
                    self.AI.CardSelect()
                    print("CardGet:",self.AI.TrickLeadingColor," ",self.AI.TrickPosition)
                    print(self.AI.CardsNow,end=" ")
                    self.AI.CardGet()
                    print(self.AI.CardReturn)
                    print()
        


if __name__ =='__main__':

    unittest.main()   
    
    
    
    
    
    
