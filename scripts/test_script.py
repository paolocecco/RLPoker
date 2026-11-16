from rlcard.agents import RandomAgent
from environments import rlcard_env


def main():
    env = rlcard_env.create_environment()

    agents = [
        RandomAgent(num_actions=env.num_actions)
        for _ in range(env.num_players)
    ]

    env.set_agents(agents)

    trajectories, payoffs = env.run(is_training=False)

    print("Players:", env.num_players)
    print("Actions:", env.num_actions)
    print("State shapes:", env.state_shape)
    print("Payoffs:", payoffs)


if __name__ == "__main__":
    main()