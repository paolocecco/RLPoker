
import random
from rlcard.games.limitholdem.utils import compare_hands


def calculate_equity(hole_cards, community_cards, simulations):
    """Estimate equity against a random opponent."""

    ranks = "23456789TJQKA"
    suits = "SHDC"

    deck = [s + r for s in suits for r in ranks]

    known_cards = hole_cards + community_cards
    remaining_deck = [
        card for card in deck if card not in known_cards
    ]

    wins = 0
    ties = 0

    missing_cards = 5 - len(community_cards)

    for _ in range(simulations):

        sampled = random.sample(
            remaining_deck,
            2 + missing_cards
        ) # the two represents the two hole cards we need to give the opponent

        opponent_cards = sampled[:2]
        future_cards = sampled[2:]

        final_community = community_cards + future_cards

        our_hand = hole_cards + final_community
        opponent_hand = opponent_cards + final_community

        result = compare_hands([our_hand, opponent_hand])

        if result == [1, 0]:
            wins += 1
        elif result == [1, 1]:
            ties += 1

    return (wins + 0.5 * ties) / simulations


class EquityAgent:

    def __init__(self, simulations,raise_threshold=0.60,call_threshold=0.35):
        self.simulations = simulations
        self.raise_threshold = raise_threshold
        self.call_threshold = call_threshold
        self.last_cards = None
        self.last_equity = None


    def reset(self):
        self.last_cards = None
        self.last_equity = None

    def __call__(self, state):

        legal_actions = state["raw_legal_actions"]
        raw = state["raw_obs"]

        hole_cards = raw["hand"]
        community_cards = raw["public_cards"]

        current_cards = (
            tuple(hole_cards),
            tuple(community_cards)
        )

        # Recalculate only if the cards have changed
        if current_cards != self.last_cards:

            self.last_equity = calculate_equity(
                hole_cards,
                community_cards,
                simulations=self.simulations
            )

            self.last_cards = current_cards

            print(f"New equity: {self.last_equity:.1%}")

        equity = self.last_equity

        if equity >= self.raise_threshold:
            if "raise" in legal_actions:
                return "raise"
            if "call" in legal_actions:
                return "call"

        if equity >= self.call_threshold:
            if "call" in legal_actions:
                return "call"

        if "check" in legal_actions:
            return "check"

        if "fold" in legal_actions:
            return "fold"

        return random.choice(legal_actions)
