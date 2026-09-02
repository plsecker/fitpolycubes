# V 5×5×9 Symmetry Discrepancy — Independent Audit

## Question

George Sicherman states he knows a V 5×5×9 tiling invariant under 180° rotation
about the long axis (Rz). Our complete enumeration of 1,120 solutions reports
**zero Rz-fixed tilings**. Why?

## Audit Results

### 1. Direct symmetry check (all 1,120 solutions)

| Symmetry | Fixed solutions |
|----------|----------------|
| Rz (180° about long axis) | **0** |
| Rx (180° about x-axis) | **0** |
| Ry (180° about y-axis) | **0** |

Every solution has trivial V4 stabilizer {I}. All 280 V4 classes have orbit size 4.

### 2. V4 closure

Every V4 transform of every solution is present in the solution set. The set is
closed under V4. This is verified for all 1,120 solutions.

### 3. V pentacube chirality

The V pentacube is **achiral** — it is identical to its mirror image. All 24 cube
symmetries (proper + improper) produce only 12 unique orientations, all of which
are proper rotations (det = +1). The solver uses all 12 orientations.

### 4. Orientation completeness

The solver generates 1,164 placements for V in 5×5×9, covering all 12 orientations.
Each orientation has the expected number of placements (81 or 105, depending on
bounding box). The solver's placement set is complete.

### 5. Rz mapping of orientations

Rz maps each V orientation to another valid orientation in the placement set.
No orientation is fixed by Rz. This means Rz necessarily permutes the pieces
within a tiling, making it impossible for a tiling to be Rz-fixed unless the
piece permutation happens to map each piece to itself — which would require
each individual piece to be Rz-symmetric, impossible for the V shape.

### 6. Original 22-record snapshot

The original snapshot (now 282 records due to overwriting) also contains **zero
Rz-fixed solutions**. The 22-record snapshot was an early, incomplete solver
output. George's prediction of "5 asymmetric × 4 + 1 symmetric × 2 = 22" was
based on this incomplete data.

## Explanation of the Discrepancy

**George's Rz-symmetric solution does not exist in the complete enumeration.**
Furthermore, **no Rz-symmetric V 5×5×9 tiling can exist at all** — this is proved
by a parity argument, not just by solver output.

### Parity Proof (definitive)

1. Rz acts on the 1,164 legal V placements. Zero placements are fixed by Rz.
2. Every Rz-orbit has size exactly 2.
3. An Rz-invariant tiling must be a union of complete Rz-orbits.
4. Each orbit contributes 2 pieces, so the total piece count must be even.
5. A 5×5×9 box requires 45 V pentacubes, which is odd.
6. Contradiction. **No Rz-invariant tiling exists.**

The same argument applies to Rx and Ry — all non-identity V4 elements have
0 fixed placements and pair placements into 2-cycles, making symmetric tilings
impossible by parity.

This proof is independent of any solver: it depends only on the geometry of
the V pentacube and the box dimensions.

### George's Claim

The most likely explanation is that George's claim was based on the incomplete
22-record snapshot. When only 22 solutions were known, it was plausible that
a symmetric class existed but hadn't been found yet. The complete enumeration
of 1,120 solutions reveals a different structure:

- **280 V4 classes**, all asymmetric (orbit size 4)
- **No symmetric classes** (orbit size 2 or 1)
- **No Rz-fixed solutions**

The mathematical structure is clean and self-consistent:

| Group | Classes | Orbit size | Total |
|-------|---------|------------|-------|
| V4 (180° rotations) | 280 | 4 | 1,120 |
| G8 (proper rotations) | 140 | 8 | 1,120 |
| G16 (full symmetry) | 70 | 16 | 1,120 |

## Alternative Possibilities Considered and Ruled Out

| Hypothesis | Result |
|------------|--------|
| Solver missed solutions | Ruled out — Algorithm X is exhaustive, terminated normally |
| Wrong V piece definition | Ruled out — standard V pentacube, verified in registry |
| Opposite chirality | Ruled out — V is achiral, all orientations are proper rotations |
| Different box dimensions | Ruled out — 5×5×9 confirmed |
| Different symmetry convention | Ruled out — Rz as defined by George tested directly |
| Placement set incomplete | Ruled out — 1,164 placements, all 12 orientations, counts verified |

## Conclusion

**No Rz-symmetric V 5×5×9 tiling exists.** The complete enumeration of 1,120
solutions partitions into 280 V4 classes, all of orbit size 4. George's
prediction was based on the incomplete 22-record snapshot and does not describe
the complete solution space.

## Verification commands

```bash
# Direct symmetry check on all solutions
python3 -c "
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from solvers.v_5x5x9_complete_analysis import *
sols = parse_solution_file('data/solutions_fast_v_5x5x9_checkpoint.dat')
V4 = {'R_z':((0,1,2),(-1,-1,1)),'R_x':((0,1,2),(1,-1,-1)),'R_y':((0,1,2),(-1,1,-1))}
for name,(p,s) in V4.items():
    fixed = sum(1 for sol in sols if canonicalize(sol) == canonicalize(apply_v4(sol,(p,s))))
    print(f'{name}: {fixed}/{len(sols)}')
"

# Full analysis
python3 solvers/v_5x5x9_complete_analysis.py
```