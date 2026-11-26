import rlcard
import random
from . import extended_rlcard_env  # registers limit-holdem-ext


# def create_environment(game="limit-holdem"):
#     seed = random.randint(0, 1000000)
#     return rlcard.make(
#         game,
#         config={"seed": seed}
#     )


def create_environment(game="limit-holdem-ext", seed=None, config=None):
    if seed is None:
        seed = random.randint(0, 1000000)
    return rlcard.make(game, config={"seed": seed, **(config or {})})