#!/usr/bin/env python3

import math
import itertools
import collections
import time

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
    def __init__(self,cards=None,bid=None,parent=None,player_type=None):
        super().__init__()
        self.relations = {'fold':None,'call':None,'bet':None}
        self.parent = parent
        if cards is None:
            self.card_context = []
        else:
            self.card_context = cards
        self.bid = bid
        self.player_type = player_type

    def set_card_context(self,cards):
        self.card_context = cards
        return None

    def get_card_context(self):
        return self.card_context

    def set_parent(self,node):
        self.parent = node 
        return None 

    def get_parent(self):
        return self.parent

    def set_bid(self,bid):
        self.bid = bid
        return None

    def get_bid(self):
        return self.bid

    def set_player_type(self,player_type):
        self.player_type = player_type
        return None 

    def get_player_type(self):
        return self.player_type

    def __repr__(self):
        return 'node ' + str(self.id) + ' {} - {} - '.format(self.player_type,self.bid) + ' {}'.format(str(self.get_card_context()))

class MCST_Set():
    def __init__(self):
        self.game_types = {}

    def all_games(self):
        return list(self.game_types.keys())

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
        self.card_context = ()
        self.turn_order = None
        self.root = None

    def set_root(self,node):
        self.root = node 
        return None 

    def get_root(self):
        return self.root

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

    def create_player_node(self,player_type=None,bid=None):
        cards = self.get_player_hand()
        new_node = PlayerNode(cards=cards,player_type=player_type,bid=bid)
        return new_node

    def build(self,compute_time=None):
        if compute_time is None:
            raise Exception("You didn't specify a compute or step limit for MCTS")
        if compute_time < 1:
            raise Exception("You have to run simulation for at least 1 second")
        if self.turn_order is None:
            raise Exception("Building a tree requires an active player..provide a turn order")

        turn_order_provided = self.get_turn_order()[:]

        start = time.time()
        elapsed_time = 0

        while elapsed_time < compute_time:
            end = time.time()
            elapsed_time = end - start

        return None

    def query(self,query):

        active_players = self.get_turn_order()[:]

        query_iter = iter(query)
        node_type, player_type, action_type, bid = next(query_iter)
        active_connection = action_type

        if self.get_root() is None:
            active_node = self.create_player_node(player_type,bid)
            self.set_root(active_node)

        active_node = self.get_root()

        for q in query_iter:
            if q[0] == 'player':
                node_type, player_type, action_type, bid = q
                if active_node.relations[active_connection] is None:
                    new_node = self.create_player_node(player_type,bid)
                    active_node.relations[active_connection] = new_node
                    new_node.parent = active_node
                active_node = active_node.relations[active_connection] 
                active_connection = action_type
            else:
                node_type, cards = q
                self.set_card_context(cards)

        while active_node.parent is not None:
            print(active_node)
            active_node = active_node.parent 
            
        return None

    def __repr__(self): 
        return 'MCTS with {} players'.format(number_of_players)

query_set = [
    ('player', 'current', 'call', 0), 
    ('player', 'opponent 1', 'call', 0), 
    ('card', (Card(rank='8', suit='hearts'), Card(rank='9', suit='hearts'), Card(rank='A', suit='clubs'))), 
    ('player', 'current', 'call', 0), 
    ('player', 'opponent 1', 'call', 0), 
    ('card', (Card(rank='8', suit='hearts'), Card(rank='9', suit='hearts'), Card(rank='A', suit='clubs'), Card(rank='9', suit='diamonds'))), 
    ('player', 'current', 'call', 0), 
    ('player', 'opponent 1', 'call', 0), 
    ('card', (Card(rank='8', suit='hearts'), Card(rank='9', suit='hearts'), Card(rank='A', suit='clubs'), Card(rank='9', suit='diamonds'), Card(rank='A', suit='hearts')))
]

if __name__ == '__main__':
    print("starting MCTS")
    number_of_players = 2
    turn_order = ('current', 'opponent 1')
    cards = (Card(rank='9', suit='spades'), Card(rank='A', suit='spades'))

    trees = MCST_Set()
    trees.add_game(number_of_players)
    current_MCST = trees.get_game(number_of_players)
    current_MCST.set_turn_order(turn_order)
    current_MCST.set_hand_context(cards)
    current_MCST.query(query_set)

    current_MCST.get_root()

    print(trees)
