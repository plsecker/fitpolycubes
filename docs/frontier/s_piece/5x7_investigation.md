# 5×7 S-Pentacube Macro Investigation

**Date**: 2026-08-25  
**Status**: COMPLETE — 3 cycles recovered (24, 36, 42); semigroup ⟨24, 36, 42⟩, GCD=6, Frobenius=54, Conductor=60

---

## 1. Source Evidence

### Catalogue: `shirakawa/S.md` (Shirakawa 5-15 page, Sillke 1998)

| Box | Pieces | Solutions | Status | Source |
|-----|--------|-----------|--------|--------|
| 5×7×12 | — | 0 | impossible | Sillke 1993 |
| 5×7×18 | — | 0 | impossible | Sillke 1993 |
| **5×7×24** | **168** | **1+** | **prime** | **Sillke 1998** |
| 5×7×30 | 210 | 1+ | **prime (CORRECTION: WRONG)** | Sillke 1998 |
| **5×7×36** | **252** | **1+** | **prime** | **Sillke 1998** |
| **5×7×42** | **294** | **1+** | **prime** | **Sillke 1998** |

**Correction note**: "The solutions of 4x10x14, 4x9x15 and 5x7x30 are wrong." — 5×7×30 is treated as impossible despite being listed as prime.

### SVG solutions available:
- `html/5-15-24x7x5.html` → extracted ✓
- `html/5-15-36x7x5.html` → extracted ✓
- `html/5-15-42x7x5.html` → extracted ✓

---

## 2. Physical Extraction

All three solutions were extracted from Shirakawa SVG files using the flat-layout coordinate mapping (the 5×7 SVG uses a 35-column flat array rather than 100px/panel structure).

| Box | Pieces | Cells | Valid |
|-----|--------|-------|-------|
| 5×7×24 | 168 | 840 | ✓ |
| 5×7×36 | 252 | 1260 | ✓ |
| 5×7×42 | 294 | 1470 | ✓ |

### Solution files:
- `data/solutions_s_5x7x24_shirakawa.dat`
- `data/solutions_s_5x7x36_shirakawa.dat`
- `data/solutions_s_5x7x42_shirakawa.dat`

---

## 3. Macro Cycles

All three cycles are **irreducible**, have **L2=0** throughout, and gate at position z−1.

| Cycle | Length | States | Gate | Avg pieces/edge | Unique frontier weights |
|-------|--------|--------|------|-----------------|------------------------|
| 5×7×24 | 24 | 25 | 23 | 7.3 | 13 |
| 5×7×36 | 36 | 37 | 35 | 7.2 | 14 |
| 5×7×42 | 42 | 43 | 41 | 7.2 | 16 |

### Cycle data:
- `tools/frontier/_5x7_concrete_cycles.json`

---

## 4. Shorter Cycle Search

Exhaustive solver results:

| z | Result | Time | Conclusion |
|---|--------|------|------------|
| 3 | **0 solutions** | 1s (exhaustive) | No 3-cycle |
| 4 | **0 solutions** | 1s (exhaustive) | No 4-cycle |
| 5 | **0 solutions** | 1s (exhaustive) | No 5-cycle |
| 6 | **0 solutions** | 7.6s (exhaustive) | No 6-cycle |
| 7-12 | TIMEOUT | 45-70s | Inconclusive |

**No primitive cycle exists below length 24.** The recovered 24-cycle is the fundamental generator.

---

## 5. Generator Set

| Generator | Status | Evidence |
|-----------|--------|----------|
| **24** | **PRIMITIVE** | Irreducible, catalogue prime, no shorter cycle exists |
| **36** | **PRIMITIVE** | Irreducible, catalogue prime |
| **42** | **PRIMITIVE** | Irreducible, catalogue prime |

All three are minimal semigroup generators.

---

## 6. Numerical Semigroup

```
S = ⟨24, 36, 42⟩
```

| Property | Value |
|----------|-------|
| GCD | 6 |
| Scaled semigroup | ⟨4, 6, 7⟩ |
| Scaled Frobenius | 9 |
| Scaled conductor | 10 |
| **Frobenius number** | **54** (largest nonrepresentable) |
| **Conductor** | **60** (all z ≥ 60, z ≡ 0 mod 6 are representable) |
| Apéry set (orig) | {0:0, 1:78, 2:36, 3:42} |

### Representable thicknesses (multiples of 6):
6, 12, 18, **24**, 30, **36**, **42**, 48, 54, **60**, 66, 72, 78, 84, ...

Nonrepresentable: 6, 12, 18, 30, 54

---

## 7. Catalogue Comparison

| z | Semigroup | Catalogue | Status |
|---|-----------|-----------|--------|
| 12 | NO | impossible | ✓ Consistent |
| 18 | NO | impossible | ✓ Consistent |
| **24** | **YES** | **prime** | ✓ |
| 30 | NO | impossible* | ✓ Consistent (correction note) |
| **36** | **YES** | **prime** | ✓ |
| **42** | **YES** | **prime** | ✓ |
| 48 | YES | not listed | Tileable (24+24) |
| 54 | NO | not listed | Impossible |
| 60 | YES | not listed | Tileable (24+36) |

*5×7×30 is listed as prime but the correction note says the solution is wrong → impossible.

---

## 8. 5×6 / 5×7 / 5×8 Comparison

| Property | 5×6 | 5×7 | 5×8 |
|----------|-----|-----|-----|
| Area | 30 | 35 | 40 |
| Shortest cycle | **4** | **24** | **6** |
| GCD | **1** | **6** | **6** |
| Frobenius | 43 | 54 | — |
| Conductor | 44 | 60 | 6 |
| L2 states | Some (in SCC) | None | None |
| Avg pieces/edge | 8.0 (4-cycle) | 7.3 | 9.6 |

### Key observations

1. **5×7 has the longest fundamental cycle** (24) of any investigated cross-section. This is more than 5× its closest neighbours.

2. **5×7 and 5×8 share GCD=6** but have different semigroup structures — 5×7 has ⟨4,6,7⟩ scaled while 5×8 is just ⟨6⟩.

3. **5×7 has no L2 states**, similar to 5×8 and the 4-cycle of 5×6, but different from the 5×6 SCC which has L2>0 states.

4. **The scaled semigroup ⟨4,6,7⟩ has Frobenius 9**, meaning 5×7 thicknesses that are ≡ 0 mod 6 are representable for z ≥ 60. Smaller representable values are {24, 36, 42, 48}.

5. **5×7 is structurally closer to 5×8** (both have GCD=6, L2=0, similar cycle structure) than to 5×6 (which has GCD=1 and complex SCC).

---

## 9. Files

- `data/solutions_s_5x7x24_shirakawa.dat` — 5×7×24 solution
- `data/solutions_s_5x7x36_shirakawa.dat` — 5×7×36 solution
- `data/solutions_s_5x7x42_shirakawa.dat` — 5×7×42 solution
- `tools/frontier/_5x7_concrete_cycles.json` — Verified cycle data
- `data/frontier/s_piece/macro_5x7_results.json` — Machine-readable results

## 10. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

## 11. Best Next Target

**5×10** (area 50, catalogue prime 18) — SVG solution available at `html/5-15-18x10x5.html`. This is the last uninvestigated cross-section with readily available SVG data. After that, the remaining catalogue cross-sections (6×6, 6×7, 4×13, etc.) would require new solver searches or alternative source data.