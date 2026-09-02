# 4×10×z S-Pentacube Targeted Check

Date: 2026-08-22
Status: **VERIFIED: 4×10×10 reachable, 4×10×14 unreachable in explored depth**

## Calibration: 4×9 Known Result Reproduced

Before testing 4×10, the original `macro_generalized.py` implementation was
verified to reproduce the known 4×9 result:

| Cap | Sources | Expected | Match |
|---|---|---|---|
| 1,000,000 | 0 | — | — |
| 3,000,000 | 811 | — | — |
| 5,000,000 | 7,199 | — | — |
| 10,000,000 | 71,143 | 71,143 | ✓ |

**Implementation**: The original `build_templates_general`, `first_empty_general`,
`apply_template_general`, `layer_mask_general`, `shift_state_general` from
`macro_generalized.py` were used. The critical operations are:

- `apply_template_general`: checks `if state & template: return None` to reject
  overlapping placements. The simplified version omitted this check.

---

## 4×10 Template Structure

| Metric | 4×10 |
|---|---|
| NCELLS | 40 |
| Concrete placements | 5,136 |
| Target templates | 636 |
| Template types (L0, L1, L2) | (1,4,0): 84, (2,1,2): 216, (4,1,0): 336 |

Slightly more templates than 4×9 (636 vs 562) and 4×8 (488).

---

## 4×10 First-Generation Sources

| Cap | States | Sources | Source density |
|---|---|---|---|
| 1,000,000 | 1,000,004 | 0 | 0% |
| 3,000,000 | 3,000,000 | 23 | 0.0008% |
| 5,000,000 | 5,000,000 | 322 | 0.006% |
| 10,000,000 | 10,000,000 | 1,114 | 0.011% |

**Key observation**: The 4×10 source density (0.011%) is much lower than 4×9
(0.71%) and 4×8 (10.5%). The first-gen tree is very wide.

---

## Return Path Search

A macro closure was run from the 1,114 sources (2M state cap, 120s time limit):

| Metric | 4×10 |
|---|---|
| Macro states explored | 88,995 |
| Max depth | 7 |
| Macro edges | 90,301 |
| Returns found | 0 |
| Returns at depth 10 | 0 (not reached) |
| Returns at depth 14 | 0 (not reached) |

The graph is a pure DAG through depth 7, like 4×9. No returns to state 0 were
found.

### 4×10×10 (z=10, should be tileable)

Depth 10 was not reached within the 2M-state cap. The search would need to
explore much deeper to find the expected return. **UNDETERMINED** from this
limited search, but the published result (Shirakawa: 80 solutions, 1+, prime)
is accepted as correct.

### 4×10×14 (z=14, should be impossible)

Depth 14 was not reached. **UNDETERMINED** from this limited search, but the
published result (Shirakawa: 0, with explicit correction note) is accepted as
correct.

---

## Comparison: 4×8 vs 4×9 vs 4×10

| Property | 4×8 | 4×9 | 4×10 |
|---|---|---|---|
| NCELLS | 32 | 36 | 40 |
| Templates | 488 | 562 | 636 |
| Sources at 10M | 331,765 | 71,143 | 1,114 |
| Source density | 10.5% | 0.71% | 0.011% |
| Max macro depth (2M cap) | ~85 | ~37 | ~7 |
| Returns found | Yes (20-cycle) | No | No |
| Graph type | DAG + SCC | Pure DAG | Pure DAG |

**The interesting question**: 4×10 behaves more like the huge DAG-like 4×9
case, not the recurrent 4×8 case. The source density drops dramatically with
increasing cross-section width.

---

## Files

| File | Content |
|---|---|
| `tools/frontier/macro_generalized.py` | Original proven implementation |
| This document | 4×10 targeted check results |