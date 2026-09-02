# Centre-Pair Symmetry Breaking for Even-Dimension Boxes

**Date**: 2026-09-02
**Scope**: `solvers/solver.cpp` only (plus this report). No catalogue or
theorem/rule documents touched. Connectivity pruning untouched (known net
loss, out of scope). Flags-off search behaviour unchanged — verified
node-for-node.

> **Provenance note (2026-09-03, repo audit).** This report describes the
> **centre-pair extension** added on top of the already-present phase-2
> solver and sound symmetry. What was **already present** in the working
> tree before this experiment: the phase-2 piece CLI / `max_nodes` /
> `--connectivity` / `--dump` infrastructure, and the sound symmetry
> scheme (centre anchor for all-odd boxes, corner/G₀ for even-dim boxes).
> What this experiment **added**: the centre-pair anchor for boxes with
> exactly one even dimension (|S| = 2), the S-tuple canonicalisation, the
> static allowed-set deactivation, and the runtime joint check.
> The working tree also contains **parallel colour/region-pruning research
> code** (`--region-prune=colour-global|colour|propagate`,
> `--research-deadends`) from a separate session; it is flag-gated OFF by
> default, was not part of this experiment, and does not affect the
> flags-off or `--symmetry` results reported here. See
> `docs/frontier/cpp_solver_repo_checkpoint.md` for the full provenance.

> **POST-CHECKPOINT CORRECTION (2026-09-03).** The original centre-pair
> implementation had a **remaining unsound generic single-row canonical
> filter**. This section documents the bug, how it was found, the evidence,
> the exact fix, and which previously reported numbers must be revalidated.
> The historical results in §3–§5 are **not** rewritten; they describe the
> pre-fix behaviour and are flagged below where they are affected.

## 0. Post-checkpoint correction: unsound generic single-row filter

**Date**: 2026-09-03 (after checkpoint `ebd28c4`)

### 0.1 The bug

