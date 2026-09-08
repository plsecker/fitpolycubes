#!/usr/bin/env python3
"""
Correct bidirectional search for V pentacube Macro paths.

This implements a corrected reverse transition based on the debug findings.
"""

import sys
import time
import json
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


def find_predecessors_correct(state: int, templates: dict) -> set:
    """
    Find all predecessors of a state using the correct semantics.
    
    For target state S, the pre-shift state is Q = pack_layers([WORD_MASK, S.layer0, S.layer1]).
    A predecessor P is a state such that Q is reachable from P by applying templates.
    
    Since templates can only add bits (not remove them), P must satisfy:
    - P.layer1 is a subset of S.layer0
    - P.layer2 is a subset of S.layer1
    - P.layer0 can be anything (as long as it can be filled to WORD_MASK)
    
    We find predecessors by exploring backwards from Q.
    """
    predecessors = set()
    
    # Construct the pre-shift state
    pre_shift = pack_layers([WORD_MASK, layer_mask(state, 0), layer_mask(state, 1)])
    
    # Explore backwards from pre_shift
    # We need to find all states P such that pre_shift is reachable from P
    # This means P.layer1 ⊆ S.layer0 and P.layer2 ⊆ S.layer1
    
    # For efficiency, we enumerate all possible P.layer0 values
    # and check if they can reach pre_shift
    
    # Actually, let's use a different approach:
    # Start from pre_shift and try to "undo" template applications
    
    seen = {pre_shift}
    queue = deque([pre_shift])
    
    while queue:
        s = queue.popleft()
        
        # If layer0 is not full, this could be a predecessor
        if layer_mask(s, 0) != WORD_MASK:
            # Check if this state satisfies the constraints
            # P.layer1 ⊆ S.layer0 and P.layer2 ⊆ S.layer1
            s_layer1 = layer_mask(s, 1)
            s_layer2 = layer_mask(s, 2)
            target_layer0 = layer_mask(state, 0)
            target_layer1 = layer_mask(state, 1)
            
            if (s_layer1 & target_layer0) == s_layer1 and (s_layer2 & target_layer1) == s_layer2:
                # This is a valid predecessor
                predecessors.add(s)
                # Don't continue exploring from here, as we've found a predecessor
        
        # Try to undo template applications
        # For each cell in layer0 that is filled, try removing templates that cover it
        layer0 = layer_mask(s, 0)
        
        for target in range(NCELLS):
            if not (layer0 & (1 << target)):
                continue
            
            for template in templates[target]:
                # Check if this template is a subset of current state
                if (s & template) == template:
                    # Try removing it
                    prev_state = s ^ template
                    
                    if prev_state not in seen:
                        seen.add(prev_state)
                        queue.append(prev_state)
    
    return predecessors


def bidirectional_search(
    templates: dict,
    target_depth: int,
    forward_depth: int,
    verbose: bool = True
) -> tuple:
    """
    Perform bidirectional search for complete paths from 0 to 0.
    """
    reverse_depth = target_depth - forward_depth
    
    if verbose:
        print(f"Bidirectional search: {forward_depth} forward + {reverse_depth} reverse")
        print()
    
    # Phase 1: Forward search from state 0
    if verbose:
        print(f"Phase 1: Forward search to depth {forward_depth}")
    
    forward_sets = [{0}]  # F[0] = {0}
    
    for d in range(1, forward_depth + 1):
        if verbose:
            print(f"  Computing F[{d}] from F[{d-1}] ({len(forward_sets[d-1]):,} states)...")
        
        start_time = time.time()
        f_next = set()
        
        for state in forward_sets[d-1]:
            successors = explore_forward(state, templates)
            f_next.update(successors)
        
        forward_sets.append(f_next)
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"    |F[{d}]| = {len(f_next):,} states ({elapsed:.1f}s)")
    
    # Phase 2: Reverse search from state 0
    if verbose:
        print()
        print(f"Phase 2: Reverse search to depth {reverse_depth}")
    
    reverse_sets = [{0}]  # R[0] = {0}
    
    for d in range(1, reverse_depth + 1):
        if verbose:
            print(f"  Computing R[{d}] from R[{d-1}] ({len(reverse_sets[d-1]):,} states)...")
        
        start_time = time.time()
        r_next = set()
        
        for state in reverse_sets[d-1]:
            predecessors = find_predecessors_correct(state, templates)
            r_next.update(predecessors)
        
        reverse_sets.append(r_next)
        elapsed = time.time() - start_time
        
        if verbose:
            print(f"    |R[{d}]| = {len(r_next):,} states ({elapsed:.1f}s)")
    
    # Phase 3: Intersection at middle depth
    if verbose:
        print()
        print("Phase 3: Intersection at middle depth")
    
    forward_middle = forward_sets[forward_depth]
    reverse_middle = reverse_sets[reverse_depth]
    
    intersection = forward_middle & reverse_middle
    
    if verbose:
        print(f"  |F[{forward_depth}]| = {len(forward_middle):,}")
        print(f"  |R[{reverse_depth}]| = {len(reverse_middle):,}")
        print(f"  |Intersection| = {len(intersection):,}")
    
    # Phase 4: Count paths through intersection
    if verbose:
        print()
        print("Phase 4: Counting paths through intersection")
    
    # Count forward paths using DP
    forward_counts = {0: 1}
    for d in range(1, forward_depth + 1):
        next_counts = {}
        for state, count in forward_counts.items():
            successors = explore_forward(state, templates)
            for succ in successors:
                next_counts[succ] = next_counts.get(succ, 0) + count
        forward_counts = next_counts
    
    # Count reverse paths using DP
    reverse_counts = {0: 1}
    for d in range(1, reverse_depth + 1):
        next_counts = {}
        for state, count in reverse_counts.items():
            predecessors = find_predecessors_correct(state, templates)
            for pred in predecessors:
                next_counts[pred] = next_counts.get(pred, 0) + count
        reverse_counts = next_counts
    
    # Total paths
    total_paths = 0
    for state in intersection:
        f_count = forward_counts.get(state, 0)
        r_count = reverse_counts.get(state, 0)
        total_paths += f_count * r_count
    
    if verbose:
        print(f"  Total paths: {total_paths:,}")
    
    stats = {
        "target_depth": target_depth,
        "forward_depth": forward_depth,
        "reverse_depth": reverse_depth,
        "forward_sets": [len(s) for s in forward_sets],
        "reverse_sets": [len(s) for s in reverse_sets],
        "intersection_size": len(intersection),
        "total_paths": total_paths,
    }
    
    return total_paths, stats


def main():
    print("=" * 70)
    print("V PENTACUBE BIDIRECTIONAL MACRO SEARCH (CORRECTED)")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Test on 5×5×6 calibration case
    print("Testing on 5×5×6 calibration case (depth 6, split 3+3)...")
    start_time = time.time()
    path_count, stats = bidirectional_search(templates, 6, 3, verbose=True)
    elapsed = time.time() - start_time
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Target depth: 6")
    print(f"Forward depth: 3")
    print(f"Reverse depth: 3")
    print(f"Total Macro paths: {path_count:,}")
    print(f"Elapsed time: {elapsed:.1f}s")
    print()
    
    print("Calibration check:")
    print(f"  Expected: 80 paths")
    print(f"  Got: {path_count} paths")
    if path_count == 80:
        print("  ✓ MATCH")
    else:
        print("  ✗ MISMATCH")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
