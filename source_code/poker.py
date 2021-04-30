#!/usr/bin/env python3

import sys
import os
import csv
import random
import itertools
import collections
import time
import math
import copy
import pandas as pd

from collections import Counter
from multiprocessing import Pool
from functools import partial

#pip install numpy
import numpy as np

# named tuple is a tuple object (immutable type) that also has names.  
# immutable means once created they can't be modified.
# named tuple means you can access properties via . notation
# so if you have a card instance: card.suit and card.rank
# should return the suit and rank respectively.
Card = collections.namedtuple('Card', ['rank', 'suit'])

# maps card ranks to integers
RankMap = {rank:i+1 for i, rank in enumerate([str(n) for n in range(2, 11)] + list('JQKA'))}
Ranks = [str(n) for n in range(2, 11)] + list('JQKA')
PokerHierachy ={'high_card':1,'one_pair':2,'two_pair':3,'three_of_kind':4,'straight':5,'flush':6,'full_house':7,'four_of_kind':8,'straight_flush':9}
PokerInverseHierachy={poker_number:name for name,poker_number in PokerHierachy.items()}

# the stupidest way of preserving an index, your welcome 
global debug

# set debug to one, to see these messages in __main__
def dprint(message):
    if debug == 1:
        print(message)
    return None

# function for converting a card to characters used mostly in Table.run_analysis
def card_to_char(card):
    if card:
        return card.rank + card.suit[0]
    else:
        return '00'

# fucntion for converting card to string... simlar to the above.
def card_to_string(card):
    if card:
        return card.rank + '-' + card.suit
    else:
        return 'Z-N/A'

