"""
Extended state representation for RLCard Limit Texas Hold'em.

Default layout (164 inputs), always from the point of view of the player to act:

    Block                     Inputs  Encoding
    hole_cards                  52    binary multi-hot (my two private cards)
    community_cards             52    binary multi-hot (the board)
    my_raises                   20    one-hot, 4 rounds x 5 slots (0-4 raises)
    opp_raises                  20    one-hot, 4 rounds x 5 slots (0-4 raises)
    last_aggressor              12    one-hot, 4 rounds x [nobody, me, opponent]
    position                     1    1 if I am the small blind, else 0
    chips                        3    my chips / 50, opponent chips / 50, pot / 100
    betting_round                4    one-hot: pre-flop, flop, turn, river

Each block can be switched off through the config, so the variants for the
state-representation comparison are just different configs:

    rlcard.make('limit-holdem')                          # RLCard default, 72 inputs
    rlcard.make('limit-holdem-ext', config=GROUP_131)    # group's 131 (RLCard raise counts, incl. bug)
    rlcard.make('limit-holdem-ext', config=GROUP_131_FIXED)  # same 131, counts from our own log
    rlcard.make('limit-holdem-ext')                      # full 164

Raise counts and "who bet last" are computed from our own record of actions,
not RLCard's `raise_nums`. RLCard builds the first observation of each hand
before resetting `raise_nums`, so its first observation of every hand (after
the first) still contains the previous hand's raise counts.

Usage:
    import rlcard
    import environments.extended_rlcard_env   # registers 'limit-holdem-ext'
    env = rlcard.make('limit-holdem-ext')
    env.state_shape[0]                 # [164]
"""

from collections import OrderedDict

import numpy as np
from rlcard.envs.limitholdem import LimitholdemEnv
from rlcard.envs.registration import register, registry

NUM_ROUNDS = 4
MAX_RAISES = 4                  # RLCard allows at most 4 raises per round
RAISE_BINS = MAX_RAISES + 1     # one-hot over 0..4 raises
MAX_PLAYER_CHIPS = 50           # most one player can commit in RLCard's limit hold'em
MAX_POT = 2 * MAX_PLAYER_CHIPS
BOARD_SIZE_TO_ROUND = {0: 0, 3: 1, 4: 2, 5: 3}

# Default config: every block on, raise counts split by player
DEFAULT_BLOCKS = {
    'hole_cards': True,
    'community_cards': True,
    'raise_encoding': 'split',   # 'split' (me/opp, 40) | 'shared' (20, from our log)
                                 # | 'shared_rlcard' (20, RLCard's own counts, incl. bug)
    'last_aggressor': True,
    'position': True,
    'chips': True,
    'betting_round': True,
}

# The group's original 131-input version, for comparison
GROUP_131 = {'raise_encoding': 'shared_rlcard', 'last_aggressor': False,
             'position': False}
# The same 131 inputs, with raise counts taken from our own log (bug fixed)
GROUP_131_FIXED = {**GROUP_131, 'raise_encoding': 'shared'}


