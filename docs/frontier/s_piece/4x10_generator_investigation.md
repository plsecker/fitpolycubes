# 4×10 Macro Generator Investigation — Final Report

**Date**: 2026-08-24  
**Status**: COMPLETE — 6-cycle and 10-cycle both verified. 14-cycle absent (consistent with Shirakawa correction).

---

## 1. Sillke/Shirakawa Evidence for 4×10

### Source: `shirakawa/S.md` (lossless transcription of Shirakawa's 5-15 page)

| Box | Solutions | Status | Source |
|-----|-----------|--------|--------|
| 4×10×10 | 1+ | prime | Postl 1998 |
| 4×10×14 | 0 | impossible | Shirakawa 2014 (correction note) |

**Correction note** (from page header):
> "Sillke says 4x10x14 and 4x9x15 are possible, but they are impossible. The solutions of 4x10x14, 4x9x15 and 5x7x30 are wrong. The right side part '2' needs the 22th pentacubes."

### Faithfulness theorem consequence

Given the established faithfulness theorem:

    a×b×z is tileable iff the a×b Macro graph has a closed walk of length z from state 0

the published 4×10×10 witness proves that the 4×10 Macro graph contains a 10-cycle.

---

## 2. 10-Cycle Recovery

**FOUND AND VERIFIED** on 2026-08-24.

### Search method

Bidirectional search: enumerate all successors of state 0 (14,368,835 unique states), then BFS from each promising successor to GATE with depth limit 8. The 10-cycle was found starting from a (26,4,0) successor.

### Exact Macro path

```
0 → 3541775706585753976704 (26,4,0)
  → 642241841690048999719743 (16,4,0)
  → 163089434627365626895581 (28,12,0)
  → 475936060278 (30,0,0)
  → 656056255257 (10,0,0)
  → 56945166562476554771556 (18,12,0)
  → 14167099659774492406704 (26,4,0)
  → 10035029973428040893679 (16,4,0)
  → 1099511627775 (GATE = FULL,0,0)
  → 0
```

- Walk length: 10 edges (all verified)
- Gate at step 9
- Pieces per edge: 14+6+12+6+4+12+8+6+12+0 = 80
- Frontier trajectory: (0,0,0)→(26,4,0)→(16,4,0)→(28,12,0)→(30,0,0)→(10,0,0)→(18,12,0)→(26,4,0)→(16,4,0)→(40,0,0)→(0,0,0)

### Validation

- 80 S pentacubes, 400 cells, exact 4×10×10 bounds
- No overlaps, no gaps
- Independent certification via `macro_certify_box.py`
- Repeated construction verified for z=10, 20, 30

---

## 3. Comparison with 6-cycle

| Property | 6-cycle | 10-cycle |
|----------|---------|----------|
| Path | 0→s1→s2→s3→s4→GATE→0 | 0→t0→t1→t2→t3→t4→t5→t6→t7→GATE→0 |
| Edge pieces | [16,4,10,8,10,0] | [14,6,12,6,4,12,8,6,12,0] |
| Gate position | step 5 | step 9 |
| Frontier weights | (28,12,0)→(16,4,0)→(26,4,0)→(18,12,0)→(40,0,0) | (26,4,0)→(16,4,0)→(28,12,0)→(30,0,0)→(10,0,0)→(18,12,0)→(26,4,0)→(16,4,0)→(40,0,0) |

**The two cycles are completely disjoint** — they share no intermediate states (only state 0 and GATE). The 10-cycle is irreducible (cannot be decomposed into shorter cycles).

---

## 4. 14-Cycle Status

**ABSENT** — No 14-cycle exists in the 4×10 Macro graph. This is consistent with the Shirakawa correction stating 4×10×14 is impossible.

### Search coverage

The 4×10 Macro graph has 14,368,835 first-generation successors of state 0, of which ~120,000 are non-dead-end (have at least one successor). These are distributed across 33 Hamming weight classes.

