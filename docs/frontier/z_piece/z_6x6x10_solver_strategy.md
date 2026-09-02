# Z 6×6×10 Solver Strategy — Formulation Analysis

**Date**: 2026-08-28
**Scope**: find a fundamentally better exact-solving formulation for the Z box
`6×6×10`, after the hybrid DLX search (MRV, symmetry-broken, 3 workers,
3600 s) failed to exhaust even one depth-1 branch (~189M nodes on a single
subtree; >1.5B nodes total).

**Headline**: the box is now **decided — UNSAT — by a complete SAT decision**
(CaDiCaL, 287 s; independently reconfirmed under axis permutation, 306 s;
placement generation verified set-identical to the repository's trusted
generator). The planar-layer DP is the right *certificate/counting* layer but
its frontier is ~10⁶ states wide at 6×6 scale — too slow in pure Python, viable
as a Numba port. One measured engineering pitfall (numpy int64 bit-shift
overflow) is documented below because it silently corrupts any bitmask port.

No catalogue truth table was modified. The 6×6×10 outcome implies a
proposed (NOT applied) `SEARCHED_NO_SOLUTION` entry — see §6.

---

## 1. Geometric structure of Z in 6×6×10 (tasks 1–2)

The Z pentacube (5/11) is **flat**: cells `(0,0,0),(1,0,0),(1,1,0),(1,2,0),
(2,2,0)`, z-span 1. Under proper 3D rotations it has **12 orientations =
4 planar orientations × 3 planes**, and **every placement lies in a single
axis-parallel plane**:

| plane family | span | placements in 6×6×10 | per-layer cell pattern along z |
|---|---|---|---|
| xy (flat) | 1 z-layer | 64 masks × 10 layers = 640 | 5 cells, one layer |
| xz (fixed y) | 3 z-layers | 4 oris × 6 planes × 4 x-pos × 8 z-pos = 768 | (2,1,2) or (1,3,1) |
| yz (fixed x) | 3 z-layers | 4 oris × 6 planes × 4 y-pos × 8 z-pos = 768 | (2,1,2) or (1,3,1) |

Total **2,176 placements** — verified **set-identical** to the repository's
trusted `generate_placements` (2,176 = 2,176, frozenset equality).

**Layer decomposition exists**: a 3-layer frontier window suffices (no piece
reaches 3 layers past its start). Boundary state = `(L0, L1)` — the cells of
layers z, z+1 pre-filled by verticals — with `L2 = 0` at every boundary.
This is the same state model as the S-piece packed frontier
(`solvers/s_z_frontier_packed.py`: three 32-bit layer masks; here three
36-bit masks → 108-bit packed states, exceeding a uint64 — see §4 pitfall).

## 2. Structural reductions that hold (task 3)

* **Mandatory layer counts**: each piece covers each residue of
  `(x+y+z) mod 5` exactly once (measured from the cell set), and the box has
  exactly 72 cells per residue → no mod-5 obstruction. Per layer z, with
  `f_z` flat pieces and `vert_z` vertical cells: `36 = 5·f_z + vert_z`, so
  **`vert_z ≡ 1 (mod 5)`**, i.e. `vert_z ∈ {1,6,11,16,21,26,31,36}` and
  `f_z ∈ {7,6,5,4,3,2,1,0}`. Boundary layers draw only first/last-row
  contributions ({1,2} per piece), so `vert_0, vert_9 = 2a + b`.
* **Checkerboard**: 3/2 per piece; box 180/180; needs exactly 36 of 72
  pieces plus-heavy — satisfiable, no obstruction.
* **Axis parity**: each piece occupies each of its 3 columns an odd number of
  times; 72 pieces → even totals ✓ no obstruction.
* **Symmetry**: 16-fold (D4 of the 6×6 cross-section × z-mirror). Useful for
  canonicalising a certificate; the SAT encoding did not need it.
