#!/usr/bin/env python3
"""
Complete analysis: 80 paths → distinct tilings → symmetry orbits
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


def template_to_placements(template, layer_offset):
    """Convert a template to concrete cell coordinates."""
    cells = []
    
    for layer in range(3):
        layer_mask_val = (template >> (layer * NCELLS)) & WORD_MASK
        
        for cell_id in range(NCELLS):
            if layer_mask_val & (1 << cell_id):
                x = cell_id % 5
                y = cell_id // 5
                z = layer_offset + layer
                cells.append((x, y, z))
    
    return cells


def find_path_to_successor(start_state, target_successor, templates, max_steps=50):
    """Find a sequence of templates that transitions from start_state to target_successor."""
    queue = deque([(start_state, [])])
    seen = {start_state}
    
    while queue:
        state, template_seq = queue.popleft()
        
        if len(template_seq) > max_steps:
            continue
        
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


def reconstruct_tiling(macro_path, templates):
    """Reconstruct a tiling from a Macro path."""
    all_placements = []
    
    for d in range(len(macro_path) - 1):
        start_state = macro_path[d]
        end_state = macro_path[d + 1]
        
        template_seq = find_path_to_successor(start_state, end_state, templates)
        
        if template_seq is None:
            return None
        
        layer_offset = d
        
        for template in template_seq:
            cells = template_to_placements(template, layer_offset)
            if len(cells) == 5:
                all_placements.append(cells)
    
    return all_placements


def canonicalize_tiling(placements):
    """Canonicalize a tiling (without symmetry)."""
    sorted_placements = [tuple(sorted(p)) for p in placements]
    sorted_placements.sort()
    return tuple(sorted_placements)


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


def find_all_paths(templates):
    """Find all 80 Macro return paths."""
    paths = []
    
    def dfs(state, depth, path):
        if depth == 6:
            if state == 0:
                paths.append(list(path))
            return
        
        # Find successors
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
        
        for succ in sorted(successors):
            dfs(succ, depth + 1, path + [succ])
    
    dfs(0, 0, [0])
    return paths


def main():
    print("=" * 70)
    print("COMPLETE ANALYSIS: 80 PATHS → TILINGS → SYMMETRY ORBITS")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Find all 80 paths
    print("Finding all 80 Macro paths...")
    start_time = time.time()
    paths = find_all_paths(templates)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    # Reconstruct all tilings
    print("Reconstructing all tilings...")
    start_time = time.time()
    tilings = []
    
    for i, path in enumerate(paths):
        if (i + 1) % 10 == 0:
            print(f"  Reconstructing tiling {i+1}/{len(paths)}...")
        
        tiling = reconstruct_tiling(path, templates)
        if tiling is not None:
            tilings.append((i, path, tiling))
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Canonicalize without symmetry
    print("Canonicalizing tilings (without symmetry)...")
    start_time = time.time()
    raw_tilings = {}
    
    for i, path, tiling in tilings:
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in raw_tilings:
            raw_tilings[canonical] = []
        
        raw_tilings[canonical].append(i)
    
    elapsed = time.time() - start_time
    print(f"  Canonicalized in {elapsed:.1f}s")
    print(f"  Distinct raw tilings: {len(raw_tilings)}")
    print()
    
    # Apply symmetry reduction
    print("Applying symmetry reduction...")
    start_time = time.time()
    symmetry_orbits = {}
    box_dims = (5, 5, 6)
    
    orbit_count = 0
    for canonical, path_indices in raw_tilings.items():
        if (orbit_count + 1) % 10 == 0:
            print(f"  Processing orbit {orbit_count+1}/{len(raw_tilings)}...")
        
        # Convert canonical back to placements
        placements = [list(p) for p in canonical]
        
        # Find canonical form under symmetry
        sym_canonical = canonicalize_under_symmetry(placements, box_dims)
        
        if sym_canonical not in symmetry_orbits:
            symmetry_orbits[sym_canonical] = []
        
        symmetry_orbits[sym_canonical].extend(path_indices)
        orbit_count += 1
    
    elapsed = time.time() - start_time
    print(f"  Symmetry reduction completed in {elapsed:.1f}s")
    print(f"  Symmetry orbits: {len(symmetry_orbits)}")
    print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Macro return paths: {len(paths)}")
    print(f"Distinct raw tilings: {len(raw_tilings)}")
    print(f"Symmetry orbits: {len(symmetry_orbits)}")
    print(f"Known tilings (Sillke 1993): 9")
    print()
    
    # Multiplicity analysis
    print("Multiplicity analysis:")
    print(f"  Paths per raw tiling: {len(paths) / len(raw_tilings):.2f}")
    print(f"  Raw tilings per orbit: {len(raw_tilings) / len(symmetry_orbits):.2f}")
    print()
    
    # Check if we match the "9"
    if len(symmetry_orbits) == 9:
        print("✓ MATCH: Symmetry orbits = 9")
        print("  The '9 tilings' refers to symmetry-inequivalent tilings")
    elif len(raw_tilings) == 9:
        print("✓ MATCH: Raw tilings = 9")
        print("  The '9 tilings' refers to raw tilings")
    else:
        print("✗ NO MATCH")
        print(f"  Expected 9, got {len(raw_tilings)} raw or {len(symmetry_orbits)} orbits")
    
    print()
    
    # Show orbit sizes
    print("Symmetry orbit sizes:")
    for i, (canonical, path_indices) in enumerate(sorted(symmetry_orbits.items(), key=lambda x: len(x[1]), reverse=True)):
        print(f"  Orbit {i+1}: {len(path_indices)} paths")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
