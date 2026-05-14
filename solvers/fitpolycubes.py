"""
Polycube Exact Cover Solver

Created on Sun May  1 19:43:13 2016
@author: Philip
"""

import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM
from common.algorithm_x import solve


# Example polycube piece (Y pentacube)
# p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 1]])   # N piece
p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 0]])     # Y piece
# p = np.array([[0, 0, 1],[1, 0, 1],[2, 0, 0],[2, 0, 1],[2, 0, 2]])   # T piece

numcubes = p.shape[0]

# Construct the box: set of (x,y,z) coordinates
box = {(x, y, z) for z in range(5) for y in range(5) for x in range(5)}

# Generate piece placements
count = 0
Y = {}
for cube in box:
    for rotindex in range(24):
        rp = cube + p @ RM[rotindex].T  # offset + rotate
        rpl = rp.tolist()
        rpinbox = [tuple(rpl[i]) in box for i in range(numcubes)]
        if all(rpinbox):
            Y[count] = list(map(tuple, rpl))
            count += 1

print("Placements found:", count)

# Build X for exact cover
X = {j: set() for j in box}
for i in Y:
    for j in Y[i]:
        X[j].add(i)

# Run solver
solutions = solve(X, Y)

# Output results
fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/solutions_n.dat")
with open(fname, "w") as f:
    f.write("# N pentacubes\n")

c = cc = cu = 0
for sol in solutions:
    c += 1
    print(c)
    solset = set()
    with open(fname, "a") as f:
        f.write(f"\n{c}\n")
        for p_index in sol:
            solset.add(frozenset(Y[p_index]))
            f.write(f"{Y[p_index]}\n")

    # Placeholder for uniqueness/symmetry checks
    # cu and cc not yet implemented

# Summary
with open(fname, "a") as f:
    f.write(f"\nElements in Y: {len(Y)}\n")
    f.write(f"Total combinations: {c}\n")
    f.write(f"Total unique: {cu}\n")
    f.write(f"Total symmetric: {cc}\n")