* **Connectivity**: automatic (pieces are connected by definition).
* **Orientation-count equations**: none beyond the layer counts above.

## 3. Candidate formulations, measured (tasks 4–5)

| # | formulation | measured behaviour on 6×6×10 / proxies | state space | exhaustive UNSAT? | certificate |
|---|---|---|---|---|---|
| F0 | hybrid DLX (repo, MRV+symmetry) | >1.5B nodes/60 min; one depth-1 branch alone >189M nodes — **not exhausted** | unbounded DFS | only if it terminates | tiling only |
| F1 | naive planar DP (lowest-cell DFS, fail-cache at boundaries) — prototype v1 | `6×6×5` proxy: 40M nodes/300 s, **1.4M distinct fail states**, incomplete | ~10⁶ states/boundary | yes in principle | yes (state table) |
| F1′ | vertical-first + in-plane oracle (v2/v3) | config enumeration explodes (2⁷⁶⁸ subsets; v3 coverage-driven still 23M vnodes for a single 5×5×5 boundary) | same | yes | yes |
| F2 | **SAT / CDCL** (pysat + CaDiCaL; ≥1-cover + pairwise-AMO over 2,176 placement vars; 195,976 clauses) | **UNSAT in 287 s**; axis-permuted `10×6×6` UNSAT 306 s; `5×5×5` UNSAT 0.0 s; `6×6×5` UNSAT 0.2 s; 13 thin boxes UNSAT (matches the theorem that the Z pentomino tiles no rectangle) | n/a (clause learning) | **yes — complete decision** | tiling witness (SAT); DRAT proof obtainable from CaDiCaL (UNSAT) |
| F2′ | CP-SAT (OR-Tools), same variables, `AddExactlyOne` | UNKNOWN on both 6×6×10 and 10×10×6 within 300 s (default workers) | n/a | yes with enough time | model / proof log |

Why F2 wins the decision role: the clause set is **monotone-safe** — it
contains only "cell covered by ≥1 placement" and "two overlapping
placements cannot both be used". Any true tiling satisfies every such
clause, so a *spurious UNSAT is impossible given a correct and complete
placement set* — and the placement set was verified equal to the repo
generator's. The remaining failure mode would be a CDCL engine bug, mitigated
by the axis-permuted rerun and the known-answer boxes (a Minisat22
cross-check was also launched; CaDiCaL's 287 s stands as the primary
evidence).

Why F1 is still worth keeping: for **SAT** instances the frontier DP yields
the repo-native layer-walk certificate (the S-piece methodology) and tiling
*counts*; the measured blocker is Python interpreter speed at ~10⁶-wide
frontiers, which a Numba port (fixed-size 3×36-bit state words — **two**
uint64s, see §4) addresses directly.

## 4. Measured engineering pitfall: numpy int64 bit-shift overflow

The prototype's placement masks were built via `1 << (y*w + x)` with
`y*w+x` an `np.int64` (inherited from the `RM` rotation matrices). numpy
shifts **wrap at bit 63**: any cross-section with more than 63 cells
(e.g. 10×10) silently produced corrupted masks (popcounts 0,1,2,3,4,37,74,…),
which in turn produced a bogus "SAT in 0.4 s with 93 garbage pieces" on
`10×10×6`. **6×6×10 is unaffected** (max bit index 35 < 63), as were all
known-answer boxes (max bit 24/35/59). Fixed by casting to Python ints;
any bitmask/DP port must use Python ints or split 64-bit words. This is
precisely why the S-piece 4×8 machinery (32-bit layers) does not transfer
to 6×6 by naive word-packing (3×36 = 108 bits > 64).

## 5. Recommended approach

1. **Decision engine: SAT/CDCL** (pysat + CaDiCaL). Encoding is 20 lines,
   placements are the audited 2,176, complete decisions in minutes.
   For UNSAT results this is already repository-grade evidence; for external
   verification, CaDiCaL can emit a DRAT proof checkable by `drat-trim`.
