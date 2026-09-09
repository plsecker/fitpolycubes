#!/usr/bin/env python3
"""SAT search for second W 5x7x9 tiling."""
import sys, re, time
from pathlib import Path
from itertools import permutations, product, combinations
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.polycube_utils import PENTACUBES, generate_placements
from pysat.solvers import Glucose4

def parse(fp):
    with open(fp) as f:
        pl = f.read().strip().split('\n')[2]
    m = re.findall(r'\((\d+),(\d+),(\d+)\)', pl)
    return [tuple(sorted((int(m[i][0]),int(m[i][1]),int(m[i][2])) for i in range(j,j+5))) for j in range(0,len(m),5)]

def can(t):
    return tuple(sorted(tuple(sorted(p)) for p in t))

def gs(b):
    a,b,c=b; d=[a,b,c]; r=[]
    for p in permutations([0,1,2]):
        if d[p[0]]==d[0] and d[p[1]]==d[1] and d[p[2]]==d[2]:
            for sx,sy,sz in product([1,-1], repeat=3):
                ps = 1 if p in [(0,1,2),(1,2,0),(2,0,1)] else -1
                if ps*sx*sy*sz == 1: r.append((p,(sx,sy,sz)))
    return r

def ap(t,s,b):
    p,sg=s; bx,by,bz=b; d=[bx,by,bz]; r=[]
    for pe in t:
        np=[]
        for x,y,z in pe:
            nx = [x,y,z][p[0]] if sg[0]==1 else d[p[0]]-1-[x,y,z][p[0]]
            ny = [x,y,z][p[1]] if sg[1]==1 else d[p[1]]-1-[x,y,z][p[1]]
            nz = [x,y,z][p[2]] if sg[2]==1 else d[p[2]]-1-[x,y,z][p[2]]
            np.append((nx,ny,nz))
        r.append(tuple(sorted(np)))
    r.sort(); return tuple(r)

def cid(x,y,z): return x+y*5+z*35

print("Loading...", flush=True)
known = parse(str(Path(__file__).resolve().parent.parent / "data" / "solutions_w_5x7x9_shirakawa.dat"))
print(f"Known: {len(known)} pieces", flush=True)

raw,_ = generate_placements(PENTACUBES['W'], (5,7,9), break_symmetry=False)
plm={}; p2d={}; v=1
for _,p in raw.items():
    c = tuple(sorted(tuple(map(int,a)) for a in p))
    if c not in p2d: plm[v]=c; p2d[c]=v; v+=1
N=len(plm)
print(f"Placements: {N}", flush=True)

box=(5,7,9)
proper=gs(box)
print(f"Proper rotations: {len(proper)}", flush=True)

orbits = []
for sym in proper:
    t = ap(known, sym, box)
    s = set()
    for p in t: s.add(p2d[tuple(sorted(p))])
    orbits.append(s)

print("Building CNF...", flush=True)
t0=time.time()
cv = {c:[] for c in range(315)}
for v,c in plm.items():
    for x,y,z in c: cv[cid(x,y,z)].append(v)

solv = Glucose4()
for c in range(315): solv.add_clause(cv[c])
for c in range(315):
    for a,b in combinations(cv[c],2): solv.add_clause([-a,-b])
for ids in orbits: solv.add_clause([-v for v in ids])
print(f"Built: {N} vars in {time.time()-t0:.1f}s", flush=True)

print("Solving...", flush=True)
t0=time.time()
r = solv.solve()
el = time.time()-t0

if r == True:
    m = solv.get_model()
    sl = [v for v in m if v > 0]
    nt = [plm[v] for v in sl]
    cs=set()
    for p in nt:
        for x,y,z in p: cs.add((x,y,z))
    nc = can(nt)
    io = any(can(ap(known,sym,box))==nc for sym in proper)
    print(f"SAT: {len(nt)}p, {len(cs)}c, in_orbit={io} ({el:.1f}s)", flush=True)
    if not io and len(cs)==315:
        print("\n✓ SECOND INEQUIVALENT W TILING FOUND! NON-UNIQUE", flush=True)
elif r == False:
    print(f"\nUNSAT ({el:.1f}s) - known orbit appears unique", flush=True)
else:
    print(f"\nUNDETERMINED ({el:.1f}s)", flush=True)

solv.delete()