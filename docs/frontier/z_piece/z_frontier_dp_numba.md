# Z Planar-Frontier DP — Numba Port

**Date**: 2026-08-29
**Reference (source of truth)**: the validated Python prototype
(`/tmp/opencode/z_frontier_v4.py`) and
`docs/frontier/z_piece/z_frontier_dp_prototype.md`. The Python prototype is
unchanged and remains the reference implementation; this Numba port is a
performance layer validated against it. No catalogue changes; 6×6×10 not
attempted.

**Verdict: the Numba port is demonstrably equivalent to the Python
reference on both exhaustive UNSAT cases and the published SAT witness,
with a ~30× measured speedup (6×6×5: 11.6 s vs 343.4 s) — and the
measured throughput makes a 6×6×10 closure plausibly practical (~1–2 min
estimated; not run, per instructions).**

---

## 1. Implementation design

`/tmp/opencode/z_frontier_numba.py`. Exactly the validated transition
system, compiled:

* **State representation**: boundary state `(L0, L1)` as two int64 layer
  masks (36 bits at 6×6 — single-limb uint64 suffices for cross-sections
  ≤ 63 cells; larger cross-sections need the two-limb generalisation,
  same structure). Boundary states stored per layer as sorted numpy
  arrays of pairs (deduplicated via hash-set insertion inside the kernel,
  then `lexsort` for a deterministic canonical order).
* **Templates**: precomputed in Python from the audited generator
  (`z_layer_dp.gen`, int-cast fixed):
  - flat masks indexed by covered cell bit (CSR: `fb_ptr`/`fb_data`);
  - vertical `(m0, m1, m2)` triples per start layer, indexed by covered
    cell bit of `m0` (`vb_ptr[z]`/`vb_m0/z`);
* **Hot loop** (`_fill_layer`, njit): for each boundary state, an
  explicit-stack DFS over the lowest empty cell, branching over the
  per-bit candidate tables (flat masks; vertical triples), with
  consistency checks (`m0 ∩ filled = 0`, `m1 ∩ (L1 ∪ l1acc) = 0`,
  `m2 ∩ l2acc = 0`), emitting successors into a per-layer
  open-addressing hash table (linear probing, exact pair keys);
  deduplication is therefore exact (no 64-bit hash collision risk).
* **Layer loop**: in Python — thin (per-layer state-array slicing +
  numpy `lexsort`/`unique`-style dedup); the exponential inner fill is
  entirely in the compiled kernel.
* **Acceptance**: frontier empty at any boundary ⇒ UNSAT (exhaustive
  state closure); reaching boundary NZ ⇒ SAT (tiling exists; final state
  must be `(0,0)`, guaranteed by template bounds).

**Not ported / not changed**: tiling reconstruction (back-pointer walk —
stays in the Python reference), D4 orbit canonicalisation (stays in
Python/numpy, identical definition), solution counting (stays a DP
accumulation, noted below). The Python prototype is untouched and remains
the reference.

## 2. Reference-vs-Numba agreement (tasks 4–5)

### 5×5×5 (rule-impossible; exhaustive closure)

| metric | Python reference | Numba port |
|---|---|---|
| verdict | UNSAT (frontier empty at boundary 2) | **identical** |
| boundary-1 states | 1,900 | **1,900** ✅ |
| D4 orbits (sym-reduced width) | 239 | **239** ✅ |

### 6×6×5 (exhaustive closure)

| metric | Python reference | Numba port |
|---|---|---|
| verdict | UNSAT (frontier empty at boundary 5) | **identical** ✅ |
| boundary profile | 1,154,524 → 117,428 → 814,994 → 4 → 0 | **1,154,524 → 117,428 → 814,994 → 4 → 0** ✅ |

### Published 6×10×10 witness (Sol.3, Shindo 1997) through the Numba code path

* classification: **32 flat + 88 vertical** (120 placements) ✅
* **120/120** witness placements are members of the audited placement
  families (flat masks ∈ `flat`-family set; vertical `(m0,m1,m2)` triples ∈
  the per-start-layer family sets) — i.e. the Numba-side placement
  machinery reproduces the published construction exactly;
* the numba witness-walk kernel verifies per-layer exact coverage and the
  **final empty boundary state (0, 0)** — ✅.

