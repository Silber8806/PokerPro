#!/usr/bin/env python3
import sys
import math
import itertools
import collections
import time
import random
import copy

from poker import *

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

def monte_carlo_simulation(cards,river,opponents,runtimes=1):
    """
        A player can use this to simulate the odds of them winning a hand of poker.
        You give it your current hand (cards variable), the current river, which is
        either: None (pre-flob), 3,4,5 for post-flop.  The odds change with the 
        number of opponents, so you need to add it to.  You do this for
        runtime number of times and report the percent of wins.  YOu can 
        think of it as a monte-carlo simulation
    """
    deck = FrenchDeck()

    # enabling cache means if same hand + river show up, use the latest odds and skip calc
    # bad thing about this is if you get a 1% percentile win-rate on a flop etc, than 
    # that becomes baked into simulation.  So disable cache == better results, enable
    # cache means quicker results.

    if river is None:
        river = []  # this is a pre-flob situation

    for card in cards + river:
        deck.remove_card(rank=card.rank,suit=card.suit) # remove the players hand and river from the deck

    deck.save_deck() # the deck with removed cards is our start point for simulating everything.  So save it and reload after each runtime.

    start_hand = cards # your hand
    draw_player = len(cards) # all peoples hands
    draw_river = 5 - len(river) # current number of cards left to draw in the river

    wins = 0
    for _ in range(runtimes):
        hands_to_compare = []
        if len(river) < 5:
            new_river = deck.draw(draw_river) # draw the river
        else:
            new_river = [] # you already drew the river (all 5 cards)
        current_river = river[:] + new_river # river with simulated cards
        player_hand = start_hand[:] + current_river[:]  # your hand including simulated river
        hands_to_compare.append(player_hand) # your hand is always first
        for _ in range(opponents):
            opponent_hand = deck.draw(draw_player) + current_river[:] # create opponents hands
            hands_to_compare.append(opponent_hand) # add after your hand
        is_win = winning_hand(hands_to_compare) # rank the hands, check if first one won

        if is_win:
            wins += 1 # keep tabs of your wins

        deck.load_deck() # reset the deck for the next simulation
        deck.reshuffle_draw_deck()

    return (wins, runtimes) # your percent wins

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

class PlayerNode(object):

    id_iter = itertools.count()

    def __init__(self,player_type,card_context=None,turn_context=None,restrict_raises=False,card_phase=None,leaf_node=False,player_action=None):
        self.id = next(self.id_iter)
        self.restrict_raises = restrict_raises
        if self.restrict_raises:
            self.relations = {'fold':None,'call':None}
        else:
            self.relations = {'fold':None,'call':None,'bet':None}
        self.card_context = card_context
        self.turn_context = turn_context
        self.card_phase = card_phase
        self.player_type = player_type
        self.leaf_node = leaf_node
        self.player_action = player_action
        self.parent = None
        self.last_turn = None
        self.bid_round = None
        self.debug = 0
        
    def get_parent_chain(self):
        parents = []
        active_node = self 
        while active_node.parent is not None:
            parents.insert(0,active_node.parent.player_action)
            active_node = active_node.parent
        return parents

    def __repr__(self):
        parents = self.get_parent_chain()
        parents.append(self.player_action)
        if self.debug == 1:
            listing = "({}) => ({}:{}:{}) => ({}) => \n\t({})".format(parents,self.card_phase,self.player_type,self.player_action,self.leaf_node,self.card_context)
        else:
            listing = "({}:{})".format(self.card_phase,parents)
        return listing

class MCST(object):
    def __init__(self,number_of_players):
        self.number_of_players = number_of_players
        self.hand = None 
        self.cards = ()
        self.turn_order = None
        self.actions = ['fold','call','bet']
        self.root = PlayerNode(player_type='start')

    def get_root(self):
        return self.root

    def select_node(self,node):
        turn_order = list(node.turn_context)
        cards = node.card_context
        card_phase = node.card_phase 

        if len(turn_order) == 1:
            if node.parent is not None:
                return self.select_node(node.parent)

        unfullfilled_actions = []
        fullfilled_actions = []
        possible_actions = len(node.relations.keys())

        closed_nodes = 0
        for action in node.relations:
            connected_node = node.relations[action]
            if connected_node is None:
                unfullfilled_actions.append(action)
            elif len(connected_node.turn_context) > 1 and connected_node.leaf_node is False:
                fullfilled_actions.append(action)
            elif connected_node.leaf_node is True:
                closed_nodes += 1

        if possible_actions == closed_nodes:
            node.leaf_node = True
            if node.parent is not None:
                return self.select_node(node.parent)

        if len(unfullfilled_actions):
            action_to_update = random.choice(unfullfilled_actions)
            new_player_type = turn_order[0]

            last_turn = copy.deepcopy(node.last_turn)
            bid_round = copy.deepcopy(node.bid_round)

            new_card_action = 1
            for player in last_turn:
                if last_turn[player] is None or last_turn[player] == 'bet':
                    new_card_action=0

            if new_card_action == 1:
                for player in last_turn:
                    if last_turn[player] != 'fold':
                        bid_round[player] = 0
                        last_turn[player] = None
                cards =  tuple(list(cards) + [1])
                card_phase += 1

            if card_phase == 4:
                node.leaf_node = True
                print("reached end game")
                if node.parent is not None:
                    return self.select_node(node.parent)

            if action_to_update == 'fold':
                turn_order.pop(0)
                bid_round[new_player_type] = 3
            else:
                bid_round[new_player_type] += 1

            last_turn[new_player_type] = action_to_update
            new_turn_order = turn_order[1:] + turn_order[0:1]

            next_player = new_turn_order[0]
            next_player_bid = bid_round[next_player]

            if next_player_bid == 2:
                restrict_raises=True 
            else:
                restrict_raises=False 

            if len(new_turn_order) == 1:
                set_as_leaf_node = True
            else:
                set_as_leaf_node = False

            new_node = PlayerNode(
                player_type=new_player_type,
                player_action=action_to_update,
                card_context=cards,
                turn_context=new_turn_order,
                restrict_raises=restrict_raises,
                card_phase=card_phase,
                leaf_node=set_as_leaf_node
            )

            new_node.last_turn = last_turn
            new_node.bid_round = bid_round
            new_node.parent = node
            node.relations[action_to_update] = new_node
            
            return new_node
        else:
            relationship_to_visit = random.choice(fullfilled_actions)
            node_to_visit = node.relations[relationship_to_visit]
            self.select_node(node_to_visit)

        return None 

    def simulate_node(self,node):
        return None

    def back_propogate_node(self,node):
        return None

    def build(self,turn_order,hand,compute_time=1):
        if compute_time is None:
            raise Exception("You didn't specify a compute or step limit for MCTS")
        if compute_time < 1:
            raise Exception("You have to run simulation for at least 1 second")

        root = self.get_root()
        root.turn_context = turn_order
        root.card_context = hand
        root.last_turn = {player:None for player in turn_order}
        root.bid_round = {player:0 for player in turn_order}
        root.card_phase=0

        start = time.time()
        elapsed_time = 0

        i = 0
        while elapsed_time < compute_time:
            end = time.time()
            self.select_node(root)
            elapsed_time = end - start
            i = i + 1
            if i > 10000:
                break

        return None

    def query(self,query_set):
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
    hand = (Card(rank='9', suit='spades'), Card(rank='A', suit='spades'))

    trees = MCST_Set()
    trees.add_game(number_of_players)
    current_MCST = trees.get_game(number_of_players)
    current_MCST.build(compute_time=1000,turn_order=turn_order,hand=hand)
    print(current_MCST)

