"""
Polycube Exact Cover Solver — Multiprocess Version
"""

import os
import sys
import multiprocessing as mp
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM
from common.algorithm_x import solve, select, deselect


#############   Parallel worker & writer  #############

def solve_worker(base_X, Y, row_choice, out_q):
    """
    Worker: start search with a single chosen row from the first column.
    """
    pid = os.getpid()
    print(f"[Worker {pid}] starting with row {row_choice}")

    # Local copy of X
    X = {k: set(v) for k, v in base_X.items()}

    # Apply the chosen row
    solution = [row_choice]
    select(X, Y, row_choice)

    # Continue search
    count = 0
    for sol in solve(X, Y, solution):
        count += 1
        out_q.put(sol)
        # Print every 100 solutions
        if count % 100 == 0:
            print(f"[Worker {pid}] found {count} solutions so far (row {row_choice})")

    print(f"[Worker {pid}] finished, total {count} solutions from row {row_choice}")


def writer_process(out_q, done_signal, fname, Y):
    c = 0
    with open(fname, "w") as f:
        f.write("# Polycube placements (exact cover solutions)\n")
        while True:
            sol = out_q.get()
            if sol == done_signal:
                break
            c += 1
            if c % 100 == 0:
                print(f"[Writer] written {c} solutions to {fname}")
            f.write(f"\n{c}\n")
            for p_index in sol:
                f.write(f"{Y[p_index]}\n")
    print(f"Total combinations: {c}")


#############   Helper: split at first column  #############

def frontier_splits(X0, Y):
    """
    Return a list of starting rows from the first branching column.
    """
    if not X0:
        return []
    c = min(X0, key=lambda col: len(X0[col]))
    return list(X0[c])   # list of row_ids


#############   Main  #############

def main():
    # Define all 12 pentacubes (free pentacubes up to reflection)
    # Each as np.array of 5 coordinate triples starting from origin
    PENTACUBES = {
        "F": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 0]]),
        "I": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0]]),
        "L": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [3, 1, 0]]),
        "N": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [3, 1, 0]]),
        "P": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]]),
        "T": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 0, 1]]),
        "U": np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0]]),
        "V": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [0, 2, 0]]),
        "W": np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]),
        "X": np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [1, 2, 0], [2, 1, 0]]),
        "Y": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [2, 1, 0]]),
        "Z": np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]),
    }
    p = PENTACUBES['N']

    box = {(x, y, z) for z in range(5) for y in range(5) for x in range(5)}

    # Generate placements
    Y = {}
    count = 0
    for cube in box:
        base = np.array(cube)
        for rotindex in range(24):
            rp = base + p @ RM[rotindex].T
            rpl = rp.tolist()
            if all(tuple(pt) in box for pt in rpl):
                Y[count] = list(map(tuple, rpl))
                count += 1
    print("Placements found:", count)

    # Build X
    X0 = {cell: set() for cell in box}
    for row_id, cells in Y.items():
        for cell in cells:
            X0[cell].add(row_id)

    # Split work
    row_choices = frontier_splits(X0, Y)
    print(f"Parallel fan-out: {len(row_choices)} workers")

    # Output file
    fname = "data/solutions_mp.dat"

    # Manager queue
    manager = mp.Manager()
    out_q = manager.Queue()
    DONE = ("__DONE__", os.getpid())

    # Writer process
    wp = mp.Process(target=writer_process, args=(out_q, DONE, fname, Y))
    wp.start()

    # Launch workers
    procs = []
    for row in row_choices:
        pproc = mp.Process(target=solve_worker, args=(X0, Y, row, out_q))
        pproc.start()
        procs.append(pproc)

    # Wait for workers
    for pproc in procs:
        pproc.join()

    # Tell writer to finish
    out_q.put(DONE)
    wp.join()

    with open(fname, "a") as f:
        f.write(f"\nElements in Y: {len(Y)}\n")


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        mp.set_start_method("spawn", force=True)
    main()
