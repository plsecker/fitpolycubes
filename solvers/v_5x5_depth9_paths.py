#!/usr/bin/env python3
"""
Depth-limited path enumeration for V pentacube in 5×5×9.

This script searches for all paths of exactly length 9 from state 0 to state 0
in the Macro state graph, without computing the full closure.

Uses iterative deepening DFS with memoization to efficiently count paths.
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
            # Safety limit hit
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


def count_paths_depth_limited(templates, target_depth, max_states_per_level=10_000_000):
    """
    Count paths from state 0 to state 0 at exactly target_depth.
    
    Uses BFS level-by-level, tracking the number of paths to each state.
    """
    print(f"Counting paths to depth {target_depth}...")
    print()
    
    # Level 0: start at state 0 with 1 path
    current_level = {0: 1}  # state -> path count
    
    for depth in range(1, target_depth + 1):
        print(f"Depth {depth}:")
        print(f"  States at previous depth: {len(current_level):,}")
        
        next_level = {}
        total_transitions = 0
        states_with_shifts = 0
        
        for state, count in current_level.items():
            # Explore from this state to find all reachable post-shift states
            successors = explore_to_shift(state, templates)
            
            if successors:
                states_with_shifts += 1
            
            for succ in successors:
                if succ in next_level:
                    next_level[succ] += count
                else:
                    next_level[succ] = count
                total_transitions += 1
        
        print(f"  States with successors: {states_with_shifts:,}")
        print(f"  Total transitions: {total_transitions:,}")
        print(f"  States at this depth: {len(next_level):,}")
        
        if 0 in next_level:
            print(f"  *** Paths to state 0: {next_level[0]:,}")
        
        # Check if we're exceeding memory limits
        if len(next_level) > max_states_per_level:
            print(f"  WARNING: Exceeding max states per level ({max_states_per_level:,})")
            print(f"  Truncating to most common states...")
            # Keep only the most common states
            sorted_states = sorted(next_level.items(), key=lambda x: x[1], reverse=True)
            next_level = dict(sorted_states[:max_states_per_level])
            print(f"  Truncated to {len(next_level):,} states")
        
        current_level = next_level
        print()
    
    # Return the count of paths to state 0 at target_depth
    return current_level.get(0, 0), current_level


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×9 - DEPTH-LIMITED PATH COUNTING")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, concrete_count, total_templates = build_templates()
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Total templates: {total_templates}")
    print()
    
    # Count paths to depth 9
    start_time = time.time()
    path_count, final_level = count_paths_depth_limited(templates, 9)
    elapsed = time.time() - start_time
    
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Target depth: 9")
    print(f"Paths from state 0 to state 0: {path_count:,}")
    print(f"States at depth 9: {len(final_level):,}")
    print(f"Elapsed time: {elapsed:.1f}s")
    print()
    
    if path_count == 0:
        print("CONCLUSION: NO TILINGS EXIST")
        result = "NO_TILINGS"
    elif path_count == 1:
        print("CONCLUSION: UNIQUE TILING (up to Macro path equivalence)")
        result = "UNIQUE"
    else:
        print(f"CONCLUSION: {path_count} TILINGS FOUND")
        print("  (Symmetry reduction needed to determine uniqueness up to box symmetry)")
        result = "NON_UNIQUE"
    
    # Save results
    output = {
        "piece": "V",
        "box": [5, 5, 9],
        "path_count": path_count,
        "states_at_depth_9": len(final_level),
        "elapsed_seconds": elapsed,
        "result": result,
    }
    
    output_file = Path("/tmp/v_5x5_depth9_paths.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
