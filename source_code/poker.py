#!/usr/bin/env python3

import random
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class PokerGame():
    def __init__(self,players):
        print('started poker game')
        self.players = players

class Deck():
    def __init__(self):
        self.ranks = [str(n) for n in range(2, 11)] + list('JQKA')
        self.suits = 'spades diamonds clubs hearts'.split()
        standard_card_deck = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        random.shuffle(standard_card_deck)
        self.cards = standard_card_deck
        self.removed_cards = []

    def draw(self,number_of_cards):
        drawn_cards = self.cards[0:number_of_cards]
        self.cards = self.cards[number_of_cards:]
        self.removed_cards.append(drawn_cards)
        return drawn_cards

    def original_deck(self):
        return self.removed_cards + self.cards

