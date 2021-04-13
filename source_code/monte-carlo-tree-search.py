#!/usr/bin/env python3

import math
import itertools
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

def check_if_tuple_of_cards(cards):
    if isinstance(cards,tuple):
        for card in cards:
            if not isinstance(card,Card):
                raise Exception("tuple not a card class...fail")
    return None 

def UCB(wins,games,parent_total,constant):
    if games == 0 or parent_total == 0:
        raise Exception("UCB requires games or parent total")
    return wins / games + constant * math.sqrt(math.log(parent_total)/games)

class GenericNode(object):

    id_iter = itertools.count()

    def __init__(self):
        self.id = next(self.id_iter)
        self.card_states = {}

    def get_card_state(self):
        return self.card_states

    def __repr__(self):
        return 'node ' + str(self.id)

class PlayerNode(GenericNode):
    def __init__(self):
        super().__init__()
        self.fold = None
        self.call = None 
        self.bet = None

class OpponentNode(PlayerNode):
    def __init__(self):
        super().__init__()

class DecisionNode(PlayerNode):
    def __init__(self):
        super().__init__()

class MCST(object):
    def __init__(self,turn_order):
        self.turn_order = turn_order
        self.card_context = []
        pass

    def get_card_context(self):
        return self.card_context

    def set_card_context(self,cards):
        self.card_context = cards 
        return None

class MCST_Set():
    def __init__(self):
        self.pre_flops = {}

    def all_hands(self):
        return list(self.pre_flops.keys())

    def add_game(self,turn_order):
        game_tuple = (turn_order)
        if cards not in self.pre_flops:
            self.pre_flops[game_tuple] = MCST(turn_order)
        return None 

    def get_game(self,turn_order):
        game_tuple = (turn_order)
        if cards not in self.pre_flops:
            self.pre_flops[game_tuple] = MCST(turn_order)
        return self.pre_flops[game_tuple] 

    def __repr__(self):
        message = 'MCTS set:'
        for turn_order, hand in self.all_hands():
            message += '\n{} - {}'.format(turn_order, hand)
        return message

query_set = [
        ('player', 'current', 'bet', -5), 
        ('player', 'opponent 1', 'bet', 0), 
        ('card', Card(rank='2', suit='spades')), 
        ('player', 'current', 'bet', 0), 
        ('player', 'opponent 1', 'bet', 0), 
        ('card', Card(rank='3', suit='diamonds')), 
        ('player', 'current', 'bet', 0), 
        ('player', 'opponent 1', 'bet', 0), 
        ('card', Card(rank='3', suit='hearts'))
    ]

if __name__ == '__main__':
    print("starting MCTS")
    turn_order = ('current', 'opponent 1')
    cards = (Card(rank='9', suit='spades'), Card(rank='A', suit='spades'))

    hand_sets = MCST_Set()
    hand_sets.add_game(turn_order)
    current_MCST = hand_sets.get_game(turn_order)
    print(current_MCST)
