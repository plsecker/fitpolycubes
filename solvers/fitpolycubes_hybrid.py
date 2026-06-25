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
from common.polycube_utils import (generate_placements, build_exact_cover_data, 
                                   filter_and_reindex_placements, PENTACUBES)

#############   Numba Core  #############

@njit(nogil=True)
def solve_numba_core(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, solution_length, max_solutions, nodes_visited):
    """
    Numba-optimized Algorithm X.
    Using flat arrays for high performance.
    Runs without GIL allowing true multithreading or multiprocessing.
    """
    nodes_visited[0] += 1
    if nodes_visited[0] % 1000000 == 0:
        print("[Worker] Branch path:", solution[0], solution[1], solution[2], solution[3], "- Visited", nodes_visited[0], "nodes, found", sol_count[0], "solutions")

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
            # Flattened storage
            idx = (sol_count[0] - 1) * solution_length
            for i in range(solution_length):
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
        while depth < solution_length and solution[depth] != -1:
            depth += 1
        
        if depth >= solution_length:
            continue

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
        
        solve_numba_core(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, solution_length, max_solutions, nodes_visited)
        
        # Deselect: Backtrack
        for i in deactivated_rows:
            active_rows[i] = True
        for j in deactivated_cols:
            active_cols[j] = True
        solution[depth] = -1

#############   Worker & Writer  #############

global_out_q = None

def init_worker(q):
    global global_out_q
    global_out_q = q

def solve_worker(X_data, X_indptr, Y_data, Y_indptr, task_rows, num_cols, num_rows, solution_length, max_solutions_global):
    """
    Worker: start search with a list of chosen rows (a search state).
    """
    pid = os.getpid()
    
    # Initialize trackers for this branch
    active_cols = np.ones(num_cols, dtype=np.bool_)
    active_rows = np.ones(num_rows, dtype=np.bool_)
    solution = np.full(solution_length, -1, dtype=np.int32)
    sol_count = np.array([0], dtype=np.int32)
    nodes_visited = np.array([0], dtype=np.int64)
    
    max_sols = 100000
    out_list = np.zeros(max_sols * solution_length, dtype=np.int32)

    # Apply the sequence of row choices (Select)
    for depth, r in enumerate(task_rows):
        solution[depth] = r
        
        r_start = Y_indptr[r]
        r_end = Y_indptr[r+1]
        for j in Y_data[r_start:r_end]:
            if active_cols[j]:
                active_cols[j] = False
                
                j_start = X_indptr[j]
                j_end = X_indptr[j+1]
                for i in X_data[j_start:j_end]:
                    if active_rows[i]:
                        active_rows[i] = False
                    
    # Announce start of this task so progress is visible immediately
    print(f"[Worker {pid}] STARTING task {task_rows}")

    # Enter Numba JIT Core
    solve_numba_core(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, solution_length, max_sols, nodes_visited)
    
    total = sol_count[0]
    print(f"[Worker {pid}] finished branch {task_rows}, found {total} solutions (visited {nodes_visited[0]} nodes)")
    
    if total > 0:
        # Pull solutions back to Python list to send to writer
        for s_idx in range(min(total, max_sols)):
            sol = out_list[s_idx*solution_length : (s_idx+1)*solution_length]
            clean_sol = [idx for idx in sol if idx != -1]
            if len(clean_sol) == solution_length:
                global_out_q.put(clean_sol)


def worker_wrapper(args):
    """
    Wrapper to allow pool.imap_unordered to call solve_worker with multiple arguments.
    """
    return solve_worker(*args)


def writer_process(out_q, done_signal, fname, Y_dict, expected_pieces, max_solutions):
    c = 0
    with open(fname, "w") as f:
        f.write(f"# Polycube solutions - Hybrid MP+Numba (Pieces: {expected_pieces})\n")
        while True:
            sol = out_q.get()
            if sol == done_signal:
                break
            c += 1
            if (c % 10) == 0:
                print(f"Solutions found so far: {c}")
            
            sol_str = "".join([str(Y_dict[p_index]) for p_index in sol])
            f.write(f"{c}\n{sol_str}\n")
            
            if max_solutions > 0 and c >= max_solutions:
                print(f"Reached maximum solutions limit ({max_solutions}). Stopping.")
                break
    print(f"Total combinations found: {c}")


def generate_tasks_recursive(X0, placements, box_list, active_cols, active_rows, current_sol, depth, max_depth, target_tasks, tasks):
    """
    Recursively generates exact cover task branches using Algorithm X column selection heuristic.
    """
    if len(tasks) >= target_tasks or depth >= max_depth:
        tasks.append(list(current_sol))
        return

    # Check if any columns are still active
    any_active = False
    for col in box_list:
        if active_cols[col]:
            any_active = True
            break
    if not any_active:
        tasks.append(list(current_sol))
        return

    # Choose column with fewest active rows (Algorithm X heuristic)
    best_col = None
    min_rows = 999999
    for col in box_list:
        if not active_cols[col]:
            continue
        count = 0
        for r in X0[col]:
            if active_rows[r]:
                count += 1
        if count < min_rows:
            min_rows = count
            best_col = col
            if min_rows == 0:
                break

    if min_rows == 0 or best_col is None:
        # Dead-end pruning
        return

    # Try each active row that covers the chosen column
    rows_to_try = [r for r in X0[best_col] if active_rows[r]]
    for r in rows_to_try:
        current_sol.append(r)
        
        deactivated_cols = []
        deactivated_rows = []
        
        for col in placements[r]:
            if active_cols[col]:
                active_cols[col] = False
                deactivated_cols.append(col)
                for row_idx in X0[col]:
                    if active_rows[row_idx]:
                        active_rows[row_idx] = False
                        deactivated_rows.append(row_idx)
                        
        generate_tasks_recursive(X0, placements, box_list, active_cols, active_rows, current_sol, depth + 1, max_depth, target_tasks, tasks)
        
        # Backtrack
        for row_idx in deactivated_rows:
            active_rows[row_idx] = True
        for col in deactivated_cols:
            active_cols[col] = True
        current_sol.pop()


