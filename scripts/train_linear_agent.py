
from environments.rlcard_env import create_environment
from agents.linear_q_agent import LinearQAgent
from agents.poker_agents import improved_random_agent


def main():

    env = create_environment()
    agent = LinearQAgent()

    num_episodes = 100000
    total_profit = 0
    recent_profit = 0

    for episode in range(num_episodes):

        state, player_id = env.reset()
        state = env.get_state(player_id)

        previous_state = None
        previous_action = None

        while not env.is_over():

            if player_id == 0:

                # Learn from our previous decision
                if previous_state is not None:
                    agent.learn(
                        previous_state,
                        previous_action,
                        0,
                        state,
                        False
                    )

                # Choose our next action
                action = agent.choose_action(state)

                previous_state = state
                previous_action = action

                state, player_id = env.step(action)

            else:

                # Opponent takes its turn
                action = improved_random_agent(state)

                state, player_id = env.step(
                    action, raw_action=True
                )

        reward = env.get_payoffs()[0]

        # Learn from the final outcome
        if previous_state is not None:
            agent.learn(
                previous_state,
                previous_action,
                reward,
                None,
                True
            )

        total_profit += reward
        recent_profit += reward

        # Gradually reduce exploration
        agent.epsilon = max(0.05, agent.epsilon * 0.99995)

        if (episode + 1) % 1000 == 0:

            print(
                "Episode:", episode + 1,
                "| Epsilon:", round(agent.epsilon, 3),
                "| Recent BB/100:", round(recent_profit / 10, 2)
            )

            recent_profit = 0

    print("Total profit:", total_profit)
    print("Average BB/100:", total_profit / num_episodes * 100)

    agent.save("linear_agent.npz")


if __name__ == "__main__":
    main()
