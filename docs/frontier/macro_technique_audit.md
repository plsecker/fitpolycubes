# Macro Technique Audit: V Pentacube in 5×5×9

**Date:** 2026-08-21  
**Status:** CORRECTED - Previous analysis was invalid  
**Audit Type:** Line-by-line comparison with S implementation

---

## Executive Summary

**CORRECTION:** The previous analysis incorrectly concluded that the Macro technique is inapplicable to V in 5×5×9. This was based on a fundamental misunderstanding of the Macro technique.

**CORRECT FINDING:** The Macro technique **IS applicable** to V in 5×5×9. The implementation is correct and does find sources (9,000 sources after 159,059 states). The issue is **computational feasibility**, not correctness.

---

## 1. Audit of Previous Error

### 1.1 The Incorrect Conclusion

The previous analysis stated:
> "V cannot tile a single 5×5 layer, therefore Macro is inapplicable"

This was **wrong** because it misunderstood what the Macro technique requires.

### 1.2 The Correct Understanding

The Macro technique does NOT require that a layer can be tiled by pieces contained entirely within that layer. Instead:

1. **Pieces can protrude** into subsequent layers (z+1, z+2)
2. **The state tracks occupancy** across 3 consecutive layers
3. **Templates represent placements** that may span multiple layers
4. **A "source" is found** when layer 0 becomes full (all 25 cells occupied), regardless of how the cells were filled

### 1.3 Why V Can Work with Macro

Even though V cannot tile a flat 5×5 layer, V pieces can:
- Lie flat (covering 5 cells in one layer)
- Stand up (covering cells across multiple layers)
- Combine flat and standing orientations to fill layer 0

The Macro technique captures this by:
- Generating templates for all V orientations
- Allowing templates to have bits in layers 0, 1, and 2
- Tracking the frontier state across 3 layers
- Finding sources when layer 0 is full (even if filled by a mix of flat and standing pieces)

---

## 2. Line-by-Line Comparison with S Implementation

### 2.1 State Representation

**S (4×8):**
```python
NCELLS = 32  # 4 × 8
LAYERS = 3
WORD_MASK = (1 << 32) - 1
# State: 3 layers of 32 bits each = 96 bits total
```

**V (5×5):**
```python
NCELLS = 25  # 5 × 5
LAYERS = 3
WORD_MASK = (1 << 25) - 1
# State: 3 layers of 25 bits each = 75 bits total
```

**Verdict:** ✅ CORRECT - Same structure, different dimensions

### 2.2 Template Generation

**S implementation:**
```python
def make_shifted_template(placement_cells, target_z):
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        
        if rel < 0 or rel >= LAYERS:
            return None
        
        shifted_masks[rel] |= (1 << cell_id(x, y))
    
    return pack_layers(shifted_masks)
```

**V implementation:**
```python
def make_shifted_template(placement_cells, target_z):
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        
        if rel < 0 or rel >= LAYERS:
            return None
        
        shifted_masks[rel] |= (1 << cell_id(x, y))
    
    return pack_layers(shifted_masks)
```

**Verdict:** ✅ IDENTICAL - Same logic

### 2.3 Template Building

**S implementation:**
```python
for placement in raw.values():
    cells = tuple(placement)
    
    for x, y, z in cells:
        target = cell_id(x, y)
        packed = make_shifted_template(cells, z)
        
        if packed is None:
            continue
        
        if packed in seen[target]:
            continue
        
        seen[target].add(packed)
        result[target].append(packed)
```

**V implementation:**
```python
for placement in raw.values():
    cells = tuple(placement)
    
    for x, y, z in cells:
        target = cell_id(x, y)
        
        packed = make_shifted_template(cells, z)
        
        if packed is None:
            continue
        
        if packed in seen[target]:
            continue
        
        seen[target].add(packed)
        result[target].append(packed)
```

**Verdict:** ✅ IDENTICAL - Same logic

### 2.4 Transition Logic

