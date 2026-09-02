# Z 6×7×10 SAT/DRAT Result

**Date**: 2026-08-30
**Purpose**: determine whether the audited SAT/DRAT certificate pipeline can
settle Z box 6×7×10, testing whether the pipeline that certified 6×6×10
scales to the wider 6×N Z family.

**Final status: INCONCLUSIVE / RESOURCE-LIMITED.** The CaDiCaL solve was
killed by the 3,600 s (1 hour) timeout without reaching a verdict.

---

## 1. Catalogue status

| check | result |
|---|---|
| `classify(6,7,10)` | `Unknown` |
| `impossible_reason` | `None` |
| in `RAW_PRIMES` / `PUBLISHED_SOLUTIONS` / `SEARCHED_NO_SOLUTION` | No / No / No |
| frontier-DP attempt | INCONCLUSIVE (900 s, 3/10 boundaries; see `z_6x7x10_frontier_result.md`) |

## 2. Placement audit (task 2)

| metric | value |
|---|---|
| box | 6×7×10 (420 cells = 84 pieces) |
| cross-section | 6×7 = 42 cells (single-limb int64 ✓) |
| placements | **2,656** (800 flat + 1,856 vertical) |
| placements per cell | min 6, max 60 (geometry-capped as for 6×6×10) |
| orientations | 12 (4 planar × 3 planes) |
| bad shape / bad bounds | 0 / 0 |
| uncovered cells | 0 / 420 |
| placement equivalence vs `generate_placements` | **True** (2,656 = 2,656, frozenset equality, 0 differences) |

## 3. CNF construction (task 3)

| metric | 6×6×10 | 6×7×10 | ratio |
|---|---|---|---|
| placements (vars) | 2,176 | **2,656** | 1.22× |
| clauses (total) | 195,976 | **248,644** | 1.27× |
| ≥1 (coverage) | 360 | **420** | 1.17× |
| AMO (no-overlap) | 195,616 | **248,224** | 1.27× |
| CNF size | 2.6 MB | **3.3 MB** | 1.27× |
| CNF sha256 | `03489962…` | **`afc8dc5f…`** | — |

The clause growth is **linear** in placements (≈ 94 AMO clauses per
placement), consistent with the geometry-capped 60-places-per-cell bound.

## 4. Encoding audit (task 4)

| check | result |
|---|---|
| every cell has ≥1 covering placement | ✅ 420/420 |
| every placement legal (5 cells, Z-congruent, in-box) | ✅ 0 violations in 2,656 |
| AMO pairs = shared-cell conflicts | ✅ (canonical CNF, 0 mixed-polarity) |
| placement-set equivalence vs repository | ✅ (2,656 = 2,656) |
| deterministic canonical DIMACS | ✅ (literals sorted, clauses sorted) |
| CNF sha256 | `afc8dc5fd17373bae1ad8b887aae8692bc2b4c52fe1bda30230042ea4811fdc7` |

## 5. CaDiCaL solve (tasks 5, 9)

| parameter | 6×6×10 | 6×7×10 |
|---|---|---|
| solver | CaDiCaL153 (python-sat 1.9.dev15) | same |
| proof logging | enabled (`with_proof=True`) | enabled |
| timeout | 900 s (sufficient) | **3,600 s (insufficient)** |
| result | **UNSAT in 287 s** | **killed at 3,600 s — no verdict** |
| CPU time | 287 s | **≥ 55 min** (last observed 42 min, timeout at ~55 min) |
| DRAT proof | 7.4M lines / 2.42 GB | not produced (solve did not complete) |

**The CaDiCaL solve did not complete within 1 hour.** The instance is
significantly harder for CDCL than 6×6×10 — the wider cross-section and
larger placement set produce a search space that CaDiCaL's clause learning
could not exhaust in the available time.

## 6. Scaling analysis (task 10)

| metric | 6×6×10 | 6×7×10 | ratio |
|---|---|---|---|
| placements | 2,176 | 2,656 | 1.22× |
| clauses | 195,976 | 248,644 | 1.27× |
| cross-section cells | 36 | 42 | 1.17× |
| pieces | 72 | 84 | 1.17× |
| SAT solve time | 287 s | **> 3,600 s (incomplete)** | **> 12.5×** |

The clause count grows linearly (1.27×), but the **solve time** grew by at
least 12.5× (287 s → > 3,600 s incomplete). This super-linear scaling
reflects CDCL's sensitivity to the problem structure: the 6×7 cross-section
provides more freedom per layer, making the proof search exponentially
harder even though the encoding size grows only modestly.

## 7. Why 6×7×10 is harder than 6×6×10

The 6×7 cross-section (42 vs 36 cells) provides ~17% more area, but the
effect on solver difficulty is super-linear:

1. **More placements per boundary state**: the frontier DP measured 27M
   layer-0 completions (vs 1.15M for 6×6) — a 23× explosion. CDCL faces the
   same combinatorial widening.
2. **More vertical placements per start layer**: 232 (6×7) vs 192 (6×6) —
   more branching choices for the solver.
3. **Larger layer area** means fewer forced constraints per piece — the
   solver must explore more partial assignments before reaching a
   contradiction.

## 8. What would settle 6×7×10

| approach | feasibility | estimated cost |
|---|---|---|
| CaDiCaL with longer timeout | possible | ~hours (extrapolating from >55 min at timeout) |
| CaDiCaL with `--max-cores` / portfolio | moderate improvement | ~hours |
| CP-SAT with layer equations | unknown; 6×10×10 was also UNKNOWN at 300 s | ~minutes to hours |
| SAT + D2 symmetry breaking | 6×7 has only 2 mirror symmetries (not square); ~2× reduction | ~half the time |
| SAT with incremental encoding | would help if solving multiple related boxes | n/a for single box |
| Frontier DP with D2 symmetry + Numba | the formulation works; the 6×7 frontier is too wide for the current implementation | ~hours |
| Frontier DP + in-plane flat-tiling oracle | would collapse boundary widths significantly | research needed |

## 9. Certificate implications (task 8)

No certificate was produced — the solve did not complete. If a future run
completes:

* **UNSAT**: the DRAT/LRAT pipeline applies exactly as for 6×6×10
  (drat-trim + lrat-check on the archived CNF + proof).
* **SAT**: the extracted tiling is validated by `validate_tiling` and
  packaged as a tiling-witness JSON (independent exact-cover + Z-congruence
  verification).

## 10. Conclusion

**6×7×10 remains UNKNOWN.** Neither the frontier DP (900 s, 3/10 boundaries)
nor the SAT pipeline (3,600 s, no verdict) could settle it within the
bounded budgets tested. The instance is a genuine combinatorial challenge —
the 6×7 cross-section provides enough freedom to make both approaches
resource-limited.

The existing 6×6×10 certificate pipeline is **validated and correct** — the
difficulty is not in the pipeline but in the intrinsic complexity of the
6×7 instance. Future work should focus on:

1. longer SAT runs (hours, not minutes);
2. symmetry-reduced encodings;
3. frontier DP with the in-plane flat-tiling oracle (structural reduction);
4. or a mathematical argument specific to the 6×7 cross-section.

## 11. Reproduction

```bash
cd /home/philip/Work/fitpolycubes
timeout 3600 .venv/bin/python -u /tmp/opencode/z_6710_sat.py
```

CNF preserved at `/tmp/opencode/z_6710_certificate/z_6710.cnf`
(sha256 `afc8dc5fd17373bae1ad8b887aae8692bc2b4c52fe1bda30230042ea4811fdc7`).
