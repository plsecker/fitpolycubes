#!/usr/bin/env python3
"""
Direct exact-cover search for S-pentacube a×b×z boxes with timeout.

Uses the numba Algorithm X solver. Establishes:
- solution count (if the search completes);
- whether a solution was found quickly;
- elapsed time;
- whether the search completed exhaustively or timed out.

Usage:
    python3 tools/frontier/solve_box_numba.py --a 5 --b 8 --z 6 --timeout 300
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from common.algorithm_x_numba import solve
from common.polycube_utils import PENTACUBES, build_exact_cover_data, generate_placements


def _run_solver(X, placements, box_list, pieces_expected, q):
    """Run the numba solver and report first solution + total count."""
    try:
        count = 0
        for sol in solve(X, placements, box_list, solution_length=pieces_expected):
            count += 1
            if count == 1:
                q.put(("first", sol))
        q.put(("total", count))
    except Exception as e:
        q.put(("error", str(e)))


def solve_box(a: int, b: int, z: int, timeout: float = 300.0) -> dict:
    """Solve a×b×z for S pentacubes with a wall-clock timeout.
    
    The numba solver is synchronous; we run it and check elapsed time
    periodically by running it in a way that can be interrupted.
    Returns a dict describing the outcome.
    """
    piece = PENTACUBES["S"]
    box = (a, b, z)
    volume = a * b * z
    pieces_expected = volume // 5

    if volume % 5 != 0:
        return {
            "a": a, "b": b, "z": z,
            "volume": volume,
            "pieces_expected": None,
            "solutions": None,
            "completed": False,
            "elapsed": 0.0,
            "note": "volume not divisible by 5",
        }

    t0 = time.time()
    placements, _ = generate_placements(piece, box, break_symmetry=False)
    t1 = time.time()
    X, box_list = build_exact_cover_data(placements, box)
    t2 = time.time()

    result = {
        "a": a, "b": b, "z": z,
        "volume": volume,
        "pieces_expected": pieces_expected,
        "placements": len(placements),
        "solutions": None,
        "completed": False,
        "elapsed": 0.0,
        "note": "",
    }

    # Run the numba solver in a subprocess so we can enforce a wall-clock timeout
    import multiprocessing as mp
    ctx = mp.get_context("spawn")

    q = ctx.Queue()
    proc = ctx.Process(target=_run_solver, args=(X, placements, box_list, pieces_expected, q))
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        result["completed"] = False
        result["elapsed"] = time.time() - t0
        result["note"] = f"TIMEOUT after {timeout}s"
        return result

    messages = []
    while not q.empty():
        messages.append(q.get())

    elapsed = time.time() - t0
    result["elapsed"] = elapsed

    first_sol = None
    total = None
    for kind, val in messages:
        if kind == "first":
            first_sol = val
        elif kind == "total":
            total = val
        elif kind == "error":
            result["note"] = f"ERROR: {val}"
            return result

    result["solutions"] = total
    result["completed"] = True
    result["note"] = f"generate={t1-t0:.1f}s build={t2-t1:.1f}s solve={elapsed-(t2-t0):.1f}s"
    if first_sol is not None:
        result["first_solution"] = first_sol
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--z", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()

    result = solve_box(args.a, args.b, args.z, args.timeout)
    for k, v in result.items():
        if k == "first_solution":
            continue
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())