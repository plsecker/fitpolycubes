#!/usr/bin/env python3
"""
Diagnostic: verify V4 group actions on solutions.
Check if solutions map to each other under V4 rotations.
"""

import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def parse_solution_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    solutions = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1; continue
        if line.isdigit():
            if i + 1 < len(lines):
                pl = lines[i + 1].strip()
                placements = []
                pat = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
                matches = re.findall(pat, pl)
                for j in range(0, len(matches), 5):
                    if j + 5 <= len(matches):
                        piece = [tuple(map(int, matches[j+k])) for k in range(5)]
                        placements.append(piece)
                if len(placements) == 45:
                    solutions.append(placements)
                i += 2
            else: i += 1
        else: i += 1
    return solutions


def canonicalize(placements):
    return tuple(sorted(tuple(sorted(p)) for p in placements))


def apply_rot(tiling, perm, signs, box=(5,5,9)):
    bx, by, bz = box
    dims = [bx, by, bz]
    result = []
    for p in tiling:
        np = []
        for x, y, z in p:
            coords = [x, y, z]
            nx = coords[perm[0]] if signs[0] == 1 else dims[perm[0]] - 1 - coords[perm[0]]
            ny = coords[perm[1]] if signs[1] == 1 else dims[perm[1]] - 1 - coords[perm[1]]
            nz = coords[perm[2]] if signs[2] == 1 else dims[perm[2]] - 1 - coords[perm[2]]
            np.append((nx, ny, nz))
        result.append(tuple(sorted(np)))
    result.sort()
    return tuple(result)


# V4 group
V4 = [
    ("I",   ((0,1,2), ( 1, 1, 1))),
    ("R_x", ((0,1,2), ( 1,-1,-1))),
    ("R_y", ((0,1,2), (-1, 1,-1))),
    ("R_z", ((0,1,2), (-1,-1, 1))),
]

sols = parse_solution_file("data/solutions_fast_v_5x5x9.dat")
print(f"{len(sols)} solutions loaded\n")

# Compute canonical forms
cans = [canonicalize(s) for s in sols]

# For each solution, apply V4 and check which other solutions match
print("V4 orbit membership (solution -> V4-applied -> matching solution):")
for idx in range(min(6, len(sols))):
    print(f"\nSolution {idx}:")
    for name, (perm, signs) in V4:
        transformed = apply_rot(sols[idx], perm, signs)
        tf = canonicalize(transformed)
        matches = [j for j, c in enumerate(cans) if c == tf]
        print(f"  {name}: transformed -> solutions {matches}")

print("\n\nChecking: under V4, does any solution have a non-trivial stabilizer?")
for idx in range(len(sols)):
    stab = []
    for name, (perm, signs) in V4:
        transformed = apply_rot(sols[idx], perm, signs)
        if canonicalize(transformed) == cans[idx]:
            stab.append(name)
    if len(stab) > 1:
        print(f"  Solution {idx}: stabilizer = {stab}")

print("\nDone.")