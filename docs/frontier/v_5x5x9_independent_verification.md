# V 5×5×9: Independent Verification of the Symmetry Result

## The Two Claims to Verify

1. **Claim A**: The complete V 5×5×9 solution set contains exactly 1,120 raw tilings.
2. **Claim B**: No tiling is fixed by Rz (180° rotation about the long axis).

## Verification of Claim A: 1,120 Solutions

### Method
The solver `fitpolycubes_fast.py` implements Algorithm X (Dancing Links) on 1,164 V-piece
placements in a 5×5×9 box. It was run twice to independently fresh output files:

| Run | Date | Solutions | Time | Output File |
|-----|------|-----------|------|-------------|
| 1 | 2026-08-24 | **1,120** | 2,325 s | `solutions_fast_v_5x5x9_checkpoint.dat` |
| 2 | 2026-08-25 | **1,120** | 2,422 s | `solutions_fast_v_5x5x9.dat` |

Both runs terminate normally (solver completes, no interruption).

### Cross-Comparison

| Check | Result |
|-------|--------|
| Run 1 count | 1,120 |
| Run 2 count | 1,120 |
| In run 1 only | 0 |
| In run 2 only | 0 |
| Intersection | **1,120** (identical sets) |
| All solutions valid | Yes (verified: 45 pieces, 225 cells, no overlap, in bounds) |

### Conclusion
Claim A is **confirmed**: the exhaustive V 5×5×9 solution set contains exactly 1,120
distinct raw tilings. The result is reproducible to the exact solution set.

---

## Verification of Claim B: No Rz-Fixed Tilings

### Direct Check
Testing Rz on all 1,120 solutions: **0 Rz-fixed tilings** found.

### Independent Constrained Search
Formulated as: "does there exist a tiling T such that Rz(T) = T?"

The 1,164 placements were partitioned into Rz-orbits. Algorithm X was run on the
orbit-reduced problem (selecting complete Rz-orbits rather than individual placements).

| Quantity | Value |
|----------|-------|
| Total placements | 1,164 |
| Rz-fixed placements (orbit size 1) | **0** |
| Rz orbits of size 2 | 582 |
| Algorithm X result | **No solution exists** |

### Parity Proof (Stronger than Search)
The impossibility can be proved by a parity argument that does not depend on any
search algorithm:

1. Rz partitions the 1,164 placements into cycles. We verified that **no placement
   is fixed by Rz** (every placement maps to a different one under Rz).
2. Therefore every Rz-cycle has size exactly 2.
3. An Rz-invariant tiling T must be a union of complete Rz-cycles.
4. Each cycle contributes 2 pieces to T, so |T| must be **even**.
5. A 5×5×9 box requires 45 V pentacubes, which is **odd**.
6. **Contradiction**. No Rz-invariant tiling can exist.

This proof applies equally to **all three non-identity V4 elements**:

| Symmetry | Fixed placements | Parity | V4-symmetric tiling exists? |
|----------|-----------------|--------|-----------------------------|
| Rz | 0 / 1,164 | 45 odd, all orbits size 2 | **No (proved)** |
| Rx | 0 / 1,164 | 45 odd, all orbits size 2 | **No (proved)** |
| Ry | 0 / 1,164 | 45 odd, all orbits size 2 | **No (proved)** |

The parity argument is mathematically rigorous and independent of solver output:
it depends only on the geometry of the V pentacube and the box dimensions.

---

## George Sicherman's Claim

George stated: *"there is a unique solution with rotation around the long axis"*

This statement was made in the context of the **22-record snapshot** produced by
an interrupted solver run. At that time, only 22 solutions were known, and George
was predicting how the solution set would decompose under V4 if it were complete.
His prediction of "5 asymmetric × 4 + 1 symmetric × 2 = 22" was a plausible
hypothesis based on incomplete data.

The complete enumeration reveals a different structure:
- 1,120 solutions, not 22
- 280 V4 classes, all asymmetric
- No symmetric classes possible (proved by parity)

George's minimal odd box page (https://sicherman.net/c5box/c5oddbox.html) lists
"V: 45 tiles, 5×5×9 (Torsten Sillke)" with no reflection sub-entry, consistent
with our results.

---

## Final Conclusion

| Claim | Status | Evidence |
|-------|--------|----------|
| 1,120 raw tilings | **Confirmed** | Two independent solver runs, identical sets |
| 0 Rz-fixed tilings | **Proved** | Parity argument: 45 odd, all Rz-orbits size 2 |
| 0 Rx-fixed tilings | **Proved** | Same parity argument |
| 0 Ry-fixed tilings | **Proved** | Same parity argument |
| 280 V4 classes | **Confirmed** | All orbit size 4, orbit-stabilizer verified |
| George's 5+1 prediction | **Not applicable** | Based on incomplete 22-record snapshot |

## Verification Commands

```bash
# Parity proof (all three V4 elements)
python3 -c "
from common.polycube_utils import PENTACUBES, generate_placements
p, _ = generate_placements(PENTACUBES['V'], (5,5,9), break_symmetry=False)
cells = [tuple(sorted(c)) for c in p.values()]
for name, fn in [('Rz',lambda cs:tuple(sorted((4-x,4-y,z) for x,y,z in cs))),
                  ('Rx',lambda cs:tuple(sorted((x,4-y,8-z) for x,y,z in cs))),
                  ('Ry',lambda cs:tuple(sorted((4-x,y,8-z) for x,y,z in cs)))]:
    fixed = sum(1 for c in cells if fn(c)==c)
    print(f'{name}: {fixed} fixed out of {len(cells)} → parity: {\"NO symmetric tiling\" if fixed==0 else \"possible\"}')
"

# Independent count
python3 solvers/fitpolycubes_fast.py V --box 5 5 9 --no-symmetry

# Full analysis
python3 solvers/v_5x5x9_complete_analysis.py
```