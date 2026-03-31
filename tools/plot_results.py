import matplotlib.pyplot as plt
import numpy as np

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

# === PLOT ===
plt.figure(figsize=(10, 6))

plt.plot(cases, suppression, marker='o', linewidth=2)

# 90% threshold line
plt.axhline(y=90, linestyle='--')

# Labels
plt.xlabel("Patient Case Index")
plt.ylabel("Oscillation Suppression (%)")
plt.title("CAALM-P Closed-Loop Pain Suppression Performance")

# Grid
plt.grid(True)

# Annotate points
for x, y in zip(cases, suppression):
    plt.text(x, y + 0.2, f"{y:.1f}", ha='center', fontsize=9)

# Save
output_path = "outputs/caalm_results_plot.png"
plt.savefig(output_path, dpi=300)

print(f"Graph saved at: {output_path}")

plt.savefig("outputs/caalm_results_plot.png", dpi=300)
plt.close()