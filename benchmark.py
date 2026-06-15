"""Run all maps and compare turns against performance benchmarks."""

import subprocess
import sys


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


def main() -> int:
    all_pass = True

    for category, maps in BENCHMARKS.items():
        print(f"\n{'=' * 50}")
        print(f"  {category.upper()}")
        print(f"{'=' * 50}")

        for filename, (drones, target) in maps.items():
            path = f"maps/{category}/{filename}"
            turns = run_map(path)
            status = "✅" if turns <= target else "❌"
            if turns > target:
                all_pass = False
            print(f"  {status} {filename:<40} {turns:>3}"
                  f" turns  (target ≤{target})")

    print(f"\n{'=' * 50}")
    if all_pass:
        print("  ✅ All benchmarks passed!")
    else:
        print("  ❌ Some benchmarks failed")
    print(f"{'=' * 50}\n")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
