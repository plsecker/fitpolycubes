#!/usr/bin/env python3
#
#  Author: Rogelio Tomas (cleaned for Python 3)
#

import numpy as np
import sys

# Define cube dimensions
side = 5
hside = side // 2

#############   Exact cover functions
# from
# http://www.cs.mcgill.ca/~aassaf9/python/algorithm_x.html
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
for i in range(-hside, hside + 1):
    for j in range(-hside, hside + 1):
        for k in range(-hside, hside + 1):
            X.add((i, j, k))

# Building Y, covering subsets
def addsubs(ypent):
    global Y, count
    maxx, maxy, maxz = ypent.max(axis=0)
    minx, miny, minz = ypent.min(axis=0)

    for i in range(-hside - minx, hside + 1 - maxx):
        for j in range(-hside - miny, hside + 1 - maxy):
            for z in range(-hside - minz, hside + 1 - maxz):
                tiles = ypent + np.array([i, j, z])
                tilestuple = list(map(tuple, tiles))
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
with open("solutions.dat", "w") as f:
    f.write("# y-pentacubes\n")

c = 0
cc = 0
cu = 0
unique = set()
uniqueflip = set()

for i in sol:
    c += 1
    print("Solution", c)
    # --- unique/symmetric filtering can go here ---

with open("solutions.dat", "a") as f:
    f.write("Elements in Y: {}\n".format(len(Y)))
    f.write("Total combinations: {}\n".format(c))
    f.write("Total unique: {}\n".format(cu))
    f.write("Total symmetric: {}\n".format(cc))

