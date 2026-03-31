# src/metrics.py

import numpy as np


def compute_oscillation_suppression(prev_band_power, next_band_power):
    """
    Percentage reduction in oscillatory band power.
    """
    if abs(prev_band_power) < 1e-12:
        return 0.0
    return float(100.0 * (prev_band_power - next_band_power) / prev_band_power)


def compute_pain_proxy_reduction(prev_envelope, next_envelope):
    """
    Percentage reduction in envelope-based pain proxy.
    """
    if abs(prev_envelope) < 1e-12:
        return 0.0
    return float(100.0 * (prev_envelope - next_envelope) / prev_envelope)


def compute_snr(signal_component, noise_component):
    """
    SNR in dB using mean-square power ratio.
    """
    sig_power = np.mean(signal_component ** 2)
    noise_power = np.mean(noise_component ** 2) + 1e-12
    snr_db = 10.0 * np.log10(sig_power / noise_power)
    return float(snr_db)


def compute_mean_current(current_values_mA):
    """
    Average stimulation current in mA.
    """
    return float(np.mean(current_values_mA))


def build_results_dict(
    prev_feat,
    next_feat,
    current_command_mA,
    reward,
    snr_db
):
    """
    Combine all metrics into one summary dictionary.
    """
    osc_supp = compute_oscillation_suppression(
        prev_feat["band_power"],
        next_feat["band_power"]
    )

    pain_proxy_reduction = compute_pain_proxy_reduction(
        prev_feat["envelope_mean"],
        next_feat["envelope_mean"]
    )

    results = {
        "prev_dominant_freq_hz": float(prev_feat["dominant_frequency_hz"]),
        "next_dominant_freq_hz": float(next_feat["dominant_frequency_hz"]),
        "prev_envelope_mean": float(prev_feat["envelope_mean"]),
        "next_envelope_mean": float(next_feat["envelope_mean"]),
        "prev_band_power": float(prev_feat["band_power"]),
        "next_band_power": float(next_feat["band_power"]),
        "oscillation_suppression_percent": float(osc_supp),
        "pain_proxy_reduction_percent": float(pain_proxy_reduction),
        "current_command_mA": float(current_command_mA),
        "reward": float(reward),
        "snr_db": float(snr_db),
    }

    return results