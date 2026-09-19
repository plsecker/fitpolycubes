# V45 Enumeration Validation — Corrected Architecture

**Date:** 2026-09-19
**Scope:** independent validation of the corrected CK6 V45 enumeration
architecture, with the connectivity-pruned engine
(`iter_targets_seeded_connected`) as the production V45 engine candidate.

## 1. The two enumerators

| | Original seeded DFS | Connectivity-pruned engine |
|---|---|---|
| Function | `iter_targets_seeded` | `iter_targets_seeded_connected` |
| Growth rule | any frontier orbit (ids ≥ s) | only orbits face-adjacent to the **centre's connected component** |
| Zero-leaf buckets | 60–160 s each (disconnected product space) | **0.0 s** (root reachability prune) |
| Leaf connectivity check | `is_face_connected` BFS on the cell set | exact `bridged` flag (no BFS) |
| V35 corrected-domain estimate | ~44–47 h | **~2–2.5 h** |

Both enumerate exactly the connected CK6-closed targets whose minimum orbit
id is s (the shard partition of the corrected architecture).  The pruned
engine is a strict subset of the original's state space with a completeness
proof (below); it yields the identical target set.

## 2. Completeness proof of the connectivity prune

**Setup.**  A target T is a connected CK6-closed cell set of odd volume V,
containing the centre cell; its orbit set O(T) has minimum id s.  The orbit
graph of T (orbits as nodes, edge when any two cells are face-adjacent) is
connected: a cell path between any two cells maps to an orbit walk.

**Spanning-tree order.**  Root a spanning tree ST of T's orbit graph at the
centre.  Order the orbits of T: **s first**, then all others by
non-decreasing ST depth.  Claim: every orbit v ≠ s added in this order is
adjacent to the centre's connected component at add time.

*Proof.*  v's ST parent p has depth(v) − 1 < depth(v), so p is added before
v.  By induction, all orbits of depth < depth(v) are in the centre component
(depth-1 orbits are centre-adjacent; each deeper orbit is adjacent to its
parent, which is in the centre component).  p is adjacent to v, so v is
centre-component-adjacent.  The seed s is added first and may be
disconnected; it joins the centre component when its parent (depth d_s) is
added, and s's ST children (depth d_s + 1) are then added through
s-adjacency.  ∎

The DFS expands **every** centre-component-adjacent orbit at every state, so
the spanning-tree order is one of the explored orders and O(T) is reached.
Soundness: every yielded set is orbit-closed, has min-id s (all orbits ≥ s,
s present), has exactly V cells (rem = 0 ⇒ cost = budget ⇒ 1 + 2·budget
cells), and is connected (leaf check below).

## 3. Root reachability prunes (provably empty buckets)

Two necessary conditions, computed once per universe
(`_conn_prune_data`, cached on the universe dict):

1. **`dist_to_center[s]`** — Dijkstra minimum node-weight path cost from
   orbit s to the centre (node weight = orbit cost).  Any target containing
   s must contain a path from s to the centre, so `dist_to_center[s]` is a
   lower bound on the target's total cost.  If it exceeds the budget, the
   bucket is provably empty.
2. **`cells_ge[s]`** — |union of orbits with id ≥ s|.  A target with min-id
   s has every orbit ≥ s, so its V − 1 non-centre cells are a subset of that
   union; if the union has fewer than V − 1 cells, the bucket is provably
   empty.

**V35 data (corrected domain, 1,730 candidates):**

| Prune | Buckets eliminated |
|---|---|
| `dist_to_center[s] > 17` | 1,225 (all far zero-leaf buckets) |
| `cells_ge[s] < 34` | 16 (near two-orbits 1858..1873) |
| **Total** | **1,241 = all zero-leaf buckets; 0 survivors** |

The boundary is exact: `dist[558] = 17 = budget` and 558 is the first
leaf-bearing min-id.  Sanity: **0** of the 489 leaf-bearing min-ids violate
either necessary condition.

## 4. Exact leaf connectivity check

Every added orbit is centre-component-adjacent at add time, so the centre
component is always connected and is the only component besides possibly
the seed s.  The cell set is connected **iff** s is bridged into the centre
component (s ∈ start_front, or some added orbit is adjacent to s).  The
leaf check is therefore the `bridged` flag — no `is_face_connected` BFS.

## 5. Independent small-volume validation (pruned engine)

`validate_v45_enumeration.py --pruned small` — all PASS:

| Check | Result |
|---|---|
| V5 subset brute force (C(18,4) = 3060 subsets) | 2 targets |
| V5 pruned raw set == reference raw set | 2 == 2, no dups |
| V5 pruned canonical set == subset brute force | 2 == 2 |
| V15 pruned total == 368 | PASS |
| V15 pruned canonical set == cell-level brute force | 189 == 189 |
| V15 pruned raw set == reference raw set | 368 == 368, no dups |
| V25 pruned total == 71,539 | PASS |
| V25 pruned canonical set == cell-level brute force | 35,822 == 35,822 |
| V25 pruned raw set == reference raw set | 71,539 == 71,539, no dups |
| V25 per-min-id counts == reference hist | PASS (626 candidates, 172 hist keys) |
| V25 min-id coverage / ownership | PASS |

`--pruned determinism` (two PYTHONHASHSEED values): identical totals, counts,
and canonical hashes — PASS.  `--pruned partition` (V25, 4 shards): raw sets
pairwise disjoint, every target exactly one branch owner, sum == 71,539 —
PASS.

## 6. Benchmark (pruned vs original, V35, budget 17)

