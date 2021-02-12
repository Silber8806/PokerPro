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

    def set_seed(self,seed):
        random.seed(seed)
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
        if len(river) < 5:
            new_river = deck.draw(draw_river)
        else:
            new_river = []
        current_river = river[:] + new_river
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
    hand_scores = []
    for hand in hands:
        score = score_hand(hand) 
        hand_scores.append(score)
    # if 1st hand did not win return 0 else 1
    return random.choice([0,1])

def score_hand(cards):
    #print("scoring: {}".format(cards))
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

    def make_bet(self,hand,river,opponents,call_bid,current_bid,pot):
        win_probabilty = simulate_win_odds(cards=hand,river=river,opponents=opponents,runtimes=5)
        expected_profit = round(win_probabilty * pot - (1 - win_probabilty) * current_bid,2)

        forced_raise = random.randint(0,10)

        if forced_raise < 2:
            return current_bid + call_bid + 20

        if opponents == 0:
            return current_bid + call_bid

        if expected_profit > 0:
            return current_bid + call_bid
        else:
            return None

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
        self.players[-1]['bet'] = self.big_blind
        self.players[-2]['bet'] = self.small_blind 
        self.current_bid = 10

    def get_current_pot(self):
        current_pot = 0
        for player in self.players:
            current_pot += player['bet']
        return current_pot

    def get_required_bid(self):
        required_bid = 0
        for player in self.players:
            required_bid = max(required_bid,player['bet'])
        return required_bid

    def get_num_active_opponents(self):
        return len(self.get_active_players()) - 1

    def get_active_players(self):
        return [player for player in self.players if player['active']]

    def all_players_checked(self):
        unique_bets = len(list(set([player['bet'] for player in self.players])))
        if unique_bets == 1:
            return True 
        else:
            return False

    def pre_flop(self):
        for player, hand in zip(self.players,chunk(self.cards[5:],2)):
            player['hand'] = hand

        print("pre-flob bidding")
        # max bid on limit poker is 3 rounds
        current_river = None

        for _ in range(0,3):
            for player in self.get_active_players():
                agent = player['player']
                if player['active']:
                    current_opponents = self.get_num_active_opponents()
                    current_hand = player['hand']
                    required_bid = self.get_required_bid()
                    current_bid = player['bet']
                    call_bid = required_bid - current_bid
                    bid = agent.make_bet(current_hand, current_river, current_opponents,call_bid, current_bid, self.get_current_pot())
                    print("current {} for {}".format(bid,player['player']))
                    if bid is None:
                        player['active'] = 0 
                    else:
                        player['bet'] = bid

            opponents_left = self.get_num_active_opponents()
            if (opponents_left == 0):
                break

            all_checked = self.all_players_checked()
            if (all_checked):
                break

        return None

    def post_flop(self):

        self.players = self.players[-2:] + self.players[:-2]  # handle post-flop starts at small blind by poker rules

        print("post flob bidding")
        for turn in range(3,6):
            current_river = self.river[:turn]
            for _ in range(0,3):
                for player in self.get_active_players():
                    agent = player['player']
                    if player['active']:
                        current_opponents = self.get_num_active_opponents()
                        current_hand = player['hand']
                        required_bid = self.get_required_bid()
                        current_bid = player['bet']
                        call_bid = required_bid - current_bid
                        bid = agent.make_bet(current_hand,current_river,current_opponents,call_bid, current_bid, self.get_current_pot())
                        print("current {} for {}".format(bid,player['player']))
                        if bid is None:
                            player['active'] = 0 
                        else:
                            player['bet'] = bid

                opponents_left = self.get_num_active_opponents()
                if (opponents_left == 0):
                    break

                all_checked = self.all_players_checked()
                if (all_checked):
                    break
            opponents_left = self.get_num_active_opponents()
            if (opponents_left == 0):
                break
        return None

    def check_last_surviving_player(self):
        opponents_left = self.get_num_active_opponents()
        winning_player = None
        if (opponents_left) == 0:
            for player in self.players:
                if player['active']:
                    winning_player = player 
                    break 
            print('winner is {}'.format(winning_player['player']))
        return 0

    def score_game(self):
        active_players = self.get_active_players()

        for player in self.get_active_players():
            print("checking win condition for {}".format(player))
            score_hand(player['hand'] + self.river)

        return None

    def run_game(self):
        print("")
        print("start game")
        self.pre_flop()
        self.check_last_surviving_player()
        self.post_flop() # re-working post_flop
        self.check_last_surviving_player()
        self.score_game() # re-working score game
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
    casino = Table(players=6,beginning_balance=100,hands=1000)
    casino.run_simulation()