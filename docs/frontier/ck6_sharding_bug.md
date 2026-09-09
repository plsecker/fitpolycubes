# CK6 Sharded Target Enumeration — Sharding/Count Prefilter Bug

Status: **CONFIRMED BUG, repair designed, regression test green.**
Date: 2026-09-09
Trigger: forensic reconstruction of George Sicherman's current "B 9"
pentacube oddity (see `data/ck6_reuse/george_b9_geometry_reconciliation.{json,txt}`).

No historical artefact was modified. No new large V35/V45 search was
launched. The repair itself (code change + V45 re-count) is designed
here but **not applied**.

---

## 1. Root cause — exact location

File: `solvers/t_ck6_oddity_v35_search.py`, `cmd_count`, **sharded
branch (volume > 35)** — the block commented
`# candidate min-ids: every orbit id that can be a minimum ... cheap
validity prefilter: seeded reachability`:

```python
start_front = sorted(un["start_front"])
cands = set(start_front)
for s0 in start_front:
    stack = [s0]; seen = {s0}
    while stack:
        v = stack.pop()
        for w in un["adj"][v]:
            if w >= s0 and w not in seen:   # <-- the unsound constraint
                seen.add(w); cands.add(w); stack.append(w)
cands = sorted(cands)
```

Downstream chain of the defect:

1. `cands` (candidate minimum-orbit ids) is used as the shard domain:
   `iter_targets_seeded(un, s, budget)` is run only for `s in cands`.
2. Per-min-id counts are written to `data/ck6_v45/minid_counts.json`
   (`hist`), whose keys become the *only* min-ids in
   `data/ck6_v45/shards.json` (`cmd_plan`).
3. The Stage 5L reuse driver (`t_ck6_reuse_multipiece.py`,
   `run_shard_piece`) streams targets from exactly those shards.

### The false mathematical assumption

The prefilter admits min-id `s` only if `s` is reachable from some
**start-front** orbit `s0` (centre-adjacent) through a chain of
adjacent orbits with **monotonically non-decreasing ids bounded below
by the chain root `s0`** (`w >= s0`).  Implicitly it assumes:

> *For every connected CK6-closed target, its minimum orbit id can be
> reached from the centre outward through orbits whose ids never dip
> below the starting start-front orbit's id* — i.e. that orbit ids
> (which follow the `l1_ball` enumeration order, x-major from −R) are
> compatible with centre-outward connectivity growth.

This is **false**. Orbit ids encode ball-iteration order, which has no
topological relationship to target connectivity. A target may contain
a "far" orbit (low id) whose only connections to the centre run
through "near" orbits (high ids). Such a target is perfectly reachable
by the seeded DFS itself (which *starts* at `s` and only requires
`ids >= s` thereafter), but the prefilter never lets shard `s` exist.

### Soundness of the rest of the pipeline (verified, not assumed)

* `iter_targets_seeded` is complete per min-id: for any target `T` with
  minimum orbit id `s`, its orbit graph is connected (cell
  connectivity implies orbit adjacency connectivity), all its orbit
  ids are `>= s`, so its orbits can be grown from `{centre, s}` through
  the frontier rule; the accumulated frontier is a function of the mask
  (`start_front ∪ adj[s] ∪ ⋃ adj[mask]`), so the `visited` mask-dedup
  is sound; leaf cost is exactly `(V−1)/2` for every `V`-cell CK6-closed
  target (centre cell free; 4-orbits cost 2, 2-orbits cost 1).
* `count_minids` (the **monolithic** count used for `volume <= 35`)
  grows from the centre with **no id constraint** and is complete; it
  is empirically validated at V25 (71,539 == reference enumerator).
* The funnel/placement stage is complete:
  `unique_orientations` normalizes each orientation to per-axis minimum
  (0,0,0), so every placement's anchor is one of its own cells; anchors
  are enumerated over the whole region; `PlacementIndex.contained`
  filters to true containment.  (See §7 for a residual edge case.)

## 2. Minimal counterexample — George's "B 9" target

Reconstructed from the live page (rev 2026-09-08), corpus frame
(rotation `diag(1,−1,0,−1)`, inversion centre at origin):

