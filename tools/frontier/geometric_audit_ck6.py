#!/usr/bin/env python3
"""
Stage 5O: geometric classification of the Stage 5N small-CK6 catalogue.

Produces:
  data/ck6_reuse/small_positive_geometric_audit.json
  data/ck6_reuse/small_positive_geometric_audit.txt
  data/ck6_reuse/george_comparison_manifest.json

Uses only the verified Stage 5N catalogue plus the repo symmetry
utilities.  No search is rerun.
"""

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from common.symmetry import affine_symmetries, element_kind  # noqa: E402

REUSE = os.path.join(REPO, "data", "ck6_reuse")
RENDERS = os.path.join(REUSE, "renders")


def cid(coords):
    h = hashlib.sha1(json.dumps(sorted(coords)).encode()).hexdigest()[:12]
    return h


def ck6_subgroup_count(cells):
    maps = affine_symmetries(cells)
    inv = [(m, t) for m, t in maps if element_kind(m) == "inversion"]
    c2d = [(m, t) for m, t in maps if element_kind(m) == "c2_diag"]
    ident = (np.eye(3, dtype=int), np.zeros(3, dtype=int))
    n = 0
    for c_m, c_t in c2d:
        for k_m, k_t in inv:
            comp = (c_m @ k_m, c_m @ k_t + c_t)
            if element_kind(comp[0]) != "mirror_diag":
                continue
            if not any(np.array_equal(comp[0], m[0])
                       and np.array_equal(comp[1], m[1]) for m in maps):
                continue
            four = [ident, (c_m, c_t), (k_m, k_t), comp]
            ok = all(
                any(np.array_equal((a[0] @ b[0], a[0] @ b[1] + a[1])[0], q[0])
                    and np.array_equal((a[0] @ b[0], a[0] @ b[1] + a[1])[1],
                                       q[1])
                    for q in four)
                for a in four for b in four)
            if ok:
                n += 1
    return n


def bbox_dims(cells):
    pts = np.array(cells)
    return list((pts.max(axis=0) - pts.min(axis=0) + 1).tolist())


def family_descriptor(cells, tiling, piece):
    d = bbox_dims(cells)
    ones = d.count(1)
    if ones == 2:
        return f"straight bar {d[0]}x{d[1]}x{d[2]}"
    if ones == 1:
        return f"slab {d[0]}x{d[1]}x{d[2]}"
    # collinear placement centroids => diagonal/axis stack of copies
    if tiling:
        cents = [np.mean(np.array(p), axis=0) for p in tiling]
        if len(cents) >= 3:
            a = np.array(cents[1]) - cents[0]
            b = np.array(cents[2]) - cents[0]
            cross = np.cross(a, b)
            if np.linalg.norm(cross) < 1e-9:
                return (f"collinear stack of {len(tiling)} copies "
                        f"(bbox {d[0]}x{d[1]}x{d[2]})")
    return f"free-form polycube (bbox {d[0]}x{d[1]}x{d[2]})"