class ExtendedLimitholdemEnv(LimitholdemEnv):
    """RLCard limit hold'em with a configurable, player-relative observation."""

    def __init__(self, config):
        self.blocks = {k: config.get(k, v) for k, v in DEFAULT_BLOCKS.items()}
        if self.blocks['raise_encoding'] not in ('split', 'shared', 'shared_rlcard'):
            raise ValueError(f"unknown raise_encoding {self.blocks['raise_encoding']!r}")
        super().__init__(config)
        self.name = 'limit-holdem-ext'

        self.layout = self._build_layout()          # block name -> (start, end)
        self.obs_size = max(end for _, end in self.layout.values())
        self.state_shape = [[self.obs_size] for _ in range(self.num_players)]

        self._events = []                # (round, player, action) for this hand
        self._small_blind_player = None
        self._pov = None                 # whose point of view get_state() encodes

    def _build_layout(self):
        sizes = []
        b = self.blocks
        if b['hole_cards']:
            sizes.append(('hole_cards', 52))
        if b['community_cards']:
            sizes.append(('community_cards', 52))
        if b['raise_encoding'] == 'split':
            sizes += [('my_raises', NUM_ROUNDS * RAISE_BINS),
                      ('opp_raises', NUM_ROUNDS * RAISE_BINS)]
        else:
            sizes.append(('shared_raises', NUM_ROUNDS * RAISE_BINS))
        if b['last_aggressor']:
            sizes.append(('last_aggressor', NUM_ROUNDS * 3))
        if b['position']:
            sizes.append(('position', 1))
        if b['chips']:
            sizes.append(('chips', 3))
        if b['betting_round']:
            sizes.append(('betting_round', NUM_ROUNDS))

        layout, start = OrderedDict(), 0
        for name, size in sizes:
            layout[name] = (start, start + size)
            start += size
        return layout

    # ------------------------------------------------------------------ #
    # Recording who did what in which round
    # ------------------------------------------------------------------ #
    def reset(self):
        self._events = []
        self._small_blind_player = None
        return super().reset()

    def step(self, action, raw_action=False):
        # Record before the game moves on, while round_counter and
        # game_pointer still describe this decision.
        action_str = action if raw_action else self._decode_action(action)
        self._events.append((self.game.round_counter, self.game.game_pointer, action_str))
        return super().step(action, raw_action)

    def step_back(self):
        ok = super().step_back()
        if ok and self._events:
            self._events.pop()
        return ok

    def get_state(self, player_id):
        # RLCard calls this for every player at the end of env.run(),
        # so encode from that player's point of view.
        self._pov = player_id
        try:
            return super().get_state(player_id)
        finally:
            self._pov = None

    def _find_small_blind(self):
        # The first observation of a hand is built before any chips move,
        # when the small blind is the player with exactly 1 chip in.
        if self._small_blind_player is None:
            for p in self.game.players:
                if p.in_chips == self.game.small_blind:
                    self._small_blind_player = p.player_id
                    break
        return self._small_blind_player

    # ------------------------------------------------------------------ #
    # Encoding
    # ------------------------------------------------------------------ #
    def _extract_state(self, state):
        extracted = super()._extract_state(state)   # keeps legal_actions, raw_obs, ...
        me = self._pov if self._pov is not None else self.game.game_pointer
        opp = 1 - me
        small_blind = self._find_small_blind()      # always call, so it's cached at reset

        # Raise counts and last aggressor from our own action record
        my_raises = [0] * NUM_ROUNDS
        opp_raises = [0] * NUM_ROUNDS
        last_aggressor = [0] * NUM_ROUNDS            # 0 nobody, 1 me, 2 opponent
        for rnd, actor, action in self._events:
            if action == 'raise':
                if actor == me:
                    my_raises[rnd] += 1
                    last_aggressor[rnd] = 1
                else:
                    opp_raises[rnd] += 1
                    last_aggressor[rnd] = 2

        obs = np.zeros(self.obs_size, dtype=np.float32)

        def block(name):
            start, end = self.layout[name]
            return obs[start:end]                    # a view, so writes go into obs

        if 'hole_cards' in self.layout:
            for card in state['hand']:
                block('hole_cards')[self.card2index[card]] = 1
        if 'community_cards' in self.layout:
            for card in state['public_cards']:
                block('community_cards')[self.card2index[card]] = 1

        if 'my_raises' in self.layout:
            for r in range(NUM_ROUNDS):
                block('my_raises')[r * RAISE_BINS + min(my_raises[r], MAX_RAISES)] = 1
                block('opp_raises')[r * RAISE_BINS + min(opp_raises[r], MAX_RAISES)] = 1
        if 'shared_raises' in self.layout:
            if self.blocks['raise_encoding'] == 'shared_rlcard':
                totals = list(state['raise_nums'])   # RLCard's counts, as the group had
            else:
                totals = [m + o for m, o in zip(my_raises, opp_raises)]
            for r in range(NUM_ROUNDS):
                block('shared_raises')[r * RAISE_BINS + min(totals[r], MAX_RAISES)] = 1

        if 'last_aggressor' in self.layout:
            for r in range(NUM_ROUNDS):
                block('last_aggressor')[r * 3 + last_aggressor[r]] = 1

        if 'position' in self.layout:
            block('position')[0] = 1.0 if small_blind == me else 0.0

        if 'chips' in self.layout:
            chips = state['all_chips']
            block('chips')[:] = [chips[me] / MAX_PLAYER_CHIPS,
                                 chips[opp] / MAX_PLAYER_CHIPS,
                                 (chips[me] + chips[opp]) / MAX_POT]

        if 'betting_round' in self.layout:
            block('betting_round')[BOARD_SIZE_TO_ROUND[len(state['public_cards'])]] = 1

        extracted['obs'] = obs
        return extracted


def describe_obs(env, obs):
    """Decode an observation into readable values (for debugging and tests)."""
    out = {}
    L = env.layout

    def part(name):
        start, end = L[name]
        return obs[start:end]

    def counts(name):
        v = part(name)
        return [int(np.argmax(v[r * RAISE_BINS:(r + 1) * RAISE_BINS])) for r in range(NUM_ROUNDS)]

    if 'hole_cards' in L:
        out['num_hole_cards'] = int(part('hole_cards').sum())
    if 'community_cards' in L:
        out['num_community_cards'] = int(part('community_cards').sum())
    if 'my_raises' in L:
        out['my_raises'], out['opp_raises'] = counts('my_raises'), counts('opp_raises')
    if 'shared_raises' in L:
        out['shared_raises'] = counts('shared_raises')
    if 'last_aggressor' in L:
        names = ['nobody', 'me', 'opp']
        v = part('last_aggressor')
        out['last_aggressor'] = [names[int(np.argmax(v[r * 3:(r + 1) * 3]))] for r in range(NUM_ROUNDS)]
    if 'position' in L:
        out['small_blind'] = bool(part('position')[0])
    if 'chips' in L:
        c = part('chips')
        out['my_chips'] = round(float(c[0]) * MAX_PLAYER_CHIPS)
        out['opp_chips'] = round(float(c[1]) * MAX_PLAYER_CHIPS)
        out['pot'] = round(float(c[2]) * MAX_POT)
    if 'betting_round' in L:
        out['betting_round'] = ['preflop', 'flop', 'turn', 'river'][int(np.argmax(part('betting_round')))]
    return out


if 'limit-holdem-ext' not in registry.env_specs:
    register(env_id='limit-holdem-ext',
             entry_point=f'{__name__}:ExtendedLimitholdemEnv')