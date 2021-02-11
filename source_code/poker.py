#!/usr/bin/env python3

import random
import collections

from itertools import permutations

Card = collections.namedtuple('Card', ['rank', 'suit'])

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Table():
    def __init__(self,players):
        print('started poker game')
        self.players = players

class FrenchDeck():

    """ 
       This is a class implementing a classic 52-card 
       french deck.  You can stream cards via:

       draw(number of cards)

       or

       permute(number of cards)

        Draw will go through the entire deck before reshuffling
        permute will reshuffle each time.  reshuffle at any time
        with the reshuffle() method.
    """

    def __init__(self):
        self.ranks = [str(n) for n in range(2, 11)] + list('JQKA')
        self.suits = 'spades diamonds clubs hearts'.split()
        standard_card_deck = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        self.all_cards = standard_card_deck[:]
        random.shuffle(standard_card_deck)
        self.cards = standard_card_deck
        self.removed_cards = []
        return None

    def reshuffle(self):
        """ reshuffles the deck """
        self.cards = self.removed_cards + self.cards
        random.shuffle(self.cards)
        self.removed_cards = []
        return None

    def _draw(self,num_of_cards,hands=1):
        """ 
            internal class to handle the logic
            for creating a generator for draw class
        """
        if num_of_cards < 1 or num_of_cards > 52:
            raise Exception("Error: Draw has to be between 1 and 52")

        if hands < 1:
            raise Exception("Error: at least 1 hand needs to be drawn")

        for _ in range(hands):
            if num_of_cards >= len(self.cards):
                self.reshuffle()
            new_draw = self.cards[:num_of_cards]
            self.removed_cards.extend(new_draw)
            self.cards = self.cards[num_of_cards:]
            yield new_draw

    def draw(self,num_of_cards,hands=1):
        """ 
            draw(num_of_cards)

            returns <num_of_cards:int> cards from the deck and 
            keeps track of these cards by moving them 
            from the cards attribute to the removed cards
            attribute.  If there are less cards than <num of cards>
            reshuffles the entire deck before drawing.

            draw(num_of_cards, hands)

            returns a generator, which you can iterate 
            through to generate up to <hands:int> number of 
            hands of <num_of_cards:int> cards.  Each iteration
            behaves like draw(num_of_cards)
        """
        if hands == 1:
            return next(self._draw(num_of_cards=num_of_cards,hands=hands))
        else:
            return self._draw(num_of_cards=num_of_cards,hands=hands)

    def _permute(self,num_of_cards,hands=1):
        """ 
            internal class to handle the logic
            for creating a generator for permute class
        """
        if num_of_cards < 1 or num_of_cards > 52:
            raise Exception("Error: Draw has to be between 1 and 52")

        if hands < 1:
            raise Exception("Error: at least 1 hand needs to be drawn")

        for _ in range(hands):
            new_draw = self.all_cards[:]
            random.shuffle(new_draw)
            yield new_draw[:num_of_cards]

    def permute(self,num_of_cards,hands=1):

        """
        permute(num_of_cards)

        returns <num_of_cards> permutation.  Doesn't reshuffle
        or alter any states.

        permute(num_of_cards, hands)

        returns a generator, which returns <hands>
        number of permutations.
        """

        if hands == 1:
            return next(self._permute(num_of_cards=num_of_cards,hands=hands))
        else:
            return self._permute(num_of_cards=num_of_cards,hands=hands)

    def set_seed(self,seed):
        random.seed(seed)
        return None

    def __str__(self):
        return "French Deck ({} of {} cards remaining)".format(len(self.cards),len(self.all_cards))

class Game():
    def __init__(self,cards):
        self.cards = cards
        self.players = (len(cards) - 5) // 2
        self.positions = { "player" + str(i+1): hand for i, hand in enumerate(chunk(cards[5:],2)) }
        self.positions['river'] = self.cards[:5]
        return None

    def run_game(self):
        print("started_game")
        return None

    def __str__(self):
        return "Game with {} players".format(self.players)

if __name__ == '__main__':
    deck = FrenchDeck()

    players = 2
    cards_per_game = 2 * 2 + 5

    for game_number, hand in enumerate(deck.permute(cards_per_game,1000)):
        print("starting game number: {}".format(game_number+1))
        game = Game(hand)
        game.run_game()
        print("finished game number: {}".format(game_number+1))

