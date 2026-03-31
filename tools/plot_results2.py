import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("outputs", exist_ok=True)

# === FINAL RESULTS FROM STEP 23D (BEST CAP = 0.99) ===
cases = np.arange(1, 10)

suppression = np.array([
    89.42,
    90.78,
    88.73,
    90.24,
    89.18,
    89.46,
    88.82,
    90.07,
    90.93
])

# =========================================================
# GRAPH 1: FINAL RESULTS
# =========================================================
plt.figure(figsize=(10, 6))

plt.plot(cases, suppression, marker='o', linewidth=2)

plt.axhline(y=90, linestyle='--')

plt.xlabel("Patient Case Index")
plt.ylabel("Oscillation Suppression (%)")
plt.title("CAALM-P Closed-Loop Pain Suppression Performance")

plt.grid(True)

for x, y in zip(cases, suppression):
    plt.text(x, y + 0.2, f"{y:.1f}", ha='center', fontsize=9)

plt.savefig("outputs/caalm_results_plot.png", dpi=300)
plt.close()

# =========================================================
# GRAPH 2: BASELINE VS OPTIMIZED
# =========================================================
baseline = np.array([88.1, 89.6, 88.0, 89.6, 88.4, 88.7, 87.6, 89.2, 89.9])

plt.figure(figsize=(10, 6))

plt.plot(cases, baseline, marker='x', linestyle='--', label='Baseline')
plt.plot(cases, suppression, marker='o', label='Optimized (Step 23D)')

plt.axhline(y=90, linestyle='--')

plt.xlabel("Patient Case Index")
plt.ylabel("Oscillation Suppression (%)")
plt.title("Baseline vs Optimized Suppression")

plt.legend()
plt.grid(True)

plt.savefig("outputs/caalm_comparison_plot.png", dpi=300)
plt.show()