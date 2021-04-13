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

class MCST_Set():
    def __init__(self):
        self.game_types = {}

    def all_hands(self):
        return list(self.pre_flops.keys())

    def add_game(self,number_of_players):
        if number_of_players not in self.game_types:
            self.game_types[number_of_players] = MCST(number_of_players)
        return None 

    def get_game(self,number_of_players):
        if number_of_players not in self.game_types:
            self.add_game(number_of_players)
        return self.game_types[number_of_players] 

    def __repr__(self):
        message = 'MCTS set:'
        for MCTS in self.game_types.values():
            message += '\n' + str(MCTS) 
        return message

class MCST(object):
    def __init__(self,number_of_players):
        self.number_of_players = number_of_players
        self.hand_context = None 
        self.card_context = None
        self.turn_order = None
        pass

    def get_turn_order(self):
        return self.turn_order

    def set_turn_order(self,turn_order):
        self.turn_order = turn_order
        return None

    def get_player_hand(self):
        return self.hand_context + self.card_context

    def get_hand_context(self):
        return self.hand_context

    def set_hand_context(self, hand_context):
        self.hand_context = hand_context 
        return None

    def get_card_context(self):
        return self.card_context

    def set_card_context(self,cards):
        self.card_context = cards 
        return None

    def query(self,query):
        return None

    def __repr__(self): 
        return 'MCTS with {} players'.format(number_of_players)

query_set = [
        ('player', 'current', 'bet', -5), 
        ('player', 'opponent 1', 'bet', 0), 
        ('card', (Card(rank='2', suit='spades'), Card(rank='5', suit='diamonds'), Card(rank='9', suit='diamonds'))), 
        ('player', 'current', 'bet', 0), 
        ('player', 'opponent 1', 'bet', 0), 
        ('card', (Card(rank='2', suit='spades'), Card(rank='5', suit='diamonds'), Card(rank='9', suit='diamonds'), Card(rank='3', suit='diamonds'))), 
        ('player', 'current', 'bet', 0), 
        ('player', 'opponent 1', 'bet', 0), 
        ('card', (Card(rank='2', suit='spades'), Card(rank='5', suit='diamonds'), Card(rank='9', suit='diamonds'), Card(rank='3', suit='diamonds'), Card(rank='3', suit='hearts')))
    ]

if __name__ == '__main__':
    print("starting MCTS")
    number_of_players = 2
    turn_order = ('current', 'opponent 1')
    cards = (Card(rank='9', suit='spades'), Card(rank='A', suit='spades'))

    trees = MCST_Set()
    trees.add_game(number_of_players)
    current_MCST = trees.get_game(number_of_players)
    print(trees)
