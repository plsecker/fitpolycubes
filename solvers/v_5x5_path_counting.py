#!/usr/bin/env python3
"""
Count Macro paths from state 0 to state 0 at depth 6 using dynamic programming.

This implements path counting through the forward sets F[0] through F[6].
"""

import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK
)


def compute_forward_sets_with_counts(templates, target_depth):
    """
    Compute forward sets F[0] through F[target_depth] and track path counts.
    
    Returns:
        F: list of sets, F[d] = set of states at depth d
        counts: list of dicts, counts[d][state] = number of paths to state at depth d
    """
    F = [set() for _ in range(target_depth + 1)]
    counts = [{} for _ in range(target_depth + 1)]
    
    # Initialize F[0] and counts[0]
    F[0] = {0}
    counts[0] = {0: 1}
    
    for d in range(target_depth):
        print(f"Computing F[{d+1}] and counts[{d+1}] from F[{d}] ({len(F[d])} states)...")
        start_time = time.time()
        
        F_next = set()
        counts_next = {}
        
        for state in F[d]:
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
            
            # Add successors to F_next and update counts
            state_count = counts[d][state]
            for succ in successors:
                F_next.add(succ)
                counts_next[succ] = counts_next.get(succ, 0) + state_count
        
        F[d+1] = F_next
        counts[d+1] = counts_next
        
        elapsed = time.time() - start_time
        print(f"  |F[{d+1}]| = {len(F_next)} states ({elapsed:.1f}s)")
    
    return F, counts


def main():
    print("=" * 70)
    print("V PENTACUBE MACRO PATH COUNTING")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Compute forward sets with path counts
    target_depth = 6
    F, counts = compute_forward_sets_with_counts(templates, target_depth)
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    # Print forward set sizes
    print("Forward set sizes:")
    for d in range(target_depth + 1):
        print(f"  F[{d}] = {len(F[d]):,}")
    
    print()
    
    # Check if state 0 is in F[6]
    if 0 in F[target_depth]:
        path_count = counts[target_depth][0]
        print(f"✓ State 0 is in F[{target_depth}]")
        print(f"  Number of paths from 0 to 0 at depth {target_depth}: {path_count:,}")
        print()
        
        # Calibration check
        print("Calibration check:")
        print(f"  Expected: 80 paths")
        print(f"  Got: {path_count} paths")
        if path_count == 80:
            print("  ✓ MATCH")
        else:
            print("  ✗ MISMATCH")
    else:
        print(f"✗ State 0 is NOT in F[{target_depth}]")
        print("  No complete Macro paths exist")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
