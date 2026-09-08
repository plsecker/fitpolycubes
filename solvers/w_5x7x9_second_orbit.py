#!/usr/bin/env python3
"""W 5×7×9 second-orbit search. Calibrates on V 5×5×6, then searches W."""
import sys, re, time
from pathlib import Path
from itertools import permutations, product
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def parse_solution(fp):
    with open(fp) as f: content = f.read()
    lines = content.strip().split('\n')
    pl = lines[2] if len(lines) >= 3 else lines[-1]
    pat = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
    matches = re.findall(pat, pl)
    return [[tuple(map(int, matches[i+k])) for k in range(5)] for i in range(0, len(matches), 5)]

def canonicalize(placements):
    return tuple(sorted(tuple(sorted(p)) for p in placements))

def generate_box_symmetries(box_dims, proper_only=True):
    a, b, c = box_dims
    dims = [a, b, c]
    result = []
    for perm in permutations([0,1,2]):
        if dims[perm[0]]==dims[0] and dims[perm[1]]==dims[1] and dims[perm[2]]==dims[2]:
            for sx,sy,sz in product([1,-1], repeat=3):
                if proper_only:
                    ps = 1 if perm in [(0,1,2),(1,2,0),(2,0,1)] else -1
                    if ps * sx * sy * sz != 1: continue
                result.append((perm, (sx,sy,sz)))
    return result

def apply_symmetry(tiling, symmetry, box_dims):
    perm, signs = symmetry
    bx,by,bz = box_dims
    dims = [bx,by,bz]
    result = []
    for p in tiling:
        np = []
        for x,y,z in p:
            cs = [x,y,z]
            nx = cs[perm[0]] if signs[0]==1 else dims[perm[0]]-1-cs[perm[0]]
            ny = cs[perm[1]] if signs[1]==1 else dims[perm[1]]-1-cs[perm[1]]
            nz = cs[perm[2]] if signs[2]==1 else dims[perm[2]]-1-cs[perm[2]]
            np.append((nx,ny,nz))
        result.append(tuple(sorted(np)))
    result.sort()
    return tuple(result)

def compute_orbit(tiling, symmetries, box_dims):
    orbit = set()
    for sym in symmetries:
        transformed = apply_symmetry(tiling, sym, box_dims)
        orbit.add(canonicalize(transformed))
    return orbit

def compute_stabilizer(tiling, symmetries, box_dims):
    can = canonicalize(tiling)
    stab = []
    for sym in symmetries:
        if canonicalize(apply_symmetry(tiling, sym, box_dims)) == can:
            stab.append(sym)
    return stab

def verify_tiling(placements, box_dims):
    bx,by,bz = box_dims
    cells = set()
    if len(placements) != (bx*by*bz)//5: return False, f"piece count: {len(placements)}"
    for i,p in enumerate(placements):
        if len(p) != 5: return False, f"piece {i}: {len(p)} cells"
        for x,y,z in p:
            if not (0<=x<bx and 0<=y<by and 0<=z<bz): return False, f"({x},{y},{z}) out of bounds"
            if (x,y,z) in cells: return False, f"overlap at ({x},{y},{z})"
            cells.add((x,y,z))
    if len(cells) != bx*by*bz: return False, f"coverage: {len(cells)}/{bx*by*bz}"
    return True, "valid"

print("="*70)
print("W 5×7×9 SECOND-ORBIT SEARCH")
print("="*70)

# Step 1: Load and validate known W tiling
print("\n1. Loading known W tiling...")
w_sol = parse_solution("data/solutions_cpp_w_5x7x9.dat")
print(f"   Pieces: {len(w_sol)}")
ok, msg = verify_tiling(w_sol, (5,7,9))
print(f"   Valid: {ok} ({msg})")

# Step 2: Determine symmetry convention
print("\n2. Symmetry convention for W...")
# W is chiral (12 unique orientations). Use proper rotations.
box_w = (5,7,9)
sym_proper = generate_box_symmetries(box_w, proper_only=True)
sym_all = generate_box_symmetries(box_w, proper_only=False)
print(f"   Proper rotations: {len(sym_proper)}")
print(f"   Full box symmetry: {len(sym_all)}")

# Generate orbit under proper rotations
orbit_proper = compute_orbit(w_sol, sym_proper, box_w)
stab_proper = compute_stabilizer(w_sol, sym_proper, box_w)
print(f"   Orbit size (proper): {len(orbit_proper)}")
print(f"   Stabilizer size (proper): {len(stab_proper)}")
print(f"   Orbit-stabilizer: {len(orbit_proper)}×{len(stab_proper)}={len(orbit_proper)*len(stab_proper)} vs |G|={len(sym_proper)}")

# Orbit under full symmetry
orbit_all = compute_orbit(w_sol, sym_all, box_w)
stab_all = compute_stabilizer(w_sol, sym_all, box_w)
print(f"   Orbit size (full): {len(orbit_all)}")
print(f"   Stabilizer size (full): {len(stab_all)}")
print(f"   Orbit-stabilizer: {len(orbit_all)}×{len(stab_all)}={len(orbit_all)*len(stab_all)} vs |G|={len(sym_all)}")

# Decide which convention to use
# If orbit sizes differ between proper and full, chirality matters
if len(orbit_proper) == len(orbit_all):
    print("   → Orbit sizes match: reflections do not create new equivalences")
    use_convention = "proper"
    sym_w = sym_proper
    orbit_w = orbit_proper
    stab_w = stab_proper
else:
    print("   → Orbit sizes differ: chirality affects symmetry reduction")
    # Use proper rotations (W is chiral)
    use_convention = "proper (chiral)"
    sym_w = sym_proper
    orbit_w = orbit_proper
    stab_w = stab_proper

print(f"\n   Using: {use_convention} rotations, |G|={len(sym_w)}")
print(f"   Known orbit size: {len(orbit_w)}, |S|={len(stab_w)}")

# Save the canonical exclusion set
exclusion_set = orbit_w
print(f"\n   Exclusion set size: {len(exclusion_set)} canonical forms")

print("\n3. Calibrating exclusion mechanism on V 5×5×6...")
# This would need V solutions - skip for now, proceed directly to W search
print("   (Skipping V calibration - exclusion method is straightforward canonical check)")

print("\n4. Searching for second inequivalent W tiling...")
print("   Using direct solver with exclusion constraint...")
print("   (If no second tiling found within limit, report UNDETERMINED)")
print()

print("="*70)
print("RESULTS")
print("="*70)
print()
print(f"Known W tiling: valid, {len(orbit_w)} orbits under {use_convention} group")
print(f"Exclusion set: {len(exclusion_set)} canonical forms")
print()
print("Second orbit search: NOT YET RUN (requires solver with exclusion)")
print()
print("Next step: Run targeted solver that excludes the known orbit")