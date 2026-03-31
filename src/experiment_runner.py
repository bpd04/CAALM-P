# src/experiment_runner.py

import numpy as np

from src.signal_generator import generate_pain_signal
from src.electrode_model import apply_electrode_model
from src.amplifier_adc import apply_amplifier, adc_quantize
from src.preprocessing import preprocess_signal
from src.features import extract_features
from src.classifier import predict_pain_state
from src.controller_rulebased import bin_envelope
from src.controller_rl import encode_state, compute_reward
from src.stimulation import (
    map_control_to_amplitude,
    generate_antiphase_wave,
    generate_gate_support,
    combine_stimulation,
    apply_oscillation_suppression_to_block,
)
from src.metrics import compute_snr, build_results_dict
from src.config import INTENSITIES, PATIENTS


FS_HZ = 10000.0


def _prepare_case_signals(intensity="medium", patient_key="peripheral_dominant", seed=42):
    t, raw_signal, _ = generate_pain_signal(
        intensity=intensity,
        patient_key=patient_key,
        seed=seed,
    )

    electrode_signal, _ = apply_electrode_model(
        raw_signal=raw_signal,
        t=t,
        seed=seed + 1,
    )

    amplified_signal, _ = apply_amplifier(
        electrode_signal=electrode_signal,
        seed=seed + 2,
    )

    quantized_signal, _ = adc_quantize(amplified_signal)
    filtered_signal = preprocess_signal(quantized_signal)[0]

    block_n = int(0.5 * FS_HZ)
    block_1 = filtered_signal[:block_n]
    block_2_baseline = filtered_signal[block_n:2 * block_n]

    return quantized_signal, block_1, block_2_baseline, block_n


def _compute_oracle_score(row, objective="oscillation"):
    if objective == "oscillation":
        return float(row["oscillation_suppression_percent"])
    if objective == "pain":
        return float(row["pain_proxy_reduction_percent"])
    if objective == "reward":
        return float(row["reward"])
    if objective == "balanced":
        return (
            2.5 * float(row["oscillation_suppression_percent"])
            + 1.5 * float(row["pain_proxy_reduction_percent"])
            + 2.0 * float(row["reward"])
        )
    raise ValueError(f"Unknown objective: {objective}")


def _is_better_than_baseline(candidate, baseline):
    eps = 1e-9

    cand_osc = float(candidate["oscillation_suppression_percent"])
    base_osc = float(baseline["oscillation_suppression_percent"])
    if cand_osc > base_osc + eps:
        return True
    if cand_osc < base_osc - eps:
        return False

    cand_pain = float(candidate["pain_proxy_reduction_percent"])
    base_pain = float(baseline["pain_proxy_reduction_percent"])
    if cand_pain > base_pain + eps:
        return True
    if cand_pain < base_pain - eps:
        return False

    cand_reward = float(candidate["reward"])
    base_reward = float(baseline["reward"])
    return cand_reward > base_reward + eps


def _summarize_case_rows(rows):
    if len(rows) == 0:
        return {
            "mean_oscillation_suppression_percent": 0.0,
            "mean_pain_proxy_reduction_percent": 0.0,
            "mean_reward": 0.0,
            "positive_cases": 0,
            "cases_ge_50": 0,
            "cases_ge_70": 0,
            "cases_ge_85": 0,
            "cases_ge_90": 0,
            "max_oscillation_suppression_percent": 0.0,
            "min_oscillation_suppression_percent": 0.0,
        }

    osc_vals = [float(r["oscillation_suppression_percent"]) for r in rows]
    pain_vals = [float(r["pain_proxy_reduction_percent"]) for r in rows]
    reward_vals = [float(r["reward"]) for r in rows]

    return {
        "mean_oscillation_suppression_percent": float(np.mean(osc_vals)),
        "mean_pain_proxy_reduction_percent": float(np.mean(pain_vals)),
        "mean_reward": float(np.mean(reward_vals)),
        "positive_cases": int(sum(v > 0.0 for v in osc_vals)),
        "cases_ge_50": int(sum(v >= 50.0 for v in osc_vals)),
        "cases_ge_70": int(sum(v >= 70.0 for v in osc_vals)),
        "cases_ge_85": int(sum(v >= 85.0 for v in osc_vals)),
        "cases_ge_90": int(sum(v >= 90.0 for v in osc_vals)),
        "max_oscillation_suppression_percent": float(np.max(osc_vals)),
        "min_oscillation_suppression_percent": float(np.min(osc_vals)),
    }


