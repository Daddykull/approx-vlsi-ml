import pandas as pd
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

PREDICTION_FILE = (
    PROJECT_ROOT
    / "results"
    / "optimization"
    / "pareto_predictions.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "optimization"
    / "pareto_validation.csv"
)


# ============================================================
# DESIGN PARAMETERS
# ============================================================

KEYS = [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("ML PARETO FRONT vs GROUND TRUTH VALIDATION")
print("=" * 70)

actual = pd.read_csv(DATASET_FILE)
predicted = pd.read_csv(PREDICTION_FILE)

print()
print(f"Actual dataset designs    : {len(actual)}")
print(f"Predicted Pareto designs  : {len(predicted)}")


# ============================================================
# FIND ACTUAL PARETO FRONT
# ============================================================

def is_dominated(row, dataframe):
    """
    Returns True if another design is at least as good
    in both objectives and strictly better in at least one.

    Objectives:
        - minimize error_rate
        - minimize cell_count
    """

    for _, other in dataframe.iterrows():

        better_or_equal_error = (
            other["error_rate"] <= row["error_rate"]
        )

        better_or_equal_cells = (
            other["cell_count"] <= row["cell_count"]
        )

        strictly_better = (
            other["error_rate"] < row["error_rate"]
            or
            other["cell_count"] < row["cell_count"]
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
    lambda row: not is_dominated(row, actual),
    axis=1
)

actual_pareto = actual[
    actual["is_pareto"]
].copy()


# ============================================================
# MERGE ML PREDICTIONS WITH ACTUAL DATA
# ============================================================

validation = predicted.merge(
    actual,
    on=KEYS,
    how="left"
)


# ============================================================
# CALCULATE PREDICTION ERRORS
# ============================================================

validation["error_rate_difference"] = (
    validation["predicted_error_rate"]
    - validation["error_rate"]
)

validation["absolute_error_rate_difference"] = (
    validation["error_rate_difference"]
    .abs()
)

validation["cell_count_difference"] = (
    validation["predicted_cell_count"]
    - validation["cell_count"]
)

validation["absolute_cell_count_difference"] = (
    validation["cell_count_difference"]
    .abs()
)


# ============================================================
# SAVE VALIDATION DATASET
# ============================================================

validation.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("PREDICTED vs ACTUAL")
print("=" * 70)

print()

print(
    f"{'k':>3} "
    f"{'t':>3} "
    f"{'c':>3} "
    f"{'Pred ER':>10} "
    f"{'Actual ER':>10} "
    f"{'Pred Cells':>11} "
    f"{'Actual Cells':>12} "
    f"{'Actual Pareto':>14}"
)

print("-" * 85)

for _, row in validation.iterrows():

    pareto_status = (
        "YES"
        if row["is_pareto"]
        else "NO"
    )

    print(
        f"{int(row['approx_bits']):3d} "
        f"{int(row['carry_truncation']):3d} "
        f"{int(row['correction_depth']):3d} "
        f"{row['predicted_error_rate']:10.4f} "
        f"{row['error_rate']:10.4f} "
        f"{row['predicted_cell_count']:11.2f} "
        f"{row['cell_count']:12.0f} "
        f"{pareto_status:>14}"
    )


# ============================================================
# STATISTICS
# ============================================================

error_mae = (
    validation[
        "absolute_error_rate_difference"
    ].mean()
)

cell_mae = (
    validation[
        "absolute_cell_count_difference"
    ].mean()
)

pareto_hits = validation[
    "is_pareto"
].sum()

total_predictions = len(validation)

pareto_hit_rate = (
    pareto_hits / total_predictions * 100
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print()

print(
    f"Actual Pareto designs       : "
    f"{len(actual_pareto)}"
)

print(
    f"ML Pareto candidates        : "
    f"{total_predictions}"
)

print(
    f"ML candidates on true Pareto: "
    f"{pareto_hits}"
)

print(
    f"Pareto hit rate             : "
    f"{pareto_hit_rate:.2f}%"
)

print()

print(
    f"Error-rate prediction MAE  : "
    f"{error_mae:.6f}"
)

print(
    f"Cell-count prediction MAE  : "
    f"{cell_mae:.4f}"
)


# ============================================================
# ACTUAL PARETO FRONT
# ============================================================

print()
print("=" * 70)
print("ACTUAL PARETO FRONT")
print("=" * 70)

actual_pareto = actual_pareto.sort_values(
    by=["error_rate", "cell_count"]
)

print()

print(
    f"{'k':>3} "
    f"{'t':>3} "
    f"{'c':>3} "
    f"{'Error Rate':>12} "
    f"{'MED':>10} "
    f"{'Cells':>10}"
)

print("-" * 60)

for _, row in actual_pareto.iterrows():

    print(
        f"{int(row['approx_bits']):3d} "
        f"{int(row['carry_truncation']):3d} "
        f"{int(row['correction_depth']):3d} "
        f"{row['error_rate']:12.6f} "
        f"{row['MED']:10.4f} "
        f"{row['cell_count']:10.0f}"
    )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("PARETO VALIDATION COMPLETE")
print("=" * 70)

print()
print("Validation saved to:")
print(OUTPUT_FILE)

print()