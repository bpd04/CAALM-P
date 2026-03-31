import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ============================================================
# CAALM-P System Architecture Diagram Generator
# Output: docs/architecture.png
# ============================================================

os.makedirs("docs", exist_ok=True)

# ------------------------------------------------------------
# Figure setup
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(34, 18))
ax.set_xlim(0, 36)
ax.set_ylim(0, 18)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ------------------------------------------------------------
# Color palette
# ------------------------------------------------------------
COLOR_BIO = "#E67E22"          # orange
COLOR_ACQ = "#3498DB"          # blue
COLOR_FEAT = "#8E44AD"         # purple
COLOR_CLASS = "#C0392B"        # red
COLOR_CTRL = "#16A085"         # teal
COLOR_SAFETY = "#F1C40F"       # yellow
COLOR_WAVE = "#D35400"         # deep orange
COLOR_PLANT = "#27AE60"        # green
COLOR_METRICS = "#2C3E50"      # dark slate
COLOR_NOTE = "#F8F9F9"         # near-white
COLOR_NOTE_EDGE = "#7F8C8D"

FORWARD_ARROW = "#111111"
INTERNAL_ARROW = "#666666"
FEEDBACK_ARROW = "#C0392B"

TEXT_WHITE = "white"
TEXT_BLACK = "#1b1b1b"

TITLE_FONT = 24
SUBTITLE_FONT = 15
MAIN_FONT = 11
SUB_FONT = 10
CONTAINER_TITLE_FONT = 12
NOTE_TITLE_FONT = 11
NOTE_TEXT_FONT = 10
LEGEND_FONT = 10


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def draw_box(x, y, w, h, text, fc, ec="#1f1f1f", lw=1.6,
             fontsize=10, fontweight="bold", text_color="white",
             rounded=0.05, z=3):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rounded}",
        linewidth=lw,
        edgecolor=ec,
        facecolor=fc,
        zorder=z
    )
    ax.add_patch(rect)

    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=fontweight,
        color=text_color,
        family="DejaVu Sans",
        wrap=True,
        zorder=z + 1
    )


def draw_container(x, y, w, h, title, fill_color):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.05",
        linewidth=2.2,
        edgecolor="#7F8C8D",
        facecolor=fill_color,
        zorder=1
    )
    ax.add_patch(rect)

    ax.text(
        x + w / 2,
        y + h - 0.28,
        title,
        ha="center",
        va="top",
        fontsize=CONTAINER_TITLE_FONT,
        fontweight="bold",
        color=TEXT_BLACK,
        family="DejaVu Sans",
        zorder=4
    )


def draw_note_box(x, y, w, h, title, body):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.05",
        linewidth=1.8,
        edgecolor=COLOR_NOTE_EDGE,
        facecolor=COLOR_NOTE,
        zorder=1
    )
    ax.add_patch(rect)

    ax.text(
        x + 0.20, y + h - 0.30,
        title,
        ha="left", va="top",
        fontsize=NOTE_TITLE_FONT,
        fontweight="bold",
        color=TEXT_BLACK,
        family="DejaVu Sans",
        zorder=3
    )

    ax.text(
        x + 0.20, y + h - 0.75,
        body,
        ha="left", va="top",
        fontsize=NOTE_TEXT_FONT,
        color="#333333",
        family="DejaVu Sans",
        zorder=3,
        linespacing=1.35
    )


def draw_forward_arrow(x1, y1, x2, y2, label=None, label_y_offset=0.35):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=2.4,
            color=FORWARD_ARROW,
            shrinkA=0,
            shrinkB=0
        ),
        zorder=5
    )
    if label:
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + label_y_offset,
            label,
            fontsize=9,
            color="#444444",
            style="italic",
            ha="center",
            family="DejaVu Sans",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=0.25),
            zorder=6
        )


