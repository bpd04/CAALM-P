# src/classifier.py

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from src.config import FS, INTENSITIES, PATIENTS
from src.signal_generator import generate_pain_signal
from src.electrode_model import apply_electrode_model
from src.amplifier_adc import apply_amplifier, adc_quantize
from src.preprocessing import preprocess_signal
from src.features import extract_features


LABEL_MAP = {
    "low": 0,
    "medium": 1,
    "high": 2,
}

LABEL_NAMES = {
    0: "low",
    1: "medium",
    2: "high",
}


def feature_dict_to_vector(feature_dict):
    """
    Convert feature dictionary into fixed-order numeric vector.
    """
    return np.array([
        feature_dict["dominant_frequency_hz"],
        feature_dict["phase_last_rad"],
        feature_dict["envelope_mean"],
        feature_dict["envelope_max"],
        feature_dict["rms"],
        feature_dict["band_power"],
        feature_dict["spectral_entropy"],
        feature_dict["burst_rate_proxy"],
    ], dtype=float)


def build_training_dataset(block_sec=0.5, blocks_per_run=6):
    """
    Build a synthetic training dataset using all pain intensities
    and all patient profiles.

    Returns:
        X : feature matrix
        y : label vector
    """
    X = []
    y = []

    block_n = int(block_sec * FS)

    seed_counter = 100

    for intensity_name in ["low", "medium", "high"]:
        for patient_key in PATIENTS.keys():
            # Generate one synthetic run
            t, raw_signal, _ = generate_pain_signal(
                intensity=intensity_name,
                patient_key=patient_key,
                seed=seed_counter
            )

            # Full acquisition chain
            electrode_signal, _ = apply_electrode_model(
                raw_signal=raw_signal,
                t=t,
                seed=seed_counter + 1
            )

            amplified_signal, _ = apply_amplifier(
                electrode_signal=electrode_signal,
                seed=seed_counter + 2
            )

            quantized_signal, _ = adc_quantize(amplified_signal)
            filtered_signal, _ = preprocess_signal(quantized_signal)

            # Split into blocks and extract features
            max_blocks = min(blocks_per_run, len(filtered_signal) // block_n)

            for i in range(max_blocks):
                start = i * block_n
                end = start + block_n
                block = filtered_signal[start:end]

                feature_dict = extract_features(block)
                x_vec = feature_dict_to_vector(feature_dict)

                X.append(x_vec)
                y.append(LABEL_MAP[intensity_name])

            seed_counter += 10

    X = np.array(X)
    y = np.array(y)

    return X, y


def train_classifier(X, y, random_state=42):
    """
    Train Random Forest classifier.
    """
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=6,
        random_state=random_state
    )
    clf.fit(X, y)
    return clf


def evaluate_classifier(clf, X, y):
    """
    Evaluate classifier on provided data.
    """
    y_pred = clf.predict(X)
    acc = accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred)
    return acc, cm


def predict_pain_state(clf, feature_dict):
    """
    Predict pain state from a feature dictionary.
    Returns numeric class and label name.
    """
    x_vec = feature_dict_to_vector(feature_dict).reshape(1, -1)
    pred = int(clf.predict(x_vec)[0])
    return pred, LABEL_NAMES[pred]