#!/usr/bin/env python3
"""
Stage 5N: extract and catalogue all small CK6 positive constructions
(completed Stage 5L all-pentacube search, V <= 25).

Reads the Stage 5L results (data/ck6_reuse/run/v*_*/final.json and
data/ck6_reuse/piece_volume_results.jsonl), groups the recorded witnesses
into distinct target SHAPES (full-O_h congruence; the proper-rotation
canonical form is retained as the concrete tileable representative),
independently verifies every representative, and writes:

  data/ck6_reuse/small_positive_catalogue.json
  data/ck6_reuse/small_positive_catalogue.txt
  data/ck6_reuse/small_positive_render_manifest.json

No exhaustive search is rerun: only per-representative exact covers of
single small targets are recomputed (and dual-checked), exactly like the
Stage 5L witness spot checks.
"""

import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from common.algorithm_x import solve  # noqa: E402
from common.algorithm_x_fast import solve as solve_fast  # noqa: E402
from common.oddity import (  # noqa: E402
    is_face_connected,
    l1_ball,
    placements_in_region,
    unique_orientations,
)
from common.registry import PENTACUBES  # noqa: E402
from common.symmetry import (  # noqa: E402
    affine_symmetries,
    element_kind,
    full_symmetry,
    order4_lunnon_code,
    symmetry_order,
)

REUSE = os.path.join(REPO, "data", "ck6_reuse")


def domain_for(cells, margin=5):
    """L1 ball (min-origin frame) containing the target and every piece
    placement inside it.  Canonical representatives are NOT centered at
    the origin (e.g. the 1x1x25 bar spans L1 up to 24), so the domain
    radius is derived from the target itself, not a global constant."""
    r = max(sum(abs(v) for v in c) for c in cells) + margin
    return l1_ball(r)


def key(cells):
    return tuple(map(tuple, cells))


# ---------------------------------------------------------------------------
# 1. load positive witnesses
# ---------------------------------------------------------------------------

