# V 5×5×9 Complete Enumeration — Symmetry Analysis Report

## Overview

This report documents the exhaustive enumeration of all V-pentacube tilings of the
5×5×9 box, the V4 symmetry classification, and reconciliation with George Sicherman's
prediction.

## Enumeration

| Metric | Value |
|--------|-------|
| Solver | `fitpolycubes_fast.py` (Algorithm X exact cover) |
| Box | 5 × 5 × 9 |
| Piece | V pentacube (12 unique orientations) |
| Placements | 1,164 |
| Total raw solutions | **1,120** |
| Search time | 2,325 s (~39 min) |
| Search status | **Exhaustive** — solver terminated normally after exploring entire search tree |
| Validation | 1,120/1,120 valid (45 pieces, 225 cells, no overlap, no gaps, in bounds) |
| Duplicates | 0 (every raw solution is distinct) |

## V4 Classification (George's Convention)

**V4 group:** {I, R_x, R_y, R_z} — the Klein four-group of 180° rotations.

- R_x: (x, y, z) → (x, 4−y, 8−z)
- R_y: (x, y, z) → (4−x, y, 8−z)
- R_z: (x, y, z) → (4−x, 4−y, z)  (long-axis rotation)

| Metric | Value |
|--------|-------|
| V4 equivalence classes | **280** |
| Asymmetric classes (\|O\|=4, \|S\|=1) | **280** |
| Symmetric classes (\|S\|>1) | **0** |
| Classes with R_z symmetry | **0** |
| Classes with R_x symmetry | **0** |
| Classes with R_y symmetry | **0** |
| V4 closure | **Verified** — every V4 transform of every solution is in the solution set |
| Orbit-stabilizer | **All 280 classes pass** (4 × 1 = 4) |

**Distribution:**
- 280 classes × 4 members = 1,120 raw tilings

## Reconciliation with George Sicherman's Prediction

George predicted that a complete 22-solution set would decompose as:
> 5 asymmetric classes × 4 + 1 symmetric class × 2 = 22

**Status: The prediction does NOT apply to the complete enumeration.**

The original 22-record snapshot was an early, incomplete solver output. The complete
enumeration contains **1,120 raw solutions** in **280 V4 classes**, all asymmetric.

George's known R_z-symmetric solution was expected to be in the 22-record snapshot.
The complete enumeration contains **no R_z-symmetric tilings** — every tiling is
fully asymmetric under V4.

## Secondary Analysis: Full Box Symmetry

For comparison, the same 1,120 solutions were classified under larger symmetry groups:

### G8 — Proper Rotations (order 8)
- **140 classes**, each with orbit size 8
- 140 × 8 = 1,120 ✓

### G16 — Full Box Symmetry including reflections (order 16)
- **70 classes**, each with orbit size 16
- 70 × 16 = 1,120 ✓

The orbit-stabilizer theorem holds perfectly at every level:
- V4: 280 × 4 = 1,120
- G8: 140 × 8 = 1,120
- G16: 70 × 16 = 1,120

## Comparison with Previous Results

| Snapshot | Solutions | V4 Classes | Notes |
|----------|-----------|------------|-------|
| Original early snapshot (lost — overwritten by later runs) | 22 | 18 | Early incomplete solver output |
| `archive/solutions_v_5x5x9_partial_282.dat` | 282 | — | Partial run, killed mid-search |
| **`solutions_v_5x5x9_complete.dat`** | **1,120** | **280** | **Exhaustive search completed** |

## Key Findings

1. **The V 5×5×9 box has exactly 1,120 V-pentacube tilings.**
2. **Under V4, all 1,120 tilings fall into 280 equivalence classes, each of size 4.**
3. **No tiling has any V4 symmetry** — every stabilizer is trivial {I}.
4. **George's 5+1 prediction** was based on the incomplete 22-record snapshot and does
   not describe the complete enumeration.
5. **The complete solution set is closed under V4** — every V4 transform of every
   solution is present in the set.
6. **Under the full 16-element box symmetry group**, the 1,120 solutions collapse to
   70 equivalence classes.

## Reproduction

To reproduce the enumeration:

```bash
python3 solvers/fitpolycubes_fast.py V --box 5 5 9 --no-symmetry
```

Output: `data/solutions_v_5x5x9_complete.dat`

To reproduce the analysis:

```bash
python3 solvers/v_5x5x9_complete_analysis.py
```

## Files

| File | Description |
|------|-------------|
| `data/solutions_v_5x5x9_complete.dat` | Complete enumeration (1,120 solutions) |
| `data/archive/solutions_v_5x5x9_partial_282.dat` | Previous partial run (282 solutions) |
| `solvers/v_5x5x9_complete_analysis.py` | Validation, dedup, V4/G8/G16 classification |
| `solvers/v_5x5x9_exhaustive_search.py` | Resumable macro-DFS solver (alternative approach) |
| `solvers/fitpolycubes_fast.py` | Exact cover solver used for final enumeration |