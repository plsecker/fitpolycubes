# Stage 5K — CK6 Symmetry Definition Audit

**Date:** 2026-09-08
**Scope:** forensic audit only. No search was launched, no historical result was
modified or deleted, no production solver code was changed.
**Verdict up front: the audit brief's premise is incorrect. The repository's
CK6 implementation matches the Sicherman/Lunnon source exactly. Source-defined
CK6 *is* the Klein four-group ⟨C, K⟩ containing inversion; the S4 rotoreflection
S(x,y,z) = (−y, x, −z) is a *different* Lunnon class, J10.**

---

## 1. Source definition

Sources inspected live (2026-09-08):

* `https://sicherman.net/csym/` — *Polycube Symmetries* (Lunnon codes), rev 2026-07-23.
* `https://sicherman.net/c5odd/c5nodd.html` — *Pentacube Oddities with Inverse/Diagonal
  Symmetry* (the CK6 class page), rev 2026-09-05.

**The 4-fold page says:**

> Polycubes have 9 types of quaternary symmetry. **The second type shown** is
> unusual: the transform that generates it consists of a 90° orthogonal rotation
> followed by reflection through the plane perpendicular to the axis of rotation.
> (Lunnon: A12, **J10**, BC10, BB10, **CK6**, BE4, CE3, BF6, EE4)

The unusual S4 rotoreflection described in the audit brief is the **second type
shown = J10**, *not* CK6 (the **fifth** type in the list). The audit brief
misattributed the description by reading the class list position incorrectly.

**The same page's subgroup table pins CK6's structure.** The CK6 row reads:
CK6 < C4 (plane-diagonal rotation), CK6 < K6 (inversion), CK6 < F5
(plane-diagonal mirror), CK6 ∥ J10, CK6 ∥ B6, CK6 ∥ E4. A group contained in
the diagonal-rotation, inversion, and diagonal-mirror 2-fold classes and
incomparable with the orthogonal-rotation class can only be the Klein
four-group **{1, c2_diag, inversion, mirror_diag}**.

**The CK6 class page says it in words:**

> Inverse/diagonal symmetry is **rotary symmetry through a plane diagonal axis
> plus inverse (point) symmetry**. It necessarily also entails plane diagonal
> mirror symmetry.

That is exactly ⟨C, K⟩ with C = 180° rotation about a face diagonal and
K = inversion; C·K is the perpendicular plane-diagonal mirror.

Recorded facts for source-defined CK6:

| property | value |
|---|---|
| point-group order | 4 |
| abstract structure | Klein four-group V4 (cyclic? **no**) |
| generators | C(x,y,z) = (y, x, −z); K(x,y,z) = (−x, −y, −z) |
| elements | I; C (c2_diag, det +1); K (inversion, det −1); CK = (−y, −x, z) (mirror_diag, det −1) |
| element orders | 1, 2, 2, 2 (all nontrivial elements are involutions) |
| inversion present? | **YES** |
| powers of a single generator | not applicable — no element has order 4 |

## 2. Current implementation

`common/symmetry.py` (the only place the group is constructed; every solver
imports it):

* `ck6_affine_maps(fixed_point)` builds exactly {E, C, K, CK} with
  C = (y, x, 2b−z), K = (2a−x, 2a−y, 2b−z), CK = K∘C — the V4 above, with
  integrality/distinctness/closure asserted at construction time.
* `order4_lunnon_code` maps the kind multiset {c2_diag, inversion, mirror_diag}
  → "CK6" and the cyclic-improper multiset {c2_ortho, s4, s4} → "J10".
* `common/oddity.py`, `solvers/t_ck6_oddity_search.py`,
  `solvers/t_ck6_oddity_v35_search.py`, `solvers/t_ck6_tower_v45.py`,
  `solvers/t_ck6_v55_search.py`, `solvers/t_ck6_canonical.py` all build the
  universe from `ck6_affine_maps((0,0))` — one shared definition, no local
  re-derivations anywhere (verified by reading every file; comments and names
  were not relied on).

Group order used everywhere: 4. Orbit construction: sizes {1 (center), 2 (axis
and mirror-plane cells), 4 (generic)}. −I is present in every constructed group.

## 3. Group comparison

Both candidate groups were built independently from their generators
(closure inside the 48 signed-permutation matrices):

**Group A — the brief's candidate ⟨S⟩, S(x,y,z) = (−y, x, −z):**

