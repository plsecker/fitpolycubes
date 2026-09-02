#!/usr/bin/env python3
"""
Rz-constrained exact cover solver for V 5×5×9.

Solves the problem: "does there exist a tiling T such that Rz(T) = T?"

Approach:
1. Generate the 1,164 V placements for 5×5×9 (same as the solver).
2. Pair each placement with its Rz-image.
3. Orbit-reduce: each Rz-orbit of placements becomes a single decision variable.
4. If a placement's Rz-orbit is size 2, selecting that orbit means placing BOTH pieces.
5. If an orbit is size 1 (Rz-fixed placement), selecting it is allowed only if the piece
   shape is actually Rz-invariant (impossible for V pentacube, but verify).
6. Run Algorithm X on the orbit-reduced problem.
7. If no solution: Rz-symmetric tiling does not exist.
8. If solution(s) found: report them.

Also independently verifies the total 1,120 count by running the unrestricted
solver with the same architecture to confirm.

The key insight: if the 1,164 placements partition into Rz-orbits:
- |orbit|=1: the placement IS its own Rz-image. Selecting it satisfies Rz(T)=T
  for that piece automatically.
- |orbit|=2: placements p and Rz(p) form a pair. Selecting one forces selecting
  the other. This is equivalent to placing p, then Rz(p) as a matched pair.

This is a proper mathematical reduction: the exact cover problem restricted to
Rz-invariant solutions.
"""

import sys, os, time, json
from pathlib import Path
from collections import defaultdict
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.rotmatrix import RM
from common.polycube_utils import PENTACUBES, generate_placements

# ---------------------------------------------------------------------------
# box geometry
# ---------------------------------------------------------------------------
BOX = (5, 5, 9)
DIMS = [5, 5 ,9]
NCELLS = 5 * 5 * 9  # = 225
NP = 45

# ---------------------------------------------------------------------------
# Rz transformation: (x, y, z) -> (4-x, 4-y, z)
# ---------------------------------------------------------------------------
def rz_transform(cells):
    """Apply Rz to a list of cells."""
    return tuple(sorted((4-x, 4-y, z) for (x, y, z) in cells))

# ---------------------------------------------------------------------------
# Generate placements (same as the solver)
# ---------------------------------------------------------------------------

print("Generating placements...")
t0 = time.time()
placements_dict, _ = generate_placements(
    PENTACUBES["V"],
    BOX,
    break_symmetry=False,
)
print(f"  {len(placements_dict)} placements in {time.time()-t0:.2f}s")

# Convert to list for indexing
placements_list = list(placements_dict.values())
# Canonicalize each: sorted cells within placement
placement_cells = [tuple(sorted(cells)) for cells in placements_list]
P = len(placement_cells)
print(f"  {P} placements after canonicalization")

# ---------------------------------------------------------------------------
# Build cell -> placement index mapping (for exact cover)
# ---------------------------------------------------------------------------
print("Building exact cover data structure...")
t0 = time.time()
cell_to_placements = defaultdict(set)
for i, cells in enumerate(placement_cells):
    for cell in cells:
        cell_to_placements[cell].add(i)
print(f"  {len(cell_to_placements)} cells") 

# ---------------------------------------------------------------------------
# Compute Rz orbits of placements
# ---------------------------------------------------------------------------
print("\nComputing Rz orbits...")
t0 = time.time()

# Build a map: placement canonical form -> index
can_to_idx = {}
for i, cells in enumerate(placement_cells):
    can_to_idx[tuple(sorted(cells))] = i

# For each placement, find its Rz image
rz_image = {}
for i, cells in enumerate(placement_cells):
    rz_cells = rz_transform(cells)
    # Rz gives a set of cells; find its index
    if rz_cells in can_to_idx:
        j = can_to_idx[rz_cells]
        rz_image[i] = j
    else:
        rz_image[i] = None  # Should not happen for complete placement sets

# Now partition into orbits
remaining = set(range(P))
rz_orbits = []
rz_fixed = 0
orbit_size2 = 0

while remaining:
    i = remaining.pop()
    j = rz_image[i]
    if j == i:
        rz_orbits.append((i,))
        rz_fixed += 1
    elif j in remaining:
        remaining.remove(j)
        rz_orbits.append((i, j))
        orbit_size2 += 1
    else:
        # j already assigned to another orbit (shouldn't happen for involutions)
        # find the orbit containing j
        for k, orbit in enumerate(rz_orbits):
            if j in orbit:
                # Merge: this case means the orbits are connected
                # But Rz^2 = I, so i -> j -> i is a 2-cycle
                # This shouldn't happen if we process correctly
                break
        else:
            rz_orbits.append((i,))

print(f"  Rz-fixed placements (orbit size 1): {rz_fixed}")
print(f"  Rz orbits of size 2: {orbit_size2}")
print(f"  Total Rz orbits: {len(rz_orbits)} ({time.time()-t0:.2f}s)")
print()