# used to take a list and chunk it into a list of n-tuples
# found this on stackoverflow for chunking lists and used
# directly for that puporse.
def chunk(lst, n):
    """ 
        This just chunks a list into pieces, found on stackoverflow
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def card_reduced_set(cards):
    """ 
    reduces a card set to prevent combinatorial redundencies:
    A hearts, A spades has same probability as A hearts, A clubs etc
    reference it as A, A, opposing pair instead.
    """
    if len(cards) != 2:
        raise Exception("Only 2 cards can be scored")
    card1, card2 = cards 

    if card1.suit == card2.suit:
        card_suited = "Same"
    else:
        card_suited = "Diff"

    sorted_ranks = sorted([card1.rank, card2.rank],key=lambda card: RankMap[card])
    sorted_ranks.append(card_suited)

    return tuple(sorted_ranks)

def method_exists(instance, method):
    """
        check if a method exists on an instance,
        used in post_hook function.
    """
    test_method = getattr(instance, method, None)
    if callable(test_method):
        return True
    return False

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
        """
            sets up the Deck.
        """
        self.ranks = [str(n) for n in range(2, 11)] + list('JQKA')
        self.suits = 'spades diamonds clubs hearts'.split()
        standard_card_deck = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        self.all_cards = standard_card_deck[:]
        random.shuffle(standard_card_deck)
        self.cards = standard_card_deck
        self.removed_cards = []
        self.saved_deck = None
        self.saved_removed_deck = None
        return None

    def set_seed(self,seed):
        random.seed(seed)
        return None

    def save_deck(self):
        """ save the deck and go back to it using the load_deck command"""
        self.saved_deck = self.cards[:]
        self.saved_removed_deck = self.removed_cards[:]
        return None

    def load_deck(self):
        """ load the deck from the save point created by save_deck command """ 
        if self.cards and self.removed_cards:
            self.cards = self.saved_deck[:]
            self.removed_cards = self.removed_cards[:]
        return None

    def reshuffle_draw_deck(self):
        """ reshuffle only the draw deck """
        random.shuffle(self.cards)
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
        if hands < 1:
            raise Exception("Error: at least 1 hand needs to be drawn")

        if num_of_cards < 1 or len(self.cards) > 52:
            raise Exception("Error: Tried to draw {} has to be between 1 and {}".format(num_of_cards,len(self.cards)))

        for _ in range(hands):
            if num_of_cards >= len(self.cards):
                self.reshuffle()
            new_draw = self.cards[:num_of_cards]
            self.removed_cards.extend(new_draw)
            self.cards = self.cards[num_of_cards:]
            # yield creates a generator.  A generator is a rule for creating a sequence of items.
            # since it is a rule, it takes up less space than a list or dict or tuple.
            # it also lets you stream a set of cards infinitely if put in a while loop.
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
            return next(self._draw(num_of_cards=num_of_cards,hands=hands)) # lets you use deck.draw(5) to draw 5 cards
        else:
            return self._draw(num_of_cards=num_of_cards,hands=hands) # if you specify number of hands, it creates a generator, you have to use a for loop on it.

    def _permute(self,num_of_cards,hands=1):
        """ 
            internal class to handle the logic
            for creating a generator for permute class
        """
        if num_of_cards < 1 or num_of_cards > len(self.cards):
            raise Exception("Error: Draw has to be between 1 and 52".format(len(self.cards)))

        if hands < 1:
            raise Exception("Error: at least 1 hand needs to be drawn")

        for _ in range(hands):
            new_draw = self.cards[:]
            random.shuffle(new_draw)
            yield new_draw[:num_of_cards]

    def permute(self,num_of_cards,hands=1):

        """
        permute(num_of_cards)

        returns <num_of_cards> permutation.  Doesn't reshuffle (based on current deck)
        or alter any states.

        permute(num_of_cards, hands)

        returns a generator, which returns <hands>
        number of permutations.
        """

        if hands == 1:
            return next(self._permute(num_of_cards=num_of_cards,hands=hands))
        else:
            return self._permute(num_of_cards=num_of_cards,hands=hands)

    def remove_card(self,rank,suit):
        """
            Take your deck and try to remove a card with a certain rank and suit
            This is used to simulate outcomes in the Player class.

            What it does high-level, it checks if a card exists in the deck,
            if it does, it removes it to the discard.  If it's not in the draw
            it makes sure it's in the discard.  If it's in neither the 
            draw or discard piles, it errors out.
        """
        card_to_find = Card(rank = rank, suit = suit)
        if card_to_find not in self.all_cards:
            raise Exception("ERROR: card is a non-standard card type")

        index = 0
        found_index = -1
        for card in self.cards:
            if card == card_to_find:
                found_index = index
            index = index + 1
        
        if found_index == -1:
            try:
                self.removed_cards.index(card_to_find)
            except:
                Exception("ERROR:card is missing from the deck completely")
        else:
            removed_card = self.cards.pop(found_index)
            self.removed_cards.append(removed_card)
        
        return None

    def __str__(self):
        return "French Deck ({} of {} cards remaining)".format(len(self.cards),len(self.all_cards))

simulate_win_odds_cache = {}

def simulate_win_odds(cards,river,opponents,runtimes=100):
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
    use_cache = 0

    if river is None:
        river = []  # this is a pre-flob situation

    card_cache = [c for c in sorted(cards,key=lambda c: RankMap[c.rank])]
    river_cache = [c for c in sorted(river,key=lambda c: RankMap[c.rank])]
    cache_key = tuple(card_cache + river_cache)

    if use_cache == 1:
        if cache_key in simulate_win_odds_cache:
            return simulate_win_odds_cache[cache_key]

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

    win_rate = wins/float(runtimes)

    if use_cache == 1:
        simulate_win_odds_cache[cache_key] = win_rate

    return  win_rate # your percent wins

#################Shahin's addition############################################
def is_flush(cards):
    """This function check each players hand for flush and returns dictionary 
    of flush, highest card on flush and the suit"""
    if len(cards)<5: 
        raise Exception("Need at least 5 cards to check for flush")
        return 0
    card_suit=[]
    for card in cards:
        card_suit.append(card.suit)
    card_suits_set=list(Counter(card_suit).keys())
    card_suits_counter=list(Counter(card_suit).values())
    if max(card_suits_counter)>=5:
        flush_count=max(card_suits_counter)
        flush_suit=card_suits_set[card_suits_counter.index(flush_count)]
        flush_cards=[]
        flush_rank=[]
        for card in cards:
            if card.suit==flush_suit:
                flush_cards.append(card)
                #Find highest flush
                flush_rank.append(Ranks.index(card.rank))
        return {'flush':{'suit':flush_suit,'flush_cards':flush_cards,'High_flush_on':max(flush_rank)}}


def is_straight(cards):
    """This function check for straight and straight flush
    It returns highes straight flush if it exist, in case
    there is no straight flush, it will return highest straight if it exists"""
    straight_flush=False
    straight={}
    card_rank=[]
    card_suit=[]
    deck=FrenchDeck()
    Ranks=deck.ranks
    for card in cards:
        card_rank.append(Ranks.index(card.rank))
        card_suit.append(card.suit)
    sort_rank=sorted(set(card_rank))
    "need to have at least 5 different ranking to check for straight"
    if len(sort_rank)>4:
        #check for lowest possible rank with Ace counting as 1
        if max(sort_rank)==12:
            if sort_rank[3]==3:
                straight_cards=[]
                for card in cards:
                    if Ranks.index(card.rank) in [0,1,2,3,12]:
                        straight_cards.append(card)
                if is_flush(straight_cards):
                    straight_flush=True
                    straight={'straight_flush':{'suit':is_flush(straight_cards)['flush']['suit'],'High_straight_on':5}}
                else: 
                    straight={'High_straight_on':5}

        #iterating over each set of card with 5cards to check for straight
        card_index=0
        while len(sort_rank)-card_index>=5:
            #checking if we have straight flush or not.
            if sort_rank[card_index+4]-sort_rank[card_index]==4:
                straight_cards=[]
                for card in cards:
                    if Ranks.index(card.rank) in sort_rank[card_index:card_index+5]:
                        straight_cards.append(card)
                #print('straight_cards hand is=', straight_cards)
                if is_flush(straight_cards):
                    straight_flush=True
                    straight={'straight_flush':{'suit':is_flush(straight_cards)['flush']['suit'],'High_straight_on':sort_rank[card_index+4]}}
                else: 
                    if straight_flush==False:# Dont count straight if you have straight flush
                        straight={'High_straight_on':sort_rank[card_index+4]}
            card_index+=1
    return straight

def is_fullHouse(cards):
    'This function returns the fullhouse hand with its trips and pair cards'
    card_rank=[]
    high_fullhouse=[]
    fullhouse_dic={}
    deck=FrenchDeck()
    Ranks=deck.ranks
    for card in cards:
        card_rank.append(card.rank)
    rank_set=list(Counter(card_rank).keys())
    rank_repetition=list(Counter(card_rank).values())
    "getting numerical value of each rank for comparison"
    numeric_rank_set=[Ranks.index(r) for r in rank_set]
    sort_rank=sorted(numeric_rank_set)
    fullhouse=[numeric_rank_set[i] for i,j in enumerate(rank_repetition) if (j==2 or j==3)]
    threekind_list=[numeric_rank_set[i] for i,j in enumerate(rank_repetition) if j==3]
    "checking condition for fullhouse"
    if ((len(threekind_list)>0) & (len(fullhouse)>1)):
        max_threekind=max(threekind_list)
        "Adding highest three of a kind"
        high_fullhouse.append(fullhouse.pop(fullhouse.index(max_threekind)))
        "Adding the second highest card, can be three of the kind or two of the kind"
        max_pair=max(fullhouse)
        high_fullhouse.append(fullhouse.pop(fullhouse.index(max(fullhouse))))
        fullhouse_dic={'Fullhouse_on':[Ranks[i] for i in high_fullhouse],'Trips_on':max_threekind,'Pairs_on':max_pair}
    return fullhouse_dic
    
def number_of_kind(cards):
    "This function returns highes number of a kind anywhere between 2 to 4 if there is less than 2 of a kind it returns highes card"
    card_rank=[]
    deck=FrenchDeck()
    Ranks=deck.ranks
    for card in cards:
        card_rank.append(card.rank)
    rank_set=list(Counter(card_rank).keys())
    rank_repetition=list(Counter(card_rank).values())
    "getting numerical value of each rank for comparison"
    numeric_rank_set=[Ranks.index(r) for r in rank_set]
    max_repetition=max(rank_repetition)
    sort_rank=sorted(numeric_rank_set)
    kicker_card=list()
    if max_repetition==4:
        """Returns 4 of a kind and use remaining 1 card for kicker-card in case they have the same 
        4 of the kind"""
        
        "Find next highest card in case highest card is the same as 4 of a kind"
        if Ranks[sort_rank[-1]]==rank_set[rank_repetition.index(max_repetition)]:
            sort_rank.pop(-1)
        kicker_card.append(sort_rank[-1])
        return {'number_of_kind':4,'number_of_kind_on':rank_set[rank_repetition.index(max_repetition)],'kicker_card':kicker_card}
    elif max_repetition==3:
        "No need to check for possibilities of having two three of the kinds"        
        three_kind=[numeric_rank_set[i] for i,j in enumerate(rank_repetition) if j==3]
        assert len(three_kind)<3, "Can not have more than two sets of three of a kind"
        if len(three_kind)>1:
            #assert len(three_kind)>1,"Your code is working fine, but your logic not because if you have more than one three of the kind it should be full house"
            high_three_card=max(three_kind)
            return {'number_of_kind':0}
        else:
            high_three_card=three_kind[0]
        counter=0
        while len(kicker_card)<2:
            "Going to next card if any of the two highest cards are the same as 3 of a kinds"
            if Ranks[sort_rank[-1-counter]]==high_three_card:
                sort_rank.pop(-1-counter)
            kicker_card.append(sort_rank[-1-counter])
            counter+=1
        return {'number_of_kind':3,'number_of_kind_on':high_three_card,'kicker_card':kicker_card}
    elif max_repetition==2:
        #need to check how many pairs we have and then select the highest two pairs if there are more than one.
        pair_rank=[]
        for repeat_index in range(len(rank_repetition)):
            if rank_repetition[repeat_index]==2:
                pair_rank_index=Ranks.index(rank_set[repeat_index])
                pair_rank.append(pair_rank_index)
        number_of_pairs=len(pair_rank)
        if number_of_pairs==1:
            counter=0
            while len(kicker_card)<3:
                "Going to next card if any of the three highest cards are the same as 3 of a kinds"
                if Ranks[sort_rank[-1-counter]]==rank_set[rank_repetition.index(max_repetition)]:
                    sort_rank.pop(-1-counter)
                kicker_card.append(sort_rank[-1-counter])
                counter+=1
            return {'number_of_kind':2,'number_of_pair':1,'number_of_kind_on':Ranks[pair_rank[0]],'sort_order':pair_rank,'kicker_card':kicker_card}
        elif number_of_pairs==2:
            counter=0
            while len(kicker_card)<1:
                "Going to next card if any of the highest cards are the same as 3 of a kinds"
                while Ranks[sort_rank[-1-counter]] in [Ranks[pair] for pair in pair_rank]:
                    sort_rank.pop(-1-counter)
                kicker_card.append(sort_rank[-1-counter])            
            return {'number_of_kind':2,'number_of_pair':2,'number_of_kind_on':[Ranks[(pair_rank[i])] for i in range(2)],'sort_order':sorted(pair_rank,reverse=True),'kicker_card':kicker_card}
        else:
            assert number_of_pairs<4, "Can not have more than 3 pairs"
            pair_rank=sorted(pair_rank)
            #removing lowest pair when we have three pair
            pair_rank.pop(0)
            counter=0
            while len(kicker_card)<1:
                "Going to next card if any of the highest cards are the same as 3 of a kinds"
                while Ranks[sort_rank[-1-counter]] in [Ranks[pair] for pair in pair_rank]:
                    sort_rank.pop(-1-counter)
                kicker_card.append(sort_rank[-1-counter])            
            return {'number_of_kind':2,'number_of_pair':2,'number_of_kind_on':[Ranks[(pair_rank[i])] for i in range(2)],'sort_order':sorted(pair_rank,reverse=True),'kicker_card':kicker_card}
    else:
        assert max_repetition==1, "number of repetition should be between 1 and 4"
        kicker_card=sort_rank[-2::-1]
        return {'number_of_kind':1,'highest_card_on':sort_rank[-1],'kicker_card':kicker_card}

"returning hands scoure in terms of dictionary with their values being a list to make it easier to compare hand at the end"

def score_hand(cards):
    #print("scoring: {}".format(cards))
    """ This function scoring each hand and returning a list as score with priority score starting from item 0 in the score
    for example the highest ranking of the hands given to straight flush, if two people get straight flush then it will look at
    the secon item in the list which is the highest card on their straight flush.
    poker_hierarchy dictionary is used to rank each hand.
    """
    poker_hierarchy={'high_card':1,'one_pair':2,'two_pair':3,'three_of_kind':4,'straight':5,'flush':6,'full_house':7,'four_of_kind':8,'straight_flush':9}
    if (len(cards) != 7):
        raise Exception("Can only score 7 cards")
        return 0
    straightFlush_or_straight=is_straight(cards)
    flush=is_flush(cards)
    fullHouse=is_fullHouse(cards)
    of_a_kind=number_of_kind(cards)
    straight_flush=[]
    straight=[]
    four_of_kind=[]
    three_of_kind=[]
    two_pair=[]
    one_pair=[]
    high_card=[]
    if (straightFlush_or_straight):
        try:
            flush_list=straightFlush_or_straight['straight_flush']
            straight_flush=[poker_hierarchy['straight_flush']]+[flush_list['High_straight_on']]
        except:
            straight=[poker_hierarchy['straight']]+[straightFlush_or_straight['High_straight_on']]
    if of_a_kind:
        if of_a_kind['number_of_kind']==4:
            four_of_kind=[poker_hierarchy['four_of_kind']]+[of_a_kind['number_of_kind_on']]+of_a_kind['kicker_card']
        elif of_a_kind['number_of_kind']==3:
            three_of_kind=[poker_hierarchy['three_of_kind']]+[of_a_kind['number_of_kind_on']]+of_a_kind['kicker_card']
        elif of_a_kind['number_of_kind']==2:
            if len(of_a_kind['sort_order'])==2:
                two_pair=[poker_hierarchy['two_pair']]+of_a_kind['sort_order']+of_a_kind['kicker_card']
            else:
                one_pair=[poker_hierarchy['one_pair']]+of_a_kind['sort_order']+of_a_kind['kicker_card']
        elif of_a_kind['number_of_kind']==1:
            high_card=[poker_hierarchy['high_card']]+[of_a_kind['highest_card_on']]+of_a_kind['kicker_card']
        else:
            #print("number_of_kind function should return number of kind between 1 and 4, but it returned ",of_a_kind['number_of_kind'])
            pass

    if (straight_flush):
        #print("\n\n\n******************************Congratulations**straight**flush****************\n\n\n")
        #print("This set of card is flash on ",straight_flush)
        return straight_flush
    elif four_of_kind:
        #print("\n\n\n******************************Congratulations**four*of*a*kind****************\n\n\n")
        return four_of_kind
    elif fullHouse:
        #print("\n\n\n******************************Congratulations**fullhouse****************\n\n\n")
        return [poker_hierarchy['full_house']]+[fullHouse['Trips_on']]+[fullHouse['Pairs_on']]
    elif flush:
        #print("\n\n\n******************************Congratulations**flush******************\n\n\n")
        #print("This set of card is flash on ",flush['flush']['High_flush_on'])
        return [poker_hierarchy['flush']]+[flush['flush']['High_flush_on']]
    elif straight:
        #print("\n\n\n******************************Congratulations**straight******************\n\n\n")
        #print("This set of card is high straight on ",straight)
        return straight
    elif three_of_kind:
        #print("\n\n\n******************************Congratulations**three*of*a*kind****************\n\n\n")
        return three_of_kind
    elif two_pair:
        #print("\n\n\n******************************Congratulations**two*pairs****************\n\n\n")
        return two_pair
    elif one_pair:
        #print("\n\n\n******************************Congratulations**one*pair****************\n\n\n")
        return one_pair
    elif high_card:
        #print("\n\n\n******************************Congratulations**high*card****************\n\n\n")
        return high_card
    else:
        #print('No ranking was found on this hand, check your score function')
        pass
    
    


################end of functions defined by Shahin ###########################

def winning_hand(hands):
    """ 
        used in the simulate_win_odds function.  This needs to be implemented still.
        Right now it just randomly picks win or lose.  Use the hand score function
        here and than check if 1st entry has highest rank.
    """
    winning_hand=[]
    hand_scores = []
    player_scores=[]
    for hand in hands:
        score = score_hand(hand)
        if winning_hand<score:
            winning_hand=score 
        hand_scores.append(score)
    for player,hand in enumerate(hands):
        if score_hand(hand)==winning_hand:
            player_scores.append(1)
        else:
            player_scores.append(0)
    # if 1st hand did not win return 0 else 1
    return player_scores[0]

class GenericPlayer(object):

    """
        This class will keep information about the player between games and 
        also stores the players strategy and decision making abilities.  
        More types of play to be added later.
    """

    def __init__(self,name,balance):
        """
            initialize player
        """
        self.name = name
        self.balance = balance # players bank account
        self.beginning_balance = self.balance
        self.bet = 0
        self.wins = 0
        self.loses = 0
        self.decisions = ['fold','check','call','bet']
        self.strategy = None
        self.balance_history = []
        self.hand_history = []
        self.games_played = []
        self.predicted_win = []
        self.call = 0
        self.current_bet = 0
        self.final_bet = 0
        self.bid_number = 0
        self.registered_balance = balance
        self.folded_this_game = 0
        self.last_survivor_this_game = 0
        self.won_game = 0
        self.final_hand = None
        self.blind_type = 'None'
        self.hand_dictionary={i+j+k:{'sum_absolute_bet':0,'sum_bet':np.array([0,0,0],dtype=float)} for i in(Ranks) for j in(Ranks) for k in(['N','Y'])} 
        self.current_game = None
        self.active_game = None
        self.pre_flob_wins = {}
        self.short_memory=None # this remembers the immidiate game number to compare it with current game for simpleLearnerPlayer

    def register_for_game(self,game):
        """
            Register a player for a game, making sure that a lot of attributes
            that keep track of state are reinitialized.  A lot of these attributes
            are used for reporting purposes later on.
        """
        game_id = game.id
        self.games_played.append(game_id)
        self.current_game = game_id
        self.active_game = game
        self.bid_number = 0
        self.registered_balance = self.balance
        self.folded_this_game = 0
        self.last_survivor_this_game = 0
        self.won_game = 0
        self.blind_type = 'None'
        self.final_hand = 'None'
        return None 

    def set_final_hand(self,hand_number):
        self.final_hand = PokerInverseHierachy[hand_number]
        return None

    def get_blind(self):
        return self.blind_type

    def set_blind(self,blind_type=None):
        """
            use this to make a person a small or large blind,
            used for reporting purposes.
        """
        self.blind_type = blind_type
        return None

    def update_balance_history(self):
        """
            update an entry for a game played to be exported later, this represents 
            a row in a data frame later on in jupyter analysis.  See Table.run_analysis
            for how that is handled.
        """
        if self.won_game == 1:
            end_game_result = 'won'
        else:
            end_game_result = 'lost'

        if self.folded_this_game == 1:
            player_status = 'fold'
        elif self.last_survivor_this_game == 1:
            player_status = 'last_man_standing'
        elif self.won_game == 1:
            player_status = 'won_game'
        else:
            player_status = 'lost_game'

        # this represents a row in the data analysis for this specific player.
        self.balance_history.append([self.current_game, end_game_result, player_status, self.blind_type, self.final_hand, self.beginning_balance, self.registered_balance, self.balance, self.balance - self.registered_balance])
        return None

    def get_pot(self,pot_value):
        """
            You get the pot and add it to you balance.
        """
        self.balance = self.balance + pot_value
        self.won_game = 1
        return None

    def pay_bid(self,pay_bid):
        """ 
            Once you make a bet, you pay the difference between your 
            current bid and the new bid here.
        """
        if pay_bid < 0:
            raise Exception("amount ${} bet needs to be positive!".format(pay_bid))
        if self.balance - pay_bid < 0:
            raise Exception("amount paid: {} is greater than balance {}".format(pay_bid,self.balance))
        else:
            self.balance = self.balance - pay_bid

    def get_all_player_actions(self):
        if self.active_game is None:
            raise Exception("Can't access player history of non-existent game")

        return self.active_game.get_player_actions()

    def get_beginning_players(self):
        if self.active_game is None:
            raise Exception("Can't access player history of non-existent game")
        return self.active_game.get_beginning_players()

    def _set_up_bet(self,opponents,call_bid,current_bid,raise_allowed=False):
        """
            sets up some basic context for a betting round.  Used by make_bet
            to attach certain betting conditions to the player.
        """
        self.opponents = opponents
        self.call = call_bid
        self.current_bet = current_bid
        self.raise_allowed = raise_allowed
        return None

    def _last_man_standing(self):
        """
            in any bid, if you are the last player still playing, you can 
            win by just calling or checking the bid.  This prevents 
            players from folding if they would have won as the last
            non-folded player on the table.
        """
        if self.opponents == 0:
            dprint("{} - is last man standing".format(self.name))
            self.call_bet()
            self.last_survivor_this_game = 1
            return 1
        return 0

    def _raise_bet(self,raise_amount,allow_all_in=True):
        """
            private method for making a raise.
        """
        dprint("{} - raises {}".format(self.name,raise_amount))
        if self.call + raise_amount > self.balance and allow_all_in == True:
            bet_amount = self.balance
        elif self.call + raise_amount > self.balance and allow_all_in == False:
            bet_amount = None
        else:
            bet_amount = self.call + raise_amount

        if bet_amount:
            self.pay_bid(bet_amount)
            self.final_bet = self.current_bet + bet_amount
            return bet_amount
        else:
            self.final_bet = None
            return None

    def call_bet(self,allow_all_in=True):
        """
            Use this method in a subclassed version of GenericPlayer in the 
            as a bet_stregty to orchestrate a call.  final_bet used here
            is supposed to be hidden in that method, but does the accounting
            for the player.  Note, if you allow_all_in=True, if your required
            bid is higher than your balance you will go all in.  Set this 
            to false to fold if the bid is higher than your balance.
        """
        dprint("{} - calls/checks".format(self.name))
        if self.call > self.balance and allow_all_in == True:
            bet_amount = self.balance
        elif self.call > self.balance and allow_all_in == False:
            bet_amount = None
        else:
            bet_amount = self.call

        if bet_amount is not None:
            self.pay_bid(bet_amount)
            self.final_bet = self.current_bet + bet_amount
            return bet_amount
        else:
            self.final_bet = None
            return None

    def raise_bet(self,raise_amount,allow_all_in=True):
        """
            if raise allowed, raise that amount, else call.
            allow_all_in = false causes you to fold if you
            have to use all your chips and can't meet the 
            balance.
        """
        if self.raise_allowed:
            self._raise_bet(raise_amount,allow_all_in)
        else:
            self.call_bet()

    def fold_bet(self):
        """ 
            fold your hand....
        """
        dprint("{} - folds".format(self.name))
        self.final_bet = None
        self.folded_this_game = 1
        return None

    def record_bet(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """ 
            This method is used in make_bet to record the hand and a lot of the statistics
            associated with it.  See table.run_analysis and the poker_hands.csv to see it.
        """
        # currently not implemented...use this one to record bets...
        self.bid_number += 1
        river_set = [None for _ in range(5)]
        if river is not None:
            for i,card in enumerate(river):
                river_set[i] = card
        hand = [card_to_string(card) for card in sorted(hand,key=lambda c: RankMap[c.rank] if c else 99)]
        if river_set:
            river_set = [card_to_string(card) for card in sorted(river_set,key=lambda c: RankMap[c.rank] if c else 99)]
        data_tuple = [self.current_game, self.name, self.__class__.__name__, self.bid_number,opponents,call_bid,current_bid,self.final_bet,pot,raise_allowed] + hand + river_set
        self.hand_history.append(data_tuple)
        return None

    def make_bet(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
            This is a method that checks if the player is the last man standing.  If he 
            is, automatically wins the round.  If he is not, it calls self.bet_strategy, 
            which is not part of GenericPlayer, but is instead used by subclasses of the
            player to implement custom strategies.  record_bet made after bet_strategy
            records the hand.  Don't manipulate this, instead inherit from this class
            and make your own strategy using a bet_strategy method.  Think of this 
            more like a dispatcher that links a players betting decisions to a game.
        """
        self._set_up_bet(opponents,call_bid,current_bid,raise_allowed)
        if (self._last_man_standing()):
            dprint("is last man")
            self.record_bet(hand,river,opponents,call_bid,current_bid,pot,raise_allowed)
            return self.final_bet
        self.bet_strategy(hand,river,opponents,call_bid,current_bid,pot,raise_allowed)
        self.record_bet(hand,river,opponents,call_bid,current_bid,pot,raise_allowed)
        return self.final_bet

    def __repr__(self):
        return "{}".format(self.name)

    def __str__(self):
        return "{} [balance: ${}]".format(self.name,self.balance)

