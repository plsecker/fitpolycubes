#!/usr/bin/env python3
"""
Apply symmetry reduction to the first 20 tilings and count orbits.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5x6_quick_diag import find_first_n_paths, reconstruct_tiling, canonicalize_tiling


def apply_box_symmetry(placements, perm, signs):
    """Apply a box symmetry transformation."""
    transformed = []
    
    for placement in placements:
        new_placement = []
        for x, y, z in placement:
            coords = [x, y, z]
            new_coords = tuple(coords[perm[i]] * signs[i] for i in range(3))
            new_placement.append(new_coords)
        transformed.append(tuple(sorted(new_placement)))
    
    return tuple(sorted(transformed))


def normalize_box(placements, box_dims):
    """Normalize a tiling to fit within the box starting at (0,0,0)."""
    all_coords = [coord for p in placements for coord in p]
    min_x = min(c[0] for c in all_coords)
    min_y = min(c[1] for c in all_coords)
    min_z = min(c[2] for c in all_coords)
    
    normalized = []
    for placement in placements:
        new_placement = tuple((x - min_x, y - min_y, z - min_z) for x, y, z in placement)
        normalized.append(new_placement)
    
    return tuple(sorted(normalized))


def canonicalize_under_symmetry(placements, box_dims):
    """Find the canonical form of a tiling under all box symmetries."""
    # Generate all symmetries
    perms = [
        (0, 1, 2), (0, 2, 1), (1, 0, 2),
        (1, 2, 0), (2, 0, 1), (2, 1, 0)
    ]
    
    canonical = None
    
    for perm in perms:
        for sx in [1, -1]:
            for sy in [1, -1]:
                for sz in [1, -1]:
                    signs = (sx, sy, sz)
                    transformed = apply_box_symmetry(placements, perm, signs)
                    normalized = normalize_box(transformed, box_dims)
                    canonical_form = canonicalize_tiling(normalized)
                    
                    if canonical is None or canonical_form < canonical:
                        canonical = canonical_form
    
    return canonical


def main():
    print("=" * 70)
    print("SYMMETRY REDUCTION: FIRST 20 TILINGS")
    print("=" * 70)
    print()
    
    # Build templates
    from solvers.v_5x5_macro import build_templates
    templates, _, _, _, _ = build_templates()
    
    # Find first 20 paths
    print("Finding first 20 Macro paths...")
    start_time = time.time()
    paths = find_first_n_paths(20, templates)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    # Reconstruct tilings
    print("Reconstructing tilings...")
    start_time = time.time()
    tilings = []
    
    for i, path in enumerate(paths):
        tiling = reconstruct_tiling(path, templates)
        if tiling is not None:
            tilings.append(tiling)
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Apply symmetry reduction
    print("Applying symmetry reduction...")
    start_time = time.time()
    symmetry_orbits = {}
    box_dims = (5, 5, 6)
    
    for i, tiling in enumerate(tilings):
        if (i + 1) % 5 == 0:
            print(f"  Processing tiling {i+1}/{len(tilings)}...")
        
        # Find canonical form under symmetry
        sym_canonical = canonicalize_under_symmetry(tiling, box_dims)
        
        if sym_canonical not in symmetry_orbits:
            symmetry_orbits[sym_canonical] = []
        
        symmetry_orbits[sym_canonical].append(i)
    
    elapsed = time.time() - start_time
    print(f"  Symmetry reduction completed in {elapsed:.1f}s")
    print(f"  Symmetry orbits: {len(symmetry_orbits)}")
    print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Raw tilings: {len(tilings)}")
    print(f"Symmetry orbits: {len(symmetry_orbits)}")
    print()
    
    # Show orbit sizes
    print("Orbit sizes:")
    for i, (canonical, tiling_indices) in enumerate(sorted(symmetry_orbits.items(), key=lambda x: len(x[1]), reverse=True)):
        print(f"  Orbit {i+1}: {len(tiling_indices)} tilings")
    
    print()
    
    # Extrapolate to 80 tilings
    if len(symmetry_orbits) > 0:
        avg_orbit_size = len(tilings) / len(symmetry_orbits)
        expected_orbits_for_80 = 80 / avg_orbit_size
        print(f"Average orbit size: {avg_orbit_size:.2f}")
        print(f"Expected orbits for 80 tilings: {expected_orbits_for_80:.1f}")
        print()
        
        if abs(expected_orbits_for_80 - 9) < 2:
            print("✓ CONSISTENT: Extrapolation suggests ~9 orbits for 80 tilings")
            print("  This matches the authoritative '9 tilings' (symmetry orbits)")
        else:
            print("✗ INCONSISTENT: Extrapolation does not match 9 orbits")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
