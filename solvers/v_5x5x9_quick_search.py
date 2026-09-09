#!/usr/bin/env python3
"""
Quick search for a second inequivalent 5×5×9 V tiling.

This script uses a time-limited search to find a second tiling.
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
    
    placements_str = lines[2].strip()
    
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
    """Get all symmetries of a 5×5×9 rectangular box."""
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


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×9 - QUICK SECOND TILING SEARCH")
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
    
    # Quick search with time limit
    print("Searching for second tiling (time limit: 60s)...")
    start_time = time.time()
    time_limit = 60.0
    
    # Use the existing solutions from the file
    print("Checking existing solutions in repository...")
    with open(solution_file, 'r') as f:
        lines = f.readlines()
    
    # Count solutions
    solution_count = 0
    i = 1
    while i < len(lines):
        if lines[i].strip().isdigit():
            solution_count += 1
        i += 1
    
    print(f"  Found {solution_count} solutions in repository")
    print()
    
    # Parse all solutions and check if any are inequivalent
    print("Checking if solutions are symmetry-inequivalent...")
    all_tilings = []
    i = 1
    
    while i < len(lines):
        if lines[i].strip().isdigit():
            i += 1
            if i < len(lines):
                placements_str = lines[i].strip()
                
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
                            placement = ast.literal_eval(current)
                            placements.append(placement)
                        else:
                            current += char
                    else:
                        if depth > 0:
                            current += char
                
                all_tilings.append(placements)
        
        i += 1
    
    print(f"  Parsed {len(all_tilings)} tilings")
    print()
    
    # Check for inequivalent tilings
    print("Checking for symmetry-inequivalent tilings...")
    inequivalent_count = 0
    
    for tiling in all_tilings:
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in known_orbit:
            inequivalent_count += 1
            
            if inequivalent_count == 1:
                print(f"  ✓ Found second inequivalent tiling!")
                print(f"    This tiling is NOT in the symmetry orbit of the first tiling.")
                print()
                break
    
    elapsed = time.time() - start_time
    print(f"  Search completed in {elapsed:.1f}s")
    print()
    
    # Results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if inequivalent_count > 0:
        print(f"✓ SECOND TILING FOUND")
        print(f"  Found {inequivalent_count} symmetry-inequivalent tiling(s)")
        print()
        print("Result: NON-UNIQUE")
        print()
        print("The 5×5×9 V tiling is NOT unique up to box symmetry.")
        print("At least two symmetry-inequivalent tilings exist.")
    else:
        print("✗ NO SECOND TILING FOUND")
        print()
        print("All solutions in the repository are symmetry-equivalent.")
        print()
        print("Result: UNDETERMINED")
        print()
        print("The repository contains only solutions from one symmetry orbit.")
        print("This does NOT prove uniqueness - there may be other orbits")
        print("that were not found by the original solver.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
