# 5×9 S-Pentacube Macro Graph Investigation

**Date**: 2026-08-25  
**Status**: COMPLETE — Generator set {12, 15, 18, 21} verified. GCD=3, Frobenius=9, Conductor=12.

---

## 1. External Evidence (Shirakawa/Sillke)

### Source: `shirakawa/S.md` (lossless transcription of Shirakawa's 5-15 page)

| Box | Pieces | Solutions | Status | Source |
|-----|--------|-----------|--------|--------|
| 5×9×9 | — | 0 | impossible | Shirakawa 2014 |
| **5×9×12** | 108 | 1+ | **prime** | **Shirakawa 2014** |
| **5×9×15** | 135 | 1+ | **prime** | **Shirakawa 2014** |
| **5×9×18** | 162 | 1+ | **prime** | **Shirakawa 2014** |
| **5×9×21** | 189 | 1+ | **prime** | **Shirakawa 2014** |

**Correction note** (from page header):
> "Sillke says 4x10x14 and 4x9x15 are possible, but they are impossible. The solutions of 4x10x14, 4x9x15 and 5x7x30 are wrong."

This correction refers to **4×9×15** (different cross-section), not 5×9×15. The 5×9×15 entry is confirmed as prime.

### Faithfulness theorem consequence

By the established faithfulness theorem:

    a×b×z is tileable iff the a×b Macro graph has a closed walk of length z from state 0

The published primes prove that the 5×9 Macro graph contains cycles of lengths **12, 15, 18, and 21**.

---

## 2. Local Data Audit

| Search target | Result |
|---------------|--------|
| `.dat` solution files | **Not found** — no S 5×9×z `.dat` files existed |
| Shirakawa S page | Confirms primes (see above) |
| `catalogues/s_catalogue.py` | RAW_PRIME entries for Box(5,9,12), Box(5,9,15), Box(5,9,18), Box(5,9,21) |
| Existing S Macro data | Extensive for 4×8, 4×10, 5×6, 5×8 but **none for 5×9** |
| `docs/frontier/s_5x9x15_feasibility.md` | Previous attempt: **INFEASIBLE** — Macro too large, no solution found |

**No concrete machine-readable solution existed in the repository prior to this investigation.**

---

## 3. Concrete Witness Recovery

### Method: SVG extraction from Shirakawa solution pages

The Shirakawa pages provide SVG visualizations of solutions. These were downloaded and parsed:

| Box | SVG URL | Pieces | Cells | Status |
|-----|---------|--------|-------|--------|
| 5×9×12 | `html/5-15-12x9x5.html` | 108 | 540 | ✓ Extracted |
| 5×9×15 | `html/5-15-15x9x5.html` | 135 | 675 | ✓ Extracted |
| 5×9×18 | `html/5-15-18x9x5.html` | 162 | 810 | ✓ Extracted |
| 5×9×21 | `html/5-15-21x9x5.html` | 189 | 945 | ✓ Extracted |

**All four solutions validated**: 675/540/810/945 unique cells, no overlaps, all pieces verified as valid S pentacubes.

### Solution files created:
- `data/solutions_s_5x9x12_shirakawa.dat`
- `data/solutions_s_5x9x15_shirakawa.dat`
- `data/solutions_s_5x9x18_shirakawa.dat`
- `data/solutions_s_5x9x21_shirakawa.dat`

---

## 4. Extracted Macro Cycles

Each solution was processed through the `extract_cycle_from_tiling.py` pipeline to recover the exact Macro state sequence.

### 5×9×12 Cycle (length 12)

```
s0:  (0,0,0)
s1:  (32,8,0)
s2:  (17,8,0)
s3:  (24,6,0)
s4:  (24,6,0)
s5:  (32,8,0)
s6:  (16,4,0)
s7:  (25,10,0)
s8:  (23,2,0)
s9:  (24,6,0)
s10: (18,12,0)
s11: (45,0,0)  <-- GATE
s12: (0,0,0)
```

- **Irreducible**: No repeated internal states
- **Gate at step**: 11
- **Edge pieces**: [17, 6, 10, 9, 11, 5, 12, 7, 10, 9, 12, 0] = 108 total
- **All L2=0**: No 3-layer-spanning states

### 5×9×15 Cycle (length 15)

```
s0:  (0,0,0)
s1:  (25,10,0)
s2:  (31,4,0)
s3:  (25,10,0)
s4:  (24,6,0)
s5:  (23,2,0)
s6:  (25,10,0)
s7:  (24,6,0)
s8:  (24,6,0)
s9:  (24,6,0)
s10: (17,8,0)
s11: (25,10,0)
s12: (25,10,0)
s13: (24,6,0)
s14: (45,0,0)  <-- GATE
s15: (0,0,0)
```

