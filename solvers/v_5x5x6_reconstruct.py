#!/usr/bin/env python3
"""
Reconstruct tilings from Macro paths for V in 5×5×6.

This script:
1. Enumerates all 80 Macro return paths at depth 6
2. Reconstructs concrete V placements from each path
3. Canonicalizes and deduplicates the tilings
4. Applies symmetry reduction
5. Investigates the path→tiling multiplicity
"""

import sys
import time
import json
from collections import deque, defaultdict
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template, 
    shift_state, WORD_MASK, NCELLS
)
from common.polycube_utils import PENTACUBES
from common.rotmatrix import RM


def template_to_placements(template, layer_offset):
    """
    Convert a template (3-layer bitmask) to concrete cell coordinates.
    
    Args:
        template: 75-bit integer representing 3 layers of 25 cells each
        layer_offset: the z-coordinate of layer 0
    
    Returns:
        list of (x, y, z) tuples
    """
    cells = []
    
    for layer in range(3):
        layer_mask = (template >> (layer * NCELLS)) & WORD_MASK
        
        for cell_id in range(NCELLS):
            if layer_mask & (1 << cell_id):
                x = cell_id % 5
                y = cell_id // 5
                z = layer_offset + layer
                cells.append((x, y, z))
    
    return cells


def find_path_to_successor(start_state, target_successor, templates, max_steps=100):
    """
    Find a sequence of templates that transitions from start_state to target_successor.
    
    Returns:
        list of templates, or None if no path found
    """
    # BFS to find path
    queue = deque([(start_state, [])])
    seen = {start_state}
    
    while queue:
        state, template_seq = queue.popleft()
        
        if len(template_seq) > max_steps:
            continue
        
        # Check if we've reached a state that shifts to target_successor
        if layer_mask(state, 0) == WORD_MASK:
            if shift_state(state) == target_successor:
                return template_seq
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append((nxt, template_seq + [template]))
    
    return None


def reconstruct_tiling_from_macro_path(macro_path, templates):
    """
    Reconstruct a complete tiling from a Macro path.
    
    Args:
        macro_path: list of 7 states [s_0=0, s_1, ..., s_6=0]
        templates: template dictionary
    
    Returns:
        list of 30 placements, where each placement is a list of 5 (x,y,z) tuples
        or None if reconstruction fails
    """
    all_placements = []
    
    for d in range(len(macro_path) - 1):
        start_state = macro_path[d]
        end_state = macro_path[d + 1]
        
        # Find template sequence for this transition
        template_seq = find_path_to_successor(start_state, end_state, templates)
        
        if template_seq is None:
            return None
        
        # Convert templates to concrete placements
        layer_offset = d  # Each Macro step corresponds to one layer
        
        for template in template_seq:
            cells = template_to_placements(template, layer_offset)
            if len(cells) == 5:
                all_placements.append(cells)
    
    return all_placements


def enumerate_all_macro_paths_depth_6(templates, verbose=True):
    """
    Enumerate all Macro return paths from state 0 to state 0 at depth 6.
    
    Returns:
        list of paths, where each path is a list of 7 states
    """
    if verbose:
        print("Enumerating all Macro return paths at depth 6...")
    
    paths = []
    
    def dfs(state, depth, path):
        if depth == 6:
            if state == 0:
                paths.append(list(path))
            return
        
        # Find all successors
        successors = set()
        queue = deque([state])
        seen = {state}
        
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
    
    if verbose:
        print(f"  Found {len(paths)} paths")
    
    return paths


def canonicalize_tiling(placements):
    """
    Canonicalize a tiling by sorting placements and cells.
    
    Args:
        placements: list of placements, where each placement is a list of (x,y,z) tuples
    
    Returns:
        canonical form as a tuple of tuples
    """
    # Sort cells within each placement
    sorted_placements = [tuple(sorted(p)) for p in placements]
    
    # Sort placements
    sorted_placements.sort()
    
    return tuple(sorted_placements)


def apply_box_symmetry(placements, symmetry):
    """
    Apply a box symmetry to a tiling.
    
    Args:
        placements: list of placements
        symmetry: tuple (perm, signs) where perm is a permutation of (0,1,2)
                  and signs is a tuple of 3 signs (+1 or -1)
    
    Returns:
        transformed placements
    """
    perm, signs = symmetry
    
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
    """
    Normalize a tiling to fit within the box starting at (0,0,0).
    
    Args:
        placements: list of placements
        box_dims: (a, b, c) box dimensions
    
    Returns:
        normalized placements
    """
    # Find minimum coordinates
    all_coords = [coord for p in placements for coord in p]
    min_x = min(c[0] for c in all_coords)
    min_y = min(c[1] for c in all_coords)
    min_z = min(c[2] for c in all_coords)
    
    # Shift to origin
    normalized = []
    for placement in placements:
        new_placement = tuple((x - min_x, y - min_y, z - min_z) for x, y, z in placement)
        normalized.append(new_placement)
    
    return tuple(sorted(normalized))


