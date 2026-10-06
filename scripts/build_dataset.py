import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "datasets"

ERROR_DATASET = (
    DATASET_DIR / "characterization.csv"
)

HARDWARE_DATASET = (
    DATASET_DIR / "hardware_characterization.csv"
)

OUTPUT_DATASET = (
    DATASET_DIR / "combined_dataset.csv"
)


# ============================================================
# LOAD DATASETS
# ============================================================

print("=" * 60)
print("BUILDING COMBINED ML DATASET")
print("=" * 60)

print()
print("Loading error characterization...")

error_df = pd.read_csv(
    ERROR_DATASET
)

print(
    f"Error designs: {len(error_df)}"
)


print()
print("Loading hardware characterization...")

hardware_df = pd.read_csv(
    HARDWARE_DATASET
)

print(
    f"Hardware designs: {len(hardware_df)}"
)


# ============================================================
# MERGE
# ============================================================

KEYS = [
    "width",
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]


print()
print("Merging datasets...")

combined_df = pd.merge(
    error_df,
    hardware_df,
    on=KEYS,
    how="inner"
)


# ============================================================
# CHECK MERGE
# ============================================================

print()
print(
    f"Combined designs: {len(combined_df)}"
)


if len(combined_df) != len(error_df):

    raise RuntimeError(
        "ERROR: Some error-characterization "
        "designs do not have hardware data."
    )


# ============================================================
# SELECT ML FEATURES
# ============================================================

columns = [
    "width",
    "approx_bits",
    "carry_truncation",
    "correction_depth",
    "error_rate",
    "MED",
    "NMED",
    "max_error",
    "cell_count"
]

combined_df = combined_df[columns]


# ============================================================
# SORT
# ============================================================

combined_df = combined_df.sort_values(
    by=[
        "approx_bits",
        "carry_truncation",
        "correction_depth"
    ]
)


# ============================================================
# SAVE
# ============================================================

combined_df.to_csv(
    OUTPUT_DATASET,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print()
print("=" * 60)
print("COMBINED DATASET COMPLETE")
print("=" * 60)

print()
print(
    f"Rows: {len(combined_df)}"
)

print(
    f"Columns: {len(combined_df.columns)}"
)

print()
print(
    f"Dataset: {OUTPUT_DATASET}"
)

print()
print("Columns:")

for column in combined_df.columns:
    print(
        f"  - {column}"
    )

print()
print("First 10 rows:")
print(
    combined_df.head(10).to_string(
        index=False
    )
)

print()