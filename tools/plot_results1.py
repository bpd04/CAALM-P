import os
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# CAALM-P final benchmark plots
# ------------------------------------------------------------

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

baseline = np.array([
    88.10,
    89.60,
    88.00,
    89.60,
    88.40,
    88.70,
    87.60,
    89.20,
    89.90
])

mean_suppression = np.mean(suppression)

# Use a clean style
plt.style.use("default")

# =========================================================
# GRAPH 1: FINAL RESULTS
# =========================================================
fig1 = plt.figure(figsize=(10, 6))

plt.plot(
    cases,
    suppression,
    marker='o',
    linewidth=2.5,
    markersize=7,
    label='Optimized Suppression'
)

# 90% milestone line
plt.axhline(
    y=90,
    linestyle='--',
    linewidth=1.5,
    label='90% milestone'
)

# Mean suppression line
plt.axhline(
    y=mean_suppression,
    linestyle=':',
    linewidth=1.5,
    label=f'Mean = {mean_suppression:.2f}%'
)

plt.xlabel("Patient Case Index", fontsize=12)
plt.ylabel("Oscillation Suppression (%)", fontsize=12)
plt.title("CAALM-P Closed-Loop Pain Suppression Performance", fontsize=14, pad=12)

plt.xticks(cases)
plt.ylim(86, 92)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()

# Annotate each point
for x, y in zip(cases, suppression):
    plt.text(
        x,
        y + 0.08,
        f"{y:.2f}",
        ha='center',
        va='bottom',
        fontsize=9
    )

plt.tight_layout()
plt.savefig("outputs/caalm_results_plot.png", dpi=300)
plt.close(fig1)

# =========================================================
# GRAPH 2: BASELINE VS OPTIMIZED
# =========================================================
fig2 = plt.figure(figsize=(10, 6))

plt.plot(
    cases,
    baseline,
    marker='x',
    linestyle='--',
    linewidth=2,
    markersize=7,
    label='Baseline'
)

plt.plot(
    cases,
    suppression,
    marker='o',
    linewidth=2.5,
    markersize=7,
    label='Optimized (Step 23D)'
)

# 90% milestone line
plt.axhline(
    y=90,
    linestyle='--',
    linewidth=1.5,
    label='90% milestone'
)

plt.xlabel("Patient Case Index", fontsize=12)
plt.ylabel("Oscillation Suppression (%)", fontsize=12)
plt.title("Baseline vs Optimized Suppression", fontsize=14, pad=12)

plt.xticks(cases)
plt.ylim(86, 92)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()

# Annotate optimized values
for x, y in zip(cases, suppression):
    plt.text(
        x,
        y + 0.08,
        f"{y:.2f}",
        ha='center',
        va='bottom',
        fontsize=9
    )

plt.tight_layout()
plt.savefig("outputs/caalm_comparison_plot.png", dpi=300)
plt.show()

print("Saved:")
print(" - outputs/caalm_results_plot.png")
print(" - outputs/caalm_comparison_plot.png")