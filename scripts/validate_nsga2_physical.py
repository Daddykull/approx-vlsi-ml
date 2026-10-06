import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

NSGA2_FILE = (
    PROJECT_ROOT
    / "results"
    / "optimization"
    / "nsga2_predictions.csv"
)

PHYSICAL_FILE = (
    PROJECT_ROOT
    / "results"
    / "merged"
    / "physical_logical_dataset.csv"
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
    / "nsga2_physical_validation.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

nsga2 = pd.read_csv(
    NSGA2_FILE
)

physical = pd.read_csv(
    PHYSICAL_FILE
)


# ============================================================
# DESIGN KEY
# ============================================================

KEYS = [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]


def make_key(df):

    return (
        df[KEYS]
        .astype(int)
        .astype(str)
        .agg("_".join, axis=1)
    )


nsga2["design_key"] = make_key(
    nsga2
)

physical["design_key"] = make_key(
    physical
)


# ============================================================
# MERGE NSGA-II WITH PHYSICAL RESULTS
# ============================================================

physical_columns = [
    "design_key",
    "error_rate",
    "core_area_um2",
    "critical_path_ns",
    "total_power_uW",
    "route_violations",
    "short_violations",
    "magic_violations",
    "lvs_errors"
]

physical_selected = physical[
    physical_columns
].copy()


validation = nsga2.merge(
    physical_selected,
    on="design_key",
    how="left"
)


# ============================================================
# VALIDATION STATUS
# ============================================================

validation["physical_validation"] = (
    validation["core_area_um2"].notna()
    & validation["critical_path_ns"].notna()
    & validation["total_power_uW"].notna()
)

validation["physical_clean"] = (
    validation["route_violations"].fillna(999) == 0
) & (
    validation["short_violations"].fillna(999) == 0
) & (
    validation["magic_violations"].fillna(999) == 0
) & (
    validation["lvs_errors"].fillna(999) == 0
)


# ============================================================
# SAVE
# ============================================================

validation.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PRINT SUMMARY
# ============================================================

total = len(validation)

validated = int(
    validation[
        "physical_validation"
    ].sum()
)

clean = int(
    validation[
        "physical_clean"
    ].sum()
)


print()
print("=" * 70)
print("NSGA-II → OPENLANE PHYSICAL VALIDATION")
print("=" * 70)

print()

print(
    f"NSGA-II candidates       : {total}"
)

print(
    f"Physically validated     : {validated}"
)

print(
    f"Clean physical results   : {clean}"
)

print()

if total > 0:

    print(
        f"Physical coverage        : "
        f"{validated / total * 100:.2f}%"
    )

    print(
        f"Clean validation rate    : "
        f"{clean / total * 100:.2f}%"
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("Validated NSGA-II Designs")
print("-" * 70)

display_columns = [
    "approx_bits",
    "carry_truncation",
    "correction_depth",
    "predicted_error_rate",
    "predicted_cell_count",
    "error_rate",
    "core_area_um2",
    "critical_path_ns",
    "total_power_uW",
    "physical_validation",
    "physical_clean"
]

print(
    validation[
        display_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# FINAL STATUS
# ============================================================

print()
print("=" * 70)

if (
    validated == total
    and clean == total
):

    print(
        "NSGA-II PHYSICAL VALIDATION: PASS"
    )

else:

    print(
        "NSGA-II PHYSICAL VALIDATION: PARTIAL"
    )

print("=" * 70)

print()
print("Saved to:")
print(OUTPUT_FILE)

print()