#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLVER = ROOT / "solvers" / "fitpolycubes_hybrid.py"

WORKERS = "4"

BOXES = [
    (2, 2, 5),
    (2, 2, 10),
    (2, 2, 15),

    (2, 3, 5),
    (2, 3, 10),
    (2, 3, 15),

    (2, 4, 5),

    (2, 5, 5),
    (2, 5, 7),

    (3, 3, 5),
    (3, 3, 10),
    (3, 3, 15),

    (3, 5, 5),
    (3, 5, 6),
    (3, 5, 7),
]


def solve(box):
    cmd = [
        sys.executable,
        str(SOLVER),
        "y",
        "--box",
        *(str(x) for x in box),
        "--workers",
        WORKERS,
    ]

    print("=" * 72)
    print(f"Testing {box[0]}x{box[1]}x{box[2]}")

    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    stdout = result.stdout
    stderr = result.stderr

    if result.returncode != 0:
        verdict = "ERROR"

    elif "Total combinations found: 0" in stdout:
        verdict = "NO SOLUTIONS"

    elif "Total combinations found:" in stdout:
        verdict = "HAS SOLUTIONS"

    else:
        verdict = "UNKNOWN"

    print(verdict)

    print("\nLast output:")
    tail = "\n".join(stdout.splitlines()[-8:])
    if tail:
        print(tail)

    if stderr:
        print("\nSTDERR:")
        print(stderr)

    return verdict


def main():
    impossible = []
    solved = []
    errors = []

    for box in BOXES:
        verdict = solve(box)

        if verdict == "NO SOLUTIONS":
            impossible.append(box)
        elif verdict == "HAS SOLUTIONS":
            solved.append(box)
        else:
            errors.append(box)

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print("\nNo solutions:")
    for b in impossible:
        print(f"  {b[0]}x{b[1]}x{b[2]}")

    print("\nHas solutions:")
    for b in solved:
        print(f"  {b[0]}x{b[1]}x{b[2]}")

    print("\nErrors:")
    for b in errors:
        print(f"  {b[0]}x{b[1]}x{b[2]}")


if __name__ == "__main__":
    main()