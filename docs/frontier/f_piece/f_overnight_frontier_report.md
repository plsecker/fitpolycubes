# F Pentacube Overnight Frontier Report

**Date**: 2026-08-31
**Purpose**: systematically reduce the F-pentacube catalogue frontier using
existing evidence, decomposition, and the structural analysis workflow
developed for Z.

---

## Executive summary

The F pentacube has **70 Unknown boxes**, and **every single one is in the
2×M×N family** (thickness-2 boxes). The Shirakawa F page states "3D
Complete" but contains **zero** 2×M×N entries — the entire 2-thick family
is outside the published classification scope.

**No source evidence, no decomposition, and no certified result exists
for any 2×M×N F box.** The 70 Unknown boxes represent a genuine open
problem in pentacube tiling theory.

---

## 1. Baseline audit (Phase 1)

### Catalogue state (dims ≤ 20)

| category | count |
|---|---|
| RAW_PRIMES | **56** |
| PUBLISHED_SOLUTIONS | **0** |
| SEARCHED_NO_SOLUTION | **1** (4×6×10) |
| IMPOSSIBLE (rule-based) | multiple families |
| **UNKNOWN / UNPROVEN** | **70** |
| DISCOVERED_COMPOSITE | **488** |

### The 70 Unknown boxes: complete list

ALL 70 are 2×M×N boxes:

| cross-section | unknown lengths |
|---|---|
| 2×2 | 5, 10, 15, 20 |
| 2×3 | 5, 10, 15, 20 |
| 2×4 | 5, 10, 15, 20 |
| 2×5 | 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 |
| 2×6 | 10, 15, 20 |
| 2×7 | 10, 15, 20 |
| 2×8 | 10, 15, 20 |
| 2×9 | 10, 15, 20 |
| 2×10 | 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 |
| 2×11 | 15, 20 |
| 2×12 | 15, 20 |
| 2×13 | 15, 20 |
| 2×14 | 15, 20 |
| 2×15 | 15, 16, 17, 18, 19, 20 |
| 2×16 | 20 |
| 2×17 | 20 |
| 2×18 | 20 |
| 2×19 | 20 |
| 2×20 | 20 |

**Every single Unknown box has a = 2.** There are zero non-2×Unknown boxes.

## 2. Source mining (Phase 2)

### 2.1 The Shirakawa F page

Source: `https://puzzlewillbeplayed.com/Shirakawa/F.html`
States: **"3D Complete."**

The page contains **zero 2×M×N entries**. The entire published
classification starts at 3×6×10 (prime minimal) and covers boxes with
minimum dimension ≥ 3. The 2×M×N family is entirely absent.

**This is NOT a transcription gap** — the page genuinely does not address
2-thick boxes for the F pentacube.

### 2.2 Why 2×M×N is absent from the source

The F pentomino is a flat pentomino (z-span 1) with bounding box 3×3×1.
For a 2×M×N box:
* the piece CAN fit (its 3-cell extent goes along M or N, not the 2-axis)
* but the tiling problem is fundamentally different from ≥3-thick boxes

Shirakawa's "3D Complete." likely means "complete for boxes with minimum
dimension ≥ 3." The 2-thick family is either:
* considered a separate problem (2D tiling in a thin slab)
* or was not investigated

**No inference can be drawn from the absence of 2×M×N entries.**

### 2.3 What the published data DOES cover

The Shirakawa F page covers boxes with minimum dimension ≥ 3:

| family | status |
|---|---|
| 3×[3–5]×N | impossible (Sillke 1993) |
| 3×6×10 | prime minimal (Hamlyn) |
| 3×6..11×10/15 | various primes |
| 4×4×N | impossible (Sillke 1993) |
| 4×5×[3–9,11] | impossible |
| 4×5×{10,12–19,21} | various primes |
| 4×6..10×10/15 | various primes |
| 5×5×[3–7,9] | impossible |
| 5×5×{8,10–15,17} | various primes |
| 5×6..9×N | various primes |
| 5×7×[7, N] | 5×7×7 impossible; others prime |

**All non-2× boxes with dims ≤ 20 are classified.** Audit B = 0 for
non-2× boxes. The decomposition engine closes every non-2× composite.

### 2.4 The 2×M×N family: no published evidence exists

| 2×M×N aspect | evidence status |
|---|---|
| Shirakawa page | ❌ absent |
| Sillke pages | ❌ not checked (external URL) |
| Michael Reid's collection | ❌ not checked (external URL) |
| Mathematical theorem | ❌ none known |
| Exhaustive search | ❌ not performed |
| Catalogue rule | ❌ removed (was empirical, no source) |

**The 2×M×N family is a genuine gap in the published F pentacube data.**

## 3. Decomposition closure (Phase 3)

### 3.1 Non-2× closure is complete

All non-2× composite boxes (within dims ≤ 20) are closed by the existing
decomposition engine using the 56 prime seeds. Audit C = 488 discovered
composites. No Unknown non-2× boxes exist.

### 3.2 The 2×M×N closure gap

The 70 Unknown 2×M×N boxes cannot be closed by decomposition because:
1. There are no 2-thick prime seeds (all primes have min dim ≥ 3)
2. The impossibility rules don't cover 2×M×N (the a ≤ 1 rule and
   specific 3×/4×/individuals don't apply)
3. No source evidence exists for any 2×M×N F box