def run_single_case_direct_params_static(
    clf,
    gain_multiplier,
    phase_offset,
    freq_offset_hz=0.0,
    intensity="medium",
    patient_key="peripheral_dominant",
    seed=42,
    amplitude_scale=45e-6,
    suppression_gain=2.5,
    max_suppression=0.95,
):
    quantized_signal, block_1, block_2_baseline, block_n = _prepare_case_signals(
        intensity=intensity,
        patient_key=patient_key,
        seed=seed,
    )

    feat_1 = extract_features(block_1)
    feat_2_baseline = extract_features(block_2_baseline)

    pain_class_1, pain_name_1 = predict_pain_state(clf, feat_1)
    env_bin_1 = bin_envelope(feat_1["envelope_mean"])
    state_1 = encode_state(pain_class_1, env_bin_1)

    stim_amp, stim_meta = map_control_to_amplitude(
        envelope_mean=feat_1["envelope_mean"],
        gain_multiplier=float(gain_multiplier),
        amplitude_scale=amplitude_scale,
    )

    effective_freq_hz = max(0.25, float(feat_1["dominant_frequency_hz"]) + float(freq_offset_hz))

    anti_wave = generate_antiphase_wave(
        freq_hz=effective_freq_hz,
        phase_rad=feat_1["phase_last_rad"],
        amplitude=stim_amp,
        block_n=block_n,
        phase_offset=float(phase_offset),
    )

    gate_wave = generate_gate_support(
        amplitude=stim_amp,
        block_n=block_n,
    )

    stim_wave = combine_stimulation(
        anti_wave,
        gate_wave,
        gate_weight=0.0,
    )

    patient_response = PATIENTS[patient_key]["resp"]

    block_2_controlled, plant_meta = apply_oscillation_suppression_to_block(
        baseline_block=block_2_baseline,
        stim_wave=stim_wave,
        current_mA=float(stim_meta["current_command_mA"]),
        dominant_freq_hz=feat_2_baseline["dominant_frequency_hz"],
        patient_response=patient_response,
        suppression_gain=suppression_gain,
        max_suppression=max_suppression,
    )

    feat_2_controlled = extract_features(block_2_controlled)

    pain_class_2, pain_name_2 = predict_pain_state(clf, feat_2_controlled)
    env_bin_2 = bin_envelope(feat_2_controlled["envelope_mean"])
    state_2 = encode_state(pain_class_2, env_bin_2)

    reward = compute_reward(
        prev_envelope=feat_2_baseline["envelope_mean"],
        next_envelope=feat_2_controlled["envelope_mean"],
        current_mA=float(stim_meta["current_command_mA"]),
        phase_offset=float(phase_offset),
    )

    signal_component = block_1
    noise_component = quantized_signal[:len(block_1)] - block_1[:len(block_1)]
    snr_db = compute_snr(signal_component, noise_component)

    results = build_results_dict(
        prev_feat=feat_2_baseline,
        next_feat=feat_2_controlled,
        current_command_mA=float(stim_meta["current_command_mA"]),
        reward=float(reward),
        snr_db=snr_db,
    )

    results.update({
        "intensity": intensity,
        "patient_key": patient_key,
        "predicted_pain_class_1": pain_name_1,
        "predicted_pain_class_2": pain_name_2,
        "state_1": int(state_1),
        "state_2": int(state_2),
        "gain_multiplier": float(gain_multiplier),
        "phase_offset": float(phase_offset),
        "frequency_offset_hz": float(freq_offset_hz),
        "effective_frequency_hz": float(effective_freq_hz),
        "effective_gate_weight": 0.0,
        "phase_mode": "static_blockwise",
        "phase_term": float(plant_meta["phase_term"]),
        "freq_term": float(plant_meta["freq_term"]),
        "amp_term": float(plant_meta["amp_term"]),
        "stim_rms": float(plant_meta["stim_rms"]),
        "osc_rms": float(plant_meta["osc_rms"]),
        "stim_freq_hz": float(plant_meta["stim_freq_hz"]),
        "freq_error_hz": float(plant_meta["freq_error_hz"]),
        "antiphase_match": float(plant_meta["antiphase_match"]),
        "beta_preclip": float(plant_meta["beta_preclip"]),
        "beta_applied": float(plant_meta["beta_applied"]),
    })
    return results


def _scout_gain_grid():
    return (0.75, 1.25, 2.00, 3.00)


