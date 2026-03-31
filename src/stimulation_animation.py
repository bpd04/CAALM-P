import numpy as np
from scipy import signal
from src.config import (
    FS,
    MIN_CURRENT_MA,
    MAX_CURRENT_MA,
    GATE_SUPPORT_FREQ,
    GATE_SUPPORT_WEIGHT,
)


def clip_stimulation_current(current_mA, min_current=MIN_CURRENT_MA, max_current=MAX_CURRENT_MA):
    """
    Clip stimulation current command to safe bounds.
    """
    return float(np.clip(current_mA, min_current, max_current))


def generate_antiphase_wave(freq_hz, phase_rad, amplitude, block_n, fs=FS, phase_offset=0.0):
    """
    Generate anti-phase waveform:
    same frequency as detected oscillation,
    shifted by pi + optional phase correction.
    """
    t_block = np.arange(block_n) / fs
    wave = amplitude * np.sin(2 * np.pi * freq_hz * t_block + phase_rad + np.pi + phase_offset)
    return wave


def generate_gate_support(amplitude, block_n, fs=FS, gate_freq=GATE_SUPPORT_FREQ):
    """
    Optional small higher-frequency helper component.
    """
    t_block = np.arange(block_n) / fs
    gate = amplitude * np.sin(2 * np.pi * gate_freq * t_block)
    return gate


def combine_stimulation(anti_wave, gate_wave, gate_weight=GATE_SUPPORT_WEIGHT):
    """
    Combine anti-phase waveform and optional gate-support waveform.
    """
    return anti_wave + gate_weight * gate_wave


def map_control_to_amplitude(envelope_mean, gain_multiplier=1.0, amplitude_scale=55e-6):
    """
    Map signal envelope to stimulation amplitude.
    """
    current_mA = 10.0 * gain_multiplier * envelope_mean
    current_mA = clip_stimulation_current(current_mA)

    amplitude = amplitude_scale * (current_mA / MAX_CURRENT_MA)

    meta = {
        "gain_multiplier": float(gain_multiplier),
        "current_command_mA": float(current_mA),
        "wave_amplitude": float(amplitude),
        "amplitude_scale": float(amplitude_scale),
    }

    return float(amplitude), meta


def _extract_narrowband_component(block, freq_hz, fs=FS, half_band=2.0, order=3):
    """
    Extract oscillatory component around dominant frequency.
    """
    low = max(1.0, freq_hz - half_band)
    high = min(fs / 2 - 1.0, freq_hz + half_band)

    if high <= low:
        return np.zeros_like(block)

    sos = signal.butter(order, [low, high], btype="bandpass", fs=fs, output="sos")
    osc = signal.sosfiltfilt(sos, block)
    return osc


def _safe_corr(a, b):
    """
    Correlation helper that avoids NaNs on near-constant signals.
    """
    a_std = np.std(a)
    b_std = np.std(b)
    if a_std < 1e-12 or b_std < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _estimate_stim_frequency_hz(stim_wave, fs=FS):
    """
    Lightweight diagnostic estimate of stimulation dominant frequency.
    Used only for metadata / instrumentation.
    """
    stim_wave = np.asarray(stim_wave, dtype=float)
    if len(stim_wave) < 8:
        return 0.0

    x = stim_wave - np.mean(stim_wave)
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), d=1.0 / fs)

    if len(freqs) <= 1:
        return 0.0

    valid = (freqs >= 0.5) & (freqs <= min(200.0, fs / 2 - 1.0))
    if not np.any(valid):
        return 0.0

    idx = np.argmax(np.abs(spec[valid]))
    return float(freqs[valid][idx])


def apply_oscillation_suppression_to_block(
    baseline_block,
    stim_wave,
    current_mA,
    dominant_freq_hz,
    patient_response=1.0,
    fs=FS,
    suppression_gain=0.8,
    max_suppression=0.55,
    match_gain=1.0,
):
    """
    Backward-compatible instrumented old-law plant model.

    Original old-law core:
        corr = corrcoef(osc_component, stim_wave)
        antiphase_raw = max(0, -corr)
        antiphase_match = min(1, match_gain * antiphase_raw)
        beta_preclip = suppression_gain * patient_response * current_norm * antiphase_match
        beta = clip(beta_preclip, 0, max_suppression)

    This keeps the strong Step-22B-style regime while allowing match_gain
    to be tuned by newer animation / benchmark scripts.
    """
    baseline_block = np.asarray(baseline_block, dtype=float)
    stim_wave = np.asarray(stim_wave, dtype=float)

    osc_component = _extract_narrowband_component(
        baseline_block,
        freq_hz=dominant_freq_hz,
        fs=fs,
        half_band=2.0,
        order=3,
    )

    residual_component = baseline_block - osc_component

    # Old-law anti-phase alignment
    corr = _safe_corr(osc_component, stim_wave)
    antiphase_raw = max(0.0, -corr)

    # Newer scripts may pass match_gain; old behavior is preserved at 1.0
    antiphase_match = float(np.clip(float(match_gain) * antiphase_raw, 0.0, 1.0))

    current_norm = float(np.clip(current_mA / MAX_CURRENT_MA, 0.0, 1.0))

    beta_preclip = float(suppression_gain * patient_response * current_norm * antiphase_match)
    beta = float(np.clip(beta_preclip, 0.0, max_suppression))

    controlled_osc = (1.0 - beta) * osc_component
    controlled_block = residual_component + controlled_osc

    # Diagnostics / metadata
    stim_rms = float(np.sqrt(np.mean(np.square(stim_wave))))
    osc_rms = float(np.sqrt(np.mean(np.square(osc_component))))
    residual_rms = float(np.sqrt(np.mean(np.square(residual_component))))
    stim_freq_hz = _estimate_stim_frequency_hz(stim_wave, fs=fs)
    freq_error_hz = float(abs(stim_freq_hz - dominant_freq_hz))

    meta = {
        "suppression_gain": float(suppression_gain),
        "max_suppression": float(max_suppression),
        "patient_response": float(patient_response),
        "dominant_freq_hz": float(dominant_freq_hz),

        "corr_osc_vs_stim": float(corr),
        "antiphase_raw": float(antiphase_raw),
        "match_gain": float(match_gain),
        "antiphase_match": float(antiphase_match),
        "current_norm": float(current_norm),
        "beta_preclip": float(beta_preclip),
        "beta_applied": float(beta),

        # compatibility keys for older / newer scripts
        "phase_term": float(antiphase_match),
        "freq_term": 1.0,
        "amp_term": float(current_norm),

        "stim_rms": float(stim_rms),
        "osc_rms": float(osc_rms),
        "residual_rms": float(residual_rms),
        "stim_freq_hz": float(stim_freq_hz),
        "freq_error_hz": float(freq_error_hz),
    }

    return controlled_block, meta