def load_positives(max_volume=25):
    combos = []
    for name in sorted(os.listdir(os.path.join(REUSE, "run"))):
        if not name.startswith("v"):
            continue
        volume = int(name[1:].split("_")[0])
        piece = name.split("_", 1)[1]
        if volume > max_volume:
            continue
        path = os.path.join(REUSE, "run", name, "final.json")
        with open(path) as f:
            fin = json.load(f)
        if fin["sat_count"]:
            combos.append(fin)
    # cross-check against the JSONL
    with open(os.path.join(REUSE, "piece_volume_results.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["volume"] > max_volume or not r["sat_count"]:
                continue
            match = [c for c in combos
                     if (c["volume"], c["piece"]) == (r["volume"], r["piece"])]
            assert match and match[0]["sat_count"] == r["sat_count"], r
    return combos


# ---------------------------------------------------------------------------
# 2. group witnesses into distinct shapes (full-O_h congruence)
# ---------------------------------------------------------------------------

def group_shapes(fin):
    """distinct shapes: key = full-O_h canonical form of the witness.

    Retains, per shape: corpus multiplicity, all proper-canonical forms
    (enantiomorphic corpus entries have different proper forms), covers,
    symmetry facts copied from the witnesses.
    """
    shapes = {}
    for w in fin["witnesses"]:
        k = key(w["canonical_target"])
        s = shapes.setdefault(k, {
            "full_canonical": w["canonical_target"],
            "proper_forms": set(),
            "corpus_entries": 0,
            "covers": set(),
            "symmetry_order": w["symmetry_order"],
            "symmetry_kinds": w["symmetry_kinds"],
            "symmetry_class": w["symmetry_class"],
            "volume": fin["volume"],
            "piece": fin["piece"],
            "tiles": fin["tiles"],
        })
        s["proper_forms"].add(key(w["canonical_target_proper"]))
        s["corpus_entries"] += 1
        s["covers"].add(w["number_of_covers"])
    for s in shapes.values():
        s["proper_forms"] = sorted(s["proper_forms"])
        s["covers"] = sorted(s["covers"])
    return shapes


# ---------------------------------------------------------------------------
# 4. independent verification of one representative
# ---------------------------------------------------------------------------

def ck6_subgroup_present(cells):
    """True iff the affine symmetry group contains a complete CK6
    subgroup {id, c2_diag, inversion, mirror_diag} (all elements share
    the figure centroid, so matrix-level closure is affine-consistent;
    verified with affine maps)."""
    maps = affine_symmetries(cells)
    inv = [(m, t) for m, t in maps if element_kind(m) == "inversion"]
    c2d = [(m, t) for m, t in maps if element_kind(m) == "c2_diag"]
    ident = (np.eye(3, dtype=int), np.zeros(3, dtype=int))
    for c_m, c_t in c2d:
        for k_m, k_t in inv:
            comp = (c_m @ k_m, c_m @ k_t + c_t)
            if element_kind(comp[0]) != "mirror_diag":
                continue
            if not any(np.array_equal(comp[0], m[0])
                       and np.array_equal(comp[1], m[1]) for m in maps):
                continue
            # closure check: composing any two of the four lands in the four
            four = [ident, (c_m, c_t), (k_m, k_t), comp]
            ok = True
            for a in four:
                for b in four:
                    p = (a[0] @ b[0], a[0] @ b[1] + a[1])
                    if not any(np.array_equal(p[0], q[0])
                               and np.array_equal(p[1], q[1]) for q in four):
                        ok = False
            if ok:
                return True
    return False


def all_covers(cells, piece):
    rows = placements_in_region(piece, domain_for(cells))
    rows = [p for p in rows if p <= set(cells)]
    y = {i: sorted(p) for i, p in enumerate(rows)}
    x = {c: set() for c in cells}
    for i, cs in y.items():
        for c in cs:
            x[c].add(i)
    sols = [sol for sol in solve(x, y) if len(sol) == len(cells) // 5]
    # dual-solver audit (Stage 4D convention)
    xf = {c: set() for c in cells}
    for i, p in enumerate(rows):
        for c in p:
            xf[c].add(i)
    yf = {i: list(p) for i, p in enumerate(rows)}
    n_fast = sum(1 for _ in solve_fast(xf, yf, set(cells), [True] * len(rows)))
    assert n_fast == len(sols), (len(sols), n_fast)
    return rows, sols


def verify_representative(piece, volume, cells, expected_covers):
    """Full independent verification; returns (tilings, checks dict)."""
    checks = {}
    piece_cells = [tuple(map(int, c)) for c in PENTACUBES[piece]]
    k = volume // 5
    checks["volume"] = len(cells) == volume == 5 * k
    checks["connected"] = is_face_connected(cells)
    syms = full_symmetry(cells)
    code = order4_lunnon_code(syms)
    checks["symmetry_order"] = symmetry_order(syms)
    checks["symmetry_class"] = (code if code is not None
                                else f"order{symmetry_order(syms)}")
    checks["ck6_or_higher"] = ck6_subgroup_present(cells)
    rows, sols = all_covers(cells, piece_cells)
    checks["covers"] = len(sols)
    checks["covers_match_witness"] = len(sols) == expected_covers
    # validate the first tiling explicitly; "valid proper orientation" is
    # decided by membership in the COMPLETE placement enumeration over a
    # containing domain (the same method used for the Stage 5L B/R spot
    # checks), which is exactly translates of unique_orientations(piece)
    tiling = None
    if sols:
        y = {i: sorted(p) for i, p in enumerate(rows)}
        placements = [frozenset(y[i]) for i in sols[0]]
        checks["tiling_count"] = len(placements) == k
        checks["tiling_disjoint"] = (
            sum(len(p) for p in placements) == volume
            and len(set().union(*placements)) == volume)
        checks["tiling_covers_target"] = set().union(*placements) == set(cells)
        complete = set(placements_in_region(piece_cells, domain_for(cells)))
        checks["tiling_valid_orientations"] = all(
            pl in complete for pl in placements)
        tiling = [sorted(p) for p in placements]
    return tiling, checks


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    combos = load_positives()
    catalogue = []
    rid = 0
    for fin in sorted(combos, key=lambda c: (c["piece"], c["volume"])):
        piece, volume = fin["piece"], fin["volume"]
        shapes = group_shapes(fin)
        for si, (fk, s) in enumerate(sorted(shapes.items()), start=1):
            rid += 1
            shape_id = f"{piece}-V{volume}-S{si}"
            # representative: lexicographically smallest proper form
            rep = min(s["proper_forms"])
            cells = {tuple(c) for c in rep}
            expected = s["covers"][0]
            assert len(s["covers"]) == 1, (shape_id, s["covers"])
            tiling, checks = verify_representative(piece, volume, cells,
                                                   expected)
            assert all(v for kk, v in checks.items()
                       if kk not in ("symmetry_order", "symmetry_class",
                                     "covers")), (shape_id, checks)
            enantiomers = len(s["proper_forms"]) > 1
            catalogue.append({
                "id": shape_id,
                "piece": piece,
                "volume": volume,
                "number_of_copies": volume // 5,
                "corpus_entries": s["corpus_entries"],
                "enantiomorphic_corpus_entries": enantiomers,
                "target_coordinates": sorted(cells),
                "proper_canonical": sorted(cells),
                "full_oh_canonical": [list(c) for c in fk],
                "symmetry_order": checks["symmetry_order"],
                "symmetry_class": checks["symmetry_class"],
                "exact_ck6": checks["symmetry_class"] == "CK6",
                "number_of_tilings": checks["covers"],
                "explicit_tiling": tiling,
                "verification": {k: v for k, v in checks.items()
                                 if k not in ("symmetry_order",
                                              "symmetry_class", "covers")},
            })
            print(f"verified {shape_id}: class={checks['symmetry_class']} "
                  f"order={checks['symmetry_order']} "
                  f"tilings={checks['covers']} "
                  f"corpus_entries={s['corpus_entries']} "
                  f"enantiomers={enantiomers}")

    # ------------------------------------------------------------------
    # 6. flags
    # ------------------------------------------------------------------
    by_piece = defaultdict(list)
    for r in catalogue:
        by_piece[r["piece"]].append(r)
    for r in catalogue:
        flags = []
        if r["exact_ck6"]:
            flags.append("exact-CK6 (order 4)")
        if r["symmetry_order"] >= 8:
            flags.append("higher-symmetry target")
        same_piece = [q for q in by_piece[r["piece"]] if q is not r]
        if not same_piece or r["volume"] == min(q["volume"] for q in
                                                [r] + same_piece):
            if r["volume"] == 15 or (r["piece"], r["volume"]) in \
                    (("I", 5), ("X", 5)):
                flags.append("smallest tile count for this piece")
        if r["corpus_entries"] > 1:
            flags.append("multiple corpus entries (conjugate CK6 placements)")
        if r["enantiomorphic_corpus_entries"]:
            flags.append("enantiomorphic corpus entries")
        if r["number_of_tilings"] > 1:
            flags.append("multiple distinct tilings")
        if sum(1 for q in by_piece[r["piece"]]
               if q["volume"] == r["volume"]) > 1:
            flags.append("multiple non-congruent shapes at this volume")
        r["flags"] = flags

    # ------------------------------------------------------------------
    # 5. write catalogue
    # ------------------------------------------------------------------
    os.makedirs(REUSE, exist_ok=True)
    cat = {
        "stage": "5N",
        "source": "completed Stage 5L all-pentacube search, V <= 25",
        "totals": {
            "positive_combinations": len({(r["piece"], r["volume"])
                                          for r in catalogue}),
            "distinct_shapes": len(catalogue),
            "corpus_entries": sum(r["corpus_entries"] for r in catalogue),
            "exact_ck6_shapes": sum(1 for r in catalogue if r["exact_ck6"]),
        },
        "constructions": catalogue,
    }
    with open(os.path.join(REUSE, "small_positive_catalogue.json"), "w") as f:
        json.dump(cat, f, indent=1)

    # text report: one section per piece, shapes grouped by volume
    lines = []
    lines.append("SMALL CK6 POSITIVE CONSTRUCTIONS -- Stage 5N catalogue")
    lines.append("=" * 60)
    lines.append(f"source: completed Stage 5L search, V <= 25 "
                 f"({cat['totals']['distinct_shapes']} distinct shapes, "
                 f"{cat['totals']['corpus_entries']} corpus entries, "
                 f"{cat['totals']['exact_ck6_shapes']} exact-CK6)")
    lines.append("")
    for piece in sorted(by_piece):
        lines.append(f"PIECE {piece}")
        lines.append("-" * 40)
        for volume in sorted({r["volume"] for r in by_piece[piece]}):
            for r in sorted((q for q in by_piece[piece]
                             if q["volume"] == volume),
                            key=lambda q: q["id"]):
                lines.append(f"  [{r['id']}]  {r['number_of_copies']} copies,"
                             f" {r['number_of_tilings']} tiling(s),"
                             f" class {r['symmetry_class']}"
                             f" (order {r['symmetry_order']}),"
                             f" corpus entries {r['corpus_entries']}"
                             f"{' [enantiomeric]' if r['enantiomorphic_corpus_entries'] else ''}")
                if r["flags"]:
                    lines.append(f"      flags: {'; '.join(r['flags'])}")
                lines.append(f"      target (proper canonical): "
                             f"{r['target_coordinates']}")
        lines.append("")
    with open(os.path.join(REUSE, "small_positive_catalogue.txt"), "w") as f:
        f.write("\n".join(lines))

    # ------------------------------------------------------------------
    # 7. render manifest (prioritised; do NOT render everything yet)
    # ------------------------------------------------------------------
    def priority(r):
        reasons = []
        if r["exact_ck6"]:
            reasons.append("exact CK6")
        reasons.append(f"volume {r['volume']}")
        if r["symmetry_order"] >= 8:
            reasons.append(f"high symmetry (order {r['symmetry_order']})")
        if r["number_of_tilings"] > 1:
            reasons.append(f"{r['number_of_tilings']} tilings")
        if r["corpus_entries"] > 1:
            reasons.append("conjugate CK6 placements")
        # strict lexicographic order per the Stage 5N brief:
        # 1. exact CK6  2. smallest volume  3. high symmetry  4. many tilings
        key = (0 if r["exact_ck6"] else 1,
               r["volume"],
               -r["symmetry_order"],
               -r["number_of_tilings"],
               r["id"])
        return key, reasons

    ranked = sorted(catalogue, key=lambda r: (priority(r)[0], r["id"]))
    manifest = {
        "stage": "5N",
        "note": "prioritised render list; not rendered yet",
        "priority_rule": "lexicographic: exact-CK6, then smallest volume, "
                         "then symmetry order, then tiling count",
        "render_list": [
            {
                "rank": i + 1,
                "id": r["id"],
                "piece": r["piece"],
                "volume": r["volume"],
                "reasons": priority(r)[1],
                "target_coordinates": r["target_coordinates"],
                "explicit_tiling": r["explicit_tiling"],
            }
            for i, r in enumerate(ranked[:12])
        ],
        "deferred": [r["id"] for r in ranked[12:]],
    }
    with open(os.path.join(REUSE, "small_positive_render_manifest.json"),
              "w") as f:
        json.dump(manifest, f, indent=1)

    print(f"\ncatalogue: {len(catalogue)} distinct shapes "
          f"({cat['totals']['exact_ck6_shapes']} exact-CK6); "
          f"render manifest top {len(manifest['render_list'])}, "
          f"deferred {len(manifest['deferred'])}")


if __name__ == "__main__":
    main()
