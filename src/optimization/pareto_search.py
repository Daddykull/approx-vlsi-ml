import pickle
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    PROJECT_ROOT
    / "results"
    / "models"
)

DATASET_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "combined_dataset.csv"
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
    / "pareto_predictions.csv"
)


# ============================================================
# LOAD ML MODELS
# ============================================================

with open(
    MODEL_DIR / "error_rate_model.pkl",
    "rb"
) as f:
    error_model = pickle.load(f)


with open(
    MODEL_DIR / "cell_count_model.pkl",
    "rb"
) as f:
    cell_model = pickle.load(f)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_design(
    approx_bits,
    carry_truncation,
    correction_depth
):

    features = pd.DataFrame(
        [[
            approx_bits,
            carry_truncation,
            correction_depth
        ]],
        columns=FEATURES
    )

    predicted_error = float(
        error_model.predict(features)[0]
    )

    predicted_cells = float(
        cell_model.predict(features)[0]
    )

    return (
        predicted_error,
        predicted_cells
    )


# ============================================================
# PARETO CHECK
# ============================================================

def is_dominated(
    row,
    dataframe
):
    """
    A design is dominated if another design has:

        error_rate <= current error_rate
        cell_count <= current cell_count

    and is strictly better in at least one objective.
    """

    for _, other in dataframe.iterrows():

        better_or_equal_error = (
            other["predicted_error_rate"]
            <=
            row["predicted_error_rate"]
        )

        better_or_equal_cells = (
            other["predicted_cell_count"]
            <=
            row["predicted_cell_count"]
        )

        strictly_better = (
            other["predicted_error_rate"]
            <
            row["predicted_error_rate"]
            or
            other["predicted_cell_count"]
            <
            row["predicted_cell_count"]
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


# ============================================================
# START
# ============================================================

print("=" * 70)
print("DISCRETE ML-BASED PARETO DESIGN-SPACE EXPLORATION")
print("=" * 70)


# ============================================================
# LOAD VALID CHARACTERIZED DESIGNS
# ============================================================

dataset = pd.read_csv(
    DATASET_FILE
)

print()
print(
    f"Valid characterized designs: "
    f"{len(dataset)}"
)


# ============================================================
# ML PREDICTIONS
# ============================================================

results = []

for _, row in dataset.iterrows():

    (
        predicted_error,
        predicted_cells
    ) = predict_design(
        int(row["approx_bits"]),
        int(row["carry_truncation"]),
        int(row["correction_depth"])
    )

    results.append([
        int(row["approx_bits"]),
        int(row["carry_truncation"]),
        int(row["correction_depth"]),
        predicted_error,
        predicted_cells
    ])


predictions = pd.DataFrame(
    results,
    columns=[
        "approx_bits",
        "carry_truncation",
        "correction_depth",
        "predicted_error_rate",
        "predicted_cell_count"
    ]
)


# ============================================================
# FIND PREDICTED PARETO FRONT
# ============================================================

predictions["is_pareto"] = predictions.apply(
    lambda row:
        not is_dominated(
            row,
            predictions
        ),
    axis=1
)


pareto = predictions[
    predictions["is_pareto"]
].copy()


pareto = pareto.sort_values(
    by=[
        "predicted_error_rate",
        "predicted_cell_count"
    ]
)


# ============================================================
# PRINT PARETO FRONT
# ============================================================

print()
print(
    f"Predicted Pareto designs: "
    f"{len(pareto)}"
)

print()

print("=" * 70)
print("PREDICTED PARETO FRONT")
print("=" * 70)

print()

print(
    f"{'k':>3} "
    f"{'t':>3} "
    f"{'c':>3} "
    f"{'Pred ER':>12} "
    f"{'Pred Cells':>12}"
)

print("-" * 60)


for _, row in pareto.iterrows():

    print(
        f"{int(row['approx_bits']):3d} "
        f"{int(row['carry_truncation']):3d} "
        f"{int(row['correction_depth']):3d} "
        f"{row['predicted_error_rate']:12.6f} "
        f"{row['predicted_cell_count']:12.2f}"
    )


# ============================================================
# SAVE
# ============================================================

pareto_to_save = pareto.drop(
    columns=["is_pareto"]
)

pareto_to_save.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("PARETO SEARCH COMPLETE")
print("=" * 70)

print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)

print()