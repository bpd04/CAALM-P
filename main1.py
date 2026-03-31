from src.classifier import build_training_dataset, train_classifier
from src.experiment_runner import run_single_case, run_all_cases

# -----------------------------
# Train classifier first
# -----------------------------
X, y = build_training_dataset(block_sec=0.5, blocks_per_run=6)
clf = train_classifier(X, y)

# -----------------------------
# Run one single case
# -----------------------------
single_result = run_single_case(
    clf=clf,
    intensity="medium",
    patient_key="peripheral_dominant",
    seed=42
)

print("Single-case result:")
for k, v in single_result.items():
    print(f"{k}: {v}")

# -----------------------------
# Run all 9 cases
# -----------------------------
all_results = run_all_cases(clf, base_seed=100)

print("\nRan all cases successfully.")
print("Total number of cases:", len(all_results))

print("\nFirst 3 results preview:")
for i, result in enumerate(all_results[:3]):
    print(f"\nCase {i+1}")
    for k, v in result.items():
        print(f"{k}: {v}")