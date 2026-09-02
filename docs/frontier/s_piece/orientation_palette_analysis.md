# S-Pentacube Orientation Palette Analysis

**Date**: 2026-08-25  
**Status**: COMPLETE — The near-universal orientation similarity is explained by sample-size effects and family structure, not by a deep Macro invariant.

---

## 1. Orientation Feature Table

The S pentacube has **12 unique orientations** under 3D rotation. They partition into **3 natural families of 4 orientations each**:

| Family | Layer occupancy | z-span | xy-projection | Orientations | Description |
|--------|----------------|--------|---------------|-------------|-------------|
| **F1** | (4,1,0) | 2 | 4 | O2, O3, O4, O11 | 4 cells in L0, 1 in L1 |
| **F2** | (1,4,0) | 2 | 4 | O1, O6, O7, O9 | 1 cell in L0, 4 in L1 |
| **F3** | (2,1,2) | 3 | 3 | O0, O5, O8, O10 | 2 cells in L0, 1 in L1, 2 in L2 |

The families are determined by the S-piece geometry:
- F1 and F2 are symmetric under layer reversal (L0↔L1 swap)
- F3 is the only family that spans 3 layers

No mirror pairs exist among the 12 orientations (all are genuinely distinct under rotation).

---

## 2. Cross-Cycle Frequency Analysis

### 2.1 Family proportions

| Cycle | F1% | F2% | F3% | F1=F2? |
|-------|-----|-----|-----|--------|
| 4×10×6 | 33.3 | 33.3 | 33.3 | ✓ exact |
| 5×8×6 | 33.3 | 33.3 | 33.3 | ✓ exact |
| 4×9×60 | 31.9 | 31.9 | 36.1 | ✓ exact |
| 4×9×75 | 30.6 | 30.6 | 38.9 | ✓ exact |
| 4×9×90 | 30.2 | 30.2 | 39.5 | ✓ exact |
| 4×9×105 | 30.6 | 30.6 | 38.9 | ✓ exact |
| 5×9×12 | 36.1 | 31.5 | 32.4 | ✗ diff=5 |
| 5×9×15 | 32.6 | 32.6 | 34.8 | ✓ exact |
| 5×9×18 | 32.1 | 32.1 | 35.8 | ✓ exact |
| 5×9×21 | 29.6 | 32.3 | 38.1 | ✗ diff=5 |
| 4×10×10 | 37.5 | 37.5 | 25.0 | ✓ exact |
| 5×6×4 | 41.7 | 41.7 | 16.7 | ✓ exact |

### 2.2 Cosine similarity matrix (12-orientation level)

| Comparison | Avg cosine | Range |
|-----------|-----------|-------|
| Within 4×9 | 0.9897 | 0.9796-0.9979 |
| Within 5×9 | 0.9541 | 0.9259-0.9790 |
| 4×9 vs 5×9 | 0.9710 | 0.9563-0.9835 |
| 4×10 vs 5×8 | 0.8571 | 0.8571 |
| All between cross-sections | 0.9246 | 0.8298-0.9835 |

### 2.3 Family-level cosine similarity

| Comparison | Avg cosine |
|-----------|-----------|
| Within 4×9 | 0.9990 |
| Within 5×9 | 0.9962 |
| 4×9 vs 5×9 | 0.9961 |
| 4×10 vs 4×9 | 0.9772 |
| 4×10 vs 5×9 | 0.9865 |

At the family level, similarity is extremely high (0.977-0.999). This is because the F1:F2:F3 ratio is primarily determined by the cross-section geometry and the Macro edge constraint.

---

## 3. Null Model Results

### 3.1 Pure random assignment

For each cycle, we computed the expected cosine similarity between the observed frequency vector and a random uniform assignment:

| Cycle | Pieces | Random avg cosine | Random std |
|-------|--------|------------------|------------|
| 5×6×4 | 24 | 0.7717 | 0.0803 |
| 4×10×6 | 48 | 0.8372 | 0.0579 |
| 5×8×6 | 48 | 0.8372 | 0.0579 |
| 4×10×10 | 80 | 0.9093 | 0.0344 |
| 5×9×12 | 108 | 0.9264 | 0.0276 |
| 5×9×15 | 135 | 0.9391 | 0.0235 |
| 5×9×18 | 162 | 0.9456 | 0.0205 |
| 5×9×21 | 189 | 0.9492 | 0.0189 |
| 4×9×60 | 432 | 0.9856 | 0.0059 |
| 4×9×105 | 756 | 0.9761 | 0.0073 |

**Key finding**: For large cycles (432+ pieces), pure random assignment already gives cosine similarity 0.976-0.986. The observed between-cycle similarity of 0.83-0.99 is **not significantly different** from what random assignment would produce.

### 3.2 Family-constrained random assignment

When fixing the F1:F2:F3 proportions and randomizing within families, the expected similarity is slightly higher but still within the observed range.

