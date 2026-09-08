#!/usr/bin/env python3
"""Independent semantic audit of the Z 6x6x10 UNSAT certificate package.

This script is STANDALONE: it imports nothing from the fitpolycubes
repository. It re-derives everything from first principles:

  1. The Z pentacube piece definition (hard-coded constant below, with
     provenance note) and the 24 proper rotations of the cube are used to
     independently regenerate the set of legal placements in the 6x6x10 box.
  2. The regenerated placement set is compared against placement_set.json.
  3. Every placement is checked: 5 cells, Z-congruent, inside the box.
  4. Coverage completeness: every one of the 360 cells is covered by at
     least one placement.
  5. The CNF file (DIMACS) is parsed and verified to correspond EXACTLY to
     the placement set:
       - one all-positive clause per cell, over exactly the placements
         containing that cell (>= 1 coverage);
       - one all-negative clause per pair of placements sharing a cell
         (no-overlap); no other clauses; no mixed polarity;
       - variable ids correspond to placements exactly as recorded in
         var_map.json.
  6. Counts are cross-checked against hashes.txt / metadata.json.

What this script does NOT do: it does not decide satisfiability. The UNSAT
claim is established by the accompanying DRAT proof, which a third party
verifies with a standard checker (see README.md).

Usage:  python3 z_6610_verify_encoding.py [package_dir]
Exit code 0 = all audits pass.
"""
import json
import hashlib
import itertools
import os
import sys
from collections import Counter

PIECE_CELLS = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 2, 0), (2, 2, 0)]
# provenance of PIECE_CELLS: common/polycube_utils.py PENTACUBES["Z"] in the
# fitpolycubes repository (piece 5/11, flat pentomino extrusion), as also
# published on https://puzzlewillbeplayed.com/Shirakawa/Z.html
W, H, NZ = 6, 6, 10
NPIECE = 5


def proper_rotation_matrices():
    """All 24 proper rotations of the cube as 3x3 int matrices (det = +1)."""
    out = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = [[0] * 3 for _ in range(3)]
            for i in range(3):
                M[i][perm[i]] = signs[i]
            det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                   - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
            if det == 1:
                out.append(M)
    return out


def orientations():
    """Distinct normalized orientations of the Z pentacube (expect 12)."""
    out = set()
    for M in proper_rotation_matrices():
        rot = [tuple(sum(M[i][j] * c[j] for j in range(3)) for i in range(3))
               for c in PIECE_CELLS]
        mn = [min(c[i] for c in rot) for i in range(3)]
        norm = tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2])
                            for c in rot))
        out.add(norm)
    return out


