from poker import FrenchDeck, Card, chunk
from shahin import number_of_kind

def create_card(notation):
    rank, suit = str(notation[0]).upper(),str(notation[1]).lower()
    suit_mapping = {
        's': 'spades',
        'h': 'hearts',
        'c': 'clubs',
        'd': 'diamonds'
    }
    return Card(rank=rank,suit=suit_mapping[suit])

def create_card_sequence(notation):
    card_list = []
    for seq in list(chunk(notation,2)):
        new_card = create_card(seq)
        card_list.append(new_card)
    return card_list

def test_double():
    double_card_hand = create_card_sequence('asah9s8s7s3s2s')
    result = number_of_kind(double_card_hand)
    assert result['number_of_kind'] == 2
    assert result['number_of_pair'] == 1
    assert result['number_of_kind_on'] == 'A'

def test_large_numbers_odds():
    deck = FrenchDeck()
    number_of_As = 0

    number_of_sims = 100
    number_of_hands = 100
    rate_of_As = 1 / 12.
    expected_As = round(7 * number_of_hands * number_of_hands * rate_of_As,0)
    low_As = round(expected_As * .8,0)
    high_As = round(expected_As * 1.2,0)

    for _ in range(number_of_sims):
        for hand in deck.permute(7,number_of_hands):
            for card in hand:
                if card.rank == 'A':
                    number_of_As += 1

    assert number_of_As >= low_As
    assert number_of_As <= high_As


if __name__ == '__main__':
    print(test_double())