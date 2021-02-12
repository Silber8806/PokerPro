#!/usr/bin/env python3

from poker import Card, FrenchDeck

Suits = 'spades diamonds clubs hearts'.split()
Ranks = [str(n) for n in range(2, 11)] + list('JQKA')

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

    print("You can create hands here that are random for testing purposes")
    deck = FrenchDeck()

    for hand in deck.permute(7,3):
        print(hand)
