
from rlcard.games.limitholdem.utils import Hand

_rank_values = {
    "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9,
    "T": 10, "J": 11, "Q": 12,
    "K": 13, "A": 14
}


def evaluate_starting_hand(hole_cards):
    """Evaluate the strength of the starting hand."""

    ranks = [_rank_values[card[1]] for card in hole_cards]
    high, low = max(ranks), min(ranks)

    pair = high == low
    suited = hole_cards[0][0] == hole_cards[1][0]

    strong = (
        (pair and high >= 10)
        or (high == 14 and low >= 11)
    )

    playable = (
        pair
        or (suited and high >= 11)
        or (high >= 13 and low >= 10)
    )

    return strong, playable


def evaluate_hand_strength(hole_cards, community_cards):
    """Evaluate hand strength using RLCard's Hand class."""

    all_cards = hole_cards + community_cards

    if len(all_cards) >= 7:
        hand = Hand(all_cards[:7])
        hand.evaluateHand()
        return hand.category

    needed = 7 - len(all_cards)
    used_ranks = {c[1] for c in all_cards}
    suit_counts = {
        s: sum(1 for c in all_cards if c[0] == s)
        for s in "SHDC"
    }
    safe_suits = sorted(suit_counts, key=lambda suit: suit_counts[suit])

    dummies = []

    for r in ["2", "4", "6", "8", "T", "Q", "A"]:
        if r not in used_ranks:
            dummies.append(safe_suits[len(dummies) % 2] + r)
            if len(dummies) == needed:
                break

    hand = Hand(all_cards + dummies)
    hand.evaluateHand()

    return hand.category
