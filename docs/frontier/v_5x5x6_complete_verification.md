# V 5×5×6 Exhaustive Enumeration — Complete Verification Report

**Date:** 2026-08-25  
**Status:** RESOLVED  
**Standard:** Matches V 5×5×9 exhaustive verification workflow

---

## 1. Overview

This report documents the exhaustive enumeration of all V-pentacube tilings of the
5×5×6 box, matching the gold-standard methodology established by the V 5×5×9
project: Algorithm X exact cover with independent cross-validation, full symmetry
analysis, and certificate production.

### 1.1 Catalogue Context

V 5×5×6 is listed as a **RAW_PRIME** in the V catalogue (`catalogues/v_catalogue.py`, line 18).
The published claim is **9 tilings** (Sillke 1993). This is recorded in the
Shirakawa transcription (`shirakawa/V.md`) and in the prior macro calibration
report (`docs/frontier/v_5x5x6_macro_calibration.md`).

## 2. Exhaustive Enumeration

### 2.1 Primary Search

| Metric | Value |
|--------|-------|
| Solver | `fitpolycubes_fast.py` (Algorithm X exact cover, Python) |
| Box | 5 × 5 × 6 |
| Piece | V pentacube (12 unique orientations) |
| Placements | 696 |
| Total raw solutions | **144** |
| Search time | 20.9 s (Python), 1.6 s (Numba-accelerated) |
| Search status | **Exhaustive** — both solvers terminated normally after exploring the entire search tree |
| Validation | 144/144 valid (30 pieces, 150 cells, no overlap, no gaps, in bounds) |
| Duplicates | 0 (every raw solution is distinct) |

### 2.2 Independent Cross-Validation

| Solver | Implementation | Solutions | Time | Match |
|--------|---------------|-----------|------|-------|
| `fitpolycubes_fast.py` | Pure Python Algorithm X | 144 | 20.9 s | — |
| `fitpolycubes_numba.py` | Numba-accelerated Algorithm X | 144 | 1.6 s | **100% identical** |

Two independent Algorithm X implementations, using different search backends,
agree on **exactly the same set of 144 solutions**.

### 2.3 Comparison with Macro Technique

The prior macro technique (`v_5x5_macro.py` + related calibration scripts) reported
**80 Macro return paths at depth 6**, which were interpreted as 80 raw tilings.
The Algorithm X enumeration finds **144 raw solutions** — a factor of 1.8× more.

The discrepancy arises because the Macro technique uses a first-empty-cell placement
order that restricts the search; some tilings require a different placement sequence
that is not captured by this order. Algorithm X exact cover has no such restriction.

**Macro technique does not produce complete enumeration for this box.**

## 3. Symmetry Classification

### 3.1 Full Box Symmetry Group (|G| = 16)

For a 5×5×6 box:
- **Axis permutations**: 2 (the two equal 5-dimensions can swap)
- **Axis reflections**: 8 (each dimension can reflect independently)
- **Total**: 16 elements

| Metric | Value |
|--------|-------|
| Symmetry orbits | **9** |
| Asymmetric orbits (|S|=1, |O|=16) | **9** |
| Symmetric orbits (|S|>1) | **0** |
| Orbit-stabilizer | **All 9 orbits pass** (16 × 1 = 16) |

**Distribution:**
- 9 orbits × 16 members = 144 raw tilings ✓

### 3.2 V4 Classification (matching V 5×5×9 convention)

V4 group = {I, R_x, R_y, R_z} — the Klein four-group.

| Metric | Value |
|--------|-------|
| V4 equivalence classes | **36** |
| Asymmetric classes (|O|=4, |S|=1) | **36** |
| Symmetric classes (|S|>1) | **0** |
| V4 closure | **Verified** — every V4 transform of every solution is in the set |
| Orbit-stabilizer | **All 36 classes pass** (4 × 1 = 4) |

### 3.3 Comparison with Published Claim

| Count | Claim | Interpretation | Agreement |
|-------|-------|---------------|-----------|
| 9 | Sillke 1993 | Symmetry orbits under full box symmetry | ✓ Confirmed |
| 144 | — | Raw physical tilings (Algorithm X enumeration) | New result |

