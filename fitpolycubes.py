"""
Polycube Exact Cover Solver

Created on Sun May  1 19:43:13 2016
@author: Philip
"""

from numpy import array
from rotmatrix import RM

#############   Exact cover functions
# From http://www.cs.mcgill.ca/~aassaf9/python/algorithm_x.html
#
def solve(X, Y, solution=None):
    if solution is None:
        solution = []
    if not X:
        yield list(solution)
    else:
        c = min(X, key=lambda c: len(X[c]))
        for r in list(X[c]):
            solution.append(r)
            cols = select(X, Y, r)
            for s in solve(X, Y, solution):
                yield s
            deselect(X, Y, r, cols)
            solution.pop()


def select(X, Y, r):
    cols = []
    for j in Y[r]:
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].remove(i)
        cols.append(X.pop(j))
    return cols


def deselect(X, Y, r, cols):
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].add(i)
#######################################

# Example polycube piece (Y pentacube)
# p = array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 1]])   # N piece
p = array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 0]])     # Y piece
# p = array([[0, 0, 1],[1, 0, 1],[2, 0, 0],[2, 0, 1],[2, 0, 2]])   # T piece

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
fname = "solutions_n.dat"
with open(fname, "w") as f:
    f.write("# N pentacubes\n")

c = cc = cu = 0
for i in solutions:
    c += 1
    solset = set()
    with open(fname, "a") as f:
        f.write(f"\n{c}\n")
        for p in i:
            solset.add(frozenset(Y[p]))
            f.write(f"{Y[p]}\n")

    # Placeholder for uniqueness/symmetry checks
    # (unique/uniqueflip sets not defined here)

# Summary
with open(fname, "a") as f:
    f.write(f"\nElements in Y: {len(Y)}\n")
    f.write(f"Total combinations: {c}\n")
    f.write(f"Total unique: {cu}\n")
    f.write(f"Total symmetric: {cc}\n")