**S implementation:**
```python
if layer_mask(state, 0) == WORD_MASK:
    # Layer 0 is full - shift
    nxt = shift_state(state)
    sources.add(nxt)
else:
    # Find first empty cell in layer 0
    target = first_empty(layer_mask(state, 0))
    
    for template in templates[target]:
        nxt = apply_template(state, template)
        
        if nxt is None or nxt in seen:
            continue
        
        seen.add(nxt)
        queue.append(nxt)
```

**V implementation:**
```python
if layer_mask(state, 0) == WORD_MASK:
    sources.add(shift_state(state))
    continue

target = first_empty(layer_mask(state, 0))

for template in templates[target]:
    nxt = apply_template(state, template)
    
    if nxt is None or nxt in seen:
        continue
    
    seen.add(nxt)
    queue.append(nxt)
```

**Verdict:** ✅ IDENTICAL - Same logic

### 2.5 Template Protrusion Verification

**Test:** Do V templates protrude into layers 1 and 2?

**Result:**
```
V templates with protrusions (first 5):
  Target 0: L0=7, L1=1, L2=1
  Target 0: L0=7, L1=4, L2=4
  Target 0: L0=1, L1=1, L2=7
  Target 0: L0=1057, L1=1, L2=1
  Target 0: L0=1, L1=1, L2=1057
```

**Verdict:** ✅ CORRECT - Templates do protrude into layers 1 and 2

---

## 3. Corrected Empirical Results

### 3.1 First Generation (Finding Sources)

**Run:** V Macro exploration up to 500,000 states

**Result:**
```
Progress: 100,000 steps, 139,151 states, 0 sources
Step 106,086: FOUND SOURCE #1
Step 106,087: FOUND SOURCE #2
Step 106,088: FOUND SOURCE #3
...
Progress: 150,000 steps, 157,851 states, 6,536 sources

Total steps: 159,059
States seen: 159,059
Sources found: 9,000
```

**Conclusion:** ✅ Sources ARE found - it just takes 106,000+ steps to find the first one

### 3.2 Macro Closure

**Run:** V Macro closure (full exploration from all sources)

**Result (before timeout at 5 minutes):**
```
8,590,000 macro states, 9,513,141 edges (252.1s)
```

**Conclusion:** The macro closure is very large (8.5M+ states) and computationally expensive

### 3.3 Comparison with S

**S (4×8):**
- First-gen tree states: 3,162,387
- First-gen sources: 331,765
- Macro states (at cap): 15,000,991
- Macro edges: 14,781,970

**V (5×5):**
- First-gen tree states: 159,059
- First-gen sources: 9,000
- Macro states (at timeout): 8,590,000+
- Macro edges: 9,513,141+

**Observation:** V has a smaller first-generation tree but a very large macro closure. This suggests that while finding the first sources is harder for V, the macro graph itself is also very large.

---

## 4. Computational Feasibility Assessment

### 4.1 State Space Size

The V macro closure has 8.5M+ states (and was still growing at timeout). This is comparable to the S closure (15M at cap).

### 4.2 Path Counting Challenge

To determine uniqueness of 5×5×9 V tiling, we need to:
1. Count all paths from state 0 to state 0 at depth 9
2. Reduce these paths under box symmetry (48 symmetries)
3. Count distinct orbits

The challenge is that:
- Each macro transition requires exploring many intermediate states
- The depth-limited search also timed out (5 minutes)
- The state space is very large

### 4.3 Feasibility Conclusion

**The Macro technique is CORRECT for V in 5×5×9, but computationally challenging.**

The state space is large enough that:
- Full closure computation takes >5 minutes (and was still running)
- Depth-limited path counting also times out
- Symmetry reduction would add additional computational cost

---

## 5. Hand-Checkable Example

### 5.1 A V Placement That Crosses the Frontier

**Placement:** V standing up vertically
```
Cells: (0,0,0), (0,0,1), (0,0,2), (1,0,0), (2,0,0)
```