class Game(object):
    """
        Game implements an actual poker game.  It has all the mechanics to do
        pre-flob, post-flob and scoring of games.  The 
    """
    def __init__(self,game_id,cards,players,minimum_balance_to_join):
        self.id = str(game_id)
        self.cards = cards
        self.river = cards[:5]
        self.winner = None
        self.big_blind = 10
        self.small_blind = 5
        # you need a minimum balance otherwise, players with $0 will join your game.
        self.minumum = minimum_balance_to_join
        self.players = [{"player": player, "active": 1, "hand": None, "bet": 0} for player in players if player.balance > self.minumum] # get rid of losers that don't have enough money
        self.player_actions = []

        for player in players:
            player.register_for_game(self) # get the unique memory id for the game

        # every poker game has a small and big blind to prevent people from always folding unless they have pocket aces.
        self.players_left_at_start = len(self.players)

        if self.players_left_at_start > 1:
            self.players[-1]['bet'] = self.big_blind
            self.players[-1]['player'].pay_bid(self.big_blind)
            self.players[-1]['player'].set_blind('big')
            self.players[-2]['bet'] = self.small_blind 
            self.players[-2]['player'].pay_bid(self.small_blind)
            self.players[-2]['player'].set_blind('small')
        
    def get_current_pot(self):
        """
            adds all current bets from all players to get the pot 
        """
        current_pot = 0
        for player in self.players:
            current_pot += player['bet']
        return current_pot

    def get_required_bid(self):
        """
            goes through all the bids to determine what a player needs to bid to still stay active.
        """
        required_bid = 0
        for player in self.players:
            required_bid = max(required_bid,player['bet'])
        return required_bid

    def get_num_active_opponents(self):
        """
            how many opponents each player still has.  Used by players to make bettign decisions
        """
        return len(self.get_active_players()) - 1

    def get_active_players(self):
        """
            get only those players that are still active.
        """
        return [player for player in self.players if player['active']]

    def all_players_checked(self):
        """
            if all players have the same bet, you have to proceed to the next round in poker.
            Use this to check that condition and skip 2nd or 3rd round of betting.
        """
        unique_bets = len(list(set([player['bet'] for player in self.players])))
        if unique_bets == 1:
            return True 
        else:
            return False

    def update_player_actions(self,player_name,action,bid):
        """ 
            Keep player history so that you can look it up for strategies for example
            MCTS simulations etc.
        """
        update_tup = ('player', player_name,action,bid)
        self.player_actions.append(update_tup)
        return None

    def update_player_actions_cards(self,card):
        """ 
            Keep player history so that you can look it up for strategies for example
            MCTS simulations etc.
        """

        self.player_actions.append(('card',card))
        return None

    def get_player_actions(self):
        return self.player_actions

    def set_beginning_players(self):
        self.beginning_players = [player['player'].name for player in self.players]
        return None

    def get_beginning_players(self):
        return self.beginning_players

    def pre_flop(self):
        """
            This is actually part of the game.  The way it works is that each player gets 
            2 cards.  The river has not been flipped yet.  Since this is limited hands
            poker, each player can bid for 3 rounds.  We artificially disallow raises
            on the last hand to make sure all players bid the same amount in the ending.
            players that try to bid more than they have just end up going all in.
        """
        for player, hand in zip(self.players,chunk(self.cards[5:],2)):
            player['hand'] = hand

        self.set_beginning_players()

        dprint("pre-flob bidding")
        # max bid on limit poker is 3 rounds
        current_river = None

        for turn in range(1,4):  # limited texas hold-em has 3 rounds max
            dprint("pre-bid round: {}".format(turn))
            for player in self.get_active_players():  # always remove those people that folded from turnss
                agent = player['player'] # get player object for method calls
                current_opponents = self.get_num_active_opponents() # how many opponents does player have
                current_hand = player['hand'] # what's the players current hand
                required_bid = self.get_required_bid() # players bid to proceed to next round
                current_bid = player['bet'] # players current bet
                call_bid = required_bid - current_bid # player needs this much to continue
                raise_allowed = turn != 3 # if 3rd turn, don't let the player raise
                bid = agent.make_bet(current_hand, current_river, current_opponents,call_bid, current_bid, self.get_current_pot(),raise_allowed) # player submits the new bid
                dprint("current {} for {}".format(bid,player['player']))
                if bid is None:  # if the player folded...than return None, they no longer have a bid
                    player['active'] = 0 
                    player_bid = None
                    final_action = 'fold'
                else:
                    player['bet'] = bid # if they returned a bid, use it here.
                    player_bid = bid - required_bid
                    if player_bid > 0:
                        final_action = 'bet'
                    else:
                        final_action = 'call'
                self.update_player_actions(agent.name,final_action,player_bid)

            opponents_left = self.get_num_active_opponents()
            if (opponents_left == 0):  # if 1 player is left quit bidding
                break

            all_checked = self.all_players_checked()
            if (all_checked): # if all players agreed on the same bid quit
                break

            dprint("current pot is: ${}".format(self.get_current_pot()))

        return None

    def post_flop(self):
        """
            In the post-flob phase, the small and big blinds go first.  The river shows the 
            first 3 cards.  Than 3 rounds of betting occur each.  The last round as customary
            no raises can happen.  During each round, 1 new card is added to the river.  
            Players can either: fold, check, call, raise or go all in.  Once the post-flop
            ends, the results are scored by the score_game method.
        """

        self.players = self.players[-2:] + self.players[:-2]  # handle post-flop starts at small blind by poker rules

        dprint("post flob bidding")
        for turn in range(1,4):
            num_of_river_cards=turn + 2  # determine number of cards in the river
            current_river = self.river[:num_of_river_cards] # the new river with the added 3 or 1 cards
            dprint("starting river turn: {}".format(turn))
            dprint("current community/river is: {}".format(current_river))
            self.update_player_actions_cards(current_river)
            for bidding_round in range(1,4):  # here we start the 3 bidding rounds
                dprint("bidding round is: {}".format(bidding_round))
                for player in self.get_active_players():  # only players that did not fold can play
                    agent = player['player'] # get player method for agent calls
                    current_opponents = self.get_num_active_opponents() # get number of opponents for player
                    current_hand = player['hand'] # players current hand
                    required_bid = self.get_required_bid() # total bid required to bet in next round
                    current_bid = player['bet'] # players current bid
                    call_bid = required_bid - current_bid # extra bet required to continue
                    raise_allowed = bidding_round != 3 # don't allow raises on 3rd round
                    bid = agent.make_bet(current_hand,current_river,current_opponents,call_bid, current_bid, self.get_current_pot(),raise_allowed) # the agent submits his bid based on the info he has
                    dprint("current {} for {}".format(bid,player['player']))
                    if bid is None:
                        player['active'] = 0 # if the player folds, he leaves the game
                        player_bid = None
                        final_action = 'fold'
                    else:
                        player['bet'] = bid # if he makes a bet, it becomes his new bet
                        player_bid = bid - required_bid
                        if player_bid > 0:
                            final_action = 'bet'
                        else:
                            final_action = 'call'
                    self.update_player_actions(agent.name,final_action,player_bid)

                opponents_left = self.get_num_active_opponents()
                if (opponents_left == 0): # if 1 player is left finish the current bidding round
                    break

                all_checked = self.all_players_checked() # if all players agree on bid finishe the current bidding round
                if (all_checked):
                    break

                dprint("current pot is: ${}".format(self.get_current_pot()))

            opponents_left = self.get_num_active_opponents()
            if (opponents_left == 0): # if only 1 person is left after a bidding round finish post flob 
                break
        return None

    def score_game(self):
        """ 
            This needs to be fleshed out.  This part should take all active players, score there hands, determine a winner or 
            winners in the case of a true tie.  Than give/split the pot accordingly.  Requires the score_hand function,
            which is not implemented yet.  This function currently has a dummy function for testing purposes, which:

            1. sees how many people have not folded
            2. divides the pot between them
            3. any extra goes to the casino
        """
        # dumb currently, just split pot evenly until we get proper scoring hand function
        all_scored_hands = []
        for player in self.get_active_players(): # this is the actual function, still needs to be implemented
            dprint("checking win condition for {}".format(player))
            player_hand_score = score_hand(player['hand'] + self.river)
            all_scored_hands.append(player_hand_score)
            player['player'].set_final_hand(player_hand_score[0])

        best_hand = max(all_scored_hands)
        winners = [1 if hand == best_hand else 0 for hand in all_scored_hands]
        number_of_winners = sum(winners)
        reward = self.get_current_pot()
        reward_per_player = reward / float(number_of_winners)

        for player in self.get_active_players():
            players_scored_hand = score_hand(player['hand'] + self.river)
            if players_scored_hand == best_hand:
                player['player'].get_pot(reward_per_player)

        for player in self.players: 
            player['player'].update_balance_history()

        for player in self.players:
            player_to_test = player['player']
            if method_exists(player_to_test,'post_game_hook'):
                player_to_test.post_game_hook()

        return None

    def run_game(self):
        """
            This runs each phase of the game
        """
        dprint("")
        dprint("start game")

        if self.players_left_at_start < 2:
            dprint("skipping game since no players left to play: {}".format(self.id))
            return None

        self.pre_flop()
        self.post_flop() # re-working post_flop
        self.score_game() # re-working score game
        dprint("end game")
        dprint("")
        return None

    def __str__(self):
        return "Game with {} players".format(self.players)

