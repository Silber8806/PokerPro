#!/usr/bin/env python3

import math

def UCB(wins,games,parent_total,constant):
    if games == 0 or parent_total == 0:
        raise Exception("UCB requires games or parent total")
    return wins / games + constant * math.sqrt(math.log(parent_total)/games)

class OpponentNode(object):

    def __init__(self):
        self.expected_value = 0
        self.total = 0
        self.fold = None 
        self.call = None 
        self.bet = None 

class DecisionNode(object):
    
    def __init__(self):
        self.expected_value = 0
        self.total = 0
        self.fold = None
        self.call = None
        self.bet = None

class MCST(object):

    def __init__(self,player_actions,active_player):
        self.root = DecisionNode()
        self.action_history=player_actions
        self.active_player=active_player

    def get_root(self):
        return self.root

example_player_actions = [('pre_flop_1', 'players_1', 'bid', -5), ('pre_flop_1', 'players_2', 'bid', 0), ('pos_flop_card_1_bid_round_1', 'players_1', 'bid', 0), ('pos_flop_card_1_bid_round_1', 'players_2', 'bid', 0), ('pos_flop_card_2_bid_round_1', 'players_1', 'bid', 0), ('pos_flop_card_2_bid_round_1', 'players_2', 'bid', 0), ('pos_flop_card_3_bid_round_1', 'players_1', 'bid', 0)]
example_player = 'players_1'

if __name__ == '__main__':
    print("starting MCTS")
    root = MCST(example_player_actions,example_player)
    print(root)
    