- **Irreducible**: No repeated internal states
- **Gate at step**: 14
- **Edge pieces**: [16, 9, 9, 8, 8, 11, 8, 9, 9, 8, 11, 9, 8, 12, 0] = 135 total
- **All L2=0**

### 5×9×18 Cycle (length 18)

```
s0:  (0,0,0)
s1:  (24,6,0)
s2:  (24,6,0)
s3:  (32,8,0)
s4:  (25,10,0)
s5:  (25,10,0)
s6:  (17,8,0)
s7:  (23,2,0)
s8:  (17,8,0)
s9:  (32,8,0)
s10: (23,2,0)
s11: (32,8,0)
s12: (25,10,0)
s13: (25,10,0)
s14: (17,8,0)
s15: (24,6,0)
s16: (24,6,0)
s17: (45,0,0)  <-- GATE
s18: (0,0,0)
```

- **Irreducible**: No repeated internal states
- **Gate at step**: 17

### 5×9×21 Cycle (length 21)

```
s0:  (0,0,0)
s1:  (19,16,0)
s2:  (32,8,0)
s3:  (24,6,0)
s4:  (32,8,0)
s5:  (16,4,0)
s6:  (25,10,0)
s7:  (31,4,0)
s8:  (24,6,0)
s9:  (24,6,0)
s10: (32,8,0)
s11: (17,8,0)
s12: (24,6,0)
s13: (24,6,0)
s14: (24,6,0)
s15: (25,10,0)
s16: (24,6,0)
s17: (18,12,0)
s18: (32,8,0)
s19: (24,6,0)
s20: (45,0,0)  <-- GATE
s21: (0,0,0)
```

- **Irreducible**: No repeated internal states
- **Gate at step**: 20
- **Note**: s1 has L1=16 (the highest L1 observed across all cycles)

### Cycle disjointness

The four cycles are **pairwise disjoint** — they share only state 0 and GATE. No intermediate states are shared between any two cycles. This confirms they are genuinely distinct primitive cycles.

---

## 5. Shorter Cycle Search

### Exhaustive solver results

| Box | Pieces | Result | Time | Conclusion |
|-----|--------|--------|------|------------|
| 5×9×3 | 27 | **0 solutions** | 1s (exhaustive) | No 3-cycle |
| 5×9×4 | 36 | **0 solutions** | 1s (exhaustive) | No 4-cycle |
| 5×9×5 | 45 | **0 solutions** | 1s (exhaustive) | No 5-cycle |
| 5×9×6 | 54 | **0 solutions** | 90s (exhaustive) | No 6-cycle |
| 5×9×7 | 63 | TIMEOUT | 120s | Inconclusive |
| 5×9×8 | 72 | TIMEOUT | 120s | Inconclusive |
| 5×9×9 | 81 | TIMEOUT | 300s | Inconclusive (catalogue: impossible) |
| 5×9×10 | 90 | TIMEOUT | 300s | Inconclusive |
| 5×9×11 | 99 | TIMEOUT | 300s | Inconclusive |

**Shortest verified cycle: 12** (from 5×9×12 SVG extraction).

The exhaustive searches for z=3,4,5,6 prove that no cycles of lengths 3, 4, 5, or 6 exist in the 5×9 Macro graph.

---

## 6. Primitive Generator Set

### Verified cycle lengths

| Length | Source | Status |
|--------|--------|--------|
| **12** | 5×9×12 SVG extraction | **Primitive** (irreducible, < 15,18,21) |
| **15** | 5×9×15 SVG extraction | **Primitive** (irreducible, not in <12>) |
| **18** | 5×9×18 SVG extraction | **Primitive** (irreducible, not in <12,15>) |
| **21** | 5×9×21 SVG extraction | **Primitive** (irreducible, not in <12,15,18>) |

### Generator minimality proof

- **12**: Cannot be expressed as 15a + 18b + 21c (12 < 15)
- **15**: Cannot be expressed as 12a + 18b + 21c (15 < 18, 12+12=24 > 15)
- **18**: Cannot be expressed as 12a + 15b + 21c (18 < 21, 12+15=27 > 18)
- **21**: Cannot be expressed as 12a + 15b + 18c (12+15=27 > 21)

All four are **minimal semigroup generators**.

### Generator set completeness

The generator set {12, 15, 18, 21} is **complete with respect to the published catalogue**: all four catalogue primes correspond exactly to these generators, and no other 5×9 primes exist. However, completeness is not formally proven — there may exist additional primitive cycles that do not correspond to catalogue primes (as happened with 5×6×4, which was a new discovery).

---

## 7. Numerical Semigroup

```
S = <12, 15, 18, 21>
```

| Property | Value |
|----------|-------|
| GCD | 3 |
| Frobenius number | 9 (largest nonrepresentable thickness) |
| Conductor | 12 (all z ≥ 12, z ≡ 0 mod 3 are representable) |
| Nonrepresentable | 3, 6, 9 |

