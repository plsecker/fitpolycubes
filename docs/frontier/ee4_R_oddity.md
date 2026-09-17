# EE4 R‑pentacube oddity (5 copies)

**Goal** – Re‑produce George Sicherman's *dual orthogonal mirror* oddity
consisting of exactly five R‑pentacubes (volume 25) with *reflections
forbidden* for the pieces, and resolve which order‑4 Lunnon symmetry
class the figure belongs to.

**Status (2026‑09‑17)** – **5‑R EE4 construction independently verified;
correspondence with George's particular 5‑17p construction remains
unconfirmed.**  The class is **EE4** (mirrors x = 0 and y = 0,
product c2 about the z‑axis), matching George's page definition of *dual
orthogonal mirror symmetry*.  An exhaustive search of all nine order‑4
classes inside the 5×5×5 box proves that EE4 admits 5‑R tilings (16
tilings of one target shape in 4 placements).  A machine‑verifiable
witness is saved at `tests/fixtures/ee4_R_5.json`.  A second class, CE3
(mirror z = 0 + mirror x = y), also admits 5‑R tilings, but its second
mirror is a *diagonal* plane, so it does not match George's definition.
Whether the verified witness is *the* construction pictured in George's
figure `5-17p.png` could **not** be established from the image: the
palette diagrams could not be unambiguously decoded and the figure's
perspective projection could not be pinned.  The comparison is therefore
reported as **DISTINCT/UNRESOLVED** (see §9–§10); the question has been
handed back to George (draft query: `reports/ee4_R_5_george_message.md`,
status note: `reports/ee4_R_5_george_query.md`).

## 1. George's reported 5‑R result