#############   Main  #############

def main(args):
    # Normalize input to uppercase for lookup
    piece_key = args.piece.upper()
    
    if piece_key not in PENTACUBES:
        print(f"Error: Piece '{args.piece}' not found in PENTACUBES.")
        print(f"Available pieces: {', '.join(sorted(PENTACUBES.keys()))}")
        sys.exit(1)
        
    p = PENTACUBES[piece_key]
    box_size = tuple(args.box) if len(args.box) == 3 else (args.box[0], args.box[0], args.box[0])
    
    # Calculate expected number of pieces
    volume = box_size[0] * box_size[1] * box_size[2]
    num_cubes_per_piece = len(p)
    expected_pieces = volume // num_cubes_per_piece

    print(f"Solving for {args.piece} pentacube (Hybrid solver)...")
    print(f"Box size: {box_size}")
    
    print(f"Generating placements for piece in {box_size} box...")
    with Timer() as t:
        placements, canonical_p_000 = generate_placements(p, box_size, break_symmetry=args.symmetry)
    print(f"Placements found: {len(placements)}")

    if args.symmetry and canonical_p_000:
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

    # Determine initial parallel branches using recursive task generator
    num_cores = mp.cpu_count()
    target_tasks = num_cores * 16
    max_depth = 4

    print("Generating parallel tasks recursively...")
    active_cols = {cell: True for cell in box_list}
    active_rows = {r: True for r in range(num_rows)}
    tasks = []
    generate_tasks_recursive(X0, placements, box_list, active_cols, active_rows, [], 0, max_depth, target_tasks, tasks)
    print(f"Generated {len(tasks)} parallel tasks (target: {target_tasks}, max depth: {max_depth}).")

    box_str = "x".join(map(str, box_size))
    fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"data/solutions_hybrid_{piece_key.lower()}_{box_str}.dat")

    out_q = mp.Queue()
    DONE = ("__DONE__", os.getpid())

    wp = mp.Process(target=writer_process, args=(out_q, DONE, fname, placements, expected_pieces, args.max_solutions))
    wp.start()

    print(f"Using a pool of {num_cores} workers.")
    
    print("Starting solver...")
    with Timer() as t:
        if args.profile_single:
            # Sequential execution for profiling
            init_worker(out_q)
            for task in tasks:
                worker_wrapper((X_data, X_indptr, Y_data, Y_indptr, task, num_cols, num_rows, expected_pieces, args.max_solutions))
        else:
            with mp.Pool(processes=num_cores, initializer=init_worker, initargs=(out_q,)) as pool:
                # We pass the flattened read-only numpy arrays which multiprocess handles efficiently
                args_list = [(X_data, X_indptr, Y_data, Y_indptr, task, num_cols, num_rows, expected_pieces, args.max_solutions) for task in tasks]
                for _ in pool.imap_unordered(worker_wrapper, args_list, chunksize=1):
                    pass

    out_q.put(DONE)
    wp.join()

if __name__ == "__main__":
    import argparse
    import cProfile
    import pstats

    parser = argparse.ArgumentParser(description="Polycube Exact Cover Solver (Hybrid)")
    parser.add_argument("piece", nargs="?", default="N", help="Piece name (e.g. N, Y, L)")
    parser.add_argument("--box", nargs="+", type=int, default=[5, 5, 5], help="Box dimensions (e.g. 5 5 5 or 4 4 5)")
    parser.add_argument("--no-symmetry", action="store_false", dest="symmetry", help="Disable symmetry breaking")
    parser.add_argument("--max-solutions", type=int, default=0, help="Stop after finding N solutions (0 = no limit)")
    parser.add_argument("--profile", action="store_true", help="Enable profiling and save to profile.prof")
    parser.add_argument("--profile-single", action="store_true", help="Enable sequential profiling and save to profile.prof")
    parser.set_defaults(symmetry=True)

    # We need to parse args here to check for --profile before calling main()
    # Note: main() also parses args, so we should pass the parsed args or re-parse
    args = parser.parse_args()

    if sys.platform.startswith("win"):
        mp.set_start_method("spawn", force=True)

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()
        main(args)
        profiler.disable()
        profiler.dump_stats("profile.prof")
        print("\nProfile written to profile.prof")
    elif args.profile_single:
        profiler = cProfile.Profile()
        profiler.enable()
        main(args)
        profiler.disable()
        profiler.dump_stats("profile.prof")
        print("\nProfile written to profile.prof")
    else:
        main(args)
