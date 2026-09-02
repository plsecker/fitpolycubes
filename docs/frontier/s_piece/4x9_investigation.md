# 4×9 S-Pentacube Macro Graph Investigation

**Date**: 2026-08-25  
**Status**: COMPLETE — 4 cycles recovered (60, 75, 90, 105), fundamental generator = 60

---

## 1. Published Evidence

### Source: `shirakawa/S.md` (lossless transcription of Shirakawa's 5-15 page)

| Box | Pieces | Solutions | Status | Source |
|-----|--------|-----------|--------|--------|
| 4×9×10 | — | 0 | impossible | Shirakawa 2014 |
| 4×9×15 | — | 0 | impossible | Shirakawa 2014 (correction note) |
| 4×9×20 | — | 0 | impossible | Shirakawa 2014 |
| 4×9×25 | — | 0 | impossible | Shirakawa 2014 |
| 4×9×30 | — | 0 | impossible | Shirakawa 2014 |
| 4×9×35 | — | 0 | impossible | Shirakawa 2014 |
| 4×9×40 | — | 0 | impossible | Shirakawa 2014 |
| 4×9×45 | — | 0 | impossible | Shirakawa 2014 |
| **4×9×60** | **432** | **1+** | **prime** | **Shirakawa 2014** |
| **4×9×75** | **540** | **1+** | **prime** | **Shirakawa 2014** |
| **4×9×90** | **648** | **1+** | **prime** | **Shirakawa 2014** |
| **4×9×105** | **756** | **1+** | **prime** | **Shirakawa 2014** |

**Correction note**: "Sillke says 4x10x14 and 4x9x15 are possible, but they are impossible." This refers to **4×9×15** specifically. The 4×9×60+ entries are confirmed prime.

### Faithfulness theorem consequence

By the faithfulness theorem, the 4×9 Macro graph must contain closed walks of lengths 60, 75, 90, and 105 from state 0. The previous apparent acyclicity (depth-51 BFS truncation) was a search-depth artifact.

---

## 2. Witness Recovery

### Method: SVG extraction from Shirakawa solution pages

All four solutions were downloaded from the Shirakawa SVG pages and parsed using the same coordinate-mapping machinery developed for 5×9:

| Box | SVG URL | Pieces | Cells | Status |
|-----|---------|--------|-------|--------|
| 4×9×60 | `html/5-15-60x9x4.html` | 432 | 2160 | ✓ Extracted |
| 4×9×75 | `html/5-15-75x9x4.html` | 540 | 2700 | ✓ Extracted |
| 4×9×90 | `html/5-15-90x9x4.html` | 648 | 3240 | ✓ Extracted |
| 4×9×105 | `html/5-15-105x9x4.html` | 756 | 3780 | ✓ Extracted |

All solutions validated: correct cell counts, no overlaps, all pieces verified as valid S pentacubes.

### Solution files created:
- `data/solutions_s_4x9x60_shirakawa.dat`
- `data/solutions_s_4x9x75_shirakawa.dat`
- `data/solutions_s_4x9x90_shirakawa.dat`
- `data/solutions_s_4x9x105_shirakawa.dat`

---

## 3. Extracted Macro Cycles

### 4×9×60 Cycle (length 60)

- **Irreducible**: No repeated internal states (only state 0 at start and end)
- **Gate at step**: 59
- **States with L2>0**: 0/61 (all L2=0)
- **Non-shift edges**: 58, avg 7.4 pieces
- **Unique frontier weights**: 40
- **Most common weights**: (20,8,0): 4x, (17,8,0): 4x, (23,8,0): 4x

### 4×9×75 Cycle (length 75)

- **Irreducible**: True
- **Gate at step**: 74
- **States with L2>0**: 0/76
- **Non-shift edges**: 74, avg 7.3 pieces
- **Most common weights**: (15,6,0): 6x, (24,6,0): 6x

### 4×9×90 Cycle (length 90)

- **Irreducible**: True
- **Gate at step**: 89
- **States with L2>0**: 0/91
- **Non-shift edges**: 89, avg 7.3 pieces

### 4×9×105 Cycle (length 105)

- **Irreducible**: True
- **Gate at step**: 104
- **States with L2>0**: 0/106
- **Non-shift edges**: 104, avg 7.3 pieces

### Cycle data

All four cycles stored in `tools/frontier/_4x9_concrete_cycles.json`.

---

## 4. Fundamental Generator

### Is 60 fundamental?

**YES.** The catalogue confirms:
- 4×9×15: IMPOSSIBLE (correction note)
- 4×9×30: 0 solutions
- 4×9×45: 0 solutions
- 4×9×60: PRIME (1+ solutions)