def draw_internal_arrow(x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.7,
            color=INTERNAL_ARROW,
            shrinkA=0,
            shrinkB=0
        ),
        zorder=5
    )


def draw_feedback_arrow(x1, y1, x2, y2, rad, label, tx, ty):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=2.1,
            color=FEEDBACK_ARROW,
            linestyle="--",
            connectionstyle=f"arc3,rad={rad}"
        ),
        zorder=2
    )

    ax.text(
        tx,
        ty,
        label,
        fontsize=9,
        color=FEEDBACK_ARROW,
        style="italic",
        ha="center",
        family="DejaVu Sans",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.92, pad=0.25),
        zorder=6
    )


# ------------------------------------------------------------
# Layout
# ------------------------------------------------------------
main_y = 12.0
main_h = 1.70

bio_w = 3.1
feat_w = 3.0
clf_w = 3.1
safety_w = 2.6
wave_w = 3.0
metrics_w = 3.1

acq_w = 3.6
ctrl_w = 4.0
plant_w = 4.1

bio_x = 0.6
acq_x = 4.2
feat_x = 8.7
clf_x = 12.3
ctrl_x = 16.2
safety_x = 20.9
wave_x = 24.0
plant_x = 27.7
metrics_x = 32.2

container_y = 7.2
container_h = 6.2

# ------------------------------------------------------------
# Title
# ------------------------------------------------------------
ax.text(
    18, 17.35,
    "CAALM-P System Architecture",
    ha="center",
    va="center",
    fontsize=TITLE_FONT,
    fontweight="bold",
    family="DejaVu Sans",
    color=TEXT_BLACK
)

ax.text(
    18, 16.78,
    "Closed-Loop Non-Invasive Pain Suppression Simulator",
    ha="center",
    va="center",
    fontsize=SUBTITLE_FONT,
    family="DejaVu Sans",
    color="#444444"
)

# ------------------------------------------------------------
# Main pipeline blocks
# ------------------------------------------------------------
draw_box(
    bio_x, main_y, bio_w, main_h,
    "Biological Pain Signal\nSynthetic Neural Oscillations",
    COLOR_BIO, text_color=TEXT_WHITE, fontsize=MAIN_FONT
)

draw_container(acq_x, container_y, acq_w, container_h, "Acquisition Chain", "#EBF5FB")
sub_x = acq_x + 0.35
sub_w = acq_w - 0.70
sub_h = 1.10
draw_box(sub_x, 11.35, sub_w, sub_h, "Electrode Pickup", COLOR_ACQ, fontsize=SUB_FONT)
draw_box(sub_x, 9.80, sub_w, sub_h, "Amplifier + ADC", COLOR_ACQ, fontsize=SUB_FONT)
draw_box(sub_x, 8.25, sub_w, sub_h, "Preprocessing\nBandpass + Smoothing", COLOR_ACQ, fontsize=SUB_FONT)
draw_internal_arrow(acq_x + acq_w/2, 11.35, acq_x + acq_w/2, 10.90)
draw_internal_arrow(acq_x + acq_w/2, 9.80, acq_x + acq_w/2, 9.35)

draw_box(
    feat_x, main_y, feat_w, main_h,
    "Feature Extraction\nFFT / STFT\nHilbert Envelope & Phase",
    COLOR_FEAT, text_color=TEXT_WHITE, fontsize=MAIN_FONT
)

draw_box(
    clf_x, main_y, clf_w, main_h,
    "Pain State Classifier\nSupervised Model\nLow / Medium / High",
    COLOR_CLASS, text_color=TEXT_WHITE, fontsize=MAIN_FONT
)

