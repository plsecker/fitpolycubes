# Exhaustive Enumeration and Symmetry Verification Method

A reusable template for determining the complete solution set of a single
pentacube in a rectangular box and classifying it under a chosen symmetry group.

Each section shows the general step, then gives the **V 5×5×9 worked example**.

---

## 1. Problem Definition

State the problem precisely before any computation.

| Field | Description |
|-------|-------------|
| **Piece** | Exact polycube (canonical coordinates, chirality) |
| **Box** | Dimensions (a×b×c) and volume |
| **Number of copies** | volume ÷ 5 |
| **Equivalence convention** | Which symmetries identify tilings (rotations only? reflections allowed?) |
| **Group of interest** | The user's stated convention for "distinct" tilings |

### V 5×5×9 worked example

```
Piece:    V pentacube  ((0,0,0),(1,0,0),(2,0,0),(0,1,0),(0,2,0))
Box:      5 × 5 × 9  (volume 225)
Copies:   45
Chiral:   No (V is achiral — 12 orientations under 24 cube symmetries)
Convention:  George's V4 group:
             I    (x, y, z)
             R_x  (x, 4−y, 8−z)
             R_y  (4−x, y, 8−z)
             R_z  (4−x, 4−y, z)
             (proper 180° rotations only, no reflections)
```

---

## 2. Raw Enumeration

Obtain the complete set of raw tilings.

### Steps

1. **Generate all legal placements** of the piece in the box (all orientations,
   all positions). Verify the count against the expected number from geometry:
   for each orientation, compute (x-range) × (y-range) × (z-range) of its bounding
   box and sum over orientations.

2. **Choose a solver.** Algorithm X (Dancing Links) is the standard exact-cover
   solver. Use it without symmetry breaking (`--no-symmetry`) to obtain every
   distinct placement sequence.

3. **Run to completion.** The solver must terminate normally (exhaust the search
   tree), not be killed or interrupted mid-search. Partial output is not valid
   for a completeness claim.

4. **Run twice independently** to a fresh output file. Cross-compare the solution
   sets. They must be identical. This rules out transient errors, filesystem
   corruption, or accidental truncation.

5. **Confirm solver termination.** The solver prints a final count and exits
   without error. The last line of output is "Total solutions found: N" or
   equivalent.

#### V 5×5×9 worked example

```
Solver:       fitpolycubes_fast.py (Algorithm X, no symmetry breaking)
Placements:   1,164  (12 orientations: 6 with 105 positions, 6 with 81)
Run 1:        1,120 solutions, 2,325 s
Run 2:        1,120 solutions, 2,422 s
Comparison:   identical sets (0 differences)
Status:       solver terminated normally both times
```

---

## 3. Solution Validation

Every raw solution must satisfy the tiling conditions.

### Checks

| Check | Criterion |
|-------|-----------|
| Piece count | Exactly `volume ÷ 5` pieces |
| Cells per piece | Exactly 5 cells |
| Cell bounds | Every cell inside [0,a)×[0,b)×[0,c) |
| No overlaps | No cell appears in more than one piece |
| Full coverage | The union of all cells has cardinality equal to the box volume |
| Gap-free | Cell count = box volume (redundant with the union check but worth verifying independently) |

### V 5×5×9 worked example

```
Valid:  1,120/1,120  (all 1,120 solutions pass all checks)
```

---

## 4. Canonical Representation

Define a deterministic canonical form so solutions can be deduplicated and compared.

### Method

```
canonicalize(tiling):
    for each piece:
        sort the 5 cell tuples within the piece
    sort the 45 pieces lexicographically
    return tuple(piece_0, piece_1, ..., piece_44)
```

This canonical form is invariant under permutation of pieces and within-piece
cell order, but NOT under box symmetries. It identifies exact raw duplicates.

### V 5×5×9 worked example

```
Distinct raw tilings:  1,120
Duplicates:            0
```

---

## 5. Symmetry Classification

