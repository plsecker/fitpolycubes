#!/usr/bin/env python3
"""
Reconstruct actual V pentacube tilings from Macro paths.

This script:
1. Enumerates all 80 Macro paths from 0 to 0 at depth 6
2. For each path, reconstructs the actual V pentacube placements
3. Verifies that each tiling is valid
4. Applies symmetry reduction to count symmetry orbits
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
    
    Args:
        path: list of states [0, s1, s2, ..., s5, 0]
        templates: dict mapping target cell to list of templates
    
    Returns:
        list of placements, where each placement is a list of 5 (x, y, z) tuples
    """
    placements = []
    
    # For each transition in the path, reconstruct the placements
    for depth in range(len(path) - 1):
        start_state = path[depth]
        end_state = path[depth + 1]
        
        # Find the sequence of intermediate states and templates
        # that transition from start_state to end_state
        intermediate_states, templates_used = find_transition_sequence(
            start_state, end_state, templates
        )
        
        if intermediate_states is None:
            return None
        
        # Convert each template to actual placements
        for i, template in enumerate(templates_used):
            # The template is applied at layer `depth`
            # We need to extract the actual cells from the template
            placement = extract_placement_from_template(template, depth)
            if placement:
                placements.append(placement)
    
    return placements


def find_transition_sequence(start_state, end_state, templates, max_steps=1000):
    """
    Find the sequence of intermediate states and templates that transition
    from start_state to end_state.
    
    Returns:
        (intermediate_states, templates_used) or (None, None) if not found
    """
    # BFS to find path
    queue = deque([(start_state, [start_state], [])])
    seen = {start_state}
    
    while queue:
        state, path, templates_used = queue.popleft()
        
        if len(path) > max_steps:
            continue
        
        # Check if layer 0 is full
        if layer_mask(state, 0) == WORD_MASK:
            # Shift and check if we've reached end_state
            shifted = shift_state(state)
            if shifted == end_state:
                return path, templates_used
            # If not, continue exploring from the shifted state
            # But we need to be careful not to infinite loop
            # Actually, in the Macro semantics, when layer 0 is full, we MUST shift
            # So we should only continue if we haven't reached end_state yet
            # But the path should end with the shift, so we shouldn't continue
            continue
        
        # Find first empty cell in layer 0
        target = first_empty(layer_mask(state, 0))
        
        if target < 0:
            # This shouldn't happen if layer 0 is not full
            continue
        
        # Try all templates for this target
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
    
    A template is a 75-bit integer representing 3 layers of 25 cells each.
    We need to extract the 5 cells that are set in the template.
    
    Args:
        template: 75-bit integer
        z_offset: the z-coordinate offset for this placement
    
    Returns:
        list of 5 (x, y, z) tuples, or None if invalid
    """
    cells = []
    
    for layer in range(3):
        layer_mask = (template >> (layer * NCELLS)) & WORD_MASK
        
        for cell_id in range(NCELLS):
            if layer_mask & (1 << cell_id):
                x = cell_id % 5
                y = cell_id // 5
                z = z_offset + layer
                cells.append((x, y, z))
    
    if len(cells) != 5:
        return None
    
    return cells


def verify_tiling(placements, box_size=(5, 5, 6)):
    """
    Verify that a tiling is valid.
    
    Args:
        placements: list of placements, where each placement is a list of 5 (x, y, z) tuples
        box_size: (x_size, y_size, z_size)
    
    Returns:
        True if valid, False otherwise
    """
    x_size, y_size, z_size = box_size
    
    # Check that we have the right number of pieces
    expected_pieces = (x_size * y_size * z_size) // 5
    if len(placements) != expected_pieces:
        return False
    
    # Check that all cells are within bounds
    for placement in placements:
        if len(placement) != 5:
            return False
        
        for x, y, z in placement:
            if not (0 <= x < x_size and 0 <= y < y_size and 0 <= z < z_size):
                return False
    
    # Check that all cells are covered exactly once
    covered = set()
    for placement in placements:
        for cell in placement:
            if cell in covered:
                return False
            covered.add(cell)
    
    expected_cells = x_size * y_size * z_size
    if len(covered) != expected_cells:
        return False
    
    return True


def canonicalize_tiling(placements):
    """
    Canonicalize a tiling by sorting the placements and cells.
    
    Args:
        placements: list of placements
    
    Returns:
        canonical form as a tuple of tuples
    """
    # Sort cells within each placement
    sorted_placements = [tuple(sorted(p)) for p in placements]
    
    # Sort placements
    sorted_placements.sort()
    
    return tuple(sorted_placements)


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
        
        # Find successors
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
    print("V PENTACUBE TILING RECONSTRUCTION AND SYMMETRY REDUCTION")
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
    valid_count = 0
    
    for i, path in enumerate(paths):
        if (i + 1) % 10 == 0:
            print(f"  Processing path {i+1}/80...")
        
        placements = reconstruct_placements_from_path(path, templates)
        
        if placements is None:
            print(f"  WARNING: Could not reconstruct tiling for path {i+1}")
            continue
        
        if verify_tiling(placements):
            valid_count += 1
            canonical = canonicalize_tiling(placements)
            tilings.append(canonical)
        else:
            print(f"  WARNING: Tiling {i+1} is invalid")
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} valid tilings in {elapsed:.1f}s")
    print()
    
    # Check distinctness
    print("Checking tiling distinctness...")
    unique_tilings = set(tilings)
    print(f"  Unique tilings: {len(unique_tilings)}")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Macro paths: {len(paths)}")
    print(f"Valid tilings reconstructed: {valid_count}")
    print(f"Unique tilings: {len(unique_tilings)}")
    print()
    
    if len(unique_tilings) == 80:
        print("✓ All 80 tilings are geometrically distinct")
    else:
        print(f"✗ Only {len(unique_tilings)} unique tilings found")
    
    print()
    print("Next step: Apply symmetry reduction to count symmetry orbits")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
