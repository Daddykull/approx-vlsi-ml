import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import joblib


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "combined_dataset.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "results"
    / "models"
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

df = pd.read_csv(DATASET_FILE)

FEATURES = [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]

X = df[FEATURES]


# ============================================================
# LOAD MODELS
# ============================================================

error_model = joblib.load(
    MODEL_DIR / "error_rate_model.pkl"
)

med_model = joblib.load(
    MODEL_DIR / "MED_model.pkl"
)

cell_model = joblib.load(
    MODEL_DIR / "cell_count_model.pkl"
)


# ============================================================
# PREDICTIONS
# ============================================================

df["predicted_error_rate"] = (
    error_model.predict(X)
)

df["predicted_MED"] = (
    med_model.predict(X)
)

df["predicted_cell_count"] = (
    cell_model.predict(X)
)


# ============================================================
# GENERIC PLOT FUNCTION
# ============================================================

def prediction_plot(
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
        s=55,
        alpha=0.8
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

    print(
        f"Saved: {output_file}"
    )


# ============================================================
# ERROR RATE
# ============================================================

prediction_plot(
    df["error_rate"],
    df["predicted_error_rate"],
    "Actual Error Rate",
    "Predicted Error Rate",
    "Random Forest Error-Rate Prediction",
    "ml_error_rate_actual_vs_predicted.png"
)


# ============================================================
# MED
# ============================================================

prediction_plot(
    df["MED"],
    df["predicted_MED"],
    "Actual MED",
    "Predicted MED",
    "Random Forest MED Prediction",
    "ml_MED_actual_vs_predicted.png"
)


# ============================================================
# LOGICAL CELL COUNT
# ============================================================

prediction_plot(
    df["cell_count"],
    df["predicted_cell_count"],
    "Actual Logical Cell Count",
    "Predicted Logical Cell Count",
    "Random Forest Cell-Count Prediction",
    "ml_cell_count_actual_vs_predicted.png"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("ML VALIDATION PLOTS COMPLETE")
print("=" * 70)

print()
print("Dataset designs :", len(df))
print()
print("Output directory:")
print(OUTPUT_DIR)
print()