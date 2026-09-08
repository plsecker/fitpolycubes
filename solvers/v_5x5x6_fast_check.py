#!/usr/bin/env python3
"""
Fast check: do the 80 paths produce duplicate tilings?
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


def find_all_paths_fast(templates):
    """Find all 80 Macro return paths (optimized)."""
    paths = []
    
    # Use iterative approach instead of recursive DFS
    # Start with state 0 at depth 0
    current_level = {0: [[0]]}  # state -> list of paths to that state
    
    for depth in range(6):
        next_level = {}
        
        for state, paths_to_state in current_level.items():
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
            
            # Extend paths to successors
            for succ in successors:
                if succ not in next_level:
                    next_level[succ] = []
                
                for path in paths_to_state:
                    next_level[succ].append(path + [succ])
        
        current_level = next_level
        
        # Count paths at this depth
        total_paths = sum(len(paths) for paths in current_level.values())
        print(f"  Depth {depth+1}: {len(current_level)} states, {total_paths} paths")
    
    # Collect all paths that end at state 0
    if 0 in current_level:
        paths = current_level[0]
    
    return paths


def main():
    print("=" * 70)
    print("FAST CHECK: 80 PATHS → DUPLICATE TILINGS?")
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
    paths = find_all_paths_fast(templates)
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
            tilings.append((i, tiling))
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Canonicalize without symmetry
    print("Canonicalizing tilings (without symmetry)...")
    start_time = time.time()
    raw_tilings = {}
    
    for i, tiling in tilings:
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in raw_tilings:
            raw_tilings[canonical] = []
        
        raw_tilings[canonical].append(i)
    
    elapsed = time.time() - start_time
    print(f"  Canonicalized in {elapsed:.1f}s")
    print(f"  Distinct raw tilings: {len(raw_tilings)}")
    print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Macro return paths: {len(paths)}")
    print(f"Distinct raw tilings: {len(raw_tilings)}")
    print(f"Known tilings (Sillke 1993): 9")
    print()
    
    # Multiplicity analysis
    if len(raw_tilings) > 0:
        print("Multiplicity analysis:")
        print(f"  Paths per raw tiling: {len(paths) / len(raw_tilings):.2f}")
        print()
        
        # Show multiplicity distribution
        multiplicity_dist = {}
        for canonical, path_indices in raw_tilings.items():
            mult = len(path_indices)
            if mult not in multiplicity_dist:
                multiplicity_dist[mult] = 0
            multiplicity_dist[mult] += 1
        
        print("Multiplicity distribution:")
        for mult in sorted(multiplicity_dist.keys()):
            count = multiplicity_dist[mult]
            print(f"  {mult} paths per tiling: {count} tilings")
        print()
    
    # Check if we match the "9"
    if len(raw_tilings) == 9:
        print("✓ MATCH: Raw tilings = 9")
        print("  The '9 tilings' refers to raw tilings")
        print("  Multiple Macro paths produce the same tiling")
    else:
        print("✗ NO MATCH")
        print(f"  Expected 9 raw tilings, got {len(raw_tilings)}")
        print()
        print("  This means either:")
        print("  1. The '9' refers to symmetry orbits (need to apply symmetry)")
        print("  2. The Macro approach is overcounting")
        print("  3. There's an issue with tiling reconstruction")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
