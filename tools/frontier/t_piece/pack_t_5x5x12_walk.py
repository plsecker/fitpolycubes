#!/usr/bin/env python3
"""
Pack the existing T 5x5x12 primitive-cycle data (closure artifact
data/frontier/t_piece/t_5x5_certificate.json, primitive_cycles[0]) into the
frozen generic Macro-walk certificate format v1
(docs/frontier/macro_certificate_format.md,
semantics_id fitpolycubes.macro-walk/semantics-1).

STDLIB ONLY. The packer re-derives every stored value from the raw per-edge
fills and refuses to emit anything if any check fails:

  P1 fill coordinates in window bounds; pieces pairwise disjoint per edge
  P2 every piece congruent to the declared T geometry under det=+1 rotations
  P3 fills avoid source-state occupancy; slot 0 completed at each edge
  P4 shift(source + fill) == successor state; matches the artifact's path ids
  P5 lifted union is an exact disjoint cover of 5x5x12 (60 pieces)
  P6 terminal predecessor facts recomputed, never copied

Output: data/frontier/certificates/t_5x5x12_cycle01_macro_walk.json

The emitted file carries both `box_tiling` and its identical legacy alias
`placements` so tools/frontier/validate_t_macro_walk.py can consume it
directly alongside the generic Layer-A checkers.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import permutations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
SRC_DEFAULT = REPO / "data/frontier/t_piece/t_5x5_certificate.json"
OUT_DEFAULT = REPO / "data/frontier/certificates/t_5x5x12_cycle01_macro_walk.json"

A, B, Z = 5, 5, 12
NCELLS = A * B
GEOMETRY = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 2, 0]]  # registry T


class PackError(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise PackError(msg)


def perm_sign(p):
    s = 1
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                s = -s
    return s


def rotation_images(base):
    out = set()
    for p in permutations(range(3)):
        for signs in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),
                      (1, -1, -1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)):
            if perm_sign(p) * signs[0] * signs[1] * signs[2] != 1:
                continue
            img = [tuple(signs[i] * c[p[i]] for i in range(3)) for c in base]
            mn = [min(c[i] for c in img) for i in range(3)]
            out.add(tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2])
                                 for c in img)))
    return out


def popcount(x):
    return bin(x).count("1")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=SRC_DEFAULT)
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args()

    art = json.load(open(args.source))
    cyc = art["primitive_cycles"][0]
    path_ids = cyc["path"]
    edges = [e["concrete_placements"] for e in cyc["edges"]]
    require(len(edges) == Z and len(path_ids) == Z + 1 and path_ids[0] == 0
            and path_ids[Z] == 0,
            "artifact cycle must have 12 edges closing through state 0")

    orientations = rotation_images([tuple(c) for c in GEOMETRY])

    walk = [{"step": k, "l0": 0, "l1": 0} for k in range(Z + 1)]
    cur0 = cur1 = 0
    lifted = []
    terminal_pieces = None
    for k, fills in enumerate(edges):
        allcells = []
        for pc in fills:
            require(len(pc) == 5, f"edge {k}: piece size != 5")
            cells = [tuple(c) for c in pc]
            for (x, y, dz) in cells:
                require(type(x) is int and type(y) is int and type(dz) is int,
                        f"edge {k}: non-integer cell")
                require(0 <= x < A and 0 <= y < B and dz in (0, 1, 2),
                        f"edge {k}: cell {(x, y, dz)} out of window bounds")
            mn = [min(c[i] for c in cells) for i in range(3)]
            canon = tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2])
                                 for c in cells))
            require(canon in orientations,
                    f"edge {k}: piece not congruent to declared T geometry")
            allcells += cells
        require(len(set(allcells)) == len(allcells),
                f"edge {k}: overlapping pieces")
        occ = {(x, y, d) for d in (0, 1) for x in range(A) for y in range(B)
               if ((cur0 if d == 0 else cur1) >> (x + A * y)) & 1}
        require(not (set(allcells) & occ), f"edge {k}: hits occupied cell")
        slot0 = {x + A * y for (x, y, dz) in allcells if dz == 0}
        covered = {i for i in range(NCELLS) if (cur0 >> i) & 1} | slot0
        require(len(covered) == NCELLS, f"edge {k}: slot 0 not completed")

        nxt0, nxt1 = cur1, 0
        for (x, y, dz) in allcells:
            cid = x + A * y
            if dz == 1:
                nxt0 |= 1 << cid
            elif dz == 2:
                nxt1 |= 1 << cid
        enc = nxt0 | (nxt1 << NCELLS)
        require(enc == path_ids[k + 1],
                f"edge {k}: recomputed successor {enc} != stored id "
                f"{path_ids[k + 1]}")
        walk[k + 1] = {"step": k + 1, "l0": nxt0, "l1": nxt1}
        cur0, cur1 = nxt0, nxt1
        lifted += [[[x, y, k + dz] for (x, y, dz) in pc] for pc in fills]
        if k == Z - 1:
            terminal_pieces = fills

    lifted_cells = [tuple(c) for p in lifted for c in p]
    require(len(lifted_cells) == len(set(lifted_cells)) == A * B * Z,
            "lifted fills are not an exact disjoint cover of 5x5x12")
    require(all(0 <= x < A and 0 <= y < B and 0 <= zz < Z
                for (x, y, zz) in lifted_cells), "lifted tiling out of bounds")

    pred_l0 = walk[Z - 1]["l0"]
    pred_l1 = walk[Z - 1]["l1"]
    remaining = NCELLS - popcount(pred_l0)
    final_flat = all(c[2] == 0 for pcs in terminal_pieces for c in pcs)
    comp = {i for i in range(NCELLS) if not (pred_l0 >> i) & 1}
    cov = set()
    covers = True
    for pcs in terminal_pieces:
        m = {x + A * y for (x, y, _) in pcs}
        if m & cov or not m <= comp:
            covers = False
            break
        cov |= m
    covers = covers and cov == comp

    cert = {
        "format": "fitpolycubes.macro-walk",
        "format_version": 1,
        "piece": {
            "name": "T",
            "geometry": GEOMETRY,
            "cell_count": 5,
        },
        "conventions": {
            "semantics_id": "fitpolycubes.macro-walk/semantics-1",
            "cell_id": "x + a*y, 0 <= x < a, 0 <= y < b",
            # legacy alias key carried by the five T cpsat witnesses; read by
            # tools/frontier/check_macro_certificate_independent.py (schema
            # allows additional convention properties)
            "piece_geometry": GEOMETRY,
            "state_packing":
                "state = l0 | (l1 << NCELLS); slot 2 always empty "
                "(nodes are post-shift states)",
            "rotations": "proper only (signed permutation matrices, det=+1)",
            "window_coords":
                "edge k fill pieces relative to layer k: (x,y,dz), "
                "dz in {0,1,2}; absolute cell = (x,y,k+dz)",
            "edge_legality_definition":
                "pieces of edge k must each be congruent to piece.geometry "
                "under proper rotation, be pairwise disjoint, avoid all cells "
                "occupied by state s_k, complete slot 0 of s_k, and "
                "shift(s_k + pieces) == s_{k+1}",
            "semantics_note":
                "machine-pinned identifier; the prose fields below are "
                "human-readable restatements of the same pinned semantics "
                "and are not parsed by checkers",
        },
        "box": {"a": A, "b": B, "z": Z},
        "walk": [
            {"step": s["step"], "l0": s["l0"], "l1": s["l1"],
             "hex": hex(s["l0"] | (s["l1"] << NCELLS))}
            for s in walk
        ],
        "edge_fills": edges,
        "box_tiling": lifted,
        "placements": json.loads(json.dumps(lifted)),  # identical alias for
        # validate_t_macro_walk.py; generic checker verifies alias equality
        "terminal": {
            "predecessor_state_index": Z - 1,
            "l0_popcount": popcount(pred_l0),
            "remaining_cells": remaining,
            "final_edge_all_slot0": bool(final_flat),
            "final_edge_covers_complement": bool(covers),
        },
        "provenance": {
            "generator":
                "tools/frontier/t_piece/pack_t_5x5x12_walk.py (fills "
                "re-derived and re-checked; nothing copied verbatim except "
                "placement triples)",
            "date": "2026-08-27",
            "source_artifact":
                "data/frontier/t_piece/t_5x5_certificate.json "
                "primitive_cycles[0] (= tools/frontier/_t_5x5_concrete_cycles"
                ".json): length-12 primitive closed Macro cycle of the "
                "complete T 5x5 closure (54,434 states, queue exhausted, "
                "cap_hit=false)",
            "solver": "repository macro-closure BFS (pre-audit artifact); "
                      "certificate re-verified post-repair by Layer-A/C++/"
                      "validate_t_macro_walk",
            "catalogue_context":
                "Box(5,5,12) is the sole 5x5 prime in RAW_PRIMES of "
                "catalogues/t_catalogue.py; impossible_reason declares "
                "(5,5,c%12!=0) published_impossible",
        },
        "claims": [
            {
                "id": "T-5x5-cycle-1",
                "statement":
                    "The Macro graph of the T pentacube on cross-section 5x5 "
                    "is cyclic: this certificate exhibits a closed Macro walk "
                    "of length 12 through state 0 (Layer A checks C1-C7g). By "
                    "the faithfulness theorem this is equivalent to "
                    "tileability of 5x5x12 by T.",
                "status": "PROVED COMPUTATION",
                "evidence": [
                    "this file (self-contained)",
                    "docs/frontier/macro_certificate_format.md",
                    "docs/frontier/t_macro_faithfulness.md",
                ],
                "checked_by": "tools/frontier/macro_certificate_generic_checker.py; "
                              "tools/frontier/check_macro_certificate_independent.py; "
                              "tools/frontier/macro_certificate_verifier.cpp",
            },
            {
                "id": "T-5x5-gate-instantiation",
                "statement":
                    "[Layer B, piece-specific; NOT checked by the generic "
                    "checker] The terminal predecessor walk[11] has "
                    "L1=L2=empty and its 20-cell L0-complement is exactly "
                    "covered by the four all-slot-0 flat-T placements of the "
                    "final edge, realizing the sufficient condition of the "
                    "repaired gate theorem (t_3xn_cyclicity_criterion.md "
                    "section 2). validate_t_macro_walk.py re-derives the walk "
                    "from the raw tiling against the repository transition "
                    "and performs an exhaustive exact-cover check of that "
                    "gate clause.",
                "status": "PROVED COMPUTATION",
                "evidence": [
                    "docs/frontier/t_piece/t_3xn_cyclicity_criterion.md",
                ],
                "checked_by": "tools/frontier/validate_t_macro_walk.py",
            },
            {
                "id": "T-5x5-scope-limits",
                "statement":
                    "[Layer C] This certificate proves existence only: it does "
                    "not prove that z=12 is minimal, it makes no claim about "
                    "solution counts, periods beyond the exhibited length, "
                    "pred(0) completeness for 5x5, or about acyclic "
                    "cross-sections elsewhere; catalogue truth tables were "
                    "not modified by this certification.",
                "status": "EMPIRICAL OBSERVATION",
                "evidence": [
                    "docs/frontier/macro_certificate_format.md section 8/9",
                ],
                "checked_by": None,
            },
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(cert, f, indent=1)
    print(f"packed OK -> {args.out}")
    print(f"  walk states: {len(cert['walk'])}, edges: {len(cert['edge_fills'])}"
          f", pieces: {len(lifted)}")
    print(f"  terminal: |L0|={popcount(pred_l0)} remaining={remaining} "
          f"L1_empty={pred_l1 == 0} final_all_slot0={final_flat} "
          f"covers_complement={covers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
