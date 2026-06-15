"""Run all maps and compare turns against performance benchmarks."""

import subprocess
import sys

import pytest

BENCHMARKS = {
    "easy": {
        "01_linear_path.txt": (2, 6),
        "02_simple_fork.txt": (4, 8),
        "03_basic_capacity.txt": (4, 6),
    },
    "medium": {
        "01_dead_end_trap.txt": (5, 12),
        "02_circular_loop.txt": (6, 15),
        "03_priority_puzzle.txt": (5, 12),
    },
    "hard": {
        "01_maze_nightmare.txt": (8, 30),
        "02_capacity_hell.txt": (12, 35),
        "03_ultimate_challenge.txt": (15, 45),
    },
    "challenger": {
        "01_the_impossible_dream.txt": (25, 45),
    },
}


def run_map(path: str) -> int:
    result = subprocess.run(
        [sys.executable, "main.py", path],
        capture_output=True, text=True,
    )
    lines = [line for line in result.stdout.split("\n") if line.strip()]
    return len(lines)


test_cases = []

for category, maps in BENCHMARKS.items():
    for filename, (drones, target) in maps.items():
        path = f"maps/{category}/{filename}"
        test_cases.append((path, target))


@pytest.mark.parametrize("path,target", test_cases)
def test_benchmarks(path, target):
    turns = run_map(path)

# Final condition and error message in case of failure

    assert turns <= target, (
        f"{path}: obtuvo {turns} turnos "
        f"(objetivo <= {target})"
    )
