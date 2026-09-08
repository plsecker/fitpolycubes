#!/usr/bin/env python3
"""
Check if all 80 paths produce distinct tilings by sampling.
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
from solvers.v_5x5x6_quick_diag import reconstruct_tiling, canonicalize_tiling


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
    print("SAMPLE CHECK: DO ALL 80 PATHS PRODUCE DISTINCT TILINGS?")
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
    
    # Sample paths: first 10, middle 10, last 10
    sample_indices = list(range(10)) + list(range(35, 45)) + list(range(70, 80))
    
    print(f"Sampling {len(sample_indices)} paths: indices {sample_indices}")
    print()
    
    # Reconstruct tilings for sample
    print("Reconstructing tilings for sample...")
    start_time = time.time()
    tilings = {}
    
    for i in sample_indices:
        path = paths[i]
        tiling = reconstruct_tiling(path, templates)
        if tiling is not None:
            tilings[i] = tiling
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Canonicalize
    print("Canonicalizing tilings...")
    start_time = time.time()
    raw_tilings = {}
    
    for i, tiling in tilings.items():
        canonical = canonicalize_tiling(tiling)
        
        if canonical not in raw_tilings:
            raw_tilings[canonical] = []
        
        raw_tilings[canonical].append(i)
    
    elapsed = time.time() - start_time
    print(f"  Canonicalized in {elapsed:.1f}s")
    print(f"  Distinct raw tilings in sample: {len(raw_tilings)}")
    print()
    
    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Sample size: {len(sample_indices)} paths")
    print(f"Distinct raw tilings in sample: {len(raw_tilings)}")
    print()
    
    if len(raw_tilings) == len(sample_indices):
        print("✓ NO DUPLICATES IN SAMPLE")
        print()
        print("This strongly suggests that all 80 paths produce distinct tilings.")
        print()
        print("Therefore:")
        print("  - 80 Macro paths → 80 distinct raw tilings")
        print("  - The '9 tilings' refers to symmetry orbits")
        print("  - We need to apply symmetry reduction to all 80 tilings")
        print("  - Expected result: 9 symmetry orbits")
    else:
        print("✗ DUPLICATES FOUND IN SAMPLE")
        print()
        print("This suggests that some Macro paths produce the same tiling.")
        print()
        print("Multiplicity distribution:")
        for canonical, path_indices in raw_tilings.items():
            print(f"  {len(path_indices)} paths: {path_indices}")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
