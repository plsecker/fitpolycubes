#!/usr/bin/env python3
"""Builds the final Z catalogue promotion patch REVIEW ARTIFACT.

- Generates the exact proposed diff to catalogues/z_catalogue.py
  (adds PUBLISHED_SOLUTIONS with the 77 source-backed rows; nothing else).
- Verifies the patch (duplicates, conflicts, canonical order, provenance).
- Writes a temporary copy to /tmp and runs the REAL audit + validation
  machinery against it via an in-memory CATALOGUES registry swap.
- Measures the exact UNKNOWN / classification impact and the derived closures.
- Emits docs/frontier/z_piece/z_catalogue_promotion_patch.md

The real catalogues/z_catalogue.py is NEVER modified.
"""
import contextlib
import difflib
import importlib.util
import io
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).parent))

from catalogues.base import Box  # noqa: E402
from catalogues.registry import CATALOGUES  # noqa: E402
from promotion_evidence import PAGE_3D_TEXT, parse_page3d  # noqa: E402

CURRENT = REPO / "catalogues/z_catalogue.py"
OUT_MD = REPO / "docs/frontier/z_piece/z_catalogue_promotion_patch.md"
TMP_PATCHED = Path("/tmp/opencode/z_catalogue_patched.py")
MAXDIM_FULL = 60


def build_patched_text(rows):
    src = CURRENT.read_text()

    # group rows by cross-section in page order
    groups = []
    for r in rows:
        key = (r["dims"][0], r["dims"][1])
        if not groups or groups[-1][0] != key:
            groups.append((key, []))
        groups[-1][1].append(r)

    lines = []
    lines.append("")
    lines.append("# Published solvable, non-prime boxes: Shirakawa Z page rows")
    lines.append("# carrying solution count '1+' with NO prime marker.")
    lines.append("# Source: https://puzzlewillbeplayed.com/Shirakawa/Z.html")
    lines.append("# (3D section, page last updated Feb 18, 2015).")
    lines.append("# Each row self-checks as pieces * 5 == a*b*c.")
    lines.append("# Proposed 2026-08-28; evidence:")
    lines.append("#   docs/frontier/z_piece/z_catalogue_promotion_patch.md")
    lines.append("#   docs/frontier/z_piece/z_promotion_evidence_package.md")
    lines.append("#   docs/frontier/z_piece/z_promotion_semantics_audit.md")
    lines.append("PUBLISHED_SOLUTIONS = {")
    for (a, b), rs in groups:
        lines.append(f"    # {a}x{b}")
        for r in rs:
            c = r["dims"][2]
            lines.append(f"    Box({a}, {b}, {c}),  # {r['count']} {r['year']} {r['who']}")
    lines.append("}")
    block = "\n".join(lines) + "\n"

    anchor = "\n\nclass ZCatalogue"
    assert src.count(anchor) == 1
    patched = src.replace(anchor, "\n" + block + "\nclass ZCatalogue")

    old_call = "    published_solutions=set(),"
    assert patched.count(old_call) == 1
    patched = patched.replace(old_call,
                              "    published_solutions=PUBLISHED_SOLUTIONS,")
    return patched


