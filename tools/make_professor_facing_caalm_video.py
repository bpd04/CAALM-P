import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# ------------------------------------------------------------
# CAALM-P professor-facing representative animation
# Save path:
#   CAALM-P/outputs/animations/caalm_professor_demo.gif
# Run from repo root using:
#   python tools/make_professor_facing_caalm_video.py
# ------------------------------------------------------------

# Build output path relative to the repo root
OUTPUT_DIR = os.path.join("outputs", "animations")
OUTPUT_GIF = os.path.join(OUTPUT_DIR, "caalm_professor_demo.gif")

# Representative cases based on validated project range
CASES = [
    {"name": "Case A", "profile": "Peripheral / Medium", "target_suppr": 88.74, "base_freq": 6.0, "amp": 1.00},
    {"name": "Case B", "profile": "Mixed / Medium",      "target_suppr": 89.32, "base_freq": 7.0, "amp": 0.95},
    {"name": "Case C", "profile": "Central / Medium",    "target_suppr": 89.74, "base_freq": 8.0, "amp": 1.05},
    {"name": "Case D", "profile": "Peripheral / High",   "target_suppr": 90.12, "base_freq": 9.0, "amp": 1.10},
    {"name": "Case E", "profile": "Central / High",      "target_suppr": 90.93, "base_freq": 10.0, "amp": 1.15},
]

FPS = 8
SECONDS_PER_CASE = 2
FRAMES_PER_CASE = FPS * SECONDS_PER_CASE
TOTAL_FRAMES = FRAMES_PER_CASE * len(CASES)

FS = 120.0
WINDOW_SEC = 1.8
N_WINDOW = int(WINDOW_SEC * FS)
T = np.arange(N_WINDOW) / FS


def build_case_signals(case, progress):
    f = case["base_freq"]
    amp = case["amp"]

    envelope = 0.90 + 0.14 * np.sin(2 * np.pi * 0.22 * T + 0.6)

    baseline = amp * envelope * (
        0.82 * np.sin(2 * np.pi * f * T + 0.8)
        + 0.13 * np.sin(2 * np.pi * (f * 1.8) * T + 1.3)
    )

    target = case["target_suppr"] / 100.0
    ramp = target * (1 - np.exp(-3.4 * progress)) / (1 - np.exp(-3.4))
    ramp = np.clip(ramp, 0, target)

    controlled = ((1 - ramp) * baseline) + 0.04 * np.sin(2 * np.pi * 1.3 * T + 0.2)

    return baseline, controlled, 100.0 * ramp


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig = plt.figure(figsize=(9, 5.4))
    gs = fig.add_gridspec(
        2, 2,
        width_ratios=[2.1, 1.0],
        height_ratios=[1.0, 0.55],
        hspace=0.30,
        wspace=0.25,
    )

    ax_sig = fig.add_subplot(gs[:, 0])
    ax_sup = fig.add_subplot(gs[0, 1])
    ax_text = fig.add_subplot(gs[1, 1])

    baseline_line, = ax_sig.plot([], [], lw=1.4, label="Incoming pain-related oscillation")
    controlled_line, = ax_sig.plot([], [], lw=2.0, label="Closed-loop modulated signal")

    ax_sig.set_xlim(0, WINDOW_SEC)
    ax_sig.set_ylim(-1.6, 1.6)
    ax_sig.set_xlabel("Time (s)")
    ax_sig.set_ylabel("Amplitude (a.u.)")
    ax_sig.set_title("Representative oscillatory pain signal modulation")
    ax_sig.legend(loc="upper right", fontsize=8)

    sup_line, = ax_sup.plot([], [], lw=2.2)
    ax_sup.axhline(90.0, linestyle="--", linewidth=1.0)
    ax_sup.set_xlim(0, SECONDS_PER_CASE)
    ax_sup.set_ylim(0, 100)
    ax_sup.set_xlabel("Progress (s)")
    ax_sup.set_ylabel("Suppression (%)")
    ax_sup.set_title("Suppression trajectory")

    ax_text.axis("off")

    fig.suptitle(
        "CAALM-P | Closed-loop noninvasive pain-suppression simulation",
        fontsize=14,
        y=0.98,
    )

    ax_text.text(
        0.00,
        0.95,
        "Representative visualization based on validated range:\n"
        "mean ≈ 89.74%, best case ≈ 90.93%, 4/9 cases ≥ 90%",
        fontsize=10,
        va="top",
    )

    case_text = ax_text.text(0.00, 0.52, "", fontsize=11, va="top")
    metrics_text = ax_text.text(0.00, 0.20, "", fontsize=10, va="top")

    def init():
        baseline_line.set_data([], [])
        controlled_line.set_data([], [])
        sup_line.set_data([], [])
        case_text.set_text("")
        metrics_text.set_text("")
        return baseline_line, controlled_line, sup_line, case_text, metrics_text

    def update(frame):
        case_idx = min(frame // FRAMES_PER_CASE, len(CASES) - 1)
        frame_in_case = frame % FRAMES_PER_CASE
        progress = frame_in_case / max(1, FRAMES_PER_CASE - 1)

        case = CASES[case_idx]
        baseline, controlled, suppr = build_case_signals(case, progress)

        baseline_line.set_data(T, baseline)
        controlled_line.set_data(T, controlled)

        local_x = np.linspace(0, SECONDS_PER_CASE, frame_in_case + 1)
        local_y = []
        for i in range(frame_in_case + 1):
            prog_i = i / max(1, FRAMES_PER_CASE - 1)
            _, _, s = build_case_signals(case, prog_i)
            local_y.append(s)

        sup_line.set_data(local_x, local_y)

        case_text.set_text(f"{case['name']} | {case['profile']}")
        metrics_text.set_text(
            f"Target case suppression: {case['target_suppr']:.2f}%\n"
            f"Animated suppression: {suppr:.2f}%"
        )

        return baseline_line, controlled_line, sup_line, case_text, metrics_text

    ani = FuncAnimation(
        fig,
        update,
        frames=TOTAL_FRAMES,
        init_func=init,
        interval=1000 / FPS,
        blit=False,
    )

    ani.save(OUTPUT_GIF, writer=PillowWriter(fps=FPS))
    plt.close(fig)

    print(f"Saved animation to: {OUTPUT_GIF}")


if __name__ == "__main__":
    main()