| matrix | det | trace | order | kind |
|---|---|---|---|---|
| I | +1 | 3 | 1 | identity |
| (−y, x, −z) | −1 | −1 | 4 | s4 (rotoreflection) |
| (−x, −y, z) | +1 | −1 | 2 | c2_ortho (180° about z) |
| (y, −x, −z) | −1 | −1 | 4 | s4 |

Order 4, **cyclic C4**, no inversion. This is Lunnon class **J10** (the repo's
own classifier returns `J10` for it).

**Group B — the repository's CK6 ⟨C, K⟩:**

| matrix | det | trace | order | kind |
|---|---|---|---|---|
| I | +1 | 3 | 1 | identity |
| (y, x, −z) | +1 | −1 | 2 | c2_diag |
| (−x, −y, −z) | −1 | −3 | 2 | inversion |
| (−y, −x, z) | −1 | 1 | 2 | mirror_diag |

Order 4, **V4**, contains inversion. Classifier returns `CK6`.

**The groups are NOT identical.** A ∩ B = {I} — they share nothing but the
identity. A is cyclic with two order-4 elements; B is elementary abelian with
none.

## 4. Inversion

**Source-defined CK6 contains central inversion: YES — unambiguously.**
Three independent confirmations: (a) the subgroup table row CK6 < K6;
(b) the class page's own words "plus inverse (point) symmetry"; (c) numerical
closure of ⟨C, K⟩ contains −I, while closure of ⟨S⟩ does not.

**S²(x,y,z) = (−x, −y, z) is a 180° proper rotation about the z-axis**
(det = +1, trace = −1, order 2) — *not* the inversion (−x, −y, −z), which has
det = −1, trace = −3. The brief's algebra here was correct; its class
attribution was not.

## 5. 9-cell fixture

`FIXTURE_9CELL` (the L-tricube oddity, fixed point (1,1,1)):

* complete affine symmetry group: order **4**, kinds exactly
  {identity, c2_diag, inversion, mirror_diag} → **source-CK6 invariant: YES**
  (exact class CK6, no supergroup);
* **inversion invariant: YES** (about (1,1,1));
* **S4-rotoreflection invariant: NO** — no s4 element exists in its symmetry
  group, and explicit S-about-x/y/z tests through (1,1,1) and (0,0,0) all fail;
* actual symmetry group found: CK6, order 4.

The fixture is genuine source-CK6. It was never valid as a J10 figure — and
never needed to be.

## 6. 19-T example

The published Sicherman 19-T / 95-cell figure
(`tools/frontier/_ck6_19T_sicherman_fixture.json`):

* full symmetry group: order **16**, kind census {identity, inversion ×1,
  c2_ortho ×3, c2_diag ×2, c4 ×2, mirror_ortho ×3, mirror_diag ×2, s4 ×2}
  = D4h about the prism axis = Lunnon **BBC2** (square box);
* element orders: fourteen involutions + four order-4 elements (2 c4, 2 s4);
* **inversion: present** (through the bbox centre (1,1,8));
* **source-CK6 generator (diagonal C2 + inversion + induced mirror): present —
  exactly 2 complete CK6 subgroups** inside Sym(U);
* the S4 rotoreflection about z through (1,1,8) is *also* a symmetry (2 J10
  subgroups) — the figure contains both classes as subgroups of BBC2;
* full rotational symmetry: the 8 proper rotations of D4h all present.

**The 19-T example is a genuine CK6-or-higher oddity under the source
definition.** The most important real-world sanity check passes.

## 7. Odd-volume implications

The project's argument — odd volume → inversion pairs all non-central cells →
one fixed centre cell → V = 4A + 2B + 1 — **is valid for source-defined CK6**,
because source CK6 *contains inversion*. Specifically:

* orbit sizes under the V4: 1, 2, 4 (census in the 7³ window: 72 four-orbits,
  27 two-orbits, 1 one-orbit — re-verified);
* K fixes exactly one lattice cell (the inversion centre), so an odd-volume
  K-closed target contains **exactly one** fixed cell: the centre cell.
  An odd CK6 target must have a central cell: **YES**;
* odd target volumes are possible: **YES** — V = 4A + 2B + 1 covers every odd
  V ≥ 1; with the T-pentacube constraint V ≡ 0 (mod 5): V ∈ {5, 15, 25, 35, …};
* the three non-centre fixed-point types f = (a,a,b), (a,b) ∈ {0,½}² \ {(0,0)}
  support even volumes only (no K-fixed cell) — unchanged;
* the L1-ball domain bound (oddity.py docstring proof) uses only K-closure and
  connectivity — both hold for source CK6.