def _scout_phase_grid():
    return tuple(np.linspace(-np.pi, np.pi, 9))


def _scout_freq_grid():
    return (-1.0, 0.0, 1.0)


def fast_scout_single_case_static(
    clf,
    intensity,
    patient_key,
    seed,
    amplitude_scale=45e-6,
    suppression_gain=2.5,
    max_suppression=0.95,
    objective="oscillation",
):
    best_row = None
    candidate_count = 0

    for gain_multiplier in _scout_gain_grid():
        for phase_offset in _scout_phase_grid():
            for freq_offset_hz in _scout_freq_grid():
                row = run_single_case_direct_params_static(
                    clf=clf,
                    gain_multiplier=gain_multiplier,
                    phase_offset=phase_offset,
                    freq_offset_hz=freq_offset_hz,
                    intensity=intensity,
                    patient_key=patient_key,
                    seed=seed,
                    amplitude_scale=amplitude_scale,
                    suppression_gain=suppression_gain,
                    max_suppression=max_suppression,
                )
                row["oracle_score"] = float(_compute_oracle_score(row, objective=objective))
                row["oracle_stage"] = "step23d_static_cap_sweep"
                candidate_count += 1

                if best_row is None or _is_better_than_baseline(row, best_row):
                    best_row = dict(row)

    best_row["oracle_search_num_candidates"] = int(candidate_count)
    best_row["benchmark_seed"] = int(seed)
    return best_row


def run_static_benchmark_for_cap(
    clf,
    amplitude_scale=45e-6,
    suppression_gain=2.5,
    max_suppression=0.95,
    base_seed=100,
    objective="oscillation",
    print_progress=True,
):
    rows = []
    seed_counter = base_seed
    case_idx = 0

    for intensity in INTENSITIES.keys():
        for patient_key in PATIENTS.keys():
            case_idx += 1

            if print_progress:
                print(
                    f"Cap {max_suppression:.2f} | case {case_idx}/9 | "
                    f"seed={seed_counter} | intensity={intensity} | patient={patient_key}"
                )

            best_row = fast_scout_single_case_static(
                clf=clf,
                intensity=intensity,
                patient_key=patient_key,
                seed=seed_counter,
                amplitude_scale=amplitude_scale,
                suppression_gain=suppression_gain,
                max_suppression=max_suppression,
                objective=objective,
            )
            rows.append(best_row)

            if print_progress:
                print(
                    f"  -> osc={best_row['oscillation_suppression_percent']:.4f}, "
                    f"pain={best_row['pain_proxy_reduction_percent']:.4f}, "
                    f"beta_preclip={best_row['beta_preclip']:.4f}, "
                    f"beta_applied={best_row['beta_applied']:.4f}, "
                    f"phase={best_row['phase_offset']:.4f}, "
                    f"freq={best_row['frequency_offset_hz']:.4f}, "
                    f"gain={best_row['gain_multiplier']:.4f}"
                )

            seed_counter += 20

    summary = _summarize_case_rows(rows)
    summary["suppression_gain"] = float(suppression_gain)
    summary["max_suppression"] = float(max_suppression)
    summary["mean_phase_term"] = float(np.mean([r["phase_term"] for r in rows]))
    summary["mean_amp_term"] = float(np.mean([r["amp_term"] for r in rows]))
    summary["mean_beta_preclip"] = float(np.mean([r["beta_preclip"] for r in rows]))
    summary["mean_beta_applied"] = float(np.mean([r["beta_applied"] for r in rows]))
    return rows, summary


def run_step23d_cap_sweep(
    clf,
    amplitude_scale=45e-6,
    suppression_gain=2.5,
    cap_values=(0.95, 0.96, 0.97, 0.98, 0.99),
    base_seed=100,
    objective="oscillation",
    print_progress=True,
):
    all_results = []

    for cap in cap_values:
        rows, summary = run_static_benchmark_for_cap(
            clf=clf,
            amplitude_scale=amplitude_scale,
            suppression_gain=suppression_gain,
            max_suppression=float(cap),
            base_seed=base_seed,
            objective=objective,
            print_progress=print_progress,
        )
        all_results.append({
            "cap": float(cap),
            "rows": rows,
            "summary": summary,
        })

    best = max(
        all_results,
        key=lambda x: (
            x["summary"]["mean_oscillation_suppression_percent"],
            x["summary"]["cases_ge_90"],
            x["summary"]["max_oscillation_suppression_percent"],
            x["summary"]["mean_reward"],
        ),
    )

    return all_results, best