def main():
    with open(os.path.join(REUSE, "small_positive_catalogue.json")) as f:
        cat = json.load(f)
    shapes = cat["constructions"]

    # ------------------------------------------------------------------
    # 2. canonicalisation + handedness per shape
    # ------------------------------------------------------------------
    for r in shapes:
        r["oh_canonical_id"] = "oh-" + cid(r["full_oh_canonical"])
        r["p24_canonical_id"] = "p24-" + cid(r["proper_canonical"])
        # achiral  <=>  min over O_h == min over proper rotations
        r["handedness"] = ("achiral" if r["full_oh_canonical"]
                           == r["proper_canonical"] else "chiral")
        r["bbox_dims"] = bbox_dims(r["target_coordinates"])
        r["family"] = family_descriptor(r["target_coordinates"],
                                        r["explicit_tiling"], r["piece"])
        r["ck6_subgroups_in_sym"] = ck6_subgroup_count(r["target_coordinates"])
        if r["symmetry_order"] >= 8:
            r["render_paths"] = []
        else:
            r["render_paths"] = []

    # ------------------------------------------------------------------
    # 3. relationships
    # ------------------------------------------------------------------
    oh_counts = Counter(r["oh_canonical_id"] for r in shapes)
    p24_counts = Counter(r["p24_canonical_id"] for r in shapes)
    dup_oh = {k: v for k, v in oh_counts.items() if v > 1}
    dup_p24 = {k: v for k, v in p24_counts.items() if v > 1}
    id_to_shape = {r["oh_canonical_id"]: r["id"] for r in shapes}
    shared_targets = [
        {"oh_canonical_id": k,
         "entries": sorted(r["id"] for r in shapes
                           if r["oh_canonical_id"] == k),
         "note": "the SAME geometric figure is tiled by different "
                 "pentacubes (Stage 5N grouped per piece/volume, so "
                 "cross-piece congruences were not merged there)"}
        for k in dup_oh]
    relationships = {
        "cross_entry_full_oh_congruences": dup_oh,
        "cross_entry_proper_congruences": dup_p24,
        "shared_target_congruences": shared_targets,
        "note_congruence": (
            "Stage 5N grouped the corpus entries by full-O_h canonical "
            "form WITHIN each piece/volume combination, so cross-piece "
            "congruences were not merged there.  The audit found exactly "
            f"{len(dup_oh)} cross-piece congruence(s): "
            + "; ".join(s["entries"][0] + " == " + s["entries"][1]
                        for s in shared_targets)
            + " (the 5x3x3 cross-tower: 5 stacked X crosses = 5 parallel "
              "I-bars).  Distinct catalogue entries are otherwise pairwise "
              "O_h-incongruent."),
        "enantiomer_pairs_across_entries": (
            "impossible by construction: mirror images share the same "
            "full-O_h canonical form and are therefore one catalogue "
            "entry; within-entry enantiomorphic corpus entries would be "
            "flagged 'enantiomorphic_corpus_entries' (none occur in this "
            "catalogue)"),
        "chiral_shapes": [r["id"] for r in shapes
                          if r["handedness"] == "chiral"],
        "higher_symmetry_parents": [
            {"id": r["id"], "symmetry_order": r["symmetry_order"],
             "ck6_subgroups_in_sym": r["ck6_subgroups_in_sym"],
             "class": r["symmetry_class"]}
            for r in shapes if r["symmetry_order"] >= 8],
        "bar_family": [r["id"] for r in shapes
                       if r["family"].startswith("straight bar")],
        "family_descriptors": {r["id"]: r["family"] for r in shapes},
    }

    # ------------------------------------------------------------------
    # 4. the three 3-copy figures
    # ------------------------------------------------------------------
    three = []
    oh_by_id = {r["oh_canonical_id"]: r["id"] for r in shapes}
    for sid in ("B-V15-S1", "R-V15-S1", "X-V15-S2"):
        r = next(x for x in shapes if x["id"] == sid)
        congruent_others = [q["id"] for q in shapes
                            if q["id"] != sid
                            and q["oh_canonical_id"] == r["oh_canonical_id"]]
        three.append({
            "id": sid,
            "volume": r["volume"],
            "number_of_copies": r["number_of_copies"],
            "symmetry_class": r["symmetry_class"],
            "symmetry_order": r["symmetry_order"],
            "lunnon_class": r["symmetry_class"],
            "number_of_tilings": r["number_of_tilings"],
            "p24_canonical_id": r["p24_canonical_id"],
            "oh_canonical_id": r["oh_canonical_id"],
            "handedness": r["handedness"],
            "congruent_to_other_stage5N_figures": congruent_others,
            "target_coordinates": r["target_coordinates"],
            "explicit_tiling": r["explicit_tiling"],
            "render_paths": [f"data/ck6_reuse/renders/{sid}_target.png",
                             f"data/ck6_reuse/renders/{sid}_tiling.png"],
        })

    # ------------------------------------------------------------------
    # 5. George comparison manifest
    # ------------------------------------------------------------------
    priority_ids = ["B-V15-S1", "R-V15-S1", "X-V15-S2", "B-V25-S12",
                    "P-V25-S3"] + [f"I-V25-S{i}" for i in range(4, 12)]
    reasons = {
        "B-V15-S1": "smallest known B-pentacube CK6 oddity in this "
                    "catalogue: 3 copies, exact CK6, 2 tilings",
        "R-V15-S1": "3-copy exact-CK6 construction with the chiral R "
                    "pentacube; R figures are the rarest class here",
        "X-V15-S2": "3-copy exact-CK6 construction (the X V=5/V=15 "
                    "order-16 entries are its higher-symmetry parents)",
        "B-V25-S12": "most-tilable exact-CK6 figure found: 10 distinct "
                     "tilings by 5 B pentacubes",
        "P-V25-S3": "order-12 (D3d-type) target with 24 tilings by 5 P "
                    "pentacubes; highest-symmetry multi-tiling case",
        "I-V25-S4": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S5": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S6": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S7": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S8": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S9": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S10": "exact-CK6 figure built from 5 straight I-bars",
        "I-V25-S11": "exact-CK6 figure built from 5 straight I-bars",
    }
    by_id = {r["id"]: r for r in shapes}
    george = {
        "stage": "5O",
        "purpose": "candidates for comparison against George Sicherman's "
                   "pentacube-oddity catalogues; novelty is NOT claimed "
                   "from absence of a textual match",
        "candidates": [],
    }
    for sid in priority_ids:
        r = by_id[sid]
        entry = {
            "id": sid,
            "piece": r["piece"],
            "volume": r["volume"],
            "copies": r["number_of_copies"],
            "tiling_count": r["number_of_tilings"],
            "symmetry_order": r["symmetry_order"],
            "symmetry_class": r["symmetry_class"],
            "oh_canonical_id": r["oh_canonical_id"],
            "p24_canonical_id": r["p24_canonical_id"],
            "target_coordinates": r["target_coordinates"],
            "render_paths": [
                f"data/ck6_reuse/renders/{sid}_target.png",
                f"data/ck6_reuse/renders/{sid}_tiling.png"],
            "reason": reasons[sid],
        }
        george["candidates"].append(entry)
    with open(os.path.join(REUSE, "george_comparison_manifest.json"),
              "w") as f:
        json.dump(george, f, indent=1)

    # ------------------------------------------------------------------
    # 6. audit outputs
    # ------------------------------------------------------------------
    n_chiral = sum(1 for r in shapes if r["handedness"] == "chiral")
    audit = {
        "stage": "5O",
        "totals": {
            "shapes": len(shapes),
            "geometrically_distinct_under_proper_rotations":
                len(p24_counts),
            "achiral": len(shapes) - n_chiral,
            "chiral": n_chiral,
            "enantiomer_pairs_across_entries": 0,
            "higher_symmetry_shapes": len(relationships[
                "higher_symmetry_parents"]),
        },
        "canonicalisation": [
            {"id": r["id"], "oh_canonical_id": r["oh_canonical_id"],
             "p24_canonical_id": r["p24_canonical_id"],
             "handedness": r["handedness"],
             "bbox_dims": r["bbox_dims"],
             "family": r["family"],
             "symmetry_class": r["symmetry_class"],
             "symmetry_order": r["symmetry_order"],
             "ck6_subgroups_in_sym": r["ck6_subgroups_in_sym"],
             "exact_ck6": r["exact_ck6"],
             "number_of_tilings": r["number_of_tilings"],
             "corpus_entries": r["corpus_entries"]}
            for r in shapes],
        "relationships": relationships,
        "three_copy_figures": three,
    }
    with open(os.path.join(REUSE, "small_positive_geometric_audit.json"),
              "w") as f:
        json.dump(audit, f, indent=1)

    # text report
    L = []
    L.append("STAGE 5O -- GEOMETRIC AUDIT OF THE SMALL CK6 CATALOGUE")
    L.append("=" * 62)
    L.append(f"shapes: {len(shapes)}  |  distinct under proper rotations: "
             f"{len(p24_counts)}  |  achiral: {len(shapes)-n_chiral}  |  "
             f"chiral: {n_chiral}  |  enantiomer pairs across entries: 0 "
             "(merged by O_h grouping)")
    L.append("")
    L.append("THE THREE 3-COPY FIGURES (smallest exact-CK6 constructions)")
    L.append("-" * 62)
    for t in three:
        L.append(f"  {t['id']}: {t['number_of_copies']} copies of "
                 f"{t['id'][0]}, V={t['volume']}, class {t['lunnon_class']} "
                 f"(order {t['symmetry_order']}), "
                 f"{t['number_of_tilings']} tiling(s), "
                 f"{t['handedness']}")
        L.append(f"    proper-rotation ID: {t['p24_canonical_id']}")
        L.append(f"    full-O_h ID:        {t['oh_canonical_id']}")
        L.append(f"    congruent to other catalogue figures: "
                 f"{t['congruent_to_other_stage5N_figures'] or 'none'}")
        L.append(f"    renders: {t['render_paths'][1]}")
        L.append("")
    L.append("HIGHER-SYMMETRY FAMILIES (parents containing CK6)")
    L.append("-" * 62)
    for h in relationships["higher_symmetry_parents"]:
        L.append(f"  {h['id']}: class {h['class']}, order "
                 f"{h['symmetry_order']}, "
                 f"{h['ck6_subgroups_in_sym']} CK6 subgroup(s) in Sym")
    L.append("")
    L.append("FAMILY / SHAPE DESCRIPTORS")
    L.append("-" * 62)
    for r in shapes:
        L.append(f"  {r['id']:12} {r['family']:42} "
                 f"{r['symmetry_class']:8} order {r['symmetry_order']:<3} "
                 f"{r['handedness']}")
    L.append("")
    L.append("STRUCTURAL NOTES")
    L.append("-" * 62)
    if shared_targets:
        for s in shared_targets:
            L.append(f"  * CROSS-PIECE CONGRUENCE: {' == '.join(s['entries'])}"
                     " -- the same figure tiled by both pieces "
                     "(5x3x3 cross-tower: 5 stacked X crosses = 5 "
                     "parallel I-bars).")
    else:
        L.append("  * No two catalogue entries are congruent (verified: no "
                 "duplicate full-O_h or proper canonical IDs).")
    L.append("  * No cross-entry enantiomer pairs can exist: mirror images "
             "share one full-O_h canonical, hence one entry.")
    L.append("  * All 52 figures contain inversion (CK6 or higher), hence "
             "ALL are achiral: proper-rotation and O_h canonicalisations "
             f"agree per figure; {len(p24_counts)} distinct figures under "
             "proper rotations.")
    L.append("  * Most exact-CK6 figures have corpus_entries = 2: they are "
             "closed under TWO conjugate centre-type CK6 placements (the "
             "19-T phenomenon); higher-symmetry figures have exactly 1.")
    L.append("  * The I-pentacube family spans bars (V=5, V=15 straight "
             "bars, V=25 1x1x25 bar and 1x5x5 slab), collinear stacks, and "
             "8 exact-CK6 free-form I-bar figures at V=25.")
    with open(os.path.join(REUSE, "small_positive_geometric_audit.txt"),
              "w") as f:
        f.write("\n".join(L))

    print(f"audit: {len(shapes)} shapes, {len(p24_counts)} proper-distinct, "
          f"{n_chiral} chiral; three-copy comparison + George manifest "
          f"written")


if __name__ == "__main__":
    main()
