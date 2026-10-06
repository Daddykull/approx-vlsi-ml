import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "final"
    / "final_results.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "final"
    / "plots"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)


# ============================================================
# PLOT FUNCTION
# ============================================================

def create_prediction_plot(
    actual,
    predicted,
    xlabel,
    ylabel,
    title,
    filename
):

    plt.figure(figsize=(7, 6))

    plt.scatter(
        actual,
        predicted,
        s=70
    )

    minimum = min(
        actual.min(),
        predicted.min()
    )

    maximum = max(
        actual.max(),
        predicted.max()
    )

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--"
    )

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output_file = OUTPUT_DIR / filename

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Saved: {output_file}")


# ============================================================
# ERROR RATE
# ============================================================

create_prediction_plot(
    df["error_rate"],
    df["predicted_error_rate"],
    "Actual Error Rate",
    "Predicted Error Rate",
    "Random Forest: Error Rate Prediction",
    "actual_vs_predicted_error_rate.png"
)


# ============================================================
# LOGICAL CELL COUNT
# ============================================================

# The RF model predicts the logical characterization
# cell-count metric, NOT OpenLane synth_cell_count.

create_prediction_plot(
    df["synth_cell_count_actual"],
    df["predicted_cell_count"],
    "OpenLane Synthesized Cell Count",
    "Predicted Logical Cell Count",
    "Logical vs Physical Cell Count",
    "logical_vs_physical_cell_count.png"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("ML PREDICTION PLOTS COMPLETE")
print("=" * 70)

print()
print("Output directory:")
print(OUTPUT_DIR)
print()