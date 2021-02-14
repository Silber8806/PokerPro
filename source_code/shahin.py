#!/usr/bin/env python3

from poker import Card, FrenchDeck
from collections import Counter

Suits = 'spades diamonds clubs hearts'.split()
Ranks = [str(n) for n in range(2, 11)] + list('JQKA')
RankMap = {rank:i+1 for i, rank in enumerate([str(n) for n in range(2, 11)] + list('JQKA'))} # function of rank mapped to number, greater the number the more valuable the card 2 => 1, K => 12, A => 13

def is_flush(cards):
    "This function check each players hand for flush and returns dictionary of flush and the suit"
    card_suit=list()
    for card in cards:
        card_suit.append(card.suit)
    card_suits_set=list(Counter(card_suit).keys())
    card_suits_counter=list(Counter(card_suit).values())
    if max(card_suits_counter)>=5:
        flush_count=max(card_suits_counter)
        flush_suit=card_suits_set[card_suits_counter.index(flush_count)]
        return {'flush':flush_suit}



def score_hand(cards):
    print("scoring: {}".format(cards))
    if (len(cards) != 7):
        raise Exception("Can only score 7 cards")
        return 0
    print("testing the score")
    if is_flush(cards):
        print("\n\n\n******************************Congratulations********************\n\n\n")
        print("This set of card is flash on ",flush_suit)
    else:
        print("no Flush")

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