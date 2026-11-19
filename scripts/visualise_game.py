
import tkinter as tk

from environments.rlcard_env import create_environment
from agents.poker_agents import (
    improved_rule_based_agent,
    improved_random_agent
)


env = create_environment()

players = [
    improved_rule_based_agent,
    improved_random_agent
]

state, player_id = env.reset()
state = env.get_state(player_id)

last_action = "New hand"
selected_action = None
action_revealed = False

root = tk.Tk()
root.title("RLPoker Visualiser")

canvas = tk.Canvas(root, width=800, height=600, bg="#18221e")
canvas.pack()


def draw_card(card, x, y):
    suits = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}

    rank = card[1:]
    if rank == "T":
        rank = "10"

    suit = suits[card[0]]
    colour = "red" if card[0] in ["H", "D"] else "black"

    canvas.create_rectangle(
        x, y, x + 60, y + 85,
        fill="white"
    )

    canvas.create_text(
        x + 30, y + 42,
        text=rank + suit,
        fill=colour,
        font=("Arial", 24, "bold")
    )



def draw_table():
    canvas.delete("all")

    raw = state["raw_obs"]

    canvas.create_oval(
        40, 40, 760, 560,
        fill="#246344",
        outline="#87633d",
        width=12
    )

    canvas.create_text(
        400, 65,
        text="Player 2 - Random Agent",
        fill="white",
        font=("Arial", 18)
    )

    canvas.create_text(
        400, 535,
        text="Player 1 - Rule Agent",
        fill="white",
        font=("Arial", 18)
    )

    # Draw each player's hole cards
    for p in range(2):
        player_state = env.get_state(p)
        cards = player_state["raw_obs"]["hand"]

        y = 95 if p == 1 else 420

        for i, card in enumerate(cards):
            draw_card(card, 335 + i * 70, y)

        canvas.create_text(
            580, y + 40,
            text=f"Chips: {raw['all_chips'][p]}",
            fill="white",
            font=("Arial", 16)
        )

    # Draw community cards
    for i, card in enumerate(raw["public_cards"]):
        draw_card(card, 225 + i * 70, 235)

    canvas.create_text(
        400, 350,
        text=f"Pot: {sum(raw['all_chips'])} chips",
        fill="white",
        font=("Arial", 22, "bold")
    )

    canvas.create_text(
        400, 385,
        text=last_action,
        fill="gold",
        font=("Arial", 16)
    )

    if not env.is_over():
        draw_legal_actions()


def next_action():
    global state, player_id, last_action
    global selected_action, action_revealed

    if env.is_over():
        return

    if not action_revealed:
        # Select an action without executing it
        selected_action = players[player_id](state)

        last_action = (
            f"Player {player_id + 1} selected "
            f"{selected_action.upper()}"
        )

        action_revealed = True

    else:
        # Execute the previously selected action
        state, player_id = env.step(
            selected_action, raw_action=True
        )

        selected_action = None
        action_revealed = False

        if env.is_over():
            last_action = f"Payoffs: {env.get_payoffs()}"
        else:
            last_action = f"Player {player_id + 1} to act"

    draw_table()


def new_hand():
    global state, player_id, last_action
    global selected_action, action_revealed

    state, player_id = env.reset()
    state = env.get_state(player_id)

    selected_action = None
    action_revealed = False
    last_action = "New hand"

    draw_table()

def draw_legal_actions():
    legal_actions = state["raw_legal_actions"]

    canvas.create_text(
        400, 195,
        text=f"Player {player_id + 1}'s turn",
        fill="gold",
        font=("Arial", 18, "bold")
    )

    actions = ["fold", "check", "call", "raise"]

    for i, action in enumerate(actions):
        x = 180 + i * 115
        colour = "#555555"

        if action in legal_actions:
            colour = "#347dba"

        if action == selected_action:
            colour = "#35a853"

        canvas.create_rectangle(
            x, 565, x + 100, 595,
            fill=colour
        )

        canvas.create_text(
            x + 50, 580,
            text=action.upper(),
            fill="white",
            font=("Arial", 14, "bold")
        )

tk.Button(root, text="Next Action", command=next_action).pack()
tk.Button(root, text="New Hand", command=new_hand).pack()

draw_table()

root.mainloop()
