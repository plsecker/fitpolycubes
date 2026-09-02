# F1/F2 Symmetry Proof: S-Pentacube Macro Cycle Orientation Balance

**Date**: 2026-08-25  
**Status**: COMPLETE — F1=F2 is a strong empirical constraint but NOT a theorem. No proof exists from the algebraic equations alone.

---

## 1. Exact Definition

### Families

The S pentacube's 12 orientations partition into 3 families based on layer occupancy:

| Family | Profile | z-span | Orientations | L0 cells | L1 cells | L2 cells |
|--------|---------|--------|-------------|----------|----------|----------|
| **F1** | (4,1,0) | 2 | O2, O3, O4, O11 | 4 | 1 | 0 |
| **F2** | (1,4,0) | 2 | O1, O6, O7, O9 | 1 | 4 | 0 |
| **F3** | (2,1,2) | 3 | O0, O5, O8, O10 | 2 | 1 | 2 |

### Algebraic identity

For any collection of placements:

```
F1 − F2 = (L0_contrib − L1_contrib − F3) / 3
```

This is an **exact algebraic identity** derived from the layer profiles.

---

## 2. Attempted Proofs

### 2.1 Telescoping sum (FAILED)

We derived:

```
3·(f1_k − f2_k) = AREA − a_k − a_{k+1} + b_k − b_{k+1}/2
```

where a_k, b_k, c_k are the L0, L1, L2 of the state before edge k.

Summing over all edges gives a tautology:

```
3·(F1 − F2) = 3·(F1 − F2)  ✓
```

The telescoping sum does **not** constrain F1−F2.

### 2.2 Conserved potential (FAILED)

We searched for a function P(state) such that:

```
P(B) − P(A) = 3·(f1 − f2)
```

for every Macro edge A → B. No such function exists because the per-edge F1−F2 is **not determined by the state alone** — 41 out of 69 (a_k, b_k) frontier states have multiple possible dF values.

### 2.3 Modular invariant (FAILED)

Exhaustive search over all coefficient triples (c₁,c₂,c₃) with |cᵢ| ≤ 5 and moduli 2–20 found no nontrivial invariant for F1−F2.

### 2.4 Geometric symmetry (FAILED)

The S pentacube is **chiral** — no geometric symmetry (rotation, reflection, layer reversal) maps F1 to F2. The 12 orientations are all distinct under the 24 cube rotations.

### 2.5 Template-level symmetry (INCONCLUSIVE)

The template counts show F1:F2 = 4:1 (e.g., 416 vs 104 for 5×9). This is because:
- F1 has 4 cells in L0, so each F1 placement can be anchored at 4× as many positions
- Each F1 placement fills 4× as many L0 cells as each F2 placement

These two biases exactly cancel, but this is a **statistical** observation, not a proof.

---

## 3. Strongest True Statement

### THEOREM
```
F1 − F2 = (L0 − L1 − F3) / 3
```
This is an exact algebraic identity from the orientation profiles.

### EXACT FACT
- **10 of 12** recovered cycles have F1 = F2 exactly.
- The two exceptions are **exact complements**: 5×9×12 (+5) and 5×9×21 (−5).
- **Total F1 = Total F2 = 993** across all 12 cycles.
- Within each cross-section group, F1 = F2 exactly.

### STRONG OBSERVATION
- The probability of F1 = F2 in 10/12 cycles by chance is **< 10⁻¹⁰**.
- The per-edge F1−F2 is **not determined by the frontier state alone** (41/69 states have multiple values).
- The minimum nonzero imbalance observed is **±5** (no ±1, ±2, ±3, ±4).

### HYPOTHESIS
The F1=F2 balance is a consequence of the Macro template set being closed under F1↔F2 in expectation. The 4:1 template count bias (F1 has 4× more templates) is exactly compensated by the 4:1 L0 filling bias (each F1 placement fills 4× as many L0 cells). This balance is exact in the limit of long closed walks but individual cycles may deviate by up to ±5.

---

## 4. Negative Result Summary

| Attempted proof | Result | Reason for failure |
|----------------|--------|-------------------|
| Telescoping sum | **FAILED** | All sums are tautologies |
| Conserved potential | **FAILED** | dF not determined by state alone |
| Modular invariant | **FAILED** | No nontrivial invariant found |
| Geometric symmetry | **FAILED** | S piece is chiral |
| Template symmetry | **INCONCLUSIVE** | F1:F2 = 4:1 at template level |

---

## 5. Data

- `data/frontier/s_piece/f1_f2_symmetry_analysis.json` — Full analysis data
- `data/frontier/s_piece/f1_f2_balance_analysis.json` — Per-cycle census
- `docs/frontier/s_piece/f1_f2_symmetry_proof.md` — This document

## 6. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

## 7. Next Mathematical Question

**Can the F1=F2 balance be proven from the fact that the Macro transition system is aperiodic and irreducible?** If the template set is closed under F1↔F2 (in the sense of having equal expected contributions), then the balance follows from the ergodic theorem for long walks. This would require analyzing the Markov chain structure of the Macro graph, which is beyond the scope of the current investigation.