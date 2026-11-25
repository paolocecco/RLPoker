import random
from rlcard import models
from agents.equity_agent import EquityAgent
from utils.hand_evaluation import (
    evaluate_starting_hand,
    evaluate_hand_strength
)



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

loose_equity_agent = EquityAgent(
    simulations=100,
    raise_threshold=0.50,
    call_threshold=0.20
)

tight_equity_agent = EquityAgent(
    simulations=100,
    raise_threshold=0.80,
    call_threshold=0.50
)


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