draw_container(ctrl_x, container_y, ctrl_w, container_h, "Hybrid Controller", "#E8F8F5")
ctrl_sub_x = ctrl_x + 0.35
ctrl_sub_w = ctrl_w - 0.70
draw_box(ctrl_sub_x, 11.35, ctrl_sub_w, sub_h, "Rule-Based Controller", COLOR_CTRL, fontsize=SUB_FONT)
draw_box(ctrl_sub_x, 9.80, ctrl_sub_w, sub_h, "Q-Learning RL Agent", COLOR_CTRL, fontsize=SUB_FONT)
draw_box(ctrl_sub_x, 8.25, ctrl_sub_w, sub_h, "State-Wise Hybrid Policy", COLOR_CTRL, fontsize=SUB_FONT)
draw_internal_arrow(ctrl_x + ctrl_w/2, 11.35, ctrl_x + ctrl_w/2, 10.90)
draw_internal_arrow(ctrl_x + ctrl_w/2, 9.80, ctrl_x + ctrl_w/2, 9.35)

draw_box(
    safety_x, main_y, safety_w, main_h,
    "Safety Layer\nAmplitude / Frequency Bounds",
    COLOR_SAFETY, text_color="#1b1b1b", fontsize=MAIN_FONT
)

draw_box(
    wave_x, main_y, wave_w, main_h,
    "Waveform Generator\nAnti-Phase Stimulation",
    COLOR_WAVE, text_color=TEXT_WHITE, fontsize=MAIN_FONT
)

draw_container(plant_x, container_y, plant_w, container_h, "Plant Model", "#EAFAF1")
plant_sub_x = plant_x + 0.35
plant_sub_w = plant_w - 0.70
draw_box(plant_sub_x, 11.35, plant_sub_w, sub_h, "Oscillation Isolation", COLOR_PLANT, fontsize=SUB_FONT)
draw_box(plant_sub_x, 9.80, plant_sub_w, sub_h, "Antiphase Suppression Law", COLOR_PLANT, fontsize=SUB_FONT)
draw_box(plant_sub_x, 8.25, plant_sub_w, sub_h, "Suppression Cap", COLOR_PLANT, fontsize=SUB_FONT)
draw_internal_arrow(plant_x + plant_w/2, 11.35, plant_x + plant_w/2, 10.90)
draw_internal_arrow(plant_x + plant_w/2, 9.80, plant_x + plant_w/2, 9.35)

draw_box(
    metrics_x, main_y, metrics_w, main_h,
    "Metrics & Validation\nSuppression % • Reward\nPain Proxy • Multi-Seed",
    COLOR_METRICS, text_color=TEXT_WHITE, fontsize=MAIN_FONT
)

# ------------------------------------------------------------
# Forward arrows
# ------------------------------------------------------------
y_arrow = main_y + main_h / 2
draw_forward_arrow(bio_x + bio_w, y_arrow, acq_x, y_arrow)
draw_forward_arrow(acq_x + acq_w, y_arrow, feat_x, y_arrow)
draw_forward_arrow(feat_x + feat_w, y_arrow, clf_x, y_arrow)
draw_forward_arrow(clf_x + clf_w, y_arrow, ctrl_x, y_arrow)
draw_forward_arrow(ctrl_x + ctrl_w, y_arrow, safety_x, y_arrow)
draw_forward_arrow(safety_x + safety_w, y_arrow, wave_x, y_arrow)
draw_forward_arrow(wave_x + wave_w, y_arrow, plant_x, y_arrow)
draw_forward_arrow(plant_x + plant_w, y_arrow, metrics_x, y_arrow)

# Small clean connection labels
ax.text(22.2, 13.95, "Safe Control Action", fontsize=9, style="italic",
        color="#444444", family="DejaVu Sans", ha="center")
ax.text(26.0, 13.95, "Anti-Phase Waveform", fontsize=9, style="italic",
        color="#444444", family="DejaVu Sans", ha="center")
ax.text(31.0, 13.95, "Suppressed Signal", fontsize=9, style="italic",
        color="#444444", family="DejaVu Sans", ha="center")

