import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOGICAL_FILE = PROJECT_ROOT / "datasets" / "characterization.csv"
PHYSICAL_FILE = PROJECT_ROOT / "results" / "physical" / "physical_metrics.csv"

OUTPUT_DIR = PROJECT_ROOT / "results" / "merged"
OUTPUT_FILE = OUTPUT_DIR / "physical_logical_dataset.csv"


KEYS = [
    "approx_bits",
    "carry_truncation",
    "correction_depth",
]


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():

    print("=" * 70)
    print("PHYSICAL + LOGICAL DATASET MERGE")
    print("=" * 70)

    logical = read_csv(LOGICAL_FILE)
    physical = read_csv(PHYSICAL_FILE)

    print(f"Logical designs : {len(logical)}")
    print(f"Physical designs: {len(physical)}")

    physical_lookup = {}

    for row in physical:
        key = tuple(row[k] for k in KEYS)
        physical_lookup[key] = row

    merged = []

    for logical_row in logical:

        key = tuple(logical_row[k] for k in KEYS)

        if key not in physical_lookup:
            continue

        physical_row = physical_lookup[key]

        combined = {}

        for key_name, value in logical_row.items():
            combined[key_name] = value

        for key_name, value in physical_row.items():

            if key_name in KEYS:
                continue

            combined[key_name] = value

        merged.append(combined)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not merged:
        raise RuntimeError("No designs were successfully merged.")

    fieldnames = list(merged[0].keys())

    with open(OUTPUT_FILE, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(merged)

    print()
    print(f"Merged designs: {len(merged)}")
    print(f"Output        : {OUTPUT_FILE}")

    print()
    print("Merged designs:")

    for row in merged:

        print(
            f"  k={row['approx_bits']}, "
            f"t={row['carry_truncation']}, "
            f"c={row['correction_depth']} | "
            f"ER={row['error_rate']} | "
            f"Area={row['core_area_um2']} um^2 | "
            f"Delay={row['critical_path_ns']} ns | "
            f"Power={row['total_power_uW']} uW"
        )


if __name__ == "__main__":
    main()