Classify the solution set under the chosen symmetry group.

### 5.1 Define the group

List every group element as an explicit coordinate transformation.

For a rectangular box with dimensions (a, b, c), each symmetry is a pair
`(perm, signs)` where `perm` is a permutation of (0,1,2) and `signs` is a
triple of +1 or −1. The box must be invariant under the permutation
(dimensions must match).

**V4** (George's convention for 5×5×9):
```
I    → perm=(0,1,2), signs=(+1,+1,+1)
R_x  → perm=(0,1,2), signs=(+1,−1,−1)     (x, 4−y, 8−z)
R_y  → perm=(0,1,2), signs=(−1,+1,−1)     (4−x, y, 8−z)
R_z  → perm=(0,1,2), signs=(−1,−1,+1)     (4−x, 4−y, z)
```

### 5.2 Apply group action to tilings

```
apply(g, tiling):
    for each piece in tiling:
        for each cell (x,y,z) in piece:
            (nx,ny,nz) = transform(g, x, y, z)
        sort the transformed cells within the piece
    sort the pieces
    return canonicalized result
```

### 5.3 Compute orbits and stabilizers

For each distinct raw tiling:

```
orbit(tiling):
    result = set()
    for each g in group:
        result.add(canonicalize(apply(g, tiling)))
    return result

stabilizer(tiling):
    result = []
    can = canonicalize(tiling)
    for each g in group:
        if canonicalize(apply(g, tiling)) == can:
            result.append(g)
    return result
```

### 5.4 Partition into equivalence classes

Process each distinct raw tiling. For each one whose canonical form is not yet
assigned to a class:
- compute its orbit
- record orbit_size = |orbit|
- record stabilizer and stabilizer_size
- assign all members of the orbit to this class
- verify orbit_size × stabilizer_size = |group| (orbit-stabilizer theorem)

### 5.5 Verify V4 closure

For every tiling T in the complete set, every V4 transform g(T) must also be
in the set. Check this explicitly. If any transform is missing, the set is not
closed under V4.

### V 5×5×9 worked example

```
V4 group size:   4
Classes:         280
  All asymmetric:    280  (stabilizer = {I}, orbit size = 4)
  Symmetric:          0
  Rz-fixed:           0
  Rx-fixed:           0
  Ry-fixed:           0
Orbit-stabilizer:     all 280 classes pass (4 × 1 = 4)
V4 closure:          verified (0 failures)
```

---

## 6. Secondary Symmetry Groups

For comparison, classify under larger groups. Keep these clearly separate from
the primary convention.

### 6.1 Proper rotations (G8)

All 8 proper rotations of the box (det = +1). This includes the V4 elements
plus the 90° rotations and axis swaps that the box dimensions allow.

### 6.2 Full box symmetry (G16)

All 16 symmetries including reflections. Use as a consistency check: every
G8 class is a union of V4 classes; every G16 class is a union of G8 classes.

### V 5×5×9 worked example

```
Group        Size   Classes   Orbit size   Total
V4             4      280         4         1,120
G8             8      140         8         1,120
G16           16       70        16         1,120

Nesting:  280 × 4 = 140 × 8 = 70 × 16 = 1,120  ✓
```

---

## 7. Mathematical Proofs (Beyond Search)

Establish symmetry impossibility results that are stronger than solver output.

### 7.1 Parity method

Given a symmetry transformation g acting on the set of legal placements:

1. Partition placements into g-cycles.
2. Count placements fixed by g (cycles of size 1).
3. An g-invariant tiling must be a union of complete g-cycles.
4. If every cycle has size ≥ 2, then any g-invariant tiling must contain
   an even number of pieces.
5. If the box requires an odd number of pieces, no g-invariant tiling exists.

This proof is independent of any solver — it depends only on the geometry of
the piece and the box.

### 7.2 When parity applies

Parity proves impossibility when:
- No placement is fixed by g (zero 1-cycles), AND
- box volume ÷ 5 is odd.

Check both conditions before asserting the proof.

### V 5×5×9 worked example

```
For each of Rz, Rx, Ry:
  Fixed placements:     0 / 1,164
  All other orbits:     size 2
  Odd piece count:      45
  → No g-invariant tiling exists (proved)
```

---

## 8. Reproducibility

Document the exact commands and expected outputs.

### Solver

```bash
python3 solvers/fitpolycubes_fast.py <PIECE> --box <A> <B> <C> --no-symmetry
```

### Validation and classification

```bash
python3 solvers/v_5x5x9_complete_analysis.py
```

### Parity verification

```bash
python3 -c "
from common.polycube_utils import PENTACUBES, generate_placements
p, _ = generate_placements(PENTACUBES['V'], (5,5,9), break_symmetry=False)
cells = [tuple(sorted(c)) for c in p.values()]
for name, fn in [('Rz',lambda cs:tuple(sorted((4-x,4-y,z) for x,y,z in cs))),
                  ('Rx',lambda cs:tuple(sorted((x,4-y,8-z) for x,y,z in cs))),
                  ('Ry',lambda cs:tuple(sorted((4-x,y,8-z) for x,y,z in cs)))]:
    fixed = sum(1 for c in cells if fn(c)==c)
    print(f'{name}: {fixed} fixed out of {len(cells)}')
"
```

### Expected results table

| Quantity | Value |
|----------|-------|
| Raw solutions | **N** |
| Primary group classes | **C** |
| Asymmetric classes | **C_asym** |
| Symmetric classes | **C_sym** |
| Rz-fixed | **0** |
| Rx-fixed | **0** |
| Ry-fixed | **0** |
| Closure verified | **Yes** |
| Orbit-stabilizer | **All pass** |

---

## 9. Provenance Reconciliation

If the result contradicts a published or privately communicated claim:

### Steps

1. **Identify the exact claim.** Quote verbatim. Note the source (URL, email,
   conversation) and date.

2. **Check public sources.** Search the claimant's published pages, catalogues,
   and the academic literature. Record what is and is not found.

3. **Determine the claim's context.** Was it based on incomplete data?
   A different piece or box? A different symmetry convention? A different
   definition of "solution" (e.g. counting only one per orbit)?

4. **Consider alternative hypotheses.**
   - Different piece (chiral counterpart, reflected version)
   - Different box dimensions
   - Different symmetry convention
   - Mistaken assignment (e.g. the symmetric tiling might be for a different
     piece, such as H or Q in the same odd box)

5. **Test each hypothesis** that could resolve the discrepancy. Compute or
   prove the result under each alternative. Report which alternatives are
   consistent with the data and which are ruled out.

6. **Report the discrepancy** without accusing. Frame the old claim as a
   reasonable inference from incomplete data, now superseded by the complete
   enumeration.

### V 5×5×9 worked example

```
Claim:  "there is a unique solution with rotation around the long axis"
Source: private communication (no published source found)
Context:  The claim accompanied a prediction of "5 asymmetric × 4 +
          1 symmetric × 2 = 22" for an incomplete 22-record snapshot.

Resolution:  The complete enumeration (1,120 solutions) contains no
             Rz-symmetric tiling. Parity proves impossibility.
             The 22-record snapshot was an interrupted partial run.

Alternative hypotheses considered and ruled out:
  - Different piece:            ruled out — V confirmed by context
  - Different box:              ruled out — 5×5×9 confirmed by context
  - Chirality/reflection:       ruled out — V is achiral
  - Mistaken piece assignment:  possible but untestable without
                                further information from the claimant
```

---

## 10. Deliverables Checklist

- [ ] Authoritative solution file (`data/solutions_<piece>_<box>_complete.dat`)
- [ ] Archived partial/historical snapshots (`data/archive/`)
- [ ] Validation script
- [ ] Symmetry classification script
- [ ] Rz-constrained search script (for direct impossibility proof)
- [ ] Parity verification script
- [ ] Final symmetry analysis report
- [ ] Independent verification report
- [ ] Discrepancy audit (if results contradict published claims)
- [ ] Provenance investigation (if results contradict private communications)
- [ ] Reproducibility section in project README

---

## Appendix: Template Script Skeleton

```python
#!/usr/bin/env python3
"""
Template for a complete enumeration and symmetry analysis script.

Replace the placeholder values marked with << >>.
"""

import sys, re, json, time
from pathlib import Path
from collections import defaultdict
from itertools import permutations, product

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ── Problem definition ──────────────────────────────────────────────
PIECE_LETTER = "<<"   # e.g. "V"
BOX = (<< , << , << )  # e.g. (5, 5, 9)
VOLUME = BOX[0] * BOX[1] * BOX[2]
NPIECES = VOLUME // 5

# ── Group definition ────────────────────────────────────────────────
# Define your symmetry group elements as (perm, signs) pairs.
# V4 example (180° rotations for a 5×5×9 box):
GROUP = {
    "I":   ((0,1,2), ( 1, 1, 1)),
    "R_x": ((0,1,2), ( 1,-1,-1)),
    "R_y": ((0,1,2), (-1, 1,-1)),
    "R_z": ((0,1,2), (-1,-1, 1)),
}

# ── Helper functions ────────────────────────────────────────────────

def canonicalize(placements):
    sorted_pieces = [tuple(sorted(p)) for p in placements]
    sorted_pieces.sort()
    return tuple(sorted_pieces)

def apply_transform(tiling, perm, signs, dims=BOX):
    result = []
    for piece in tiling:
        new_piece = []
        for x, y, z in piece:
            coords = [x, y, z]
            nx = coords[perm[0]] if signs[0]==1 else dims[perm[0]]-1-coords[perm[0]]
            ny = coords[perm[1]] if signs[1]==1 else dims[perm[1]]-1-coords[perm[1]]
            nz = coords[perm[2]] if signs[2]==1 else dims[perm[2]]-1-coords[perm[2]]
            new_piece.append((nx, ny, nz))
        result.append(tuple(sorted(new_piece)))
    result.sort()
    return tuple(result)

def compute_orbit(tiling, group):
    orbit = set()
    for name, (perm, signs) in group.items():
        transformed = apply_transform(tiling, perm, signs)
        orbit.add(canonicalize(transformed))
    return orbit

def compute_stabilizer(tiling, group):
    can = canonicalize(tiling)
    stab = []
    for name, (perm, signs) in group.items():
        if canonicalize(apply_transform(tiling, perm, signs)) == can:
            stab.append(name)
    return stab

# ── Validation ──────────────────────────────────────────────────────

def verify_tiling(placements, box=BOX):
    bx, by, bz = box
    if len(placements) != NPIECES:
        return False, f"Expected {NPIECES} pieces"
    cells = set()
    for pi, p in enumerate(placements):
        if len(p) != 5:
            return False, f"Piece {pi} has {len(p)} cells"
        for x, y, z in p:
            if not (0 <= x < bx and 0 <= y < by and 0 <= z < bz):
                return False, f"({x},{y},{z}) out of bounds"
            if (x, y, z) in cells:
                return False, f"Overlap at ({x},{y},{z})"
            cells.add((x, y, z))
    if len(cells) != VOLUME:
        return False, f"Coverage: {len(cells)}/{VOLUME}"
    return True, "Valid"

# ── Main analysis ───────────────────────────────────────────────────

def main():
    print(f"Piece {PIECE_LETTER} in {BOX[0]}×{BOX[1]}×{BOX[2]}")
    print(f"Expected pieces: {NPIECES}")
    print()

    # 1. Load solutions
    # sols = parse_solution_file("data/solutions_...")

    # 2. Validate
    # ...

    # 3. Deduplicate
    # ...

    # 4. Classify under group
    # ...

    # 5. Report
    # ...

    return 0

if __name__ == "__main__":
    sys.exit(main())
```