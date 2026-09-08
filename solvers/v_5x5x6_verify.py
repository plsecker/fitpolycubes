#!/usr/bin/env python3
"""
Verify reconstructed tilings and understand the "9 tilings" reference.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5x6_quick_diag import find_first_n_paths, reconstruct_tiling


def verify_tiling(placements, box_dims):
    """Verify a tiling is valid."""
    a, b, c = box_dims
    
    # Check we have 30 placements
    if len(placements) != 30:
        return False, f"Expected 30 placements, got {len(placements)}"
    
    # Check each placement has 5 cells
    for i, p in enumerate(placements):
        if len(p) != 5:
            return False, f"Placement {i} has {len(p)} cells, expected 5"
    
    # Build occupancy grid
    grid = {}
    for i, p in enumerate(placements):
        for x, y, z in p:
            # Check bounds
            if not (0 <= x < a and 0 <= y < b and 0 <= z < c):
                return False, f"Placement {i} cell ({x},{y},{z}) out of bounds"
            
            # Check for overlap
            if (x, y, z) in grid:
                return False, f"Overlap at ({x},{y},{z}) between placements {grid[(x,y,z)]} and {i}"
            
            grid[(x, y, z)] = i
    
    # Check complete coverage
    expected_cells = a * b * c
    if len(grid) != expected_cells:
        return False, f"Incomplete coverage: {len(grid)} cells filled, expected {expected_cells}"
    
    return True, "Valid tiling"


def main():
    print("=" * 70)
    print("VERIFYING RECONSTRUCTED TILINGS")
    print("=" * 70)
    print()
    
    # Build templates
    from solvers.v_5x5_macro import build_templates
    templates, _, _, _, _ = build_templates()
    
    # Find first 10 paths
    print("Finding first 10 Macro paths...")
    paths = find_first_n_paths(10, templates)
    print(f"  Found {len(paths)} paths")
    print()
    
    # Reconstruct and verify
    print("Reconstructing and verifying tilings...")
    valid_count = 0
    
    for i, path in enumerate(paths):
        tiling = reconstruct_tiling(path, templates)
        
        if tiling is None:
            print(f"  Path {i+1}: Failed to reconstruct")
            continue
        
        is_valid, msg = verify_tiling(tiling, (5, 5, 6))
        
        if is_valid:
            print(f"  Path {i+1}: ✓ {msg}")
            valid_count += 1
        else:
            print(f"  Path {i+1}: ✗ {msg}")
    
    print()
    print(f"Valid tilings: {valid_count}/{len(paths)}")
    print()
    
    # Now let's understand what "9 tilings" means
    print("=" * 70)
    print("UNDERSTANDING THE '9 TILINGS' REFERENCE")
    print("=" * 70)
    print()
    
    print("The source (Sillke 1993) states: 5×5×6 -> 9 tilings")
    print()
    print("Possible interpretations:")
    print("  1. 9 raw tilings (all distinct placements)")
    print("  2. 9 tilings up to box symmetry")
    print("  3. 9 tilings up to some other equivalence")
    print()
    print("If interpretation 1 is correct:")
    print("  - We should find exactly 9 distinct tilings")
    print("  - But we're finding 80 Macro paths")
    print("  - This suggests either:")
    print("    a) Multiple paths produce the same tiling")
    print("    b) The Macro approach is overcounting")
    print("    c) The '9' refers to something else")
    print()
    print("If interpretation 2 is correct:")
    print("  - There are 9 symmetry orbits")
    print("  - The total number of raw tilings could be larger")
    print("  - For a 5×5×6 box, the symmetry group has size 16")
    print("  - So we might expect up to 9 × 16 = 144 raw tilings")
    print("  - But we only found 80 Macro paths")
    print()
    print("Next steps:")
    print("  1. Check if the 80 paths produce duplicate tilings")
    print("  2. Apply symmetry reduction to see how many orbits")
    print("  3. Compare with the '9' under the correct interpretation")
    print()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
