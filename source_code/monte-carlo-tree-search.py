#!/usr/bin/env python3

import math

def UCB(wins,games,parent_total,constant):
    if games == 0 or parent_total == 0:
        raise Exception("UCB requires games or parent total")
    return wins / games + constant * math.sqrt(math.log(parent_total)/games)

class DecisionNode(object):
    
    def __init__(self):
        self.expected_value = 0
        self.total = 0
        self.fold = None
        self.call = None
        self.bet = None

class MCST(object):

    def __init__(self,player_count=2):
        self.root = DecisionNode()
        self.player_count=player_count

    def get_root(self):
        return self.root

if __name__ == '__main__':
    print("starting MCTS")
    root = MCST()
    print(root)
    