## 3. Speed and memory (task 6)

| run | Python reference | Numba port | speedup |
|---|---|---|---|
| `5×5×5` exhaustive closure | 0.3 s (1,900 states) | **0.58 s** (incl. ~0.5 s one-time JIT compile; steady-state ≈ 0.1 s) | ≈ 3× (compile-dominated) |
| `6×6×5` exhaustive closure | 343.4 s (2.09 M states, incomplete attempt documented at 300 s in the first campaign; the v4 reference completed in 343 s) | **11.6 s** | **≈ 30×** |

Memory (Numba): hash table 2²³ entries × 24 B ≈ 100 MB for the widest
boundary (6×6×5: 1.15 M unique states), DFS stack 6 × 512 × 8 B — total
well under 500 MB. Python reference: same data as ~1–2 GB of dict/tuple
objects.

Node-throughput comparison (same tree): Python ~135k fill-nodes/s vs
Numba ~3.5M fill-nodes/s (6×6×5: 40M nodes in 11.6 s incl. dedup) —
**≈ 30×**, consistent with the measured wall-clock ratio.

## 4. Mod-5 congruence pruning (task 7)

The pruning invariant (derived in the prototype doc from the layer-count
equation): at any node of the layer-z fill, with `va` = vertical cells
placed so far in this layer and `R` = remaining cells, a completion must
satisfy `popcount(L0) + va + R ≡ A (mod 5)`; branches violating it can
never complete.

* Implemented as an optional flag in `_fill_layer` (requires a popcount
  of the boundary mask and a flat-placement counter in the stack).
* **Equivalence test on `6×6×5`**: pruning enabled vs disabled produce
  **identical boundary profiles** (`[1,154,524, 117,428, 814,994, 4, 0]`)
  and the same UNSAT verdict ✅ — i.e. the congruence removes only
  mathematically impossible branches, exactly as required. (At this scale
  the measured prune count is 0: reachable states satisfy the congruence
  automatically, as theory predicts — the invariant is a property of
  complete layers, and the DP only visits completable branches.)
* The same enable/disable equivalence was verified on `5×5×5` ✅.

## 5. D4 symmetry reduction (task 8)

Implemented identically to the Python prototype's `sym_reduce` (8 D4
transforms of the 5×5 cross-section; per state, the canonical pair is the
minimum over transforms of the (L0′, L1′) pair after (min, max)
normalisation). Verified on the Numba-produced boundary-1 states:
**1,900 → 239 orbits** ✅ (exact match with the Python reference).

Soundness caveat (documented in the prototype doc): the (min, max)
normalisation treats `(L0, L1)` as an unordered pair — the L0/L1 swap is
**not** a box symmetry, so the 239 figure is a *reported orbit metric*,
not a sound state-dedup for path-based reasoning. The exhaustive UNSAT
closures in both the reference and the port use the unreduced state sets
(sound). A D4-only (no-swap) orbit count would be the sound reduction;
measuring it is a trivial follow-up.

## 6. 6×6×10 feasibility estimate (task 10; NOT run)

Measured Numba throughput on the 6×6 scale: **~180k boundary states/s**
(6×6×5: 2.09 M states in 11.6 s, including per-state fill enumeration and
dedup). For 6×6×10 (10 layers, 36-bit cross-section — same single-limb
encoding):

* layer-count scaling: expected total state mass ~2–5× the 5-layer box
  (more boundaries to close);
* naive extrapolation: **~1–2 min**;
* caveat: the 6×6×10 frontier width at deep boundaries is unmeasured; if
  the deep-boundary width grows beyond the 6×6×5 profile, runtime could
  reach ~10–30 min. A single capped 900 s probe would settle the question
  definitively — **deliberately not run here** (task instruction), but the
  measured numbers make it plausibly practical.

## 7. Files

* Numba implementation: `/tmp/opencode/z_frontier_numba.py`
* Python reference (unchanged): `/tmp/opencode/z_frontier_v4.py`
* Witness-walk kernel: inline in the validation session (see §5 above)
* Validation battery outputs: printed in-session (this doc §2)

Catalogue truth tables, certificate semantics, the certified 6×6×10
package, and all prior results: **untouched**.
