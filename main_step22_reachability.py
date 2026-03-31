# main_step22_reachability.py

from src.classifier import build_training_dataset, train_classifier
from src.experiment_runner import (
    run_reachability_sweep,
    summarize_reachability_results,
)

BEST_AMPLITUDE_SCALE = 45e-6
BEST_GATE_WEIGHT = 0.0

SUPPRESSION_GAIN_GRID = (1.3, 1.6, 2.0, 2.5)
MAX_SUPPRESSION_GRID = (0.4, 0.6, 0.8, 0.9, 0.95)


def main():
    # Train classifier once
    X, y = build_training_dataset(block_sec=0.5, blocks_per_run=6)
    clf = train_classifier(X, y)

    # Oracle reachability sweep
    sweep_rows, best_config = run_reachability_sweep(
        clf=clf,
        base_seed=100,
        amplitude_scale=BEST_AMPLITUDE_SCALE,
        gate_weight=BEST_GATE_WEIGHT,
        suppression_gain_grid=SUPPRESSION_GAIN_GRID,
        max_suppression_grid=MAX_SUPPRESSION_GRID,
        objective="oscillation",
    )

    ordered = summarize_reachability_results(sweep_rows)

    print("STEP 22A ORACLE REACHABILITY SWEEP\n")

    print("Top reachability configurations:")
    for i, row in enumerate(ordered[:10], start=1):
        print(
            f"{i}. "
            f"gain={row['suppression_gain']:.2f}, "
            f"max_sup={row['max_suppression']:.2f}, "
            f"mean_osc={row['mean_oscillation_suppression_percent']:.4f}, "
            f"mean_pain={row['mean_pain_proxy_reduction_percent']:.4f}, "
            f"mean_reward={row['mean_reward']:.4f}, "
            f"cases>=90={row['cases_ge_90']}/9, "
            f"max_case={row['max_oscillation_suppression_percent']:.4f}, "
            f"min_case={row['min_oscillation_suppression_percent']:.4f}"
        )

    print("\nBest configuration found:")
    print(best_config)

    print("\nDecision:")
    if best_config["mean_oscillation_suppression_percent"] >= 90.0:
        print("Mean 90% suppression is reachable under the current plant/action sweep.")
    elif best_config["cases_ge_90"] > 0:
        print("90% suppression is reachable in some cases, but not yet as a robust mean.")
    else:
        print("90% suppression is not reachable under the current plant/action sweep.")


if __name__ == "__main__":
    main()