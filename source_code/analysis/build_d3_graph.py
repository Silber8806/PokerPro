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
import json

from poker import *

Card = collections.namedtuple('Card', ['rank', 'suit'])

debug = 0

def dprint(message):
    if debug == 1:
        print(message)

def order_by_rank(cards):
    return tuple(sorted(list(cards),key=lambda card: (RankMap[card.rank], card.suit)))

def UCB(wins,games,parent_total,constant):
    if games == 0 or parent_total == 0:
        return 0
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

class MCST_Set(object):
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

    def __init__(self,player_type,turn_context=None,restrict_raises=False,card_phase=None,player_action=None,new_phase=0):
        self.id = next(self.id_iter)
        self.restrict_raises = restrict_raises
        if self.restrict_raises:
            self.relations = {'fold':None,'call':None}
        else:
            self.relations = {'fold':None,'call':None,'bet':None}
        self.leaf_node = {}
        self.end_game_node = False
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
    
    @property
    def parents(self):
        parents = []
        active_node = self 
        while active_node.parent is not None:
            parents.insert(0,active_node.parent.player_action)
            active_node = active_node.parent
        return parents

    @property 
    def fold(self):
        return self.relations['fold']

    @property 
    def call(self):
        return self.relations['call']

    @property 
    def bet(self):
        return self.relations['bet']

    def get_game_total(self, card):
        game_total = 0
        for card_set in self.card_totals:
            if card_set[0:len(card)] == card:
                game_total += self.card_totals[card_set]
        return game_total

    def get_win_total(self, card):
        win_total = 0
        for card_set in self.card_wins:
            if card_set[0:len(card)] == card:
                win_total += self.card_wins[card_set]
        return win_total

    def get_child_game_totals(self,card):
        game_totals = {}
        for action in self.relations:
            node =  self.relations[action]
            if node is not None:
                child_total = node.get_game_total(card)
                game_totals[action] = child_total 
        return game_totals

    def get_child_win_totals(self,card):
        win_totals = {}
        for action in self.relations:
            node =  self.relations[action]
            if node is not None:
                child_total = node.get_win_total(card)
                win_totals[action] = child_total 
        return win_totals

    def __repr__(self):
        parents = self.parents
        parents.append(self.player_action)
        if self.debug == 1:
            listing = "({}) => ({}:{}:{}) => ({}) => \n\t({})".format(parents,self.card_phase,self.player_type,self.player_action,self.leaf_node,self.card_context)
        else:
            listing = "({}:{})".format(self.card_phase,parents)
        return listing

