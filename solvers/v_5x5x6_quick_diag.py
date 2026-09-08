#!/usr/bin/env python3
"""
Quick diagnostic: understand the 80→9 discrepancy for V in 5×5×6.

This script:
1. Finds a few Macro paths
2. Reconstructs tilings from them
3. Checks if they're actually different tilings or the same tiling
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
    """Canonicalize a tiling."""
    sorted_placements = [tuple(sorted(p)) for p in placements]
    sorted_placements.sort()
    return tuple(sorted_placements)


def find_first_n_paths(n, templates):
    """Find first n Macro return paths."""
    paths = []
    
    def dfs(state, depth, path):
        if len(paths) >= n:
            return
        
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
        
        for succ in sorted(successors):  # Sort for determinism
            dfs(succ, depth + 1, path + [succ])
    
    dfs(0, 0, [0])
    return paths


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - QUICK DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Find first 10 paths
    print("Finding first 10 Macro paths...")
    start_time = time.time()
    paths = find_first_n_paths(10, templates)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    # Reconstruct tilings
    print("Reconstructing tilings...")
    tilings = []
    
    for i, path in enumerate(paths):
        print(f"  Path {i+1}: {path}")
        tiling = reconstruct_tiling(path, templates)
        
        if tiling is None:
            print(f"    ✗ Failed to reconstruct")
        else:
            print(f"    ✓ Reconstructed {len(tiling)} placements")
            tilings.append(tiling)
    
    print()
    
    # Canonicalize and check for duplicates
    print("Checking for duplicate tilings...")
    canonical_tilings = {}
    
    for i, tiling in enumerate(tilings):
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in canonical_tilings:
            canonical_tilings[canonical] = []
        
        canonical_tilings[canonical].append(i)
    
    print(f"  Distinct tilings: {len(canonical_tilings)}")
    print()
    
    for canonical, path_indices in canonical_tilings.items():
        print(f"  Tiling from paths: {path_indices}")
    
    print()
    print("=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
