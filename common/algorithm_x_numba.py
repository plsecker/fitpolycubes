import numpy as np
from numba import njit

@njit
def solve_numba(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, max_solutions=1000000):
    """
    Numba-optimized Algorithm X.
    Using flat arrays for high performance.
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
    
    # We must copy row indices because we'll deactivate them
    rows_to_try = X_data[start:end]
    
    for r in rows_to_try:
        if not active_rows[r]:
            continue

        # Depth of solution is just count of non-negative entries
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
        
        solve_numba(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, max_solutions)
        
        # Deselect: Backtrack
        for i in deactivated_rows:
            active_rows[i] = True
        for j in deactivated_cols:
            active_cols[j] = True
        solution[depth] = -1

def solve(X_dict, Y_dict, box_list):
    """
    Wrapper to convert dictionary structures to Numba-friendly arrays and run solver.
    """
    num_rows = len(Y_dict)
    num_cols = len(box_list)
    
    # Map box tuples to integer indices
    box_to_idx = {cell: i for i, cell in enumerate(box_list)}
    
    # Convert X (cols -> rows) to CSR-like flat arrays
    X_data = []
    X_indptr = [0]
    for cell in box_list:
        rows = list(X_dict[cell])
        X_data.extend(rows)
        X_indptr.append(len(X_data))
    X_data = np.array(X_data, dtype=np.int32)
    X_indptr = np.array(X_indptr, dtype=np.int32)
    
    # Convert Y (rows -> cols) to CSR-like flat arrays
    Y_data = []
    Y_indptr = [0]
    for r in range(num_rows):
        cols = [box_to_idx[cell] for cell in Y_dict[r]]
        Y_data.extend(cols)
        Y_indptr.append(len(Y_data))
    Y_data = np.array(Y_data, dtype=np.int32)
    Y_indptr = np.array(Y_indptr, dtype=np.int32)
    
    active_cols = np.ones(num_cols, dtype=np.bool_)
    active_rows = np.ones(num_rows, dtype=np.bool_)
    solution = np.full(25, -1, dtype=np.int32)
    sol_count = np.array([0], dtype=np.int32)
    
    # Pre-allocate output for 100,000 solutions (adjustable)
    max_sols = 100000
    out_list = np.zeros(max_sols * 25, dtype=np.int32)
    
    solve_numba(X_data, X_indptr, Y_data, Y_indptr, active_cols, active_rows, solution, sol_count, out_list, max_sols)
    
    # Yield solutions back to caller
    total = sol_count[0]
    for s_idx in range(min(total, max_sols)):
        yield out_list[s_idx*25 : (s_idx+1)*25].tolist()
