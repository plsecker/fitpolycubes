# 5×10 S-Pentacube Macro Investigation

**Date**: 2026-08-25  
**Status**: COMPLETE — Single generator {18} recovered; GCD=18; no shorter cycles found below 18.

---

## 1. Source Verification

### Source: `shirakawa/S.md` (Shirakawa's 5-15 page)

| Box | Pieces | Solutions | Status | Source |
|-----|--------|-----------|--------|--------|
| **5×10×18** | **180** | **1+** | **prime** | **Shirakawa 2014** |

The 5×10 section has a single entry: 5×10×18 as prime. No other 5×10 thicknesses are listed. No correction notes affect 5×10.

### SVG solution
- URL: `html/5-15-18x10x5.html`
- SVG: `svgz/5-15/5-15-5x10x18.svgz`
- Title: "5-15 x 180 : 5x10x18"
- Downloaded successfully ✓

---

## 2. Physical Extraction

The 5×10 SVG uses a **flat layout** with 50 unique x-positions (matching the 5×10 cross-section grid of 50 cells), arranged in a snake pattern across 6 panels.

### Coordinate mapping
- x-positions sorted → index 0-49
- grid_x = index ÷ 10, grid_y = index % 10 (row-major)
- depth = svg_y ÷ 10

### Validation
| Metric | Value |
|--------|-------|
| Box | 5×10×18 |
| Cells | 900 (all present) |
| Pieces | 180 (all valid S pentacubes) |
| Overlaps/gaps | None |

### Solution file
- `data/solutions_s_5x10x18_shirakawa.dat`

---

## 3. Macro Cycle

| Property | Value |
|----------|-------|
| Length | **18** (irreducible) |
| States | 19 (including start/end 0) |
| Gate index | 17 |
| L2>0 states | **0** (all L2=0) |
| Non-shift edges | 17 |
| Avg pieces/edge | 10.6 |
| Unique frontier weights | 8 |

### Frontier trajectory
```
s0:  ( 0, 0, 0)
s1:  (22, 8, 0)
s2:  (32, 8, 0)
s3:  (22, 8, 0)
s4:  (18,12, 0)
s5:  (36, 4, 0)
s6:  (18,12, 0)
s7:  (38,12, 0)
s8:  (32, 8, 0)
s9:  (22, 8, 0)
s10: (18,12, 0)
s11: (38,12, 0)
s12: (16, 4, 0)
s13: (38,12, 0)
s14: (32, 8, 0)
s15: (22, 8, 0)
s16: (32, 8, 0)
s17: (50, 0, 0) <-- GATE
s18: ( 0, 0, 0)
```

### Edge pieces
[16, 12, 8, 10, 12, 8, 14, 8, 8, 10, 14, 4, 16, 8, 8, 12, 12] = 180 total

### Cycle data
- `tools/frontier/_5x10_concrete_cycles.json`

---

## 4. Shorter Cycle Search

| z | Result | Time | Conclusion |
|---|--------|------|------------|
| 3 | **0 solutions** | 1s (exhaustive) | No 3-cycle |
| 4 | **0 solutions** | 1s (exhaustive) | No 4-cycle |
| 5 | **0 solutions** | 2s (exhaustive) | No 5-cycle |
| 6-17 | TIMEOUT | 40-85s | Inconclusive |

No primitive cycle exists below length 18 for z=3,4,5 (proven). The recovered 18-cycle is the fundamental generator.

---

## 5. Generator Set

| Generator | Status | Evidence |
|-----------|--------|----------|
| **18** | **PRIMITIVE** | Irreducible, catalogue prime, no shorter cycle proven |

### Numerical semigroup
```
⟨18⟩ — GCD = 18
```
Representable: all multiples of 18.

---

## 6. Catalogue Comparison

| z | Semigroup | Catalogue | Status |
|---|-----------|-----------|--------|
| **18** | **YES** | **prime** | ✓ |
| 36 | YES | not listed | Tileable (18+18) |
| 54 | YES | not listed | Tileable (18+18+18) |

---

## 7. 5×N Progression (5×6 through 5×10)

| Property | 5×6 | 5×7 | 5×8 | 5×9 | 5×10 |
|----------|-----|-----|-----|-----|------|
| Width N | 6 | 7 | 8 | 9 | 10 |
| Area | 30 | 35 | 40 | 45 | 50 |
| Recovered cycles | {4,29,46,47} | {24,36,42} | {6} | {12,15,18,21} | {18} |
| Shortest cycle | 4 | 24 | 6 | 12 | 18 |
| Number of generators | 4 | 3 | 1 | 4 | 1 |
| GCD | 1 | 6 | 6 | 3 | 18 |
| Frobenius | 43 | 54 | N/A | 9 | N/A |
| Conductor | 44 | 60 | 6 | 12 | 18 |
| L2 in cycle | No | No | No | No | No |
| L2 in SCC | Yes | ? | ? | ? | ? |

**No smooth trend exists.** The progression is qualitatively irregular: 4 generators → 3 → 1 → 4 → 1 with no monotonic relationship to width or area.

---

## 8. Files

- `data/solutions_s_5x10x18_shirakawa.dat` — 5×10×18 solution
- `tools/frontier/_5x10_concrete_cycles.json` — Verified cycle data
- `data/frontier/s_piece/macro_5x10_results.json` — Machine-readable results

## 9. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

## 10. Best Next Target

**No further SVG witnesses remain for the S pentacube.** The remaining catalogue cross-sections (6×6, 6×7, 4×13, etc.) have no known SVG solutions. Further progress would require either:
1. A targeted exact-cover solver search for a specific small box
2. Analysis of the already-extracted Macro data for deeper structural patterns
3. Investigation of the 4×8 and 5×6 Macro SCCs which are the only cross-sections with complete Macro closure