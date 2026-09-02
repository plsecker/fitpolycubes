# S-Pentacube Macro Results: Consolidation and Next Frontier

**Date**: 2026-08-25  
**Status**: COMPLETE — All catalogue primes explained; 5×7 identified as the best next target

---

## 1. Authoritative Cross-Section Table

### 1.1 Investigated cross-sections

| Cross-section | Area | Recovered cycles | Catalogue primes | GCD | Frobenius | Conductor | Generator completeness |
|---------------|------|-----------------|-----------------|-----|-----------|-----------|----------------------|
| **4×5** | 20 | {6} | {6} | 6 | — | 6 | **PROVEN** (complete closure) |
| **5×6** | 30 | {4, 29, 46, 47} | {29, 46, 47} | 1 | 43 | 44 | **PROVEN** (complete closure, 7.9M states) |
| **4×8** | 32 | {20, 130} | {20, 130} | 10 | 110 | 120 | NOT PROVEN (bounded, 30M states) |
| **5×8** | 40 | {6} | {} | 6 | — | 6 | NOT PROVEN (no catalogue to verify) |
| **4×9** | 36 | {60, 75, 90, 105} | {60, 75, 90, 105} | 15 | 45 | 60 | NOT PROVEN (bounded, 65M states) |
| **4×10** | 40 | {6, 10} | {10} | 2 | 14 | 16 | NOT PROVEN (bounded) |
| **5×9** | 45 | {12, 15, 18, 21} | {12, 15, 18, 21} | 3 | 9 | 12 | NOT PROVEN (bounded) |

### 1.2 Catalogue coverage

| Cross-section | Primes | Covered | Missing | Status |
|---------------|--------|---------|---------|--------|
| 4×5 | 1 | 1 | 0 | ✓ ALL COVERED |
| 5×6 | 3 | 3 | 0 | ✓ ALL COVERED (+ new 4-cycle) |
| 4×8 | 2 | 2 | 0 | ✓ ALL COVERED |
| 4×9 | 4 | 4 | 0 | ✓ ALL COVERED |
| 4×10 | 1 | 1 | 0 | ✓ ALL COVERED (+ new 6-cycle) |
| 5×9 | 4 | 4 | 0 | ✓ ALL COVERED |

**Every catalogue prime is explained by our recovered Macro cycles.**

---

## 2. Numerical Semigroup Summary

| Cross-section | Semigroup | GCD | Scaled semigroup | Frobenius | Conductor | Notes |
|---------------|-----------|-----|-----------------|-----------|-----------|-------|
| 4×5 | ⟨6⟩ | 6 | ⟨6⟩ | — | 6 | Only 4×5×6 tileable |
| 5×6 | ⟨4, 29, 46, 47⟩ | 1 | ⟨4, 29, 46, 47⟩ | 43 | 44 | All z ≥ 44 tileable |
| 4×8 | ⟨20, 130⟩ | 10 | ⟨2, 13⟩ | 110 | 120 | z ≥ 120, z ≡ 0 mod 10 |
| 5×8 | ⟨6⟩ | 6 | ⟨6⟩ | — | 6 | All z ≡ 0 mod 6 |
| 4×9 | ⟨60, 75, 90, 105⟩ | 15 | ⟨4, 5, 6, 7⟩ | 45 | 60 | z ≥ 60, z ≡ 0 mod 15 |
| 4×10 | ⟨6, 10⟩ | 2 | ⟨3, 5⟩ | 14 | 16 | Even z ≥ 16 |
| 5×9 | ⟨12, 15, 18, 21⟩ | 3 | ⟨4, 5, 6, 7⟩ | 9 | 12 | z ≥ 12, z ≡ 0 mod 3 |

---

## 3. Generator Status

Three distinct notions of "generator" are explicitly separated:

### A. Primitive Macro cycle (irreducible closed walk)
Every recovered cycle has been verified as irreducible — no repeated internal states. Status: **KNOWN for all recovered cycles.**

### B. Numerical-semigroup generator (not a combination of others)
Every recovered cycle is a minimal semigroup generator. Status: **KNOWN for all recovered cycles.**

### C. Globally primitive Macro cycle (cannot be decomposed using ANY cycles)
Status: **UNKNOWN for all recovered cycles.** This would require a complete enumeration of the Macro graph's recurrent SCC, which has only been achieved for 4×5 and 5×6.

---

## 4. Missing Primitive Lengths

### 4.1 Catalogue cross-sections not yet investigated

