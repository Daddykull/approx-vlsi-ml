import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "combined_dataset.csv"
)

VALIDATION_FILE = (
    PROJECT_ROOT
    / "results"
    / "optimization"
    / "pareto_validation.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "optimization"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "pareto_comparison.png"
)


# ============================================================
# LOAD DATA
# ============================================================

actual = pd.read_csv(
    DATASET_FILE
)

validation = pd.read_csv(
    VALIDATION_FILE
)


# ============================================================
# FIND ACTUAL PARETO FRONT
# ============================================================

def is_dominated(row, dataframe):

    for _, other in dataframe.iterrows():

        better_or_equal_error = (
            other["error_rate"]
            <=
            row["error_rate"]
        )

        better_or_equal_cells = (
            other["cell_count"]
            <=
            row["cell_count"]
        )

        strictly_better = (
            other["error_rate"]
            <
            row["error_rate"]
            or
            other["cell_count"]
            <
            row["cell_count"]
        )

        if (
            better_or_equal_error
            and
            better_or_equal_cells
            and
            strictly_better
        ):
            return True

    return False


actual["is_pareto"] = actual.apply(
    lambda row:
        not is_dominated(
            row,
            actual
        ),
    axis=1
)

actual_pareto = actual[
    actual["is_pareto"]
].copy()


# ============================================================
# PLOT
# ============================================================

plt.figure(
    figsize=(10, 7)
)

# Actual Pareto front
plt.scatter(
    actual_pareto["cell_count"],
    actual_pareto["error_rate"],
    marker="o",
    s=70,
    label="Actual Pareto Front"
)


# ML predicted Pareto candidates
plt.scatter(
    validation["predicted_cell_count"],
    validation["predicted_error_rate"],
    marker="x",
    s=80,
    label="ML Predicted Pareto"
)


# ============================================================
# LABEL AXES
# ============================================================

plt.xlabel(
    "Cell Count"
)

plt.ylabel(
    "Error Rate"
)

plt.title(
    "ML-Predicted vs Ground-Truth Pareto Front"
)


plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print()
print("=" * 70)
print("PARETO PLOT GENERATED")
print("=" * 70)

print()
print(
    "Saved to:"
)

print(
    OUTPUT_FILE
)

print()