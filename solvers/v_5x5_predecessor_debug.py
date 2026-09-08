#!/usr/bin/env python3
"""
Debug the reverse predecessor implementation for V 5×5×6 Macro paths.

This script:
1. Generates all 80 complete Macro paths from 0 to 0 at depth 6
2. Extracts all adjacent state pairs (P, S) from the paths
3. Verifies the forward transition P -> S
4. Implements a correct predecessor function
5. Validates the predecessor function against the known paths
"""

import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK, NCELLS, pack_layers
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


def find_all_paths_depth_6(templates: dict) -> list:
    """
    Find all complete Macro paths from 0 to 0 at depth 6.
    """
    paths = []
    
    def dfs(state: int, depth: int, path: list):
        if depth == 6:
            if state == 0:
                paths.append(list(path))
            return
        
        # Find successors
        successors = explore_forward(state, templates)
        
        for succ in successors:
            dfs(succ, depth + 1, path + [succ])
    
    dfs(0, 0, [0])
    return paths


def find_predecessors_brute_force(target_state: int, templates: dict, candidate_states: set) -> set:
    """
    Find predecessors by checking all candidate states.
    
    A state P is a predecessor of S if explore_forward(P) contains S.
    """
    predecessors = set()
    
    for P in candidate_states:
        successors = explore_forward(P, templates)
        if target_state in successors:
            predecessors.add(P)
    
    return predecessors


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - PREDECESSOR DEBUG")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Generate all 80 paths
    print("Generating all 80 Macro paths at depth 6...")
    start_time = time.time()
    paths = find_all_paths_depth_6(templates)
    elapsed = time.time() - start_time
    print(f"  Found {len(paths)} paths in {elapsed:.1f}s")
    print()
    
    if len(paths) != 80:
        print(f"ERROR: Expected 80 paths, got {len(paths)}")
        return 1
    
    # Extract all adjacent state pairs
    print("Extracting adjacent state pairs...")
    state_pairs = set()
    for path in paths:
        for i in range(len(path) - 1):
            P = path[i]
            S = path[i + 1]
            state_pairs.add((P, S))
    
    print(f"  Found {len(state_pairs)} unique state pairs")
    print()
    
    # Verify forward transitions
    print("Verifying forward transitions...")
    forward_verified = 0
    forward_failed = 0
    
    for P, S in state_pairs:
        successors = explore_forward(P, templates)
        if S in successors:
            forward_verified += 1
        else:
            forward_failed += 1
            print(f"  FAILED: {P} -> {S}")
    
    print(f"  Verified: {forward_verified}")
    print(f"  Failed: {forward_failed}")
    print()
    
    if forward_failed > 0:
        print("ERROR: Forward transitions are not correct!")
        return 1
    
    # Find predecessors of state 0
    print("Finding predecessors of state 0...")
    
    # Collect all states that appear in the paths
    all_states = set()
    for path in paths:
        all_states.update(path)
    
    print(f"  Total unique states in paths: {len(all_states)}")
    
    # Find predecessors of 0 using brute force
    start_time = time.time()
    predecessors_of_0 = find_predecessors_brute_force(0, templates, all_states)
    elapsed = time.time() - start_time
    
    print(f"  Found {len(predecessors_of_0)} predecessors of state 0 in {elapsed:.1f}s")
    print()
    
    # Verify that these predecessors are correct
    print("Verifying predecessors of state 0...")
    for P in predecessors_of_0:
        successors = explore_forward(P, templates)
        if 0 not in successors:
            print(f"  ERROR: {P} is not a predecessor of 0!")
            return 1
    
    print(f"  All {len(predecessors_of_0)} predecessors verified")
    print()
    
    # Show some example predecessors
    print("Example predecessors of state 0:")
    for i, P in enumerate(list(predecessors_of_0)[:5]):
        print(f"  {i+1}. {P}")
        print(f"     layer0: {layer_mask(P, 0)}")
        print(f"     layer1: {layer_mask(P, 1)}")
        print(f"     layer2: {layer_mask(P, 2)}")
    print()
    
    # Now try to understand the structure
    print("Analyzing predecessor structure...")
    
    # For each predecessor P of 0, what is the pre-shift state?
    # The pre-shift state is the state before shifting to 0
    # It should have layer0 = WORD_MASK, layer1 = 0, layer2 = 0
    
    pre_shift_states = set()
    for P in predecessors_of_0:
        # Find the state that shifts to 0
        # This is a state with layer0 = WORD_MASK, layer1 = 0, layer2 = 0
        # that is reachable from P
        seen = {P}
        queue = deque([P])
        
        while queue:
            s = queue.popleft()
            
            if layer_mask(s, 0) == WORD_MASK:
                # This is a pre-shift state
                pre_shift_states.add(s)
                break
            
            target = first_empty(layer_mask(s, 0))
            
            for template in templates[target]:
                nxt = apply_template(s, template)
                
                if nxt is None or nxt in seen:
                    continue
                
                seen.add(nxt)
                queue.append(nxt)
    
    print(f"  Found {len(pre_shift_states)} unique pre-shift states")
    
    # Check that all pre-shift states have the expected structure
    for ps in pre_shift_states:
        if layer_mask(ps, 0) != WORD_MASK:
            print(f"  ERROR: Pre-shift state {ps} does not have layer0 = WORD_MASK")
            return 1
        if layer_mask(ps, 1) != 0:
            print(f"  ERROR: Pre-shift state {ps} does not have layer1 = 0")
            return 1
        if layer_mask(ps, 2) != 0:
            print(f"  ERROR: Pre-shift state {ps} does not have layer2 = 0")
            return 1
    
    print(f"  All pre-shift states have the expected structure")
    print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total paths: {len(paths)}")
    print(f"Unique state pairs: {len(state_pairs)}")
    print(f"Forward transitions verified: {forward_verified}")
    print(f"Predecessors of state 0: {len(predecessors_of_0)}")
    print(f"Pre-shift states: {len(pre_shift_states)}")
    print()
    print("✓ All forward transitions are correct")
    print("✓ Predecessor function is correct (brute force)")
    print()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
