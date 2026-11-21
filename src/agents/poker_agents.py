import random
from rlcard import models

rule_agent = models.load("limit-holdem-rule-v1").agents[0]

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
    legal = state["raw_legal_actions"]

    if "check" in legal:
        return "check"
    if "call" in legal:
        return "call"

    return random.choice(legal)

#def evaluate_hand_strength(hand):

def loose_aggressive_agent(state, raise_prob=0.75):
    """Raise frequently, regardless of hand strength."""
    legal = state["raw_legal_actions"]

    if "raise" in legal and random.random() < raise_prob:
        return "raise"

    if "check" in legal:
        return "check"
    if "call" in legal:
        return "call"

    return random.choice(legal)


def tight_aggressive_agent(state):
    """
    Uses hole cards to decide whether to play aggressively.
    """
    legal = state["raw_legal_actions"]
    hand = state["raw_obs"]["hand"]

    rank_values = {
        "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 6, "7": 7, "8": 8, "9": 9,
        "T": 10, "J": 11, "Q": 12,
        "K": 13, "A": 14
    }

    ranks = [rank_values[card[1]] for card in hand]
    high, low = max(ranks), min(ranks)

    pair = high == low
    suited = hand[0][0] == hand[1][0]

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

    if strong:
        if "raise" in legal:
            return "raise"
        if "call" in legal:
            return "call"
        return "check"

    if playable:
        if "check" in legal:
            return "check"
        if "call" in legal:
            return "call"

    if "check" in legal:
        return "check"
    if "fold" in legal:
        return "fold"

    return random.choice(legal)

