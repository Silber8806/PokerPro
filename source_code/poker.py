#!/usr/bin/env python3

import random
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def initialize_players(num_of_players, balance):
    players = []
    for player in range(num_of_players):
        name = "players" + str(player + 1)
        balance = balance 
        new_player = Player(name,balance)
        players.append(new_player)
    
    return players

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

    def save_deck(self):
        """ save the deck and go back to it """
        self.saved_deck = self.cards[:]
        self.saved_removed_deck = self.removed_cards[:]
        return None

    def load_deck(self):
        """ load the deck from the save point """ 
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
        if num_of_cards < 1 or num_of_cards > 52:
            raise Exception("Error: Draw has to be between 1 and 52")

        if hands < 1:
            raise Exception("Error: at least 1 hand needs to be drawn")

        for _ in range(hands):
            if num_of_cards >= len(self.cards):
                self.reshuffle()
            new_draw = self.cards[:num_of_cards]
            self.removed_cards.extend(new_draw)
            self.cards = self.cards[num_of_cards:]
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
            return next(self._draw(num_of_cards=num_of_cards,hands=hands))
        else:
            return self._draw(num_of_cards=num_of_cards,hands=hands)

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

    def set_seed(self,seed):
        random.seed(seed)
        return None

    def remove_card(self,rank,suit):
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
    deck = FrenchDeck()

    if river is None:
        river = []

    for card in cards + river:
        deck.remove_card(rank=card.rank,suit=card.suit)

    deck.save_deck()

    start_hand = cards 
    draw_player = len(cards)
    draw_river = 5 - len(river)

    wins = 0
    for _ in range(runtimes):
        hands_to_compare = []
        current_river = river[:] + deck.draw(draw_river)
        player_hand = start_hand[:] + current_river[:]
        hands_to_compare.append(player_hand)
        for _ in range(opponents):
            opponent_hand = deck.draw(draw_player) + current_river[:]
            hands_to_compare.append(opponent_hand)
        is_win = winning_hand(hands_to_compare)

        if is_win:
            wins += 1

        deck.load_deck()

    return wins/float(runtimes)

def winning_hand(*hands):
    for hand in hands:
        pass 
    return random.choice([0,1])

def score_hand(cards):
    print("scoring: {}".format(cards))
    return 0

class Player():
    """
        This class will keep information about a player between games
        and also have a method that makes decisions about a game situation.
    """
    def __init__(self,name,balance):
        self.name = name
        self.balance = balance 
        self.bet = 0
        self.wins = 0
        self.loses = 0
        self.decisions = ['fold','check','call','bet']
        self.strategy = None

    def pre_flob_bet(self,hand,opponents,call_bid,current_bid,pot):
        win_probabilty = simulate_win_odds(cards=hand,river=None,opponents=opponents,runtimes=100)
        if win_probabilty < .45:
            return None
        else:
            return current_bid + call_bid

    def take_turn(self, river, hand, opponents):
        if opponents == 0:
            return 0, 'check'

        bet = 0

        decision = random.choice(self.decisions)

        if (decision == 'bet'):
            bet = self.make_bet(50)
        
        return bet, decision

    def make_bet(self,bet):
        self.balance = self.balance - bet 
        return bet

    def __repr__(self):
        return "{}".format(self.name)

    def __str__(self):
        return "{}".format(self.name)

class Game():
    """
        Game implements all the logic about a game including who is playing, who has not yet folded,
        how big the pot is and also implements each players turn as well as scoring the end game.
    """
    def __init__(self,cards,players):
        self.cards = cards
        self.players = [{"player": player, "active": 1, "hand": None, "bet": 0, 'small_blind': 1} for player in players]
        self.river = cards[:5]
        self.pot = 0
        self.winner = None
        self.big_blind = 10
        self.small_blind = 5
        self.pot = 15
        self.players[-1]['bet'] = self.big_blind
        self.players[-2]['bet'] = self.small_blind 
        self.current_bid = 10

    def get_num_active_opponents(self):
        return len(self.get_active_players()) - 1

    def get_active_players(self):
        return [player for player in self.players if player['active']]

    def score_game(self):
        active_players = self.get_active_players()

        if len(active_players) == 1:
            self.winner = active_players
            print("player {} won!".format(self.winner[0]['player']))
        else: 
            for player in self.players:
                current_player = self.players[player]
                print("checking win condition for {}".format(player))
                score_hand(current_player['hand'] + self.river)
        return None

    def pre_flop(self):
        for player, hand in zip(self.players,chunk(self.cards[5:],2)):
            player['hand'] = hand

        # max bid on limit poker is 3 rounds
        for _ in range(0,3):
            for player in self.players:
                agent = player['player']
                if player['active']:
                    current_opponents = self.get_num_active_opponents()
                    current_hand = player['hand']
                    required_bid = self.current_bid
                    current_bid = player['bet']
                    bid = agent.pre_flob_bet(current_hand,current_opponents,required_bid, current_bid, self.pot)
                    if bid is None:
                        player['active'] = False 
                    else:
                        current_bid = bid 
                    print("current {} for {}".format(bid,player['player']))
            
        return None

    def post_flop(self):
        return None

    def run_game(self):
        print("")
        print("start game")
        self.pre_flop()
        #self.post_flop() # re-working post_flop
        #self.score_game() # re-working score game
        print("end game")
        print("")
        return None

    def __str__(self):
        return "Game with {} players".format(self.players)

class Table():
    """ 
        This class sets up a table, starts the simulation by instantiating a FrenchDeck
        and than streams a set of cards, which it uses per game.  This needs to be 
        flehsed out a bit.
    """
    def __init__(self,players,beginning_balance,hands):
        self.players = players 
        self.balance = beginning_balance
        self.hands = hands

    def run_simulation(self):
        print('started poker game')
        deck = FrenchDeck()

        players = initialize_players(num_of_players=self.players, balance = self.balance)

        for _, hand in enumerate(deck.permute(self.players * 2 + 5,2)):
            game = Game(hand,players)
            game.run_game()
        return 0

if __name__ == '__main__':
    casino = Table(players=2,beginning_balance=100,hands=1000)
    casino.run_simulation()