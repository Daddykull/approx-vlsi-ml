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
    / "final"
    / "final_results.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "final"
    / "plots"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "physical_ppa_improvement.png"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)


# ============================================================
# BASELINE
# ============================================================

baseline = df[
    df["design"] == "k0_t0_c0"
].iloc[0]


baseline_area = baseline["core_area_um2"]
baseline_delay = baseline["critical_path_ns"]
baseline_power = baseline["total_power_uW"]


# ============================================================
# SELECT AGGRESSIVE APPROXIMATION POINT
# ============================================================

# Use the most aggressive validated configuration.
aggressive = df[
    df["design"] == "k8_t8_c0"
].iloc[0]


area_improvement = (
    (baseline_area - aggressive["core_area_um2"])
    / baseline_area
    * 100
)

delay_improvement = (
    (baseline_delay - aggressive["critical_path_ns"])
    / baseline_delay
    * 100
)

power_improvement = (
    (baseline_power - aggressive["total_power_uW"])
    / baseline_power
    * 100
)


# ============================================================
# PLOT
# ============================================================

metrics = [
    "Area",
    "Delay",
    "Power"
]

improvements = [
    area_improvement,
    delay_improvement,
    power_improvement
]


plt.figure(figsize=(8, 6))

bars = plt.bar(
    metrics,
    improvements
)

plt.ylabel(
    "Improvement relative to exact baseline (%)"
)

plt.xlabel(
    "Physical metric"
)

plt.title(
    "Physical PPA Improvement at k8_t8_c0"
)

plt.grid(
    axis="y",
    alpha=0.3
)


# Add values above bars

for bar, value in zip(
    bars,
    improvements
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}%",
        ha="center",
        va="bottom"
    )


plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("PHYSICAL PPA IMPROVEMENT")
print("=" * 70)

print()

print(
    f"Baseline : k0_t0_c0"
)

print(
    f"Optimized: k8_t8_c0"
)

print()

print(
    f"Area improvement  : {area_improvement:.2f}%"
)

print(
    f"Delay improvement : {delay_improvement:.2f}%"
)

print(
    f"Power improvement : {power_improvement:.2f}%"
)

print()

print("=" * 70)
print("PLOT SAVED")
print("=" * 70)

print()
print(OUTPUT_FILE)
print()