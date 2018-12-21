# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 10:02:59 2018
AI based on Bridge Experience
@author: hanyl
"""

from card import Card
#from model import Model
#from player import AIplayer
#常量定义
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


class CTC(object):
    """
    牌表map的value,可扩充内容
    """
    def __init__(self,Player):
        self.Player = Player #可取值-1，0，1，2，3，分别表示OutHand,Declarer……情况

class AIplay(object):
    def __init__(self):
        self.CardTable={} #字典的形式实现,key为Card类型，value为CTC
        self.CardNumTable=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]] #[player][color],记录实际的张数，>=0时对其他人不可见
                                                            #可以取值<0,表示该门已经垫了多少张/该门已经无牌，对外可见
        self.CardsNow={} #map，key=Card,value=int,初始值为0,存储当前玩家手上有的牌，value>0,表示该牌可出
        self.PlayerNow=NullPlayer    #当前玩家的身份，可取枚举值0，1，2，3
        self.TrickLeadingColors={}   #记录每一轮的LeadingColor，map,（轮数，花色）
        self.TrickLeadingColors[-1]=NullColor 
        self.TrickLeadingColor=NullColor
        self.LastTrickLeadingColor=NullColor
        self.TrickNow=0 #当前的轮数，取值0-12
        self.FirstCard=NullCard
        self.SecondCard=NullCard
        self.ThirdCard=NullCard #本轮出的前三张牌
        #self.TrickCards=[self.FirstCard,self.SecondCard,self.ThirdCard]
        self.DeclarerM=NullPlayer #表示庄家在Model模块中的位置
        self.TrickPosition=0 #取值1，2，3，4表示当前几号位出牌
        self.CardReturn=NullCard
        self.Trump=NullColor #本局主色
        #self.ReturnNum=NullNum
        #self.ReturnColor=NullColor
        
        
    def setCardTable(self,Model):
        """
        叫完牌后，打牌之前调用一下
        初始化CT,CNT，DeclarerM等信息
        """
        self.DeclarerM=(Model.win_bid_position)%4  #win_bid_position is int ，win_bid_position先假定为庄家
                                                    #需要model里存一个庄家的位置！！！
        self.OpenLeadingM=(self.DeclarerM-1)%4
        self.DummyM=(self.DeclarerM-2)%4
        self.OPMateM=(self.DeclarerM-3)%4 
        #确定各角色在Modelplayer里的调用位置，接口,与enums中定义的玩家方位有关
        for player in Players:
            for card in Model.players[(self.DeclarerM-player) % 4].cards:  #-/+与enums中定义的玩家方位的转向（逆、顺）有关
                self.CardTable[card] = CTC(player)
            for color in Colors:
                self.CardNumTable[player][color] = Model.players[(self.DeclarerM-player) % 4].color_num[color]
        
    #下面的函数是从Model中获取信息的接口
    def getColorInfo(self,Model):
        if Model.king_color is not None:
            self.Trump= Model.king_color
        else:
            self.Trump = NullColor
        if self.TrickPosition is not 1:    #当前玩家几号位出牌
            self.TrickLeadingColors[self.TrickNow]=Model.first_played_color
        else:
            self.TrickLeadingColors[self.TrickNow]=NullColor#一号位玩家所引花色
        self.TrickLeadingColor=self.TrickLeadingColors[self.TrickNow]
        self.LastTrickLeadingColor=self.TrickLeadingColors.get(self.TrickNow-1,NullColor)
        
    def getCardInfo(self,Model):
        if self.TrickPosition is 4:
            self.ThirdCard = Model.pie_history[(Model.current_player_position+1)%4]
            self.SecondCard = Model.pie_history[(Model.current_player_position+2)%4]
            self.FirstCard = Model.pie_history[(Model.current_player_position+3)%4]
        elif self.TrickPosition is 3:
            self.SecondCard = Model.pie_history[(Model.current_player_position+1)%4]
            self.FirstCard = Model.pie_history[(Model.current_player_position+2)%4]
        elif self.TrickPosition is 2:
            self.FirstCard = Model.pie_history[(Model.current_player_position+1)%4]
        if Model.current_player is not None:
            for card in Model.current_player.cards:
                self.CardsNow[card]=0
            
    
    def Position(self,P_P,P_D):
        """
        由庄家位置、当前位置计算当前玩家的角色
        """
        if P_P is P_D:
            return Declarer
        elif P_P is (P_D+2)%4:
            return Dummy
        elif P_P is (P_D+1)%4:
            return OLMate
        return OL
    
    def getTrickHistory(self,Model):
        if Model.play_order is None:
            self.TrickPosition=1
        else:
            self.TrickPosition=Model.play_order+1 #出牌位置
        if Model.pie is not None:
            self.TrickNow=Model.pie #当前是第几轮
        self.PlayerNow=self.Position(Model.current_player_position,self.DeclarerM) #当前玩家的角色
        self.getColorInfo(Model)
        self.getCardInfo(Model)
        self.ReturnNum = NullNum
        self.ReturnColor = NullColor #置零
    
    def refT(self,card,LC): #根据card的情况，更新CT和CNT;
        player = self.CardTable[card].Player
        if player is not OutHand:
            self.CardNumTable[player][Card(card).color]-=1
            if Card(card).color is not LC:
                self.CardNumTable[player][LC]-=1
            self.CardTable[card].Player = OutHand
    
    def refreshCardTable(self,Model):
        """
        根据上轮和本轮的出牌更新CardTable以及CardNumTable;
        在前者信息变动的时候，同时更新后者，
        CNT存储了每个角色的牌的数量，当实际发生出牌时，数量减一；
            当本门没有换出其他花色时，可以达到负值，表示本门已经垫出几张牌；当小于0时，表明为所有人可知的信息
        """
        if self.TrickNow is not 0:
            for player in Positions:
                self.refT(Model.play_table.history[self.TrickNow-1][player],self.LastTrickLeadingColor)
        if self.TrickPosition > 3:
            self.refT(self.ThirdCard,self.TrickLeadingColor)
        if self.TrickPosition > 2:
            self.refT(self.SecondCard,self.TrickLeadingColor)
        if self.TrickPosition > 1:
            self.refT(self.FirstCard,self.TrickLeadingColor)             
        
    def playPrepare(self,Model):
        """
        调用上述四个获取历史信息，得到所有本轮出牌需要的信息
        更新CT,CNT
        """
        self.getTrickHistory(Model)
        self.refreshCardTable(Model)
        
    #牌的信息，接口函数
    def gCard(self,color,number): #由Color,Number生成Card对象
        return Card(color*13+number)

    #获取牌信息的函数
    #主要使用的是 cardsNum,haveCard,haveCardOut 
    def KnowElsePlayers(self,player,color):
        for p in Players: #若有一人牌打完了，且大家都知道，且不是明手，那么就知道剩余一人的牌
            if self.CardNumTable[p][color] < 0 and p is not self.PlayerNow and p is not Dummy:
                return True
        return False
    
    def OutColorNum(self,player,color):
        ocn = 0
        for c in Colors: #若其他花色都打完了
            if c is not color and self.CardNumTable[player][c]< 0:
                ocn+=1
        return ocn
    
    def cardsNumG(self,player,color): #上帝视角God
        n = self.CardNumTable[player][color]
        if n<0:
            return 0
        return n
    
    def cardsNum(self,player,color):
        """
        return 某玩家player某种花色color的牌的数量
                >=0的返回值表示结果，-1表示不知道
        """
        if player is self.PlayerNow: #自己的牌自己知道
            return self.cardsNumG(player,color)
        if player is Dummy: #明手的牌都知道
            return self.cardsNumG(player,color)
        if player is Declarer and self.PlayerNow is Dummy: #Dummy知道Declarer的牌
            return self.cardsNumG(player,color)
        if self.CardNumTable[player][color]<0: #如果是出完了 大家也知道
            return 0
        if self.KnowElsePlayers(player,color): #知道其余三人的情况,那也能推知剩余一人的情况
            return self.CardsNumG(player,color)
        if self.OutColorNum(player,color)>=3:  #如果其他三门都出完了，大家也知道
            return self.cardsNumG(player,color)
        return -1 #表示不知道

    def haveCardG(self,player,card):#上帝视角God
        if self.CardTable[card].Player is player:
            return True
        return False
    
    def haveCard(self,player,card):
        """
        return 判断某玩家player有无某张牌card
        1,0,-1 分别表示有，无，不知道
        """
        if player is self.PlayerNow: #自己的牌自己知道
            return self.haveCardG(player,card)
        if player is Dummy: #Dummy的牌都知道
            return self.haveCardG(player,card)
        if player is NullPlayer:
            return 0
        if self.PlayerNow is Dummy and player is Declarer: #Dummy知道Declarer的牌
            return self.haveCardG(player,card)
        if self.CardNumTable[player][card.color]<0: #如果是出完了 大家也知道
            return False
        if self.KnowElsePlayers(player,card.color): #知道其余三人的情况,那也能推知剩余一人的情况
            return self.haveCardG(player,card)
        if self.OutColorNum(player,card.color)>=3: #知道本人其余门的情况，能推知该门的情况
            return self.haveCardG(player,card)
        return -1
    
    def haveCardOut(self,card):
        if self.CardTable[card].Player is OutHand:
            return True
        else:
            return False

    def AvailableCards_1(self): #首先判断可出的牌，在CardsNow中赋值为1
        ccn = 0 #本轮可以出的牌数
        if self.TrickPosition > 1: #被动出牌玩家
            for card in list[self.CardsNow.keys()]:#遍历所有的牌
                if card.color is self.TrickLeadingColor:
                    self.CardsNow[card] += 1
                    ccn += 1
        if ccn is 0: #包含两种情况，1.是首引玩家 2.是被动玩家，但没有同花色
            for card in list[self.CardsNow.keys()]:
                self.CardsNow[card]+=1 #所有的牌都加1
                
      #添加其他规则！让你的AI更智能！
     
    def CardSelect(self):
        """
        给CardsNow中的Card赋值,值大于1，代表该牌合法，值越大代表这张牌更适合现在的情况，最后对CardsNow中的card进行排序，输入最大的一个
        主要的逻辑：将桥牌经验总结成规则，放入CardSelect的if分支中，可以通过对累加值进行调整实现优先级
        """
        #首先判断可出的牌，在CardsNow中赋值为1,_1代表第一条规则
        self.AvailableCards_1()
        #添加其他规则!!DIY!!
            
    
    def CardGet(self):
        self.CardReturn=sorted(self.CardsNow.items(),key=lambda v:v[-1],reverse=1)[0][0]  #按value从大到小排序，取其key
        self.CardsNow = {} #字典置零
        
    
    def Play(self,Model):
        self.PlayPrepare(Model)
        self.CardSelect()
        self.CardGet()
        return self.CardReturn

    def reset(self): #只在需要回溯或者最终的时候调用，平时的记录是连续的
        self.CardTable={} #字典的形式实现,key为Card类型，value为CTC
        self.CardNumTable=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]] #[player][color],记录实际的张数，>=0时对其他人不可见
                                                            #可以取值<0,表示该门已经垫了多少张/该门已经无牌，对外可见
        self.CardsNow={} #map，key=Card,value=int,初始值为0,存储当前玩家手上有的牌，value>0,表示该牌可出
        self.PlayerNow=NullPlayer    #当前玩家的身份，可取枚举值0，1，2，3
        self.TrickLeadingColors={}   #记录每一轮的LeadingColor，map,（轮数，花色）
        self.TrickLeadingColors[-1]=NullColor 
        self.TrickLeadingColor=NullColor
        self.LastTrickLeadingColor=NullColor
        self.TrickNow=0 #当前的轮数，取值0-12
        self.FirstCard=NullCard
        self.SecondCard=NullCard
        self.ThirdCard=NullCard #本轮出的前三张牌
        #self.TrickCards=[self.FirstCard,self.SecondCard,self.ThirdCard]
        self.DeclarerM=NullPlayer #表示庄家在Model模块中的位置
        self.TrickPosition=0 #取值1，2，3，4表示当前几号位出牌
        self.CardReturn=NullCard
        self.Trump=NullColor

