# CK6 V45 Sharding Pipeline — Repair and Validation

Status: **REPAIRED AND VALIDATED** (small-volume reference validation,
placement hardening, George-target smoke test).  The full V45 re-run is
**not** started.  All historical V45 artefacts are untouched.

Date: 2026-09-10
Companion documents:
- `docs/frontier/ck6_sharding_bug.md` (audit: root cause, counterexample,
  completeness proofs)
- `data/ck6_reuse/ck6_sharding_bug_regression.json` (audit record)
- `data/ck6_reuse/ck6_v45_sharding_repair.json` (this repair's record)

---

## 1. What was repaired

### 1.1 Corrected candidate-min-id domain and shard planner

New module: **`solvers/ck6_sharding_corrected.py`** (the historical
`solvers/t_ck6_oddity_v35_search.py` is left byte-identical; the
defective prefilter remains there, unused by the corrected path).

`corrected_candidate_min_ids(un)` implements the sound necessary
condition:

> a min-id `s` is admissible iff `s` can **reach** a start-front
> (centre-adjacent) orbit through adjacent orbits with ids `>= s`.

*Necessity proof.*  A target with minimum orbit id `s` is connected,
contains the inversion-centre cell (odd volume), and all its orbits
have ids `>= s`; connectivity therefore supplies a path from `s` to a
centre-adjacent orbit using only ids `>= s`.  ∎

The filter may over-approximate (an admitted `s` may yield an empty
shard — harmless); it never drops a realizable min-id.  The simplest
fully-correct alternative — all orbit ids as the shard domain — is also
acceptable; the filter merely avoids provably-empty shards.

`build_corrected_plan(volume, n_shards)` builds a complete, disjoint
plan with hard assertions:

- every candidate min-id appears in **exactly one** shard
  (sorted concatenation == sorted domain, and no duplicates);
- for V45: domain size == **3,696** and min-id **3590 present**;
- shards are contiguous ranges over the sorted candidate domain
  (load balancing by true per-min-id target counts should replace this
  after the corrected count pass; correctness does not depend on
  balance).

### 1.2 Placement-domain hardening (separate latent defect)

`common/oddity.py::placements_in_region` was hardened.  Orientations
are normalized to per-axis minimum (0,0,0) but need not *contain*
(0,0,0) as a cell — true for **18/24 orientations of repo-M** and
**6/24 of repo-P**.  For such an orientation the placement's anchor
(component-wise minimum corner) is not a placement cell and can lie
outside a non-box region that fully contains the placement; the old
anchor-in-region loop then missed the placement.  The hardened version
computes the exact anchor set

    {a : a + o ⊆ region} = ⋂_{c∈o} (region − c),

which is a strict superset of the old enumeration (identical for
orientations containing (0,0,0); box regions gain only the previously
missed boundary placements).  `PlacementIndex`/`FastFunnel` inherit the
fix (they wrap `placements_in_region`).

## 2. Validation performed

### 2.1 Reference validation (exact set equality, not just counts)

`solvers/ck6_sharding_corrected.py validate` — corrected sharding
(sound filter + per-min-id seeded DFS) vs the single-process reference
enumerator `enumerate_connected_ck6_targets`:

| volume | corrected total | reference total | set equality |
|--------|-----------------|-----------------|--------------|
| V5     | 2               | 2               | YES          |
| V15    | 368             | 368             | YES          |
| V25    | 71,539          | 71,539          | YES          |

### 2.2 Permanent regression tests (all PASS)

- `tools/frontier/test_ck6_sharding_bug.py` — George B-9 counterexample
  (min-id 3590; old prefilter rejects / corrected accepts; seeded-DFS
  reachability; repo-M covers == 12; V5/V15/V25 set equality).
- **`tools/frontier/test_placement_domain_completeness.py`** (new) —
  for repo-M (18/24 min-corner-less orientations) and repo-P (6/24):
  - region = a single placement whose orientation lacks (0,0,0): the
    placement itself is reported (the old code missed it — this is the
    minimal demonstration of the latent defect);
  - regions = L1 balls R=2, R=3: `placements_in_region` == brute-force
    extended-box enumeration (72 and 384 placements respectively);
  - mixed region: hardened == brute force.
- Box-domain compatibility: `S5P.all_tilings` (which uses the hardened
  `placements_in_region`) still returns 2 covers for the B-V15 target
  (repo-B) and 12 covers for George's B-9 target (repo-M) — unchanged
  from the pre-hardening forensic results.

### 2.3 George-target smoke test (V45)

Corrected plan: `data/ck6_reuse/ck6_v45_shards_corrected.json`
(3,696 candidate min-ids, 8 shards; shard 7 = ids [3234..3937] holds
3590).  The smoke test runs the corpus enumeration for **min-id 3590**
(the decisive element of George's shard) for repo-M through the
driver's own `funnel_and_cover` path, stopping at George's target.
Result: **CONFIRMED.** The real seeded DFS over min-id 3590's full
subtree (3,430,348 CK6 targets) yielded George's target (leaf #3,430,348)
and the driver's own `funnel_and_cover` returned **SAT with 12 covers** —
matching the forensic prediction exactly
(see `data/ck6_reuse/ck6_v45_sharding_repair.json`, field `smoke_test`).
(The remaining 461 min-ids of shard 7 are bulk work deliberately not
run; min-id 3590's own subtree contained no other repo-M-tileable
target before George's leaf.)

## 3. Old vs corrected V45 shard plan

| | old (historical) | corrected |
|---|---|---|
| candidate min-ids | 86 | **3,696** |
| domain range | [3652..3937] | [0..3937] |
| omitted range | — | **[0..3651] was omitted** (3,652 ids) |
| shards | 4 | 8 (corrected plan; count is a free parameter) |
| George min-id 3590 | absent | shard 7 |

Work estimate: the 86 historical min-ids keep their historical work;
the corrected plan adds 3,610 new min-id DFS passes, most of which are
expected to be cheap (empty or small shards — the corrected filter
over-approximates).  True load balancing requires the corrected count
pass first; the shipped plan balances by candidate count only.

## 4. Files

- `solvers/ck6_sharding_corrected.py` — corrected logic + plan + smoke
  (new; historical solver untouched).
- `common/oddity.py` — `placements_in_region` hardened (the only
  modification to existing code; strictly additive placements, see
  §1.2).
- `tools/frontier/test_placement_domain_completeness.py` — new
  regression test (ALL PASS).
- `tools/frontier/test_ck6_sharding_bug.py` — permanent counterexample
  regression (ALL PASS, re-run after hardening).
- `data/ck6_reuse/ck6_v45_shards_corrected.json` — corrected V45 plan
  (distinct name; historical `data/ck6_v45/shards.json` untouched).
- `data/ck6_reuse/ck6_v45_sharding_repair.json` — machine-readable
  repair record.

## 5. Not done (per instructions)

- The full V45 matrix re-run (and the full 462-min-id shard 7 walk)
  was **not** started.
- Historical `data/ck6_v45/shards.json`, `minid_counts.json`, and all
  Stage 5L reports remain byte-identical.
- The V45 piece results remain annotated as non-exhaustive until the
  corrected corpus re-run is performed.

## 6. Recommended next steps

1. Re-count V45 over the corrected domain (incremental, resumable) →
   `data/ck6_v45/minid_counts_corrected.json`; rebuild
   `shards_corrected.json` balanced by true counts.
2. Re-run the V45 piece matrix (M and B first) on the corrected corpus.
3. Swap `t_ck6_oddity_v35_search.cmd_count`'s sharded branch to the
   corrected filter (or adopt `ck6_sharding_corrected` wholesale) so
   future volumes (V55+) cannot regress; keep the old path behind a
   flag for A/B comparison.
4. Keep both regression tests as CI gates.
