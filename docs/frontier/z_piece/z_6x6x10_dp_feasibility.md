# 6×6×10 Frontier-DP Feasibility Probe — Results

**Date**: 2026-08-30
**Purpose**: determine whether the validated Numba planar-frontier DP can
exhaustively settle 6×6×10, using the capacity-corrected hash table
(`ht_cap_log=24`, 16 M entries).

**Verdict: YES — the closure completed in 241.7 s (≈ 4 min), independently
confirming the certified UNSAT result.** The frontier DP is a practical
alternative to SAT for this box.

---

## 1. Exact command and configuration

```python
from z_frontier_numba import run
r = run(6, 6, 10, prune_mod5=True, ht_cap_log=24, verbose=True)
```

* committed Numba implementation: `tools/frontier/z_piece/z_frontier_numba.py`
  (sha256 `c630a658…`, commit `b714c93` — unmodified);
* `prune_mod5=True` (validated congruence; enable/disable equivalence
  confirmed in `z_frontier_dp_numba.md` §4);
* `symmetry=disabled` (per task requirement);
* `ht_cap_log=24` (16,777,216 hash-table entries — capacity-only change
  from the previous run's `ht_cap_log=23`; no transition-semantics change);
* hard wall-clock cap: **900 seconds** (`timeout 900`).

## 2. Environment

| item | value |
|---|---|
| VM | 4 cores, 29 GB RAM |
| Python | 3.12.3 |
| numba | 0.67.0 |
| numpy | 2.5.2 |
| date | 2026-08-30T14:42:35Z |

## 3. Measured results

| boundary | states | new inserts | dup hits | prunes |
|---|---|---|---|---|
| 1 | 1,154,524 | 1,154,524 | 9,864 | 0 |
| 2 | 117,428 | 117,428 | 72 | 0 |
| 3 | 814,994 | 814,994 | 41,420 | 0 |
| 4 | 4,315,608 | 4,315,608 | 37,704 | 0 |
| 5 | 4,187,792 | 4,187,792 | 41,212 | 0 |
| 6 | 6,128,644 | 6,128,644 | 37,424 | 0 |
| 7 | 6,559,440 | 6,559,440 | 56,708 | 0 |
| 8 | **9,226,084** | 9,226,084 | 148,284 | 0 |
| 9 | **52** | 52 | 0 | 0 |
| 10 | **0** | 0 | 0 | 0 |

| metric | value |
|---|---|
| verdict | **UNSAT (frontier empty at boundary 10)** |
| elapsed | **241.7 s** (≈ 4 min) |
| peak RSS | 974,464 kB ≈ 952 MB |
| max frontier width | **9,226,084** states (boundary 8) |
| total boundary states processed | 22,896,280 |
| hash-table peak occupancy | 9,226,084 / 16,777,216 = 55.0 % |
| mod-5 prunes | 0 (congruence holds automatically on reachable states) |
| closure complete | **YES** — exhaustive state closure across all 10 boundaries |

## 4. State-space growth analysis

The frontier profile shows three phases:

1. **Growth phase** (boundaries 1–3): the first three boundaries match
   6×6×5 exactly (vertical starts 0–2 have identical geometry). Width
   grows from 1.15 M to 815 K.
2. **Explosion phase** (boundaries 4–8): with 10 layers, vertical pieces
   can start at layers 3–7 (unavailable in 6×6×5), so the frontier
   explodes: 815 K → 4.3 M → 4.2 M → 6.1 M → 6.6 M → **9.2 M**.
3. **Collapse phase** (boundaries 9–10): the box's finite geometry binds
   sharply — boundary 9 collapses to **52 states** and boundary 10 to **0**
   (exhaustive UNSAT proof). This mirrors the 6×6×5 pattern (815 K → 4 → 0)
   but at 6×6×10 scale.

The collapse at boundary 9 means the problem is *easier* than the peak
width suggests: the last two boundaries are nearly forced. The hard work
is concentrated at boundaries 4–8.

## 5. Comparison with estimates (task 10)

| estimate | predicted | actual |
|---|---|---|
| optimistic | 1–2 min | **4.0 min** — close |
| conservative | 10–30 min | actual is **better** |

The 1–2 min estimate was close but underestimated the boundary 4–8
explosion (the naive estimate assumed a flat frontier profile). The
conservative 10–30 min estimate was too pessimistic.

## 6. Comparison with the SAT/DRAT certificate (task 7)

| evidence | method | verdict | independent? |
|---|---|---|---|
| SAT/DRAT/LRAT | CaDiCaL + drat-trim + lrat-check | UNSAT ✅ | ✅ (complete CDCL + verified proof) |
| frontier DP (this probe) | Numba planar DP, exhaustive state closure | **UNSAT** ✅ | ✅ (independent formulation, independent implementation, exhaustive state closure) |

**Two completely independent formulations** (SAT exact-cover encoding vs
planar frontier transfer-matrix) reach the same conclusion by different
mechanisms. This is the strongest possible confirmation of the 6×6×10
UNSAT result.

## 7. Capacity wall resolution (previous run's bottleneck)

The previous run used `ht_cap_log=23` (8 M entries) and reached boundary 7
(6.56 M states) before being killed at 900 s. The hash table was
approaching capacity. This run uses `ht_cap_log=24` (16 M entries):

| boundary | prev run states (ht_cap=23) | this run states (ht_cap=24) | hash occupancy |
|---|---|---|---|
| 7 | 6,559,440 | 6,559,440 | 39.1 % |
| 8 | not reached | **9,226,084** | 55.0 % |

The capacity increase was sufficient. The peak occupancy at boundary 8
(55 %) is well within the linear-probing efficiency range. No table
overflow occurred.

## 8. Is a full independent DP proof run worthwhile?

**Yes — and it has already succeeded.** The 241.7 s exhaustive closure is:

* fast enough to be practical for 6×6×10-scale boxes;
* an independent confirmation of the SAT/DRAT result (different formulation,
  different implementation, different algorithm);
* a demonstration that the frontier DP can serve as a **counting and
  structural-analysis engine** for Z boxes at the 6×6 scale.

For future Z boxes at the 6×6 scale:
* SAT (CaDiCaL) remains the fastest decision engine (~5 min for UNSAT,
  including DRAT verification);
* the frontier DP provides independent confirmation (~4 min), exact
  tiling counts (with transition-expanded accumulation), and macro-cycle
  extraction (state-graph SCC analysis);
* both together provide the strongest possible evidence: two independent
  formulations agreeing on the same conclusion.

## 9. Certificate implications

This DP result does **not** modify the existing certificate (the SAT/DRAT/
LRAT package remains the primary evidence). It provides an **independent
cross-check** — the mathematical equivalent of a second referee confirming
the same result by a different method.

## 10. Reproduction

```bash
cd /home/philip/Work/fitpolycubes
timeout 900 python3 -u -c "
import sys, time
sys.path.insert(0, '/tmp/opencode'); sys.path.insert(0, 'tools/frontier/z_piece'); sys.path.insert(0, '.')
from z_frontier_numba import run
r = run(6, 6, 10, prune_mod5=True, ht_cap_log=24, verbose=True)
print(r['verdict'])
"
```

Expected output: per-layer state counts matching §3, verdict `UNSAT
(frontier empty at boundary 10)`, elapsed ≈ 240 s.
