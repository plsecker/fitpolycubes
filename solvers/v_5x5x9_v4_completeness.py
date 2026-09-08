#!/usr/bin/env python3
"""
Verify if V4-transformed tilings are valid (they should be if the group action
is correct and the solver found all solutions).
"""

import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def parse_sols(fp):
    with open(fp) as f: content = f.read()
    sols = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'): i += 1; continue
        if line.isdigit():
            if i + 1 < len(lines):
                pl = lines[i+1].strip()
                placements = []
                pat = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
                matches = re.findall(pat, pl)
                for j in range(0, len(matches), 5):
                    if j+5 <= len(matches):
                        placements.append([tuple(map(int, matches[j+k])) for k in range(5)])
                if len(placements) == 45: sols.append(placements)
                i += 2
            else: i += 1
        else: i += 1
    return sols


def apply_rot(tiling, perm, signs, box=(5,5,9)):
    bx, by, bz = box
    dims = [bx, by, bz]
    result = []
    for p in tiling:
        np = []
        for x,y,z in p:
            nx = x if signs[0]==1 else dims[perm[0]]-1-[x,y,z][perm[0]]
            ny = y if signs[1]==1 else dims[perm[1]]-1-[x,y,z][perm[1]]
            nz = z if signs[2]==1 else dims[perm[2]]-1-[x,y,z][perm[2]]
            np.append((nx,ny,nz))
        result.append(tuple(sorted(np)))
    return result


def verify(tiling, box=(5,5,9)):
    bx,by,bz = box
    cells = set()
    if len(tiling) != 45: return f"wrong piece count: {len(tiling)}"
    for i,p in enumerate(tiling):
        if len(p) != 5: return f"piece {i} has {len(p)} cells"
        for x,y,z in p:
            if not (0<=x<bx and 0<=y<by and 0<=z<bz):
                return f"out of bounds: ({x},{y},{z})"
            if (x,y,z) in cells: return f"overlap at ({x},{y},{z})"
            cells.add((x,y,z))
    if len(cells) != bx*by*bz: return f"coverage: {len(cells)}/{bx*by*bz}"
    return "valid"


# V4
V4 = {"I":((0,1,2),(1,1,1)), "R_x":((0,1,2),(1,-1,-1)),
       "R_y":((0,1,2),(-1,1,-1)), "R_z":((0,1,2),(-1,-1,1))}

sols = parse_sols("data/solutions_fast_v_5x5x9.dat")
print(f"Loaded {len(sols)} solutions\n")

# Build a set of canonical forms for quick lookup
def can(tiling):
    return tuple(sorted(tuple(sorted(p)) for p in tiling))

can_set = set()
for s in sols: can_set.add(can(s))

# For solution[0], apply all V4 elements and check validity + repository presence
print("Checking V4 orbit of solution[0]:")
for name, (perm, signs) in V4.items():
    t = apply_rot(sols[0], perm, signs)
    status = verify(t)
    tc = can(t)
    in_repo = tc in can_set
    print(f"  {name}: {status}, {'IN REPO' if in_repo else 'NOT IN REPO'}")

print()

# Count how many V4 variants are in the repository for each solution
print("V4 completeness of each solution:")
for idx in range(len(sols)):
    count = 0
    for name, (perm, signs) in V4.items():
        t = apply_rot(sols[idx], perm, signs)
        if can(t) in can_set: count += 1
    print(f"  Solution {idx}: {count}/4 V4 variants in repo")

print()
print("Done.")