def get_box_symmetries(box_dims):
    """
    Get all symmetries of a rectangular box.
    
    For a box with dimensions (a, b, c), the symmetry group includes:
    - Permutations of dimensions
    - Reflections of each dimension
    
    Returns:
        list of (perm, signs) tuples
    """
    a, b, c = box_dims
    
    symmetries = []
    
    # All permutations of (0, 1, 2)
    perms = [
        (0, 1, 2), (0, 2, 1), (1, 0, 2),
        (1, 2, 0), (2, 0, 1), (2, 1, 0)
    ]
    
    # All sign combinations
    for perm in perms:
        for sx in [1, -1]:
            for sy in [1, -1]:
                for sz in [1, -1]:
                    symmetries.append((perm, (sx, sy, sz)))
    
    return symmetries


def canonicalize_under_symmetry(placements, box_dims):
    """
    Find the canonical form of a tiling under all box symmetries.
    
    Args:
        placements: list of placements
        box_dims: (a, b, c) box dimensions
    
    Returns:
        canonical form
    """
    symmetries = get_box_symmetries(box_dims)
    
    canonical = None
    
    for symmetry in symmetries:
        transformed = apply_box_symmetry(placements, symmetry)
        normalized = normalize_box(transformed, box_dims)
        canonical_form = canonicalize_tiling(normalized)
        
        if canonical is None or canonical_form < canonical:
            canonical = canonical_form
    
    return canonical


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - TILING RECONSTRUCTION")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, concrete_count, total_templates = build_templates()
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Total templates: {total_templates}")
    print()
    
    # Enumerate all Macro paths
    start_time = time.time()
    paths = enumerate_all_macro_paths_depth_6(templates, verbose=True)
    elapsed_enum = time.time() - start_time
    
    print(f"  Enumeration time: {elapsed_enum:.1f}s")
    print()
    
    # Reconstruct tilings from paths
    print("Reconstructing tilings from Macro paths...")
    start_time = time.time()
    
    tilings = []
    failed = 0
    
    for i, path in enumerate(paths):
        if i % 10 == 0:
            print(f"  Processing path {i+1}/{len(paths)}...")
        
        tiling = reconstruct_tiling_from_macro_path(path, templates)
        
        if tiling is None:
            failed += 1
        else:
            tilings.append((path, tiling))
    
    elapsed_recon = time.time() - start_time
    print(f"  Reconstruction time: {elapsed_recon:.1f}s")
    print(f"  Successful: {len(tilings)}")
    print(f"  Failed: {failed}")
    print()
    
    # Canonicalize tilings
    print("Canonicalizing tilings...")
    start_time = time.time()
    
    canonical_tilings = {}
    
    for path, tiling in tilings:
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in canonical_tilings:
            canonical_tilings[canonical] = []
        
        canonical_tilings[canonical].append(path)
    
    elapsed_canon = time.time() - start_time
    print(f"  Canonicalization time: {elapsed_canon:.1f}s")
    print(f"  Distinct raw tilings: {len(canonical_tilings)}")
    print()
    
    # Apply symmetry reduction
    print("Applying symmetry reduction...")
    start_time = time.time()
    
    symmetry_orbits = {}
    box_dims = (5, 5, 6)
    
    for canonical, paths_list in canonical_tilings.items():
        # Convert canonical back to placements
        placements = [list(p) for p in canonical]
        
        # Find canonical form under symmetry
        sym_canonical = canonicalize_under_symmetry(placements, box_dims)
        
        if sym_canonical not in symmetry_orbits:
            symmetry_orbits[sym_canonical] = []
        
        symmetry_orbits[sym_canonical].extend(paths_list)
    
    elapsed_sym = time.time() - start_time
    print(f"  Symmetry reduction time: {elapsed_sym:.1f}s")
    print(f"  Symmetry orbits: {len(symmetry_orbits)}")
    print()
    
    # Analyze multiplicity
    print("Analyzing path multiplicity...")
    
    multiplicity_histogram = defaultdict(int)
    
    for canonical, paths_list in canonical_tilings.items():
        multiplicity = len(paths_list)
        multiplicity_histogram[multiplicity] += 1
    
    print("  Multiplicity histogram (paths per tiling):")
    for mult in sorted(multiplicity_histogram.keys()):
        count = multiplicity_histogram[mult]
        print(f"    {mult} paths: {count} tilings")
    
    print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Macro return paths: {len(paths)}")
    print(f"Distinct raw tilings: {len(canonical_tilings)}")
    print(f"Symmetry orbits: {len(symmetry_orbits)}")
    print(f"Known tilings: 9")
    print()
    
    if len(symmetry_orbits) == 9:
        print("✓ PERFECT MATCH: Symmetry orbits = 9")
    else:
        print(f"✗ MISMATCH: Expected 9, got {len(symmetry_orbits)}")
    
    # Save results
    output = {
        "piece": "V",
        "box": [5, 5, 6],
        "macro_paths": len(paths),
        "distinct_raw_tilings": len(canonical_tilings),
        "symmetry_orbits": len(symmetry_orbits),
        "known_tilings": 9,
        "multiplicity_histogram": dict(multiplicity_histogram),
    }
    
    output_file = Path("/tmp/v_5x5x6_reconstruction.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