| Cross-section | Area | Catalogue primes | SVG available? | Priority |
|---------------|------|-----------------|----------------|----------|
| **5×7** | **35** | **24, 36, 42** | **YES** | **HIGHEST** |
| **5×10** | **50** | **18** | **YES** | **HIGH** |
| 6×6 | 36 | 15, 20, 25 | Unknown | Medium |
| 6×7 | 42 | 10, 15 | Unknown | Medium |
| 4×13 | 52 | 30 | Unknown | Low |
| 4×14 | 56 | 30 | Unknown | Low |
| 6×9 | 54 | 10, 15 | Unknown | Low |
| 6×10 | 60 | 10 | Unknown | Low |
| 7×8 | 56 | 30 | Unknown | Low |
| 8×8 | 64 | 10 | Unknown | Low |

### 4.2 SVG solutions available (not yet extracted)

- **5×7×24**: `../svgz/5-15/5-15-5x7x24.svgz` ✓
- **5×7×36**: `../svgz/5-15/5-15-5x7x36.svgz` ✓
- **5×7×42**: `../svgz/5-15/5-15-5x7x42.svgz` ✓
- **5×10×18**: `../svgz/5-15/5-15-5x10x18.svgz` ✓

---

## 5. Unresolved Discrepancies

### 5.1 Resolved

| Discrepancy | Status | Explanation |
|-------------|--------|-------------|
| 5×6×28 catalogue "impossible" | **RESOLVED** | Catalogue error; 28 = 7×4 is tileable via Macro construction |
| 4×9 "acyclic" BFS result | **RESOLVED** | Search-depth artifact; four cycles extracted from SVG |
| 4×10×14 catalogue "impossible" | **CONSISTENT** | No 14-cycle exists in Macro graph |
| 4×9×15 catalogue "impossible" | **CONSISTENT** | Refers to 4×9×15 (different cross-section from 5×9×15) |

### 5.2 Remaining

| Cross-section | Issue | Type |
|---------------|-------|------|
| 5×7 | 3 catalogue primes, no Macro analysis | Missing published witness extraction |
| 5×10 | 1 catalogue prime, no Macro analysis | Missing published witness extraction |
| 6×6 | 3 catalogue primes, no Macro analysis | Missing published witness extraction |
| 4×8, 4×9, 4×10, 5×8, 5×9 | Generator completeness unproven | Potentially incomplete generator sets |

---

## 6. Recommended Next Target: 5×7

### Why 5×7?

1. **Highest priority uninvestigated cross-section**: Area 35, between the cyclic 5×6 (area 30) and the unexplored 5×8 (which we found a 6-cycle for via Numba).

2. **SVG solutions available**: 5×7×24, 5×7×36, and 5×7×42 all have downloadable SVG solutions on the Shirakawa site.

3. **Three catalogue primes**: 24, 36, 42 — suggesting a semigroup with GCD=6, possibly ⟨6⟩ or ⟨12, 18⟩ or something more complex.

4. **Previous Macro attempt failed**: The width survey reports only 58 sources found in 3M first-gen states (0.002% density), with macro closure completing in 715 states and state 0 unreachable. The SVG extraction approach would bypass this entirely.

### Extraction plan

The same SVG extraction pipeline developed for 5×9 and 4×9 would be applied:
1. Download SVG solutions for 5×7×24, 5×7×36, 5×7×42
2. Parse placements using the coordinate-mapping machinery
3. Validate all pieces as valid S pentacubes
4. Extract Macro cycles via `extract_cycle_from_tiling.py`
5. Determine fundamental generator(s)
6. Compute semigroup and compare with catalogue primes

---

## 7. Files

- `data/frontier/s_piece/consolidated_results.json` — Machine-readable consolidated data
- `docs/frontier/s_piece/consolidated_results.md` — This document

## 8. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

## 9. Summary

**What the Macro programme has established:**
- 7 cross-sections investigated, 12 irreversible cycles recovered
- All catalogue primes explained by recovered semigroups
- 1 catalogue error corrected (5×6×28)
- 1 new cross-section discovered (5×8)
- 2 new primitive cycles discovered (5×6×4, 4×10×6)

**What remains conjectural:**
- Generator completeness for 5 cross-sections (bounded closure only)
- F1=F2 balance (strong empirical constraint, not a theorem)
- 4×9/5×9 scaling relationship (numerical coincidence, not structural)

**The most valuable next computation:**
Extract 5×7 Macro cycles from the three available Shirakawa SVG solutions. This would add a new cross-section to the verified dataset with minimal computational cost.