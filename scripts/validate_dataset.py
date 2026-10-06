import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET = PROJECT_ROOT / "datasets" / "combined_dataset.csv"


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 65)
print("VALIDATING COMBINED DATASET")
print("=" * 65)

df = pd.read_csv(DATASET)

print()
print(f"Dataset: {DATASET}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# EXPECTED COLUMNS
# ============================================================

expected_columns = [
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

print()
print("Checking columns...")

if list(df.columns) != expected_columns:
    raise RuntimeError(
        "ERROR: Dataset columns do not match expected columns."
    )

print("PASS: Column structure is correct.")


# ============================================================
# ROW COUNT
# ============================================================

print()
print("Checking row count...")

if len(df) != 55:
    raise RuntimeError(
        f"ERROR: Expected 55 designs, found {len(df)}."
    )

print("PASS: 55 designs found.")


# ============================================================
# MISSING VALUES
# ============================================================

print()
print("Checking missing values...")

missing = df.isnull().sum()

if missing.sum() != 0:
    print(missing[missing > 0])
    raise RuntimeError("ERROR: Missing values detected.")

print("PASS: No missing values.")


# ============================================================
# DUPLICATE CONFIGURATIONS
# ============================================================

keys = [
    "width",
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]

print()
print("Checking duplicate configurations...")

duplicates = df.duplicated(subset=keys).sum()

if duplicates != 0:
    raise RuntimeError(
        f"ERROR: Found {duplicates} duplicate configurations."
    )

print("PASS: All configurations are unique.")


# ============================================================
# PARAMETER VALIDATION
# ============================================================

print()
print("Checking parameter ranges...")

if (df["approx_bits"] < 0).any():
    raise RuntimeError("ERROR: Negative approx_bits found.")

if (df["carry_truncation"] < 0).any():
    raise RuntimeError("ERROR: Negative carry_truncation found.")

if (df["correction_depth"] < 0).any():
    raise RuntimeError("ERROR: Negative correction_depth found.")

if (df["error_rate"] < 0).any() or (df["error_rate"] > 1).any():
    raise RuntimeError("ERROR: error_rate outside [0,1].")

if (df["MED"] < 0).any():
    raise RuntimeError("ERROR: Negative MED found.")

if (df["NMED"] < 0).any():
    raise RuntimeError("ERROR: Negative NMED found.")

if (df["max_error"] < 0).any():
    raise RuntimeError("ERROR: Negative max_error found.")

if (df["cell_count"] <= 0).any():
    raise RuntimeError("ERROR: Invalid cell_count found.")

print("PASS: Parameter ranges are valid.")


# ============================================================
# BASIC STATISTICS
# ============================================================

print()
print("=" * 65)
print("DATASET STATISTICS")
print("=" * 65)

print()
print(df.describe().round(6).to_string())


# ============================================================
# UNIQUE DESIGN PARAMETERS
# ============================================================

print()
print("=" * 65)
print("DESIGN-SPACE PARAMETERS")
print("=" * 65)

for column in [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]:
    print()
    print(f"{column}:")
    print(sorted(df[column].unique().tolist()))


# ============================================================
# CORRELATION
# ============================================================

print()
print("=" * 65)
print("CORRELATION WITH TARGET METRICS")
print("=" * 65)

correlation = df[
    [
        "approx_bits",
        "carry_truncation",
        "correction_depth",
        "error_rate",
        "MED",
        "NMED",
        "max_error",
        "cell_count"
    ]
].corr()

print()
print(correlation.round(3).to_string())


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 65)
print("DATASET VALIDATION COMPLETE")
print("=" * 65)

print()
print("STATUS: PASS")
print()
print("The dataset is ready for ML surrogate modeling.")
print()