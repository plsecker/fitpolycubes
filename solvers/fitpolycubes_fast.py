"""
Polycube Exact Cover Solver - Optimized with Boolean Masks

Created on Sun May  1 19:43:13 2016
@author: Philip
"""

import os
import sys
import numpy as np
from numpy import array

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM

#############   Exact cover functions (Non-mutating) #############

def solve(X, Y, active_cols, active_rows, found, solution=None):
    if solution is None:
        solution = []

    # If no active columns remain, we found a solution
    if not active_cols:
        found[0] += 1
        yield list(solution)
        return

    # Choose the active column with the fewest active rows
    # X[c] contains all row indices i that cover column c
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
            if count == 0: break # Constraint cannot be satisfied

    if min_rows == 0 or best_col is None:
        return

    # Try each active row that covers the chosen column
    for r in list(X[best_col]):
        if not active_rows[r]:
            continue

        solution.append(r)
        
        # Deactivate rows and columns
        cols_deactivated, rows_deactivated = select(X, Y, active_cols, active_rows, r)
        
        yield from solve(X, Y, active_cols, active_rows, found, solution)
        
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

#################################################################

# Example polycube piece (Y pentacube)
p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 1]])   # N piece
# p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 0]])   # Y piece
# p = np.array([[0, 0, 1],[1, 0, 1],[2, 0, 0],[2, 0, 1],[2, 0, 2]])   # T piece

numcubes = p.shape[0]

# Construct the box: set of (x,y,z) coordinates
box = {(x, y, z) for z in range(5) for y in range(5) for x in range(5)}

# Generate piece placements
count = 0
Y = {}
for cube in box:
    base = array(cube)
    for rotindex in range(24):
        rp = base + p @ RM[rotindex].T
        rpl = [tuple(map(int, pt)) for pt in rp]
        if all(pt in box for pt in rpl):
            Y[count] = rpl
            count += 1

print("Placements found:", count)

# Build X for exact cover (mapping columns to rows)
X = {cell: set() for cell in box}
for row_id, cells in Y.items():
    for cell in cells:
        X[cell].add(row_id)

# Initialize trackers
active_rows = [True] * len(Y)
active_cols = set(box)
found = [0]

# Run solver
solutions = solve(X, Y, active_cols, active_rows, found)
# Output results
import os
fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/solutions_fast.dat")
with open(fname, "w") as f:
    f.write("#Npentacubes (Fast Solver)\n")

c = 0
for sol in solutions:
    c += 1
    if c % 100 == 0:
        print(f"Found {c} solutions...")

    sol_str = "".join([str(Y[p_index]) for p_index in sol])
    with open(fname, "a") as f:
        f.write(f"{c}\n{sol_str}\n")

