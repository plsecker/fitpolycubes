#!/usr/bin/env python3
"""
Simple debug: understand the predecessor structure for V 5×5×6.

This script:
1. Finds a few complete Macro paths from 0 to 0 at depth 6
2. Extracts the state immediately before the final transition to 0
3. Analyzes the structure of these predecessor states
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


def explore_forward(state: int, templates: dict) -> set:
    """
    Explore forward from a state to find all reachable post-shift states.
    """
    successors = set()
    seen = {state}
    queue = deque([state])
    
    while queue:
        s = queue.popleft()
        
        # Check if layer 0 is full
        if layer_mask(s, 0) == WORD_MASK:
            # Shift and add to successors
            successors.add(shift_state(s))
            continue
        
        # Find first empty cell in layer 0
        target = first_empty(layer_mask(s, 0))
        
        # Try all templates for this target
        for template in templates[target]:
            nxt = apply_template(s, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append(nxt)
    
    return successors


def find_first_n_paths(templates: dict, n: int = 5) -> list:
    """
    Find first n complete Macro paths from 0 to 0 at depth 6.
    """
    paths = []
    
    def dfs(state: int, depth: int, path: list):
        if len(paths) >= n:
            return
        
        if depth == 6:
            if state == 0:
                paths.append(list(path))
            return
        
        # Find successors
        successors = explore_forward(state, templates)
        
        for succ in sorted(successors):  # Sort for determinism
            dfs(succ, depth + 1, path + [succ])
    
    dfs(0, 0, [0])
    return paths


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - SIMPLE PREDECESSOR DEBUG")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Find first 5 paths
    print("Finding first 5 Macro paths at depth 6...")
    start_time = time.time()
    paths = find_first_n_paths(templates, 5)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    # Analyze each path
    for i, path in enumerate(paths):
        print(f"Path {i+1}: {path}")
        
        # Extract the state before the final transition to 0
        if len(path) >= 2:
            predecessor = path[-2]
            print(f"  Predecessor of 0: {predecessor}")
            print(f"    layer0: {layer_mask(predecessor, 0):025b}")
            print(f"    layer1: {layer_mask(predecessor, 1):025b}")
            print(f"    layer2: {layer_mask(predecessor, 2):025b}")
            
            # Verify that this is indeed a predecessor
            successors = explore_forward(predecessor, templates)
            if 0 in successors:
                print(f"    ✓ Verified: 0 is in successors")
            else:
                print(f"    ✗ ERROR: 0 is NOT in successors")
                print(f"    Successors: {successors}")
        print()
    
    # Now let's understand what a predecessor of 0 should look like
    print("=" * 70)
    print("UNDERSTANDING PREDECESSOR STRUCTURE")
    print("=" * 70)
    print()
    
    print("For a state P to be a predecessor of 0:")
    print("  1. P must be able to reach a pre-shift state by applying templates")
    print("  2. The pre-shift state must have:")
    print("     - layer0 = WORD_MASK (full)")
    print("     - layer1 = 0")
    print("     - layer2 = 0")
    print("  3. After shifting, the result is 0")
    print()
    
    print("So the pre-shift state is: pack_layers([WORD_MASK, 0, 0])")
    pre_shift = (WORD_MASK) | (0 << NCELLS) | (0 << (2 * NCELLS))
    print(f"  Pre-shift state: {pre_shift}")
    print(f"    layer0: {layer_mask(pre_shift, 0):025b}")
    print(f"    layer1: {layer_mask(pre_shift, 1):025b}")
    print(f"    layer2: {layer_mask(pre_shift, 2):025b}")
    print()
    
    print("A predecessor P must be able to reach this pre-shift state.")
    print("This means:")
    print("  - P.layer0 is a subset of WORD_MASK")
    print("  - P.layer1 is a subset of 0 (i.e., P.layer1 = 0)")
    print("  - P.layer2 is a subset of 0 (i.e., P.layer2 = 0)")
    print("  - After applying templates, P.layer0 becomes WORD_MASK")
    print()
    
    print("So predecessors of 0 must have:")
    print("  - layer1 = 0")
    print("  - layer2 = 0")
    print("  - layer0 is not full (otherwise it would have already shifted)")
    print()
    
    # Verify this with the examples
    print("Verifying with examples:")
    for i, path in enumerate(paths):
        if len(path) >= 2:
            predecessor = path[-2]
            l0 = layer_mask(predecessor, 0)
            l1 = layer_mask(predecessor, 1)
            l2 = layer_mask(predecessor, 2)
            
            print(f"  Path {i+1} predecessor:")
            print(f"    layer0: {l0:025b} ({l0})")
            print(f"    layer1: {l1:025b} ({l1})")
            print(f"    layer2: {l2:025b} ({l2})")
            
            if l1 == 0 and l2 == 0:
                print(f"    ✓ Matches expected structure")
            else:
                print(f"    ✗ Does NOT match expected structure")
            print()
    
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    print("The predecessor function should find states P where:")
    print("  - layer1 = 0")
    print("  - layer2 = 0")
    print("  - layer0 is not full")
    print("  - P can reach the pre-shift state by applying templates")
    print()
    print("The current implementation is looking for the wrong structure.")
    print()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
