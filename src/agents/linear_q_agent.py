
import numpy as np
import random


class LinearQAgent:

    def __init__(self, alpha=0.01, gamma=1.0, epsilon=1.0):

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        self.weights = np.zeros((4, 72))
        self.biases = np.zeros(4)

    def get_q_values(self, state):

        obs = state["obs"]

        return self.weights @ obs + self.biases

    def choose_action(self, state):

        legal_actions = list(state["legal_actions"].keys())

        # Exploration
        if random.random() < self.epsilon:
            return random.choice(legal_actions)

        # Exploitation
        q_values = self.get_q_values(state)

        best_value = max(q_values[a] for a in legal_actions)

        best_actions = [
            a for a in legal_actions
            if q_values[a] == best_value
        ]

        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, done):

        obs = state["obs"]

        current_q = self.get_q_values(state)[action]

        if done:
            target = reward
        else:
            next_q_values = self.get_q_values(next_state)
            legal_actions = list(next_state["legal_actions"].keys())

            target = reward + self.gamma * max(
                next_q_values[a] for a in legal_actions
            )

        error = target - current_q

        # Update weights and bias
        self.weights[action] += self.alpha * error * obs
        self.biases[action] += self.alpha * error

    def save(self, filename):
        np.savez(
            filename,
            weights=self.weights,
            biases=self.biases
        )

    def load(self, filename):
        with np.load(filename) as data:
            self.weights = data["weights"]
            self.biases = data["biases"]
