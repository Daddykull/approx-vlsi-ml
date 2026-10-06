import subprocess
import re
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RTL_DIR = PROJECT_ROOT / "rtl"
TEST_DIR = PROJECT_ROOT / "tests"
SIM_DIR = PROJECT_ROOT / "sim"


# ============================================================
# DESIGN PARAMETERS
# ============================================================

WIDTH = 16
APPROX_BITS = 4
CARRY_TRUNCATION = 2
CORRECTION_DEPTH = 1


# ============================================================
# FILE PATHS
# ============================================================

RTL_FILE = RTL_DIR / "generated_adder.v"
TESTBENCH = TEST_DIR / "test_approx_adder.v"
SIM_FILE = SIM_DIR / "approx_adder.vvp"


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("Approximate VLSI ML Design Automation Framework")
print("=" * 60)

print(f"Adder width: {WIDTH}")
print(f"Approximate bits : {APPROX_BITS}")
print(f"Carry truncation : {CARRY_TRUNCATION}")
print(f"Correction depth : {CORRECTION_DEPTH}")
print()


# ============================================================
# CHECK DIRECTORIES
# ============================================================

RTL_DIR.mkdir(exist_ok=True)
SIM_DIR.mkdir(exist_ok=True)


# ============================================================
# STAGE 1 — RTL GENERATION
# ============================================================

print("[1/3] RTL Generation")
print("-" * 60)

# Run the existing RTL generator
generator_script = PROJECT_ROOT / "src" / "generator" / "generate_rtl.py"

if generator_script.exists():

    result = subprocess.run(
        [
            "python",
            str(generator_script),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("RTL generation failed.")
        print(result.stderr)
        raise SystemExit(1)

else:
    print("Generator script not found.")
    print(f"Expected: {generator_script}")
    raise SystemExit(1)


if not RTL_FILE.exists():
    print("RTL generation failed: generated_adder.v not found.")
    raise SystemExit(1)

print(f"RTL generated: {RTL_FILE}")
print()


# ============================================================
# STAGE 2 — ICARUS VERILOG COMPILATION
# ============================================================

print("[2/3] Icarus Verilog Simulation")
print("-" * 60)

compile_cmd = [
    "iverilog",
    "-o",
    str(SIM_FILE),
    str(TESTBENCH),
    str(RTL_FILE),
]

print("Compiling RTL...")

compile_result = subprocess.run(
    compile_cmd,
    capture_output=True,
    text=True,
)

if compile_result.returncode != 0:
    print("Icarus compilation failed.")
    print(compile_result.stderr)
    raise SystemExit(1)

print("Compilation successful.")


# ============================================================
# RUN SIMULATION
# ============================================================

print("Running simulation...")

simulation_result = subprocess.run(
    [
        "vvp",
        str(SIM_FILE),
    ],
    capture_output=True,
    text=True,
)

if simulation_result.returncode != 0:
    print("Simulation failed.")
    print(simulation_result.stderr)
    raise SystemExit(1)

simulation_output = simulation_result.stdout

print()
print(simulation_output)


# ============================================================
# STAGE 3 — EXTRACT ERROR METRICS
# ============================================================

print("[3/3] Error Characterization")
print("-" * 60)

patterns = {
    "vectors": r"Number of vectors\s*:\s*(\d+)",
    "error_vectors": r"Error vectors\s*:\s*(\d+)",
    "total_error": r"Total error\s*:\s*(\d+)",
    "maximum_error": r"Maximum error\s*:\s*(\d+)",
}


metrics = {}

for name, pattern in patterns.items():

    match = re.search(pattern, simulation_output)

    if match:
        metrics[name] = int(match.group(1))
    else:
        metrics[name] = None


# ============================================================
# DISPLAY RESULTS
# ============================================================

print(f"Number of vectors : {metrics['vectors']}")
print(f"Error vectors     : {metrics['error_vectors']}")
print(f"Total error       : {metrics['total_error']}")
print(f"Maximum error     : {metrics['maximum_error']}")


# ============================================================
# ERROR RATE
# ============================================================

if metrics["vectors"] and metrics["error_vectors"] is not None:

    error_rate = (
        metrics["error_vectors"]
        / metrics["vectors"]
    )

    print(f"Error rate        : {error_rate:.4f}")


# ============================================================
# PIPELINE STATUS
# ============================================================

print()
print("=" * 60)
print("PIPELINE STATUS")
print("=" * 60)

print("Python parameters       [OK]")
print("RTL generation          [OK]")
print("Icarus compilation     [OK]")
print("Icarus simulation       [OK]")
print("Error characterization  [OK]")

print()
print("Next stage:")
print("Dataset generation → ML prediction → Pareto optimization")
print("=" * 60)