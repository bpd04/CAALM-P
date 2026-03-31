# src/electrode_model.py

import numpy as np
from src.config import FS, MOTION_ARTIFACT_UV, MAINS_INTERFERENCE_UV, MAINS_FREQ


def generate_contact_profile(t, rng):
    """
    Simulate slow variation in electrode-skin contact quality.
    Output stays roughly between 0.82 and 0.98.
    """
    contact = 0.90 + 0.08 * np.sin(2 * np.pi * 0.20 * t + rng.uniform(0, 2 * np.pi))
    return contact


def generate_motion_artifact(t, rng):
    """
    Simulate motion artifact as sparse, slow disturbances.
    """
    motion_base = (np.sign(np.sin(2 * np.pi * 0.35 * t)) + 1.0) / 2.0
    motion = MOTION_ARTIFACT_UV * motion_base * (1.0 + 0.2 * rng.normal(size=len(t)))
    return motion


def generate_mains_interference(t, rng):
    """
    Simulate 50 Hz powerline interference.
    """
    mains = MAINS_INTERFERENCE_UV * np.sin(2 * np.pi * MAINS_FREQ * t + rng.uniform(0, 2 * np.pi))
    return mains


def apply_electrode_model(raw_signal, t, seed=0):
    """
    Apply the full electrode pickup model:
    - contact variation
    - motion artifact
    - mains interference

    Returns:
        electrode_signal
        meta
    """
    rng = np.random.default_rng(seed)

    contact = generate_contact_profile(t, rng)
    motion = generate_motion_artifact(t, rng)
    mains = generate_mains_interference(t, rng)

    electrode_signal = contact * raw_signal + motion + mains

    meta = {
        "contact_mean": float(np.mean(contact)),
        "contact_min": float(np.min(contact)),
        "contact_max": float(np.max(contact)),
        "motion_std": float(np.std(motion)),
        "mains_std": float(np.std(mains)),
    }

    return electrode_signal, meta