### 3.3 Sample size effect on "all 12 orientations"

| Pieces | P(missing at least 1 orientation) |
|--------|----------------------------------|
| 24 | 1.49 (expected) |
| 48 | 0.18 |
| 60 | 0.06 |
| 108 | 0.001 |
| 432 | ~0.000 |

**Key finding**: With 48+ pieces, the probability of missing any orientation is < 0.2. The observation that "all 12 orientations are used in every cycle" is a **consequence of sample size**, not a structural invariant.

---

## 4. Exact Invariants

### 4.1 F1=F2 symmetry (APPROXIMATE, not exact)

F1 and F2 counts are equal in 10 out of 12 cycles. The exceptions are:
- 5×9×12: F1=39, F2=34 (diff=5)
- 5×9×21: F1=56, F2=61 (diff=5)

This is a **strong statistical observation** but not an exact invariant. The near-equality arises because F1 and F2 are symmetric under layer reversal (L0↔L1), and the Macro edge constraint treats them symmetrically on average.

### 4.2 Total pieces per cycle = area × length / 5

**EXACT COMPUTATIONAL FACT**: This is a volumetric constraint, not a Macro invariant.

### 4.3 Gate always at (AREA, 0, 0)

**THEOREM**: A consequence of the Macro model definition.

---

## 5. Family-Level Compression

The 12 orientations compress into 3 families of 4 each:

```
F1 (4,1,0): O2, O3, O4, O11  — 4 cells in L0, 1 in L1
F2 (1,4,0): O1, O6, O7, O9   — 1 cell in L0, 4 in L1  
F3 (2,1,2): O0, O5, O8, O10  — 2 cells in L0, 1 in L1, 2 in L2
```

At the family level, cross-cycle cosine similarity is 0.977-0.999, significantly higher than at the 12-orientation level (0.83-0.99). This confirms that the family-level distribution is the primary conserved quantity, while individual orientation choices within each family are approximately uniform.

---

## 6. Within vs Between Cross-Section Comparison

| Comparison | 12-orientation level | Family level |
|-----------|---------------------|-------------|
| Within 4×9 | 0.9897 | 0.9990 |
| Within 5×9 | 0.9541 | 0.9962 |
| 4×9 vs 5×9 | 0.9710 | 0.9961 |
| 4×10 vs 4×9 | 0.9282 | 0.9772 |

Within-cross-section similarity is higher than between-cross-section at the 12-orientation level, confirming that cross-section geometry influences the distribution. At the family level, the difference largely disappears.

---

## 7. Conclusion Classification

### REFUTED HYPOTHESES
1. **"All 12 orientations are always used" is a structural fact.** REFUTED: It is a sample-size effect.
2. **The orientation similarity indicates a deep Macro invariant.** REFUTED: Random assignment produces similar values.
3. **F1=F2 is an exact invariant.** REFUTED: Two cycles have diff=5.

### VERIFIED FACTS
1. **The 12 orientations partition into 3 families of 4** based on layer occupancy.
2. **F1 and F2 are symmetric under layer reversal.**
3. **The family-level distribution is the primary conserved quantity.**
4. **Within-family orientation choices are approximately uniform.**

### STRONG OBSERVATIONS
1. **F1=F2 in 10 of 12 cycles** — a strong statistical tendency, not an invariant.
2. **Family-level cross-cycle similarity (0.977-0.999) is higher than 12-orientation level (0.83-0.99).**
3. **The F1:F2:F3 ratio is cross-section-dependent**, determined by the Macro edge constraints.

### EXPLANATION OF THE OBSERVED PHENOMENON
The near-universal orientation similarity (0.83-0.99) is explained by three factors:

1. **Sample size effect (dominant)**: With 48+ pieces per cycle, even random assignment gives cosine similarity 0.77-0.99. The observed range is not significantly different from random.

2. **Family structure (secondary)**: The 3 families of 4 orientations each compress the 12-dimensional frequency vector to 3 dimensions. At the family level, similarity is 0.977-0.999.

3. **Cross-section geometry (tertiary)**: The F1:F2:F3 ratio varies with cross-section, but within each family, orientations are approximately uniformly distributed.

---

## 8. Data

- `data/frontier/s_piece/orientation_feature_table.json` — Orientation feature table
- `data/frontier/s_piece/orientation_palette_analysis.json` — Full analysis data

## 9. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

## 10. Recommended Next Research Question

**Is there a structural explanation for the F1=F2 near-equality?**

The fact that F1 and F2 counts are equal in 10 of 12 cycles (and differ by only 5 in the other 2) suggests a genuine constraint, not just a statistical tendency. This could be explained by:

1. A parity or mod-2 invariant in the Macro transition system.
2. A conservation law relating the L0 and L1 cell counts across a complete cycle.
3. A symmetry in the template set that forces equal numbers of (4,1,0) and (1,4,0) placements.

Investigating this would require analyzing the Macro template structure, not just the cycle statistics.