class MCST(object):
    def __init__(self,turn_order,card_branching=1,monte_carlo_sims=1):
        self.turn_order = turn_order
        self.small_blind = turn_order[-2]
        self.big_blind = turn_order[-1]
        self.post_flop_turn_order = self.turn_order[-2:] + self.turn_order[:-2] 
        self.actions = ['fold','call','bet']
        self.done = {}
        self.card_branching = card_branching
        self.monte_carlo_sims = monte_carlo_sims
        self.hands_simulated = set()
        self.card_context = None
        self.node_count = 1
        self.root = PlayerNode(player_type='start')
        self.root.turn_context = self.turn_order
        self.root.last_turn = {player:None for player in self.turn_order}
        self.root.bid_round = {player:0 for player in self.turn_order}
        self.root.card_phase=0

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

    def select_node(self,root,node):
        turn_order = list(node.turn_context)
        cards = self.card_context

        if cards is None:
            raise Exception("Card context has to be set to select node")

        if len(root.turn_context) == 1:
            return 'done'

        if len(turn_order) == 1:
            if node.parent is not root.parent:
                return self.select_node(root,node.parent)

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
                    abridged_key.append(key[0:len(cards)])

                if cards not in abridged_key:
                    unfullfilled_actions.append(action)
                    continue

                missing_leaf = False
                for key in connected_node.leaf_node.keys():
                    if key[0:len(cards)] == cards:
                        if connected_node.leaf_node[key] == False:
                            missing_leaf = True
                            break

                if len(connected_node.turn_context) > 1 and missing_leaf is True:
                    fullfilled_actions.append(action)
                elif missing_leaf is False:
                    closed_nodes += 1

        if possible_actions == closed_nodes:
            node.leaf_node[cards] = True
            if node is root:
                return 'done'
            if node.parent is not root.parent:
                return self.select_node(root,node.parent)

        if len(unfullfilled_actions):
            action_to_update = random.choice(unfullfilled_actions)

            if node.relations[action_to_update] is not None:
                updated_node = node.relations[action_to_update]
                self.update_node(updated_node,cards)
                return updated_node
            else:
                card_phase = node.card_phase 
                last_turn = copy.deepcopy(node.last_turn)
                bid_round = copy.deepcopy(node.bid_round)
        
                new_card_action = 1
                bid_matching=set()
                for player in turn_order:
                    if last_turn[player] == 'fold':
                        continue 
                    elif last_turn[player] is None:
                        new_card_action=0
                        break
                    else:
                        bid_matching.add(bid_round[player])

                if new_card_action == 1:
                    if len(bid_matching) != 1:
                        new_card_action=0

                    if new_card_action == 1:
                        
                        if card_phase == 0:
                            turn_order_to_check=self.turn_order
                        elif card_phase > 0 and card_phase < 4:
                            turn_order_to_check=self.post_flop_turn_order

                        player_positions = [last_turn[player] for player in turn_order_to_check if last_turn[player] != 'fold']

                        if player_positions[0] not in ('call','bet'):
                            new_card_action=0
                        else:
                            for player in player_positions[1:]:
                                if player == 'bet' or player is None:
                                    new_card_action=0

                if new_card_action == 1:
                    for player in last_turn:
                        if last_turn[player] != 'fold':
                            bid_round[player] = 0
                            last_turn[player] = None
                    card_phase += 1

                    if card_phase > 0 and card_phase < 4:
                        turn_order = [player for player in self.post_flop_turn_order if last_turn[player] != 'fold']

                if card_phase == 4:
                    node.leaf_node[cards] = True
                    node.end_game_node = True
                    if node.parent is not root.parent:
                        return self.select_node(root,node.parent)

                new_player_type = turn_order[0]
                if action_to_update == 'fold':
                    turn_order.pop(0)
                    new_turn_order = turn_order
                    bid_round[new_player_type] = 4
                else:
                    bid_round[new_player_type] += 1
                    new_turn_order = turn_order[1:] + turn_order[0:1]

                last_turn[new_player_type] = action_to_update
                
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
                    turn_context=new_turn_order,
                    restrict_raises=restrict_raises,
                    card_phase=card_phase,
                    new_phase=new_card_action
                )

                self.node_count += 1
                new_node.end_game_node = set_as_end_game_node
                new_node.leaf_node[cards] = set_as_end_game_node
                new_node.last_turn = last_turn
                new_node.bid_round = bid_round
                new_node.parent = node
                node.relations[action_to_update] = new_node

                return new_node
        else:
            graded_nodes = []
            for action in fullfilled_actions:
                node_to_grade = node.relations[action]

                game_wins = 0
                for card in node_to_grade.card_wins:
                    if card[0:len(cards)] == cards:
                        game_wins += node_to_grade.card_wins[card]

                game_totals = 0
                for card in node_to_grade.card_totals:
                    if card[0:len(cards)] == cards:
                        game_totals += node_to_grade.card_totals[card]

                parent_totals = 0
                for card in node_to_grade.parent.card_totals:
                    if card[0:len(cards)] == cards:
                        parent_totals += node_to_grade.parent.card_totals[card]

                UCB_score = UCB(wins=game_wins,games=game_totals,parent_total=parent_totals,constant=math.sqrt(2))
                graded_nodes.append((UCB_score,action))

            tie_breaker = {'fold':0, 'bet':1, 'call':2}
            graded_nodes = sorted(graded_nodes,key=lambda score: (-score[0],-tie_breaker[score[1]]))
            relationship_to_visit = graded_nodes[0][1]
            node_to_visit = node.relations[relationship_to_visit]
            return self.select_node(root,node_to_visit)

    def simulate_node(self,node):

        node.back_propogation_list = {}

        if node.player_type == 'current' and node.player_action != 'fold':
            active_opponents = len(node.turn_context)
            hand = self.card_context[:2]

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

                river = self.card_context[2:]
                current_river_cards = len(river)

                hand, river = list(hand),list(river)

                deck = FrenchDeck()
                for card in hand + river:
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

                    cards_to_propogate = list(hand) + list(new_river)

                    hand_prop_key = list(order_by_rank(cards_to_propogate[:2])) 
                    river_prop_key = list(order_by_rank(cards_to_propogate[2:5]))
                    last_prop_key = list(cards_to_propogate[5:])
                    propagation_key = tuple(hand_prop_key + river_prop_key + last_prop_key)

                    node.back_propogation_list[propagation_key] = {"wins":wins,"total":total}

                    deck.load_deck()
                    deck.reshuffle_draw_deck()
        else:
            propagation_key = self.card_context
            node.back_propogation_list[propagation_key] = {"wins":0,"total":0}
        return None

    def back_propogate_node(self,node):
        card_updates_to_propogate = node.back_propogation_list
        
        for prop_key in card_updates_to_propogate:
            active_node = node 

            new_wins = card_updates_to_propogate[prop_key]['wins']
            new_total = card_updates_to_propogate[prop_key]['total']

            while active_node is not None:
                if active_node.card_phase == 0:
                    card_slots = 2
                elif active_node.card_phase == 1:
                    card_slots = 5
                elif active_node.card_phase == 2:
                    card_slots = 6
                elif active_node.card_phase == 3:
                    card_slots = 7

                card_to_update = prop_key[0:card_slots]

                current_wins = active_node.card_wins.get(card_to_update,0) + new_wins
                active_node.card_wins[card_to_update] = current_wins

                current_totals = active_node.card_totals.get(card_to_update,0) + new_total
                active_node.card_totals[card_to_update] = current_totals

                active_node = active_node.parent

        return None

    def build(self,cards,node='root',compute_time=1,max_nodes=100000):
        if compute_time is None:
            raise Exception("You didn't specify a compute or step limit for MCTS")
        if compute_time < 1:
            raise Exception("You have to run simulation for at least 1 second")

        cards = list(cards)
        cards = tuple(order_by_rank(cards[:2]) + order_by_rank(cards[2:5]) + tuple(cards[5:]))
        self.card_context = cards
        self.done[cards] = False
        self.hands_simulated.add(cards)

        if node == 'root':
            root = self.get_root()
        else:
            root = node

        if root.card_phase == 0:
            card_slots = 2
        elif root.card_phase == 1:
            card_slots = 5
        elif root.card_phase == 2:
            card_slots = 6
        elif root.card_phase == 3:
            card_slots = 7
        else:
            raise Exception("can't have phase greater than 3")

        if len(cards) != card_slots:
            raise Exception("can't have more card slots {} than cards {} - phase {}".format(len(cards),card_slots,root.card_phase))

        root.leaf_node[cards] = False
        
        start = time.time()
        elapsed_time = 0

        i = 0
        while elapsed_time < compute_time:
            end = time.time()
            new_node = self.select_node(root,root)
            if new_node == 'done':
                self.done[cards] = True
                break
            self.simulate_node(new_node)
            self.back_propogate_node(new_node)
            elapsed_time = end - start
            i = i + 1
            if max_nodes != math.inf:
                if i > max_nodes:
                    break

        return None

    def update_node(self,node,cards):
        if node.end_game_node == True:
            node.leaf_node[cards] = True
        else:
            node.leaf_node[cards] = False
        return None

    def create_node(self,cards,parent_node,action_to_update):
        card_phase = parent_node.card_phase
        turn_order = list(parent_node.turn_context)

        last_turn = copy.deepcopy(parent_node.last_turn)
        bid_round = copy.deepcopy(parent_node.bid_round)

        new_card_action = 1
        bid_matching=set()
        for player in turn_order:
            if last_turn[player] == 'fold':
                continue 
            elif last_turn[player] is None:
                new_card_action=0
                break
            else:
                bid_matching.add(bid_round[player])

        if new_card_action == 1:
            if len(bid_matching) != 1:
                new_card_action=0

            if new_card_action == 1:
                
                if card_phase == 0:
                    turn_order_to_check=self.turn_order
                elif card_phase > 0 and card_phase < 4:
                    turn_order_to_check=self.post_flop_turn_order

                player_positions = [last_turn[player] for player in turn_order_to_check if last_turn[player] != 'fold']

                if player_positions[0] not in ('call','bet'):
                    new_card_action=0
                else:
                    for player in player_positions[1:]:
                        if player == 'bet' or player is None:
                            new_card_action=0

        if new_card_action == 1:
            for player in last_turn:
                if last_turn[player] != 'fold':
                    bid_round[player] = 0
                    last_turn[player] = None
            card_phase += 1

            if card_phase > 0 and card_phase < 4:
                turn_order = [player for player in self.post_flop_turn_order if last_turn[player] != 'fold']

        if card_phase == 4:
            parent_node.leaf_node[cards] = True
            parent_node.end_game_node = True
            return 'end game'

        new_player_type = turn_order[0]
        if action_to_update == 'fold':
            turn_order.pop(0)
            bid_round[new_player_type] = 3
            new_turn_order = turn_order
        else:
            bid_round[new_player_type] += 1
            new_turn_order = turn_order[1:] + turn_order[0:1]

        last_turn[new_player_type] = action_to_update

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
            turn_context=new_turn_order,
            restrict_raises=restrict_raises,
            card_phase=card_phase,
            new_phase=new_card_action
        )

        self.node_count += 1
        new_node.end_game_node = set_as_end_game_node
        new_node.leaf_node[cards] = set_as_end_game_node
        new_node.last_turn = last_turn
        new_node.bid_round = bid_round
        new_node.parent = parent_node
        parent_node.relations[action_to_update] = new_node

        return new_node

    def query(self,hand,query_set):
        node = self.get_root()
        hand = order_by_rank(hand)
        self.card_context = hand

        for query in query_set:
            player, action_type, _ = query
            prev_node = node
            node = node.relations[action_type]
            
            if node is None:
                if len(prev_node.turn_context) == 1 or prev_node.end_game_node == True:
                    raise Exception("Can't create node after game over...")
                node = self.create_node(hand,prev_node,action_type)
                self.simulate_node(node)
                self.back_propogate_node(node)
            else:
                abridged_key = []
                for key in node.card_totals.keys():
                    abridged_key.append(key[0:len(hand)])
                if hand not in abridged_key:
                    self.update_node(node,hand)
                    self.simulate_node(node)
                    self.back_propogate_node(node)

            if node.player_type != player:
                raise Exception("wrong player type...please check for bugs")

        return node 

    def __repr__(self): 
        return 'MCTS with {} players'.format(str(self.turn_order))

