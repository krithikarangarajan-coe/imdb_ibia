"""Optional plotting of per-model classification counts."""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt


def plot_classification_results(results, model_names, output_png="classification_results.png"):
    """Bar chart of malignant vs non-malignant counts per model.

    results: dict {filename: [label_per_model, ...]}
    model_names: list of model names, in the same order as the per-file label lists.
    """
    malignant_counts = []
    non_malignant_counts = []

    for idx in range(len(model_names)):
        malignant = sum(1 for labels in results.values() if labels[idx] == "malignant")
        non_malignant = sum(1 for labels in results.values() if labels[idx] == "non-malignant")
        malignant_counts.append(malignant)
        non_malignant_counts.append(non_malignant)

    x = np.arange(len(model_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(10, len(model_names) * 1.2), 8))
    ax.bar(x - width / 2, malignant_counts, width, label="Malignant", color="red")
    ax.bar(x + width / 2, non_malignant_counts, width, label="Non-Malignant", color="green")

    ax.set_xlabel("Models")
    ax.set_ylabel("Number of Images")
    ax.set_title("Classification Results by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, rotation=90, ha="right")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {output_png}")