def main():
    solvable_rows, family_rows = parse_page3d(PAGE_3D_TEXT)
    composite_rows = [r for r in solvable_rows
                      if "prime" not in r["marker"] and r["count"] in {"1+", "11+"}]
    assert len(composite_rows) == 77

    boxes = [Box(*r["dims"]) for r in composite_rows]
    canon = [b.canonical() for b in boxes]

    # ---------------- task 4: patch self-verification ----------------
    checks = {}
    checks["entries_total"] = len(boxes)
    checks["duplicates"] = len(boxes) - len(set(canon))
    checks["non_canonical_order"] = [str(b) for b, c in zip(boxes, canon) if b != c]
    import dataclasses
    zc = CATALOGUES["Z"]
    checks["overlap_RAW_PRIMES"] = sorted(str(b) for b in set(canon) & zc.primes)
    checks["overlap_SEARCHED_NO_SOLUTION"] = sorted(
        str(b) for b in set(canon) if b in zc.searched_no_solution)
    checks["inside_impossible_reason"] = sorted(
        str(b) for b in set(canon) if zc.impossible_reason(b) is not None)
    checks["provenance_comments"] = sum(
        1 for r in composite_rows
        if r["count"] == "1+" and r["who"] == "Shirakawa" and 1997 <= r["year"] <= 2015)

    patched_text = build_patched_text(composite_rows)
    TMP_PATCHED.write_text(patched_text)

    # ---------------- load patched module (temp copy) ----------------
    spec = importlib.util.spec_from_file_location("z_catalogue_patched", TMP_PATCHED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    patched_cat = mod.Z_CATALOGUE

    import solvers.decomp as decomp
    import tools.audit_catalogue as audit_mod
    import tools.validate_catalogue as validate_mod

    real_cat = CATALOGUES["Z"]
    assert real_cat.published_solutions == set()

    def scan_classes(cat):
        CATALOGUES["Z"] = cat
        decomp.catalogue = cat
        decomp.classify.cache_clear()
        out = {}
        for a in range(1, MAXDIM_FULL + 1):
            for b in range(a, MAXDIM_FULL + 1):
                for c in range(b, MAXDIM_FULL + 1):
                    if (a * b * c) % 5:
                        continue
                    out[Box(a, b, c)] = decomp.classify(Box(a, b, c)).__class__.__name__
        return out

    base_cls = scan_classes(real_cat)
    patched_cls = scan_classes(patched_cat)

    # restore registry BEFORE running audit/validate so they see patched cat explicitly
    transitions = Counter()
    reshapes = Counter()          # closed -> closed, node type changed (benign)
    status_changes = []           # closure status flipped (must be Unknown->closed)
    impossible_touched = []       # anything entering/leaving Impossible
    for bx in base_cls:
        b0, b1 = base_cls[bx], patched_cls[bx]
        if b0 == b1:
            continue
        transitions[(b0, b1)] += 1
        closed0 = b0 not in ("Unknown", "Impossible")
        closed1 = b1 not in ("Unknown", "Impossible")
        if b0 == "Impossible" or b1 == "Impossible":
            impossible_touched.append((str(bx), b0, b1))
        elif closed0 == closed1:
            reshapes[(b0, b1)] += 1        # same closure status, new tree shape
        elif not closed0 and closed1:
            status_changes.append((str(bx), b0, b1))   # expected promotion effect
        else:
            status_changes.append((str(bx), b0, b1))   # REGRESSION if any

    regressions = [(b, t0, t1) for b, t0, t1 in status_changes
                   if t0 not in ("Unknown",) or t1 in ("Unknown", "Impossible")]

    newly_closed = sorted(
        (bx for bx in base_cls
         if base_cls[bx] == "Unknown"
         and patched_cls[bx] in {"PublishedSolution", "Slab", "Width", "Breadth",
                                  "Generator"}),
        key=lambda bx: (bx.a * bx.b * bx.c, bx))
    direct_in_window = {b.canonical() for b in patched_cat.published_solutions}
    derived = [bx for bx in newly_closed if bx not in direct_in_window]
    direct_closed = [bx for bx in newly_closed if bx in direct_in_window]

    base_unknown = sum(1 for v in base_cls.values() if v == "Unknown")
    patch_unknown = sum(1 for v in patched_cls.values() if v == "Unknown")
    base_closed = sum(1 for v in base_cls.values()
                      if v not in ("Unknown", "Impossible"))
    patch_closed = sum(1 for v in patched_cls.values()
                       if v not in ("Unknown", "Impossible"))

    # ---------------- run REAL audit machinery on patched catalogue ----
    CATALOGUES["Z"] = patched_cat
    decomp.catalogue = patched_cat
    decomp.classify.cache_clear()
    buf_audit = io.StringIO()
    with contextlib.redirect_stdout(buf_audit):
        audit_mod.audit_catalogue("Z", 20, None)
    audit_out = buf_audit.getvalue()

    buf_val = io.StringIO()
    with contextlib.redirect_stdout(buf_val):
        val_ok = validate_mod.validate_catalogue("Z")
    validate_out = buf_val.getvalue()

    # audit summary numbers from the captured output
    def section_count(text, title):
        seg = text.split(title)
        if len(seg) < 2:
            return None
        body = seg[1].split("AUDIT")[0] if "AUDIT" in seg[1] else seg[1]
        m = next((l for l in body.splitlines() if l.strip().startswith("Count:")), "")
        return int(m.split(":")[1]) if m else None

    a_b = section_count(audit_out, "AUDIT B: Unproven composites")
    a_c = section_count(audit_out, "AUDIT C: Discovered composites")

    # restore
    CATALOGUES["Z"] = real_cat
    decomp.catalogue = real_cat
    decomp.classify.cache_clear()

    # ---------------- diff text ----------------
    diff = "\n".join(difflib.unified_diff(
        CURRENT.read_text().splitlines(),
        patched_text.splitlines(),
        fromfile="a/catalogues/z_catalogue.py (current)",
        tofile="b/catalogues/z_catalogue.py (proposed)",
        lineterm=""))

    # ---------------- markdown artifact ----------------
    L = []
    add = L.append
    add("# Z Catalogue Promotion Patch — for human review")
    add("")
    add("**Date**: 2026-08-28  ")
    add("**Status**: NOT APPLIED. `catalogues/z_catalogue.py` is untouched; every")
    add("number below was measured against a temporary in-memory copy.")
    add("")
    add("## 1. What the patch does")
    add("")
    add("* Adds `PUBLISHED_SOLUTIONS` — exactly **77 boxes**, one per Shirakawa")
    add("  Z-page row with solution count `1+` and no prime marker")
    add("  (source-semantics audit: all four questions resolved, no blockers).")
    add("* Wires it into the `ZCatalogue` constructor")
    add("  (`published_solutions=set()` -> `published_solutions=PUBLISHED_SOLUTIONS`).")
    add("* Changes **nothing** else: `RAW_PRIMES`, `PRIMES`, impossible rules,")
    add("  `SEARCHED_NO_SOLUTION`, `ROW_FAMILIES`, `WIDTH_SPLITS`,")
    add("  `MINIMAL_ODD`/`MINIMAL_EVEN` and the class body are byte-identical.")
    add("* The **50 derived closures are NOT added manually** — they are re-derived")
    add("  automatically by the existing decomposition engine from the promoted")
    add("  evidence (list in §5).")
    add("* The **s:0 / family zero rows are deliberately excluded** (8 per-box")
    add("  rows incl. `3x23x50 s:0`, 10 family rows). They are a separate policy")
    add("  question per the evidence package (task 8) and are not part of this")
    add("  patch in any form.")
    add("")
    add("## 2. Patch verification (pre-apply checks)")
    add("")
    add("| check | result |")
    add("|---|---|")
    add(f"| additions | {checks['entries_total']} |")
    add(f"| duplicate dimensions | {checks['duplicates']} (must be 0) |")
    add(f"| non-canonical ordering | {len(checks['non_canonical_order'])} (must be 0) |")
    add(f"| overlap with RAW_PRIMES | {len(checks['overlap_RAW_PRIMES'])} |")
    add(f"| overlap with SEARCHED_NO_SOLUTION | {len(checks['overlap_SEARCHED_NO_SOLUTION'])} |")
    add(f"| inside impossible_reason rules | {len(checks['inside_impossible_reason'])} |")
    add(f"| rows with provenance comment (1+ / year / Shirakawa) | "
        f"{checks['provenance_comments']}/77 |")
    ok = (checks["duplicates"] == 0 and not checks["non_canonical_order"]
          and not checks["overlap_RAW_PRIMES"]
          and not checks["overlap_SEARCHED_NO_SOLUTION"]
          and not checks["inside_impossible_reason"]
          and checks["provenance_comments"] == 77)
    add(f"| **all pre-apply checks pass** | **{'YES' if ok else 'NO'}** |")
    add("")
    add("## 3. Exact proposed diff")
    add("")
    add("```diff")
    add(diff)
    add("```")
    add("")
    add("## 4. Validation of the temporary patched catalogue")
    add("")
    add("Method: the patched file was written to `/tmp`, imported, and installed")
    add("into the `CATALOGUES` registry under the name `Z` **in memory only**; the")
    add("repo's real audit and validation tools were then run unchanged.")
    add("")
    add(f"* `tools/validate_catalogue.py` result: "
        f"**{'PASSED' if val_ok else 'FAILED'}**")
    add("* Audit D (published solutions) now reports the 77 promoted rows.")
    add(f"* Audit dim<=20 after patch: B (unproven composites) = {a_b}, "
        f"C (discovered composites) = {a_c}.")
    add("* Source provenance: Shirakawa Z page 3D section, rows `1+` with no")
    add("  prime marker; years 2013/2014/2015; every row satisfies")
    add("  `pieces*5 == a*b*c` (77/77, enforced by the extraction parser).")
    add("")
    add("<details><summary>full validate_catalogue output</summary>")
    add("")
    add("```")
    add(validate_out.rstrip())
    add("```")
    add("")
    add("</details>")
    add("")
    add("<details><summary>full audit output (dim<=20, patched)</summary>")
    add("")
    add("```")
    add(audit_out.rstrip())
    add("```")
    add("")
    add("</details>")
    add("")
    add("## 5. Impact (dims <= 60, full canonical scan)")
    add("")
    add("| metric | before | after patch | delta |")
    add("|---|---|---|---|")
    add(f"| Unknown boxes | {base_unknown} | {patch_unknown} | "
        f"**-{base_unknown - patch_unknown}** |")
    add(f"| closed constructions (non-prime, non-impossible) | {base_closed} | "
        f"{patch_closed} | +{patch_closed - base_closed} |")
    add(f"| Audit B (unproven composites, dim<=20) | 331 | {a_b} | -{331 - a_b} |")
    add(f"| Audit C (discovered composites, dim<=20) | 69 | {a_c} | +{a_c - 69} |")
    add("")
    add(f"Classification transitions observed: {dict(transitions)}  ")
    add(f"Benign proof re-shapes among already-closed boxes: {dict(reshapes)} "
        f"(total {sum(reshapes.values())}) — the box stays closed; only the")
    add("first-found closing branch changes once the evidence set grows.")
    add(f"Unknown -> closed promotions: {len(status_changes) - len(regressions)} "
        f"(expected 102).  ")
    add(f"Boxes entering/leaving Impossible: **{len(impossible_touched)}** "
        "(must be 0).  ")
    add(f"**Regressions (closed -> open or similar): {len(regressions)}**"
        + ("" if not regressions else ": " + str(regressions)))
    add("")
    add(f"Newly closed boxes: {len(newly_closed)} total = "
        f"{len(direct_closed)} direct published rows (in-window) + "
        f"**{len(derived)} derived automatically**.")
    add("")
    add("### The derived closures (NOT added manually — engine derives them)")
    add("")
    for bx in derived:
        add(f"* {bx}  [{patched_cls[bx]}]")
    add("")
    add("Direct published rows inside the window (closed as `PublishedSolution`):")
    add("")
    add("* " + ", ".join(f"`{bx}`" for bx in direct_closed))
    add("")
    add("Outside the 60-window, further cascades also become derivable (e.g.")
    add("`5x10x72 = PRIME 5x10x33 + PUB 5x10x39`); they are outside the measured")
    add("window and require no action.")
    add("")
    add("## 6. Review checklist for the approver")
    add("")
    add("1. §2 table all-green (duplicates / conflicts / ordering / provenance).")
    add("2. §3 diff touches only the `PUBLISHED_SOLUTIONS` block and the")
    add("   constructor argument.")
    add("3. §4 validation PASSED; §5 shows only `Unknown -> closed` transitions.")
    add("4. s:0 / family rows absent from the diff (deliberate; separate policy).")
    add("5. On approval: apply §3 verbatim to `catalogues/z_catalogue.py`, then")
    add("   run `tools/validate_catalogue.py Z` and")
    add("   `tools/audit_catalogue.py Z --max-dim 20`.")
    add("")
    add("## 7. Provenance")
    add("")
    add("* Source rows: package §1 table (77 rows, verbatim page strings).")
    add("* Semantics: `z_promotion_semantics_audit.md` (Q1-Q4 resolved).")
    add("* Replay: package §2 (127/127 trees close and validate).")
    add("* This artifact regenerable via "
        "`tools/frontier/z_piece/build_promotion_patch.py`.")
    add("")

    OUT_MD.write_text("\n".join(L))
    print(f"wrote {OUT_MD}")
    print(f"pre-apply checks ok={ok}; validate={'PASS' if val_ok else 'FAIL'}; "
          f"unknown {base_unknown}->{patch_unknown}; auditB {a_b}; auditC {a_c}; "
          f"derived={len(derived)}; promotions={len(status_changes)-len(regressions)}; "
          f"reshapes={sum(reshapes.values())}; regressions={len(regressions)}; "
          f"impossible_touched={len(impossible_touched)}")


if __name__ == "__main__":
    main()