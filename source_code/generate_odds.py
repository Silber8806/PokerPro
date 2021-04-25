#!/usr/bin/env python3

# computationally expensive...figure I'd at least try out the angle to see about compute times.  Once you get to 4-river hands...it's
# 100s millions of hands that have to be considered...

import sys
from poker import simulate_win_odds, Card, FrenchDeck

if __name__ == '__main__':
    deck = FrenchDeck()
    
    all_cards = deck.all_cards[:]
    spades = [card for card in all_cards if card.suit == 'spades']
    clubs = [card for card in all_cards if card.suit == 'clubs']

    doubles = [list(tup) for tup in zip(spades,clubs)]
    off_rank = [[spade,club] for spade in spades for club in clubs if spade.rank != club.rank and spade.rank < club.rank]
    same_suit = [[spade,spade2] for spade in spades for spade2 in spades if spade.rank != spade2.rank and spade.rank < spade2.rank]

    possible_2_pairs = doubles + off_rank + same_suit

    print("If you run this past this point, it will take hours to days to complete... so early exiting...")
    sys.exit(0)

    i = 0
    print("creating all 2 pair cards")
    print("expected count: {}".format(len(7 * possible_2_pairs)))
    for opponent in range(2,7):
        for pair in possible_2_pairs:
            win_odds = simulate_win_odds(cards=pair,river=None,opponents=opponent,runtimes=100)
            i += 1
            if i % 1000 == 0:
                print("{} iterations".format(i))

    i = 0
    print("creating all 3-card flops")
    for pair in possible_2_pairs:
        possible_cards = [card for card in all_cards if card not in pair]
        three_pair_combos = [[card1,card2,card3] for card1 in possible_cards 
                                                       for card2 in possible_cards 
                                                       for card3 in possible_cards if card1 != card2 and card2 != card3 and card3 != card1 and 
                                                                                      card1 < card2 and card2 < card3 ]
        for three_pair in three_pair_combos:
            win_odds = simulate_win_odds(cards=pair,river=three_pair,opponents=1,runtimes=100)
            i += 1
            if i % 100000 == 0:
                print("{} iterations".format(i))

    i = 0
    print("creating all 4-card flops")
    for pair in possible_2_pairs:
        possible_cards = [card for card in all_cards if card not in pair]
        four_pairs_combos = [[card1,card2,card3,card4] for card1 in possible_cards 
                                                       for card2 in possible_cards 
                                                       for card3 in possible_cards
                                                       for card4 in possible_cards if card1 not in (card2,card3,card4) and
                                                                                      card2 not in (card3,card4) and 
                                                                                      card3 not in (card4) and 
                                                                                      card1 < card2 and 
                                                                                      card2 < card3 and 
                                                                                      card3 < card4]
        for four_pair in four_pairs_combos:
            win_odds = simulate_win_odds(cards=pair,river=four_pair,opponents=1,runtimes=100)
            i += 1
            if i % 100000 == 0:
                print("{} iterations".format(i))

print("finished...")