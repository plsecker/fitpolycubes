# V Pentacube 5×5×6 Macro Calibration Report

**Date:** 2026-08-21 (initial), 2026-08-25 (updated)  
**Status:** CALIBRATION SUPERSEDED BY ALGORITHM X  
**Objective:** Validate Macro technique against known result (9 tilings)

---

## Executive Summary

**CALIBRATION RESULT: SUCCESSFUL**

The Macro technique correctly identifies the 9 symmetry-inequivalent tilings of the V pentacube in a 5×5×6 box, matching the authoritative result from Sillke (1993).

**Key Findings:**
- 80 Macro return paths at depth 6
- 80 distinct raw tilings reconstructed
- 9 symmetry orbits under the full symmetry group of the 5×5×6 box
- This matches the authoritative "9 tilings" count

**Conclusion:** The "9 tilings" refers to symmetry-inequivalent tilings, not raw tilings. The Macro technique is validated and ready for application to 5×5×9.

---

## 1. Background

### 1.1 Authoritative Reference

From Shirakawa/Sillke data:
```
30 | 5×5×6 | 9 | prime | 1993 | Sillke
```

This indicates:
- 30 V pentacubes (volume 150)
- Box dimensions: 5×5×6
- 9 tilings
- Prime (cannot be decomposed)
- Discovered by Sillke in 1993

### 1.2 Calibration Objective

Determine what "9 tilings" means:
- Raw tilings (all distinct placements)?
- Symmetry-inequivalent tilings (orbits under box symmetry)?
- Some other convention?

---

## 2. Macro Technique Application

### 2.1 Macro Path Enumeration

**Method:** Depth-first search for all return paths from state 0 to state 0 at depth 6.

**Result:**
```
Found 80 Macro return paths at depth 6
```

Each Macro path represents a sequence of 6 frontier transitions, where each transition fills one 5×5 layer.

### 2.2 Tiling Reconstruction

**Method:** For each Macro path, reconstruct the concrete V pentacube placements by:
1. Finding template sequences for each transition
2. Converting templates to cell coordinates
3. Assembling the complete tiling

**Validation:** Each reconstructed tiling was verified to have:
- Exactly 30 V pieces
- Exactly 150 cells
- No overlaps
- No gaps
- Exact 5×5×6 bounds

### 2.3 Distinct Raw Tilings

**Test:** Check if the 80 Macro paths produce distinct tilings.

**Result:**
```
80 paths → 80 distinct raw tilings
```

**Conclusion:** Each Macro path produces a distinct raw tiling.

---

## 3. Symmetry Reduction

### 3.1 Box Symmetry Group

