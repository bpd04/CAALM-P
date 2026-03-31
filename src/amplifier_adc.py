# src/amplifier_adc.py

import numpy as np
from scipy import signal
from src.config import (
    AMP_GAIN,
    AMP_WHITE_NOISE_UV,
    AMP_FLICKER_NOISE_UV,
    AMP_CLIP_VOLT,
    ADC_BITS,
    ADC_VREF,
)


def generate_flicker_noise(n, rng):
    """
    Generate simple 1/f-like noise using a shaping filter.
    """
    white = rng.normal(0, 1, n)

    # Simple IIR-shaped pink-ish noise
    b = [0.049922, 0.095993, 0.050612, -0.004408]
    a = [1.0, -2.494956, 2.017265, -0.522189]

    y = signal.lfilter(b, a, white)
    y = y / (np.std(y) + 1e-12)
    return AMP_FLICKER_NOISE_UV * y


def apply_amplifier(electrode_signal, gain=AMP_GAIN, seed=0):
    """
    Simulate instrumentation amplifier:
    - add white noise
    - add flicker noise
    - amplify
    - clip to hardware voltage range
    """
    rng = np.random.default_rng(seed)

    n = len(electrode_signal)

    white_noise = rng.normal(0, AMP_WHITE_NOISE_UV, n)
    flicker_noise = generate_flicker_noise(n, rng)

    amp_input = electrode_signal + white_noise + flicker_noise
    amplified_signal = gain * amp_input

    # Clip to amplifier output range
    amplified_signal = np.clip(amplified_signal, -AMP_CLIP_VOLT, AMP_CLIP_VOLT)

    meta = {
        "gain": gain,
        "white_noise_std": float(np.std(white_noise)),
        "flicker_noise_std": float(np.std(flicker_noise)),
        "amplified_min": float(np.min(amplified_signal)),
        "amplified_max": float(np.max(amplified_signal)),
    }

    return amplified_signal, meta


def adc_quantize(amplified_signal, v_ref=ADC_VREF, bits=ADC_BITS):
    """
    Simulate ADC quantization.
    """
    q = (2 * v_ref) / (2 ** bits)

    clipped = np.clip(amplified_signal, -v_ref, v_ref - q)
    codes = np.round((clipped + v_ref) / q)
    quantized_signal = codes * q - v_ref

    meta = {
        "adc_bits": bits,
        "v_ref": v_ref,
        "quantization_step": q,
        "quantized_min": float(np.min(quantized_signal)),
        "quantized_max": float(np.max(quantized_signal)),
    }

    return quantized_signal, meta