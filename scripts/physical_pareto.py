import pandas as pd
import matplotlib.pyplot as plt
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

CSV_OUTPUT = (
    OUTPUT_DIR
    / "physical_pareto.csv"
)

PLOT_OUTPUT = (
    OUTPUT_DIR
    / "physical_pareto.png"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

OBJECTIVES = [
    "error_rate",
    "core_area_um2",
    "critical_path_ns",
    "total_power_uW"
]


# ============================================================
# PARETO DOMINANCE
# ============================================================

def is_dominated(row, dataframe):

    for _, other in dataframe.iterrows():

        better_or_equal = all(
            other[obj] <= row[obj]
            for obj in OBJECTIVES
        )

        strictly_better = any(
            other[obj] < row[obj]
            for obj in OBJECTIVES
        )

        if better_or_equal and strictly_better:
            return True

    return False


df["is_physical_pareto"] = df.apply(
    lambda row: not is_dominated(row, df),
    axis=1
)

pareto = df[
    df["is_physical_pareto"]
].copy()


# ============================================================
# SAVE PARETO DATASET
# ============================================================

pareto.to_csv(
    CSV_OUTPUT,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("PHYSICAL PARETO ANALYSIS")
print("=" * 70)

print()
print(f"Total physical designs : {len(df)}")
print(f"Physical Pareto designs: {len(pareto)}")

print()
print("Physical Pareto Front")
print("-" * 70)

columns = [
    "approx_bits",
    "carry_truncation",
    "correction_depth",
    "error_rate",
    "core_area_um2",
    "critical_path_ns",
    "total_power_uW"
]

print(
    pareto[columns].to_string(
        index=False
    )
)


# ============================================================
# 2D VISUALIZATION
# ============================================================

plt.figure(
    figsize=(10, 7)
)

plt.scatter(
    df["core_area_um2"],
    df["error_rate"],
    s=70,
    label="All Physical Designs"
)

plt.scatter(
    pareto["core_area_um2"],
    pareto["error_rate"],
    s=100,
    marker="x",
    label="Physical Pareto Designs"
)

plt.xlabel(
    "Core Area (µm²)"
)

plt.ylabel(
    "Error Rate"
)

plt.title(
    "Physical Pareto Front: Error Rate vs Area"
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.savefig(
    PLOT_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("PHYSICAL PARETO ANALYSIS COMPLETE")
print("=" * 70)

print()
print("CSV saved to:")
print(CSV_OUTPUT)

print()
print("Plot saved to:")
print(PLOT_OUTPUT)

print()