* 45 cells, face-connected, exact CK6 (order 4:
  identity / inversion / c2_diag / mirror_diag);
* `O_h` canonical id **`oh-109166b4c83a`** (proper id identical);
* **minimum orbit id 3590** (16 distinct orbits, ids 3590..3937);
* contains both start-front orbits: **3652** (±x/±y centre-neighbours)
  and **3937** (±z centre-neighbours);
* reachable by `iter_targets_seeded(un, 3590, 22)` mechanics — proven
  by an exact bounded BFS replay (6,976 states, mask reached);
* **repo-M tiles it in 12 ways** (independent full-domain enumeration;
  the driver's own `funnel_and_cover` path also returns SAT=12);
  repo-B covers it 0 times.

Old prefilter: `cands = [3652..3937]` (86 ids) — **3590 excluded**.
Consequence: no shard 3590 → target never enumerated → absent from the
V45 corpus → the recorded `repo-M V45 = SAT 0` is not exhaustive.

Permanent regression test:
`tools/frontier/test_ck6_sharding_bug.py` (all checks PASS; see
`data/ck6_reuse/ck6_sharding_bug_regression.json`).  It asserts:
validity + canonical id; min-id == 3590; old prefilter rejects 3590
(bug reproduced); corrected filter accepts 3590; seeded-DFS
reachability (bounded exact replay); repo-M covers == 12; and corrected
sharding reproduces the reference corpora V5 = 2, V15 = 368,
V25 = 71,539 with **set equality** (no duplicates, no omissions).

## 3. Old vs corrected candidate-min-id logic

**Old (unsound):** `s` admitted iff reachable *from* a start-front
orbit `s0` via ids `>= s0`.
Fails when the target's start-front orbits have *higher* ids than its
minimum — exactly George's target (3590 < 3652).

**Corrected (sound necessary condition):** `s` admitted iff `s` can
**reach** a start-front orbit through adjacent orbits with `ids >= s`.
Necessity proof: a target with min-id `s` is connected, contains the
centre, and all its orbits have ids `>= s`; hence within the target
there is a path from `s` to a centre-adjacent orbit using only ids
`>= s`.  The filter may over-approximate (harmless: empty shards yield
0 targets).  For V45 it yields **3,696 candidate min-ids (0..3937)** vs
the old 86.

**Simplest fully-correct alternative:** use **all** orbit ids
`0..N−1` as the shard domain; impossible min-ids yield empty shards.
Correctness is trivial; cost is one seeded DFS per impossible id.

### Completeness/disjointness proof (corrected partition)

* *Disjoint:* a target's minimum orbit id is intrinsic; shard `s`
  enumerates exactly `{T : minid(T) = s}` (seed `s` forced, ids `< s`
  forbidden).  Distinct `s` ⇒ disjoint target sets.
* *Complete:* every connected CK6-closed odd-volume target contains its
  inversion centre cell (odd volume ⇒ a fixed cell) and has orbit cost
  exactly `(V−1)/2`; by connectivity its orbits admit a growth order
  from `{centre, s}` through the frontier rule with ids `>= s`; the
  frontier is mask-determined so dedup never removes reachability;
  hence `iter_targets_seeded(un, s, (V−1)//2)` yields it.
* The corrected candidate filter keeps every `s` satisfying the
  necessary condition of the completeness proof, so no target's shard
  is dropped.

## 4. V35 impact assessment — **NOT affected** (checked, not extrapolated)

* `cmd_count` uses the **monolithic** `count_minids` for
  `volume <= 35`; the prefilter code path is only for `volume > 35`.
  `data/ck6_v35/minid_counts.json` (total 15,289,669, elapsed 85.9 s)
  is a monolithic count.
* The monolithic DFS is complete (no id constraint; validated at V25
  against the reference enumerator), so the V35 hist
  (489 min-ids, [558..1857]) is the true min-id distribution and
  `data/ck6_v35/shards.json` covers exactly those min-ids.
* Therefore the V35 corpus and partition are complete, and the
  **completed Stage 5L V35 piece results remain valid as exhaustive
  searches** (v35_A: SAT 0; v35_B: SAT 544 / 1,652 solutions;
  v35_E: SAT 0).
* Process check: **no CK6 search process is currently running**
  (`ps` — only system processes).  The "running V35 search" premise is
  stale: the Stage 5L V35 matrix completed only pieces A/B/E; the run was
  **interrupted during V35 F** (2/8 shards complete, 2 partial checkpoints,
  no `final.json` — see `data/ck6_reuse/run/v35_F/` and
  `data/ck6_reuse/run_v45_v35.log`) and pieces G–Z never started.  Nothing
  needs to be stopped.  The remaining 20 V35 piece combos can safely run on
  the existing V35 corpus/plan.
* The V55 production plan (`data/ck6_v55/shard_plan.json`) shards **all
  7,139 orbit ids (0..7138), no gaps** — a complete partition that does
  not use the prefilter; also not affected.  (Its `status.txt` claims
  "running" but no process exists — stale status.)

## 5. V45 impact assessment — **AFFECTED**

* Old candidate domain: 86 min-ids [3652..3937].
* Corrected candidate domain: **3,696 min-ids [0..3937]**.
* **Omitted candidate min-ids below the plan minimum: 3,652** (all of
  0..3651), including 3590 (George's target).
* Revised V45 target count: **unknown without running the missing
  shards** (forbidden here); bounded below by
  1,469,999 + (targets of the omitted min-ids, ≥ 1 — George's B-9
  target, oh-109166b4c83a).
* Consequently **all 23 recorded V45 piece results are not exhaustive negatives**
  (21 pieces recorded sat_count = 0; **I recorded 215 SAT / 215 solutions and
  R recorded 4 SAT / 8 solutions** — all within the buggy 86-min-id domain)
  and must be annotated as such; any "piece P has no V45 CK6 oddity" claim
  derived from them is unsupported.

## 6. Historical evidence preservation

Untouched: `data/ck6_v45/shards.json`, `data/ck6_v45/minid_counts.json`,
`data/ck6_v35/*`, all `data/ck6_reuse/run/**/final.json`,
`piece_volume_results.jsonl`.  Corrected artefacts should be written
under distinct names, e.g. `data/ck6_v45/minid_counts_corrected.json`
and `data/ck6_v45/shards_corrected.json`.

## 7. Secondary observation (latent, no counterexample found)

`placements_in_region` is complete because anchors are enumerated over
the whole region and every orientation contains its per-axis minimum
corner... **except** that a normalized orientation need not *contain*
(0,0,0) as a cell (true for M and P).  Then a placement's anchor (its
component-wise min corner) is not a placement cell and can lie outside
a ball-shaped region while all placement cells are inside.  For
George's V45 target this did not occur (ball index rows 140 == complete
box-domain count), but for boundary-hugging targets and min-corner-less
pieces the ball-domain funnel index could drop placements.  Cheap
hardening: build the funnel index over a containing **box** of the
universe ball, or extend the anchor range by the piece span.  No
impact on the sharding bug above.

## 8. Recommended next steps

1. **Repair** `cmd_count`'s sharded branch: replace the prefilter with
   `corrected_prefilter_candidates` (or all orbit ids).  Keep the old
   code path behind a flag for A/B comparison if desired.
2. **Re-count V45** for the 3,652 omitted min-ids (incremental, shard
   at a time; resumable) → `minid_counts_corrected.json`; rebuild
   `shards_corrected.json`; verify old ∪ new partition disjointness
   (old min-ids are a subset of the corrected domain, so only the new
   shards need running).
3. **Re-run the V45 piece matrix** (or at least M and B) on the
   corrected corpus; expect George's B-9 target to surface as repo-M
   SAT with 12 covers (oh-109166b4c83a).
4. **Annotate** Stage 5L V45 results as non-exhaustive (append-only
   notes; do not rewrite history).
5. **V35**: no corpus repair needed; optionally finish the remaining 20
   piece combos on the existing complete V35 corpus.
6. Keep `tools/frontier/test_ck6_sharding_bug.py` as a permanent
   regression gate (fast mode ≈ 15 s; full mode ≈ 3.5 min with V25).
7. Optional hardening: box-domain funnel index (§7).