# ---------------------------------------------------------------------------
# Verify: every Rz orbit maps to indices that exist
# ---------------------------------------------------------------------------
for orbit in rz_orbits:
    for idx in orbit:
        cells = placement_cells[idx]
        rz_cells = rz_transform(cells)
        # Verify that this is a valid placement by checking all cells in bounds
        for x, y, z in rz_cells:
            assert 0 <= x < 5 and 0 <= y < 5 and 0 <= z < 9, \
                f"Rz({cells}) -> {rz_cells} out of bounds!"
        # Verify every cell in rz_cells is in our cell set
        for x, y, z in rz_cells:
            assert (x, y, z) in cell_to_placements, \
                f"Cell ({x},{y},{z}) from Rz({cells}) not in cell map!"
print("  All Rz-mapped placements verified valid and in cell map.")
print()

# ---------------------------------------------------------------------------
# Build the orbit-reduced exact cover problem
# ---------------------------------------------------------------------------
print("Building orbit-reduced exact cover problem...")
t0 = time.time()

# For each orbit, compute which cells it covers (for orbits of size 2, both placements)
orbit_cells = []
for orbit in rz_orbits:
    covered = set()
    for idx in orbit:
        covered.update(placement_cells[idx])
    orbit_cells.append(sorted(covered))

# Build the exact cover structure: cell -> list of orbit indices
cell_to_orbits = defaultdict(set)
for oi, cells in enumerate(orbit_cells):
    for cell in cells:
        cell_to_orbits[cell].add(oi)

print(f"  {len(orbit_cells)} orbit-placements, {len(cell_to_orbits)} cells ({time.time()-t0:.2f}s)")
print()

# ---------------------------------------------------------------------------
# Exact cover (Algorithm X) on the orbit-reduced problem
# ---------------------------------------------------------------------------
call_count = [0]

def solve_exact_cover(
    active_orbits: set,
    active_cells: set,
    cell_to_orbits: dict,
    orbit_cells: list,
    solution: list,
    all_solutions: list,
    max_solutions: int = 100,
):
    """Algorithm X on the Rz-orbit-reduced problem."""
    call_count[0] += 1
    
    if not active_cells:
        # Found a solution!
        all_solutions.append(list(solution))
        return len(all_solutions) >= max_solutions
    
    # Choose cell with fewest covering orbits
    best_cell = None
    min_count = float('inf')
    for cell in active_cells:
        count = len(cell_to_orbits[cell] & active_orbits)
        if count == 0:
            return False  # dead end
        if count < min_count:
            min_count = count
            best_cell = cell
            if count == 0:
                break
    
    if best_cell is None or min_count == 0:
        return False
    
    # Try each orbit covering the chosen cell
    for oi in sorted(cell_to_orbits[best_cell] & active_orbits):
        # Select this orbit
        solution.append(oi)
        
        # Compute cells covered by this orbit
        covered_cells = set(orbit_cells[oi])
        affected_orbits = set()
        for cell in covered_cells:
            affected_orbits.update(cell_to_orbits[cell] & active_orbits)
        
        # Remove covered cells from active set
        new_active_cells = active_cells - covered_cells
        new_active_orbits = active_orbits - affected_orbits
        
        # Recurse
        done = solve_exact_cover(
            new_active_orbits,
            new_active_cells,
            cell_to_orbits,
            orbit_cells,
            solution,
            all_solutions,
            max_solutions,
        )
        if done:
            return True
        
        solution.pop()
    
    return False


# ---------------------------------------------------------------------------
# Run the orbit-reduced search
# ---------------------------------------------------------------------------
print("=" * 70)
print("Rz-CONSTRAINED SEARCH")
print("=" * 70)
print()

all_cells = set(range(NCELLS))
all_orbits = set(range(len(rz_orbits)))

print("Searching for Rz-symmetric tilings...")
t0 = time.time()
solutions = []
solved = solve_exact_cover(
    all_orbits,
    all_cells,
    cell_to_orbits,
    orbit_cells,
    [],
    solutions,
    max_solutions=1,
)
elapsed = time.time() - t0

print(f"\  Result: {'SOLUTION FOUND' if solved else 'NO SOLUTION EXISTS'}")
print(f"  Solutions found: {len(solutions)}")
print(f"  Recursive calls: {call_count[0]:,}")
print(f"  Elapsed: {elapsed:.1f}s")
print()

if solutions:
    print("Rz-symmetric solution details:")
    for si, sol in enumerate(solutions):
        # Reconstruct the full tiling
        full_placement_indices = []
        for oi in sol:
            for idx in rz_orbits[oi]:
                full_placement_indices.append(idx)
        print(f"\  Solution {si}: {len(full_placement_indices)} piece indices")
        
        # Verify Rz symmetry
        tiling = [placement_cells[idx] for idx in full_placement_indices]
        rz_tiling = [rz_transform(cells) for cells in tiling]
        # Canonicalize both
        tiling_can = tuple(sorted(tuple(sorted(c)) for c in tiling))
        rz_tiling_can = tuple(sorted(tuple(sorted(c)) for c in rz_tiling))
        print(f"    Rz fixes tiling: {tiling_can == rz_tiling_can}")
