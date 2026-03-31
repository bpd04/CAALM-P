# main.py

import time

from src.classifier import build_training_dataset, train_classifier
from src.experiment_runner import run_step23d_cap_sweep

BEST_AMPLITUDE_SCALE = 45e-6
BEST_SUPPRESSION_GAIN = 2.5

ARCHIVE_BASELINE = {
    "mean_oscillation_suppression_percent": 88.8368033463615,
    "mean_pain_proxy_reduction_percent": 57.07550652070194,
    "mean_reward": 4.1370007021167385,
    "best_single_case": 89.91333737384944,
    "worst_single_case": 87.66599509311243,
}

CAP_VALUES = (0.95, 0.96, 0.97, 0.98, 0.99)


def main():
    print("STEP 23D HARD SUPPRESSION CAP SWEEP")
    print("Training classifier...\n")

    t0 = time.time()

    X, y = build_training_dataset(block_sec=0.5, blocks_per_run=6)
    clf = train_classifier(X, y)

    print("Running Step 22B static scout while sweeping only max_suppression...\n")
    print(f"suppression_gain = {BEST_SUPPRESSION_GAIN}")
    print(f"cap_values = {CAP_VALUES}")
    print("waveform = static blockwise")
    print("gate_weight fixed at 0.0")
    print("plant law = recovered old-law instrumentation\n")

    all_results, best = run_step23d_cap_sweep(
        clf=clf,
        amplitude_scale=BEST_AMPLITUDE_SCALE,
        suppression_gain=BEST_SUPPRESSION_GAIN,
        cap_values=CAP_VALUES,
        base_seed=100,
        objective="oscillation",
        print_progress=True,
    )

    elapsed = time.time() - t0

    print("\nSTEP 23D CAP SWEEP SUMMARY:\n")
    for item in all_results:
        cap = item["cap"]
        s = item["summary"]
        print(f"Cap = {cap:.2f}")
        print("  Mean oscillation suppression (%):", s["mean_oscillation_suppression_percent"])
        print("  Mean pain proxy reduction (%):", s["mean_pain_proxy_reduction_percent"])
        print("  Mean reward:", s["mean_reward"])
        print("  Positive cases:", s["positive_cases"], "/ 9")
        print("  Cases >= 85% suppression:", s["cases_ge_85"], "/ 9")
        print("  Cases >= 90% suppression:", s["cases_ge_90"], "/ 9")
        print("  Best single-case suppression (%):", s["max_oscillation_suppression_percent"])
        print("  Worst single-case suppression (%):", s["min_oscillation_suppression_percent"])
        print("  Mean beta_preclip:", s["mean_beta_preclip"])
        print("  Mean beta_applied:", s["mean_beta_applied"])
        print("  Delta mean suppression vs archived baseline:",
              s["mean_oscillation_suppression_percent"] - ARCHIVE_BASELINE["mean_oscillation_suppression_percent"])
        print()

    best_cap = best["cap"]
    best_summary = best["summary"]

    print("BEST CAP FOUND:\n")
    print("Best cap:", best_cap)
    print("Mean oscillation suppression (%):", best_summary["mean_oscillation_suppression_percent"])
    print("Mean pain proxy reduction (%):", best_summary["mean_pain_proxy_reduction_percent"])
    print("Mean reward:", best_summary["mean_reward"])
    print("Cases >= 90% suppression:", best_summary["cases_ge_90"], "/ 9")
    print("Best single-case suppression (%):", best_summary["max_oscillation_suppression_percent"])
    print("Worst single-case suppression (%):", best_summary["min_oscillation_suppression_percent"])
    print("Mean beta_preclip:", best_summary["mean_beta_preclip"])
    print("Mean beta_applied:", best_summary["mean_beta_applied"])

    print("\nDecision:")
    if best_summary["mean_oscillation_suppression_percent"] >= 90.0:
        print("Success: raising the hard cap is sufficient to reach mean 90% suppression.")
        print("Next step: freeze this cap and validate robustness across additional seeds.")
    elif best_summary["cases_ge_90"] > 0:
        print("Partial success: raising the cap produces one or more >=90% cases.")
        print("Next step: validate robustness and then inspect whether antiphase_match is the next limiter.")
    elif best_summary["mean_oscillation_suppression_percent"] > ARCHIVE_BASELINE["mean_oscillation_suppression_percent"]:
        print("The cap sweep improved the ceiling, but 90% is still not reached.")
        print("Next step: keep the better cap and then tune one internal factor at a time.")
    else:
        print("Raising the cap does not materially improve the ceiling.")
        print("Next step: antiphase_match / correlation structure is likely the next true bottleneck.")

    print(f"\nElapsed time: {elapsed / 60.0:.2f} minutes")


if __name__ == "__main__":
    main()