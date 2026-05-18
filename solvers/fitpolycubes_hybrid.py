"""
Polycube Exact Cover Solver - Hybrid (Multiprocessing + Numba)
"""
import os

# Force Numba to use a single thread per process *before* importing it.
# This prevents thread over-subscription and core thrashing.
os.environ["NUMBA_NUM_THREADS"] = "1"

# Now it is safe to import your heavy performance libraries
import sys
import multiprocessing as mp
import numpy as np
from numba import njit

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM
from common.utils import Timer
from common.polycube_utils import generate_placements, build_exact_cover_data, filter_and_reindex_placements

#############   Numba Core  #############

@njit(nogil=True)
def solve_numba_core(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, max_solutions):
    """
    Numba-optimized Algorithm X.
    Using flat arrays for high performance.
    Runs without GIL allowing true multithreading or multiprocessing.
    """
    # Check if all columns are covered
    any_active_col = False
    for c in range(len(active_cols)):
        if active_cols[c]:
            any_active_col = True
            break
            
    if not any_active_col:
        sol_count[0] += 1
        # Store a snapshot of the solution if we have space
        if sol_count[0] <= max_solutions:
            # Flattened storage: each solution is 25 indices
            idx = (sol_count[0] - 1) * 25
            for i in range(25):
                out_list[idx + i] = solution[i]
        return

    # Choose column with fewest active rows
    best_col = -1
    min_rows = 999999

    for c in range(len(active_cols)):
        if not active_cols[c]:
            continue
            
        count = 0
        start = X_indptr[c]
        end = X_indptr[c+1]
        for r_idx in X_data[start:end]:
            if active_rows[r_idx]:
                count += 1
        
        if count < min_rows:
            min_rows = count
            best_col = c
            if count == 0: break 

    if min_rows == 0 or best_col == -1:
        return

    # Try each active row that covers the chosen column
    start = X_indptr[best_col]
    end = X_indptr[best_col+1]
    
    rows_to_try = X_data[start:end]
    
    for r in rows_to_try:
        if not active_rows[r]:
            continue

        depth = 0
        while depth < 25 and solution[depth] != -1:
            depth += 1
        solution[depth] = r
        
        # Select: Deactivate rows and columns
        deactivated_cols = []
        deactivated_rows = []
        
        r_start = Y_indptr[r]
        r_end = Y_indptr[r+1]
        for j in Y_data[r_start:r_end]:
            if active_cols[j]:
                active_cols[j] = False
                deactivated_cols.append(j)
                
                j_start = X_indptr[j]
                j_end = X_indptr[j+1]
                for i in X_data[j_start:j_end]:
                    if active_rows[i]:
                        active_rows[i] = False
                        deactivated_rows.append(i)
        
        solve_numba_core(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, max_solutions)
        
        # Deselect: Backtrack
        for i in deactivated_rows:
            active_rows[i] = True
        for j in deactivated_cols:
            active_cols[j] = True
        solution[depth] = -1

#############   Worker & Writer  #############

def solve_worker(X_data, X_indptr, Y_data, Y_indptr, row_choice, num_cols, num_rows, out_q):
    """
    Worker: start search with a single chosen row from the first column.
    """
    pid = os.getpid()
    
    # Initialize trackers for this branch
    active_cols = np.ones(num_cols, dtype=np.bool_)
    active_rows = np.ones(num_rows, dtype=np.bool_)
    solution = np.full(25, -1, dtype=np.int32)
    sol_count = np.array([0], dtype=np.int32)
    
    max_sols = 100000
    out_list = np.zeros(max_sols * 25, dtype=np.int32)

    # Apply the initial row_choice (Select)
    solution[0] = row_choice
    
    r_start = Y_indptr[row_choice]
    r_end = Y_indptr[row_choice+1]
    for j in Y_data[r_start:r_end]:
        if active_cols[j]:
            active_cols[j] = False
            
            j_start = X_indptr[j]
            j_end = X_indptr[j+1]
            for i in X_data[j_start:j_end]:
                if active_rows[i]:
                    active_rows[i] = False
                    
    # Enter Numba JIT Core
    solve_numba_core(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, max_sols)
    
    total = sol_count[0]
    if total > 0:
        print(f"[Worker {pid}] finished branch {row_choice}, found {total} solutions")
        
        # Pull solutions back to Python list to send to writer
        for s_idx in range(min(total, max_sols)):
            sol = out_list[s_idx*25 : (s_idx+1)*25]
            clean_sol = [idx for idx in sol if idx != -1]
            if len(clean_sol) == 25:
                out_q.put(clean_sol)


def writer_process(out_q, done_signal, fname, Y_dict):
    c = 0
    with open(fname, "w") as f:
        f.write("#Npentacubes (Hybrid MP+Numba)\n")
        while True:
            sol = out_q.get()
            if sol == done_signal:
                break
            c += 1
            if c % 100 == 0:
                print(f"[Writer] written {c} solutions to {fname}")
            
            sol_str = "".join([str(Y_dict[p_index]) for p_index in sol])
            f.write(f"{c}\n{sol_str}\n")
    print(f"Total combinations found: {c}")


#############   Main  #############

def main():
    p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 1]])   # N piece
    box_size = 5
    break_symmetry = True
    
    print(f"Generating placements for piece in {box_size} box...")
    with Timer() as t:
        placements, canonical_p_000 = generate_placements(p, box_size, break_symmetry=break_symmetry)
    print(f"Placements found: {len(placements)}")

    if break_symmetry and canonical_p_000:
        placements = filter_and_reindex_placements(placements, canonical_p_000)

    X0, box_list = build_exact_cover_data(placements, box_size)
    num_rows = len(placements)
    num_cols = len(box_list)

    print("Converting data structures for Numba...")
    # Map box tuples to integer indices
    box_to_idx = {cell: i for i, cell in enumerate(box_list)}
    
    # Convert X (cols -> rows) to CSR-like flat arrays
    X_data = []
    X_indptr = [0]
    for cell in box_list:
        rows = list(X0[cell])
        X_data.extend(rows)
        X_indptr.append(len(X_data))
    X_data = np.array(X_data, dtype=np.int32)
    X_indptr = np.array(X_indptr, dtype=np.int32)
    
    # Convert Y (rows -> cols) to CSR-like flat arrays
    Y_data = []
    Y_indptr = [0]
    for r in range(num_rows):
        cols = [box_to_idx[cell] for cell in placements[r]]
        Y_data.extend(cols)
        Y_indptr.append(len(Y_data))
    Y_data = np.array(Y_data, dtype=np.int32)
    Y_indptr = np.array(Y_indptr, dtype=np.int32)

    # Determine initial branches from the first column (fastest to fail)
    first_col = box_list[0]
    row_choices = list(X0[first_col])
    print(f"Parallel fan-out: {len(row_choices)} initial branches")

    fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/solutions_hybrid.dat")

    manager = mp.Manager()
    out_q = manager.Queue()
    DONE = ("__DONE__", os.getpid())

    wp = mp.Process(target=writer_process, args=(out_q, DONE, fname, placements))
    wp.start()

    num_cores = mp.cpu_count()
    print(f"Using a pool of {num_cores} workers.")
    
    print("Starting solver...")
    with Timer() as t:
        with mp.Pool(processes=num_cores) as pool:
            # We pass the flattened read-only numpy arrays which multiprocess handles efficiently
            args_list = [(X_data, X_indptr, Y_data, Y_indptr, row, num_cols, num_rows, out_q) for row in row_choices]
            pool.starmap(solve_worker, args_list)

    out_q.put(DONE)
    wp.join()

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        mp.set_start_method("spawn", force=True)
    main()
