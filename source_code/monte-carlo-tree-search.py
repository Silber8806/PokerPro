#!/usr/bin/env python3

import math
import itertools

def UCB(wins,games,parent_total,constant):
    if games == 0 or parent_total == 0:
        raise Exception("UCB requires games or parent total")
    return wins / games + constant * math.sqrt(math.log(parent_total)/games)

class GenericNode(object):

    id_iter = itertools.count()

    def __init__(self):
        self.id = next(self.id_iter)
        self.expected_value = 0
        self.total = 0
        self.fold = None 
        self.call = None 
        self.bet = None

    def print_tree(self,level=0):
        print(level * "\t" + str(self))
        if self.fold is None and self.call is None and self.bet is None:
            return None 
        else:
            level += 1
            for branch_type in ['fold','call','bet']:
                branch_child = getattr(self,branch_type)
                if branch_child is not None:
                    branch_child.print_tree(level)

    def __repr__(self):
        return 'node ' + str(self.id)

class CardNode(GenericNode):
    def __init__(self):
        super().__init__()

class OpponentNode(GenericNode):
    def __init__(self):
        super().__init__()

class DecisionNode(GenericNode):
    def __init__(self):
        super().__init__()

class MCST(object):

    def __init__(self,player_actions,active_player):
        self.action_history=player_actions
        self.active_player=active_player
        self.root = None

    def set_root(self,node):
        self.root = node
        return None

    def construct_tree(self):
        current_player = self.active_player

        if len(self.action_history) == 0:
            return None

        action_history_iter = iter(self.action_history)
        phase, player, bid_type, amount_bid = next(action_history_iter)

        last_node, last_action = DecisionNode() if player == current_player else OpponentNode(), bid_type

        self.set_root(last_node)

        for action in action_history_iter:
            phase, player, bid_type, amount_bid = action
            if player == current_player:
                new_node = DecisionNode()
            else:
                new_node = OpponentNode()

            setattr(last_node, last_action, new_node)

            last_node, last_action = new_node, bid_type

    def __repr__(self):
        self.root.print_tree()
        return 'MSCT_Tree'

example_player_actions = [('pre_flop_1', 'players_1', 'call', -5), ('pre_flop_1', 'players_2', 'call', 0), ('pos_flop_card_1_bid_round_1', 'players_1', 'call', 0), ('pos_flop_card_1_bid_round_1', 'players_2', 'call', 0), ('pos_flop_card_2_bid_round_1', 'players_1', 'call', 0), ('pos_flop_card_2_bid_round_1', 'players_2', 'call', 0), ('pos_flop_card_3_bid_round_1', 'players_1', 'call', 0)]
example_player = 'players_1'

if __name__ == '__main__':
    print("starting MCTS")
    MCST_tree = MCST(example_player_actions,example_player)
    MCST_tree.construct_tree()
    print(MCST_tree)
    