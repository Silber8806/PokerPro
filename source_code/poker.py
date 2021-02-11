#!/usr/bin/env python3

import random
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Table():
    def __init__(self,players):
        print('started poker game')
        self.players = players

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
    def __init__(self,name,balance):
        self.name = name
        self.balance = balance 
        self.bet = 0
        self.wins = 0
        self.loses = 0
        self.hand = None
        self.river = None
        self.active = True
        self.decisions = ['fold','check','bet']
        self.opponents = 0

    def draw_hand(self,hand):
        self.hand = hand

    def set_viewable_river(self,river):
        self.river = river

    def set_opponent_number(self,opponents):
        self.opponents = opponents

    def take_turn(self):
        if not self.active:
            return 0, 'fold'

        if self.opponents == 1:
            return 0, 'check'

        bet = 0

        hand = self.hand 
        river = self.river
        num_of_opponents = self.opponents

        decision = random.choice(self.decisions)

        if (decision == 'fold'):
            self.active = False
        elif (decision == 'bet'):
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
    def __init__(self,cards,players):
        self.cards = cards
        self.players = players
        self.river = cards[:5]
        self.pot = 0
        for player, hand in zip(self.players,chunk(cards[5:],2)):
            player.draw_hand(hand)

    def update_active_players(self):
        current_players = []
        for player in self.players:
            if not player.active:
                continue
            else:
                current_players.append(player)
        self.players = current_players
        return None

    def score_game(self):
        if self.get_active_players() == 1:
            print "player 1 won!"
            return None

        for player in self.players:
            if player.active:
                print("player final result")
        return None

    def reward_player(self,pot):
        return None

    def get_active_players(self):
        active_players = sum([1 for player in self.players if player.active])
        return active_players

    def run_game(self):
        for turn in range(3,6):
            current_river = self.river[:turn]
            for player in self.players:
                if player.active:
                    player.set_viewable_river(current_river)
                    player.set_opponent_number(self.get_active_players())
                    bet, decision = player.take_turn()
                    print("{} decides to {} with bet {}".format(player, decision, bet))
                    self.pot = self.pot + bet
            if self.get_active_players() == 1:
                break
                    
        self.score_game()
        return None

    def __str__(self):
        return "Game with {} players".format(self.players)

if __name__ == '__main__':
    deck = FrenchDeck()

    num_of_players = 2
    players = initialize_players(num_of_players=2, balance = 100)
    print(players)

    for game_number, hand in enumerate(deck.draw(num_of_players * 2 + 5,1000)):
        game = Game(hand,players)
        game.run_game()
        break