def recurse(tree,d):
    if tree.player_type == 'start':
        d['name'] = 'Game Start'
    else:
        hand = (Card(rank='A', suit='diamonds'), Card(rank='A', suit='hearts'))
        total = tree.get_game_total(hand)
        wins = tree.get_win_total(hand)
        combos = len(tree.card_totals)

        rate = str(round(100 * wins / (1 if total == 0 else total),0))
        
        mapping = {'current': 'you', 'opponent 1': 'computer'}

        d['name'] = str(mapping[tree.player_type] + ' ' + tree.player_action) + ' ({}%)'.format(rate)
    
    if tree.player_type != 'start':
        d['parent'] = str(tree.parent.id)

    d['children'] = []
    for rel in sorted(tree.relations,reverse=True):
        if tree.relations[rel] is None or rel == 'fold':
            continue 
        new_d = {}
        recurse(tree.relations[rel],new_d)
        d['children'].append(new_d)

    if len(d['children']) == 0:
        del d['children']
    
    return None

treeData = [
  {
    "name": "Top Level",
    "parent": "null",
    "children": [
      {
        "name": "Level 2: A",
        "parent": "Top Level",
        "children": [
          {
            "name": "Son of A",
            "parent": "Level 2: A"
          },
          {
            "name": "Daughter of A",
            "parent": "Level 2: A"
          }
        ]
      },
      {
        "name": "Level 2: B",
        "parent": "Top Level"
      }
    ]
  }
]

pickled_file = 'MCST.pickle' # previous code generated this file
if os.path.exists(pickled_file):
    with open(pickled_file, 'rb') as handle:
        trees = pickle.load(handle)

new_tree = trees.get_game(('current','opponent 1'))

d = {}
recurse(new_tree.get_root(),d)

json_for_d3 = json.dumps(d, indent=4, sort_keys=True)

with open('mcts.json','w') as new_file:
    new_file.write(json_for_d3)