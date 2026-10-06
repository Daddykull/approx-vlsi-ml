import pandas as pd
import numpy as np
import pickle

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET = PROJECT_ROOT / "datasets" / "combined_dataset.csv"
MODEL_DIR = PROJECT_ROOT / "results" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("ML SURROGATE MODEL TRAINING")
print("=" * 70)

print()
print(f"Loading dataset:")
print(DATASET)

df = pd.read_csv(DATASET)

print()
print(f"Designs loaded: {len(df)}")


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]

TARGETS = [
    "error_rate",
    "MED",
    "cell_count"
]

X = df[FEATURES]


# ============================================================
# CROSS VALIDATION
# ============================================================

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# ============================================================
# TRAIN MODELS
# ============================================================

for target in TARGETS:

    print()
    print("=" * 70)
    print(f"TRAINING MODEL: {target}")
    print("=" * 70)

    y = df[target]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )

    # --------------------------------------------------------
    # Cross-validation
    # --------------------------------------------------------

    mae_scores = -cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="neg_mean_absolute_error"
    )

    rmse_scores = np.sqrt(
        -cross_val_score(
            model,
            X,
            y,
            cv=cv,
            scoring="neg_mean_squared_error"
        )
    )

    r2_scores = cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="r2"
    )

    print()
    print("5-Fold Cross Validation")
    print("-" * 40)

    print(
        f"MAE  : {mae_scores.mean():.6f}"
        f" ± {mae_scores.std():.6f}"
    )

    print(
        f"RMSE : {rmse_scores.mean():.6f}"
        f" ± {rmse_scores.std():.6f}"
    )

    print(
        f"R²   : {r2_scores.mean():.6f}"
        f" ± {r2_scores.std():.6f}"
    )

    # --------------------------------------------------------
    # Train final model on complete dataset
    # --------------------------------------------------------

    model.fit(X, y)

    # --------------------------------------------------------
    # Training-set sanity check
    # --------------------------------------------------------

    predictions = model.predict(X)

    train_mae = mean_absolute_error(y, predictions)
    train_rmse = np.sqrt(
        mean_squared_error(y, predictions)
    )
    train_r2 = r2_score(y, predictions)

    print()
    print("Full-Dataset Fit")
    print("-" * 40)

    print(f"MAE  : {train_mae:.6f}")
    print(f"RMSE : {train_rmse:.6f}")
    print(f"R²   : {train_r2:.6f}")

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    print()
    print("Feature Importance")
    print("-" * 40)

    importance = model.feature_importances_

    for feature, value in zip(FEATURES, importance):
        print(f"{feature:20s}: {value:.4f}")

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    model_path = MODEL_DIR / f"{target}_model.pkl"

    with open(model_path, "wb") as file:
        pickle.dump(model, file)

    print()
    print(f"Model saved:")
    print(model_path)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("ML MODEL TRAINING COMPLETE")
print("=" * 70)

print()
print("Models generated:")

for target in TARGETS:
    print(f"  - results/models/{target}_model.pkl")

print()