# ------------------------------------------------------------
# Feedback arrows
# ------------------------------------------------------------
draw_feedback_arrow(
    metrics_x + 0.30, 10.15,
    ctrl_x + 2.0, 10.15,
    rad=-0.42,
    label="Reward Feedback",
    tx=24.2,
    ty=9.7
)

draw_feedback_arrow(
    plant_x + 0.95, 7.40,
    bio_x + 0.75, 7.40,
    rad=-0.05,
    label="Next Time-Step State",
    tx=15.3,
    ty=6.82
)

# ------------------------------------------------------------
# Bottom technical formalism panels
# ------------------------------------------------------------
note_y = 1.0
note_h = 4.2
note_w = 8.0

draw_note_box(
    0.8, note_y, note_w, note_h,
    "Signal & Control Formalism",
    "Signal model:\n"
    "x(t) = A sin(ωt + φ) + n(t)\n\n"
    "Anti-phase control:\n"
    "u(t) = -kA sin(ωt + φ + Δφ)\n\n"
    "Objective:\n"
    "Suppress pathological oscillatory component"
)

draw_note_box(
    9.5, note_y, note_w, note_h,
    "Feature Extraction & Classification",
    "Feature extraction:\n"
    "• FFT / STFT → dominant frequency\n"
    "• Hilbert transform → envelope, phase\n\n"
    "Classifier:\n"
    "Supervised pain-state mapping\n"
    "Low / Medium / High"
)

draw_note_box(
    18.2, note_y, note_w, note_h,
    "RL Formulation",
    "State definition:\n"
    "S = {frequency, amplitude, phase, pain_level}\n\n"
    "Action space:\n"
    "A = {stim_amplitude, phase_shift}\n\n"
    "Reward:\n"
    "R = - suppression_error - energy_penalty"
)

draw_note_box(
    26.9, note_y, 8.0, note_h,
    "Real-Time & Plant Assumptions",
    "Sampling frequency: e.g. 1 kHz+\n"
    "Control update: blockwise closed loop\n"
    "Latency budget: bounded sensing → actuation\n\n"
    "Plant assumptions:\n"
    "• LTI approximation\n"
    "• Additive Gaussian noise\n"
    "• Safety bounds on amplitude / frequency"
)

# ------------------------------------------------------------
# Legend
# ------------------------------------------------------------
legend_x = 29.3
legend_y = 0.15

ax.text(
    legend_x, legend_y + 2.35,
    "Legend",
    fontsize=11,
    fontweight="bold",
    family="DejaVu Sans",
    color=TEXT_BLACK
)

draw_box(legend_x, legend_y + 1.60, 0.72, 0.44, "", COLOR_BIO, fontsize=1)
ax.text(legend_x + 0.95, legend_y + 1.82, "Main Pipeline Block",
        fontsize=LEGEND_FONT, va="center", family="DejaVu Sans")

draw_container(legend_x, legend_y + 0.95, 0.72, 0.44, "", "#EBF5FB")
ax.text(legend_x + 0.95, legend_y + 1.17, "Container Group",
        fontsize=LEGEND_FONT, va="center", family="DejaVu Sans")

draw_box(legend_x, legend_y + 0.30, 0.72, 0.44, "", COLOR_CTRL, fontsize=1)
ax.text(legend_x + 0.95, legend_y + 0.52, "Sub-Component",
        fontsize=LEGEND_FONT, va="center", family="DejaVu Sans")

ax.annotate(
    "", xy=(legend_x + 0.72, legend_y - 0.08), xytext=(legend_x, legend_y - 0.08),
    arrowprops=dict(arrowstyle="->", linewidth=2.1, color=FEEDBACK_ARROW, linestyle="--")
)
ax.text(legend_x + 0.95, legend_y - 0.08, "Feedback Path",
        fontsize=LEGEND_FONT, va="center", family="DejaVu Sans")

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------
plt.savefig("docs/architecture.png", dpi=260, bbox_inches="tight")
plt.show()