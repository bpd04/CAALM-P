# src/controller_rl.py

import numpy as np
from src.config import ACTIONS, ALPHA, GAMMA, EPSILON


ENVELOPE_BINS = ["low", "medium", "high"]

# Reachable-state redesign:
# Use only the 5 state combinations that actually appear in the simulator.
# Index mapping:
#   0 -> (pain=0, env="low")
#   1 -> (pain=0, env="medium")
#   2 -> (pain=1, env="medium")
#   3 -> (pain=1, env="high")
#   4 -> (pain=2, env="high")
REACHABLE_STATE_PAIRS = [
    (0, "low"),
    (0, "medium"),
    (1, "medium"),
    (1, "high"),
    (2, "high"),
]


def _pair_distance(pain_a, env_a, pain_b, env_b):
    env_idx_a = ENVELOPE_BINS.index(env_a)
    env_idx_b = ENVELOPE_BINS.index(env_b)
    return abs(pain_a - pain_b) + abs(env_idx_a - env_idx_b)


def encode_state(pain_class, envelope_bin):
    """
    Map the raw (pain_class, envelope_bin) pair into one of the 5 reachable states.
    If the exact pair is not in the reachable manifold, map to the nearest reachable state.
    """
    pair = (pain_class, envelope_bin)
    if pair in REACHABLE_STATE_PAIRS:
        return REACHABLE_STATE_PAIRS.index(pair)

    # Map unreachable pair to nearest reachable pair
    best_idx = 0
    best_dist = 1e9
    for i, (p, e) in enumerate(REACHABLE_STATE_PAIRS):
        d = _pair_distance(pain_class, envelope_bin, p, e)
        if d < best_dist:
            best_dist = d
            best_idx = i

    return best_idx


def decode_state_idx(state_idx):
    """
    Return the reachable-state pair for reporting.
    """
    return REACHABLE_STATE_PAIRS[state_idx]


def initialize_q_table():
    """
    Q-table shape = (5 reachable states, num_actions)
    """
    num_states = len(REACHABLE_STATE_PAIRS)
    num_actions = len(ACTIONS)
    Q = np.zeros((num_states, num_actions), dtype=float)
    return Q


def select_action(Q, state, epsilon=EPSILON, rng=None):
    """
    Epsilon-greedy action selection.
    """
    if rng is None:
        rng = np.random.default_rng()

    if rng.random() < epsilon:
        action_idx = int(rng.integers(0, Q.shape[1]))
    else:
        action_idx = int(np.argmax(Q[state]))

    return action_idx


def select_action_greedy(Q, state):
    """
    Greedy action selection for evaluation after training.
    """
    return int(np.argmax(Q[state]))


def get_action_params(action_idx):
    """
    Return (gain_multiplier, phase_offset) from ACTIONS list.
    """
    gain_multiplier, phase_offset = ACTIONS[action_idx]
    return gain_multiplier, phase_offset


def compute_reward(prev_envelope, next_envelope, current_mA, phase_offset):
    """
    Reward favors reduction in envelope amplitude and penalizes
    stronger current and large phase offset.
    """
    reduction_term = 25.0 * (prev_envelope - next_envelope)
    current_penalty = 0.06 * current_mA
    phase_penalty = 0.20 * abs(phase_offset)

    reward = reduction_term - current_penalty - phase_penalty
    return float(reward)


def update_q(Q, state, action_idx, reward, next_state, alpha=ALPHA, gamma=GAMMA):
    """
    Standard Q-learning update.
    """
    best_next = np.max(Q[next_state])

    Q[state, action_idx] = (
        (1 - alpha) * Q[state, action_idx]
        + alpha * (reward + gamma * best_next)
    )

    return Q


def epsilon_by_episode(
    episode_idx,
    total_episodes,
    eps_start=0.35,
    eps_end=0.05,
):
    """
    Linear epsilon decay across training.
    """
    if total_episodes <= 1:
        return eps_end

    frac = episode_idx / (total_episodes - 1)
    eps = eps_start + frac * (eps_end - eps_start)
    return float(max(eps_end, min(eps_start, eps)))