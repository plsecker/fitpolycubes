#!/usr/bin/env python3
"""
Validate the exclusion mechanism on 5×5×6.

This script:
1. Generates all 80 tilings from 5×5×6 using Macro
2. Groups them into 9 symmetry orbits
3. Picks one orbit representative
4. Excludes that orbit
5. Confirms that the other 8 orbits can still be found
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


def canonicalize_tiling(placements):
    """Canonicalize a tiling by sorting the placements and cells."""
    sorted_placements = [tuple(sorted(p)) for p in placements]
    sorted_placements.sort()
    return tuple(sorted_placements)


def get_box_symmetries_5x5x6():
    """Get all symmetries of a 5×5×6 rectangular box."""
    symmetries = []
    
    permutations = [
        (0, 1, 2),
        (1, 0, 2),
    ]
    
    for perm in permutations:
        for rx in [False, True]:
            for ry in [False, True]:
                for rz in [False, True]:
                    symmetries.append((perm, (rx, ry, rz)))
    
    return symmetries


def apply_symmetry(placements, symmetry, box_size):
    """Apply a symmetry transformation to a tiling."""
    a, b, c = box_size
    perm, (rx, ry, rz) = symmetry
    
    transformed = []
    for placement in placements:
        new_placement = []
        for x, y, z in placement:
            coords = [x, y, z]
            new_coords = [coords[perm[0]], coords[perm[1]], coords[perm[2]]]
            
            if rx:
                new_coords[0] = a - 1 - new_coords[0]
            if ry:
                new_coords[1] = b - 1 - new_coords[1]
            if rz:
                new_coords[2] = c - 1 - new_coords[2]
            
            new_placement.append(tuple(new_coords))
        
        transformed.append(tuple(sorted(new_placement)))
    
    transformed.sort()
    return tuple(transformed)


def generate_symmetry_orbit(placements, box_size):
    """Generate all tilings in the symmetry orbit."""
    symmetries = get_box_symmetries_5x5x6()
    orbit = set()
    
    for symmetry in symmetries:
        transformed = apply_symmetry(placements, symmetry, box_size)
        orbit.add(transformed)
    
    return orbit


def find_transition_sequence(start_state, end_state, templates, max_steps=1000):
    """Find the sequence of intermediate states and templates."""
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
    """Extract the actual V pentacube placement from a template."""
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


def reconstruct_placements_from_path(path, templates):
    """Reconstruct the actual V pentacube placements from a Macro path."""
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


def enumerate_all_paths(templates, target_depth, max_paths=100):
    """Enumerate all Macro paths from 0 to 0 at target_depth."""
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


def enumerate_paths_excluding_orbit(templates, target_depth, excluded_orbit, max_paths=100):
    """Enumerate Macro paths, excluding those that produce tilings in the excluded orbit."""
    paths_found = []
    
    def dfs(state, depth, path):
        if len(paths_found) >= max_paths:
            return
        
        if depth == target_depth:
            if state == 0:
                placements = reconstruct_placements_from_path(path, templates)
                
                if placements is None:
                    return
                
                canonical = canonicalize_tiling(placements)
                
                if canonical not in excluded_orbit:
                    paths_found.append((path, placements))
                    return
            
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
    return paths_found


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - EXCLUSION MECHANISM VALIDATION")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Generate all 80 tilings
    print("Generating all 80 tilings from 5×5×6...")
    start_time = time.time()
    all_paths = enumerate_all_paths(templates, 6, max_paths=80)
    elapsed = time.time() - start_time
    print(f"  Generated {len(all_paths)} paths in {elapsed:.1f}s")
    print()
    
    if len(all_paths) != 80:
        print(f"  WARNING: Expected 80 paths, got {len(all_paths)}")
    
    # Reconstruct tilings
    print("Reconstructing tilings from paths...")
    start_time = time.time()
    all_tilings = []
    
    for path in all_paths:
        placements = reconstruct_placements_from_path(path, templates)
        if placements:
            all_tilings.append(placements)
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(all_tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Group into symmetry orbits
    print("Grouping tilings into symmetry orbits...")
    box_size = (5, 5, 6)
    orbits = []
    seen_canonical = set()
    
    for tiling in all_tilings:
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in seen_canonical:
            orbit = generate_symmetry_orbit(tiling, box_size)
            orbits.append(orbit)
            seen_canonical.update(orbit)
    
    print(f"  Found {len(orbits)} symmetry orbits")
    print()
    
    if len(orbits) != 9:
        print(f"  WARNING: Expected 9 orbits, got {len(orbits)}")
    
    # Pick the first orbit to exclude
    excluded_orbit = orbits[0]
    print(f"Excluding orbit 1 (size: {len(excluded_orbit)})")
    print()
    
    # Search for tilings excluding the first orbit
    print("Searching for tilings excluding orbit 1...")
    start_time = time.time()
    
    found_tilings = enumerate_paths_excluding_orbit(
        templates, 6, excluded_orbit, max_paths=100
    )
    
    elapsed = time.time() - start_time
    print(f"  Search completed in {elapsed:.1f}s")
    print(f"  Found {len(found_tilings)} tilings")
    print()
    
    # Check which orbits were found
    print("Checking which orbits were found...")
    found_orbits = set()
    
    for path, placements in found_tilings:
        canonical = canonicalize_tiling(placements)
        
        for i, orbit in enumerate(orbits):
            if canonical in orbit:
                found_orbits.add(i)
                break
    
    print(f"  Found tilings from {len(found_orbits)} different orbits")
    print(f"  Orbit indices: {sorted(found_orbits)}")
    print()
    
    # Results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    expected_orbits = set(range(1, 9))  # Orbits 1-8 (excluding orbit 0)
    
    if found_orbits == expected_orbits:
        print("✓ VALIDATION SUCCESSFUL")
        print()
        print("The exclusion mechanism correctly excludes orbit 0")
        print("and finds tilings from all other 8 orbits.")
        print()
        print("The mechanism is ready for application to 5×5×9.")
    else:
        print("✗ VALIDATION FAILED")
        print()
        print(f"Expected to find orbits: {sorted(expected_orbits)}")
        print(f"Actually found orbits: {sorted(found_orbits)}")
        print()
        
        missing = expected_orbits - found_orbits
        if missing:
            print(f"Missing orbits: {sorted(missing)}")
        
        extra = found_orbits - expected_orbits
        if extra:
            print(f"Unexpected orbits: {sorted(extra)}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
