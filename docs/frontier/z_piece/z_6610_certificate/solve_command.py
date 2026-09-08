#!/usr/bin/env python3
"""Exact command/script of the certified 6x6x10 UNSAT run (2026-08-28).

This is the verbatim logic executed for the with_proof (DRAT) run recorded in
metadata.json["runs"]. Re-running it reproduces the CNF, the UNSAT result and
the DRAT proof (wall time ~415 s single-process, ~1.5 GB RAM for the proof
list).

Requires: python-sat (pip install python-sat)
"""
import sys, time
sys.path.insert(0, "/tmp/opencode")          # for z_sat/z_layer_dp prototypes
sys.path.insert(0, ".")
from z_sat import placements_cells
from pysat.formula import IDPool
from pysat.solvers import Cadical153

t0 = time.time()
pls = placements_cells(6, 6, 10)
pool = IDPool(start_from=1)
vs = [pool.id(p) for p in pls]
cnf = []
cover = {}
for v, p in zip(vs, pls):
    for c in p:
        cover.setdefault(c, []).append(v)
for c, l in cover.items():
    cnf.append(l[:])
    for i in range(len(l)):
        for j in range(i + 1, len(l)):
            cnf.append([-l[i], -l[j]])
print("vars", len(vs), "clauses", len(cnf), flush=True)

with Cadical153(bootstrap_with=cnf, with_proof=True) as s:
    sat = s.solve()
    proof = s.get_proof()
print("result:", "SAT" if sat else "UNSAT", "in", round(time.time() - t0, 1), "s", flush=True)
print("proof lines:", len(proof), flush=True)
open("z_6610.drat", "w").write("\n".join(proof))
print("DRAT written: z_6610.drat", flush=True)
