# src/config.py

# -----------------------------
# Sampling and simulation setup
# -----------------------------
FS = 10_000                 # Sampling rate in Hz
DURATION = 60.0             # Total simulation duration in seconds
BLOCK_SEC = 0.05            # Closed-loop update every 50 ms
BLOCK_N = int(FS * BLOCK_SEC)

# -----------------------------
# Pain intensities
# -----------------------------
INTENSITIES = {
    "low": 0.70,
    "medium": 1.00,
    "high": 1.35,
}

# -----------------------------
# Virtual patient profiles
# Each profile controls how strong:
# - oscillations are
# - burst activity is
# - central sensitization is
# - stimulation response is
# -----------------------------
PATIENTS = {
    "peripheral_dominant": {
        "osc": 1.20,
        "bursts": 0.80,
        "central": 0.70,
        "resp": 1.00,
    },
    "mixed": {
        "osc": 1.00,
        "bursts": 1.00,
        "central": 1.00,
        "resp": 0.85,
    },
    "central_sensitized": {
        "osc": 0.80,
        "bursts": 1.10,
        "central": 1.40,
        "resp": 0.65,
    },
}

# -----------------------------
# Signal model parameters
# -----------------------------
OSC_FREQ_MIN = 8.0
OSC_FREQ_MAX = 12.0

# Approximate microvolt-scale signal model
NOCICEPTIVE_BASE_UV = 15e-6
OSC_BASE_UV = 45e-6
BURST_BASE_UV = 30e-6

# -----------------------------
# Electrode / acquisition model
# -----------------------------
MOTION_ARTIFACT_UV = 8e-6
MAINS_INTERFERENCE_UV = 3e-6
MAINS_FREQ = 50.0

# -----------------------------
# Amplifier + ADC model
# -----------------------------
AMP_GAIN = 5000
AMP_WHITE_NOISE_UV = 1.8e-6
AMP_FLICKER_NOISE_UV = 0.8e-6
AMP_CLIP_VOLT = 2.5

ADC_BITS = 12
ADC_VREF = 2.5

# -----------------------------
# Filtering
# -----------------------------
NOTCH_FREQ = 50.0
NOTCH_Q = 30.0
BP_LOW = 6.0
BP_HIGH = 20.0

# -----------------------------
# Stimulation / safety model
# -----------------------------
MIN_CURRENT_MA = 0.2
MAX_CURRENT_MA = 4.0
GATE_SUPPORT_FREQ = 100.0
GATE_SUPPORT_WEIGHT = 0.15

# -----------------------------
# RL controller settings
# -----------------------------
ALPHA = 0.18       # learning rate
GAMMA = 0.90       # discount factor
EPSILON = 0.15     # exploration probability

# Actions = (gain_multiplier, phase_offset)
# phase offset is small correction around anti-phase
ACTIONS = [
    (0.5, 0.0),
    (0.8, 0.0),
    (1.1, 0.0),
    (0.8, 0.15 * 3.141592653589793),
    (0.8, -0.15 * 3.141592653589793),
    (1.3, 0.0),
]