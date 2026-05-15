#!/usr/bin/env python3
#
#  Author: Rogelio Tomas (cleaned for Python 3)
#

import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.algorithm_x import solve

# Define cube dimensions
side = 5
hside = side // 2


##### Generating y-pentacubes functions
def ypentacubesfromdirection(direction):
    y = []
    body = []
    zer = []
    # put the zeros location in a list
    for i in range(3):
        if direction[i] == 0:
            zer.append(i)
    # make body (4 cubes in a row pointing in direction)
    for c in range(0, 4):
        body.append(direction * c)
    # make the 8 y-pentacubes (add the 'arms' onto this body)
    for izer in range(2):
        for b in [1, -1]:
            up = direction * 2
            down = direction * 1
            ypentup = list(body)
            ypentdown = list(body)
            up[zer[izer]] = b
            ypentup.append(np.array(up))
            down[zer[izer]] = b
            ypentdown.append(np.array(down))
            y.append(np.array(ypentup))
            y.append(np.array(ypentdown))
    return y

# Generating box to uniquely cover later
X = set()
for i in range(side):
    for j in range(side):
        for k in range(side):
            X.add((i, j, k))

# Building Y, covering subsets
def addsubs(ypent):
    global Y, count
    maxx, maxy, maxz = ypent.max(axis=0)
    minx, miny, minz = ypent.min(axis=0)

    for i in range(-minx, side - maxx):
        for j in range(-miny, side - maxy):
            for z in range(-minz, side - maxz):
                tiles = ypent + np.array([i, j, z])
                tilestuple = [tuple(map(int, tile)) for tile in tiles]
                Y[count] = tilestuple
                count += 1

# Subcollections
Y = {}
count = 0
for i in range(3):
    vec = np.array([0, 0, 0])
    vec[i] = 1
    ypens = ypentacubesfromdirection(vec)
    for pen in ypens:
        addsubs(pen)

print("Number of Y subsets:", count)

# Putting X in the required format for solve()
X = {j: set() for j in X}
for i in Y:
    for j in Y[i]:
        X[j].add(i)

# Exact cover solver
sol = solve(X, Y)

###### Functions to mirror solutions
# NOTE: 'longside' and 'smallside' were undefined in original code.
# Here I assume they both equal 'side'. Adjust if your box is not square.
longside = side
smallside = side

def flipxy(xy, case):
    if case == 1:
        return (longside - 1 - xy[0], xy[1])
    if case == 2:
        return (xy[0], smallside - 1 - xy[1])
    if case == 3:
        return (longside - 1 - xy[0], smallside - 1 - xy[1])

def flip(x, case):
    return [flipxy(np.array(e), case) for e in x]

def flipset(x, case):
    return {frozenset(flip(e, case)) for e in x}

##################

# counting, finding unique and symmetric solutions and output
fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/solutions_y.dat")
with open(fname, "w") as f:
    f.write("#Ypentacubes\n")

c = 0
for sol in sol:
    c += 1
    print("Solution", c)
    sol_str = "".join([str(Y[p_index]) for p_index in sol])
    with open(fname, "a") as f:
        f.write(f"{c}\n{sol_str}\n")