2. **Certificate/counting layer: planar frontier DP** (S-piece methodology,
   3×36-bit states) ported to Numba — recommended for SAT boxes to produce
   the repo-native layer-walk certificate and solution counts.
3. **Validation protocol for any future run** (adopted here): placement-set
   equality against `generate_placements`; known-answer boxes in both
   directions (`5×5×5`/`6×6×5` UNSAT by rule; a published-prime box SAT);
   axis-permutation agreement; second solver agreement where feasible.

## 6. Outcome for 6×6×10 and proposed catalogue change (NOT applied)

**`6×6×10` is not tileable** — proven by two complete SAT decisions
(`6×6×10` 287 s; `10×6×6` 306 s) over placements verified against the repo
generator, plus the monotone-safety argument. Consequences:

* The "+8 downstream closures" leverage from the frontier analysis is **dead**
  (it was conditional on solvability).
* The box leaves the Unknown frontier as *resolved-negative*.

**Proposed, NOT applied** (follows the S-catalogue precedent that a complete
search with no solution is recorded in `SEARCHED_NO_SOLUTION`; an exhaustive
complete-decision proof strictly dominates "empirical search"):

```python
SEARCHED_NO_SOLUTION = {
    # 6x6x10: exhaustive complete SAT decision (CaDiCaL, UNSAT 287s;
    # axis-permuted rerun 10x6x6 UNSAT 306s; placements verified identical
    # to generate_placements). 2026-08-28. See
    # docs/frontier/z_piece/z_6x6x10_solver_strategy.md
    Box(6, 6, 10),
}
```

Measured effect if approved: Audit B 320 → 319 (the box is inside the
dim ≤ 20 window); Unknown dim ≤ 60³ 10,468 → 10,467; no other classification
changes (the box is currently `Unknown`, appears in no closed tree).

## 7. Validation stack for the UNSAT claim (status)

| check | status |
|---|---|
| placement set ≡ repo `generate_placements` (frozenset equality) | ✅ 2,176 = 2,176 |
| complete decision (CaDiCaL 287 s) | ✅ |
| axis-permuted independent decision (`10×6×6`, 306 s) | ✅ |
| known-answer UNSAT boxes (`5×5×5`, `6×6×5`, 13 thin boxes — Z tiles no rectangle) | ✅ |
| known-answer SAT box (`6×10×10` / `10×10×6`, 120 pieces) | ⚠️ open — naive CDCL and CP-SAT exceed 300–900 s; published witness drawing unreachable from this VM; listed as follow-up |
| second solver (Minisat22) cross-run | ⚠️ did not finish within 1200 s (engine weaker than CaDiCaL); CaDiCaL's 287 s UNSAT stands as primary evidence |
| monotone-safety argument (spurious UNSAT impossible given correct placements) | ✅ (§3) |

## 8. Concrete next implementation steps

1. On approval, add the `SEARCHED_NO_SOLUTION` entry (§6) — one line.
2. For SAT-side validation: solve `6×10×10` with (a) CP-SAT + per-layer
   redundant cardinality constraints, or (b) `kissat` via a binary install,
   or (c) extract the published witness from the Shirakawa solution drawing
   (`html/Z-10x10x6.html`, reachable via a networked browser) and force it as
   assumptions in the SAT encoding — the witness then validates the full
   encode→solve→extract→validate chain against published ground truth.
3. Productise the planar frontier DP as `solvers/z_frontier_packed.py`
   (S-piece pattern, 2×uint64 state words, Numba core) for tiling counts and
   repo-native certificates on future SAT boxes.

## 9. Reproduction

```
# placement generator (fixed int-cast; see §4)
/tmp/opencode/z_layer_dp.py
# SAT decision engine
/tmp/opencode/z_sat.py        # solve_box(6,6,10) -> UNSAT in ~287 s
```
(Scratch prototypes under `/tmp/opencode/`; nothing in the repository's
solver or catalogue code was modified.)
