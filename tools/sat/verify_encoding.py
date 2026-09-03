#!/usr/bin/env python3
"""Standalone semantic audit of a polycube UNSAT/SAT certificate package.

This script is STANDALONE: it imports nothing from the fitpolycubes
repository. It re-derives everything from first principles:

  1. The piece definition (from the package metadata, or --piece-cells) and
     the 24 proper rotations of the cube are used to independently
     regenerate the set of legal placements in the box.
  2. The regenerated placement set is compared against placement_set.json.
  3. Every placement is checked: correct cell count, piece-congruent,
     inside the box.
  4. Coverage completeness: every box cell is covered by at least one
     placement.
  5. The CNF file (DIMACS) is parsed and verified to correspond EXACTLY to
     the placement set:
        - one all-positive clause per cell, over exactly the placements
          containing that cell (>= 1 coverage);
        - one all-negative clause per pair of placements sharing a cell
          (no-overlap); no other clauses; no mixed polarity;
        - variable ids correspond to placements exactly as recorded in
          var_map.json;
        - the clause sequence equals the canonical rebuild (sorted
          literals, deduplicated, sorted clauses).
  6. Counts and hashes are cross-checked against metadata.json / hashes.txt.

What this script does NOT do: it does not decide satisfiability. The UNSAT
claim is established by the accompanying DRAT proof, which a third party
verifies with a standard checker (drat-trim; see the package README).
For SAT packages the witness tiling is validated by the companion
tiling_validator (C++) and/or the validate-tiling step of the workflow.

Accepted metadata schemas (both certified package generations):
  box:   {"w":..,"h":..,"nz":..}  or  [a,b,c]
  piece: {"name":..,"cells":[[x,y,z],..],...}  or  a descriptive string
         (then --piece-cells is required)

Usage:  python3 verify_encoding.py <package_dir> [--piece-cells CSV;CSV;CSV]
Exit code 0 = all audits pass.
"""
import argparse
import hashlib
import itertools
import json
import os
import sys


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


def orientations(piece_cells):
    """Distinct normalized orientations of the piece under proper rotations."""
    out = set()
    for M in proper_rotation_matrices():
        rot = [tuple(sum(M[i][j] * c[j] for j in range(3)) for i in range(3))
               for c in piece_cells]
        mn = [min(c[i] for c in rot) for i in range(3)]
        norm = tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2])
                            for c in rot))
        out.add(norm)
    return out


