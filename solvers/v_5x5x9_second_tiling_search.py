#!/usr/bin/env python3
"""
Search for a second inequivalent 5×5×9 V tiling.

This script:
1. Loads a known 5×5×9 V tiling from the repository
2. Generates its full symmetry orbit (16 elements)
3. Searches for a second inequivalent tiling using the Macro framework
4. Reports whether the tiling is UNIQUE or NON-UNIQUE
"""

import sys
import time
import ast
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK, NCELLS
)


def parse_solution_file(filepath):
    """Parse a solution file and return the first tiling."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Skip header and solution number
    placements_str = lines[2].strip()
    
    # Parse the placements
    # Format: ((x,y,z), (x,y,z), ...)((x,y,z), ...)
    placements = []
    current = ""
    depth = 0
    
    for char in placements_str:
        if char == '(':
            depth += 1
            if depth == 1:
                current = ""
            else:
                current += char
        elif char == ')':
            depth -= 1
            if depth == 0:
                # End of a placement
                placement = ast.literal_eval(current)
                placements.append(placement)
            else:
                current += char
        else:
            if depth > 0:
                current += char
    
    return placements


def canonicalize_tiling(placements):
    """Canonicalize a tiling by sorting the placements and cells."""
    sorted_placements = [tuple(sorted(p)) for p in placements]
    sorted_placements.sort()
    return tuple(sorted_placements)


def get_box_symmetries_5x5x9():
    """
    Get all symmetries of a 5×5×9 rectangular box.
    
    For a box with dimensions (5, 5, 9), the symmetry group includes:
    - Permutations of axes: 2 permutations (swap the two 5's or not)
    - Reflections: 2³ = 8 reflections (each axis can be reflected or not)
    - Total: 2 × 8 = 16 symmetries
    """
    symmetries = []
    
    # Generate all permutations of axes
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


def generate_symmetry_orbit(placements, box_size):
    """Generate all tilings in the symmetry orbit of the given tiling."""
    symmetries = get_box_symmetries_5x5x9()
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


def enumerate_paths_excluding_orbit(templates, target_depth, known_orbit, max_paths=100):
    """
    Enumerate Macro paths, excluding those that produce tilings in the known orbit.
    
    Returns the first path that produces a tiling NOT in the known orbit.
    """
    paths_found = []
    
    def dfs(state, depth, path):
        if len(paths_found) >= max_paths:
            return
        
        if depth == target_depth:
            if state == 0:
                # Reconstruct the tiling
                placements = reconstruct_placements_from_path(path, templates)
                
                if placements is None:
                    return
                
                canonical = canonicalize_tiling(placements)
                
                # Check if this tiling is in the known orbit
                if canonical not in known_orbit:
                    paths_found.append((path, placements))
                    return
            
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
    return paths_found


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×9 - SECOND TILING SEARCH")
    print("=" * 70)
    print()
    
    # Load known solution
    print("Loading known 5×5×9 V tiling...")
    solution_file = Path(__file__).resolve().parent.parent / "data" / "solutions_fast_v_5x5x9.dat"
    known_placements = parse_solution_file(solution_file)
    print(f"  Loaded {len(known_placements)} placements")
    print()
    
    # Generate symmetry orbit
    print("Generating symmetry orbit...")
    box_size = (5, 5, 9)
    known_orbit = generate_symmetry_orbit(known_placements, box_size)
    print(f"  Orbit size: {len(known_orbit)}")
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Search for second tiling
    print("Searching for second inequivalent tiling...")
    print("  (This may take a while...)")
    start_time = time.time()
    
    # Try to find just one second tiling
    second_tilings = enumerate_paths_excluding_orbit(
        templates, 9, known_orbit, max_paths=1
    )
    
    elapsed = time.time() - start_time
    print(f"  Search completed in {elapsed:.1f}s")
    print()
    
    # Results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if len(second_tilings) > 0:
        path, placements = second_tilings[0]
        print(f"✓ SECOND TILING FOUND")
        print(f"  Macro path length: {len(path)}")
        print(f"  Number of placements: {len(placements)}")
        print()
        print("Result: NON-UNIQUE")
        print()
        print("The 5×5×9 V tiling is NOT unique up to box symmetry.")
        print("At least two symmetry-inequivalent tilings exist.")
    else:
        print("✗ NO SECOND TILING FOUND")
        print()
        print("Result: UNDETERMINED")
        print()
        print("The search did not find a second tiling within the time limit.")
        print("This does NOT prove uniqueness.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
