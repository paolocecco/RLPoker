# RLPoker

An experimental reinforcement-learning project for Limit Texas Hold'em, built
with [RLCard](https://github.com/datamllab/rlcard).

## Getting started

Create and activate a virtual environment, then install the project and its
dependencies in editable mode. Run these commands from the repository root:

```zsh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Editable installation makes the `environments` package importable without
setting `PYTHONPATH`. Repeat the install command after cloning the repository or
creating a new virtual environment.

## Run the example

```zsh
python scripts/test_script.py
```

The script creates a Limit Hold'em environment, assigns an RLCard
`RandomAgent` to each player, runs one game, and prints the player count,
available actions, state shapes, and payoffs. The payoff values vary between
runs.

## Project layout

```text
src/environments/rlcard_env.py  Creates the RLCard environment
scripts/test_script.py         Runs a sample game
requirements.txt               Project dependencies
pyproject.toml                 Packaging configuration
```

## Dependencies

Dependencies are listed in `requirements.txt` and are installed by
`python -m pip install -e .`.
