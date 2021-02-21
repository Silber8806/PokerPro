#!/usr/bin/env python3

import sys
import os
import csv
import random
import collections
import time

# named tuple is a tuple object (immutable type) that also has names.  
# immutable means once created they can't be modified.
# named tuple means you can access properties via . notation
# so if you have a card instance: card.suit and card.rank
# should return the suit and rank respectively.
Card = collections.namedtuple('Card', ['rank', 'suit'])
RankMap = {rank:i+1 for i, rank in enumerate([str(n) for n in range(2, 11)] + list('JQKA'))}

# the stupidest way of preserving an index, your welcome 
global unique_table_id
global unique_game_id

unique_table_id = 0
unique_game_id = 0

debug=0

def dprint(message):
    if debug == 1:
        print(message)
    return None

def card_to_char(card):
    if card:
        return card.rank + card.suit[0]
    else:
        return '00'

def card_to_string(card):
    if card:
        return card.rank + '-' + card.suit
    else:
        return 'Z-N/A'

def chunk(lst, n):
    """ 
        This just chunks a list into pieces, found on stackoverflow
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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

def simulate_win_odds(cards,river,opponents,runtimes=1000):
    """
        A player can use this to simulate the odds of them winning a hand of poker.
        You give it your current hand (cards variable), the current river, which is
        either: None (pre-flob), 3,4,5 for post-flop.  The odds change with the 
        number of opponents, so you need to add it to.  You do this for
        runtime number of times and report the percent of wins.  YOu can 
        think of it as a monte-carlo simulation
    """
    deck = FrenchDeck()

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

    return wins/float(runtimes) # your percent wins

def winning_hand(*hands):
    """ 
        used in the simulate_win_odds function.  This needs to be implemented still.
        Right now it just randomly picks win or lose.  Use the hand score function
        here and than check if 1st entry has highest rank.
    """
    hand_scores = []
    for hand in hands:
        score = score_hand(hand) 
        hand_scores.append(score)
    # if 1st hand did not win return 0 else 1
    return random.choice([0,1])

def score_hand(cards):
    """ 
        needs to be implemented.  You need to take the hand of 7 cards
        rank it so that it can be compared to other hands.
    """
    #dprint("scoring: {}".format(cards))
    return 0

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

    def register_for_game(self,game_id):
        self.games_played.append(game_id)
        self.current_game = game_id
        self.bid_number = 0
        self.registered_balance = self.balance
        self.folded_this_game = 0
        self.last_survivor_this_game = 0
        self.won_game = 0
        self.blind_type = 'None'
        return None 

    def set_blind(self,blind_type=None):
        self.blind_type = blind_type
        return None

    def update_balance_history(self):
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

        self.balance_history.append([self.current_game, end_game_result, player_status, self.blind_type, self.beginning_balance, self.registered_balance, self.balance, self.balance - self.registered_balance])
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

    def _set_up_bet(self,opponents,call_bid,current_bid,raise_allowed=False):
        self.opponents = opponents
        self.call = call_bid
        self.current_bet = current_bid
        self.raise_allowed = raise_allowed
        return None

    def _last_man_standing(self):
        if self.opponents == 0:
            dprint("{} - is last man standing".format(self.name))
            self.call_bet()
            self.last_survivor_this_game = 1
            return 1
        return 0

    def _raise_bet(self,raise_amount,allow_all_in=True):
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
        # currently not implemented...use this one to record bets...
        self.bid_number += 1
        river_set = [None for _ in range(5)]
        if river is not None:
            for i,card in enumerate(river):
                river_set[i] = card
        hand = sorted([card_to_string(card) for card in hand])
        river_set = sorted([card_to_string(card) for card in river_set])
        data_tuple = [self.current_game, self.name, self.__class__.__name__, self.bid_number,opponents,call_bid,current_bid,self.final_bet,pot,raise_allowed] + hand + river_set
        self.hand_history.append(data_tuple)
        return None

    def make_bet(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
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

class Game():
    """
        Game implements an actual poker game.  It has all the mechanics to do
        pre-flob, post-flob and scoring of games.  The 
    """
    def __init__(self,cards,players,minimum_balance_to_join):
        global unique_game_id
        unique_game_id = unique_game_id + 1
        self.id = str(unique_game_id)
        self.cards = cards
        self.river = cards[:5]
        self.winner = None
        self.big_blind = 10
        self.small_blind = 5
        # you need a minimum balance otherwise, players with $0 will join your game.
        self.minumum = minimum_balance_to_join
        self.players = [{"player": player, "active": 1, "hand": None, "bet": 0} for player in players if player.balance > self.minumum] # get rid of losers that don't have enough money

        for player in players:
            player.register_for_game(self.id) # get the unique memory id for the game

        # every poker game has a small and big blind to prevent people from always folding unless they have pocket aces.
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
                else:
                    player['bet'] = bid # if they returned a bid, use it here.

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
                    else:
                        player['bet'] = bid # if he makes a bet, it becomes his new bet

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
        number_of_players = len(self.get_active_players())  # number of players still in game
        reward = self.get_current_pot() // number_of_players # pot per player
        casino_free_money = self.get_current_pot() % number_of_players # casinos free money

        dprint("splitting the current pot: ${} by {} people".format(self.get_current_pot(),number_of_players))
        for player in self.get_active_players(): # reward the active players
            player['player'].get_pot(reward)
            dprint("{} got a reward of ${} for not folding".format(player['player'],reward))
        dprint("casino gets the remainder ${}".format(casino_free_money))
        # dumb currently, just split pot evenly until we get proper scoring hand function

        for player in self.get_active_players(): # this is the actual function, still needs to be implemented
            dprint("checking win condition for {}".format(player))
            score_hand(player['hand'] + self.river)

        for player in self.players:
            player['player'].update_balance_history()

        return None

    def run_game(self):
        """
            This runs each phase of the game
        """
        dprint("")
        dprint("start game")
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
    def __init__(self,player_types,beginning_balance,minimum_play_balance,hands):
        global unique_table_id
        unique_table_id += 1
        self.player_types = player_types 
        self.player_types_names = '|'.join(sorted([player_type.__name__ for player_type in self.player_types]))
        self.players = None
        self.balance = beginning_balance
        self.min_balance = minimum_play_balance
        self.hands = hands
        self.games_played = []
        self.id = str(int(unique_table_id))

    def add_games_played(self,game_id):
        self.games_played.append(game_id)
        return None

    def initialize_players(self):
        """ create new players with certain balance of dollars to play with"""
        if len(self.player_types) < 2:
            raise Exception("Error: too few players")

        if len(self.player_types) > 6:
            raise Exception("Error: no more than 6 players allowed")

        players = []
        for i, player_type in enumerate(self.player_types):
            balance = self.balance 
            name = "players_" + str(i + 1)
            new_player = player_type(name,balance)
            players.append(new_player)

        self.players = players
        
        return players

    def progress_player_turn_order(self):
        self.players = self.players[-1:] + self.players[:-1]
        return None

    def run_simulation(self):
        """
            This starts a simulation for a single table with fixed number of people
        """
        
        start_time = time.time()
        dprint('started poker game')
        deck = FrenchDeck()

        self.initialize_players() # create your players
        
        for _, hand in enumerate(deck.permute(len(self.player_types) * 2 + 5,self.hands)): # start streaming 5 cards + 2 per person.  Permute means it reshuffles each time.
            game = Game(hand,self.players,self.min_balance) # Start a new game instance with settings
            self.add_games_played(game.id)
            game.run_game() # start the actual simulation
            self.progress_player_turn_order()

        elapsed_time = time.time() - start_time
        dprint("ending poker game: {} games in {} seconds".format(self.hands,round(elapsed_time,2)))
        
        return 0

    def run_analysis(self):
        """
            run a quick analysis and statistics section for the players...
        """

        script_dir = os.path.dirname(__file__)
        data_dir = os.path.join(script_dir,'data')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        file_name = 'poker_balances_' + self.id + '.csv'
        file_loc = os.path.join(data_dir,file_name)

        fieldnames = ['table_id','game_id','player_name','player_type','game_result', 
                                    'game_reason', 'blind_type', 'beginning_balance',
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

        fieldnames = ["table_id","player_types"]

        with open(file_loc,'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames) 
            data_tuple=[str(self.id),self.player_types_names]
            writer.writerows([data_tuple])
        return 0

class AlwaysCallPlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        self.call_bet()
        return None

class AlwaysRaisePlayer(GenericPlayer):
    def bet_strategy(self,hand,river,opponents,call_bid,current_bid,pot,raise_allowed=False):
        self.raise_bet(20)
        return None

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
        win_probabilty = simulate_win_odds(cards=hand,river=river,opponents=opponents,runtimes=5)
        expected_profit = round(win_probabilty * pot - (1 - win_probabilty) * current_bid,2)

        forced_raise = random.randint(0,10)
        if forced_raise < 6:
            self.raise_bet(10)
            return None

        # if you statistically will make money, call the bid else just fold
        if expected_profit > 0:
            self.call_bet()
        else:
            self.fold_bet()
        return None

global player_types 
player_type_allowed_classes = [cls.__name__ for cls in GenericPlayer.__subclasses__()] # lists all possible Player Stragegies

def validate_player_types(player_types_list):
    for player_type in player_types_list:
        if player_type not in player_types:
            raise Exception("Bad Player Type, should be in: {}".format(player_type_allowed_classes))
    return 0

if __name__ == '__main__':
    print("starting poker simulation...(set debug=1 to see messages)")

    all_simulations = [
        [ # game 1
            AlwaysCallPlayer, # defines strategy of player 1
            AlwaysCallPlayer, # defines strategy of player 2
            AlwaysCallPlayer, # defines strategy of player 3
            AlwaysCallPlayer, # defines strategy of player 4
            AlwaysCallPlayer, # defines strategy of player 5
            SmartPlayer # defines strategy of player 6
        ],
        [ # game 2
            AlwaysRaisePlayer, # defines strategy of player 1
            AlwaysRaisePlayer, # defines strategy of player 2
            AlwaysRaisePlayer, # defines strategy of player 3
            AlwaysRaisePlayer, # defines strategy of player 4
            AlwaysRaisePlayer, # defines strategy of player 5
            SmartPlayer # defines strategy of player 6
        ]      
    ]

    for player_types in all_simulations:
        validate_player_types(player_types)

    for player_types in all_simulations:
        for _ in range(1):
            casino = Table(player_types=player_types,beginning_balance=100000,minimum_play_balance=50,hands=100) # Create a table with a deck and players.  Start dealing cards in a stream and play a game per hand.
            casino.run_simulation() # start the actual simulation
            casino.run_analysis() # only remove comment if you want to generate files for the game
            break
        break
    print("finished poker simulation...")