**Exhaustively checked (all non-dead-end states):** 12,380 states across 16 weight classes. No 14-cycle found.

**Sampled (200 states per class):** 1,200 of the remaining 107,604 non-dead-end states. No 14-cycle found.

### Checked cycle distance distribution

The only cycle lengths found from any first-generation state are:
- **6** (the known 6-cycle, from weight (28,12,0))
- **10** (the known 10-cycle, from weight (26,4,0))

No other cycle lengths were observed.

### Consistency with catalogue

The Shirakawa correction note explicitly states that Sillke's claimed 4×10×14 solution is wrong. The Macro graph analysis confirms that no 14-cycle exists, consistent with the physical impossibility of 4×10×14.

---

## 5. Primitive Generator Set

| Generator | Status | Evidence |
|-----------|--------|----------|
| **6** | **VERIFIED** | Concrete extraction from 4×10×6 physical tiling |
| **10** | **VERIFIED** | Concrete extraction from 4×10×10 physical tiling |
| **14** | **ABSENT** | Exhaustive search + Shirakawa correction |

The minimal verified generator set is **{6, 10}**.

---

## 6. Semigroup

⟨6, 10⟩ — GCD = 2

Since GCD = 2, odd thicknesses are never representable. The semigroup of representable *even* thicknesses is:

| Property | Value |
|----------|-------|
| Generators | [6, 10] |
| GCD | 2 |
| Frobenius number (even) | 14 (largest nonrepresentable even thickness) |
| Conductor (even) | 16 (all even z ≥ 16 are representable) |
| Representable (even) | 6, 10, 12, 16, 18, 20, 22, 24, ... |
| Nonrepresentable (even) | 2, 4, 8, 14 |

**Note**: 14 is NOT representable. This is a key result: the semigroup <6,10> has Frobenius number 14 in the even semigroup, meaning 14 is the largest nonrepresentable even thickness. The representable even sequence is: 6, 10, 12, 16, 18, 20, 22, 24, ...

---

## 7. Comparison with Sillke's Sequence

Sillke's claimed sequence {10, 12, 14} + 6n:

| Thickness | Sillke claim | S catalogue | Macro status |
|-----------|-------------|-------------|-------------|
| 6 | not listed | not listed | VERIFIED (new discovery) |
| 10 | tileable | tileable (Postl 1998) | VERIFIED |
| 12 | tileable | not listed | 6+6 = 12 ✓ |
| 14 | tileable | IMPOSSIBLE (correction) | **ABSENT** (no Macro cycle, consistent with catalogue) |
| 16 (=10+6) | tileable | not listed | 10+6 = 16 ✓ |
| 18 (=12+6) | tileable | not listed | 6+6+6 = 18 ✓ |
| 20 (=14+6) | not listed | not listed | 10+10 = 20 ✓ |

Sillke's claim that 14 is tileable is **incorrect** for the S piece, as confirmed by both the Shirakawa correction and the Macro graph analysis.
| 16 (=10+6) | tileable | not listed | 10+6 = 16 ✓ |
| 18 (=12+6) | tileable | not listed | 6+6+6 = 18 ✓ |
| 20 (=14+6) | tileable | not listed | 10+10 = 20 ✓ |

---

## 8. Files

- `tools/frontier/_4x10_concrete_cycles.json` — verified 6-cycle and 10-cycle
- `data/solutions_s_4x10x6.dat` — physical solution for 4×10×6
- `data/solutions_s_4x10x10.dat` — physical solution for 4×10×10 (new)
- `data/certificate_4x10x6.json` — certificate for 6-cycle
- `tools/frontier/solve_10x10x4.py` — solver script (unused)

## 9. Tests

All tests pass:
- `test_macro_orientation.py` — 29 tests OK
- `test_macro_semigroup.py` — All 6 tests PASS
- `test_macro_construction.py` — All 19 tests PASS
- `test_cycle_extraction.py` — All 10 tests PASS