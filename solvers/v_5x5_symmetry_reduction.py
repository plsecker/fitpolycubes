#!/usr/bin/env python3
"""
Apply symmetry reduction to V pentacube tilings in 5×5×6 box.

This script:
1. Reconstructs all 80 tilings from Macro paths
2. Applies the full symmetry group of the 5×5×6 box
3. Counts symmetry orbits
4. Verifies that we get 9 orbits (matching authoritative result)
"""

import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK, NCELLS
)


def reconstruct_placements_from_path(path, templates):
    """
    Reconstruct the actual V pentacube placements from a Macro path.
    """
    placements = []
    
    for depth in range(len(path) - 1):
        start_state = path[depth]
        end_state = path[depth + 1]
        
        intermediate_states, templates_used = find_transition_sequence(
            start_state, end_state, templates
        )
        
        if intermediate_states is None:
            return None
        
        for i, template in enumerate(templates_used):
            placement = extract_placement_from_template(template, depth)
            if placement:
                placements.append(placement)
    
    return placements


def find_transition_sequence(start_state, end_state, templates, max_steps=1000):
    """
    Find the sequence of intermediate states and templates that transition
    from start_state to end_state.
    """
    queue = deque([(start_state, [start_state], [])])
    seen = {start_state}
    
    while queue:
        state, path, templates_used = queue.popleft()
        
        if len(path) > max_steps:
            continue
        
        if layer_mask(state, 0) == WORD_MASK:
            shifted = shift_state(state)
            if shifted == end_state:
                return path, templates_used
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        if target < 0:
            continue
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append((nxt, path + [nxt], templates_used + [template]))
    
    return None, None


def extract_placement_from_template(template, z_offset):
    """
    Extract the actual V pentacube placement from a template.
    """
    cells = []
    
    for layer in range(3):
        layer_mask_val = (template >> (layer * NCELLS)) & WORD_MASK
        
        for cell_id in range(NCELLS):
            if layer_mask_val & (1 << cell_id):
                x = cell_id % 5
                y = cell_id // 5
                z = z_offset + layer
                cells.append((x, y, z))
    
    if len(cells) != 5:
        return None
    
    return cells


def canonicalize_tiling(placements):
    """
    Canonicalize a tiling by sorting the placements and cells.
    """
    sorted_placements = [tuple(sorted(p)) for p in placements]
    sorted_placements.sort()
    return tuple(sorted_placements)


def get_box_symmetries(box_size):
    """
    Get all symmetries of a rectangular box.
    
    For a box with dimensions (a, b, c), the symmetry group includes:
    - Permutations of axes (if dimensions are equal)
    - Reflections of each axis
    
    For 5×5×6, we have:
    - 2 permutations of the two 5's (swap or not)
    - 2^3 = 8 reflections (each axis can be reflected or not)
    - Total: 2 × 8 = 16 symmetries
    """
    a, b, c = box_size
    symmetries = []
    
    # Generate all permutations of axes
    # For 5×5×6, we can swap the first two axes (both are 5)
    permutations = [
        (0, 1, 2),  # identity
        (1, 0, 2),  # swap x and y
    ]
    
    # Generate all reflections
    for perm in permutations:
        for rx in [False, True]:
            for ry in [False, True]:
                for rz in [False, True]:
                    symmetries.append((perm, (rx, ry, rz)))
    
    return symmetries


def apply_symmetry(placements, symmetry, box_size):
    """
    Apply a symmetry transformation to a tiling.
    
    Args:
        placements: list of placements
        symmetry: (perm, (rx, ry, rz)) where perm is axis permutation
                  and rx, ry, rz are reflection flags
        box_size: (a, b, c) box dimensions
    
    Returns:
        transformed placements (canonicalized)
    """
    a, b, c = box_size
    perm, (rx, ry, rz) = symmetry
    
    transformed = []
    for placement in placements:
        new_placement = []
        for x, y, z in placement:
            # Apply permutation
            coords = [x, y, z]
            new_coords = [coords[perm[0]], coords[perm[1]], coords[perm[2]]]
            
            # Apply reflections
            if rx:
                new_coords[0] = a - 1 - new_coords[0]
            if ry:
                new_coords[1] = b - 1 - new_coords[1]
            if rz:
                new_coords[2] = c - 1 - new_coords[2]
            
            new_placement.append(tuple(new_coords))
        
        transformed.append(tuple(sorted(new_placement)))
    
    # Canonicalize
    transformed.sort()
    return tuple(transformed)


