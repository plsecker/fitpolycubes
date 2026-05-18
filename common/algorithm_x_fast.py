"""
Optimized Algorithm X with Boolean Masks (Non-mutating)
"""

def solve(X, Y, active_cols, active_rows, solution=None):
    if solution is None:
        solution = []

    # If no active columns remain, we found a solution
    if not active_cols:
        yield list(solution)
        return

    # Choose the active column with the fewest active rows
    best_col = None
    min_rows = float('inf')

    for c in active_cols:
        count = 0
        for r_idx in X[c]:
            if active_rows[r_idx]:
                count += 1
        
        if count < min_rows:
            min_rows = count
            best_col = c
            if count == 0: break 

    if min_rows == 0 or best_col is None:
        return

    # Try each active row that covers the chosen column
    for r in list(X[best_col]):
        if not active_rows[r]:
            continue

        solution.append(r)
        
        # Deactivate rows and columns
        cols_deactivated, rows_deactivated = select(X, Y, active_cols, active_rows, r)
        
        yield from solve(X, Y, active_cols, active_rows, solution)
        
        # Backtrack: reactivate
        deselect(active_cols, active_rows, cols_deactivated, rows_deactivated)
        solution.pop()

def select(X, Y, active_cols, active_rows, r):
    """Deactivates columns covered by row r and rows that cover those same columns."""
    cols_deactivated = []
    rows_deactivated = []
    
    # For every column j that row r covers
    for j in Y[r]:
        if j in active_cols:
            active_cols.remove(j)
            cols_deactivated.append(j)
            
            # For every row i that also covers column j, deactivate row i
            for i in X[j]:
                if active_rows[i]:
                    active_rows[i] = False
                    rows_deactivated.append(i)
                    
    return cols_deactivated, rows_deactivated

def deselect(active_cols, active_rows, cols_deactivated, rows_deactivated):
    """Reactivates rows and columns during backtracking."""
    for i in rows_deactivated:
        active_rows[i] = True
    for j in cols_deactivated:
        active_cols.add(j)
