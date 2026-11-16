
import random
import numpy as np

from environments.rlcard_env import create_environment

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

def display_reduced_state(state, player_id, decision):
    raw = state["raw_obs"]
    legal_actions = list(state["legal_actions"].keys())
    print(" ")
    print("its player: " +  str(player_id + 1) + "s turn descision " + str(decision))
    print(" ")
    print("Hole cards:", raw["hand"])
    print("Community cards:", raw["public_cards"])
    print("Chips committed:", raw["all_chips"])
    print("Pot size:", sum(raw["all_chips"]))
    print("Raises per round:", raw["raise_nums"])

    print("\n--- LEGAL ACTIONS ---")
    for action_id in legal_actions:
        print(f"{action_id}: {ACTION_NAMES[action_id]}")

    return legal_actions


def main():
    env = create_environment()
    player1profit = 0 

    for episode in range(10):
        state, player_id = env.reset()

        # Play 10 full hands
        decision = 1

        while not env.is_over():

            legal_actions = display_reduced_state(
                state, player_id, decision
            )

            # Temporary random policy
            action = random.choice(legal_actions)

            print("\n--- SELECTED ACTION ---")
            print(f"Player {player_id}: {ACTION_NAMES[action]}")

            # Apply the action and obtain the next state
            state, player_id = env.step(action)
            decision += 1

        print(f"\n{'=' * 50}")
        print("GAME FINISHED")
        print("Final payoffs:", env.get_payoffs())
        player1profit += env.get_payoffs()[0]
        print("Total profit (BB):", player1profit)


if __name__ == "__main__":
    main()
