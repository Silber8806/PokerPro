#!/usr/bin/env python3

from poker import Card, FrenchDeck

Suits = 'spades diamonds clubs hearts'.split()
Ranks = [str(n) for n in range(2, 11)] + list('JQKA')
RankMap = {rank:i+1 for i, rank in enumerate([str(n) for n in range(2, 11)] + list('JQKA'))} # function of rank mapped to number, greater the number the more valuable the card 2 => 1, K => 12, A => 13

def score_hand(cards):
    print("scoring: {}".format(cards))
    if (len(cards) != 7):
        raise Exception("Can only score 7 cards")
    return 0

if __name__ == '__main__':
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
    deck = FrenchDeck()

    for hand in deck.permute(7,3):
        print(hand)
        last_hand = hand

    print("switching last hand to hand for exercise")
    hand = last_hand

    print("implement the following:")
    print(score_hand(hand))

    print("should say if it's a straight, double, triple etc or maybe a rank!")