class Table():
    """ 
        This class sets up a table, starts the simulation by instantiating a FrenchDeck
        and than streams a set of cards, which it uses per game.  This needs to be 
        flehsed out a bit.
    """
    def __init__(self,table_id,scenario_name,player_types,beginning_balance,minimum_play_balance,hands):
        self.scenario_name = scenario_name # what scanario it is being played under, see simulation variable
        self.player_types = player_types # player types for this game, list of class names, which are instantiatd later
        self.player_types_names = '|'.join(sorted([player_type.__name__ for player_type in self.player_types])) # names of the subclasses representing player strategy
        self.players = None # actual player instances (not classes)
        self.balance = beginning_balance # beginning balance for this table
        self.min_balance = minimum_play_balance # minimum balance to join
        self.hands = hands # number of hands for this table
        self.games_played = [] # record of all games played, game id
        self.id = str(int(table_id)) # unique table id for this specific table
        self.start_game_serial = int(table_id) * 1000000

    def add_games_played(self,game_id):
        """
            use this method to add a game to the games_played array.  Each game_id
            represents the unique id of a game
        """
        self.games_played.append(game_id)
        return None

    def initialize_players(self):
        """ create new players with certain balance of dollars to play with"""
        if len(self.player_types) < 2:
            raise Exception("Error: too few players")

        if len(self.player_types) > 6:
            raise Exception("Error: no more than 6 players allowed")

        players = []
        for i, player_type in enumerate(self.player_types): # player types represent GenericPlayer subtype, which gets instantiated here.
            balance = self.balance 
            name = "players_" + str(i + 1)
            new_player = player_type(name,balance) # creates a player instance, player_type is the name of a class.  Note using Class as a 1st class citizen.
            players.append(new_player)

        self.players = players # all the players now instantiated
        
        return players

    def progress_player_turn_order(self):
        """ 
            change the player order.  each time a new game begins, you move the start position forward 1 position.
        """
        self.players = self.players[-1:] + self.players[:-1]
        return None

    def run_simulation(self):
        """
            This starts a simulation for a single table with fixed number of people
        """
        
        start_time = time.time()
        dprint('started poker game')
        deck = FrenchDeck() # French deck of cards used to play the game, you can think of this as the dealer.

        self.initialize_players() # create your players
        
        for _, hand in enumerate(deck.permute(len(self.player_types) * 2 + 5,self.hands)): # start streaming 5 cards + 2 per person.  Permute means it reshuffles each time.
            self.start_game_serial += 1
            game = Game(self.start_game_serial,hand,self.players,self.min_balance) # Start a new game instance with settings, this represents the actual poker game
            self.add_games_played(game.id) # remember to record that this game happened at this table for later analysis
            game.run_game() # start the actual simulation
            self.progress_player_turn_order() # move the turn order for players

        elapsed_time = time.time() - start_time
        dprint("ending poker game: {} games in {} seconds".format(self.hands,round(elapsed_time,2)))
        
        return 0

    def run_analysis(self):
        """
            This part exports data for consumption in Jupyter notebook system.  3 files 
            created below:
            poker_balances*.csv -> think of this as game level information
            poker_hands*.csv -> think of this as information about each persons bet.  Each player makes 12 bets per Game max over 4 different card + community card situations
            poker_table_info*.csv -> think of this information as tying a simulation scenario to a table.

            All the data is pulled from either the table class or the Player class purposely to prevent too much muddling and tight coupling.
            Table class more so since this is a method of the class.  Player is the primary reporting class.
        """

        script_dir = os.path.dirname(__file__)
        data_dir = os.path.join(script_dir,'data')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        file_name = 'poker_balances_' + self.id + '.csv'
        file_loc = os.path.join(data_dir,file_name)

        fieldnames = ['table_id','game_id','player_name','player_type','game_result', 
                                    'game_reason', 'blind_type', 'final_hand', 'beginning_balance',
                                    'game_start_balance','game_end_balance','game_net_change']
        
        with open(file_loc,'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for i,player in enumerate(self.players):
                for history in player.balance_history:
                    data_tuple = [str(self.id)] + [history[0]] + [player.name] + [player.__class__.__name__] + history[1:]
                    writer.writerows([data_tuple])

        file_name = 'poker_hands_' + self.id + '.csv'
        file_loc = os.path.join(data_dir,file_name)

        fieldnames = ["table_id","game_id","player_name","player_type","bet_number",
                                "opponents","call","current","final","pot","allowed",
                                "hand1","hand2","community1","community2","community3",
                                "community4","community5"]

        with open(file_loc,'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames) 
            for player in self.players:
                for history in player.hand_history:
                    data_tuple = [str(self.id)] + history
                    writer.writerows([data_tuple])

        file_name = 'poker_table_info_' + self.id + '.csv'
        file_loc = os.path.join(data_dir,file_name)

        fieldnames = ["table_id","scenario_name","player_types"]

        with open(file_loc,'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames) 
            data_tuple=[str(self.id),self.scenario_name,self.player_types_names]
            writer.writerows([data_tuple])
        return 0

# Write your own classes here to implement a new player strategy
# first you inherit from GenericPlayer, which implements under the cover the mechanisms for joining a game
# use self.call_bet() to make a call or check
# use self.raise_bet(number) to increase your bet by number
# use self.fold to fold.
# automatically does the accounting under the cover.
# feel free to use these variables in making decisions...explained below:
# hand -> 2-card hand the player holds, see Card named-tuple
# river -> 3-4-5 card hand the player holds, see Card named-tuple for details
# opponents -> how many opponents are left
# call_bid -> current amount required to make a call
# current_bid -> current amount already put into pot
# pot -> current pot, basically how much you can earn if you win
# raise_allowed -> influences raise behavior, last round of betting raises aren't allowed so rasies become calls

# The below are some sample classes:
# AlwaysCallPlayer:
# Player will always call no matter what
# AlwaysRaisePlayer:
# player will always raise no matter what
# SmartPlayer:
# raises 10% of the time, else does a monte carlo simulation of hand and calls only if they will most likely win money.

# Player that always calls
class AlwaysCallPlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        self.call_bet()
        return None

# Player that always raises
class AlwaysRaisePlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        self.raise_bet(20)
        return None

# Player that always calls
class CalculatedPlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        win_probabilty = simulate_win_odds(cards=hand,river=river,opponents=opponents,runtimes=100)
        equal_chance_probability = 1 / float(opponents + 1)
        if win_probabilty >= equal_chance_probability:
            self.call_bet()
        else:
            self.fold_bet()
        return None

# Player that always calls
class GambleByProbabilityPlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        win_probabilty = simulate_win_odds(cards=hand,river=river,opponents=opponents,runtimes=100)
        equal_chance_probability = 1 / float(opponents + 1)
        if win_probabilty >= equal_chance_probability:
            self.raise_bet(round(100 * win_probabilty,0))
        else:
            self.fold_bet()
        return None

# conservative player 
## need to check if big blind and small blind still have to pay their bid even if they fold
class ConservativePlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
        This player only plays the hand that has higher than 70% chance of winning. 
        This player will fold if winning odd is less than 70%, call if win probability is 
        between 70% and 80%. Raise by 20% if chance of winning is between 80% and 90%, raise by 
        30% of its balance if chance is between 90% and 95%, raise by 50% if chance is between 
        95% and 99% and goes all in if chance is 100%
        """
        win_probability = simulate_win_odds(cards=hand,river=river,opponents=2,runtimes=100)
        if win_probability>0.5 and win_probability<=0.7:
            self.call_bet()
        elif  win_probability>0.7 and win_probability<=0.9:
            self.raise_bet(round(0.01*self.balance,0))
        elif  win_probability>0.9 and win_probability<=0.95:
            self.raise_bet(round(0.02*self.balance,0))
        elif  win_probability>0.95 and win_probability<=0.99:
            self.raise_bet(round(0.05*self.balance,0))
        elif  win_probability>0.99:
            self.raise_bet(round(0.1*self.balance,0))
        else:
            self.fold_bet()
        return None

# sophisticated player with more complicated strategy.
class SmartPlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
            This is the only strategy for playing cards that I've implemented.  It's not done
            yet.  The gist of it is as follows:

            1. you calculate your win probability using the simulate_win_odds (still needs to score hands to work)
            2. you calculate the expected profit: chance of win * current pot - chance of losing * current bid (should be full bid price)
            3. if you have no opponents, you win, so you call/check and collect your money.
            4. you decide to raise the pot 10% of the time for $10
            5. if you will make a profit, you at minimum check/call.
            6. if you lose money on average, than just fold and get out of the game.

            The return has the following meaning:
            return <number> -> your total bet for this turn.  Most be equal or greater than current_bid + call_bid.
            return None -> you folded this hand and lose all your money.
        """
        win_probabilty = simulate_win_odds(cards=hand,river=river,opponents=opponents,runtimes=100)
        expected_profit = round(win_probabilty * pot - (1 - win_probabilty) * current_bid,2)
        equal_chance_probability = 1 / float(opponents + 1)
        high_probability_of_win = 1.4 * equal_chance_probability

        if win_probabilty > high_probability_of_win:
            self.raise_bet(100)
            return None

        # if you statistically will make money, call the bid else just fold
        if expected_profit > 0:
            self.call_bet()
        else:
            self.fold_bet()
        return None

class simpleLearnerPlayer(GenericPlayer):
    
    def policy(self):
        return 0
    def simpleLearnerCall(self,hand):
        """
        Made this function to make the decision for making call,fold and raise
        """
        hand_rank=[x for x,y in hand]
        hand_suit=[y for x,y in hand]
        
        if hand_suit[0]==hand_suit[1]:
            same_suit='Y'
        else:
            same_suit='N'
        self.dictionary_key=[hand_rank[0]+hand_rank[1]+same_suit,hand_rank[1]+hand_rank[0]+same_suit,'action']#saving the previous hand dictionary and action
       
        #using same probability to play for first hand
        chance=random.random()
        if self.hand_dictionary[self.dictionary_key[0]]['sum_absolute_bet']==0:
            
            if chance<0.33:
                
                self.dictionary_key[2]='fold'
                self.fold_bet()
            elif chance>=0.33 and chance<0.66:
                
                self.dictionary_key[2]='call'
                self.call_bet()
            else:
                
                self.dictionary_key[2]='raise'
                self.raise_bet(20)
        else:
            #print('repeated hand*************************************',self.hand_dictionary[self.dictionary_key[0]]['sum_bet'])
            #print('repeated absolute gain/lost',self.hand_dictionary[self.dictionary_key[0]]['sum_absolute_bet'])
            action=self.hand_dictionary[self.dictionary_key[0]]['sum_bet'].argmax()
            #if self.hand_dictionary[self.dictionary_key[0]]['sum_bet']>0:
            if action==0:    
                
                self.dictionary_key[2]='fold'
                self.fold_bet()
            elif action==1:
                
                self.dictionary_key[2]='call'
                self.call_bet()
            else:
                raise_amount=20#round(100*self.hand_dictionary[self.dictionary_key[0]]['sum_bet']/self.hand_dictionary[self.dictionary_key[0]]['sum_absolute_bet'],0)
                #print('reapeated winning hand,raising by',raise_amount)
                self.dictionary_key[2]='raise'
                self.raise_bet(raise_amount)
        return None
               
    def update_SimpleLearnerReward(self):
        if self.dictionary_key[2]=='fold':
                    for i in range(2):#setting dictionary for both combination
                        self.hand_dictionary[self.dictionary_key[i]]['sum_absolute_bet']+=abs(self.balance_history[len(self.balance_history)-1][8])#updating hand dictionary
                        self.hand_dictionary[self.dictionary_key[i]]['sum_bet']+=np.array([self.balance_history[len(self.balance_history)-1][8],0,0])
        elif self.dictionary_key[2]=='call':
                    for i in range(2):#setting dictionary for both combination
                        self.hand_dictionary[self.dictionary_key[i]]['sum_absolute_bet']+=abs(self.balance_history[len(self.balance_history)-1][8])#updating hand dictionary
                        self.hand_dictionary[self.dictionary_key[i]]['sum_bet']+=np.array([0,self.balance_history[len(self.balance_history)-1][8],0])
        elif self.dictionary_key[2]=='raise':
                    for i in range(2):#setting dictionary for both combination
                        self.hand_dictionary[self.dictionary_key[i]]['sum_absolute_bet']+=abs(self.balance_history[len(self.balance_history)-1][8])#updating hand dictionary
                        self.hand_dictionary[self.dictionary_key[i]]['sum_bet']+=np.array([0,0,self.balance_history[len(self.balance_history)-1][8]])
        else:
            raise Exception('Action must select between fold, call or raise actions')
        return None    
    
    def repeat_action(self):
        if self.dictionary_key[2]=='call':
            
            self.call_bet()
        elif self.dictionary_key[2]=='raise':
            
            self.raise_bet(20)
        else:
            raise Exception('Check your code only two options for repeating actions should be call and raise')
        return None
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
        This player is a very simple learner, it looks at the first two card and make the decision on
        whether to call, raise or fold based on the first two call. Player has 3 simple policies, fold, call and raise by 20.
        we selected the same betting amount as we had for always call and always raise players in order to be able to compare the results.
        Player starts learning by playing games, at first he randomly selects between different policy (fold, call and raise) and sotre the
        final results "game net change" as its rewards. As it play more hands it starts to build the intuition about which hands/strategy give him better results.
        Player going to store the first two cards as a dictionary with rankings and whether they are the same suit or not as Y/N (for example if player has king 
        daimond and 2 club the key for the dictionary will be K2N & 2KN, but if we had King club and 2 club then the key for dictionary will be 2KY & K2Y). Then we append 
        the value of "game net change" after each game into the list. 
        As player plays more hand it starts utilizing the "game net change" value for each pair for cards. for example if player recieves 2KY it looks at "game net change"
        value from previous plays and calculates the probability of playing by adding all the "game net change" values in the list for 2KY hand and then divide that by adding
        the absolute value of "game net change".

        """
       
        if len(self.balance_history)==0:
            self.number_of_finished_games=0
            
            if self.short_memory!=self.current_game: #only making beting decision when we recieve the first two cards
                self.simpleLearnerCall(hand)
                self.short_memory=self.current_game
            else:
                self.repeat_action()
        else :#if len(self.balance_history)>self.number_of_finished_games:
            
            if self.short_memory!=self.current_game:
                
                #updating the reward 
                self.update_SimpleLearnerReward()
                
                self.simpleLearnerCall(hand)
                self.short_memory=self.current_game
                number_of_game=len(self.balance_history)
                
                self.number_of_finished_games=len(self.balance_history)
                
            else:
                self.repeat_action()
            
        return None

class AwareLearnerPlayer(GenericPlayer):
    def __init__(self,name,balance):
        super().__init__(name,balance)
        self.previous_game={}
        self.initial_balance=balance
        self.number_of_game=1
        self.previous_list=[]
    
    def AwareLearnerCall(self,hand):
        """
        Made this function to make the decision for making call,fold and raise
        """
        hand_rank=[x for x,y in hand]
        hand_suit=[y for x,y in hand]
        
        if hand_suit[0]==hand_suit[1]:
            same_suit='Y'
        else:
            same_suit='N'
        self.dictionary_key=[hand_rank[0]+hand_rank[1]+same_suit,hand_rank[1]+hand_rank[0]+same_suit,'action']#saving the previous hand dictionary and action
        
        if self.hand_dictionary[self.dictionary_key[0]]['sum_absolute_bet']==0:
            
            #calling the first hand if player hanst played this hand and opponents dont have higher odds of winnings
                self.dictionary_key[2]='call'
                self.call_bet()
        else:
            
            action=self.hand_dictionary[self.dictionary_key[0]]['sum_bet'].argmax()
            
            if action==0:    
                
                self.dictionary_key[2]='fold'
                self.fold_bet()
            elif action==1:
                
                winning_probability=self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][action]/(abs(self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][action])+abs(self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][0])+abs(self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][2]))
                #if number of winning on call is high then raise, otherwise keep calling.
                if winning_probability>0.7:
                    self.dictionary_key[2]='raise'
                    self.raise_bet(round(0.2*self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][action],0))
                else:
                    self.dictionary_key[2]='call'
                    self.call_bet()
            else:
                #player only going to raise on the hands that he already won
                if self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][action]>0:
                    raise_amount=round(0.1*self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][action],0)#raising by 10% of cumulative wins
                    
                    self.dictionary_key[2]='raise'
                    self.raise_bet(raise_amount)
                #if player lost money on this hand its going to check between cumulative lost between call and fold and select the one
                #with lower loss
                elif self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][1]>self.hand_dictionary[self.dictionary_key[0]]['sum_bet'][0]:
                    self.dictionary_key[2]='call'
                    self.call_bet()
                else:
                    self.dictionary_key[2]='fold'
                    self.fold_bet()
        return None
               
    def temp_balance_dictionary(self,active_players,temp_dictionary):
        #print('active players in temb balance dictionary',self.active_game.players)
        for player in self.active_game.players:
            #print('player is',player['player'])
            #print('active is',player['active'])

            
            if player['active']==1:
                active_players+=1
                
                if player['player'].name!=self.name:
                    temp_dictionary.update({player['player'].name:player['player'].balance_history[-1][-1]})
        return temp_dictionary,active_players
        
    def opponent_winning_probability(self,active_players,temp_dictionary):
        
        player_action_list=self.active_game.player_actions.copy()
        #removing all the items with card information from the list.
        for action_list in player_action_list:
            if len(action_list)!=4:
                player_action_list.remove(action_list)
        for _,player,action,_ in player_action_list[-2*active_players:-active_players]:#self.active_game.player_actions[-2*active_players:-active_players]:
            
            if player!=self.name:#dont want to check our own action
                
                if player in temp_dictionary:
                    self.previous_game[player][action]['cum_sum']+=temp_dictionary[player]
                    self.previous_game[player][action]['abs_sum']+=abs(temp_dictionary[player])
                    self.previous_game[player][action]['probability']=self.previous_game[player][action]['cum_sum']/self.previous_game[player][action]['abs_sum']                                     
                else:
                    print('*******************check why player active_game.players is not in active_game.player_actions???????? ')
        return None
    
    def max_opponent_probability(self,action_list):
        """
        This function looks at all the players action and their historical results, then return the current action
        and highest probability of winning against other player
        """
        max_probability=0
        #print('action_list is',action_list, 'previous list is',self.previous_list)
        #print('------curent actions are ',list(set(action_list)-set(self.previous_list)))
        for action_tuple in list(set(action_list)-set(self.previous_list)):
            if len(action_tuple)==4:#filtering out the cards
                
                #print('action tuple is ',action_tuple)
                _,player,action,_ = action_tuple
                if (player!=self.name)&(action!='fold'):
                    if self.previous_game[player][action]['probability']>max_probability:
                        max_probability=self.previous_game[player][action]['probability']
        self.previous_list=action_list.copy() #updating previous list for next betting round
        return max_probability
        
        
    
    def action_based_on_opponent(self,probability,hand,thereshold=0.7):
        if probability>thereshold:
            #print('our player is folding because other player has higher chance')
            #print('previous hand is (not updating self.dictionary_key)',hand)
            self.fold_bet()
        else:
            self.AwareLearnerCall(hand)
        return None
        
    #using the same functions as simple learner to update rewards for each hand, probably there is a better way
    # than copy and pasting the same funciton, however going to do this for the time being.
    def update_SimpleLearnerReward(self):
        if self.dictionary_key[2]=='fold':
                    for i in range(2):#setting dictionary for both combination
                        self.hand_dictionary[self.dictionary_key[i]]['sum_absolute_bet']+=abs(self.balance_history[len(self.balance_history)-1][8])#updating hand dictionary
                        self.hand_dictionary[self.dictionary_key[i]]['sum_bet']+=np.array([self.balance_history[len(self.balance_history)-1][8],0,0])
        elif self.dictionary_key[2]=='call':
                    for i in range(2):#setting dictionary for both combination
                        self.hand_dictionary[self.dictionary_key[i]]['sum_absolute_bet']+=abs(self.balance_history[len(self.balance_history)-1][8])#updating hand dictionary
                        self.hand_dictionary[self.dictionary_key[i]]['sum_bet']+=np.array([0,self.balance_history[len(self.balance_history)-1][8],0])
        elif self.dictionary_key[2]=='raise':
                    for i in range(2):#setting dictionary for both combination
                        self.hand_dictionary[self.dictionary_key[i]]['sum_absolute_bet']+=abs(self.balance_history[len(self.balance_history)-1][8])#updating hand dictionary
                        self.hand_dictionary[self.dictionary_key[i]]['sum_bet']+=np.array([0,0,self.balance_history[len(self.balance_history)-1][8]])
        else:
            raise Exception('Action must select between fold, call or raise actions')
        return None    
    
    
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
        This player uses different strategy from SimpleLearner Player to learn by playing hand. Unlike SimpleLearner that 
        randomly selects between fold, call and raise when there is no previous information, this player starts playing everyhand to
        learn whether it is a good hand or not. We expect this player to perform better by not losing the money by randomly folding or raising
        then it looks at the gain for call, if its negative its going to fold next time.
        Player learn about betting strategy by observing other players actions (bet, fold, raise) and the reward of their actions, then he decide his action based on the other result
        learn whether it is a good hand or not. We expect this player to perform better by not losing the money 
        """
        if self.number_of_game==1:
            self.call_bet()#playing the first game as we dont have hany knowledge about previous games
        else:
            
            action_list=[action_tuple for action_tuple in self.active_game.get_player_actions() if len(action_tuple)==4]#removing card info from the list
            max_probability=self.max_opponent_probability(action_list)
            self.action_based_on_opponent(max_probability,hand)
        
        
       
  



    def post_game_hook(self):

        if self.number_of_game==1:
            #creating a dictionary to record winnig hand of other players for their action.
            self.previous_game={player['player'].name:{'bet':{'cum_sum':0,'abs_sum':0,'probability':0},'call':{'cum_sum':0,'abs_sum':0,'probability':0}}  for player in self.active_game.players if player['player'].name!=self.name}
        else:
            self.update_SimpleLearnerReward()
            
        self.number_of_game+=1
        active_players=0
        temp_dictionary={}
        temp_dictionary,active_players=self.temp_balance_dictionary(active_players,temp_dictionary)
                         
                
        
        
        self.opponent_winning_probability(active_players,temp_dictionary)
                                                                      
        
        self.previous_list=[]
        

##########################################################################################
#                          Monte Carlo Tree Search - Player
##########################################################################################

def order_by_rank(cards):
    """ 
    order a set of Card objects by rank....
    """
    return tuple(sorted(list(cards),key=lambda card: (RankMap[card.rank], card.suit)))

def UCB(wins,games,parent_total,constant):
    """
    This is the upper confidence bound equation:

    win/total game + constant * sqrt(log(parent games) / child games)
    """
    if games == 0 or parent_total == 0:
        return 0
    return wins / games + constant * math.sqrt(math.log(parent_total)/games)

def monte_carlo_simulation(cards,river,opponents,runtimes=1):
    """
        A player can use this to simulate the odds of them winning a hand of poker.
        You give it your current hand (cards variable), the current river, which is
        either: None (pre-flob), 3,4,5 for post-flop.  The odds change with the 
        number of opponents, so you need to add it to.  You do this for
        runtime number of times and report the wins and totals.  YOu can 
        think of it as a monte-carlo simulation.
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

    return (wins, runtimes) # wins and number of games

class MCST_Set(object):
    """ 
    MCST - monte carlo tree search algorithm and it's associated tree.  get_root gets the actual tree.
    """

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
    def __init__(self,turn_order,card_branching=5,monte_carlo_sims=5):
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
        self.updates = 0
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

            self.updates += 1

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
        if compute_time < .1:
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
                self.updates += 1
            else:
                abridged_key = []
                for key in node.card_totals.keys():
                    abridged_key.append(key[0:len(hand)])
                if hand not in abridged_key:
                    self.update_node(node,hand)
                    self.simulate_node(node)
                    self.back_propogate_node(node)
                    self.updates += 1

            if node.player_type != player:
                raise Exception("wrong player type...please check for bugs")

        return node 

    def __repr__(self): 
        return 'MCTS with {} players'.format(str(self.turn_order))

class MonteCarloTreeSearchPlayer(GenericPlayer):

    def __init__(self,name,balance):
        super().__init__(name,balance)

        self.decision_tree = MCST_Set()
        self.moving_average = []
        self.last_odds = [0,0,0]

    def get_opponents_map(self):

        opponent_map = {}

        o = 0
        for player in self.get_beginning_players():
            if player == self.name:
                opponent_map[player] = 'current'
            else:
                o += 1
                opponent_map[player] = 'opponent ' + str(o)

        return opponent_map

    def get_turn_order(self):
        opponent_map = self.get_opponents_map()
        turn_order_map = [opponent_map[player] for player in self.get_beginning_players()]
        return tuple(turn_order_map)

    def get_converted_player_actions(self):
        converted_list = []
        opponent_map = self.get_opponents_map()
        for action in self.get_all_player_actions():
            if action[0] == 'card':
                action_cards = sorted(action[1][0:3],key=lambda card: (RankMap[card.rank],card.suit)) + action[1][3:]
                action = ('card',tuple(action_cards))
                converted_list.append(action)
            else:
                player_type, player_name, bet_type, bet_amount = action 
                converted_list.append((player_type,opponent_map[player_name],bet_type,bet_amount))
        return converted_list

    def past_player_actions(self):
        past_actions = []
        opponent_map = self.get_opponents_map()
        for action in self.get_all_player_actions():
            if action[0] == 'player':
                _, player_name, bet_type, bet_amount = action 
                past_actions.append((opponent_map[player_name],bet_type,bet_amount))

        return past_actions

    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):

        if call_bid / self.balance > .02:
            self.fold_bet()
            return None

        beginning_players = self.get_turn_order()
        if not self.decision_tree.has_game(beginning_players):
            self.decision_tree.add_game(beginning_players)
            new_tree = self.decision_tree.get_game(beginning_players)
        else:
            new_tree = self.decision_tree.get_game(beginning_players)

        if not new_tree.has_hand(hand):
            new_tree.build(cards=hand,compute_time=.25,max_nodes=math.inf)

        if river is None:
            river = []

        path_query = self.past_player_actions()
        decision_node = new_tree.query(hand=hand,query_set=path_query)

        last_card_phase = decision_node.card_phase

        if last_card_phase== 0:
            cards_to_slot = 2
        elif last_card_phase == 1:
            cards_to_slot = 5
        elif last_card_phase == 2:
            cards_to_slot = 6
        elif last_card_phase == 3:
            cards_to_slot = 7
        else:
            raise Exception("phases need to be between 0 and 3")

        card_query = tuple(list(order_by_rank(hand)) + list(order_by_rank(river[0:3])) + list(river[3:]))
        card_query = card_query[0:cards_to_slot]

        if card_query not in decision_node.card_totals:
            new_tree.build(node=decision_node,cards=card_query,compute_time=.1,max_nodes=100)

        if decision_node.card_totals[card_query] < 100:
            new_tree.build(node=decision_node,cards=card_query,compute_time=.1,max_nodes=100)

        child_totals = decision_node.get_child_game_totals(card_query)
        child_wins = decision_node.get_child_win_totals(card_query)

        decision_info = []
        for action in child_totals:
            totals = child_totals[action]
            wins = child_wins[action]
            if totals == 0:
                totals = 1
            decision_info.append((action,wins/totals))

        decision_info.sort(key=lambda ky: -ky[1])
        
        if len(decision_info) > 0:
            decision_to_make = decision_info[0][0]
            win_odds = decision_info[0][1]
        else:
            decision_to_make = 'fold'
            win_odds = 0

        equal_chance_probability = 1 / float(opponents + 1)
        pre_flop_moving_average = equal_chance_probability
        wager_probability = equal_chance_probability
        if decision_node.card_phase == 0:
            if len(self.moving_average) > 20:
                self.moving_average.pop(0)
            
            if win_odds > 0:
                self.moving_average.append(win_odds)
            
            self.last_odds[0] = win_odds

            if sum(self.moving_average) ==  0:
                pre_flop_moving_average = equal_chance_probability
            else:
                pre_flop_moving_average = sum(self.moving_average) / len(self.moving_average)

            wager_probability = pre_flop_moving_average

        if decision_node.card_phase in (1,2):
            self.last_odds[decision_node.card_phase] = win_odds
            prob_diff = self.last_odds[decision_node.card_phase] - self.last_odds[decision_node.card_phase - 1]
            if prob_diff >= 0:
                greater_or_equal = True
            else:
                greater_or_equal = False

            if greater_or_equal == True or win_odds >= equal_chance_probability:
                wager_probability = win_odds - .01
        elif decision_node.card_phase == 3:
            wager_probability = equal_chance_probability

        made_wager = 0
        if decision_to_make == 'bet' or decision_to_make == 'call':
            if win_odds >= wager_probability:
                made_wager = 1
                if win_odds >= .9:
                    self.raise_bet(1000)
                elif decision_to_make == 'bet':
                    self.raise_bet(100)
                elif decision_to_make == 'call':
                    self.call_bet()
        
        if made_wager == 0:
            self.fold_bet()
        return None

##########################################################################################
#                          Monte Carlo Tree Search 
##########################################################################################

class simpleLearnerPlayer(GenericPlayer):
    def policy():
        return 0
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        """
        This player is a very simple learner, it looks at the first two card and make the decision on
        whether to call, raise or fold based on the first two call. Player has 3 simple policies, fold, call and raise by 20.
        we selected the same betting amount as we had for always call and always raise players in order to be able to compare the results.
        Player starts learning by playing games, at first he randomly selects between different policy (fold, call and raise) and sotre the
        final results "game net change" as its rewards. As it play more hands it starts to build the intuition about which hands/strategy give him better results.
        Player going to store the first two cards as a dictionary with rankings and whether they are the same suit or not as Y/N (for example if player has king 
        daimond and 2 club the key for the dictionary will be K2N & 2KN, but if we had King club and 2 club then the key for dictionary will be 2KY & K2Y). Then we append 
        the value of "game net change" after each game into the list. 
        As player plays more hand it starts utilizing the "game net change" value for each pair for cards. for example if player recieves 2KY it looks at "game net change"
        value from previous plays and calculates the probability of playing by adding all the "game net change" values in the list for 2KY hand and then divide that by adding
        the absolute value of "game net change".
        we use uniform random number generator between 0 and 1 
        1- if random value is less than calculated probability player raise
        2- if random value is greater caluculated probability but less than calculated probability +0.2 player call
        3- if random value is less than calculated probability +0.2 player fold.

        in order to avoid early elimination of some cards, if calculated probability became negative we change that to 0.1  which means player may raise the hand with 10 percent chance or call the hand with 0.1+0.2=0.3 30%
        probability

        use make bet function as part of class.
        on the player make attribute of player call history.
        make preflop wins as dictionary.
        learn about getter and setter ( encapsolation), later.
        make the function for making it suitless. get the card and make it suitless.

        """
        
        print('______________________________________________________________________')
        print('______________________________________________________________________')
        
        """if len(self.balance_history)==0:
            
            self.number_of_finished_games=0
        
        
        elif len(self.balance_history)>self.number_of_finished_games:
            number_of_game=len(self.balance_history)
            print('card1 is ',self.balance_history)
            #print('last_item is', self.balance_history[-1][-1])
            self.number_of_finished_games=len(self.balance_history)
            #print(self.number_of_finished_games)
        hand_rank=[x for x,y in hand]
        hand_suit=[y for x,y in hand]

        
        if hand_suit[0]==hand_suit[1]:
            same_suit='Y'
        else:
            same_suit='N'
        dictionary_key=[hand_rank[0]+hand_rank[1]+same_suit,hand_rank[1]+hand_rank[0]+same_suit]
        #using same probability to play for first hand
        #print('dictionary is ',self.hand_dictionary[dictionary_key[0]]['sum_absolute_bet'])
        print('river is ',river)
        if self.hand_dictionary[dictionary_key[0]]['sum_absolute_bet']==0:
            chance=random.random()
            if chance<0.33:
                self.fold_bet()
            elif chance>=0.33 and chance<0.66:
                self.call_bet()
            else:
                self.raise_bet(20)
        else:
            if self.hand_dictionary[0]['sum_bet']>0:
                self.raise_bet(round(100*self.hand_dictionary[0]['sum_bet']/self.hand_dictionary[0]['sum_absolute_bet'],0))
            else:
                if chance<0.2:
                    self.call_bet()
                else:
                    self.fold_bet()
        """
        
        print('current pot is',pot)
        print(random.random())
        #print([x(card.rank) for x in hand])
        #sys.exit(0)

def validate_config(config):
    """
        Checks the config for errors, quiet extensive.
    """
    print("validating the simulation settings...")

    required_keys = set(['tables','hands','balance','minimum_balance','simulations'])
    config_options = set(config.keys())

    if not required_keys.issubset(config_options):
        for option in config_options:
            if option not in required_keys:
                print("missing: {}".format(option))
        raise Exception("Config Error: Missing Keys in Simulation Config")

    bad_integer_error=0
    for numeric_option in ['tables','hands','balance','minimum_balance']:
        if not isinstance(config[numeric_option],int):
            bad_integer_error=1
            print("Config Error: {} should be an integer".format(numeric_option))
            continue

        if int(config[numeric_option]) < 1:
            bad_integer_error=1
            print("Config Error: {} should be an integer greater than 0".format(numeric_option))

    if bad_integer_error == 1:
        raise Exception("Config_Error: bad type found!")

    if config['hands'] < 2:
        raise Exception("Config Error: hands needs to be at minimum 2")

    if config['balance'] < config['minimum_balance']:
        raise Exception("Config Error: {} player beginning balance has to be greater than {}".format(config['balance'],config['minimum_balance']))
    
    if not isinstance(config['simulations'],list):
        raise Exception("Config Error: simulations should be a list of simulations")

    if len(config['simulations']) < 1:
        raise Exception("Config Error: you need at least 1 simulation under simulations key")

    for simulation in config['simulations']:
        if 'simulation_name' not in simulation:
            raise Exception("Config Error: simulation is missing simulation_name key")
        if 'player_types' not in simulation:
            raise Exception("Config Error: simulation is missing player_types array")
        if not isinstance(simulation['player_types'],list):
            raise Exception("Config Error: simulation player_types key needs to be a list")
        player_type_allowed_classes = [cls.__name__ for cls in GenericPlayer.__subclasses__()]
        if len(simulation['player_types']) < 2 or len(simulation['player_types']) > 6:
            raise Exception("Config Error: simulation has less than 2 or more than 6 players") 
        for player_type in simulation['player_types']:
            if player_type.__name__ not in player_type_allowed_classes:
                raise Exception("Config issue: {} not in {} allowed player_types".format(player_type.__name__, player_type_allowed_classes))

    print('finished the validation settings...')
    return None

def run_table_in_parallel(table_id, scenario_name,player_types,beginning_balance,minimum_play_balance,hands):
    print("running table_id {} for scenario: {} (parallel processing)".format(table_id, scenario_name))
    casino = Table( # generates a new table
                    table_id=table_id,
                    scenario_name=scenario_name, # use this to look up scenario in data analysis
                    player_types=player_types, # player types defined by subclassed version of GenericPlayer class
                    beginning_balance=beginning_balance, # beginning balances of player
                    minimum_play_balance=minimum_play_balance, # minimum balance to play
                    hands=hands # number of hands to be played in this table
                )
    casino.run_simulation() # start the actual simulation
    casino.run_analysis() # export the data for jupyter analysis at some later date
    return None

def run_all_simulations(config):
    """ 
        reads the configuration file config representing simulations to run
        and starts the simulations in serial fashion.
    """
    validate_config(config) # validate the configuration to prevent runtime errors
    tables = config['tables'] # get number of tables to run
    hands =config['hands'] # get number of hands to deal per table
    player_balance = config['balance'] # players beginning balance
    minimum_to_play = config['minimum_balance'] # minimum balance to join next game for a given player
    simulations = config['simulations'] # all the simulations that we will run, this represents a list

    # turns on pools of workers to run tables in parallel.  
    # pros/cons -> really fast 5x speed up, bad side -> really bad for debugging and seeing the simulation in action
    # pros/cons for turning off parallelism -> much slower: 1/5th the time, great for debugging and seeing the simulation in action with debug = 1 set.
    
    print("beginning all simulation...")
    sim_number = 0
    for simulation in simulations: # run simluation one at a time in serial fashion
        sim_number += 1
        print("")
        print("simulation running: {}".format(simulation['simulation_name']))
        start_time = time.time()
        if use_parallel == 1:
            pool = Pool()
            run_in_parallel=partial(
                        run_table_in_parallel,
                        scenario_name=simulation['simulation_name'],
                        player_types=simulation['player_types'],
                        beginning_balance=player_balance,
                        minimum_play_balance=minimum_to_play,
                        hands=hands
                    )
            table_ids = range((sim_number-1) * tables + 1,sim_number * tables + 1)
            pool.map(run_in_parallel,table_ids)
        else:
            print("running job in serial fashion")
            table_ids = range((sim_number-1) * tables + 1,sim_number * tables + 1)
            for table_id in table_ids:
                print("running table_id {} for scenario: {} (serial processing)".format(table_id, simulation['simulation_name']))
                casino = Table( # generates a new table
                                table_id=table_id,
                                scenario_name=simulation['simulation_name'], # use this to look up scenario in data analysis
                                player_types=simulation['player_types'], # player types defined by subclassed version of GenericPlayer class
                                beginning_balance=player_balance, # beginning balances of player
                                minimum_play_balance=minimum_to_play, # minimum balance to play
                                hands=hands # number of hands to be played in this table
                            )
                casino.run_simulation() # start the actual simulation
                casino.run_analysis() # export the data for jupyter analysis at some later date
        end_time = time.time()
        elapsed_time = round(end_time - start_time,2)
        print("simulation finished: {} - time_required: {} seconds".format(simulation['simulation_name'],elapsed_time))
        dprint("")
    print("")
    print('finished all simulation')
    return None

debug = 0 # to see detailed messages of simulation, put this to 1, think verbose mode
use_parallel = 1 # would not recommend using use_cache=1 on function simulate_win_odds due to not knowing if globals are thread or process safe.

# serial runs are guanteed unique repeatable results.  Parallel runs due to randomness of start times are not.  worth noting.

if __name__ == '__main__':
    print("starting poker simulation...(set debug=1 to see messages)")

    if debug == 1 and use_parallel == 1:
        raise Exception("Parallelism (use_parallel=1) is not supported with debug mode (debug=1)...set debug to 0")

    # defines all the simulations we will run
    simulations = {
       'tables': 5, # number of poker tables simulated
       'hands': 10, # number of hands the dealer will player, has to be greater than 2
       'balance': 100000, # beginning balance in dollars, recommend > 10,000 unless you want player to run out of money
       'minimum_balance': 50, # minimum balance to join a table
       'simulations': [ # each dict in the list is a simulation to run    
            {
                'simulation_name': 'monte vs 1 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    #AlwaysCallPlayer, # defines strategy of player 1
                    AlwaysCallPlayer,
                    MonteCarloTreeSearchPlayer

                ]
            },
            {
                'simulation_name': 'smart vs 1 all different types player', # name of simulation - reference for data analytics
                'player_types': [ # type of players, see the subclasses of GenericPlayer
                    AlwaysCallPlayer, # defines strategy of player 1
                    SmartPlayer,
                    AwareLearnerPlayer
                ]
            }           
        ]
    }

    random.seed(42) # gurantees standardized output for any given config

    run_all_simulations(simulations) # runs all the simulations in simulation variable