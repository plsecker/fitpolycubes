#!/usr/bin/env python3
"""
Calibration: V pentacube in 5×5×6 (known 9 tilings).

This script counts Macro return paths at depth 6 and determines
the relationship between Macro paths and tilings.
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


def count_macro_paths_depth_6(templates, verbose=True):
    """
    Count Macro return paths from state 0 to state 0 at exactly depth 6.
    Uses dynamic programming to track path counts.
    """
    if verbose:
        print("Counting Macro return paths at depth 6...")
        print()
    
    # dp[state] = number of paths from state 0 to this state
    dp = {0: 1}
    
    for depth in range(1, 7):
        if verbose:
            print(f"Depth {depth}:")
            print(f"  States at previous depth: {len(dp):,}")
        
        dp_next = {}
        total_transitions = 0
        
        for state, count in dp.items():
            successors = explore_to_shift(state, templates)
            
            for succ in successors:
                if succ in dp_next:
                    dp_next[succ] += count
                else:
                    dp_next[succ] = count
                total_transitions += 1
        
        if verbose:
            print(f"  Total transitions: {total_transitions:,}")
            print(f"  States at this depth: {len(dp_next):,}")
            
            if 0 in dp_next:
                print(f"  *** Paths to state 0: {dp_next[0]:,}")
        
        dp = dp_next
        
        if verbose:
            print()
    
    # Return count of paths to state 0 at depth 6
    path_count = dp.get(0, 0)
    
    if verbose:
        print(f"Complete Macro paths from 0 to 0 at depth 6: {path_count:,}")
    
    return path_count, dp


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - MACRO CALIBRATION")
    print("=" * 70)
    print()
    print("Known result: 9 tilings (Sillke 1993)")
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, concrete_count, total_templates = build_templates()
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Total templates: {total_templates}")
    print()
    
    # Count Macro return paths at depth 6
    start_time = time.time()
    path_count, final_dp = count_macro_paths_depth_6(templates, verbose=True)
    elapsed = time.time() - start_time
    
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Macro return paths at depth 6: {path_count:,}")
    print(f"Known tilings: 9")
    print(f"Elapsed time: {elapsed:.1f}s")
    print()
    
    if path_count == 9:
        print("✓ PERFECT MATCH: Macro paths = tilings")
        print("  Each Macro path corresponds to exactly one tiling")
        result = "MATCH"
    elif path_count < 9:
        print(f"✗ UNDERCOUNT: Macro paths ({path_count}) < tilings (9)")
        print("  Each Macro path may correspond to multiple tilings")
        result = "UNDERCOUNT"
    else:
        print(f"✗ OVERCOUNT: Macro paths ({path_count}) > tilings (9)")
        print("  Something is wrong with the counting")
        result = "OVERCOUNT"
    
    # Save results
    output = {
        "piece": "V",
        "box": [5, 5, 6],
        "macro_paths": path_count,
        "known_tilings": 9,
        "result": result,
        "elapsed_seconds": elapsed,
    }
    
    output_file = Path("/tmp/v_5x5x6_calibration.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
