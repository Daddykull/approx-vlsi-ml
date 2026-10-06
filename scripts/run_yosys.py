import sys
import csv
import re
import subprocess
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PATHS
# ============================================================

RTL_DIR = PROJECT_ROOT / "rtl"

DATASET_DIR = PROJECT_ROOT / "datasets"

ERROR_DATASET = DATASET_DIR / "characterization.csv"

HARDWARE_DATASET = DATASET_DIR / "hardware_characterization.csv"

RESULT_DIR = (
    PROJECT_ROOT
    / "results"
    / "characterization"
)

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# YOSYS
# ============================================================

YOSYS_EXE = r"C:\oss-cad-suite\bin\yosys.exe"


# ============================================================
# RUN YOSYS
# ============================================================

def run_yosys(rtl_file, module_name):

    report_file = (
        RESULT_DIR
        / f"{module_name}.txt"
    )

    rtl_path = str(
        rtl_file
    ).replace("\\", "/")

    yosys_script = f"""
read_verilog "{rtl_path}"
hierarchy -top {module_name}
proc
opt
check
stat
"""

    result = subprocess.run(
        [
            YOSYS_EXE,
            "-p",
            yosys_script
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Save complete report
    report_file.write_text(
        result.stdout,
        encoding="utf-8"
    )

    return result.stdout


# ============================================================
# PARSE YOSYS STATISTICS
# ============================================================

def parse_statistics(output):

    cell_match = re.search(
        r"^\s*(\d+)\s+cells\s*$",
        output,
        re.MULTILINE
    )

    if not cell_match:

        raise RuntimeError(
            "Could not find total cell count "
            "in Yosys output."
        )

    return {
        "cell_count": int(
            cell_match.group(1)
        )
    }


# ============================================================
# LOAD VALID CONFIGURATIONS
# ============================================================

def load_configurations():

    if not ERROR_DATASET.exists():

        raise FileNotFoundError(
            f"Error dataset not found:\n"
            f"{ERROR_DATASET}"
        )

    configurations = []

    with ERROR_DATASET.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            configurations.append(
                {
                    "width": int(row["width"]),
                    "approx_bits": int(
                        row["approx_bits"]
                    ),
                    "carry_truncation": int(
                        row["carry_truncation"]
                    ),
                    "correction_depth": int(
                        row["correction_depth"]
                    )
                }
            )

    return configurations


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("YOSYS SYNTHESIS CHARACTERIZATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Check Yosys
    # --------------------------------------------------------

    yosys_path = Path(YOSYS_EXE)

    if not yosys_path.exists():

        print()
        print(
            "ERROR: Yosys executable was not found."
        )
        print()
        print(YOSYS_EXE)
        return

    print()
    print(
        f"Yosys executable: {YOSYS_EXE}"
    )

    # --------------------------------------------------------
    # Load configurations
    # --------------------------------------------------------

    try:

        configurations = load_configurations()

    except Exception as error:

        print()
        print(
            f"ERROR loading configurations: {error}"
        )
        return

    print()
    print(
        f"Configurations loaded: "
        f"{len(configurations)}"
    )

    # --------------------------------------------------------
    # Characterize designs
    # --------------------------------------------------------

    rows = []

    for config in configurations:

        width = config["width"]
        k = config["approx_bits"]
        t = config["carry_truncation"]
        c = config["correction_depth"]

        module_name = (
            f"approx_adder_w{width}"
            f"_k{k}"
            f"_t{t}"
            f"_c{c}"
        )

        rtl_file = (
            RTL_DIR
            / f"{module_name}.v"
        )

        print()
        print(
            f"Synthesizing: "
            f"k={k}, "
            f"t={t}, "
            f"c={c}"
        )

        # ----------------------------------------------------
        # Check RTL
        # ----------------------------------------------------

        if not rtl_file.exists():

            print(
                "WARNING: Missing RTL:"
            )

            print(rtl_file)

            continue

        # ----------------------------------------------------
        # Run Yosys
        # ----------------------------------------------------

        try:

            output = run_yosys(
                rtl_file,
                module_name
            )

        except subprocess.CalledProcessError as error:

            print()
            print(
                "ERROR: Yosys failed for "
                f"{module_name}"
            )

            if error.stdout:
                print()
                print("Yosys stdout:")
                print(error.stdout)

            if error.stderr:
                print()
                print("Yosys stderr:")
                print(error.stderr)

            continue

        # ----------------------------------------------------
        # Parse statistics
        # ----------------------------------------------------

        try:

            stats = parse_statistics(
                output
            )

        except RuntimeError as error:

            print()
            print(
                f"ERROR parsing statistics "
                f"for {module_name}"
            )

            print(error)

            continue

        # ----------------------------------------------------
        # Add row
        # ----------------------------------------------------

        rows.append(
            {
                "width": width,
                "approx_bits": k,
                "carry_truncation": t,
                "correction_depth": c,
                "cell_count":
                    stats["cell_count"]
            }
        )

        print(
            "Cell count: "
            f"{stats['cell_count']}"
        )

    # ========================================================
    # WRITE HARDWARE DATASET
    # ========================================================

    with HARDWARE_DATASET.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "width",
            "approx_bits",
            "carry_truncation",
            "correction_depth",
            "cell_count"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 60)
    print("YOSYS CHARACTERIZATION COMPLETE")
    print("=" * 60)

    print()
    print(
        f"Configurations loaded: "
        f"{len(configurations)}"
    )

    print(
        f"Designs synthesized: "
        f"{len(rows)}"
    )

    print()
    print(
        f"Dataset: {HARDWARE_DATASET}"
    )

    print()
    print(
        f"Reports: {RESULT_DIR}"
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()