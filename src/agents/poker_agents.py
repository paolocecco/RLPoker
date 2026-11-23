import random
from rlcard import models
from rlcard.games.limitholdem.utils import Hand

rule_agent = models.load("limit-holdem-rule-v1").agents[0]

_rank_values = {
        "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 6, "7": 7, "8": 8, "9": 9,
        "T": 10, "J": 11, "Q": 12,
        "K": 13, "A": 14
    }

def evaluate_starting_hand(hole_cards):
    '''Evaluate the strength of the starting hand'''
    ranks = [_rank_values[card[1]] for card in hole_cards]
    high, low = max(ranks), min(ranks)

    pair = high == low
    suited = hole_cards[0][0] == hole_cards[1][0]

    # Premium starting hands
    strong = (
        (pair and high >= 10)
        or (high == 14 and low >= 11)
    )

    # Wider range of playable hands
    playable = (
        pair
        or (suited and high >= 11)
        or (high >= 13 and low >= 10)
    )

    return strong, playable

def evaluate_hand_strength(hole_cards, community_cards):
    '''General function to evaluate hand strength using rlcard's Hand class'''
    
    # Pad 5 or 6 cards to 7 with non-interfering dummy cards
    all_cards = hole_cards + community_cards

    # River (7 cards): evaluate directly with zero dummies
    if len(all_cards) >= 7:
        hand = Hand(all_cards[:7])
        hand.evaluateHand()
        print(hand.category)
        return hand.category

    # Flop (5 cards) or Turn (6 cards): pad up to 7
    needed = 7 - len(all_cards)
    used_ranks = {c[1] for c in all_cards}
    suit_counts = {s: sum(1 for c in all_cards if c[0] == s) for s in 'SHDC'}
    safe_suits = sorted(suit_counts, key=lambda suit: suit_counts[suit])

    dummies = []
    for r in ['2', '4', '6', '8', 'T', 'Q', 'A']:
        if r not in used_ranks:
            dummies.append(safe_suits[len(dummies) % 2] + r)
            if len(dummies) == needed:
                break

    hand = Hand(all_cards + dummies)
    print(f"number of cards in hand: {len(all_cards + dummies)}")
    print(f"dummies added: {dummies}")
    hand.evaluateHand()

    return hand.category  # Returns an integer representing the hand strength


def random_agent(state):
    legal_actions = state["raw_legal_actions"]
    return random.choice(legal_actions)

def improved_random_agent(state):
    legal_actions = state["raw_legal_actions"].copy()

    if "check" in legal_actions and "fold" in legal_actions:
        legal_actions.remove("fold")

    return random.choice(legal_actions)

def rule_based_agent(state):
    '''RLCard's rule-based agent'''
    return rule_agent.step(state)

def improved_rule_based_agent(state):
    action = rule_based_agent(state)

    if action == "fold" and "check" in state["raw_legal_actions"]:
        action = "check"

    return action



def calling_station_agent(state):
    """Always check or call when possible."""
    legal_actions = state["raw_legal_actions"]

    if "check" in legal_actions:
        return "check"
    if "call" in legal_actions:
        return "call"

    return random.choice(legal_actions)



def loose_aggressive_agent(state, raise_prob=0.75, fold_prob=0.25, bluff_prob=0.25):
    """Raise frequently, regardless of hand strength."""
    legal_actions = state["raw_legal_actions"]
    hole_cards = state["raw_obs"]["hand"]
    community_cards = state["raw_obs"]["public_cards"]
    all_cards = hole_cards + community_cards

    if len(all_cards) < 5: # Preflop
        strong, playable = evaluate_starting_hand(hole_cards)

        if strong or playable:
            if "raise" in legal_actions and random.random() < raise_prob:
                return "raise"
            if "call" in legal_actions:
                return "call"
            if "check" in legal_actions:
                return "check"
            

        if "raise" in legal_actions and random.random() < bluff_prob:
            return "raise"
        if "check" in legal_actions:
            return "check"
        if "fold" in legal_actions and random.random() < fold_prob:
            return "fold"

        return random.choice(legal_actions)

    elif len(all_cards) >= 5: # Postflop
        hand_strength = evaluate_hand_strength(hole_cards, community_cards)

        if hand_strength >= 2:  # One pair or better
            if "raise" in legal_actions and random.random() < raise_prob:
                return "raise"
            if "call" in legal_actions:
                return "call"
            if "check" in legal_actions:
                return "check"

        if hand_strength == 1:  # High card
            if "raise" in legal_actions and random.random() < bluff_prob:
                return "raise"
            if "check" in legal_actions:
                return "check"
            if "fold" in legal_actions and random.random() < fold_prob:
                return "fold"

        return random.choice(legal_actions)


def tight_aggressive_agent(state, raise_prob=0.5, fold_prob=0.5):
    """
    Uses hole cards then all cards to decide whether to play aggressively.
    """
    legal_actions = state["raw_legal_actions"]
    hole_cards = state["raw_obs"]["hand"]
    community_cards = state["raw_obs"]["public_cards"]
    all_cards = hole_cards + community_cards

    if len(all_cards) < 5:  # Preflop
        strong, playable = evaluate_starting_hand(hole_cards)

        if strong:
            if "raise" in legal_actions and random.random() < raise_prob:
                return "raise"
            if "call" in legal_actions:
                return "call"
            if "check" in legal_actions:
                return "check"

        if playable:
            if "check" in legal_actions:
                return "check"
            if "call" in legal_actions:
                return "call"

        if "check" in legal_actions:
            return "check"
        if "fold" in legal_actions and random.random() < fold_prob:
            return "fold"
        if "call" in legal_actions:
            return "call"

        return random.choice(legal_actions)

    elif len(all_cards) >= 5:  # Postflop
        hand_strength = evaluate_hand_strength(hole_cards, community_cards)

        if hand_strength >= 3:  # Two pair or better
            if "raise" in legal_actions and random.random() < raise_prob:
                return "raise"
            if "call" in legal_actions:
                return "call"
            if "check" in legal_actions:
                return "check"

        if hand_strength == 2:  # One pair
            if "call" in legal_actions:
                return "call"
            if "check" in legal_actions:
                return "check"

        if hand_strength == 1:  # High card
            if "check" in legal_actions:
                return "check"
            if "fold" in legal_actions and random.random() < fold_prob:
                return "fold"

        return random.choice(legal_actions)

