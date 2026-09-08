#!/usr/bin/env python3
"""
Classify 22 solutions under all 3 symmetry conventions and compare.
"""
import sys, re
from itertools import permutations, product
sys.path.insert(0, '')

# Load solutions
def load(fp):
    with open(fp) as f: content = f.read()
    sols = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1; continue
        if line.isdigit() and i+1 < len(lines):
            pl = lines[i+1].strip()
            placements = []
            pat = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
            matches = re.findall(pat, pl)
            for j in range(0, len(matches), 5):
                if j+5 <= len(matches):
                    placements.append([(int(matches[j+k][0]), int(matches[j+k][1]), int(matches[j+k][2])) for k in range(5)])
            if len(placements) == 45:
                sols.append(placements)
            i += 2
        else:
            i += 1
    return sols

sols = load("data/solutions_fast_v_5x5x9.dat")
print(f"Loaded {len(sols)} solutions\n")

def can(t):
    return tuple(sorted(tuple(sorted(p)) for p in t))

# Group generators for three conventions
dims = [5,5,9]

# V4: 180-degree rotations only
def group_v4():
    g = []
    for perm in permutations([0,1,2]):
        if dims[perm[0]]==dims[0] and dims[perm[1]]==dims[1] and dims[perm[2]]==dims[2]:
            for sx,sy,sz in product([1,-1], repeat=3):
                # V4 has even number of -1 signs (0 or 2) and no permutation
                n_neg = sum(1 for s in (sx,sy,sz) if s==-1)
                if perm==(0,1,2) and n_neg in (0,2):
                    g.append((perm, (sx,sy,sz)))
    return g

# G8: all 8 proper rotations preserving 5×5×9
def group_g8():
    g = []
    for perm in permutations([0,1,2]):
        if dims[perm[0]]==dims[0] and dims[perm[1]]==dims[1] and dims[perm[2]]==dims[2]:
            for sx,sy,sz in product([1,-1], repeat=3):
                perm_sign = 1 if perm in [(0,1,2),(1,2,0),(2,0,1)] else -1
                det = perm_sign * sx * sy * sz
                if det == 1:
                    g.append((perm, (sx,sy,sz)))
    return sorted(g)

# G16: full box symmetry (include reflections = det=-1)
def group_g16():
    g = []
    for perm in permutations([0,1,2]):
        if dims[perm[0]]==dims[0] and dims[perm[1]]==dims[1] and dims[perm[2]]==dims[2]:
            for sx,sy,sz in product([1,-1], repeat=3):
                g.append((perm, (sx,sy,sz)))
    return sorted(g)

def apply(t, perm, signs, box=(5,5,9)):
    bx,by,bz = box
    db = [bx,by,bz]
    result = []
    for p in t:
        np = []
        for x,y,z in p:
            cs = [x,y,z]
            nx = cs[perm[0]] if signs[0]==1 else db[perm[0]]-1-cs[perm[0]]
            ny = cs[perm[1]] if signs[1]==1 else db[perm[1]]-1-cs[perm[1]]
            nz = cs[perm[2]] if signs[2]==1 else db[perm[2]]-1-cs[perm[2]]
            np.append((nx,ny,nz))
        result.append(tuple(sorted(np)))
    return result

def classify(group_fn, label):
    g = group_fn()
    cans = [can(s) for s in sols]
    processed = set()
    classes = []
    for idx,s in enumerate(sols):
        c = cans[idx]
        if c in processed: continue
        orbit = set()
        for perm, signs in g:
            transformed = apply(s, perm, signs)
            orbit.add(can(transformed))
        orbit_sols = [j for j,cj in enumerate(cans) if cj in orbit]
        processed.update(orbit)
        classes.append({
            'orbit_size': len(orbit),
            'solutions': sorted(orbit_sols),
        })
    print(f"{label} ({len(g)} elements): {len(classes)} classes")
    for i, c in enumerate(classes):
        print(f"  Class {i+1}: |O|={c['orbit_size']}, {len(c['solutions'])} solutions {c['solutions']}")
    print(f"  Total solutions: {sum(len(c['solutions']) for c in classes)}")
    print()
    return classes

print("=== Symmetry Convention Comparison ===\n")
classify(group_v4, "V4 (180° rotations)")
classify(group_g8, "G8 (all proper rotations)")
classify(group_g16, "G16 (full box symmetry)")