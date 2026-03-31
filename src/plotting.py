# src/plotting.py

import numpy as np
import matplotlib.pyplot as plt


def save_and_close(fig, save_path=None):
    """
    Save figure if path is provided, then close it without blocking.
    """
    fig.tight_layout()
    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure: {save_path}")
    plt.close(fig)


def plot_signal_pair(t, signal_a, signal_b, label_a, label_b, title, ylabel="Amplitude", save_path=None):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(t, signal_a, label=label_a, linewidth=1)
    ax.plot(t, signal_b, label=label_b, linewidth=1, alpha=0.85)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    save_and_close(fig, save_path)


def plot_three_stage_signals(t, sig1, sig2, sig3, titles, ylabels, save_path=None):
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

    axes[0].plot(t, sig1, linewidth=1)
    axes[0].set_title(titles[0])
    axes[0].set_ylabel(ylabels[0])
    axes[0].grid(True)

    axes[1].plot(t, sig2, linewidth=1)
    axes[1].set_title(titles[1])
    axes[1].set_ylabel(ylabels[1])
    axes[1].grid(True)

    axes[2].plot(t, sig3, linewidth=1)
    axes[2].set_title(titles[2])
    axes[2].set_xlabel("Time (s)")
    axes[2].set_ylabel(ylabels[2])
    axes[2].grid(True)

    save_and_close(fig, save_path)


def plot_filtered_and_envelope(t, filtered_signal, envelope, save_path=None):
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    axes[0].plot(t, filtered_signal, linewidth=1)
    axes[0].set_title("Filtered Signal Block")
    axes[0].set_ylabel("Voltage")
    axes[0].grid(True)

    axes[1].plot(t, envelope, linewidth=1)
    axes[1].set_title("Hilbert Envelope of Filtered Signal")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Envelope")
    axes[1].grid(True)

    save_and_close(fig, save_path)


def plot_confusion_matrix(cm, class_names, save_path=None):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")

    ax.set_title("Pain-State Classifier Confusion Matrix")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_xticks(range(len(class_names)))
    ax.set_xticklabels(class_names)
    ax.set_yticks(range(len(class_names)))
    ax.set_yticklabels(class_names)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")

    fig.colorbar(im, ax=ax, label="Count")
    save_and_close(fig, save_path)


def plot_q_table(Q, save_path=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(Q, cmap="viridis", aspect="auto")
    ax.set_title("Q-table After RL Update")
    ax.set_xlabel("Action Index")
    ax.set_ylabel("State Index")
    fig.colorbar(im, ax=ax, label="Q value")
    save_and_close(fig, save_path)


def plot_metrics_bar(results_dict, keys_to_plot, save_path=None):
    values = [results_dict[k] for k in keys_to_plot]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(keys_to_plot, values)
    ax.set_title("Performance Metrics Summary")
    ax.set_ylabel("Value")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")

    save_and_close(fig, save_path)


def plot_normalized_phase_comparison(t, signal_a, signal_b, label_a, label_b, title, save_path=None):
    a_norm = signal_a / (np.max(np.abs(signal_a)) + 1e-12)
    b_norm = signal_b / (np.max(np.abs(signal_b)) + 1e-12)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(t, a_norm, label=label_a, linewidth=1)
    ax.plot(t, b_norm, label=label_b, linewidth=1, alpha=0.85)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Normalized Amplitude")
    ax.legend()
    ax.grid(True)

    save_and_close(fig, save_path)