# src/features.py

import numpy as np
from scipy import signal
from src.config import FS, BP_LOW, BP_HIGH


def compute_fft(block, fs=FS):
    """
    Compute one-sided FFT power spectrum.
    Returns:
        freqs, power
    """
    windowed = block * np.hanning(len(block))
    spectrum = np.fft.rfft(windowed)
    power = np.abs(spectrum) ** 2
    freqs = np.fft.rfftfreq(len(block), d=1 / fs)
    return freqs, power


def compute_dominant_frequency(block, fs=FS, fmin=BP_LOW, fmax=BP_HIGH):
    """
    Find dominant frequency in the target band.
    """
    freqs, power = compute_fft(block, fs=fs)
    mask = (freqs >= fmin) & (freqs <= fmax)

    masked_freqs = freqs[mask]
    masked_power = power[mask]

    if len(masked_freqs) == 0:
        return 0.0

    return float(masked_freqs[np.argmax(masked_power)])


def compute_hilbert_phase(block):
    """
    Compute instantaneous phase using analytic signal.
    """
    analytic = signal.hilbert(block)
    phase = np.angle(analytic)
    envelope = np.abs(analytic)
    return phase, envelope


def compute_rms(block):
    """
    Root mean square amplitude.
    """
    return float(np.sqrt(np.mean(block ** 2)))


def compute_band_power(block, fs=FS, fmin=BP_LOW, fmax=BP_HIGH):
    """
    Compute total power in the target band using FFT.
    """
    freqs, power = compute_fft(block, fs=fs)
    mask = (freqs >= fmin) & (freqs <= fmax)
    return float(np.sum(power[mask]))


def compute_spectral_entropy(block, fs=FS):
    """
    Compute spectral entropy from FFT power distribution.
    """
    freqs, power = compute_fft(block, fs=fs)
    p = power / (np.sum(power) + 1e-12)
    entropy = -np.sum((p + 1e-12) * np.log(p + 1e-12))
    return float(entropy)


def compute_burst_rate_proxy(block, fs=FS):
    """
    Simple burst-rate proxy:
    count proportion of samples above mean(|x|)+2*std(x)
    and convert to events per second proxy.
    """
    threshold = np.mean(np.abs(block)) + 2.0 * np.std(block)
    burst_fraction = np.mean(np.abs(block) > threshold)
    burst_rate = burst_fraction * fs
    return float(burst_rate)


def extract_features(block, fs=FS):
    """
    Extract all major features from a filtered signal block.

    Returns:
        feature_dict
    """
    dominant_freq = compute_dominant_frequency(block, fs=fs)
    phase, envelope = compute_hilbert_phase(block)

    feature_dict = {
        "dominant_frequency_hz": dominant_freq,
        "phase_last_rad": float(phase[-1]),
        "envelope_mean": float(np.mean(envelope)),
        "envelope_max": float(np.max(envelope)),
        "rms": compute_rms(block),
        "band_power": compute_band_power(block, fs=fs),
        "spectral_entropy": compute_spectral_entropy(block, fs=fs),
        "burst_rate_proxy": compute_burst_rate_proxy(block, fs=fs),
    }

    return feature_dict