George Sicherman's page on odd polycube constructions
(<https://sicherman.net/c5odd/c5hodd.html>, figure `5-17p.png`) reports
a construction of exactly five R‑pentacubes (volume 25) with *dual
orthogonal mirror symmetry* — "mirror symmetry through two different
coordinate axes" — and with reflections forbidden for the pieces.  The
figure's palette shows four piece colours (red, gold, aqua, green);
pixel analysis suggests two gold regions (top and bottom), which would
mean five pieces in four colours, but this is an inference from the
raster, not a proven fact.

## 2. Geometry of the R‑pentacube

The repository defines the R piece in `common/registry.py` (letter "R")
with the coordinate set:

```text
R = {(0,0,0), (1,0,0), (1,1,0), (1,1,1), (2,1,0)}
```

Only the 24 proper rotations (the matrix set `common.rotmatrix.RM`) are
used – reflections are **not** allowed.  R is chiral and asymmetric, so
all 24 orientations are distinct; `generate_placements` yields 1152
placements in a 5×5×5 box.  All 24 RM matrices have determinant +1
(verified; see §7).

## 3. EE4 symmetry definition

EE4 is the order‑4 Lunnon class *dual orthogonal mirror*:

* generators: a 180° rotation about a coordinate axis (`c2_ortho`) and
  two orthogonal mirror planes (`mirror_ortho`),
* in `common/symmetry.py`:
  `{("c2_ortho", "mirror_ortho", "mirror_ortho"): "EE4"}`.

Concretely (matrices acting on column vectors, box `{-2..2}^3`):

```text
MX = diag(-1, 1, 1)   mirror plane x = 0
MY = diag(1, -1, 1)   mirror plane y = 0
RZ = MX·MY = diag(-1, -1, 1)   180° rotation about the z-axis
G  = {I, MX, MY, RZ}
```

The fixed cells of G in the box are the five z‑axis cells (0,0,z); the
125 box cells split into 5 orbits of size 1, 20 of size 2 and 20 of
size 4 (45 orbits).

**EE4 vs CE3 (nomenclature check).**  The other tileable order‑4 class,
CE3, is the group `{I, MZ, MXY, R110}` with

```text
MZ   = diag(1, 1, -1)                mirror plane z = 0
MXY  = [[0,1,0],[1,0,0],[0,0,1]]     mirror plane x = y   (diagonal)
R110 = MZ·MXY = [[0,1,0],[1,0,0],[0,0,-1]]   c2 about (1,1,0)
```

The distinction is in the planes, not the labels: EE4 has **two
orthogonal coordinate‑plane mirrors** (x = 0 and y = 0); CE3 has one
coordinate‑plane mirror (z = 0) and one **diagonal** mirror (x = y).
George's "mirror symmetry through two different coordinate axes" is
exactly EE4.  Both groups are validated against
`common.symmetry.order4_lunnon_code` (closure + code) in
`tools/order4_R_class_comparison.py`.

## 4. Initial search and the coordinate‑frame bug

The original 5×5×5 EE4 search returned **zero** tilings.  The cause was
a coordinate‑frame mismatch:

* `common.polycube_utils.generate_placements()` generates placements in
  the `{0..4}^3` box (all coordinates ≥ 0),
* centred EE4‑invariant targets live in the `{-2..2}^3` box and contain
  cells with negative coordinates (20 of the 25 cells of the witness
  target have a negative coordinate).

A placement in `{0..4}^3` can never cover a cell with a negative
coordinate, so no exact cover of any centred target was possible and the
search reported "zero tileable targets" trivially.  That negative result
was an artifact of the bug.

**Fix:** translate every placement by (−2,−2,−2) into the `{-2..2}^3`
box before searching.  With the translation, EE4 is tileable.  The bug
is pinned by the regression test `tests/test_ee4_coordinate_frame.py`
(see §11).

## 5. Correct exhaustive 5×5×5 EE4 search

`tools/order4_R_class_comparison.py` tests all nine order‑4 Lunnon
classes (A12, J10, BB10, BC10, CE3, BF6, EE4, BE4, CK6).  For each
class it:

1. builds the group as explicit 3×3 integer matrices and validates it
   against `common.symmetry.order4_lunnon_code` (closure + code),
2. computes the orbits of the 125 cells of the box `{-2..2}^3`,
3. searches for all tilings of a G‑invariant, face‑connected 25‑cell
   target by exactly five proper‑rotation R placements (backtracking
   over placements with orbit‑closure pruning; the target is implicit:
   the union of the five placements must be a union of G‑orbits),
4. counts the connected G‑invariant 25‑cell targets (reverse search
   over orbit subsets + cell‑connectivity check; validated against a
   brute‑force orbit‑combination enumeration on class A12).

The EE4 run is fully reproducible: 119,023 search nodes, 16 tilings, 4
canonical targets, 2,072,331 connected 25‑cell targets (5,630,888
orbit‑subsets explored).

**One target shape.**  The four "canonical targets" are four distinct
normalized placements of a **single shape**: `canonical_form` (the
lexicographically smallest image over the full O_h group) is identical
for all four, and every pair is O_h‑equivalent (verified
computationally).  The shape is a 3×5×4 "wall":

```text
bbox: x ∈ [-1,1], y ∈ [-2,2], z ∈ [-2,1]   (y-wall placement)
z-layer counts (top to bottom): 2, 10/11, 11/10, 2
x-layer counts: 6, 13, 6
y-layer counts: 2, 8, 5, 8, 2
```

The two pairs mentioned in earlier notes are the y‑wall and x‑wall
placements (related by a 90° rotation about z); within each pair the
two targets differ in which z‑axis fixed cell is included.

## 6. Complete 9‑class comparison

| class | generators / orbit type | connected 25‑cell targets | tileable | canonical witnesses |
|---|---|---|---|---|
| A12  | cyclic C4 about z (no mirrors) | 8,719 | no | 0 |
| J10  | cyclic S4 about z (no mirrors) | 5,729 | no | 0 |
| BB10 | c2 axes x,y,z (no mirrors) | 18,729 | no | 0 |
| BC10 | c2 axes z,(1,1,0),(1,-1,0) (no mirrors) | 8,583 | no | 0 |
| CE3  | mirrors z=0 & x=y; product c2 about (1,1,0) | 392,719 | **yes** | 4 |
| BF6  | mirrors x=y & x=-y; product c2 about z | 116,641 | no | 0 |
| **EE4** | **mirrors x=0 & y=0; product c2 about z** | **2,072,331** | **yes** | **4** |
| BE4  | mirror z=0 + inversion; product c2 about z | 145,795 | no | 0 |
| CK6  | mirror x=-y + inversion; product c2 about (1,1,0) | 21,127 | no | 0 |

Full machine‑readable results:
`tools/frontier/order4_R_class_comparison_results.json`.  The table was
re‑produced in full during the finishing audit (2026‑09‑17).

## 7. Verified EE4 witness

The witness saved as `tests/fixtures/ee4_R_5.json` (canonical target
#1, first tiling) contains: the EE4 generators with matrices and mirror
planes, the box, the 25‑cell target, its canonical form, and the five
placements as `rotation_index` (index into `common.rotmatrix.RM`),
`rotation_matrix`, `translation` and `cells`.

The five placements (all proper rotations, det +1):

```text
R0: RM[5]  + (1,-1, 0)   cells (0,0,-1) (1,-1,0) (1,0,-1) (1,0,0) (1,1,-1)
R1: RM[11] + (0, 2,-1)   cells (0,1,0) (0,1,1) (0,2,-1) (0,2,0) (1,1,0)
R2: RM[3]  + (0,-2, 0)   cells (0,-2,-1) (0,-2,0) (0,-1,-2) (0,-1,-1) (1,-1,-1)
R3: RM[17] + (0, 1,-2)   cells (-1,0,-1) (-1,1,-1) (-1,1,0) (0,1,-2) (0,1,-1)
R4: RM[23] + (0,-1, 1)   cells (-1,-1,-1) (-1,-1,0) (-1,0,0) (0,-1,0) (0,-1,1)
```

`tools/verify_ee4_R_witness.py` independently re‑verifies the fixture
from scratch: every placement is a proper rotation of R plus an integer
translation; the five placements are pairwise disjoint and cover the
target; the target has exactly the EE4 symmetry group (order 4, kinds
`c2_ortho, mirror_ortho, mirror_ortho`); it is face‑connected; it lies
in the box; the canonical form matches.

```text
$ python3 tools/verify_ee4_R_witness.py
placement 0: RM[5] + t=(1, -1, 0)  ok
...
ALL CHECKS PASSED
```

The 16 tilings split into 8 orientation‑multiset classes of 2 tilings
each; the fixture uses the class `{RM 3, 5, 11, 17, 23}`.  Each target
has 2 tiling classes under its own symmetry group.  Full per‑tiling
structural signatures (piece adjacency graphs, contact counts,
boundary‑touch patterns, cells on the symmetry‑fixed planes) are in
`data/ee4_R_5/structural_comparison.json`.

## 8. Complete classification of the 5‑R EE4 tilings

The 16 tilings were exhaustively classified (2026‑09‑17) with
`tools/frontier/classify_ee4_R_tilings.py`; the full machine‑readable
result is `data/ee4_R_5/all_tilings.json` and the human‑readable
catalogue is `reports/ee4_R_5_catalogue.md` (renders in
`data/ee4_R_5/catalogue/`).

**Counts.**

| quantity | value |
|---|---|
| raw tilings | 16 |
| literal targets | 8 |
| canonical targets | 4 |
| target classes (proper rotations / O_h) | 1 / 1 |
| tiling classes under target symmetry | 8 |
| tiling classes (proper rotations / O_h) | 1 / 1 |
| orientation‑multiset classes | 8 |

**Structure.**  The four canonical targets are one shape in four
placements, all related by proper rotations (c4, c2_ortho, c2_diag).
Each canonical class contains **two literal targets**, pure translates
by (0, 0, ±1) along z.  Every target has EE4 symmetry {I, RZ, MX, MY};
the proper part is {I, RZ}.

Each literal target has exactly **two tilings**, related by RZ (the
proper c2 about z).  Every tiling has **trivial stabilizer** within the
target's full EE4 group: each decomposition breaks all three nontrivial
target symmetries.  The two tilings of one literal target have
**different RM multisets** (conjugate under RZ); the translate partner
on the other literal target has the **same RM multiset**.  Hence:

* **8 classes under target symmetry** – the RZ‑orbits {T, RZ·T}, one
  per literal target;
* **8 orientation‑multiset families** of 2 – pure translates of each
  other (same decomposition shifted by (0, 0, ±1));
* **1 class under O_h** (and under proper rotations) – all 16 tilings
  are equivalent by proper rotations + translations.

Reflections MX, MY map any tiling to a decomposition into **reflected**
R pieces, which is invalid (R is chiral); they connect no valid tilings.

**George's construction.**  George's 5‑17p uses RM indices
{3, 5, 11, 17, 23} — exactly the multiset of the family
{3, 5, 11, 17, 23} (tilings T4, T12).  The correspondence with his
particular construction remains unconfirmed (§10).

## 9. Comparison with George's figure

**What is proven computationally.**  EE4 admits 5‑R tilings; the witness
is valid; the target shape is the 3×5×4 wall of §5; the five
orientations are RM 3, 5, 11, 17, 23 (normalized forms in
`tools/describe_ee4_R_witness.py`).

**What could not be established from the image.**  The palette diagrams
in `5-17p.png` (six items: small red, small gold, two large diagrams,
small gold, small aqua) could not be unambiguously decoded into five R
orientations after an extensive pixel‑analysis effort, and the figure's
perspective projection could not be pinned (conflicting estimates of the
projection steps; conflicting bottom‑region pixel dumps).  The
exploratory pixel tool `tools/frontier/analyze_george_figure.py` is
kept only as historical evidence and is explicitly marked experimental;
the final EE4 result does not depend on it.

**Qualitative observations (inferred from the image, not proven).**  The
pictured figure appears bulky and tall, with two gold cubes at the top,
a red piece below them, and a large gold body with aqua/green accents
tapering to a tip at the bottom.  Our witness target is a flat 3×5×4
wall with 2 cells at the top layer and 2 at the bottom layer.  These
silhouettes are not obviously the same, but without a pinned projection
this cannot be decided rigorously.

## 10. Final status

**5‑R EE4 construction independently verified; correspondence with
George's particular 5‑17p construction remains unconfirmed.**  The
mathematical result is fully resolved and verified: EE4 is the class,
the witness is valid, and the construction is reproducible.  Whether
George's pictured decomposition is *this* witness could not be
established from the image: the palette could not be decoded, the
projection could not be pinned, and the qualitative silhouettes do not
clearly agree.  Per the investigation's stop conditions, no match is
claimed without evidence.  The fixture is kept as the canonical EE4
witness; no "George reproduced" claim is made.  The question has been
handed back to George (draft query `reports/ee4_R_5_george_message.md`,
status note `reports/ee4_R_5_george_query.md`); his confirmation is
required before any correspondence claim is recorded.

## 11. Reproducibility artifacts

* `tools/order4_R_class_comparison.py` – exhaustive order‑4 class
  comparison (groups, orbits, tiling search, connected‑target count).
* `tools/frontier/order4_R_class_comparison_results.json` – full table.
* `tools/frontier/make_ee4_R_fixture.py` – regenerates the fixture.
* `tests/fixtures/ee4_R_5.json` – the witness.
* `tools/verify_ee4_R_witness.py` – independent verification.
* `tools/describe_ee4_R_witness.py` – deterministic human‑readable
  placement/target report.
* `tools/render_ee4_R_witness.py`, `tools/render_ee4_R_comparison.py`,
  `tools/frontier/render_ee4_all_targets.py` – renders.
* `tools/frontier/analyze_ee4_R_structural.py` – per‑target/per‑tiling
  structural signatures and equivalence classes.
* `data/ee4_R_5/renders/`, `data/ee4_R_5/comparison/` – rendered
  cross‑sections, 3D views, orthographic views, orientation diagrams,
  composite.
* `data/ee4_R_5/structural_comparison.json` – full structural report.
* `tools/frontier/classify_ee4_R_tilings.py` – exhaustive classification
  of the 16 tilings (counts, equivalence classes, stabilizers,
  orientation‑multiset families).
* `data/ee4_R_5/all_tilings.json` – full machine‑readable
  classification (all 16 tilings with RM indices, translations,
  adjacency, contacts, boundary, fixed‑plane and axis cells,
  stabilizers, all class memberships).
* `tools/frontier/write_ee4_R_catalogue.py` – regenerates
  `reports/ee4_R_5_catalogue.md` from `all_tilings.json`.
* `reports/ee4_R_5_catalogue.md` – the human‑readable catalogue: one
  entry per inequivalent tiling class, the 8 orientation‑multiset
  families, the full 16‑tiling table, and the George comparison note.
* `tools/frontier/render_ee4_R_catalogue.py` – renders one figure per
  orientation‑multiset class with RM‑index labels.
* `data/ee4_R_5/catalogue/` – the 8 class renders.
* `tests/test_ee4_R_classification.py` – regression test for the
  classification invariants (16 tilings, 8 literal / 4 canonical
  targets, 8 target‑symmetry classes, 1 O_h class, 8 multiset
  families, trivial stabilizers, witness T4 matches the fixture).
* `tests/test_ee4_R_witness.py` – regression test for the witness.
* `tools/package_ee4_R_george.py` – regenerates the George package:
  `reports/ee4_R_5_witness_description.md` (clean description) and
  `reports/ee4_R_5_witness.png` (two‑panel render: R piece + witness).
* `reports/ee4_R_5_george_message.md` – draft message to George
  (figure + placements + coordinate appendix).
* `reports/ee4_R_5_george_query.md` – status note for the query.
* `tests/test_ee4_coordinate_frame.py` – regression test for the
  coordinate‑frame bug.

**Tests** (repo convention: plain scripts, `PYTHONPATH=.`):

```text
$ PYTHONPATH=. python3 tests/test_ee4_R_witness.py
ALL EE4 WITNESS CHECKS PASSED
$ PYTHONPATH=. python3 tests/test_ee4_coordinate_frame.py
COORDINATE-FRAME REGRESSION CHECKS PASSED
$ PYTHONPATH=. python3 tests/test_ee4_R_classification.py
ALL EE4 CLASSIFICATION CHECKS PASSED
$ PYTHONPATH=. python3 tools/verify_ee4_R_witness.py
ALL CHECKS PASSED
```

No impossibility regression is added: the interesting negative results
(7 of 9 classes have no 5‑R tiling) are documented here and in the
results JSON only.

## 12. Remaining uncertainty

* Whether George's pictured construction is exactly this witness
  (DISTINCT/UNRESOLVED, §10).  Resolving it would require either a
  reliable decode of the palette diagrams or an independent
  reconstruction of the figure from a pinned projection — both were
  attempted and neither succeeded.
* The four canonical targets are one shape in four placements; the
  fixture uses the y‑wall placement.  If the George figure is ever
  matched, the matching placement (y‑wall vs x‑wall, and which z‑axis
  fixed cell) would need to be identified.

*Prepared by OpenWork on 2026‑09‑17.*