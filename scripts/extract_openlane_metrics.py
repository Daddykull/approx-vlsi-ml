import csv
import re
from pathlib import Path

OPENLANE = Path.home() / "OpenLane" / "designs"
OUTPUT = Path(
    "/mnt/c/Users/Mahadeo Manjarekar/Documents/approx-vlsi-ml/"
    "results/physical/physical_metrics.csv"
)

DESIGN_RE = re.compile(
    r"approx_adder_w16_k(\d+)_t(\d+)_c(\d+)$"
)

rows = []

for design_dir in sorted(OPENLANE.glob("approx_adder_w16_*")):

    match = DESIGN_RE.match(design_dir.name)

    if not match:
        continue

    k, t, c = map(int, match.groups())

    runs_dir = design_dir / "runs"

    if not runs_dir.exists():
        continue

    metric_files = list(
        runs_dir.glob("*/reports/metrics.csv")
    )

    if not metric_files:
        print(f"[SKIP] No metrics.csv: {design_dir.name}")
        continue

    # Select latest run by run-directory name
    metric_files.sort()
    metrics_file = metric_files[-1]

    with open(metrics_file, newline="") as f:
        reader = csv.DictReader(f)
        data = next(reader)

    def get(key):
        return data.get(key, "")

    def number(key):
        value = get(key)

        if value in ("", None):
            return ""

        try:
            return float(value)
        except ValueError:
            return value

    internal = number("power_typical_internal_uW")
    switching = number("power_typical_switching_uW")
    leakage = number("power_typical_leakage_uW")

    total_power = ""

    if all(
        isinstance(x, float) and x >= 0
        for x in [internal, switching, leakage]
    ):
        total_power = internal + switching + leakage

    row = {
        "design_name": get("design_name"),
        "approx_bits": k,
        "carry_truncation": t,
        "correction_depth": c,

        "flow_status": get("flow_status"),
        "run_id": get("config"),

        "die_area_mm2": number("DIEAREA_mm^2"),
        "core_area_um2": number("CoreArea_um^2"),
        "open_dp_util_percent": number("OpenDP_Util"),

        "synth_cell_count": number("synth_cell_count"),
        "total_cells": number("TotalCells"),

        "wire_length": number("wire_length"),
        "vias": number("vias"),
        "hpwl": number("HPWL"),

        "wns_ns": number("wns"),
        "tns_ns": number("tns"),
        "critical_path_ns": number("critical_path_ns"),

        "clock_period_ns": number("CLOCK_PERIOD"),
        "clock_frequency_mhz": number(
            "suggested_clock_frequency"
        ),

        "internal_power_uW": internal,
        "switching_power_uW": switching,
        "leakage_power_uW": leakage,
        "total_power_uW": total_power,

        "route_violations": number(
            "tritonRoute_violations"
        ),
        "short_violations": number(
            "Short_violations"
        ),
        "metspc_violations": number(
            "MetSpc_violations"
        ),
        "offgrid_violations": number(
            "OffGrid_violations"
        ),
        "minhole_violations": number(
            "MinHole_violations"
        ),
        "magic_violations": number(
            "Magic_violations"
        ),

        "pin_antenna_violations": number(
            "pin_antenna_violations"
        ),
        "net_antenna_violations": number(
            "net_antenna_violations"
        ),

        "lvs_errors": number("lvs_total_errors"),

        "routing_layer1_pct": number(
            "routing_layer1_pct"
        ),
        "routing_layer2_pct": number(
            "routing_layer2_pct"
        ),
        "routing_layer3_pct": number(
            "routing_layer3_pct"
        ),
        "routing_layer4_pct": number(
            "routing_layer4_pct"
        ),
        "routing_layer5_pct": number(
            "routing_layer5_pct"
        ),
        "routing_layer6_pct": number(
            "routing_layer6_pct"
        ),

        "fp_core_util": number("FP_CORE_UTIL"),
        "pl_target_density": number(
            "PL_TARGET_DENSITY"
        ),

        "std_cell_library": get(
            "STD_CELL_LIBRARY"
        ),
        "synth_strategy": get(
            "SYNTH_STRATEGY"
        ),
    }

    rows.append(row)

    print(
        f"[OK] {design_dir.name} | "
        f"Area={row['core_area_um2']} um^2 | "
        f"Delay={row['critical_path_ns']} ns | "
        f"Power={row['total_power_uW']} uW | "
        f"LVS={row['lvs_errors']}"
    )


if not rows:
    raise SystemExit("ERROR: No OpenLane metrics found.")


OUTPUT.parent.mkdir(parents=True, exist_ok=True)

fieldnames = list(rows[0].keys())

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(rows)

print()
print("=" * 72)
print(f"Extracted designs : {len(rows)}")
print(f"Output            : {OUTPUT}")
print("=" * 72)