**Template generation (target = cell (0,0) at z=0):**
```
min_z = 0
target_rel = 0 - 0 = 0

Cell (0,0,0): rel = 0 - 0 - 0 = 0 → layer 0, cell_id = 0
Cell (0,0,1): rel = 1 - 0 - 0 = 1 → layer 1, cell_id = 0
Cell (0,0,2): rel = 2 - 0 - 0 = 2 → layer 2, cell_id = 0
Cell (1,0,0): rel = 0 - 0 - 0 = 0 → layer 0, cell_id = 1
Cell (2,0,0): rel = 0 - 0 - 0 = 0 → layer 0, cell_id = 2

Template:
  Layer 0: bits 0, 1, 2 (cells (0,0), (1,0), (2,0))
  Layer 1: bit 0 (cell (0,0))
  Layer 2: bit 0 (cell (0,0))
```

**Verification:** This template has cells in all 3 layers, demonstrating that V placements can cross the frontier.

---

## 6. Recommendations

### 6.1 Immediate Actions

1. **Accept that Macro is correct** for V in 5×5×9
2. **Acknowledge computational challenge** - the state space is large
3. **Do not claim inapplicability** - this was an error

### 6.2 Path Forward

To determine uniqueness, we need:

1. **Optimized Macro implementation:**
   - Use the existing `macro_generalized.py` with checkpoint/resume
   - Run with longer timeout (30+ minutes)
   - Save checkpoint to allow resume

2. **Alternative approaches:**
   - SAT solver encoding
   - ILP formulation
   - Symmetry-breaking during search

3. **Mathematical approaches:**
   - Prove uniqueness/non-uniqueness through combinatorial arguments
   - Use coloring or parity arguments

### 6.3 Scaling Assessment

**V (5×5×9):** Macro is correct but computationally challenging (8.5M+ states)

**W (5×7×9):** Likely similar or larger state space (5×7 = 35 cells vs 5×5 = 25 cells)

**S (5×9×15):** Much larger state space (5×9 = 45 cells), likely infeasible with current approach

**T (3×15×17):** Very large state space (3×15 = 45 cells), likely infeasible

---

## 7. Summary

### 7.1 Corrected Understanding

✅ The Macro technique **IS applicable** to V in 5×5×9  
✅ The implementation is **correct** (identical to S implementation)  
✅ Sources **ARE found** (9,000 sources after 159,059 states)  
❌ The previous conclusion of "inapplicability" was **wrong**

### 7.2 Current Status

**Uniqueness status for V in 5×5×9: UNDETERMINED**

The Macro technique is correct, but the computational cost is high:
- 8.5M+ macro states discovered (still growing)
- Full closure computation takes >5 minutes
- Depth-limited path counting also times out

### 7.3 Next Steps

To determine uniqueness:
1. Run Macro with checkpoint/resume and longer timeout
2. Implement optimized path counting
3. Apply symmetry reduction
4. Or use alternative methods (SAT, ILP, mathematical proof)

---

## 8. Validation

### 8.1 Tests Performed

1. ✅ Line-by-line comparison with S implementation (all functions identical)
2. ✅ Verified templates protrude into layers 1 and 2
3. ✅ Ran first-generation exploration (found 9,000 sources)
4. ✅ Ran macro closure (8.5M+ states before timeout)
5. ✅ Constructed hand-checkable example of frontier-crossing placement

### 8.2 Reproducibility

All tests can be reproduced:

```bash
# Run first-generation exploration
python3 -c "
import sys
sys.path.insert(0, '.')
from solvers.v_5x5_macro import build_templates, layer_mask, first_empty, apply_template, shift_state, WORD_MASK
from collections import deque

templates, _, _, _, _ = build_templates()
queue = deque([0])
seen = {0}
sources = set()

while queue:
    state = queue.popleft()
    if layer_mask(state, 0) == WORD_MASK:
        sources.add(shift_state(state))
        continue
    target = first_empty(layer_mask(state, 0))
    for template in templates[target]:
        nxt = apply_template(state, template)
        if nxt is None or nxt in seen:
            continue
        seen.add(nxt)
        queue.append(nxt)

print(f'Sources found: {len(sources)}')
"
```

---

**Report prepared by:** OpenWork automated analysis  
**Date:** 2026-08-21  
**Status:** CORRECTED (previous error acknowledged and fixed)
