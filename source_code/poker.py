#!/usr/bin/env python3

import random
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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

    def shuffle_deck(self):
        self.cards = self.original_deck()
        self.removed_cards = []
        random.shuffle(self.cards)
        return None

class DeckSequence():
    def __init__(self,players,decks=10):
        self.players = players
        self.decks=decks
        self.cards_in_play = players * 2 + 5
        self.cards_used_per_deck = 52 - (52 % self.cards_in_play)
        self.plays_per_deck = self.cards_used_per_deck / self.cards_in_play

        sample_deck = Deck()

        self.sequence = []

        for _ in range(0,self.decks):
            generated_deck = sample_deck.cards[0:self.cards_used_per_deck]
            self.sequence.extend(generated_deck)
            sample_deck.shuffle_deck()

        self.hands = list(chunk(self.sequence,self.cards_in_play))

if __name__ == '__main__':
    deck = DeckSequence(players=2,decks=100)

    for hand in deck.hands:
        print(hand)

