"""
Polycube Exact Cover Solver - Optimized Multiprocess Version
"""

import os
import sys
import multiprocessing as mp
import numpy as np

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM
from common.algorithm_x_fast import solve, select
from common.utils import Timer
from common.polycube_utils import (generate_placements, build_exact_cover_data, 
                                   filter_and_reindex_placements, PENTACUBES)

#############   Parallel worker & writer  #############

def solve_worker(X, Y, row_choice, active_cols_init, active_rows_init, out_q):
    """
    Worker: start search with a single chosen row from the first column.
    Uses boolean mask optimization for speed.
    """
    pid = os.getpid()
    
    # Create local copies of trackers
    active_cols = set(active_cols_init)
    active_rows = list(active_rows_init)

    # Apply the chosen starting row
    solution = [row_choice]
    select(X, Y, active_cols, active_rows, row_choice)

    # Continue search
    count = 0
    for sol in solve(X, Y, active_cols, active_rows, solution):
        count += 1
        out_q.put(sol)
        if count % 100 == 0:
            print(f"[Worker {pid}] found {count} solutions so far (start row {row_choice})")


def writer_process(out_q, done_signal, fname, Y):
    """
    Single process dedicated to writing solutions to disk in the standard format.
    """
    c = 0
    with open(fname, "w") as f:
        f.write("#Npentacubes (Multiprocess)\n")
        while True:
            sol = out_q.get()
            if sol == done_signal:
                break
            c += 1
            if c % 100 == 0:
                print(f"[Writer] written {c} solutions to {fname}")
            
            sol_str = "".join([str(Y[p_index]) for p_index in sol])
            f.write(f"{c}\n{sol_str}\n")
    print(f"Total combinations found: {c}")


#############   Helper: split at first column  #############

def frontier_splits(X0):
    """
    Return a list of starting rows from the first branching column.
    """
    if not X0:
        return []
    c = min(X0, key=lambda col: len(X0[col]))
    return list(X0[c])


#############   Main  #############

def main():
    piece_name = sys.argv[1] if len(sys.argv) > 1 else "P"
    if piece_name not in PENTACUBES:
        print(f"Error: Piece '{piece_name}' not found in PENTACUBES.")
        print(f"Available pieces: {', '.join(sorted(PENTACUBES.keys()))}")
        sys.exit(1)
        
    p = PENTACUBES[piece_name]
    print(f"Solving for {piece_name} pentacube (MP solver)...")
    
    box_size = 5
    break_symmetry = True
    
    print(f"Generating placements for piece in {box_size} box...")
    with Timer() as t:
        placements, canonical_p_000 = generate_placements(p, box_size, break_symmetry=break_symmetry)
    print(f"Placements found: {len(placements)}")

    if break_symmetry and canonical_p_000:
        placements = filter_and_reindex_placements(placements, canonical_p_000)

    X0, box_list = build_exact_cover_data(placements, box_size)

    # Split work
    row_choices = frontier_splits(X0)
    print(f"Parallel fan-out: {len(row_choices)} initial branches")

    active_rows_init = [True] * len(placements)
    active_cols_init = set(box_list)

    # Output file
    fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"data/solutions_mp_{piece_name.lower()}.dat")

    # Manager for queue
    manager = mp.Manager()
    out_q = manager.Queue()
    DONE = ("__DONE__", os.getpid())

    # Start writer
    wp = mp.Process(target=writer_process, args=(out_q, DONE, fname, placements))
    wp.start()

    # Use a Pool to manage worker processes
    num_cores = mp.cpu_count()
    print(f"Using a pool of {num_cores} workers.")
    
    print("Starting solver...")
    with Timer() as t:
        with mp.Pool(processes=num_cores) as pool:
            # Prepare arguments for starmap
            args_list = [(X0, placements, row, active_cols_init, active_rows_init, out_q) for row in row_choices]
            pool.starmap(solve_worker, args_list)

    # Signal writer to finish
    out_q.put(DONE)
    wp.join()


if __name__ == "__main__":
    # Support for Windows (spawn) and Linux (fork)
    if sys.platform.startswith("win"):
        mp.set_start_method("spawn", force=True)
    main()

