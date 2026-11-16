import rlcard
import random


def create_environment(game="limit-holdem"):
    seed = random.randint(0, 1000000)
    return rlcard.make(
        game,
        config={"seed": seed}
    )