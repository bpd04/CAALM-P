# src/preprocessing.py

import numpy as np
from scipy import signal
from src.config import FS, NOTCH_FREQ, NOTCH_Q, BP_LOW, BP_HIGH


def apply_notch_filter(x, fs=FS, notch_freq=NOTCH_FREQ, q=NOTCH_Q):
    """
    Apply an IIR notch filter to suppress mains interference.
    """
    b, a = signal.iirnotch(notch_freq, q, fs=fs)
    y = signal.filtfilt(b, a, x)
    return y


def apply_bandpass_filter(x, fs=FS, low=BP_LOW, high=BP_HIGH, order=4):
    """
    Apply Butterworth bandpass filter to isolate the pain-related oscillation band.
    """
    sos = signal.butter(order, [low, high], btype="bandpass", fs=fs, output="sos")
    y = signal.sosfiltfilt(sos, x)
    return y


def preprocess_signal(x, fs=FS):
    """
    Full preprocessing pipeline:
    1. Notch filter
    2. Bandpass filter
    """
    x_notch = apply_notch_filter(x, fs=fs)
    x_filt = apply_bandpass_filter(x_notch, fs=fs)

    meta = {
        "fs": fs,
        "notch_freq": NOTCH_FREQ,
        "bandpass_low": BP_LOW,
        "bandpass_high": BP_HIGH,
    }

    return x_filt, meta