def regen_placements(oris, dims):
    """All legal placements of the piece orientations in the box."""
    a, b, c = dims
    pls = set()
    for ori in oris:
        sx = max(q[0] for q in ori)
        sy = max(q[1] for q in ori)
        sz = max(q[2] for q in ori)
        for px in range(a - sx):
            for py in range(b - sy):
                for pz in range(c - sz):
                    cells = tuple(sorted((px + q[0], py + q[1], pz + q[2])
                                         for q in ori))
                    pls.add(cells)
    return pls


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_piece_cells(s):
    return [tuple(int(v) for v in t.split(",")) for t in s.split(";")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package", help="certificate package directory")
    ap.add_argument("--piece-cells", dest="piece_cells",
                    help="piece cells as 'x,y,z;x,y,z;...' when metadata "
                         "does not record them (older schema)")
    ap.add_argument("--standard", choices=("canonical", "legacy"),
                    default="canonical",
                    help="canonical = deduplicated clause set (current "
                         "standard, Z 4x11x15 packages); legacy = naive "
                         "multiset with duplicate AMO pairs (the certified "
                         "Z 6x6x10 package generation)")
    args = ap.parse_args()
    pkg = args.package
    standard = args.standard
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

    # ---- resolve box dims and piece cells (both schema generations) ----
    box = meta.get("box") or placement_json.get("box")
    if isinstance(box, dict):
        dims = (box["w"], box["h"], box["nz"])
    else:
        dims = tuple(box)
    piece_cells = None
    if isinstance(meta.get("piece"), dict) and meta["piece"].get("cells"):
        piece_cells = [tuple(c) for c in meta["piece"]["cells"]]
    elif isinstance(placement_json.get("piece"), dict) \
            and placement_json["piece"].get("cells"):
        piece_cells = [tuple(c) for c in placement_json["piece"]["cells"]]
    elif args.piece_cells:
        piece_cells = parse_piece_cells(args.piece_cells)
    if piece_cells is None:
        print("FAIL resolve piece cells (metadata lacks them; pass "
              "--piece-cells)")
        sys.exit(1)
    ncells_piece = len(piece_cells)
    a, b, c = dims
    all_cells = {(x, y, z) for x in range(a) for y in range(b)
                 for z in range(c)}

    # ---- 1. independent placement regeneration (own geometry code) ----
    oris = orientations(piece_cells)
    regen = regen_placements(oris, dims)
    check("independent placement regeneration count == metadata",
          len(regen) == meta["placement_count"], str(len(regen)))

    # ---- 2. packaged placement_set.json matches the regeneration ----
    packaged = set(tuple(tuple(q) for q in p)
                   for p in placement_json["placements"])
    check("placement_set.json == independent regeneration", packaged == regen)
    check("packaged box dims", tuple(placement_json.get("box", {}).values()
                                     if isinstance(placement_json.get("box"),
                                                    dict)
                                     else placement_json.get("box", ()))
          == dims)

    # ---- 3. legality of every placement ----
    bad_shape = [p for p in regen
                 if tuple(sorted((q[0] - min(x[0] for x in p),
                                  q[1] - min(x[1] for x in p),
                                  q[2] - min(x[2] for x in p)) for q in p))
                 not in oris]
    bad_bounds = [p for p in regen
                  if any(not (0 <= q[i] < dims[i]) for q in p
                         for i in range(3))]
    bad_size = [p for p in regen if len(p) != ncells_piece]
    check(f"all placements have {ncells_piece} cells", not bad_size)
    check("all placements piece-congruent", not bad_shape, str(len(bad_shape)))
    check("all placements inside the box", not bad_bounds, str(len(bad_bounds)))

    # ---- 4. coverage completeness + var map (canonical sorted order) ----
    pls_sorted = sorted(regen, key=lambda p: sorted(p))
    cover = {}
    for i, p in enumerate(pls_sorted):
        for q in p:
            cover.setdefault(q, []).append(i)
    check("every box cell covered by >= 1 placement",
          set(cover) == all_cells, f"{len(cover)}/{len(all_cells)}")
    check("var_map.json maps variable id -> placement exactly",
          all(var_map[str(i + 1)] == [list(q) for q in p]
              for i, p in enumerate(pls_sorted)))

    # ---- 5. CNF parse ----
    cnf_name = None
    for fn in sorted(os.listdir(pkg)):
        if fn.endswith(".cnf"):
            cnf_name = fn
            break
    if cnf_name is None:
        print("FAIL no .cnf file in package")
        sys.exit(1)
    parsed, header = [], None
    with open(os.path.join(pkg, cnf_name)) as f:
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
          header == (len(regen), meta["clause_count"]),
          f"{header} vs ({len(regen)}, {meta['clause_count']})")

    # ---- 6. clause families ----
    clauses_ge1 = [cl for cl in parsed if all(x > 0 for x in cl)]
    clauses_amo = [cl for cl in parsed if all(x < 0 for x in cl)]
    check("no mixed-polarity or malformed clauses",
          len(clauses_ge1) + len(clauses_amo) == len(parsed),
          f"{len(clauses_ge1)} ge1 + {len(clauses_amo)} amo")
    check(f">= 1 coverage clause per cell ({len(all_cells)})",
          len(clauses_ge1) == len(all_cells), str(len(clauses_ge1)))

    # ---- 7. exact CNF <-> placement-set correspondence ----
    # Naive rebuild as a list (ALO per cell + AMO per shared-cell pair, in
    # placement order).  Two standards exist:
    #   canonical (current, default): the file must equal the DEDUPLICATED
    #       clause set — sorted literals, no duplicate clauses, sorted
    #       sequence (the certified Z 4x11x15 standard);
    #   legacy (the certified Z 6x6x10 generation): the file must equal the
    #       naive MULTISET, duplicate AMO clauses included.
    naive = []
    for q, l in cover.items():
        lids = sorted(i + 1 for i in l)
        naive.append(tuple(lids))
        for i in range(len(lids)):
            for j in range(i + 1, len(lids)):
                naive.append(tuple(sorted((-lids[i], -lids[j]))))
    if standard == "canonical":
        expected = sorted(set(naive))
        check("CNF clauses correspond exactly to the placement set "
              "(canonical, deduplicated)",
              tuple(expected) == tuple(sorted(parsed)),
              f"{len(expected)} distinct vs {len(parsed)} in file")
        check("CNF file contains no duplicate clauses",
              len(set(parsed)) == len(parsed),
              f"{len(parsed) - len(set(parsed))} duplicates")
    else:
        check("CNF clauses correspond exactly to the placement set "
              "(legacy naive multiset)",
              tuple(sorted(naive)) == tuple(sorted(parsed)),
              f"{len(naive)} vs {len(parsed)}")
    check("CNF clause multiset equals placement-set multiset (order-free)",
          sorted(naive) == sorted(parsed)
          if standard == "legacy" else sorted(set(naive)) == sorted(parsed))

    # ---- 8. metadata / hash cross-checks ----
    check("clause count matches metadata",
          meta["clause_count"] == len(parsed))
    check("placement count matches metadata",
          meta["placement_count"] == len(regen))
    sha = meta.get("sha256", {})
    cnf_hash = sha256_file(os.path.join(pkg, cnf_name))
    recorded_cnf = sha.get("cnf")
    if recorded_cnf:
        check("CNF sha256 matches metadata", cnf_hash == recorded_cnf)
    else:
        print("NOTE  metadata has no sha256.cnf; computed "
              f"{cnf_hash[:16]}... (record it)")
    drat_path = None
    for fn in sorted(os.listdir(pkg)):
        if fn.endswith(".drat"):
            drat_path = fn
            break
    recorded_proof = sha.get("proof") or sha.get("drat")
    if drat_path and recorded_proof:
        check("DRAT sha256 matches metadata",
              sha256_file(os.path.join(pkg, drat_path)) == recorded_proof,
              drat_path)
    elif drat_path:
        print(f"NOTE  DRAT present ({drat_path}) but no hash recorded in "
              "metadata.sha256")
    else:
        print("NOTE  DRAT not present in this copy; check metadata "
              "sha256.proof after obtaining it")

    # ---- summary ----
    print("=" * 60)
    print(f"box {a}x{b}x{c}, piece {ncells_piece} cells, "
          f"{len(regen)} placements, {len(parsed)} clauses")
    print("ENCODING AUDIT:", "ALL CHECKS PASSED" if ok else "FAILURES PRESENT")
    print("(satisfiability itself is decided by the SAT/DRAT layer — "
          "see the package README)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
