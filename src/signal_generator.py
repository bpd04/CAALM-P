# src/signal_generator.py

import numpy as np
from src.config import (
    FS,
    DURATION,
    INTENSITIES,
    PATIENTS,
    OSC_FREQ_MIN,
    OSC_FREQ_MAX,
    NOCICEPTIVE_BASE_UV,
    OSC_BASE_UV,
    BURST_BASE_UV,
)


def generate_time_vector(fs=FS, duration=DURATION):
    """
    Create the simulation time axis.
    Returns:
        t : numpy array of shape (N,)
    """
    n = int(fs * duration)
    t = np.arange(n) / fs
    return t


def generate_nociceptive_component(t, intensity_scale):
    """
    Generate the baseline nociceptive component.
    This is a slow-varying baseline pain-related signal.
    """
    x_noc = NOCICEPTIVE_BASE_UV * intensity_scale * (
        1.0 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
    )
    return x_noc


def generate_oscillatory_component(t, intensity_scale, patient_params, rng):
    """
    Generate the pathological oscillatory component.
    This represents the abnormal rhythmic pain-related neural activity.
    """
    f0 = rng.uniform(OSC_FREQ_MIN, OSC_FREQ_MAX)
    phi0 = rng.uniform(0, 2 * np.pi)

    slow_mod = 1.0 + 0.2 * np.sin(2 * np.pi * 0.12 * t + rng.uniform(0, 2 * np.pi))

    x_osc = (
        OSC_BASE_UV
        * intensity_scale
        * patient_params["osc"]
        * slow_mod
        * np.sin(2 * np.pi * f0 * t + phi0)
    )

    return x_osc, f0, phi0


def generate_burst_component(t, intensity_scale, patient_params, rng, fs=FS):
    """
    Generate irregular burst-like ectopic activity.
    We model this as sparse random events convolved with a decaying oscillatory kernel.
    """
    n = len(t)

    # Event rate increases with intensity and patient burst tendency
    event_rate = 1.2 * intensity_scale * patient_params["bursts"]  # events/sec approx
    events = rng.poisson(event_rate / fs, n).astype(float)

    kernel_t = np.arange(int(0.08 * fs)) / fs
    burst_freq = rng.uniform(18.0, 23.0)

    kernel = np.exp(-kernel_t / 0.015) * np.sin(2 * np.pi * burst_freq * kernel_t)
    kernel /= (np.max(np.abs(kernel)) + 1e-12)

    x_burst = np.convolve(events, kernel, mode="same")
    x_burst = x_burst * (BURST_BASE_UV * intensity_scale * patient_params["bursts"])

    return x_burst


def generate_central_gain(t, intensity_scale, patient_params, rng, fs=FS):
    """
    Generate a slow-varying central sensitization gain.
    This amplifies the incoming peripheral pain signal over time.
    """
    n = len(t)

    # Create slow random drift
    white = rng.normal(0, 1, n)
    win = int(0.4 * fs)
    win = max(win, 3)

    kernel = np.ones(win) / win
    smooth = np.convolve(np.abs(white), kernel, mode="same")

    smooth = (smooth - smooth.min()) / (smooth.max() - smooth.min() + 1e-12)

    g_c = 1.0 + 0.8 * (patient_params["central"] * intensity_scale - 0.4) * smooth
    return g_c


def generate_noise(t, rng):
    """
    Generate small white noise component.
    """
    noise = rng.normal(0, 2e-6, len(t))
    return noise


def generate_pain_signal(intensity="medium", patient_key="peripheral_dominant", seed=0):
    """
    Main signal generator function.

    Args:
        intensity (str): "low", "medium", or "high"
        patient_key (str): one of the patient profile keys
        seed (int): random seed for reproducibility

    Returns:
        t : time vector
        raw_signal : final synthetic pain signal
        meta : dictionary with metadata
    """
    rng = np.random.default_rng(seed)

    intensity_scale = INTENSITIES[intensity]
    patient_params = PATIENTS[patient_key]

    t = generate_time_vector()

    x_noc = generate_nociceptive_component(t, intensity_scale)
    x_osc, f0, phi0 = generate_oscillatory_component(t, intensity_scale, patient_params, rng)
    x_burst = generate_burst_component(t, intensity_scale, patient_params, rng)
    g_c = generate_central_gain(t, intensity_scale, patient_params, rng)
    noise = generate_noise(t, rng)

    raw_signal = g_c * (x_noc + x_osc + x_burst) + noise

    meta = {
        "intensity": intensity,
        "patient_key": patient_key,
        "dominant_frequency_hz": f0,
        "initial_phase_rad": phi0,
        "central_gain_mean": float(np.mean(g_c)),
        "central_gain_max": float(np.max(g_c)),
    }

    return t, raw_signal, meta