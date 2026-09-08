#!/usr/bin/env python3
"""Solve 10x10x4 for S pentacubes and save the solution."""
import sys, time, multiprocessing as mp
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.polycube_utils import PENTACUBES, generate_placements, build_exact_cover_data
from common.algorithm_x_numba import solve

def run_solver_inner(X, placements, box_list, pieces_expected, q):
    try:
        count = 0
        for sol in solve(X, placements, box_list, solution_length=pieces_expected):
            count += 1
            if count == 1:
                q.put(("first", sol))
        q.put(("total", count))
    except Exception as e:
        q.put(("error", str(e)))

def main():
    piece = PENTACUBES["S"]
    box = (10, 10, 4)
    volume = 400
    pieces_expected = 80

    print(f"Solving {box[0]}x{box[1]}x{box[2]}...", flush=True)
    t0 = time.time()
    placements, _ = generate_placements(piece, box, break_symmetry=False)
    t1 = time.time()
    print(f"Placements: {len(placements)} [{t1-t0:.1f}s]", flush=True)

    X, box_list = build_exact_cover_data(placements, box)
    t2 = time.time()
    print(f"X built [{t2-t1:.1f}s]", flush=True)

    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    proc = ctx.Process(target=run_solver_inner, args=(X, placements, box_list, pieces_expected, q))
    proc.start()
    proc.join(timeout=7200)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        print(f"TIMEOUT after 7200s", flush=True)
    else:
        messages = []
        while not q.empty():
            messages.append(q.get())
        for kind, val in messages:
            if kind == "first":
                print(f"FOUND SOLUTION!", flush=True)
                outpath = Path("data/solutions_s_10x10x4.dat")
                with open(outpath, "w") as f:
                    f.write(f"# Polycube solutions - Numba (Box: {box}, Pieces: {pieces_expected})\n")
                    f.write("1\n")
                    clean = [idx for idx in val if idx != -1]
                    sol_str = "".join([str(placements[p_idx]) for p_idx in clean])
                    f.write(f"{sol_str}\n")
                print(f"Saved to {outpath}", flush=True)
            elif kind == "total":
                print(f"Total solutions: {val}", flush=True)
            elif kind == "error":
                print(f"Error: {val}", flush=True)

    print(f"Elapsed: {time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()