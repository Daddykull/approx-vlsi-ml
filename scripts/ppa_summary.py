import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "merged"
    / "physical_logical_dataset.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "physical_pareto"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "ppa_summary.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)


# ============================================================
# BASELINE
# ============================================================

baseline = df[
    (df["approx_bits"] == 0)
    & (df["carry_truncation"] == 0)
    & (df["correction_depth"] == 0)
].iloc[0]


# ============================================================
# FIND BEST DESIGNS
# ============================================================

best_area = df.loc[
    df["core_area_um2"].idxmin()
]

best_delay = df.loc[
    df["critical_path_ns"].idxmin()
]

best_power = df.loc[
    df["total_power_uW"].idxmin()
]


# ============================================================
# SUMMARY FUNCTION
# ============================================================

def design_name(row):

    return (
        f"k{int(row['approx_bits'])}"
        f"_t{int(row['carry_truncation'])}"
        f"_c{int(row['correction_depth'])}"
    )


def improvement(baseline_value, new_value):

    return (
        (baseline_value - new_value)
        / baseline_value
        * 100
    )


# ============================================================
# CREATE SUMMARY
# ============================================================

rows = []

for metric, row, column in [
    ("Minimum Area", best_area, "core_area_um2"),
    ("Minimum Delay", best_delay, "critical_path_ns"),
    ("Minimum Power", best_power, "total_power_uW")
]:

    rows.append({

        "objective": metric,

        "design": design_name(row),

        "error_rate": row["error_rate"],

        "baseline_value": baseline[column],

        "optimized_value": row[column],

        "improvement_percent":
            improvement(
                baseline[column],
                row[column]
            )
    })


summary = pd.DataFrame(rows)


# ============================================================
# SAVE
# ============================================================

summary.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PRINT
# ============================================================

print()
print("=" * 70)
print("PPA IMPROVEMENT SUMMARY")
print("=" * 70)

print()

print(
    summary.to_string(
        index=False
    )
)

print()
print("=" * 70)
print("BASELINE")
print("=" * 70)

print(
    f"Design : {design_name(baseline)}"
)

print(
    f"Error Rate : {baseline['error_rate']}"
)

print(
    f"Area : {baseline['core_area_um2']:.4f} um²"
)

print(
    f"Delay : {baseline['critical_path_ns']:.4f} ns"
)

print(
    f"Power : {baseline['total_power_uW']:.9f} uW"
)

print()
print("=" * 70)
print("PPA SUMMARY COMPLETE")
print("=" * 70)

print()
print("Saved to:")
print(OUTPUT_FILE)
print()