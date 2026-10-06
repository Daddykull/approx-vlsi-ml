import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXHAUSTIVE_FILE = (
    PROJECT_ROOT
    / "results"
    / "optimization"
    / "pareto_predictions.csv"
)

NSGA2_FILE = (
    PROJECT_ROOT
    / "results"
    / "optimization"
    / "nsga2_predictions.csv"
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
    / "optimizer_comparison.csv"
)


# ============================================================
# LOAD RESULTS
# ============================================================

exhaustive = pd.read_csv(
    EXHAUSTIVE_FILE
)

nsga2 = pd.read_csv(
    NSGA2_FILE
)


# ============================================================
# DESIGN KEY
# ============================================================

KEYS = [
    "approx_bits",
    "carry_truncation",
    "correction_depth"
]

exhaustive["design_key"] = (
    exhaustive[KEYS]
    .astype(int)
    .astype(str)
    .agg("_".join, axis=1)
)

nsga2["design_key"] = (
    nsga2[KEYS]
    .astype(int)
    .astype(str)
    .agg("_".join, axis=1)
)


# ============================================================
# SET COMPARISON
# ============================================================

exhaustive_set = set(
    exhaustive["design_key"]
)

nsga2_set = set(
    nsga2["design_key"]
)

common = (
    exhaustive_set
    & nsga2_set
)

nsga2_only = (
    nsga2_set
    - exhaustive_set
)

exhaustive_only = (
    exhaustive_set
    - nsga2_set
)


# ============================================================
# COVERAGE
# ============================================================

if len(exhaustive_set) > 0:

    nsga2_coverage = (
        len(common)
        / len(exhaustive_set)
        * 100
    )

else:

    nsga2_coverage = 0.0


# ============================================================
# CREATE COMPARISON TABLE
# ============================================================

rows = []

for key in sorted(
    exhaustive_set
    | nsga2_set
):

    e = exhaustive[
        exhaustive["design_key"] == key
    ]

    n = nsga2[
        nsga2["design_key"] == key
    ]

    row = {
        "design_key": key,
        "in_exhaustive": len(e) > 0,
        "in_nsga2": len(n) > 0
    }

    if len(e) > 0:

        row[
            "exhaustive_error_rate"
        ] = e.iloc[0][
            "predicted_error_rate"
            if "predicted_error_rate" in e.columns
            else "predicted_error"
        ]

        row[
            "exhaustive_cell_count"
        ] = e.iloc[0][
            "predicted_cell_count"
            if "predicted_cell_count" in e.columns
            else "predicted_cells"
        ]

    else:

        row[
            "exhaustive_error_rate"
        ] = None

        row[
            "exhaustive_cell_count"
        ] = None

    if len(n) > 0:

        row[
            "nsga2_error_rate"
        ] = n.iloc[0][
            "predicted_error_rate"
        ]

        row[
            "nsga2_cell_count"
        ] = n.iloc[0][
            "predicted_cell_count"
        ]

    else:

        row[
            "nsga2_error_rate"
        ] = None

        row[
            "nsga2_cell_count"
        ] = None

    rows.append(row)


comparison = pd.DataFrame(rows)


# ============================================================
# SAVE
# ============================================================

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("EXHAUSTIVE SEARCH vs NSGA-II")
print("=" * 70)

print()

print(
    f"Exhaustive Pareto designs : "
    f"{len(exhaustive_set)}"
)

print(
    f"NSGA-II Pareto designs    : "
    f"{len(nsga2_set)}"
)

print(
    f"Common designs            : "
    f"{len(common)}"
)

print(
    f"NSGA-II coverage          : "
    f"{nsga2_coverage:.2f}%"
)

print()

print(
    f"NSGA-II only designs      : "
    f"{len(nsga2_only)}"
)

print(
    f"Exhaustive-only designs   : "
    f"{len(exhaustive_only)}"
)


# ============================================================
# AGREEMENT CHECK
# ============================================================

print()

if (
    len(nsga2_only) == 0
    and len(exhaustive_only) == 0
):

    print(
        "OPTIMIZER AGREEMENT: PASS"
    )

    print(
        "NSGA-II recovered the complete "
        "exhaustive Pareto front."
    )

else:

    print(
        "OPTIMIZER AGREEMENT: PARTIAL"
    )

    if nsga2_only:

        print()
        print("NSGA-II-only designs:")

        for key in sorted(nsga2_only):

            print(
                f"  {key}"
            )

    if exhaustive_only:

        print()
        print("Exhaustive-only designs:")

        for key in sorted(exhaustive_only):

            print(
                f"  {key}"
            )


print()
print("=" * 70)
print("COMPARISON COMPLETE")
print("=" * 70)

print()
print("Saved to:")
print(OUTPUT_FILE)

print()