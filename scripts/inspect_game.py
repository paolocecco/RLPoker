
import random
import numpy as np
from agents.poker_agents import (
    random_agent,
    improved_random_agent,
    rule_based_agent,
    improved_rule_based_agent,
    calling_station_agent,
    loose_aggressive_agent,
    tight_aggressive_agent,
    loose_equity_agent,
    tight_equity_agent
)

from environments.extended_rlcard_env import describe_obs
from environments.rlcard_env import create_environment
from agents.equity_agent import EquityAgent

ACTION_NAMES = {
    0: "Call",
    1: "Raise",
    2: "Fold",
    3: "Check",
}

# def display_state(state, player_id, decision):
#     raw = state["raw_obs"]
#     obs = state["obs"]
#     legal_actions = list(state["legal_actions"].keys())

#     print(f"\n{'=' * 50}")
#     print(f"DECISION {decision} - PLAYER {player_id}")
#     print(f"{'=' * 50}")

#     # Human-readable information
#     print("\n--- RAW STATE ---")
#     for key, value in raw.items():
#         print(f"{key}: {value}")

#     # Betting history, if recorded
#     print("\n--- ACTION HISTORY ---")
#     print(state.get("action_record", []))

#     # Numerical representation for the DQN
#     print("\n--- ENCODED OBSERVATION ---")
#     print("Shape:", obs.shape)
#     print("Vector:", obs)
#     print("Active feature indices:",
#           np.flatnonzero(obs).tolist())

#     # Possible actions
#     print("\n--- LEGAL ACTIONS ---")
#     for action_id in legal_actions:
#         print(f"{action_id}: {ACTION_NAMES[action_id]}")
        

#     return legal_actions

def format_card(card):
    suits = {
        "S": "♠",
        "H": "♥",
        "D": "♦",
        "C": "♣"
    }

    rank = card[1:]
    if rank == "T":
        rank = "10"

    return rank + suits[card[0]]


def format_hand(cards):
    return " ".join(
        f"[{format_card(card)}]" for card in cards
    )

def display_reduced_state(env, state, player_id, decision):
    raw = state["raw_obs"]
    legal_actions = list(state["legal_actions"].keys())
    print(" ")
    print("its player: " +  str(player_id + 1) + "s turn descision " + str(decision))
    print(" ")
    print("Hole cards:", format_hand(raw["hand"]))
    print("Community cards:", format_hand(raw["public_cards"]))
    print("Chips committed:", raw["all_chips"])
    print("Pot size:", sum(raw["all_chips"]))
    print("Raises per round:", raw["raise_nums"])
    print("Extended obs:", describe_obs(env, state["obs"]))

    print("\n--- LEGAL ACTIONS ---")
    for action_id in legal_actions:
        print(f"{action_id}: {ACTION_NAMES[action_id]}")

    return legal_actions


def main():


    player1 = loose_equity_agent
    player2 = tight_equity_agent
    env = create_environment()
    player1profit = 0 

    for episode in range(1000):
        if isinstance(player1, EquityAgent):
            player1.reset()

        if isinstance(player2, EquityAgent):
            player2.reset()

        state, player_id = env.reset()
        state = env.get_state(player_id)
        decision = 1

        while not env.is_over():

            legal_actions = display_reduced_state(
                env, state, player_id, decision
            )

            # Temporary random policy
            if ( player_id == 0 ):
                action = player1(state)
            else:
                action = player2(state)

            print("\n--- SELECTED ACTION ---")
            print(f"Player {player_id + 1}: {action}")

            # Apply the action and obtain the next state
            state, player_id = env.step(action, raw_action = True)
            decision += 1

        print(f"\n{'=' * 50}")
        print("GAME FINISHED")
        print("Final payoffs:", env.get_payoffs())
        player1profit += env.get_payoffs()[0]
        print("Total profit (BB):", player1profit)
        print("Average BB/100:", player1profit / 10000 * 100)


if __name__ == "__main__":
    main()