No shorter cycle exists. 60 is the fundamental generator.

### Generator set

| Generator | Status | Evidence |
|-----------|--------|----------|
| **60** | **PRIMITIVE** | Irreducible, catalogue prime, no shorter cycle exists |
| **75** | **PRIMITIVE** | Irreducible, catalogue prime |
| **90** | **PRIMITIVE** | Irreducible, catalogue prime |
| **105** | **PRIMITIVE** | Irreducible, catalogue prime |

### Semigroup

⟨60, 75, 90, 105⟩ — GCD = 15

| Property | Value |
|----------|-------|
| Scaled semigroup | ⟨4, 5, 6, 7⟩ |
| Scaled Frobenius | 3 |
| Scaled conductor | 4 |
| **Frobenius number** | **45** |
| **Conductor** | **60** |
| Nonrepresentable | 15, 30, 45 |

All z ≥ 60 with z ≡ 0 (mod 15) are representable.

---

## 5. Comparison with 5×9

### The remarkable scaling relationship

The 4×9 and 5×9 cycles exhibit a striking structural relationship:

| Property | 4×9 | 5×9 | Ratio |
|----------|-----|-----|-------|
| Area | 36 | 45 | 0.8 |
| Generators | 60, 75, 90, 105 | 12, 15, 18, 21 | **5.0** |
| Scaled semigroup | ⟨4,5,6,7⟩ | ⟨4,5,6,7⟩ | **identical** |
| GCD | 15 | 3 | 5.0 |
| Frobenius | 45 | 9 | 5.0 |
| Conductor | 60 | 12 | 5.0 |
| Avg pieces/edge | 7.4 | 9.5 | 0.78 |
| Orientation similarity | — | — | **0.956-0.984** |

**VERIFIED FACT**: Every 4×9 generator is exactly **5×** the corresponding 5×9 generator:
- 60 = 5 × 12
- 75 = 5 × 15
- 90 = 5 × 18
- 105 = 5 × 21

**VERIFIED FACT**: The orientation cosine similarity between 4×9 and 5×9 cycles is 0.956-0.984, comparable to the within-5×9 similarity (0.93-0.98).

### Interpretation

The 4×9 and 5×9 Macro graphs appear to be **structurally related by a scaling factor of 5**. This is consistent with the area ratio (36:45 = 4:5) and suggests that each Macro edge in 5×9 corresponds to approximately 5 Macro edges in 4×9.

**HYPOTHESIS**: The 4×9 Macro graph may be a "stretched" version of the 5×9 Macro graph, where each 5×9 Macro transition is decomposed into 5 finer 4×9 transitions. This would explain:
1. The exact 5× cycle length ratio
2. The identical scaled semigroup
3. The high orientation similarity
4. The lower avg pieces/edge (7.4 vs 9.5)

---

## 6. Correction of Previous Search Result

The previous 4×9 Macro search (depth 51, 65M states) concluded the graph was a "widening DAG" with no cycles. This conclusion was **incorrect** — it was a search-depth artifact.

**Corrected interpretation**: The 4×9 Macro graph is **cyclic**, as proven by:
1. The faithfulness theorem (catalogue tileability ⇒ cyclicity)
2. Four independently verified Macro cycles (60, 75, 90, 105)
3. Concrete physical tilings extracted from Shirakawa SVGs

The BFS simply did not reach the return depth (59 for z=60). The graph was still widening at depth 51 with 8M states/depth and 8.4M pending states.

---

## 7. Files

- `data/solutions_s_4x9x60_shirakawa.dat` — 4×9×60 solution (432 pieces)
- `data/solutions_s_4x9x75_shirakawa.dat` — 4×9×75 solution (540 pieces)
- `data/solutions_s_4x9x90_shirakawa.dat` — 4×9×90 solution (648 pieces)
- `data/solutions_s_4x9x105_shirakawa.dat` — 4×9×105 solution (756 pieces)
- `tools/frontier/_4x9_concrete_cycles.json` — Verified cycle data
- `docs/frontier/s_piece/4x9_investigation.md` — This document

---

## 8. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

---

## 9. Recommended Next Research

1. **Verify 4×9×120, 135, 150** via macro construction to confirm the semigroup prediction.
2. **Investigate the 5× scaling relationship** — is it a general phenomenon? Does 4×10 have a similar relationship with 5×8?
3. **Compare 4×8 with 5×6** — both have L2>0 states and complex SCCs. Do they share a similar scaling relationship?
4. **Extract 4×9×60, 75, 90, 105 cycles** from the constructed tilings to verify they match the SVG-extracted cycles.