import random
import csv

from poker import FrenchDeck, score_hand

PokerHierachy ={'high_card':1,'one_pair':2,'two_pair':3,'three_of_kind':4,'straight':5,'flush':6,'full_house':7,'four_of_kind':8,'straight_flush':9}
PokerInverseHierachy={poker_number:name for name,poker_number in PokerHierachy.items()}

random.seed(42)

number_of_hands = 1000000
final_hands = {}

if __name__ == '__main__':

    test_deck = FrenchDeck()

    i = 0
    for card in test_deck.permute(7,number_of_hands):
        result = PokerInverseHierachy[score_hand(card)[0]]
        if result in final_hands:
            final_hands[result] += 1
        else:
            final_hands[result] = 0

        i += 1

        if i % 1000 == 0:
            print("processed {} hands".format(i))

    report = sorted(final_hands.items(),key = lambda x: x[1])
    fieldnames = ['final_hand','number','all_hands','percent']

    with open('final_odds.csv','w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames) 
        print(fieldnames)
        for ky, val in report:
            data_row = [ky,val,number_of_hands,100 * round(val/float(number_of_hands),8)]
            print(data_row)
            writer.writerow(data_row)
        