The centre-pair scheme as originally implemented (and committed at
`ebd28c4`) was **not fully sound**. After the centre-pair block computed the
tuple-canonical static filter and the static over-approximation, control
**fell through** to the generic single-row canonical filter ("Canonical
restriction on placements covering the anchor cell"). That generic filter
canonicalises each placement covering `anchor_cell` (= `cell_neg`) against
`g_sym.maps` — the **full** preservation-checked group (the `else` branch
that restricts to the fixing subgroup `g0` is not taken in `pair_mode`).

The generic filter is **unsound** for the centre-pair scheme: group elements
may **swap the two anchor cells** (`cell_neg` ↔ `cell_pos`). For a placement
`r` covering `cell_neg`, its orbit-minimum image (over the full group) can
cover `cell_pos` instead. The generic filter compares `sigs[r]` (the
placement's own signature) against the orbit-minimum `best`; if the
orbit-minimum image covers `cell_pos`, then `best` is a *different*
placement's signature, so `sigs[r] != best` and the filter deletes `r` —
even though `r` is part of a canonical tuple. This destroys whole solution
orbits.

### 0.2 How the bug was found

The bug was discovered by testing the centre-pair scheme on a **chiral H
5×5×6** box, where the symmetry group genuinely swaps the two anchor cells.
The old code lost a measurable fraction of solution orbits (see §0.3).

### 0.3 H 5×5×6 orbit-loss evidence

Ground truth (raw, flags-off, exhaustive): **205,668 solutions**, **25,902
solution orbits** under the chiral-safe group (|G| = 16).

| code | solutions | orbits represented | orbits lost |
|---|---|---|---|
| old (checkpoint `ebd28c4`) | 21,315 | 20,248 / 25,902 | **5,654 (21.8 %)** |
| fixed (current) | 27,459 | 25,902 / 25,902 | **0 (0 %)** |

The old code lost **21.8 % of solution orbits**; the fixed code loses
**0**. Validation via `validate_sym.py` (orbit-recovery over all group
images): old = **INCOMPLETE**, fixed = **PASS (valid + complete over
orbits)**.

### 0.4 The exact fix

In `setup_symmetry()`, immediately after the centre-pair block sets
`g_sym.maps`, `g_sym.active`, and `g_sym.anchor_cell`, an early return is
added:

```cpp
if (g_sym.pair_mode) {
    return static_cast<int>(g_sym.pair_pruned_rows);
}
```

This returns from `setup_symmetry` **before** the generic single-row
canonical filter runs, so the generic filter is no longer applied in
`pair_mode`. The tuple-canonical static filter plus the runtime joint check
(unchanged) are the complete, sound restriction. The fix is **23 insertions,
0 deletions** versus `ebd28c4`, confined to `setup_symmetry`. `SYM_DEBUG`
diagnostic output was also added (env-gated, inert by default).

### 0.5 Validation of the fix (2026-09-03)

| test | old (checkpoint) | fixed (current) | verdict |
|---|---|---|---|
| H 5×5×6 orbit-loss | 21,315 sols, 20,248/25,902 orbits (21.8 % lost) | 27,459 sols, 25,902/25,902 orbits (0 lost) | **fix validated** |
| P 1×4×5 pair | 19 nodes / 3 sols | 19 nodes / 3 sols | identical |
| V 5×5×6 pair | 77,287 nodes / 18 sols (9/9 orbits) | 93,440 nodes / 18 sols (9/9 orbits) | both sound |
| flags-off V 5×5×9 (1M cap) | 1,000,031 nodes / 0 sols | 1,000,031 nodes / 0 sols | identical |
| flags-off V 5×5×6 | 366,907 nodes / 144 sols | 366,907 nodes / 144 sols | identical |
| non-pair sym V 5×5×9 | 7,816,207 nodes / 140 sols | 7,816,207 nodes / 140 sols | identical |
| corner-anchor Z 6×6×10 | 100,045 nodes / 0 sols | 100,045 nodes / 0 sols | identical |
| colour/region V 5×5×9 | 100,030 nodes / 0 sols | 100,030 nodes / 0 sols | identical |
| CLI | identical | identical | identical |

The fix does **not** alter the colour/region-pruning code, the CLI, the
non-pair symmetry paths (centre anchor for all-odd, corner/G₀ for even-dim),
or the runtime pair joint-check logic. Flags-off behaviour is unchanged
node-for-node.

### 0.6 Which previously reported numbers must be revalidated

The fix changes the `--symmetry` path for **centre-pair cases** (exactly one
even dimension). The following historical numbers were produced with the
pre-fix code and **must be revalidated** against the fixed code:

* **Z 4×11×15 `--symmetry` centre-pair (200M cap)** — §4: 200,000,064 nodes
  / 0 sols / depth 107/132 / 556 s. The generic filter may have been
  removing placements for this case; the fixed code may change the node
  count and depth. **Re-run required.**
* **P 1×4×5 `--symmetry` centre-pair** — §3: 19 nodes / 3 sols. Re-verified
  here: **unchanged** (19 / 3) — the flat achiral P's full group fixes
  `cell_neg`, so the generic filter was sound for this case. **No re-run
  needed.**
* **V 5×5×6 `--symmetry` centre-pair** — not in the original report, but
  re-verified here: both old and new give 18 sols / 9 orbits (sound), though
  node counts differ (77,287 vs 93,440). **No orbit loss either way.**

The **flags-off** results (§3) and the **all-odd** V 5×5×9 `--symmetry`
result (§3) are **unaffected** (re-verified identical here).

## 1. Design

Let `S` be the **centre anchor set**: the product over axes of
`{mid}` for an odd dimension `d = 2m+1` and `{k−1, k}` for an even
dimension `d = 2k`.

* Every box symmetry maps `S` **setwise** onto itself: a sign flip
  `x → d−1−x` fixes `mid` and exchanges `{k−1, k}`; an axis permutation
  maps even axes to even axes (it must preserve the dimension multiset
  anyway to map the box onto itself).
* For Z 4×11×15: `S = {(1,5,7), (2,5,7)}` (cell ids 329, 330), |S| = 2.

Every tiling covers all |S| cells of `S` with exactly one placement each.
Write `t(T)` for the |S|-tuple of covering placements, ordered by the fixed
cell order on `S`, and `Σ(t)` for the sequence of placement signatures
(sorted 5-cell keys; signatures are unique per placement). A tiling `T` is
**canonical** iff `Σ(t(T))` is the lex-minimum of `{ Σ(t(u(T))) : u ∈ G }`,
where `G` is the full preservation-checked symmetry group (box symmetries
that map the piece's placement set onto itself).

Implementation (gated behind the existing `--symmetry` toggle):

* |S| = 1 (all dims odd): the previous static centre-cell filter,
  **unchanged**.
* |S| = 2 (exactly one even dim — the Z case): two mechanisms.
  - *Static*: at setup, enumerate all realisable S-tuples (pairs of
    disjoint placements covering the two cells, plus the degenerate
    one-placement-covers-both tuple), keep the tuple-canonical ones, and
    pre-deactivate any placement that participates in **no** canonical
    tuple.
  - *Runtime*: when the second anchor cell becomes covered (the first
    coverage is permanent — exact cover), the S-tuple is complete and is
    checked against the precomputed canonical-partner sets of the
    first-committed placement; non-canonical branches are cut there.
* |S| ≥ 4 (two or three even dims): falls back to the previous
  corner/fixing-subgroup scheme (no benchmark case needs it).

## 2. Soundness proof

**(a) Setwise invariance.** Verified at setup with a hard check: every
`u ∈ G` satisfies `u(S) = S`. Consequently the action of `G` on
S-indexed tuples is well defined after the slot re-ordering
(`u` may permute the slots; the comparison re-orders images into the
fixed S order).

**(b) Every orbit retains a representative.** For any tiling `T`, choose
`u*` attaining the lex-minimum of `Σ(t(u(T)))` over `u ∈ G`. The orbit of
`u*(T)` equals the orbit of `T`, so `Σ(t(u*(T)))` is still the minimum and
`u*(T)` is canonical. Note `u*` need not fix any cell of `S`: the
canonicalisation object is the **tuple**, not a placement at a fixed cell
— this is precisely what makes the full group usable.

**(c) Pruning never loses a canonical tiling.** The S-cells of a partial
state, once covered, are covered by the same placements in every
completion. If the partial tuple `t` is not tuple-canonical, some `u` has
`Σ(u·t) <lex Σ(t)`; then for every completion `T`,
`Σ(t(u(T))) = Σ(u·t) < Σ(t) = Σ(t(T))`, so `T` was not canonical either.
Hence cutting non-canonical states at the second commitment point (and the
static removal of placements that appear in no canonical tuple) removes
only non-canonical tilings. With (b), at least one tiling per solution
orbit survives.

**(d) Full group vs subgroup — why this differs from the old unsound
rule.** The previous unsound rule canonicalised corner placements against
the full group: the corner *cell* moves under sign-flip elements, the
orbit minimum can be a non-corner image, and there is no set structure to
re-order into — whole solution orbits could be lost. The centre-pair rule
is sound with the full group **because** the anchor set is only setwise
fixed and the tuple re-ordering makes the action well defined. For a
single-cell anchor the sound group remains the cell's fixing subgroup
(the corner scheme keeps `G₀`).

## 3. Validation

> **Note (2026-09-03).** The centre-pair results in this section were
> produced with the **pre-fix** code (which still applied the unsound
> generic single-row filter). See §0 for the post-checkpoint correction and
> which numbers must be revalidated. The flags-off and all-odd results below
> are unaffected.

**Flags-off equivalence** (current binary vs the pre-change phase2
binary, identical placement files):

| case | result |
|---|---|
| V 5×5×9, full | 43,621,737 nodes / 1,120 solutions — exact match |
| W 5×5×17, 50M cap | 50,000,052 nodes — exact match |
| Z 4×11×15, 20M cap | 20,000,063 nodes — exact match |
| V 1×4×5, W 1×3×10 | exact match |

**All-odd regression** (V 5×5×9 `--symmetry`): 7,816,207 nodes / 140
solutions, setup line identical, solution dump **byte-identical** to the
previously orbit-verified run (0/1,120 solution orbits lost — that
verification carries over).

**Pair-path mechanical validation** (P 1×4×5, SAT, small enough for
exhaustive ground truth): |G| = 8 (all 8 reflections preserve the flat
achiral P); brute force gives **6 raw tilings**; the pair scheme returns
**3** solutions; mechanical orbit-recovery check over all group images:
**0/6 orbits lost** — sound. Setup stats: 34 anchor placements, 24
pre-deactivated, 160 S-tuple candidates → 46 canonical.

## 4. Z 4×11×15 results (200M-node cap each)

| config | nodes | sols | max depth | wall |
|---|---|---|---|---|
| symmetry off (baseline) | 200,000,073 | 0 | 106/132 | 581 s |
| existing corner symmetry | 20,000,063 @ 20M cap = baseline prefix — **no-op by measurement** (\|H\| = 1, 0 rows removed) | 0 | 106/132 @200M (prior session) | — |
| **new centre-pair** | 200,000,064 | 0 | **107**/132 | 556 s |

Centre-pair setup on Z: |G| = 8 (all reflections preserve the flat
achiral Z); anchor cells (329, 330); 48 placements cover the anchor cells,
**34 pre-deactivated** (14 survive); 848 S-tuple candidates → 125
canonical. Runtime: **52,413 joint checks, 30,867 prunes** in 200M nodes.

## 5. Verdict — why the scheme does not materially help this case

The reduction mechanisms work exactly as proven (34/48 anchor placements
eliminated statically; 59 % of the joint checks that fired cut their
branch; depth 106 → 107 at equal node budget), but the effect is
**immaterial at the 200M-node scale**: the cap is still hit, and the wall
time is unchanged (556 s vs 581 s, within noise).

The reason is structural: the search branches on the minimum-degree
column, so corner and edge cells are committed first, and the interior
centre pair is only covered **~52 thousand times in 200 million nodes**.
The prunable subtree mass sits below a commitment point that the tree
barely reaches; the tree's mass lies overwhelmingly *above* it
(breadth-dominated frontier, not deep dead-ends). No anchor-set scheme —
pair or otherwise — can prune nodes that occur before the anchor set is
committed. Making the case tractable would require committing the anchor
early (e.g. a fixed-cell branching order or a lex-lead/orderly-generation
canonical test), which changes the search order and is a different
project.

Per the task constraints: stopped here. No unlimited run was launched
(the 200M-cap run completed in ~9 min and is the whole evidence base);
no connectivity, heuristic, or other work was touched.

## 6. Deliverables and build

* `solvers/solver.cpp`: centre-pair scheme (setup enumeration, static
  allowed-set deactivation, runtime joint check with counters), block
  comment with the proof, unchanged flags-off path.
* Build on this machine: `python-zig build-exe solvers/solver.cpp -O
  ReleaseFast -lc -lc++` (no g++ present).
* Validation scripts were session-local (`/tmp/opencode`); the
  orbit-recovery method is documented in
  `docs/frontier/solver_benchmark_connectivity_symmetry.md`.

> **Binary provenance (2026-09-03, repo audit).** The centre-pair results
> in §3–§4 were produced by `/tmp/opencode/solver_v3` (built 2026-09-02
> 22:49 from the working-tree `solvers/solver.cpp` of that session, which
> already contained the parallel colour code). The all-odd V regression
> (§3) was also re-verified with the current working-tree build
> (`solver_audit`, 2026-09-03) and is byte-identical. The "existing corner
> symmetry" no-op row in §4 was produced by the earlier
> `/tmp/opencode/solver_v2` (corner/G₀ scheme); the current working tree
> routes one-even-dim boxes to the centre-pair path automatically, so that
> row is not reproducible from the current source without the v2 binary.
