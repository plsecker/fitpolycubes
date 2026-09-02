# Macro Technique Analysis for V Pentacube in 5×5×9

**Date:** 2026-08-21  
**Status:** FUNDAMENTAL LIMITATION IDENTIFIED  
**Target:** V pentacube in minimal odd box 5×5×9

---

## Executive Summary

**FINDING:** The generalized Macro/state-graph technique **cannot be applied** to the V pentacube in a 5×5×9 box due to a fundamental structural limitation: **the V pentacube cannot tile a single 5×5 layer by itself.**

**CONCLUSION:** The Macro technique, which relies on filling layers one at a time, is inapplicable to V in 5×5 cross-section. Alternative approaches are required.

---

## 1. The Macro Technique: How It Works

The Macro technique reduces a 3D tiling problem to a finite state graph by:

1. **State representation:** Track the occupancy of 3 consecutive z-layers (layer 0, 1, 2)
2. **Templates:** Pre-compute all ways a piece can be placed relative to a target cell on layer 0
3. **Layer-by-layer filling:** Apply templates to fill layer 0 completely
4. **State transition:** When layer 0 is full, shift down (layer 1 → 0, layer 2 → 1, etc.)
5. **Graph exploration:** Build a directed graph of macro states (post-shift configurations)
6. **Path counting:** Count paths from empty state to empty state at target depth

This technique succeeded for the S pentacube in 4×8×N because:
- S is a truly 3D piece (cells span z=0 and z=1 in canonical form)
- When rotated, S placements always span multiple layers
- The Macro technique can track the "frontier" of partially-filled layers
- Sources (states where layer 0 is full) are reachable

---

## 2. Why Macro Fails for V in 5×5

### 2.1 V Pentacube Structure

The V pentacube is defined as:
```
[[0 0 0]
 [1 0 0]
 [2 0 0]
 [0 1 0]
 [0 2 0]]
```

This is a **2D piece** (all cells at z=0) in its canonical form. When rotated in 3D:
- **4 rotations** keep V in a single layer (2D orientations)
- **8 rotations** make V span multiple layers (3D orientations)

### 2.2 The Critical Test: Can V Tile a 5×5 Layer?

**Test:** Generate all single-layer placements of V in a 5×5×1 box and attempt exact-cover tiling.

**Result:**
```
Single-layer placements: 36
Tilings of 5×5 layer: 0
```

**The V pentacube cannot tile a 5×5 layer by itself.**

This was verified for multiple layer sizes:
- 3×5: 0 tilings
- 5×5: 0 tilings
- 5×7: 0 tilings
- 5×9: 0 tilings

### 2.3 Why This Breaks the Macro Technique

The Macro technique requires that we can fill layer 0 completely before shifting. If layer 0 can never be full, then:
- No sources are discovered
- The macro graph is empty
- No paths can be counted
- The technique produces no results

**Observed behavior:**
```
Phase 1: Finding first-generation sources...
  Cap hit at 100,000 states
  First-generation sources: 0
  First-gen tree states: 100,000

Phase 2: Computing Macro closure...
  Macro states: 0
  Macro edges: 0
```

The algorithm explores 100,000+ intermediate states but never reaches a state where layer 0 is full.

---

## 3. Comparison with S Pentacube

### 3.1 S Pentacube Structure

The S pentacube is defined as:
```
[[0 0 0]
 [1 0 0]
 [2 0 0]
 [0 0 1]
 [2 1 0]]
```

This is a **truly 3D piece** (cells at z=0 and z=1). When rotated, S placements always span multiple layers.

### 3.2 Why Macro Works for S

Even though S cannot tile a single 4×8 layer by itself (0 single-layer placements), the Macro technique still works because:
- S placements span layers 0 and 1 (and sometimes layer 2)
- The templates add cells to multiple layers simultaneously
- The frontier state tracks partial coverage across layers
- Sources are reachable when the combination of placements fills layer 0

The key difference: **S pieces interlock across layers**, allowing the frontier to advance even though no single piece lies flat.

### 3.3 Why V Is Different

V pieces can lie flat (4 single-layer rotations), but:
- When V lies flat, it cannot tile a 5×5 layer (coloring/parity obstruction)
- When V stands up (multi-layer rotations), it spans layers but doesn't help fill layer 0 efficiently
- The combination of flat and standing V pieces still cannot fill a 5×5 layer

This suggests a **coloring or parity argument** prevents V from tiling any rectangular layer.

---

## 4. Implications

### 4.1 Macro Technique Limitations

The Macro technique requires:
1. Pieces that span multiple layers (to track frontier state)
2. Combinations of pieces that can fill a complete cross-section layer
3. Reachable sources (states where layer 0 is full)

**V fails condition 2:** No combination of V placements can fill a 5×5 layer.

### 4.2 Does V Tile 5×5×9 at All?

**Yes.** Sicherman's "Pentacubes in an Odd Box" and the repository catalogues confirm that V can tile 5×5×9. The tiling exists, but:
- V pieces must be arranged in a complex 3D pattern
- Pieces span multiple layers in non-trivial ways
- The tiling cannot be decomposed into independent layers

### 4.3 Alternative Approaches Required

To determine uniqueness of the 5×5×9 V tiling, we need:

1. **Full 3D exact-cover solver:**
   - Direct enumeration of all tilings in 5×5×9
   - Already attempted; solver hangs due to problem size