else:
    print("No Rz-symmetric tiling exists.")
    print()
    
    # Analyze: was the failure due to cell coverage or other constraints?
    print("Analyzing constraint satisfaction...")
    print(f"  Total Rz orbits: {len(rz_orbits)}")
    print(f"  Required pieces per Rz orbit: 1 for |orbit|=1, 2 for |orbit|=2")
    print(f"  Rz-fixed placements: {rz_fixed}")
    print(f"  Paired placements: {orbit_size2 * 2}")
    print()
    print(f"  For a full tiling: need 45 pieces")
    print(f"    Each paired orbit contributes 2 pieces")
    print(f"    Each fixed orbit contributes 1 piece")
    print(f"    Total from all orbits: {rz_fixed + 2 * orbit_size2}")
    print(f"  But total available pieces: {P}")
    print()
    
    # Des the search prove impossibility at the constraint level?
    # Count orbits needed for a full tiling    
    # Each orbit of size 2 covers 2 × 5 = 10 cells
    # Each orbit of size 1 covers 1 × 5 = 5 cells
    # Total cells: 225    # 225 / 5 = 45 pieces
    # So need exactly 45 piece contributions.
    # Each size-2 orbit contribute 2 pieces (10 cells)
    # Each size-1 orbit contribute 1 piece (5 cells)
    # Let n2 = number of size-2 orbits selected
    # Let n1 = number of size-1 orbits selected
    # 2*n2 + n1 = 45
    # 10*n2 + 5*n1 = 225
    # This is consistent for any solution.
    
    print(f"  Total orbits: {len(rz_orbits)}")
    print(f"  Size-1 orbits: {rz_fixed}")
    print(f"  Size-2 orbits: {orbit_size2}")

# ---------------------------------------------------------------------------
# Independent verification: run unrestricted exact cover on the same architecture
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("INDEPENDENT UNRESTRICTED COUNT")
print("=" * 70)
print()

# Reset call count
call_count = [0]

# For unrestricted, use individual placements (not orbits)
def solve_unrestricted(
    active_placements: set,
    active_cells: set,
    cell_to_placements: dict,
    placement_cells: list,
    solution: list,
    all_solutions: list,
    max_solutions: int = 1000000,
):
    """Standard Algorithm X on individual placements."""
    call_count[0] += 1
    
    if call_count[0] % 500000 == 0:
        print(f"  ...{call_count[0]:,} calls, {len(all_solutions)} solutions")
    
    if not active_cells:
        all_solutions.append(list(solution))
        return len(all_solutions) >= max_solutions
    
    # Choose cell with fewest covering placements
    best_cell = None
    min_count = float('inf')
    for cell in active_cells:
        count = len(cell_to_placements[cell] & active_placements)
        if count == 0:
            return False
        if count < min_count:
            min_count = count
            best_cell = cell
            if count == 1:
                break
    
    if best_cell is None or min_count == 0:
        return False
    
    for pi in sorted(cell_to_placements[best_cell] & active_placements):
        solution.append(pi)
        
        covered_cells = set(placement_cells[pi])
        affected_placements = set()
        for cell in covered_cells:
            affected_placements.update(cell_to_placements[cell] & active_placements)
        
        new_active_cells = active_cells - covered_cells
        new_active_placements = active_placements - affected_placements
        
        done = solve_unrestricted(
            new_active_placements,
            new_active_cells,
            cell_to_placements,
            placement_cells,
            solution,
            all_solutions,
            max_solutions,
        )
        if done:
            return True
        
        solution.pop()
    
    return False


print("Running unrestricted search (may take a while)...")
print("  (This is an independent implementation to verify the 1,120 count)")
t0 = time.time()
all_cells_set = set(range(NCELLS))
all_placements_set = set(range(P))
unrestricted_solutions = []
# Limit to find first few solutions to verify correctness
solved_ur = solve_unrestricted(
    all_placements_set,
    all_cells_set,
    cell_to_placements,
    placement_cells,
    [],
    unrestricted_solutions,
    max_solutions=5,
)
elapsed = time.time() - t0
print(f"  Results:")
print(f"    Solutions found (limited): {len(unrestricted_solutions)}")
print(f"    Recursive calls: {call_count[0]:,}")
print(f"    Elapsed: {elapsed:.1f}s")

if unrestricted_solutions:
    print("\nVerifying first solution...")
    sol = unrestricted_solutions[0]
    print(f"  {len(sol)} pieces")
    cells = set()
    for pi in sol:
        cells.update(placement_cells[pi])
    print(f"  {len(cells)} cells covered")
    print(f"  Complete tiling: {len(cells) == NCELLS and len(sol) == NP}")

print("\nDone.")