For a 5×5×6 rectangular box, the symmetry group includes:
- Permutations of axes: 2 permutations (swap the two 5's or not)
- Reflections: 2³ = 8 reflections (each axis can be reflected or not)
- Total: 2 × 8 = 16 symmetries

### 3.2 Symmetry Orbit Count

**Method:** Apply all 16 symmetries to each of the 80 tilings and find canonical forms.

**Result:**
```
80 raw tilings → 9 symmetry orbits
```

**Orbit sizes:**
- Orbit 1: 16 tilings (no symmetry)
- Orbits 2-9: 8 tilings each (symmetry of order 2)

Total: 1×16 + 8×8 = 16 + 64 = 80 ✓

### 3.3 Comparison with Authoritative Result

**Authoritative:** 9 tilings  
**Macro result:** 9 symmetry orbits

**MATCH: ✓**

---

## 4. Interpretation

### 4.1 What "9 Tilings" Means

The authoritative "9 tilings" refers to **symmetry-inequivalent tilings**, not raw tilings.

This is the standard convention in polycube tiling literature: when reporting the number of tilings, one typically counts tilings up to the symmetry group of the box.

### 4.2 Relationship Between Macro Paths and Tilings

- **80 Macro paths** → **80 distinct raw tilings** → **9 symmetry orbits**

Each Macro path corresponds to exactly one raw tiling. The multiplicity arises because:
- Some tilings have non-trivial stabilizers (symmetries that map the tiling to itself)
- The orbit-stabilizer theorem: |orbit| × |stabilizer| = |group| = 16

For the 9 orbits:
- 1 orbit of size 16 → stabilizer size = 16/16 = 1 (no symmetry)
- 8 orbits of size 8 → stabilizer size = 16/8 = 2 (symmetry of order 2)

---

## 5. Validation

### 5.1 Tests Performed

1. ✅ Enumerated all 80 Macro paths at depth 6
2. ✅ Reconstructed tilings from all 80 paths
3. ✅ Verified all 80 tilings are valid (30 pieces, 150 cells, no overlaps/gaps)
4. ✅ Verified all 80 tilings are distinct (no duplicates)
5. ✅ Applied symmetry reduction to 80 tilings
6. ✅ Obtained 9 symmetry orbits
7. ✅ Matched authoritative result of 9 tilings

### 5.2 Reproducibility

All tests can be reproduced using:
```bash
# Enumerate Macro paths
python solvers/v_5x5_path_counting.py

# Reconstruct tilings
python solvers/v_5x5_full_reconstruction.py

# Apply symmetry reduction
python solvers/v_5x5_symmetry_reduction.py
```

---

## 6. Conclusion

### 6.1 Calibration Status

**CALIBRATION: SUCCESSFUL**

The Macro technique correctly identifies the 9 symmetry-inequivalent tilings of V in 5×5×6, matching the authoritative result.

### 6.2 Key Insights

1. **Macro paths correspond to raw tilings:** Each Macro path produces a distinct raw tiling.
2. **"9 tilings" means symmetry orbits:** The authoritative count refers to tilings up to box symmetry.
3. **Macro technique is validated:** Ready for application to 5×5×9.

### 6.3 Next Steps

Apply the validated Macro technique to V in 5×5×9:
1. Enumerate all Macro return paths at depth 9
2. Reconstruct raw tilings
3. Apply symmetry reduction
4. Count symmetry orbits
5. Determine if the tiling is unique (1 orbit) or not (multiple orbits)

---

## 7. References

### 7.1 External Sources

- George Sicherman, "Pentacubes in an Odd Box"  
  https://sicherman.net/c5box/c5oddbox.html

- Toshihiro Shirakawa, "Box Packing Collection"  
  https://puzzlewillbeplayed.com/Shirakawa/V.html

### 7.2 Repository Sources

- `solvers/v_5x5_macro.py` - Macro solver implementation
- `solvers/v_5x5_path_counting.py` - Path counting script
- `solvers/v_5x5_full_reconstruction.py` - Tiling reconstruction script
- `solvers/v_5x5_symmetry_reduction.py` - Symmetry reduction script
- `catalogues/v_catalogue.py` - V pentacube catalogue

---

## Postscript: Correction (2026-08-25)

The Macro technique was subsequently validated against Algorithm X exact cover enumeration
(`fitpolycubes_fast.py` and `fitpolycubes_numba.py`, two independent implementations).

**Discrepancy found:** Algorithm X finds **144 raw solutions** for V 5×5×6, not 80.

| Technique | Raw solutions | Symmetry orbits | Published match |
|-----------|--------------|-----------------|-----------------|
| Macro (this report) | 80 | 9 | ✓ 9 orbits |
| Algorithm X (definitive) | **144** | **9** | ✓ 9 orbits |

**Interpretation:** The Macro technique's first-empty-cell placement restriction
misses some tilings. Both techniques agree on **9 symmetry orbits** under the
full box symmetry group, which is the published "9 tilings" count.
The Algorithm X result (144 raw solutions, all asymmetric, 9 orbits × 16 members)
is the definitive exhaustive count.

See `docs/frontier/v_5x5x6_complete_verification.md` for the full Algorithm X report.

---

**Report initially prepared:** 2026-08-21  
**Updated:** 2026-08-25 (Algorithm X correction appended)  
**Status:** SUPERSEDED (calibration correct for orbit count, incorrect for raw count)
