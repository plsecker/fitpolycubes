#!/usr/bin/env python3
"""
Quick check: do the first 20 paths produce duplicate tilings?
"""

import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5x6_quick_diag import find_first_n_paths, reconstruct_tiling, canonicalize_tiling


def main():
    print("=" * 70)
    print("QUICK CHECK: FIRST 20 PATHS → DUPLICATES?")
    print("=" * 70)
    print()
    
    # Build templates
    from solvers.v_5x5_macro import build_templates
    templates, _, _, _, _ = build_templates()
    
    # Find first 20 paths
    print("Finding first 20 Macro paths...")
    start_time = time.time()
    paths = find_first_n_paths(20, templates)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    # Reconstruct tilings
    print("Reconstructing tilings...")
    start_time = time.time()
    tilings = []
    
    for i, path in enumerate(paths):
        tiling = reconstruct_tiling(path, templates)
        if tiling is not None:
            tilings.append((i, tiling))
    
    elapsed = time.time() - start_time
    print(f"  Reconstructed {len(tilings)} tilings in {elapsed:.1f}s")
    print()
    
    # Canonicalize
    print("Canonicalizing tilings...")
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
    print(f"Macro paths checked: {len(paths)}")
    print(f"Distinct raw tilings: {len(raw_tilings)}")
    print()
    
    if len(raw_tilings) == len(paths):
        print("✓ NO DUPLICATES: Each path produces a distinct tiling")
        print()
        print("This means:")
        print("  - The 80 Macro paths likely produce 80 distinct tilings")
        print("  - The '9 tilings' must refer to symmetry orbits")
        print("  - We need to apply symmetry reduction to get 9 orbits")
    else:
        print("✗ DUPLICATES FOUND")
        print()
        print("Multiplicity distribution:")
        multiplicity_dist = {}
        for canonical, path_indices in raw_tilings.items():
            mult = len(path_indices)
            if mult not in multiplicity_dist:
                multiplicity_dist[mult] = 0
            multiplicity_dist[mult] += 1
        
        for mult in sorted(multiplicity_dist.keys()):
            count = multiplicity_dist[mult]
            print(f"  {mult} paths per tiling: {count} tilings")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
