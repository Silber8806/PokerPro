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
        if num_of_cards < 1 or num_of_cards > 52:
            raise Exception("Error: Draw has to be between 1 and 52")

        if hands < 1:
            raise Exception("Error: at least 1 hand needs to be drawn")

        for _ in range(hands):
            new_draw = self.all_cards[:]
            random.shuffle(new_draw)
            yield new_draw[:num_of_cards]

    def permute(self,num_of_cards,hands=1):

        """
        permute(num_of_cards)

        returns <num_of_cards> permutation.  Doesn't reshuffle
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

    def __str__(self):
        return "French Deck ({} of {} cards remaining)".format(len(self.cards),len(self.all_cards))

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

class PLayerStrategy():
    """
        This class will hold player strategies that are used by make_turn.  You can
        switch strategies or use the same one.  They represent thought processes regarding
        a set of cards and number of opponents.
    """
    def __init__(self):
        return None

    def strategy1(self):
        print('implement strategy here...')
        return None

class Game():
    """
        Game implements all the logic about a game including who is playing, who has not yet folded,
        how big the pot is and also implements each players turn as well as scoring the end game.
    """
    def __init__(self,cards,players):
        self.cards = cards
        self.players = {player.name: {"player": player, "active": 1, "hand": None} for player in players}
        self.river = cards[:5]
        self.pot = 0
        self.winner = None
        for player, hand in zip(self.players,chunk(cards[5:],2)):
            self.players[player]['hand'] = hand

    def get_active_players(self):
        return [self.players[player] for player in self.players if self.players[player]['active']]

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

    def reward_player(self,pot):
        return None

    def run_game(self):
        print("")
        print("start game")
        for turn in range(3,6):
            current_river = self.river[:turn]
            print(turn - 2, current_river)
            for player in self.players:
                current_player = self.players[player]
                if current_player['active']:
                    number_of_opponents = len(self.get_active_players()) - 1
                    bet, decision = current_player['player'].take_turn(current_river, current_player["hand"],number_of_opponents)
                    print("{} decides to {} with bet {}".format(player, decision, bet))
                    self.pot = self.pot + bet
                    if decision == "fold":
                        current_player['active'] = 0    
        self.score_game()
        print("end game")
        print("")
        return None

    def __str__(self):
        return "Game with {} players".format(self.players)

def score_hand(cards):
    print("scoring: {}".format(cards))
    return 0

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

        for _, hand in enumerate(deck.permute(self.players * 2 + 5,1000)):
            game = Game(hand,players)
            game.run_game()
        return 0

if __name__ == '__main__':
    casino = Table(players=2,beginning_balance=100,hands=1000)
    casino.run_simulation()
