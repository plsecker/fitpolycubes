#!/usr/bin/env python3
"""
Write the EE4 5-R tiling catalogue (Task 8 of the classification).

Reads data/ee4_R_5/all_tilings.json and writes
reports/ee4_R_5_catalogue.md: one entry per inequivalent tiling class
under target symmetry (8 classes), the orientation-multiset families
(8), the full 16-tiling table, and the George comparison note.

Usage: PYTHONPATH=. .venv/bin/python tools/frontier/write_ee4_R_catalogue.py
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DATA = os.path.join(REPO_ROOT, "data", "ee4_R_5", "all_tilings.json")
OUT = os.path.join(REPO_ROOT, "reports", "ee4_R_5_catalogue.md")

GEORGE_MS = [3, 5, 11, 17, 23]  # RM indices of George's 5-17p construction


def fmt_rm(ms):
    return "{" + ", ".join(str(i) for i in ms) + "}"


def fmt_adj(adj):
    return " / ".join("[" + ",".join(str(i) for i in row) + "]"
                      for row in adj)


def fmt_contacts(c):
    return " / ".join("[" + ",".join(str(i) for i in row) + "]"
                      for row in c)


def fmt_boundary(b):
    parts = []
    for k in ("x-", "x+", "y-", "y+", "z-", "z+"):
        parts.append(f"{k}:{b.get(k, [])}")
    return " ".join(parts)


def fmt_fixed(f):
    return " / ".join("[" + ",".join(str(i) for i in row) + "]"
                      for row in f)


def fmt_axis(a):
    return " / ".join(str(row) if row else "–" for row in a)


def main():
    with open(DATA) as f:
        data = json.load(f)

    counts = data["counts"]
    tilings = {t["id"]: t for t in data["tilings"]}
    targets = {t["canonical_index"]: t for t in data["targets"]}

    # literal-target label per tiling: which of the two translates
    lit_label = {}
    for t in data["targets"]:
        lits = [set(tuple(c) for c in lt) for lt in t["literal_targets"]]
        for tid in t["tiling_ids"]:
            lt = set(tuple(c) for c in tilings[tid]["literal_target"])
            lit_label[tid] = "A" if lt == lits[0] else "B"

    lines = []
    add = lines.append

    add("# EE4 5-R tiling catalogue")
    add("")
    add("Complete classification of all tilings of 25-cell EE4-invariant "
        "targets by five copies of the chiral pentacube **R** inside the "
        "5×5×5 box. Reflections are forbidden (R is chiral); only proper "
        "rotations and translations of R are used.")
    add("")
    add("## Result")
    add("")
    add("We independently exhaustively classified all 5-R EE4 tilings:")
    add("")
    add(f"- **{counts['raw_tilings']} raw tilings** of "
        f"**{counts['literal_targets']} literal targets** "
        f"({counts['canonical_targets']} canonical targets, one shape).")
    add(f"- **{counts['tiling_classes_target_symmetry']} equivalence classes "
        "under target symmetry** (orbits of the proper subgroup "
        "{I, RZ} of the target's EE4 group).")
    add(f"- **{counts['tiling_classes_oh']} equivalence class under full "
        "cubic symmetry O_h** (also 1 under proper rotations alone).")
    add(f"- **{counts['orientation_multiset_classes']} orientation-multiset "
        "families** of 2 tilings each (pure translates of each other).")
    add("")
    add("## Verified counts")
    add("")
    add("| quantity | value |")
    add("|---|---|")
    add("| connected EE4-invariant 25-cell targets | 2,072,331 |")
    add("| orbit-subsets explored | 5,630,888 |")
    add("| search nodes | 119,023 |")
    add(f"| raw tilings | {counts['raw_tilings']} |")
    add(f"| literal targets | {counts['literal_targets']} |")
    add(f"| canonical targets | {counts['canonical_targets']} |")
    add(f"| target classes under proper rotations | "
        f"{counts['target_classes_proper_rotation']} |")
    add(f"| target classes under O_h | {counts['target_classes_oh']} |")
    add(f"| tiling classes under target symmetry | "
        f"{counts['tiling_classes_target_symmetry']} |")
    add(f"| tiling classes under proper rotations | "
        f"{counts['tiling_classes_proper_rotation']} |")
    add(f"| tiling classes under O_h | {counts['tiling_classes_oh']} |")
    add(f"| orientation-multiset classes | "
        f"{counts['orientation_multiset_classes']} |")
    add("")
    add("## Structure")
    add("")
    add("### Targets")
    add("")
    add("- The 4 canonical targets are all **proper-rotation-equivalent**: "
        "one shape in 4 placements (related by c4, c2_ortho, c2_diag).")
    add("- Each canonical class contains **2 literal targets**, pure "
        "translates by (0, 0, ±1) along z.")
    add("- Every target has EE4 symmetry of order 4: "
        "{I, RZ, MX, MY}; the proper part is {I, RZ} (c2 about z).")
    add("")
    add("### Tilings")
    add("")
    add("- Each literal target has exactly **2 tilings**, related by RZ "
        "(the proper c2 about z).")
    add("- Every tiling has **trivial stabilizer** within the target's full "
        "EE4 group: each decomposition breaks all three nontrivial target "
        "symmetries (RZ, MX, MY).")
    add("- The two tilings of one literal target have **different RM "
        "multisets** (conjugate under RZ).")
    add("- The translate partner on the other literal target has the "
        "**same RM multiset**.")
    add("- All 16 tilings are equivalent under proper rotations + "
        "translations: **1 class under O_h** (and under proper rotations).")
    add("")
    add("## The 8 classes under target symmetry")
    add("")
    add("Each class is an RZ-orbit {T, RZ·T} on one literal target. "
        "Renders: `data/ee4_R_5/catalogue/`.")
    add("")
    add("| class | tilings | canon | literal | RM multiset (T, RZ·T) | "
        "translate partner | render |")
    add("|---|---|---|---|---|---|---|")
    for cls in sorted(data["target_symmetry_classes"],
                      key=lambda c: c["tiling_ids"]):
        a, b = cls["tiling_ids"]
        ta, tb = tilings[a], tilings[b]
        canon = cls["canonical_target_index"]
        # translate partners: same multiset, other literal target
        partners = [t["id"] for t in data["tilings"]
                    if t["rm_multiset"] == ta["rm_multiset"]
                    and t["id"] != a]
        ms_tag = "M" + "_".join(str(i) for i in ta["rm_multiset"])
        add(f"| {a}, {b} | T{a}, T{b} | {canon} | "
            f"{lit_label[a]}/{lit_label[b]} | "
            f"{fmt_rm(ta['rm_multiset'])}, {fmt_rm(tb['rm_multiset'])} | "
            f"T{partners[0]} | `class_{ms_tag}.png` |")
    add("")
    add("## Orientation-multiset families (8)")
    add("")
    add("Each family pairs the two tilings with the same RM multiset; they "
        "are **pure translates** of each other (same decomposition, shifted "
        "by (0, 0, ±1) onto the other literal target of the same canonical "
        "class). They are *not* related by any target symmetry.")
    add("")
    add("| multiset | tilings | translation | canonical target |")
    add("|---|---|---|---|")
    for mc in sorted(data["orientation_multiset_classes"],
                     key=lambda m: m["tiling_ids"]):
        a, b = mc["tiling_ids"]
        tr = mc["relationship"]["translation"]
        add(f"| {fmt_rm(mc['multiset'])} | T{a}, T{b} | "
            f"({tr[0]}, {tr[1]}, {tr[2]}) | "
            f"{tilings[a]['canonical_target_index']} |")
    add("")
    add("## Full tiling table")
    add("")
    add("| id | canon | literal | RM multiset | piece translations | "
        "adjacency | contacts | boundary | fixed-plane cells | axis cells | "
        "stabilizer |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for t in sorted(data["tilings"], key=lambda t: t["id"]):
        trs = " / ".join("(" + ",".join(str(v) for v in p["translation"])
                         + ")" for p in t["pieces"])
        add(f"| T{t['id']} | {t['canonical_target_index']} | "
            f"{lit_label[t['id']]} | {fmt_rm(t['rm_multiset'])} | {trs} | "
            f"{fmt_adj(t['adjacency'])} | {fmt_contacts(t['contacts'])} | "
            f"{fmt_boundary(t['boundary_touch'])} | "
            f"{fmt_fixed(t['fixed_plane_counts'])} | "
            f"{fmt_axis(t['axis_cells'])} | "
            f"{', '.join(t['stabilizer_kinds'])} |")
    add("")
    add("## Relationship to George's 5-17p construction")
    add("")
    add(f"George's construction uses RM indices {fmt_rm(GEORGE_MS)} — "
        "exactly the multiset of the family "
        f"{fmt_rm(GEORGE_MS)} (tilings T4, T12). "
        "The 5-R EE4 construction is independently verified; the "
        "correspondence with George's particular 5-17p construction "
        "remains **unconfirmed** (his target and translations are not "
        "available to us).")
    add("")

    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("->", OUT)


if __name__ == "__main__":
    main()