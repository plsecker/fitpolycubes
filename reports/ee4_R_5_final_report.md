# EE4 5‑R oddity — final verification report

**Date:** 2026‑09‑17 · **Branch:** `frontier-solutions` · **Scope:** finishing
pass on the EE4 R‑pentacube investigation.

**Bottom line.** The class is **EE4** (mirrors x = 0 and y = 0, product c2
about z), matching George Sicherman's "dual orthogonal mirror symmetry".
An exhaustive 5×5×5 search proves EE4 admits 5‑R tilings; a
machine‑verifiable witness is saved and independently re‑verified.  The
comparison against George's pictured figure is **DISTINCT/UNRESOLVED**:
the image's palette could not be decoded and its projection could not be
pinned, so no match is claimed.

## 1. Complete 9‑class comparison

| class | generators / orbit type | connected 25‑cell targets | tileable | canonical witnesses |
|---|---|---|---|---|
| A12  | cyclic C4 about z (no mirrors) | 8,719 | no | 0 |
| J10  | cyclic S4 about z (no mirrors) | 5,729 | no | 0 |
| BB10 | c2 axes x,y,z (no mirrors) | 18,729 | no | 0 |
| BC10 | c2 axes z,(1,1,0),(1,−1,0) (no mirrors) | 8,583 | no | 0 |
| CE3  | mirrors z=0 & x=y; product c2 about (1,1,0) | 392,719 | **yes** | 4 |
| BF6  | mirrors x=y & x=−y; product c2 about z | 116,641 | no | 0 |
| **EE4** | **mirrors x=0 & y=0; product c2 about z** | **2,072,331** | **yes** | **4** |
| BE4  | mirror z=0 + inversion; product c2 about z | 145,795 | no | 0 |
| CK6  | mirror x=−y + inversion; product c2 about (1,1,0) | 21,127 | no | 0 |

Reproduced in full during this pass; machine‑readable results in
`tools/frontier/order4_R_class_comparison_results.json`.

**EE4 vs CE3.**  EE4 has two orthogonal *coordinate‑plane* mirrors
(x = 0, y = 0).  CE3 has one coordinate‑plane mirror (z = 0) and one
*diagonal* mirror (x = y).  George's "mirror symmetry through two
different coordinate axes" is EE4.

## 2. Coordinate‑frame bug — cause and fix

**Cause.**  `common.polycube_utils.generate_placements()` generates
placements in the `{0..4}^3` frame (all coordinates ≥ 0), while centred
EE4‑invariant targets live in `{-2..2}^3` and contain cells with negative
coordinates (20 of the witness target's 25 cells).  A `{0..4}^3`
placement can never cover a negative‑coordinate cell, so the original
search was trivially unsatisfiable and reported zero tilings.

**Fix.**  Translate every placement by (−2,−2,−2) into `{-2..2}^3` before
searching.  With the fix, EE4 is tileable.

**Regression test.**  `tests/test_ee4_coordinate_frame.py` pins the bug:
it asserts the target has negative‑coordinate cells, that no raw
`{0..4}^3` placement can cover them, and that the translated placements
cover the target exactly.

## 3. Verified witness

`tests/fixtures/ee4_R_5.json` — canonical target #1, first tiling.
Target: 25 cells, face‑connected, exact EE4 symmetry (order 4, kinds
`c2_ortho, mirror_ortho, mirror_ortho`), bbox x[−1,1] y[−2,2] z[−2,1].
Five proper‑rotation R placements (RM indices 3, 5, 11, 17, 23),
pairwise disjoint, exact cover.

`tools/verify_ee4_R_witness.py` re‑verifies all of this from scratch:
**ALL CHECKS PASSED**.

**One target shape.**  The four "canonical targets" are four normalized
placements of a *single* shape (identical `canonical_form`; all pairs
O_h‑equivalent).  The 16 tilings split into 8 orientation‑multiset
classes of 2 tilings each; each target has 2 tiling classes under its own
symmetry.

## 4. George comparison — verdict and evidence

**Verdict: DISTINCT/UNRESOLVED.**

* The palette diagrams in `5-17p.png` could not be unambiguously decoded
  into five R orientations (six palette items, four colours; the
  projection was never pinned).
* The figure's perspective projection could not be pinned; bottom‑region
  pixel dumps conflicted between runs.
* Qualitatively, the pictured figure appears bulky/tall (two gold cubes
  on top, red below, large gold body tapering to a tip), whereas the
  witness target is a flat 3×5×4 wall (2 cells top layer, 2 bottom).
  The silhouettes do not clearly agree, but this is not conclusive
  without a pinned projection.

Per the stop conditions, no match is claimed.  The exploratory pixel tool
`tools/frontier/analyze_george_figure.py` is marked experimental and the
final result does not depend on it.

## 5. Files added / changed (this pass)

**Added**
* `tools/describe_ee4_R_witness.py`
* `tools/render_ee4_R_comparison.py`
* `tools/frontier/analyze_ee4_R_structural.py`
* `tests/test_ee4_R_witness.py`
* `tests/test_ee4_coordinate_frame.py`
* `data/ee4_R_5/comparison/` (10 renders: 3D, ortho x/y/z, 5
  orientations, composite, 4 target 3D views)
* `data/ee4_R_5/structural_comparison.json`
* `reports/ee4_R_5_final_report.md` (this file)

**Changed**
* `docs/frontier/ee4_R_oddity.md` — rewritten (11 sections)
* `tools/frontier/analyze_george_figure.py` — marked exploratory

**Pre‑existing EE4 artifacts (unchanged)**
* `tools/order4_R_class_comparison.py`,
  `tools/frontier/order4_R_class_comparison_results.json`,
  `tools/frontier/make_ee4_R_fixture.py`,
  `tools/verify_ee4_R_witness.py`, `tools/render_ee4_R_witness.py`,
  `tools/frontier/render_ee4_all_targets.py`,
  `tests/fixtures/ee4_R_5.json`, `data/ee4_R_5/renders/`.

Nothing was committed (per instruction).  Unrelated CK6/V45 working‑tree
changes were left untouched.

## 6. Test commands and results

```text
$ PYTHONPATH=. python3 tools/verify_ee4_R_witness.py
ALL CHECKS PASSED
target bbox: {'x': [-1, 1], 'y': [-2, 2], 'z': [-2, 1]}
search context: {'tilings_total': 16, 'canonical_targets': 4,
                 'nodes': 119023, 'seconds': 3.12}

$ PYTHONPATH=. python3 tests/test_ee4_R_witness.py
ALL EE4 WITNESS CHECKS PASSED

$ PYTHONPATH=. python3 tests/test_ee4_coordinate_frame.py
COORDINATE-FRAME REGRESSION CHECKS PASSED

$ PYTHONPATH=. python3 tools/frontier/analyze_ee4_R_structural.py
wrote data/ee4_R_5/structural_comparison.json
```

## 7. Remaining uncertainty

* Whether George's pictured construction is exactly this witness
  (DISTINCT/UNRESOLVED).  Resolving it needs a reliable palette decode or
  a pinned projection; both were attempted and neither succeeded.
* If ever matched, the matching placement (y‑wall vs x‑wall, and which
  z‑axis fixed cell) would still need to be identified.