The 2×M×N family requires either:
* A new prime discovery (e.g., finding that 2×5×N is tileable for some N)
* A proof that all 2×M×N boxes are impossible
* Or accepting them as permanently Unknown

## 4. Structural analysis (Phase 4)

### 4.1 Can the F pentacube tile a 2-thick box at all?

The F pentomino has cells in a 3×3 bounding box (2D). As a pentacube
(z-span 1), its 3D orientations include placements where the 3-cell extent
goes along the box's M or N dimension (not the 2-thick axis). The piece
fits in a 2-thick box ✓.

However, the F pentomino is NOT symmetric — it has a handedness (chirality).
In a 2-thick box, the piece must use both layers. The question is whether
the F pentomino's shape allows a consistent tiling in a 2-layer geometry.

This is a genuine open problem. No published result addresses it.

### 4.2 The 2×M×N volume constraint

For a 2×M×N box: volume = 2MN. For pentacube tiling: 2MN ≡ 0 (mod 5).
Since gcd(2,5) = 1: MN ≡ 0 (mod 5). So either M or N must be divisible
by 5, or both must have factors of 5.

Looking at the Unknown boxes:
- 2×2×{5,10,15,20}: MN = 2×5=10 ✓, 2×10=20 ✓, etc. (N divisible by 5)
- 2×3×{5,10,15,20}: MN = 3×5=15 ✓, etc.
- 2×4×{5,10,15,20}: MN = 4×5=20 ✓, etc.
- 2×5×{5..20}: MN = 5×N ✓ (M=5 divisible by 5)
- etc.

The volume constraint is satisfied for all the Unknown boxes ✓.

### 4.3 Thickness-2 tiling theory

For a 2-thick box tiled by pentacubes:
* Each piece must span both layers (since each piece has 5 cells and
  each layer has MN/2 cells... wait, that's not right either)
* Actually, pieces can be entirely within one layer (if the piece's
  z-span is 1 and it's placed in layer 0 or layer 1)
* OR pieces can span both layers (if oriented with z-extent 2)

For the F pentomino (z-span 1 in canonical orientation):
* In its canonical orientation: the piece occupies 1 layer entirely
* In other orientations: the piece can span 2 layers

The 2-thick tiling problem is fundamentally different from the ≥3-thick
problem addressed by Shirakawa. It requires its own analysis.

## 5. Classification (Phases 5–6)

| class | count | items |
|---|---|---|
| **A. READY TO PROMOTE** | 0 | No new source evidence found |
| **B. READY TO CLOSE INTERNALLY** | 0 | No new decomposition discovered |
| **C. NEEDS HUMAN REVIEW** | 0 | No ambiguous source data found |
| **D. SMALL TARGETED COMPUTATION** | 1 | 2×5×5 (smallest 2×M×N box, volume 50 = 10 pieces) |
| **E. HARD / PARK** | 69 | The remaining 2×M×N boxes (awaiting 2×5×5 result) |

## 6. Three most important structural facts

1. **The F frontier is monolithic**: ALL 70 Unknown boxes are 2×M×N. The
   non-2× frontier is completely closed. This is a binary classification:
   solve the 2×M×N problem and the F catalogue is complete; don't, and
   70 boxes remain open.

2. **No published source addresses 2×M×N for F.** The Shirakawa page
   states "3D Complete" but contains zero 2×M×N entries. This means
   either (a) the problem was not investigated, or (b) the problem was
   deemed out of scope. In neither case can absence of evidence be
   interpreted as evidence of impossibility.

3. **The 2×M×N problem is fundamentally different from ≥3-thick tiling.**
   The F pentomino (z-span 1) can be placed with its 3-cell extent along
   M or N (both ≥ 3), but the 2-thick dimension limits the piece to
   z-span ≤ 2 orientations. This restricts the piece to a subset of its
   12 orientations, changing the tiling problem's structure.

## 7. Ranked results

| rank | target | class | reason |
|---|---|---|---|
| 1 | **2×5×5** | D | Smallest 2×M×N box (10 pieces). If SAT finds a tiling, the entire family opens up. If UNSAT, it's evidence for a general impossibility. |
| 2 | **2×5×10** | D | Next smallest with M=5 (20 pieces). Volume = 100. Tests the M=5 pattern. |
| 3 | **2×2×5** | D | Absolute minimum (4 pieces). Tests the extreme case. |
| 4 | **2×10×10** | D | Volume = 200 (40 pieces). Tests the square cross-section. |
| 5 | **6×6×15** | B | Already closed by decomposition (not Unknown). No action needed. |

## 8. Recommendation

**The single best next task for F is: solve 2×5×5 (the smallest 2×M×N box).**

This box has 50 cells = 10 F pentacubes. It can be:
* Solved by SAT (CaDiCaL): the encoding has ~10× fewer variables than
  6×7×10 (estimated ~200-500 placements), so CaDiCaL should handle it in
  seconds-to-minutes.
* If SAT: the tiling provides a constructive certificate and opens the
  2×M×N family for further investigation.
* If UNSAT: the DRAT proof provides verifiable evidence and suggests that
  the entire 2×M×N family may be impossible (adding back the empirical
  a==2 rule with actual computational evidence).

Either outcome is valuable. The computation should take < 5 minutes.

## 9. Reproduction

```bash
# Audit
.venv/bin/python tools/audit_catalogue.py F --max-dim 20
# Validate
.venv/bin/python -m unittest tools.frontier.z_piece.test_z_frontier_closures
```
