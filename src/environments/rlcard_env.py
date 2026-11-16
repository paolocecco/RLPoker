import rlcard


def create_environment(game="limit-holdem", seed=42):
    return rlcard.make(
        game,
        config={"seed": seed}
    )