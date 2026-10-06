import pickle
import pandas as pd

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_DIR = PROJECT_ROOT / "results" / "models"


# ============================================================
# LOAD MODELS
# ============================================================

MODELS = {}

for target in [
    "error_rate",
    "MED",
    "cell_count"
]:

    model_path = MODEL_DIR / f"{target}_model.pkl"

    with open(model_path, "rb") as file:
        MODELS[target] = pickle.load(file)


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

    design = pd.DataFrame(
        [[
            approx_bits,
            carry_truncation,
            correction_depth
        ]],
        columns=FEATURES
    )

    predictions = {}

    for target, model in MODELS.items():

        prediction = model.predict(design)[0]

        predictions[target] = float(prediction)

    return predictions


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("ML SURROGATE PREDICTION")
    print("=" * 65)

    test_designs = [
        (2, 0, 0),
        (4, 2, 1),
        (6, 4, 2),
        (8, 6, 4)
    ]

    for design in test_designs:

        approx_bits, carry_truncation, correction_depth = design

        prediction = predict_design(
            approx_bits,
            carry_truncation,
            correction_depth
        )

        print()
        print(
            f"Design: "
            f"k={approx_bits}, "
            f"t={carry_truncation}, "
            f"c={correction_depth}"
        )

        print(
            f"  Predicted Error Rate : "
            f"{prediction['error_rate']:.6f}"
        )

        print(
            f"  Predicted MED        : "
            f"{prediction['MED']:.6f}"
        )

        print(
            f"  Predicted Cell Count : "
            f"{prediction['cell_count']:.2f}"
        )

    print()
    print("=" * 65)
    print("PREDICTION TEST COMPLETE")
    print("=" * 65)