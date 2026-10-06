import sys
import csv
import re
import subprocess
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT PATHS
# ============================================================

RTL_DIR = PROJECT_ROOT / "rtl"
TEST_DIR = PROJECT_ROOT / "tests"
DATASET_DIR = PROJECT_ROOT / "datasets"

RTL_DIR.mkdir(parents=True, exist_ok=True)
TEST_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# PARAMETERS
# ============================================================

WIDTH = 16

APPROX_BITS_VALUES = [0, 2, 4, 6, 8]

CARRY_TRUNCATION_VALUES = [0, 2, 4, 6, 8]

CORRECTION_DEPTH_VALUES = [0, 1, 2, 4]

NUM_VECTORS = 1000


# ============================================================
# GENERATE VERILOG
# ============================================================

def generate_design(k, t, c):

    module_name = (
        f"approx_adder_w{WIDTH}"
        f"_k{k}"
        f"_t{t}"
        f"_c{c}"
    )

    output_file = (
        RTL_DIR /
        f"{module_name}.v"
    )

    from src.generator.adder_generator import (
        generate_approximate_adder
    )

    generate_approximate_adder(
        width=WIDTH,
        approx_bits=k,
        carry_truncation=t,
        correction_depth=c,
        output_file=str(output_file)
    )

    return module_name, output_file


# ============================================================
# CREATE TESTBENCH
# ============================================================

def create_testbench(module_name):

    testbench = f"""
`timescale 1ns/1ps

module test_approx_adder;

    reg [15:0] a;
    reg [15:0] b;
    reg cin;

    wire [15:0] sum;
    wire cout;

    integer i;
    integer exact_result;
    integer approx_result;
    integer error;

    integer error_count;
    integer total_error;
    integer max_error;

    {module_name} dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    initial begin

        error_count = 0;
        total_error = 0;
        max_error = 0;

        cin = 0;

        for (i = 0; i < {NUM_VECTORS}; i = i + 1) begin

            a = (i * 37) % 65536;
            b = (i * 91) % 65536;

            #1;

            exact_result = a + b;
            approx_result = {{cout, sum}};

            error = exact_result - approx_result;

            if (error < 0)
                error = -error;

            if (error != 0)
                error_count = error_count + 1;

            total_error = total_error + error;

            if (error > max_error)
                max_error = error;

        end

        $display(
            "RESULT error_count=%0d total_error=%0d max_error=%0d",
            error_count,
            total_error,
            max_error
        );

        $finish;

    end

endmodule
"""

    testbench_file = TEST_DIR / "generated_tb.v"

    testbench_file.write_text(
        testbench,
        encoding="utf-8"
    )

    return testbench_file


# ============================================================
# RUN ICARUS
# ============================================================

def run_simulation(rtl_file, testbench_file):

    output_file = TEST_DIR / "auto_sim.vvp"

    compile_command = [
        "iverilog",
        "-o",
        str(output_file),
        str(rtl_file),
        str(testbench_file)
    ]

    compile_result = subprocess.run(
        compile_command,
        check=True,
        capture_output=True,
        text=True
    )

    result = subprocess.run(
        ["vvp", str(output_file)],
        check=True,
        capture_output=True,
        text=True
    )

    return result.stdout


# ============================================================
# PARSE RESULTS
# ============================================================

def parse_results(output):

    pattern = (
        r"RESULT "
        r"error_count=(\d+) "
        r"total_error=(\d+) "
        r"max_error=(\d+)"
    )

    match = re.search(pattern, output)

    if not match:
        raise RuntimeError(
            "Could not parse simulation output."
        )

    error_count = int(match.group(1))
    total_error = int(match.group(2))
    max_error = int(match.group(3))

    return error_count, total_error, max_error


# ============================================================
# MAIN CHARACTERIZATION
# ============================================================

def main():

    print("=" * 60)
    print("AUTOMATED APPROXIMATE ADDER CHARACTERIZATION")
    print("=" * 60)

    dataset_file = (
        DATASET_DIR /
        "characterization.csv"
    )

    rows = []

    # --------------------------------------------------------
    # Determine valid design combinations
    # --------------------------------------------------------

    valid_designs = []

    for k in APPROX_BITS_VALUES:

        for t in CARRY_TRUNCATION_VALUES:

            # Carry truncation cannot exceed
            # the approximate region.
            if t > k:
                continue

            for c in CORRECTION_DEPTH_VALUES:

                # Correction depth cannot exceed
                # the approximate region.
                if c > k:
                    continue

                valid_designs.append(
                    (k, t, c)
                )

    total_designs = len(valid_designs)

    print()
    print(f"Valid designs : {total_designs}")
    print()

    # --------------------------------------------------------
    # Characterize every valid design
    # --------------------------------------------------------

    for current, (k, t, c) in enumerate(
        valid_designs,
        start=1
    ):

        print(
            f"[{current}/{total_designs}] "
            f"k={k}, t={t}, c={c}"
        )

        # ----------------------------------------------------
        # Generate RTL
        # ----------------------------------------------------

        module_name, rtl_file = generate_design(
            k,
            t,
            c
        )

        # ----------------------------------------------------
        # Generate testbench
        # ----------------------------------------------------

        testbench_file = create_testbench(
            module_name
        )

        # ----------------------------------------------------
        # Run Icarus
        # ----------------------------------------------------

        output = run_simulation(
            rtl_file,
            testbench_file
        )

        # ----------------------------------------------------
        # Parse results
        # ----------------------------------------------------

        error_count, total_error, max_error = (
            parse_results(output)
        )

        # ----------------------------------------------------
        # Calculate metrics
        # ----------------------------------------------------

        error_rate = (
            error_count / NUM_VECTORS
        )

        med = (
            total_error / NUM_VECTORS
        )

        max_possible_error = (
            (2 ** WIDTH) - 1
        )

        nmed = (
            med / max_possible_error
        )

        # ----------------------------------------------------
        # Store row
        # ----------------------------------------------------

        row = {
            "width": WIDTH,
            "approx_bits": k,
            "carry_truncation": t,
            "correction_depth": c,
            "num_vectors": NUM_VECTORS,
            "error_count": error_count,
            "error_rate": error_rate,
            "total_error": total_error,
            "MED": med,
            "NMED": nmed,
            "max_error": max_error
        }

        rows.append(row)

        # ----------------------------------------------------
        # Display metrics
        # ----------------------------------------------------

        print(
            f"    ER={error_rate:.6f}, "
            f"MED={med:.4f}, "
            f"NMED={nmed:.8f}, "
            f"MAX={max_error}"
        )

    # ========================================================
    # WRITE CSV
    # ========================================================

    fieldnames = [
        "width",
        "approx_bits",
        "carry_truncation",
        "correction_depth",
        "num_vectors",
        "error_count",
        "error_rate",
        "total_error",
        "MED",
        "NMED",
        "max_error"
    ]

    with dataset_file.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("CHARACTERIZATION COMPLETE")
    print("=" * 60)

    print()
    print(f"Designs characterized : {total_designs}")
    print(f"Vectors per design   : {NUM_VECTORS}")
    print(f"Dataset               : {dataset_file}")
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()