The published "9 tilings" refers to **9 symmetry orbits** under the full box symmetry
group of order 16. Every orbit is asymmetric (stabilizer = {I}).

## 4. Comparison with V 5×5×9

| Metric | V 5×5×6 | V 5×5×9 | Ratio |
|--------|----------|----------|-------|
| Box volume | 150 cells | 225 cells | 1.5× |
| Tiles | 30 | 45 | 1.5× |
| Placements | 696 | 1,164 | 1.7× |
| Raw solutions | **144** | **1,120** | 7.8× |
| V4 classes | 36 | 280 | 7.8× |
| Full sym. orbits (|G|=16) | 9 | 70 (G16) | 7.8× |
| Search time (Python) | 20.9 s | 2,325 s | 111× |
| Search time (Numba) | 1.6 s | ~180 s (est.) | 112× |
| Symmetric tilings | **0** | **0** | Same |
| Stabilizers | All trivial | All trivial | Same |

**Key findings:**
1. Both boxes have **zero symmetric tilings** — every stabilizer is trivial.
2. The solution count scales faster than linearly with box volume (7.8× for 1.5× volume).
3. The V4 orbit-stabilizer structure is identical in character (all trivial stabilizers).
4. Search complexity scales more steeply than solution count (111× time for 7.8× solutions).

## 5. Independent Certificate

The certificate file `data/v_5x5x6_certificate.json` contains:
- All 144 solutions in canonical form with SHA-256 checksums
- Full symmetry classification (9 box orbits, 36 V4 classes)
- Search metadata

**Verification tool:** `solvers/v_5x5x6_certificate_validator.py`

The validator performs 5 independent checks without re-running the solver:
1. Every solution is valid (piece counts, cell counts, overlaps, gaps, bounds)
2. Every solution is unique (no duplicate canonical forms)
3. Total count matches the claim
4. Orbit-stabilizer theorem holds for all symmetry classes
5. Checksums are intact

**Result:** ALL CHECKS PASSED ✓ (verified 2026-08-25)

## 6. Solver Configuration for Reproducibility

```bash
# Primary search (Python Algorithm X):
python solvers/fitpolycubes_fast.py V --box 5 5 6

# Independent validation (Numba-accelerated):
python solvers/fitpolycubes_numba.py V --box 5 5 6

# Analysis and certificate:
python solvers/v_5x5x6_complete_analysis_v2.py
python solvers/v_5x5x6_certificate.py
python solvers/v_5x5x6_certificate_validator.py
```

## 7. Files Changed / Created

| File | Action | Description |
|------|--------|-------------|
| `data/solutions_fast_v_5x5x6.dat` | Updated | 144 solutions from Python solver |
| `data/solutions_numba_v_5x5x6.dat` | Created | 144 solutions from Numba solver |
| `data/v_5x5x6_certificate.json` | Created | Independent certificate |
| `data/v_5x5x6_complete_solutions.json` | Created | Compact solution data |
| `data/v_5x5x6_analysis_results.json` | Created | Analysis summary |
| `solvers/v_5x5x6_complete_analysis_v2.py` | Created | Comprehensive analysis (Phase 2-4) |
| `solvers/v_5x5x6_certificate.py` | Created | Certificate writer |
| `solvers/v_5x5x6_certificate_validator.py` | Created | Independent certificate validator |
| `docs/frontier/v_5x5x6_complete_verification.md` | Created | This report |

## 8. Remaining Uncertainty

None. The box is **fully resolved** to the V 5×5×9 standard:
- Exhaustive search with two independent Algorithm X implementations
- 100% solution agreement between implementations
- Complete symmetry classification at V4 and full-box levels
- Orbit-stabilizer theorem verified at every level
- Certificate produced and validated
- Published claim ("9 tilings") interpreted and confirmed as 9 symmetry orbits
- Discrepancy with prior macro technique explained and documented

---

**Report prepared by:** OpenWork automated analysis  
**Date:** 2026-08-25  
**Status:** FINAL — V 5×5×6 is RESOLVED