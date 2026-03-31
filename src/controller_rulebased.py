# src/controller_rulebased.py

import numpy as np


def bin_envelope(envelope_mean):
    """
    Convert envelope strength into a coarse bin.
    """
    if envelope_mean < 0.12:
        return "low"
    elif envelope_mean < 0.22:
        return "medium"
    else:
        return "high"


def choose_rulebased_action(feature_dict, pain_class=None):
    """
    Simple interpretable controller.

    Inputs:
        feature_dict: output of extract_features(...)
        pain_class: optional classifier output
                    0 = low, 1 = medium, 2 = high

    Returns:
        action_dict with:
            gain_multiplier
            phase_offset
            envelope_bin
    """
    env = feature_dict["envelope_mean"]
    dom_freq = feature_dict["dominant_frequency_hz"]

    envelope_bin = bin_envelope(env)

    # Base gain rule from envelope
    if envelope_bin == "low":
        gain_multiplier = 0.7
    elif envelope_bin == "medium":
        gain_multiplier = 1.0
    else:
        gain_multiplier = 1.3

    # Optional refinement from pain class
    if pain_class is not None:
        if pain_class == 0:
            gain_multiplier *= 0.9
        elif pain_class == 1:
            gain_multiplier *= 1.0
        elif pain_class == 2:
            gain_multiplier *= 1.1

    # Phase correction rule (simple placeholder)
    # For very high dominant frequencies in band, slightly reduce offset error
    if dom_freq > 11.0:
        phase_offset = -0.05 * np.pi
    else:
        phase_offset = 0.0

    action_dict = {
        "gain_multiplier": float(gain_multiplier),
        "phase_offset": float(phase_offset),
        "envelope_bin": envelope_bin,
    }

    return action_dict