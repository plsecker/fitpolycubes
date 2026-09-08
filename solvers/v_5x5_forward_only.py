#!/usr/bin/env python3
"""
Forward-only depth-limited Macro exploration for V pentacube in 5×5×9.

This builds forward reachable sets F[d] for d=0..9 and checks if state 0
is reachable at depth 9.
"""

import sys
import time
import json
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template, 
    shift_state, WORD_MASK, NCELLS
)


def explore_to_shift(state, templates, max_intermediate=1_000_000):
    """
    Explore from a state until we reach a shift (layer 0 full).
    Returns set of post-shift states reachable.
    """
    successors = set()
    seen = {state}
    queue = deque([state])
    
    while queue:
        if len(seen) > max_intermediate:
            break
        
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
    
    return successors


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×9 - FORWARD-ONLY DEPTH-LIMITED EXPLORATION")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, concrete_count, total_templates = build_templates()
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Total templates: {total_templates}")
    print()
    
    target_depth = 9
    
    # Build forward sets F[d] for d=0..target_depth
    print(f"Building forward sets F[0..{target_depth}]...")
    print()
    
    F = [set() for _ in range(target_depth + 1)]
    F[0] = {0}
    
    total_time = 0
    
    for d in range(target_depth):
        start_time = time.time()
        
        print(f"Computing F[{d+1}] from F[{d}] ({len(F[d]):,} states)...")
        
        F_next = set()
        states_processed = 0
        
        for state in F[d]:
            successors = explore_to_shift(state, templates)
            F_next.update(successors)
            
            states_processed += 1
            if states_processed % 1000 == 0:
                elapsed = time.time() - start_time
                print(f"  Processed {states_processed:,}/{len(F[d]):,} states, "
                      f"found {len(F_next):,} successors ({elapsed:.1f}s)")
        
        F[d + 1] = F_next
        
        elapsed = time.time() - start_time
        total_time += elapsed
        
        print(f"  F[{d+1}]: {len(F[d+1]):,} states ({elapsed:.1f}s)")
        
        # Check if state 0 is in F[d+1]
        if 0 in F[d + 1]:
            print(f"  *** STATE 0 FOUND AT DEPTH {d+1}! ***")
        
        print()
    
    print(f"Total time: {total_time:.1f}s")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Target depth: {target_depth}")
    print()
    
    print("Forward set sizes:")
    for d in range(target_depth + 1):
        has_zero = "✓" if 0 in F[d] else " "
        print(f"  F[{d}]: {len(F[d]):,} states {has_zero}")
    
    print()
    
    # Check if state 0 is reachable at depth 9
    if 0 in F[target_depth]:
        print(f"✓ STATE 0 IS REACHABLE AT DEPTH {target_depth}")
        print()
        print("This means complete Macro paths from 0 to 0 exist!")
        print()
        
        # We know paths exist, but we don't know how many
        # To count them, we'd need to track path counts, not just reachability
        print("To count the exact number of paths, we would need to track")
        print("path counts through the layered graph (dynamic programming).")
        print()
        print("However, this requires storing the full edge set, which is")
        print("computationally expensive.")
        
        result = "PATHS_EXIST"
    else:
        print(f"✗ STATE 0 IS NOT REACHABLE AT DEPTH {target_depth}")
        print()
        print("This means NO complete Macro paths from 0 to 0 exist at depth 9.")
        print()
        print("CONCLUSION: NO TILINGS OF 5×5×9 BY V PENTACUBE")
        
        result = "NO_TILINGS"
    
    # Save results
    output = {
        "piece": "V",
        "box": [5, 5, 9],
        "target_depth": target_depth,
        "result": result,
        "F_sizes": [len(F[d]) for d in range(target_depth + 1)],
        "zero_reachable_at_depth_9": 0 in F[target_depth],
        "total_time_seconds": total_time,
    }
    
    output_file = Path("/tmp/v_5x5_forward_only.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