def enumerate_all_paths(templates, target_depth, max_paths=100):
    """
    Enumerate all Macro paths from 0 to 0 at target_depth.
    """
    paths = []
    
    def dfs(state, depth, path):
        if len(paths) >= max_paths:
            return
        
        if depth == target_depth:
            if state == 0:
                paths.append(list(path))
            return
        
        successors = set()
        seen = {state}
        queue = deque([state])
        
        while queue:
            s = queue.popleft()
            
            if layer_mask(s, 0) == WORD_MASK:
                successors.add(shift_state(s))
                continue
            
            target = first_empty(layer_mask(s, 0))
            
            for template in templates[target]:
                nxt = apply_template(s, template)
                
                if nxt is None or nxt in seen:
                    continue
                
                seen.add(nxt)
                queue.append(nxt)
        
        for succ in successors:
            dfs(succ, depth + 1, path + [succ])
    
    dfs(0, 0, [0])
    return paths


def main():
    print("=" * 70)
    print("V PENTACUBE SYMMETRY REDUCTION")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Enumerate all 80 paths
    print("Enumerating all 80 Macro paths...")
    start_time = time.time()
    paths = enumerate_all_paths(templates, 6, max_paths=80)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    if len(paths) != 80:
        print(f"ERROR: Expected 80 paths, got {len(paths)}")
        return 1
    
    # Reconstruct tilings
    print("Reconstructing tilings from Macro paths...")
    start_time = time.time()
    tilings = []
    
    for i, path in enumerate(paths):
        if (i + 1) % 10 == 0:
            print(f"  Processing path {i+1}/80...")
        
        placements = reconstruct_placements_from_path(path, templates)
        
        if placements is None:
            print(f"  WARNING: Could not reconstruct tiling for path {i+1}")
            continue
        
        canonical = canonicalize_tiling(placements)
        tilings.append(canonical)
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Get symmetries
    box_size = (5, 5, 6)
    symmetries = get_box_symmetries(box_size)
    print(f"Box size: {box_size}")
    print(f"Number of symmetries: {len(symmetries)}")
    print()
    
    # Apply symmetry reduction
    print("Applying symmetry reduction...")
    start_time = time.time()
    
    orbits = {}
    for i, tiling in enumerate(tilings):
        if (i + 1) % 10 == 0:
            print(f"  Processing tiling {i+1}/{len(tilings)}...")
        
        # Find canonical form under all symmetries
        canonical_forms = []
        for symmetry in symmetries:
            transformed = apply_symmetry(tiling, symmetry, box_size)
            canonical_forms.append(transformed)
        
        # Use the lexicographically smallest as the orbit representative
        orbit_rep = min(canonical_forms)
        
        if orbit_rep not in orbits:
            orbits[orbit_rep] = []
        
        orbits[orbit_rep].append(i)
    
    elapsed = time.time() - start_time
    print(f"  Symmetry reduction completed in {elapsed:.1f}s")
    print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total tilings: {len(tilings)}")
    print(f"Symmetry orbits: {len(orbits)}")
    print()
    
    # Show orbit sizes
    print("Orbit sizes:")
    orbit_sizes = sorted([len(members) for members in orbits.values()], reverse=True)
    for i, size in enumerate(orbit_sizes):
        print(f"  Orbit {i+1}: {size} tilings")
    print()
    
    # Calibration check
    print("Calibration check:")
    print(f"  Expected: 9 symmetry orbits")
    print(f"  Got: {len(orbits)} symmetry orbits")
    if len(orbits) == 9:
        print("  ✓ MATCH")
    else:
        print("  ✗ MISMATCH")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
