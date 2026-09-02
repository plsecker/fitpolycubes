# Z 6×7×10 Frontier-DP Result

**Date**: 2026-08-30
**Purpose**: bounded feasibility probe of the validated Numba planar-frontier
DP on Z box 6×7×10 (currently UNKNOWN). Single-box investigation; no
catalogue changes; no SAT/CP-SAT runs; no broad searches.

**Final status: INCONCLUSIVE / RESOURCE-LIMITED.** The DP processed 3 of 10
boundaries before the 900 s wall-clock cap. No UNSAT or SAT conclusion can
be drawn.

---

## 1. Catalogue status (task 1)

| check | result |
|---|---|
| `classify(6,7,10)` | `Unknown` |
| `impossible_reason` | `None` |
| in `RAW_PRIMES` | No |
| in `PUBLISHED_SOLUTIONS` | No |
| in `SEARCHED_NO_SOLUTION` | No |
| in Shirakawa page (6×7 row) | only `6×7×25` (prime); no 6×7×10 |
| decomposition closure (`classify`) | no existing decomposition closes it |

**6×7×10 is genuinely UNKNOWN** — no existing evidence or decomposition
resolves it.

## 2. Geometry

| item | value |
|---|---|
| box | 6×7×10 |
| cross-section | 6×7 = **42 cells** (single-limb uint64 ✓) |
| layers | 10 |
| volume | 420 = 84 pieces |
| flat masks | 80 (4 orientations × 20 positions) |
| vertical triples per start layer | 232 (starts 0–7; starts 8–9 empty) |
| total placements | 800 flat + 1,856 vertical = **2,656** |

## 3. Exact command and configuration (task 1)

```python
from z_frontier_numba import run
r = run(6, 7, 10, prune_mod5=True, ht_cap_log=25, verbose=True)
```

| parameter | value | rationale |
|---|---|---|
| `prune_mod5` | `True` | validated congruence (A mod 5 = 2); enable/disable equivalence confirmed |
| `ht_cap_log` | 25 (32 M entries) | capacity sized for the wider 6×7 cross-section (6×6×10 used 24) |
| symmetry | disabled | per task requirement |
| wall-clock cap | 900 s | `timeout 900` (hard kill) |

## 4. Environment

| item | value |
|---|---|
| VM | 4 cores, 29 GB RAM |
| Python | 3.12.3 |
| numba | 0.67.0 |
| numpy | 2.5.2 |
| start | 2026-08-30T15:17:27Z |
| terminated | ~2026-08-30T15:32:27Z (900 s timeout) |

## 5. Measured results (tasks 5, 8)

| boundary | states | new inserts | dup hits | prunes |
|---|---|---|---|---|
| 1 | **27,067,552** | 27,067,552 | 217,580 | 0 |
| 2 | **1,419,442** | 1,419,442 | 1,274 | 0 |
| 3 | **14,467,846** | 14,467,846 | 674,960 | 0 |
| 4–10 | not reached | — | — | — |

| metric | value |
|---|---|
| boundaries processed | **3 of 10** |
| closure complete | **NO** |
| result | **INCONCLUSIVE / RESOURCE-LIMITED** |

### Comparison with 6×6×10

| boundary | 6×6×10 | 6×7×10 | ratio |
|---|---|---|---|
| 1 | 1,154,524 | **27,067,552** | **23.4×** |
| 2 | 117,428 | **1,419,442** | **12.1×** |
| 3 | 814,994 | **14,467,846** | **17.8×** |

The 6×7 cross-section produces dramatically wider frontiers than 6×6:
the additional column provides ~23× more layer-0 completion possibilities.

### Frontier dynamics

| phase | observation |
|---|---|
| boundary 1 | **explosion**: 27 M completions of layer 0 (vs 1.15 M for 6×6×10) |
| boundary 2 | sharp contraction: 27 M → 1.4 M (19× reduction) — the vertical pieces started at layer 0 are highly constrained by layer 1's geometry |
| boundary 3 | re-expansion: 1.4 M → 14.5 M (10× growth) — verticals starting at layer 2 open new possibilities |
| boundaries 4–10 | not reached — the 900 s budget was consumed by the boundary 1 and 3 fill enumerations |

## 6. Scaling analysis (task 7)

The 6×7 cross-section (42 cells vs 36 for 6×6) produces:

* **~23× wider boundary 1**: the 7-column dimension creates many more
  placement combinations (80 flat masks vs 64; 232 vertical triples per
  start layer vs 192);
* **higher per-state fill cost**: 42 cells per layer vs 36 — the
  lowest-empty-cell DFS explores more branches per completion;
* **net effect**: ~17× more boundary states at boundary 3, and the total
  fill work exceeded 900 s for only 3 of 10 layers.

The scaling from 6×6 to 6×7 is **not a simple size increase** — it is a
combinatorial widening that makes the pure-Python/numba frontier DP
significantly more expensive. A 6×8 or 7×7 cross-section would be wider
still.

## 7. What would be needed to settle 6×7×10

| approach | feasibility | estimated cost |
|---|---|---|
| Numba DP with more memory/time | possible but expensive | ~2–6 hours (estimated from the 900 s / 3-boundary data point) |
| Numba DP + D4 symmetry reduction | 6×7 is not square — only D2 (4 transforms: 180° + 2 mirrors); reduction factor ~2–4×, not 8× | moderate |
| SAT (CaDiCaL + drat-trim) | the audited encoding scales linearly (§2 of the strategy doc); 2,656 placements → ~200k clauses — likely fast | minutes |
| CP-SAT with layer equations | the 42-cell cross-section makes the per-layer equations stronger (more constrained); worth trying | minutes |
| witness-guided (if a tiling is published) | no published tiling for 6×7×10 | n/a |

## 8. Certificate implications (task 8)

If the DP completes with SAT, the extracted tiling can be converted to the
existing certificate framework:

* **tiling-witness JSON**: 84 placements as cell sets → independent
  exact-cover + Z-congruence validation (the `validate_tiling` protocol,
  already validated against the published 6×10×10 ground truth);
* the witness JSON format matches the `macro-walk-certificate` schema's
  geometry conventions (piece geometry authoritative, checker derives
  everything).

No DRAT proof is needed for SAT results — the tiling itself is the
certificate (constructive and independently checkable).

## 9. Recommendation

**6×7×10 should be attacked with SAT (CaDiCaL), not the frontier DP.** The
frontier DP is the right tool for 6×6-scale cross-sections (where it
completed in 242 s), but the 6×7 cross-section produces a frontier too wide
for the current implementation. The SAT encoding's linear clause scaling
(~90 clauses/placement, 2,656 placements → ~200k clauses) is well within
CaDiCaL's capability.

If the SAT result is UNSAT, the DRAT/LRAT certificate pipeline applies
exactly as for 6×6×10. If SAT, the tiling witness provides a constructive
certificate. In both cases, the evidence is catalogue-grade.

The frontier DP should be revisited for 6×7-scale boxes after a Numba port
with D2 symmetry reduction and the in-plane flat-tiling oracle — the
current bottleneck is the pure-Python/numba layer-fill enumeration, not the
formulation itself.

## 10. Reproduction

```bash
cd /home/philip/Work/fitpolycubes
timeout 900 python3 -u -c "
import sys
sys.path.insert(0, '/tmp/opencode'); sys.path.insert(0, 'tools/frontier/z_piece'); sys.path.insert(0, '.')
from z_frontier_numba import run
r = run(6, 7, 10, prune_mod5=True, ht_cap_log=25, verbose=True)
print(r['verdict'])
"
```
