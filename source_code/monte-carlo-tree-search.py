#!/usr/bin/env python3
import sys
import math
import itertools
import collections
import time
import random
import copy
import pickle
import os

from poker import *

Card = collections.namedtuple('Card', ['rank', 'suit'])

debug = 0

def dprint(message):
    if debug == 1:
        print(message)

def order_by_rank(cards):
    return tuple(sorted(list(cards),key=lambda card: (card.rank, card.suit)))

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

    def add_game(self,turn_order):
        if turn_order not in self.game_types:
            self.game_types[turn_order] = MCST(turn_order)
        return None 

    def has_game(self,turn_order):
        if turn_order in self.game_types:
            return True 
        else: 
            return False

    def get_game(self,turn_order):
        if turn_order not in self.game_types:
            self.add_game(turn_order)
        return self.game_types[turn_order] 

    def __repr__(self):
        message = 'MCTS set:'
        for MCTS in self.game_types.values():
            message += '\n' + str(MCTS) 
        return message

class PlayerNode(object):

    id_iter = itertools.count()

    def __init__(self,player_type,card_context=None,turn_context=None,restrict_raises=False,card_phase=None,game_node=False,player_action=None,new_phase=0):
        self.id = next(self.id_iter)
        self.restrict_raises = restrict_raises
        if self.restrict_raises:
            self.relations = {'fold':None,'call':None}
        else:
            self.relations = {'fold':None,'call':None,'bet':None}
        self.card_context = card_context
        if card_context is not None:
            self.card_slots = len(card_context)
        else:
            self.card_slots = 2
        if card_context is not None:
            self.leaf_node = {card_context: game_node}
        else:
            self.leaf_node = {}
        self.end_game_node = game_node
        self.turn_context = turn_context
        self.card_phase = card_phase
        self.player_type = player_type
        self.player_action = player_action
        self.parent = None
        self.last_turn = None
        self.bid_round = None
        self.debug = 0
        self.card_wins = {}
        self.card_totals = {}
        self.new_phase = new_phase
        self.back_propogation_list = []
        
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
    def __init__(self,turn_order,card_branching=100,monte_carlo_sims=1):
        self.turn_order = turn_order
        self.hand = None 
        self.cards = ()
        self.actions = ['fold','call','bet']
        self.root = PlayerNode(player_type='start')
        self.done = {}
        self.card_branching = card_branching
        self.monte_carlo_sims = monte_carlo_sims
        self.hands_simulated = set()

    def get_root(self):
        return self.root

    def has_hand(self,hand):
        ordered_hand = order_by_rank(hand)
        if ordered_hand in self.hands_simulated:
            return True 
        else:
            return False

    def draw_river(self,removed_cards,draw_cards):
        deck = FrenchDeck()

        for card in removed_cards:
            deck.remove_card(rank=card.rank,suit=card.suit)

        new_cards = deck.draw(draw_cards)
        new_cards = order_by_rank(new_cards)
        return new_cards

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
            else:
                abridged_key = []
                for key in connected_node.card_totals.keys():
                    abridged_key.append(key[0:2])

                if cards not in abridged_key:
                    unfullfilled_actions.append(action)
                    continue

                missing_leaf = False
                for key in connected_node.leaf_node.keys():
                    if key[0:2] == cards:
                        if connected_node.leaf_node[key] == False:
                            missing_leaf = True
                            break

                if len(connected_node.turn_context) > 1 and missing_leaf is True:
                    fullfilled_actions.append(action)
                elif missing_leaf is False:
                    closed_nodes += 1

        if possible_actions == closed_nodes:
            node.leaf_node[cards] = True
            if node.player_type == 'start':
                return 'done'
            if node.parent is not None:
                return self.select_node(node.parent)

        if len(unfullfilled_actions):
            action_to_update = random.choice(unfullfilled_actions)

            new_player_type = turn_order[0]

            if node.relations[action_to_update] is not None:
                updated_node = node.relations[action_to_update]

                if action_to_update == 'fold':
                    turn_order.pop(0)

                new_turn_order = turn_order[1:] + turn_order[0:1]
                updated_node.player_type = new_player_type
                updated_node.turn_context = new_turn_order

                if updated_node.end_game_node == True:
                    updated_node.leaf_node[cards] = True
                else:
                    updated_node.leaf_node[cards] = False

                updated_node.card_context = cards
                return updated_node
            else:
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
                    card_phase += 1

                if card_phase == 4:
                    node.leaf_node[cards] = True
                    node.end_game_node = True
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
                    set_as_end_game_node = True
                else:
                    set_as_end_game_node = False

                new_node = PlayerNode(
                    player_type=new_player_type,
                    player_action=action_to_update,
                    card_context=cards,
                    turn_context=new_turn_order,
                    restrict_raises=restrict_raises,
                    card_phase=card_phase,
                    game_node=set_as_end_game_node,
                    new_phase=new_card_action
                )

                self.node_count = new_node.id + 1
                new_node.last_turn = last_turn
                new_node.bid_round = bid_round
                new_node.parent = node
                node.relations[action_to_update] = new_node
                return new_node
        else:
            relationship_to_visit = random.choice(fullfilled_actions)
            node_to_visit = node.relations[relationship_to_visit]
            return self.select_node(node_to_visit)

    def simulate_node(self,node):

        node.back_propogation_list = {}

        if node.player_type == 'current' and node.player_action != 'fold':
            active_opponents = len(node.turn_context)
            hand = node.card_context[:2]

            if node.card_phase == 0:
                river = []
                hand, river = list(hand),list(river)
                wins, total = monte_carlo_simulation(cards=hand,river=river,opponents=active_opponents,runtimes=self.monte_carlo_sims)

                propogation_key = tuple(hand)
                node.back_propogation_list[propogation_key] = {"wins":wins,"total":total}
            else:
                if node.card_phase == 1:
                    total_river_cards = 3
                elif node.card_phase == 2:
                    total_river_cards = 4
                elif node.card_phase == 3:
                    total_river_cards = 5
                else:
                    raise Exception("No card phase greater than 3")

                river = node.card_context[3:]
                current_river_cards = len(river)

                hand, river = list(hand),list(river)

                deck = FrenchDeck()
                for card in hand:
                    deck.remove_card(rank=card.rank,suit=card.suit) # remove the players hand and river from the deck
                deck.save_deck()

                cards_to_draw = total_river_cards - current_river_cards

                if cards_to_draw < 0:
                    raise Exception("simulation: can't draw less than 0 cards")

                for _ in range(0,self.card_branching):
                    if cards_to_draw == 0:
                        new_river = river
                    else:
                        new_river = list(river) + list(deck.draw(cards_to_draw))
                    wins, total = monte_carlo_simulation(cards=hand,river=new_river,opponents=active_opponents,runtimes=self.monte_carlo_sims)

                    propagation_key = tuple(hand + new_river)
                    node.back_propogation_list[propagation_key] = {"wins":wins,"total":total}

                    deck.load_deck()
                    deck.reshuffle_draw_deck()
                    
        else:
            propagation_key = node.card_context
            node.back_propogation_list[propagation_key] = {"wins":0,"total":0}
        return None

    def back_propogate_node(self,node):
        card_updates_to_propogate = node.back_propogation_list
        
        for prop_key in card_updates_to_propogate:
            active_node = node 

            new_wins = card_updates_to_propogate[prop_key]['wins']
            new_total = card_updates_to_propogate[prop_key]['total']

            while active_node is not None:
                card_slots = active_node.card_slots
                card_to_update = prop_key[:card_slots]

                current_wins = active_node.card_wins.get(card_to_update,0) + new_wins
                active_node.card_wins[card_to_update] = current_wins

                current_totals = active_node.card_totals.get(card_to_update,0) + new_total
                active_node.card_totals[card_to_update] = current_totals

                active_node = active_node.parent

        return None

    def build(self,hand,compute_time=1,max_nodes=1000):
        if compute_time is None:
            raise Exception("You didn't specify a compute or step limit for MCTS")
        if compute_time < 1:
            raise Exception("You have to run simulation for at least 1 second")

        hand = order_by_rank(hand)

        self.done[hand] = False
        self.hands_simulated.add(hand)

        root = self.get_root()
        root.turn_context = self.turn_order
        root.card_context = hand
        root.last_turn = {player:None for player in self.turn_order}
        root.bid_round = {player:0 for player in self.turn_order}
        root.leaf_node[hand] = False
        root.card_phase=0

        start = time.time()
        elapsed_time = 0

        i = 0
        while elapsed_time < compute_time:
            end = time.time()
            new_node = self.select_node(root)
            if new_node == 'done':
                self.done[hand] = True
                break
            self.simulate_node(new_node)
            self.back_propogate_node(new_node)
            elapsed_time = end - start
            i = i + 1
            if max_nodes != math.inf:
                if i > max_nodes:
                    break

        return None

    def query(self,query_set):
        return None

    def __repr__(self): 
        return 'MCTS with {} players'.format(str(self.turn_order))

query_set = {
    'card_context': (Card(rank='9', suit='spades'), Card(rank='A', suit='spades')),
    'decisions':[
        ('current','bet',100),
        ('opponent 1','call',0),
        ('current','bet',100),
        ('opponent 1','call',0)
    ]
}

if __name__ == '__main__':
    print("starting MCTS")
    turn_order = ('current', 'opponent 1')

    pickled_file = 'MCST.pickle'
    if os.path.exists(pickled_file):
        with open(pickled_file, 'rb') as handle:
            trees = pickle.load(handle)
    else:
        trees = MCST_Set()
        trees.add_game(turn_order)
        current_MCST = trees.get_game(turn_order)

        print("starting first simulation")
        hand = (Card(rank='9', suit='spades'), Card(rank='A', suit='spades'))
        current_MCST.build(compute_time=120,hand=hand,max_nodes=math.inf)

        print(current_MCST.get_root().card_totals)

        with open(pickled_file, 'wb') as handle:
            pickle.dump(trees, handle, protocol=pickle.HIGHEST_PROTOCOL)

    current_MCST = trees.get_game(turn_order)