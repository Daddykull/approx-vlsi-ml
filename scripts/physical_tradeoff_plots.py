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


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)


# ============================================================
# DESIGN LABEL
# ============================================================

df["design"] = (
    "k"
    + df["approx_bits"].astype(str)
    + "_t"
    + df["carry_truncation"].astype(str)
    + "_c"
    + df["correction_depth"].astype(str)
)


# ============================================================
# GENERIC PLOT FUNCTION
# ============================================================

def create_plot(
    x_column,
    x_label,
    filename,
    title
):

    plt.figure(
        figsize=(10, 7)
    )

    plt.scatter(
        df[x_column],
        df["error_rate"],
        s=80
    )

    # Add design labels
    for _, row in df.iterrows():

        plt.annotate(
            row["design"],
            (
                row[x_column],
                row["error_rate"]
            ),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    plt.xlabel(x_label)

    plt.ylabel(
        "Error Rate"
    )

    plt.title(
        title
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        OUTPUT_DIR
        / filename
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


# ============================================================
# GENERATE THREE TRADE-OFF PLOTS
# ============================================================

print()
print("=" * 70)
print("PHYSICAL TRADE-OFF ANALYSIS")
print("=" * 70)
print()


create_plot(
    "core_area_um2",
    "Core Area (µm²)",
    "error_vs_area.png",
    "Error Rate vs Physical Area"
)


create_plot(
    "critical_path_ns",
    "Critical Path Delay (ns)",
    "error_vs_delay.png",
    "Error Rate vs Critical Path Delay"
)


create_plot(
    "total_power_uW",
    "Total Power (µW)",
    "error_vs_power.png",
    "Error Rate vs Total Power"
)


print()
print("=" * 70)
print("TRADE-OFF ANALYSIS COMPLETE")
print("=" * 70)
print()