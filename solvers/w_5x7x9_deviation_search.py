#!/usr/bin/env python3
"""Deviation search: forbid each known placement one at a time, solve."""
import sys, re, time
sys.path.insert(0, '/home/philip/Work/fitpolycubes')
from common.polycube_utils import PENTACUBES, generate_placements, build_exact_cover_data
from common.algorithm_x_fast import solve

def parse(fp):
    with open(fp) as f:
        pl = f.read().strip().split('\n')[2]
    m = re.findall(r'\((\d+),(\d+),(\d+)\)', pl)
    return [tuple(sorted((int(m[i][0]),int(m[i][1]),int(m[i][2])) for i in range(j,j+5))) for j in range(0,len(m),5)]

def can(t):
    return tuple(sorted(tuple(sorted(p)) for p in t))

known = parse("/home/philip/Work/fitpolycubes/data/solutions_w_5x7x9_shirakawa.dat")
print(f"Known: {len(known)} pieces", flush=True)

raw,_ = generate_placements(PENTACUBES['W'], (5,7,9), break_symmetry=False)
all_pl = {}
for idx, p in raw.items():
    c = tuple(sorted(tuple(map(int,a)) for a in p))
    if c not in all_pl.values():
        all_pl[idx] = c

# Build ID mapping for known placements
known_set = set(known)
known_ids = []
for idx, p in all_pl.items():
    if p in known_set:
        known_ids.append(idx)

print(f"Known placement IDs: {len(known_ids)}", flush=True)

# Rank placements by number of alternative placements for their cells
from collections import Counter
cell_counts = Counter()
for idx, p in all_pl.items():
    for x,y,z in p: cell_counts[(x,y,z)] += 1

# Score each placement: sum of alternative counts for its cells
placement_scores = []
for kid in known_ids:
    p = all_pl[kid]
    score = sum(cell_counts[c] for c in p)
    placement_scores.append((score, kid, p))

placement_scores.sort()  # lowest score = most constrained = best to try first
print("\n5 most constrained placements to forbid:")
for score, kid, p in placement_scores[:5]:
    print(f"  ID={kid}, score={score}, p={p}", flush=True)

# Deviate from the search timeout
print("\n" + "="*70, flush=True)
print("DEVIATION SEARCH", flush=True)
print("="*70, flush=True)

timeout_per_branch = 30  # seconds

found = None
for score, forbid_id, forbid_p in placement_scores:
    print(f"\n--- Forbidding ID={forbid_id} (score={score}) ---", flush=True)
    
    # Build filtered placement list
    filtered = {}
    ni = 0
    for idx, p in all_pl.items():
        if idx == forbid_id: continue
        filtered[ni] = p
        ni += 1
    
    print(f"  Placements left: {len(filtered)}", flush=True)
    
    X, bl = build_exact_cover_data(filtered, (5,7,9))
    ac = set(bl)
    ar = [True] * len(filtered)
    
    t0 = time.time()
    sol_found = False
    for sol in solve(X, filtered, ac, ar):
        elapsed = time.time() - t0
        if elapsed > timeout_per_branch:
            print(f"  TIMEOUT ({elapsed:.1f}s)", flush=True)
            break
        
        sol_pieces = [filtered[s] for s in sol]
        cells = set()
        for p in sol_pieces:
            for x,y,z in p: cells.add((x,y,z))
        
        if len(cells) == 315:
            print(f"  ✓ COMPLETE TILING FOUND! ({elapsed:.1f}s)", flush=True)
            found = sol_pieces
            sol_found = True
            break
    
    if not sol_found:
        print(f"  No solution ({time.time()-t0:.1f}s)", flush=True)
    
    if found: break

if found:
    print(f"\n{'='*70}", flush=True)
    print("✓ SECOND TILING FOUND!", flush=True)
    print(f"  Pieces: {len(found)}", flush=True)
    
    # Check orbit
    from itertools import permutations, product
    box = (5,7,9)
    proper = []
    for p in permutations([0,1,2]):
        if [5,7,9][p[0]]==5 and [5,7,9][p[1]]==7 and [5,7,9][p[2]]==9:
            for sx,sy,sz in product([1,-1], repeat=3):
                ps = 1 if p in [(0,1,2),(1,2,0),(2,0,1)] else -1
                if ps*sx*sy*sz == 1: proper.append((p,(sx,sy,sz)))
    
    def ap(t,s):
        p,sg=s; d=[5,7,9]; r=[]
        for pe in t:
            np=[]
            for x,y,z in pe:
                nx = [x,y,z][p[0]] if sg[0]==1 else d[p[0]]-1-[x,y,z][p[0]]
                ny = [x,y,z][p[1]] if sg[1]==1 else d[p[1]]-1-[x,y,z][p[1]]
                nz = [x,y,z][p[2]] if sg[2]==1 else d[p[2]]-1-[x,y,z][p[2]]
                np.append((nx,ny,nz))
            r.append(tuple(sorted(np)))
        r.sort(); return tuple(r)
    
    new_c = can(found)
    in_orb = any(can(ap(known,s))==new_c for s in proper)
    print(f"  In known orbit: {in_orb}", flush=True)
    
    if not in_orb:
        print(f"\nRESULT: NON-UNIQUE", flush=True)
    else:
        print(f"\nRESULT: IN KNOWN ORBIT (try different branch)", flush=True)
else:
    print(f"\n{'='*70}", flush=True)
    print("No second tiling found in any branch.", flush=True)
    print("RESULT: UNDETERMINED", flush=True)

print(f"\n{'='*70}", flush=True)