#!/usr/bin/env python3

from poker import Card, FrenchDeck
from collections import Counter

Suits = 'spades diamonds clubs hearts'.split()
Ranks = [str(n) for n in range(2, 11)] + list('JQKA')
RankMap = {rank:i+1 for i, rank in enumerate([str(n) for n in range(2, 11)] + list('JQKA'))} # function of rank mapped to number, greater the number the more valuable the card 2 => 1, K => 12, A => 13

def is_flush(cards):
    """This function check each players hand for flush and returns dictionary 
    of flush, highest card on flush and the suit"""
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
                #Find highest flush
                flush_rank.append(Ranks.index(card.rank))
        return {'flush':{'suit':flush_suit,'flush_cards':flush_cards,'High_flush_on':Ranks[max(flush_rank)]}}


def is_straight(cards):
    """This function check for straight and straight flush
    It returns highes straight flush if it exist, in case
    there is no straight flush, it will return highest straight if it exists"""
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
                if straight_flush==False:# Dont count straight if you have straight flush
                    straight={'High_straight_on':Ranks[sort_rank[card_index+4]]}
        card_index+=1
    return straight
#### ned to find a better way of creating an object for each hand with their rank and suit instead of creating the list each time for any of the define
#### defined function (i.e; for any of the is_straight, is_flush, number_of_kind I am recreating the list for ranking or suit) 
def number_of_kind(cards):
    "This function returns highes number of a kind anywhere between 2 to 4 if there is less than 2 of a kind it returns highes card"
    card_rank=[]
    for card in cards:
        card_rank.append(card.rank)
    rank_set=list(Counter(card_rank).keys())
    rank_repetition=list(Counter(card_rank).values())
    "getting numerical value of each rank for comparison"
    numeric_rank_set=[Ranks.index(r) for r in rank_set]
    max_repetition=max(rank_repetition)
    sort_rank=sorted(numeric_rank_set)
    kicker_card=list()
    if max_repetition==4:
        """Returns 4 of a kind and use remaining 1 card for kicker-card in case they have the same 
        4 of the kind"""
        
        "Find next highest card in case highest card is the same as 4 of a kind"
        if Ranks[sort_rank[-1]]==rank_set[rank_repetition.index(max_repetition)]:
            sort_rank.pop(-1)
        kicker_card.append(sort_rank[-1])
        return {'number_of_kind':4,'number_of_kind_on':rank_set[rank_repetition.index(max_repetition)],'kicker_card':kicker_card}
    elif max_repetition==3:
        "Getting the hishes 3 of the kinds in case we have to sets of three of the kind"        
        three_kind=[numeric_rank_set[i] for i in rank_repetition if i==3]
        assert len(three_kind)>2, "Can not have more than two sets of three of a kind"
        if len(three_kind)>1:
            high_three_card=max(three_kind)
        else:
            high_three_card=three_kind[0]
        counter=0
        while len(kicker_card)<2:
            "Going to next card if any of the two highest cards are the same as 3 of a kinds"
            if Ranks[sort_rank[-1-counter]]==high_three_card:
                sort_rank.pop(-1-counter)
            kicker_card.append(sort_rank[-1-counter])
        return {'number_of_kind':3,'number_of_kind_on':Ranks[high_three_card],'kicker_card':kicker_card}
    elif max_repetition==2:
        #need to check how many pairs we have and then select the highest two pairs if there are more than one.
        pair_rank=[]
        for repeat_index in range(len(rank_repetition)):
            if rank_repetition[repeat_index]==2:
                pair_rank_index=Ranks.index(rank_set[repeat_index])
                pair_rank.append(pair_rank_index)
        number_of_pairs=len(pair_rank)
        if number_of_pairs==1:
            counter=0
            while len(kicker_card)<3:
            "Going to next card if any of the three highest cards are the same as 3 of a kinds"
            if Ranks[sort_rank[-1-counter]]==rank_set[rank_repetition.index(max_repetition)]:
                sort_rank.pop(-1-counter)
            kicker_card.append(sort_rank[-1-counter])
            return {'number_of_kind':2,'number_of_pair':1,'number_of_kind_on':Ranks[pair_rank[0]],'kicker_card':kicker_card}
        elif number_of_pairs==2:
            counter=0
            while len(kicker_card)<1:
            "Going to next card if any of the highest cards are the same as 3 of a kinds"
            if Ranks[sort_rank[-1-counter]]==rank_set[rank_repetition.index(max_repetition)]:
                sort_rank.pop(-1-counter)
            kicker_card.append(sort_rank[-1-counter])            
            return {'number_of_kind':2,'number_of_pair':2,'number_of_kind_on':[Ranks[(pair_rank[i])] for i in range(2)],'sort_order':sorted(pair_rank),'kicker_card':kicker_card}
        else:
            assert number_of_pairs<4, "Can not have more than 3 pairs"
            pair_rank=sorted(pair_rank)
            #removing lowest pair
            pair_rank.pop(0)

        return {'number_of_kind':2,'number_of_pair':2,'number_of_kind_on':[Ranks[(pair_rank[i])] for i in range(2)]}
    else:
        return {}
            

    if len(cards)<5: 
        raise Exception("Need at least 5 cards to check for flush")
        return 0

    return 0
## need to add a function to pick the highest card
## need to add a logic if I have full house on a hand it ignores three of the kind
"returning hands scoure in terms of dictionary with their values being a list to make it easier to compare hand at the end"
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
    
    numb_of_kind=number_of_kind(cards)
    if numb_of_kind:
        print("\n\n\n******************************Congratulations**on number of kinds******************\n\n\n")
        print(numb_of_kind)

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