| bucket | leaves | original | pruned | pruned states |
|--------|-------:|---------:|-------:|--------------:|
| 100 | 0 | 81.8 s | **0.0 s** | 0 (root prune) |
| 300 | 0 | 97.3 s | **0.0 s** | 0 |
| 558 | 1 | 99.8 s | **13.9 s** | 2,704,558 |
| 800 | 0 | 58.6 s | **0.0 s** | 0 |
| 1000 | 66 | 118.1 s | **13.0 s** | 2,704,099 |
| 1200 | 2,306 | 146.7 s | **12.8 s** | 2,694,059 |
| 1335 | 68,072 | 60.9 s | **12.7 s** | 2,669,495 |
| 1450 | 0 | 92.6 s | **0.0 s** | 0 |
| 1550 | 261,366 | 195.6 s | **10.0 s** | 2,033,956 |

Every bucket yields exactly the same leaf set as the original.  The pruned
state count per leaf-bearing bucket ≈ N(17 − cost[s]) (connected
centre-sets of cost ≤ 15: 2.70 M; cost ≤ 16: 7.90 M).

## 7. V35 full validation (corrected domain)

Run: `validate_v45_enumeration.py --pruned v35`, launched 2026-09-19 08:11
NZST as systemd transient `v45-v35-pruned` (outside the OpenWork cgroup,
`.venv/bin/python -u`, log `/tmp/opencode/v45_validation/v35_pruned.log`).

**Result (2026-09-19): PASS — all checks green.**

```
== full corrected V35 enumeration over the corrected domain ==
  corrected candidate domain: 1730 min-ids [0..1873]
  [PASS] V35 reference total == 15,289,669 -- 15,289,669
  corrected V35 enumeration: 15,289,669 targets in 5031s
  [PASS] V35 corrected total == 15,289,669 -- 15,289,669
  [PASS] V35 per-min-id counts == reference hist on all hist keys -- mismatches=0
  [PASS] V35 zero targets on non-hist candidates
  [PASS] V35 min-id coverage: every hist key enumerated
  [PASS] V35 no duplicated ownership (per-bucket masks unique)
  [PASS] V35 histogram consistency (sum per-min-id == total)
V35 OK
```

- Total: **15,289,669** targets (matches the authoritative reference exactly).
- Per-min-id counts match the reference histogram on all 489 hist keys
  (mismatches = 0); zero targets on all 1,241 non-hist candidates; every
  hist key covered; per-bucket masks unique (no duplicated ownership);
  histogram sums to the total.
- Enumeration wall time **5,031 s (~84 min)** plus the ~134 s reference
  pass — vs the original engine's projected **~44–47 h** (11 h 50 m in,
  0 progress lines, still in the zero-leaf region; see
  `v45_validation_run_crash.md`).  ~30× speedup, peak RSS 7.2 GB
  (reference pass) / ~0.1–0.4 GB during enumeration.

## 8. George B-9 regression (min orbit id 3590)

Run: `validate_v45_enumeration.py --pruned george` (static checks + full
min-id-3590 subtree walk with the pruned engine).

**Correction to the historical evidence chain (2026-09-19):** the figure
"3,430,348 targets" that earlier docs attributed to the min-id-3590 subtree
is a leaf **position**, not a total.  The 2026-09-11 smoke test
(`ck6_sharding_corrected.smoke_george_b9`) stopped as soon as George's
target was found, after 3,430,348 targets; its note over-claimed that as
the full subtree total, and the harness inherited the error.  The
2026-09-12 monolithic runs (run2/run3, same enumeration
`iter_targets_seeded(un45, 3590, 22)`, `min_ids=[3590]`) reached 14.2M and
20,342,912 targets before RSS/RAM safety stops, so the subtree total is
**>= 20,342,912**.  The pruned walk below establishes the authoritative
total (same target set, provably complete).

**Result (2026-09-19): PASS — all checks green.**

```
== George B-9 regression ==
  [PASS] George target has 45 cells / face-connected / CK6-closed
  [PASS] George canonical id == oh-109166b4c83a
  [PASS] George min orbit id == 3590; orbit cost == 22
  [PASS] V45 start_front == {3652, 3937}; centre-adjacent orbits present
  [PASS] OLD prefilter excludes 3590 (bug reproduced)
  [PASS] CORRECTED filter accepts 3590; domain == 3696 min-ids
  George target found at leaf #2,488,006 (59s)
  [PASS] George target yielded exactly once by bucket 3590 -- found=1 total=22877932
  [PASS] min-id-3590 subtree total >= 20,342,912 (run3 partial) -- 22,877,932
  [PASS] Exactly one ownership path (min-id 3590 is intrinsic)
  subtree walk: 22,877,932 targets in 1638s
GEORGE OK
```

- **Authoritative min-id-3590 subtree total: 22,877,932 targets** (the
  run2/run3 partial counts 14.2M / 20,342,912 were consistent lower
  bounds; the smoke test's 3,430,348 was a leaf position, not a total).
- George's B-9 target (oh-109166b4c83a) is yielded **exactly once** by
  bucket 3590 — at leaf #2,488,006 in the pruned DFS order (the original
  engine's order placed it at #3,430,348; the target set is identical).
- Walk wall time **1,638 s (~27 min)**, peak RSS ~6.1 GB — vs the
  original engine's run2/run3, which were still running at 20.3M targets
  / 98 min / 16 GB RSS when the RAM safety stop fired.

## 9. Related prior work

- `solvers/test_strong_prune.py` and `solvers/t_ck6_oddity_v35_search_pruned.py`
  (untracked): per-state component-connectivity lower bounds.  Superseded by
  the structural connectivity prune + root reachability prunes, which are
  provably complete, exact at the leaf, and eliminate all zero-leaf buckets
  at the root.
- `docs/frontier/v45_validation_run_crash.md`: crash diagnosis and the V35
  slowness analysis that motivated the pruned engine.