#!/usr/bin/env python3
"""W 5x7x9 deviation search using z3 SAT solver."""
import sys, re, time
sys.path.insert(0, '/home/philip/Work/fitpolycubes')
from z3 import *
from common.polycube_utils import PENTACUBES, generate_placements

def parse(fp):
    with open(fp) as f: pl = f.read().strip().split('\n')[2]
    m = re.findall(r'\((\d+),(\d+),(\d+)\)', pl)
    return [tuple(sorted((int(m[i][0]),int(m[i][1]),int(m[i][2])) for i in range(j,j+5))) for j in range(0,len(m),5)]

known = parse("/home/philip/Work/fitpolycubes/data/solutions_w_5x7x9_shirakawa.dat")
print(f"Known: {len(known)} pieces", flush=True)

raw,_ = generate_placements(PENTACUBES['W'], (5,7,9), break_symmetry=False)
all_pl = {}
p2id = {}
for idx, p in raw.items():
    c = tuple(sorted(tuple(map(int,a)) for a in p))
    if c not in p2id:
        all_pl[len(all_pl)] = c
        p2id[c] = len(all_pl) - 1

N = len(all_pl)
print(f"Placements: {N}", flush=True)

# z3 variables
vars = [Bool(f'p{i}') for i in range(N)]

t0 = time.time()

# At-least-one per cell
cell_vars = {c: [] for c in range(315)}
for vid, p in all_pl.items():
    for x,y,z in p:
        cell_vars[x+y*5+z*35].append(vars[vid])

# Exclusion: forbid the most constrained known placement
# Find known placement with fewest alternatives
from collections import Counter
cell_counts = Counter()
for p in all_pl.values():
    for x,y,z in p: cell_counts[(x,y,z)] += 1

known_ids = [p2id[p] for p in known]
scores = [(sum(cell_counts[c] for c in all_pl[kid]), kid) for kid in known_ids]
scores.sort()

print(f"Top 5 forbids:", flush=True)
for score, kid in scores[:5]:
    print(f"  ID={kid}, score={score}, p={all_pl[kid][:2]}...", flush=True)

for score, forbid_id in scores[:5]:  # Try 5 most constrained
    print(f"\n--- Forbidding ID={forbid_id} (score={score}) ---", flush=True)
    
    solver = Solver()
    solver.set("timeout", 60000)  # 60s timeout
    
    # At-least-one per cell
    for c_vars in cell_vars.values():
        solver.add(Or(c_vars))
    
    # At-most-one per cell using PbLe
    for c_vars in cell_vars.values():
        solver.add(PbLe([(v, 1) for v in c_vars], 1))
    
    # Exactly 63 placements
    solver.add(PbEq([(v, 1) for v in vars], 63))
    
    # Forbid this placement
    solver.add(Not(vars[forbid_id]))
    
    st = time.time()
    r = solver.check()
    et = time.time() - st
    
    if r == sat:
        model = solver.model()
        selected = [i for i in range(N) if is_true(model[vars[i]])]
        print(f"  SAT: {len(selected)} placements ({et:.1f}s)", flush=True)
        found = [all_pl[i] for i in selected]
        
        # Validate
        cells = set()
        for p in found:
            for x,y,z in p: cells.add((x,y,z))
        print(f"  Cells: {len(cells)}", flush=True)
        
        if len(cells) == 315:
            print(f"\n{'='*70}", flush=True)
            print("✓ SECOND TILING FOUND!", flush=True)
            print("Result: NON-UNIQUE (pending orbit check)", flush=True)
            print(f"{'='*70}", flush=True)
            
            # Orbit check  
            from itertools import permutations, product
            box = (5,7,9)
            proper = []
            for p in permutations([0,1,2]):
                if [5,7,9][p[0]]==5 and [5,7,9][p[1]]==7 and [5,7,9][p[2]]==9:
                    for sx,sy,sz in product([1,-1], repeat=3):
                        ps = 1 if p in [(0,1,2),(1,2,0),(2,0,1)] else -1
                        if ps*sx*sy*sz == 1: proper.append((p,(sx,sy,sz)))
            
            def can(t):
                return tuple(sorted(tuple(sorted(p)) for p in t))
            
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
            
            nc = can(found)
            in_orb = any(can(ap(known,s))==nc for s in proper)
            print(f"  In known orbit: {in_orb}", flush=True)
            if not in_orb:
                print("\n✓ TRULY INEQUIVALENT! NON-UNIQUE", flush=True)
            else:
                print("\n(In known orbit - try different forbid)", flush=True)
            sys.exit(0)
    elif r == unsat:
        print(f"  UNSAT ({et:.1f}s)", flush=True)
    else:
        print(f"  TIMEOUT ({et:.1f}s)", flush=True)

print(f"\n{'='*70}", flush=True)
print("No second tiling found. RESULT: UNDETERMINED", flush=True)
print(f"{'='*70}", flush=True)