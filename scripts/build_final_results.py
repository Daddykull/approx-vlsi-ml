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
    / "final"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "final_results.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

nsga2 = pd.read_csv(NSGA2_FILE)
physical = pd.read_csv(PHYSICAL_FILE)


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


nsga2["design_key"] = make_key(nsga2)
physical["design_key"] = make_key(physical)


# ============================================================
# CHECK AVAILABLE PHYSICAL COLUMNS
# ============================================================

print()
print("Available physical columns:")
print(list(physical.columns))
print()


# ============================================================
# STANDARDIZE PHYSICAL CELL COUNT
# ============================================================

if "synth_cell_count" in physical.columns:

    physical["synth_cell_count_actual"] = (
        physical["synth_cell_count"]
    )

elif "total_cells" in physical.columns:

    physical["synth_cell_count_actual"] = (
        physical["total_cells"]
    )

elif "cell_count" in physical.columns:

    physical["synth_cell_count_actual"] = (
        physical["cell_count"]
    )

else:

    raise KeyError(
        "No physical cell-count column found. "
        "Expected one of: "
        "synth_cell_count, total_cells, cell_count"
    )


# ============================================================
# SELECT PHYSICAL RESULTS
# ============================================================

physical_columns = [
    "design_key",

    "error_rate",
    "MED",
    "NMED",
    "max_error",

    "synth_cell_count_actual",

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


# ============================================================
# MERGE NSGA-II + PHYSICAL RESULTS
# ============================================================

final = nsga2.merge(
    physical_selected,
    on="design_key",
    how="left"
)


# ============================================================
# PHYSICAL VALIDATION
# ============================================================

final["physical_validation"] = (
    final["core_area_um2"].notna()
    & final["critical_path_ns"].notna()
    & final["total_power_uW"].notna()
)


# ============================================================
# CLEAN DRC / LVS CHECK
# ============================================================

final["clean_drc_lvs"] = (
    final["route_violations"].fillna(999) == 0
) & (
    final["short_violations"].fillna(999) == 0
) & (
    final["magic_violations"].fillna(999) == 0
) & (
    final["lvs_errors"].fillna(999) == 0
)


# ============================================================
# DESIGN LABEL
# ============================================================

final["design"] = (
    "k"
    + final["approx_bits"].astype(str)
    + "_t"
    + final["carry_truncation"].astype(str)
    + "_c"
    + final["correction_depth"].astype(str)
)


# ============================================================
# SAVE
# ============================================================

final.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("=" * 70)
print("FINAL MASTER RESULTS")
print("=" * 70)

print()

print(
    f"NSGA-II designs       : {len(nsga2)}"
)

print(
    f"Physical matches      : "
    f"{int(final['physical_validation'].sum())}"
)

print(
    f"Clean DRC/LVS designs : "
    f"{int(final['clean_drc_lvs'].sum())}"
)

print()

display_columns = [
    "design",

    "predicted_error_rate",
    "error_rate",

    "predicted_cell_count",
    "synth_cell_count_actual",

    "MED",

    "core_area_um2",
    "critical_path_ns",
    "total_power_uW",

    "physical_validation",
    "clean_drc_lvs"
]

print(
    final[
        display_columns
    ].to_string(index=False)
)

print()
print("=" * 70)
print("FINAL MASTER RESULTS COMPLETE")
print("=" * 70)

print()
print("Saved to:")
print(OUTPUT_FILE)
print()