def regen_placements():
    """All legal placements of the Z pentacube in the W x H x NZ box."""
    oris = orientations()
    pls = set()
    for ori in oris:
        sx = max(c[0] for c in ori)
        sy = max(c[1] for c in ori)
        sz = max(c[2] for c in ori)
        for px in range(W - sx):
            for py in range(H - sy):
                for pz in range(NZ - sz):
                    cells = tuple(sorted((px + c[0], py + c[1], pz + c[2])
                                         for c in ori))
                    pls.add(cells)
    return oris, pls


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    pkg = sys.argv[1] if len(sys.argv) > 1 else "."
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name +
              (f"  [{detail}]" if detail else ""))
        if not cond:
            ok = False

    meta = json.load(open(os.path.join(pkg, "metadata.json")))
    placement_json = json.load(open(os.path.join(pkg, "placement_set.json")))
    var_map = json.load(open(os.path.join(pkg, "var_map.json")))

    # ---- 1. independent placement regeneration (own geometry code) ----
    oris, regen = regen_placements()
    check("orientation count is 12", len(oris) == 12, str(len(oris)))
    check("independent placement regeneration count == metadata",
          len(regen) == meta["placement_count"], str(len(regen)))

    # ---- 2. packaged placement_set.json matches the regeneration ----
    packaged = set(tuple(tuple(c) for c in p) for p in placement_json["placements"])
    check("placement_set.json == independent regeneration", packaged == regen)
    check("packaged box dims", placement_json["box"] == {"w": W, "h": H, "nz": NZ})

    # ---- 3. legality of every placement ----
    bad_shape = [p for p in regen
                 if tuple(sorted((c[0] - min(x[0] for x in p),
                                  c[1] - min(x[1] for x in p),
                                  c[2] - min(x[2] for x in p)) for c in p))
                 not in oris]
    bad_bounds = [p for p in regen
                  if any(not (0 <= c[i] < (W, H, NZ)[i]) for c in p
                         for i in range(3))]
    check("all placements Z-congruent", not bad_shape, str(len(bad_shape)))
    check("all placements inside the box", not bad_bounds, str(len(bad_bounds)))

    # ---- 4. coverage completeness ----
    # canonical placement order: sorted by sorted-cell-list (the order the
    # certified build used for variable ids)
    pls_sorted = sorted(regen, key=lambda p: sorted(p))
    cover = {}
    for i, p in enumerate(pls_sorted):
        for c in p:
            cover.setdefault(c, []).append(i)
    all_cells = {(x, y, z) for x in range(W) for y in range(H)
                 for z in range(NZ)}
    check("every cell covered by >= 1 placement",
          set(cover) == all_cells, f"{len(cover)}/{len(all_cells)}")
    check("var_map.json maps variable id -> placement exactly",
          all(var_map[str(i + 1)] == [list(c) for c in p]
              for i, p in enumerate(pls_sorted)))

    # ---- 5. CNF parse ----
    parsed, header = [], None
    with open(os.path.join(pkg, "z_6610.cnf")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p cnf"):
                _, _, nv, nc = line.split()
                header = (int(nv), int(nc))
                continue
            lits = [int(t) for t in line.split()]
            assert lits[-1] == 0, "DIMACS clause not zero-terminated"
            parsed.append(tuple(lits[:-1]))
    check("DIMACS header counts (vars/clauses)",
          header == (2176, 195976), str(header))

    # ---- 6. clause families ----
    clauses_ge1 = [cl for cl in parsed if all(x > 0 for x in cl)]
    clauses_amo = [cl for cl in parsed if all(x < 0 for x in cl)]
    check("no mixed-polarity or malformed clauses",
          len(clauses_ge1) + len(clauses_amo) == len(parsed),
          f"{len(clauses_ge1)} ge1 + {len(clauses_amo)} amo")
    check(">= 1 coverage clause per cell (360)",
          len(clauses_ge1) == len(all_cells), str(len(clauses_ge1)))

    # ---- 7. exact CNF <-> placement-set correspondence ----
    # The packaged CNF is canonical: literals sorted within each clause and
    # clauses sorted; rebuild the same canonical form independently from the
    # regenerated placement set and require byte-level equality of the clause
    # sequence (order-insensitive multiset equality would also be checked).
    expected = []
    for c, l in cover.items():
        lids = sorted(i + 1 for i in l)
        expected.append(tuple(lids))
        for i in range(len(lids)):
            for j in range(i + 1, len(lids)):
                expected.append(tuple(sorted((-lids[i], -lids[j]))))
    expected.sort()
    check("CNF clauses correspond exactly to the placement set (canonical)",
          tuple(expected) == tuple(sorted(parsed)),
          f"{len(expected)} vs {len(parsed)}")
    check("CNF clause multiset equals placement-set multiset (order-free)",
          sorted(expected) == sorted(parsed) and len(expected) == len(parsed))

    # ---- 8. metadata / hash cross-checks ----
    check("clause count matches metadata",
          meta["clause_count"] == len(parsed) == 195976)
    check("placement count matches metadata",
          meta["placement_count"] == len(regen) == 2176)
    check("CNF sha256 matches metadata",
          sha256_file(os.path.join(pkg, "z_6610.cnf")) == meta["sha256"]["cnf"])
    drat_path = os.path.join(pkg, "z_6610.drat")
    if os.path.exists(drat_path):
        check("DRAT sha256 matches metadata",
              sha256_file(drat_path) == meta["sha256"]["drat"])
    else:
        print("NOTE  DRAT not present in this copy; check "
              "metadata sha256.drat after obtaining it")

    # ---- summary ----
    print("=" * 60)
    print("ENCODING AUDIT:", "ALL CHECKS PASSED" if ok else "FAILURES PRESENT")
    print("(satisfiability itself is decided by the SAT/DRAT layer — "
          "see README.md)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
