#!/usr/bin/env python3

from poker import Card, FrenchDeck
from collections import Counter

Suits = 'spades diamonds clubs hearts'.split()
Ranks = [str(n) for n in range(2, 11)] + list('JQKA')
RankMap = {rank:i+1 for i, rank in enumerate([str(n) for n in range(2, 11)] + list('JQKA'))} # function of rank mapped to number, greater the number the more valuable the card 2 => 1, K => 12, A => 13

def is_flush(cards):
    "This function check each players hand for flush and returns dictionary of flush and the suit"
    if len(cards)<5: 
        raise Exception("Need at least 5 cards to check for flush")
        return 0
    card_suit=[]
    for card in cards:
        card_suit.append(card.suit)
    card_suits_set=list(Counter(card_suit).keys())
    card_suits_counter=list(Counter(card_suit).values())
    if max(card_suits_counter)>=5:
        flush_count=max(card_suits_counter)
        flush_suit=card_suits_set[card_suits_counter.index(flush_count)]
        flush_cards=[]
        flush_rank=[]
        for card in cards:
            if card.suit==flush_suit:
                flush_cards.append(card)
                #Find highes flush
                flush_rank.append(Ranks.index(card.rank))
        return {'flush':{'suit':flush_suit,'flush_cards':flush_cards,'High_flush_on':Ranks[max(flush_rank)]}}


def is_straight(cards):
    #"This function check for straight and straight flush"
    #"It returns highes straight flush if it exist, in case there is no straight flush, it will return highest straight if it exists"
    straight_flush=False
    straight={}
    card_rank=[]
    card_suit=[]
    for card in cards:
        card_rank.append(Ranks.index(card.rank))
        card_suit.append(card.suit)
    sort_rank=sorted(set(card_rank))
    print('sorted ranking is=',sort_rank)
    #check for lowest possible rank with Ace counting as 1
    if max(sort_rank)==12:
        if sort_rank[3]==3:
            straight_cards=[]
            for card in cards:
                if Ranks.index(card.rank) in [0,1,2,3,12]:
                    straight_cards.append(card)
            print('straight_cards hand is=', straight_cards)
            if is_flush(straight_cards):
                straight_flush=True
                straight={'straigh_flush':{'suit':is_flush(straight_cards)['flush']['suit'],'High_straight_on':5}}
            else: 
                straight={'High_straight_on':5}

    #iterating over each set of card with 5cards to check for straight
    card_index=0
    while len(sort_rank)-card_index>=5:
        #checking if we have straight flush or not.
        if sort_rank[card_index+4]-sort_rank[card_index]==4:
            straight_cards=[]
            for card in cards:
                if Ranks.index(card.rank) in sort_rank[card_index:card_index+5]:
                    straight_cards.append(card)
            print('straight_cards hand is=', straight_cards)
            if is_flush(straight_cards):
                straight_flush=True
                straight={'straigh_flush':{'suit':is_flush(straight_cards)['flush']['suit'],'High_straight_on':Ranks[sort_rank[card_index+4]]}}
            else: 
                if straight_flush==False:# Dont count straight if you had straight flush
                    straight={'High_straight_on':Ranks[sort_rank[card_index+4]]}
        card_index+=1
    return straight


    

    if len(cards)<5: 
        raise Exception("Need at least 5 cards to check for flush")
        return 0

    return 0


def score_hand(cards):
    print("scoring: {}".format(cards))
    if (len(cards) != 7):
        raise Exception("Can only score 7 cards")
        return 0
    print("testing the score")
    if is_flush(cards):
        print("\n\n\n******************************Congratulations**flush******************\n\n\n")
        print("This set of card is flash on ",is_flush(cards))
    else:
        print("no Flush")
    straight=is_straight(cards)
    if straight:
        if 'straight_flush' in straight.keys():
            print("\n\n\n******************************Congratulations**straight**flush****************\n\n\n")
            print("This set of card is flash on ",straight['straight_flush']['suit'],"and straight high on",straight['straight_flush']['High_straight_on'])
        else:
            print("\n\n\n******************************Congratulations**straight******************\n\n\n")
            print("This set of card is high straight on ",straight['High_straight_on'])

if __name__ == '__main__':
    '''
    print("Possible Suites")
    print(Suits)
    print("Possible Ranks")
    print(Ranks)

    print("How to create a Card")
    new_card = Card(rank='A',suit='spades')
    print(new_card)

    print("You can get the strength of a rank using rank map")
    for rank in Ranks:
        print("{} is mapped to {}".format(rank,RankMap[rank]))

    print("You can create hands here that are random for testing purposes")
    '''
    deck = FrenchDeck()
    for hand in deck.permute(7,10):
        print(hand)
        #delete this later added for test
        print(score_hand(hand))
        last_hand = hand

    '''
    print("switching last hand to hand for exercise")
    hand = last_hand

    print("implement the following:")
    print(score_hand(hand))

    print("should say if it's a straight, double, triple etc or maybe a rank!")
'''