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
p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 1]])   # N piece
# p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 0]])     # Y piece
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
        rpl = [tuple(map(int, pt)) for pt in rp]
        rpinbox = [pt in box for pt in rpl]
        if all(rpinbox):
            Y[count] = rpl
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
    f.write("#Npentacubes\n")

c = 0
for sol in solutions:
    c += 1
    print(c)
    sol_str = "".join([str(Y[p_index]) for p_index in sol])
    with open(fname, "a") as f:
        f.write(f"{c}\n{sol_str}\n")
