import pickle
import pandas as pd
import numpy as np

from pathlib import Path

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
    / "optimization"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "nsga2_predictions.csv"
)


# ============================================================
# LOAD DATA AND MODELS
# ============================================================

df = pd.read_csv(
    DATASET_FILE
)

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
# DESIGN PARAMETERS
# ============================================================

# x[0] = approx_bits
# x[1] = carry_truncation
# x[2] = correction_depth

LOWER_BOUNDS = np.array([
    0,
    0,
    0
])

UPPER_BOUNDS = np.array([
    8,
    8,
    4
])


# ============================================================
# DISCRETE DESIGN HANDLING
# ============================================================

VALID_DESIGNS = set(
    tuple(
        row[
            [
                "approx_bits",
                "carry_truncation",
                "correction_depth"
            ]
        ].astype(int)
    )
    for _, row in df.iterrows()
)


def nearest_valid_design(x):

    candidate = np.round(x).astype(int)

    candidate[0] = np.clip(
        candidate[0],
        0,
        8
    )

    candidate[1] = np.clip(
        candidate[1],
        0,
        candidate[0]
    )

    candidate[2] = np.clip(
        candidate[2],
        0,
        min(candidate[0], 4)
    )

    if tuple(candidate) in VALID_DESIGNS:
        return candidate

    # Find nearest valid characterized configuration
    best = None
    best_distance = float("inf")

    for design in VALID_DESIGNS:

        design_array = np.array(
            design,
            dtype=int
        )

        distance = np.sum(
            (design_array - candidate) ** 2
        )

        if distance < best_distance:

            best_distance = distance
            best = design_array

    return best


# ============================================================
# NSGA-II PROBLEM
# ============================================================

class ApproximateAdderProblem(
    ElementwiseProblem
):

    def __init__(self):

        super().__init__(

            n_var=3,

            n_obj=2,

            xl=LOWER_BOUNDS,

            xu=UPPER_BOUNDS
        )

    def _evaluate(
        self,
        x,
        out,
        *args,
        **kwargs
    ):

        design = nearest_valid_design(x)

        features = pd.DataFrame(
            [
                {
                    "approx_bits": design[0],
                    "carry_truncation": design[1],
                    "correction_depth": design[2]
                }
            ]
        )

        predicted_error = (
            error_model.predict(features)[0]
        )

        predicted_cells = (
            cell_model.predict(features)[0]
        )

        # Minimize both objectives
        out["F"] = np.array([
            predicted_error,
            predicted_cells
        ])


# ============================================================
# RUN NSGA-II
# ============================================================

print()
print("=" * 70)
print("ML-BASED NSGA-II OPTIMIZATION")
print("=" * 70)
print()

problem = ApproximateAdderProblem()

algorithm = NSGA2(
    pop_size=40
)

result = minimize(

    problem,

    algorithm,

    termination=(
        "n_gen",
        50
    ),

    seed=42,

    verbose=False
)


# ============================================================
# EXTRACT SOLUTIONS
# ============================================================

solutions = []

for x, f in zip(
    result.X,
    result.F
):

    design = nearest_valid_design(x)

    solutions.append({

        "approx_bits":
            int(design[0]),

        "carry_truncation":
            int(design[1]),

        "correction_depth":
            int(design[2]),

        "predicted_error_rate":
            float(f[0]),

        "predicted_cell_count":
            float(f[1])
    })


# ============================================================
# REMOVE DUPLICATES
# ============================================================

results = pd.DataFrame(
    solutions
)

results = results.drop_duplicates(
    subset=[
        "approx_bits",
        "carry_truncation",
        "correction_depth"
    ]
)

results = results.sort_values(
    [
        "predicted_error_rate",
        "predicted_cell_count"
    ]
)


# ============================================================
# SAVE
# ============================================================

results.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PRINT
# ============================================================

print(
    f"NSGA-II solutions found: {len(results)}"
)

print()

print(
    results.to_string(
        index=False
    )
)

print()
print("=" * 70)
print("NSGA-II OPTIMIZATION COMPLETE")
print("=" * 70)

print()
print("Saved to:")
print(OUTPUT_FILE)

print()