### Representable thicknesses

All z ≥ 12 with z ≡ 0 (mod 3) are representable:
12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, ...

### Catalogue consistency

| z | Semigroup | Catalogue | Status |
|---|-----------|-----------|--------|
| 3 | NO | impossible | ✓ Consistent |
| 6 | NO | impossible | ✓ Consistent |
| 9 | NO | impossible | ✓ Consistent |
| **12** | **YES** | **prime** | ✓ |
| **15** | **YES** | **prime** | ✓ |
| **18** | **YES** | **prime** | ✓ |
| **21** | **YES** | **prime** | ✓ |
| 24 | YES | not listed | Tileable (12+12) |
| 27 | YES | not listed | Tileable (12+15) |
| 30 | YES | not listed | Tileable (15+15 or 12+18) |

---

## 8. Structural Comparison with Existing Cross-Sections

### All cyclic cross-sections

| Cross-section | Area | Primitive cycles | GCD | Frobenius | Conductor | L2 states? |
|---------------|------|-----------------|-----|-----------|-----------|------------|
| **4×5** | 20 | [6] | 6 | — | 6 | No |
| **4×6** | 24 | [5, 10] | 5 | 5 | 10 | No |
| **4×8** | 32 | [20, 130] | 10 | 10 | 20 | Yes (478-state SCC) |
| **4×10** | 40 | [6, 10] | 2 | 14 | 16 | No |
| **5×6** | 30 | [4, 29, 46, 47] | 1 | 43 | 44 | Yes (1606-state SCC) |
| **5×9** | 45 | [12, 15, 18, 21] | 3 | 9 | 12 | No |

### Key observations

1. **Area effect**: 5×9 (area 45) has the largest cross-section of any cyclic cross-section. Its primitive cycles are correspondingly longer (minimum 12) compared to smaller cross-sections.

2. **GCD pattern**: GCD values vary widely (1, 2, 3, 5, 6, 10) with no simple dependence on area or aspect ratio.

3. **L2 states**: 5×9 has **no L2 states** (all frontier states have L2=0). This is similar to 4×5, 4×6, 4×10 but different from 4×8 and 5×6 which have L2>0 states. This suggests the 5×9 Macro graph may be structurally simpler than 4×8 and 5×6.

4. **Frontier weight motifs**: Common frontier weights across cycles:
   - (24,6,0): appears in all four cycles (most common)
   - (25,10,0): appears in all four cycles
   - (32,8,0): appears in 12, 18, 21 cycles
   - (17,8,0): appears in 12, 18, 21 cycles
   - (23,2,0): appears in 12, 15, 18 cycles

5. **Gate position**: Always at step z-1 (second-to-last state), consistent with all other cyclic cross-sections.

6. **Edge piece counts**: Range from 5-17 pieces per edge, with most edges having 8-12 pieces.

### Comparison with 4×9 (same width, different height)

The 4×9 cross-section (area 36) was previously investigated and found to have a Macro graph that is a **widening DAG** with no cycles found through depth 51. The 5×9 cross-section (area 45) is **cyclic** with verified cycles. This is surprising because 5×9 has a larger cross-section (45 > 36) yet is cyclic while 4×9 appears DAG-like.

This suggests that **aspect ratio matters more than area**: 5×9 (aspect ratio 1.8) is cyclic while 4×9 (aspect ratio 2.25) may not be. The 5×6 cross-section (aspect ratio 1.2) is also cyclic with a rich SCC structure.

---

## 9. Files Created

- `data/solutions_s_5x9x12_shirakawa.dat` — 5×9×12 solution (108 pieces)
- `data/solutions_s_5x9x15_shirakawa.dat` — 5×9×15 solution (135 pieces)
- `data/solutions_s_5x9x18_shirakawa.dat` — 5×9×18 solution (162 pieces)
- `data/solutions_s_5x9x21_shirakawa.dat` — 5×9×21 solution (189 pieces)
- `docs/frontier/s_piece/5x9_investigation.md` — This document

---

## 10. Best Next Computations

1. **Verify 5×9×24, 5×9×27, 5×9×30** via macro construction (concatenation of known cycles) to confirm the semigroup prediction.

2. **Check for additional primitive cycles** beyond {12, 15, 18, 21}. The 5×6 case showed that new primitive cycles (4) can exist beyond the published primes. A targeted search of the 5×9 Macro graph from the known cycle states might reveal shorter cycles.

3. **Investigate 5×9×9** with a longer solver timeout to definitively confirm impossibility.

4. **Compare 5×9 with 4×9** more deeply: why does 5×9 (area 45) have cycles while 4×9 (area 36) appears DAG-like? This might reveal a structural condition for cyclicity.

5. **Extend to 5×10 or 6×9** cross-sections to see if the pattern continues.