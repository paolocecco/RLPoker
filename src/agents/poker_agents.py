import random
from rlcard import models
from agents.linear_q_agent import LinearQAgent

rule_agent = models.load("limit-holdem-rule-v1").agents[0]



linear_agent = LinearQAgent(epsilon=0)
linear_agent.load("linear_agent.npz")

def trained_linear_agent(state):
    action_id = linear_agent.choose_action(state)

    actions = ["call", "raise", "fold", "check"]

    return actions[action_id]

def random_agent(state):
    legal_actions = state["raw_legal_actions"]
    return random.choice(legal_actions)

def improved_random_agent(state):
    legal_actions = state["raw_legal_actions"].copy()

    if "check" in legal_actions and "fold" in legal_actions:
        legal_actions.remove("fold")

    return random.choice(legal_actions)

def rule_based_agent(state):
    return rule_agent.step(state)

def improved_rule_based_agent(state):
    action = rule_based_agent(state)

    if action == "fold" and "check" in state["raw_legal_actions"]:
        action = "check"

    return action
