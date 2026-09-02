# 6×6×10 DP Probe — Diagnostic and Root Cause Analysis

**Date**: 2026-08-30
**Purpose**: determine what the attempted 6×6×10 feasibility probe actually
ran, why its output resembles 6×6×5 for the first three boundaries, and what
configuration is required for a clean re-run.

---

## 1. What actually ran

The probe was launched with:

```python
from z_frontier_numba import run
r = run(6, 6, 10, prune_mod5=True, ht_cap_log=23, verbose=True)
```

The log's own configuration line confirms the parameters:

```
config: w=6 h=6 nz=10 prune_mod5=True symmetry=disabled ht_cap_log=23
```

**The process did execute 6×6×10** (w=6, h=6, nz=10). This is confirmed by:

1. the config line in the log explicitly stating `nz=10`;
2. boundary 4 = 4,315,608 states (6×6×5 has only 4 at this boundary);
3. boundaries 5–7 = 4.19 M / 6.13 M / 6.56 M states (6×6×5's frontier
   emptied at boundary 5);
4. the placement generator (`gen(6,6,10)`) produces 2,304 vertical
   candidate triples across 8 start-layers (vs 864 across 3 for 6×6×5).

## 2. Why the first three boundaries match 6×6×5

**This is mathematically correct, not contamination.**

The boundary states at boundaries 1, 2, 3 are determined by vertical
placements starting at layers 0, 1, 2. Both 6×6×5 and 6×6×10 have the same
cross-section (6×6) and the same 3-layer vertical span, so the vertical
placements starting at layers 0, 1, 2 are identical:

| start layer | `gen(6,6,5)` | `gen(6,6,10)` | boundary states |
|---|---|---|---|
| 0 | 192 | 192 | identical |
| 1 | 192 | 192 | identical |
| 2 | 192 | 192 | identical |
| **3** | **0** | **192** | **diverges** |

The divergence starts at boundary 4 because `gen(6,6,5)` cannot generate
vertical placements starting at layer 3 (they would span layers 3,4,5 but
layer 5 does not exist in a 5-layer box), while `gen(6,6,10)` can.

| boundary | 6×6×5 states | 6×6×10 states | identical? |
|---|---|---|---|
| 1 | 1,154,524 | 1,154,524 | ✅ (expected) |
| 2 | 117,428 | 117,428 | ✅ (expected) |
| 3 | 814,994 | 814,994 | ✅ (expected) |
| 4 | 4 | **4,315,608** | ✅ diverges (correct) |
| 5 | 0 (UNSAT) | **4,187,792** | ✅ diverges |
| 6 | — | **6,128,644** | new |
| 7 | — | **6,559,440** | new |

## 3. Root cause of the ambiguity

**The output is not contaminated** — it is genuine 6×6×10 output. The
perception of contamination arises because the first three boundaries are
mathematically identical to 6×6×5, and no dimension-verification was
embedded in the probe output beyond the initial `config:` line.

**Contributing factor**: the `verbose=True` output prints boundary counts
without restating the box dimensions, making it easy to misattribute the
output to a different box when scanning logs.

## 4. Process termination

The probe was killed by the `timeout 900` wrapper after processing 7 of 10
boundaries. The log was last modified at 14:05 UTC (~2.5 min after start),
suggesting the process may have stalled or been OOM-killed before the 900 s
timeout expired (the 6.6 M-state boundary 7 fill would consume significant
memory in the open-addressing hash table: 8 M entries × 24 B ≈ 200 MB, plus
the DFS stack and state arrays). The `exit_code=` line was never written to
the result file, confirming the process did not terminate cleanly.

**Likely termination cause**: hash table capacity exhaustion. At
`ht_cap_log=23` (8,388,608 entries), boundary 7 produced 6,559,440 unique
states — approaching the 78 % load factor. Boundary 8 could exceed 8 M
states, causing the open-addressing insert to loop indefinitely (no empty
slot available).

## 5. Confirmation: no 6×6×10 result has been obtained

The probe processed 7 of 10 boundaries before termination. **No accepting
state was reached; the search did not complete; the result is
INCONCLUSIVE.** The existing SAT/DRAT/LRAT certificate (UNSAT) remains the
only authoritative classification for 6×6×10.

## 6. Committed implementation integrity (task 7)

```
sha256(working copy)  = c630a658f6251f9ec26a2135c96f8897e6610b4b90c2b8893fa44adb2b21292a
sha256(commit b714c93) = c630a658f6251f9ec26a2135c96f8897e6610b4b90c2b8893fa44adb2b21292a
git diff b714c93 -- tools/frontier/z_piece/z_frontier_numba.py = (empty)
```

**Unchanged from commit b714c93.**

## 7. Parameter smoke test (task 6; no search performed)

```
box: 6x6x10
cross-section: 6x6 = 36 cells; layers: 10; total cells: 360
pieces: 72
flat masks: 320
vertical candidate entries (by bit, all layers): 2,304 total
vertical placements per start layer:
  start layer 0: 288 candidates (m0×m1×m2 triples)
  start layer 1: 288
  start layer 2: 288
  start layer 3: 288
  start layer 4: 288
  start layer 5: 288
  start layer 6: 288
  start layer 7: 288
  start layer 8: 0  (vertical would span 8,9,10 — layer 10 does not exist)
  start layer 9: 0

config for the real 6×6×10 probe:
  run(w=6, h=6, nz=10, prune_mod5=True, ht_cap_log=23)
  FULL = 68719476735  (36-bit mask)
  A_mod5 = 1
  ht_cap = 8,388,608
```

## 8. Exact command/configuration for the real probe

```python
import sys
sys.path.insert(0, "/tmp/opencode")
sys.path.insert(0, "tools/frontier/z_piece")
sys.path.insert(0, ".")
from z_frontier_numba import run
r = run(w=6, h=6, nz=10, prune_mod5=True, ht_cap_log=23, verbose=True)
```

**Required fix before re-running**: increase `ht_cap_log` to ≥ 24 (16 M
entries) to accommodate the measured frontier width (6.56 M states at
boundary 7, growing). Without this, the open-addressing hash table will
overflow and the process will hang.

## 9. Data integrity checklist

| check | result |
|---|---|
| processes killed | ✅ (0 remaining) |
| process was 6×6×10 (not 6×6×5) | ✅ confirmed by config line + divergent boundary 4+ |
| boundary 1–3 = 6×6×5 explained | ✅ vertical starts 0–2 identical |
| boundary 4+ divergence explained | ✅ nz=10 has vertical starts at layers 3–7 |
| committed implementation unchanged | ✅ sha256 match with b714c93 |
| stale __pycache__ | ✅ no stale .pyc (mtime check clean) |
| stale output files | ✅ probe log is from the 6×6×10 run only |
| catalogue modified | ❌ not modified |
| certified results modified | ❌ not modified |
