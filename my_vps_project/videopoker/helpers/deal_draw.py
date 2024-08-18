import random


def deal_cards():
    deck = ['2♠', '2♥', '2♦', '2♣', '3♠', '3♥', '3♦', '3♣', '4♠', '4♥', '4♦', '4♣', '5♠', '5♥', '5♦', '5♣', '6♠', '6♥', '6♦', '6♣',
            '7♠', '7♥', '7♦', '7♣', '8♠', '8♥', '8♦', '8♣', '9♠', '9♥', '9♦', '9♣', 'T♠', 'T♥', 'T♦', 'T♣', 'J♠', 'J♥', 'J♦', 'J♣', 'Q♠', 'Q♥',
            'Q♦', 'Q♣', 'K♠', 'K♥', 'K♦', 'K♣', 'A♠', 'A♥', 'A♦', 'A♣']
    
    random.shuffle(deck)
    return deck[:5], deck[5:10]

def evaluate_hand(hand):
    suits = []
    ranks = []
    flush = False
    straight = False
    three_of_kind = False
    pairs = 0 # Integer. Calculates number of pairs in hand
    
    
    # Splitting ranks from suits for evaluation
    for card in hand:
        ranks.append(card[0])
        suits.append(card[1])
    
    
    
    # Filling ranks dictionary with ranks as key and number of that rank as value
    rank_dict = {}
    for rank in ranks:
        if rank in rank_dict:
            rank_dict[rank] += 1
        else:
            rank_dict[rank] = 1
    
    pairs_ranks = []
    # Verifying combinations
    for k, v in rank_dict.items():
        if v == 2:
            pairs +=1
            pairs_ranks.append(k)
            continue
        if v == 3:
            three_of_kind = True
            continue
        if v == 4:
            return 'Four of a Kind'
    
    if pairs == 1 and not three_of_kind:
        if pairs_ranks[0] in 'JQKA':
            return 'Jacks or Better'
        else:
            return 'No value'

    if pairs == 2:
        return 'Two pairs'
    
    if three_of_kind and not pairs:
        return 'Three of a Kind'
    
    if all([three_of_kind, pairs]):
        return 'Full House'
    
    # Verifying all the suits are the same
    if len(set(suits)) == 1:
        flush = True
        
    # Verifying straight
    if len(set(ranks)) == 5:
        straight_list = []
        for rank in ranks:
            if rank in '23456789':
                straight_list.append(int(rank))
            else:
                tmp_rank = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}.get(rank)
                straight_list.append(tmp_rank)
        
        straight_list = sorted(straight_list)
        
        if straight_list[0] + 4 == straight_list[-1]:
            straight = True
            
        if 14 in straight_list and not straight:
            if straight_list[0] == 2 and straight_list[-2] == 5:
                straight = True
        
    
    # Verifying Straight
    if not flush and straight:
        return 'Straight'
    
    # Verifying Flush
    if flush and not straight:
        return 'Flush'
    
    # Verifying Royal Flush
    if all([flush, straight, 'K' in ranks, 'A' in ranks]):
        return 'Royal Flush'
    
    # Verifying Straight Flush
    if all([flush, straight]):
        return 'Straight Flush'
    
    return 'No value'