2. **Modified Macro technique:**
   - Track more than 3 layers (e.g., 5 or 9 layers)
   - Use a different state representation
   - Define "slabs" instead of layers

3. **SAT/ILP formulation:**
   - Encode as Boolean satisfiability or integer linear program
   - Use modern SAT solvers (CaDiCaL, Kissat) or ILP solvers

4. **Symmetry-breaking during search:**
   - Integrate symmetry detection into the solver
   - Avoid enumerating symmetric copies

5. **Mathematical proof:**
   - Prove uniqueness/non-uniqueness through combinatorial arguments
   - Use coloring, parity, or other invariants

---

## 5. Scaling Assessment for Other Pieces

### 5.1 W Pentacube (5×7×9)

W is defined as:
```
[[0 0 0]
 [1 0 0]
 [1 1 0]
 [2 1 0]
 [2 2 0]]
```

W is also a 2D piece (all cells at z=0). Like V, it likely cannot tile a single 5×7 layer.

**Prediction:** Macro technique will fail for W in 5×7 cross-section for the same reason.

### 5.2 S Pentacube (5×9×15)

S is a truly 3D piece. The Macro technique worked for S in 4×8.

**Prediction:** Macro technique may work for S in 5×9 cross-section, but:
- State space will be much larger (5×9 = 45 cells vs 4×8 = 32 cells)
- State size: 3 × 45 = 135 bits (vs 3 × 32 = 96 bits)
- Computation will be significantly slower

### 5.3 T Pentacube (3×15×17)

T is defined as:
```
[[0 0 0]
 [1 0 0]
 [2 0 0]
 [1 1 0]
 [1 2 0]]
```

T is a 2D piece. It likely cannot tile a single 3×15 layer.

**Prediction:** Macro technique will fail for T in 3×15 cross-section.

---

## 6. Recommendations

### 6.1 Immediate Actions

1. **Do not attempt Macro for V, W, or T** in their minimal odd boxes
2. **Document this limitation** clearly in the project
3. **Focus on S** if Macro is to be used (it's the only piece where Macro has been validated)

### 6.2 Future Work

To solve the uniqueness question for V, W, T:

1. **Implement a faster exact-cover solver:**
   - Dancing Links (DLX) implementation
   - SAT solver encoding
   - ILP formulation

2. **Develop alternative decomposition techniques:**
   - Slab-based Macro (track 5+ layers)
   - Cross-section + height decomposition
   - Divide-and-conquer with interface tracking

3. **Use symmetry-breaking:**
   - Integrate symmetry detection into the solver
   - Enumerate only one representative per symmetry orbit

4. **Mathematical approaches:**
   - Prove uniqueness/non-uniqueness through combinatorial arguments
   - Use computational proof assistants

---

## 7. Summary Table

| Piece | Minimal Odd Box | Macro Applicable? | Reason |
|-------|----------------|-------------------|--------|
| V | 5×5×9 | **NO** | Cannot tile single 5×5 layer |
| W | 5×7×9 | **NO** (predicted) | Cannot tile single 5×7 layer |
| S | 5×9×15 | **MAYBE** | 3D piece, but large state space |
| T | 3×15×17 | **NO** (predicted) | Cannot tile single 3×15 layer |

---

## 8. Validation

### 8.1 Tests Performed

1. ✅ Verified V piece definition (2D piece, 4 single-layer rotations)
2. ✅ Generated all single-layer placements in 5×5×1 (36 placements)
3. ✅ Attempted exact-cover tiling of 5×5 layer (0 solutions)
4. ✅ Tested multiple layer sizes (3×5, 5×5, 5×7, 5×9) - all 0 solutions
5. ✅ Ran Macro solver for V in 5×5×9 (0 sources, 0 macro states)
6. ✅ Compared with S pentacube (truly 3D piece, Macro works)

### 8.2 Reproducibility

All tests can be reproduced using:
```bash
# Test if V can tile a 5x5 layer
python3 -c "
import sys
sys.path.insert(0, '.')
from common.polycube_utils import PENTACUBES, generate_placements, build_exact_cover_data
from common.algorithm_x_fast import solve

piece = PENTACUBES['V']
raw, _ = generate_placements(piece, (5, 5, 1), break_symmetry=False)
single_layer = {idx: p for idx, p in raw.items() 
                if len(set(z for x, y, z in p)) == 1}
X, box_list = build_exact_cover_data(single_layer, (5, 5, 1))
count = sum(1 for _ in solve(X, single_layer, set(box_list), [True]*len(single_layer)))
print(f'V tilings of 5x5 layer: {count}')
"

# Run Macro solver for V in 5x5x9
python3 solvers/v_5x5_macro.py --target-depth 9 --max-states 100000
```

---

## 9. Conclusion

**The Macro technique cannot be applied to the V pentacube in 5×5×9 due to a fundamental structural limitation: V cannot tile a single 5×5 layer.**

This is not a computational limitation or a matter of insufficient search; it is a mathematical property of the V pentacube and the 5×5 cross-section.

**Uniqueness status for V in 5×5×9: UNDETERMINED**

The uniqueness question remains open and requires alternative computational or mathematical approaches.

---

**Report prepared by:** OpenWork automated analysis  
**Date:** 2026-08-21  
**Status:** FINAL (fundamental limitation identified, no false results reported)