Nothing in the odd-volume machinery needs to change. (Had the group been J10,
the inversion-pairing argument would have collapsed — but that group is not
CK6.)

## 8. Historical V=5..45 results

All five results were produced by code paths that construct the group solely
via `common.symmetry.ck6_affine_maps` (verified by reading each driver; the
V=35 shard driver, V=45 tower driver, and V=55 driver all import the same
function; `common/fastfunnel.py` / `common/packed_funnel.py` are
group-agnostic placement indexes). Inversion was imposed in every case
(K ∈ the constructed group), and source-defined CK6 was enforced.

| volume | searched group | orbit structure | inversion imposed | classification |
|---|---|---|---|---|
| V=5 | ⟨C,K⟩ V4 (design-doc argument: only 5-cell T-tilable target is T; EE4 ⊉ CK6) | n/a | yes | **VALID SOURCE-CK6 RESULT** |
| V=15 | ⟨C,K⟩ V4, center-type | 1/2/4 orbits, V=4A+2B+1 | yes | **VALID SOURCE-CK6 RESULT** (two independent methods agree) |
| V=25 | ⟨C,K⟩ V4, center-type | same | yes | **VALID SOURCE-CK6 RESULT** (71,539 targets, dual solver) |
| V=35 | ⟨C,K⟩ V4, center-type | same, sharded | yes | **VALID SOURCE-CK6 RESULT** (15,289,669 targets, report.json consistent) |
| V=45 | ⟨C,K⟩ V4, center-type | same, sharded | yes | **VALID SOURCE-CK6 RESULT** (1,469,999 targets, terminal partition exact) |

These may continue to be described as CK6 theorems. One caveat that is *not*
a validity issue: `tools/verify_ck6_oddity.py` (the standalone witness
auditor promised in the design doc) was never landed — but every result to
date is negative, so no historical claim depends on a witness audit.

## 9. Consequence for V=55

The V=55 architecture (`solvers/t_ck6_v55_search.py`: min-id sharded orbit
DFS + packed funnel + dual exact cover) targets **exactly the right problem**:
the universe is built from `ck6_affine_maps((0,0))`, the budget equation
2A + B = (V−1)/2 follows from the (valid) inversion orbit structure, and the
L1 ≤ 27 domain bound holds. The old V=55 plan remains mathematically valid and
is **not** invalidated by this audit.

Status note: `data/ck6_v55/status.txt` is a stale marker from 2026-09-07
("production running"); no search process is currently alive (verified via
`ps`; `shard_000.log` is 0 bytes). Nothing was relaunched during this audit.

## 10. Required correction

**No correction to the group definition, orbit generation, target enumeration,
funnel, or V=55 driver is required — the definition is proven correct against
the source.** The solver rewrite contemplated by the brief must **not** happen.

Exactly one next engineering task: **land `tools/verify_ck6_oddity.py` — the
independent witness auditor (re-deriving geometry from `common/registry.py` +
`RM`, checking partition, connectivity, Sym ⊇ CK6, and odd tile count) —
before the V=55 search is resumed**, so that a future positive witness is
independently verifiable. Regression coverage for the definition itself was
added during this audit:
`tools/frontier/test_ck6_definition_audit.py` (5 tests, all passing, including
the new 11-cell exact-J10 fixture `FIXTURE_J10_11CELL` demonstrating that the
S4 rotoreflection class is a genuinely different group).

---

## Appendix: new regression fixture (audit item 11)

`FIXTURE_J10_11CELL` = {(0,0,0), (0,0,±1)} ∪ {(1,0,1), (0,1,−1), (−1,0,1),
(0,−1,−1)} ∪ {(1,1,1), (−1,1,−1), (−1,−1,1), (1,−1,−1)} — 11 cells,
face-connected, exact symmetry group J10 = ⟨S⟩ (order 4, kinds
{c2_ortho, s4, s4}), verified: S(T) = S²(T) = S³(T) = S⁴(T) = T with
S⁴ = I, and inversion maps T to a *different* set (T is not
inversion-invariant). This fixture permanently pins the distinction between
J10 (the S4 rotoreflection class) and CK6 in the regression suite.

## Appendix: safety compliance

* No V=55 or V=65+ launch (stale runner confirmed dead; not restarted).
* No SAT runs, no long computations (all scripts complete in seconds).
* No historical result modified or deleted (`data/ck6_v*` untouched).
* No production solver modified — the only new files are
  `tools/frontier/test_ck6_definition_audit.py` and this report.
* Existing regression suite `tools/frontier/test_ck6_oddity.py` re-run: all
  17 tests pass.
