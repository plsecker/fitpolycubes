#!/usr/bin/env python3
"""
Bidirectional meet-in-the-middle search for V pentacube Macro paths.

This implements a depth-restricted bidirectional search to find all
complete Macro paths from state 0 to state 0 at a given depth.

Strategy:
1. Compute forward states from state 0 to middle depth
2. Compute reverse states from state 0 backwards for remaining steps
3. Intersect at middle depth
4. Count/construct paths through intersection

Usage:
    python3 solvers/v_5x5_bidirectional.py --target-depth 6  # Calibration
    python3 solvers/v_5x5_bidirectional.py --target-depth 9  # Target
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK, NCELLS, pack_layers
)


def explore_forward(state: int, templates: Dict[int, List[int]]) -> Set[int]:
    """
    Explore forward from a state to find all reachable post-shift states.
    
    This fills layer 0 completely and returns the shifted state.
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


def find_predecessors(state: int, templates: Dict[int, List[int]]) -> Set[int]:
    """
    Find all states that can transition to the given state in one Macro step.
    
    A state s can transition to state if explore_forward(s) contains state.
    This means s can fill layer 0 and shift to reach state.
    
    To find predecessors efficiently:
    1. Reconstruct the pre-shift state: pack_layers([WORD_MASK, layer0(state), layer1(state)])
    2. Find all states that can reach this pre-shift state by filling layer 0
    """
    predecessors = set()
    
    # The pre-shift state before shifting to 'state'
    # After shift: layer 0 of state came from layer 1 of pre-shift
    #              layer 1 of state came from layer 2 of pre-shift
    #              layer 2 of state came from layer 3 of pre-shift (not stored)
    # Before shift: layer 0 of pre-shift was full (WORD_MASK)
    pre_shift_state = pack_layers([
        WORD_MASK,
        layer_mask(state, 0),
        layer_mask(state, 1)
    ])
    
    # Now find all states that can reach pre_shift_state by filling layer 0
    # We do this by reverse BFS: start from pre_shift_state and remove templates
    seen = {pre_shift_state}
    queue = deque([pre_shift_state])
    
    while queue:
        s = queue.popleft()
        
        # If layer 0 is empty, this is a valid predecessor (starting state for this Macro step)
        if layer_mask(s, 0) == 0:
            predecessors.add(s)
            continue
        
        # Try to reverse each template application
        # Find the last template that was applied (the one that filled the last empty cell)
        layer0 = layer_mask(s, 0)
        
        # The last template applied must have covered the highest-numbered filled cell
        # (because we fill cells in order from first_empty)
        # Actually, this is not quite right - we fill in order of first_empty, which is the lowest empty cell
        
        # Let's try a different approach: try removing each template and see if it's valid
        for target in range(NCELLS):
            # Check if this target cell is filled
            if not (layer0 & (1 << target)):
                continue
            
            for template in templates[target]:
                # Check if this template is a subset of current state
                if (s & template) == template:
                    # Try removing it
                    prev_state = s ^ template
                    prev_layer0 = layer_mask(prev_state, 0)
                    
                    # Check if this is a valid previous state
                    # The previous state should have first_empty <= target
                    # (because we fill in order)
                    if prev_layer0 == 0:
                        # Layer 0 is empty, valid predecessor
                        if prev_state not in seen:
                            seen.add(prev_state)
                            predecessors.add(prev_state)
                            queue.append(prev_state)
                    else:
                        prev_first_empty = first_empty(prev_layer0)
                        # The previous first_empty should be <= target
                        # (we fill cells in order, so the previous first empty should be before or at target)
                        if prev_first_empty <= target and prev_state not in seen:
                            seen.add(prev_state)
                            queue.append(prev_state)
    
    return predecessors


def bidirectional_search(
    templates: Dict[int, List[int]],
    target_depth: int,
    forward_depth: int,
    verbose: bool = True
) -> Tuple[int, Dict]:
    """
    Perform bidirectional search for complete paths from 0 to 0.
    
    Args:
        templates: Macro templates
        target_depth: Total depth of paths
        forward_depth: Depth for forward search (remaining is reverse)
        verbose: Print progress
    
    Returns:
        (path_count, stats)
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
            predecessors = find_predecessors(state, templates)
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
    
    # For each state in intersection, count:
    # - Number of forward paths from 0 to this state
    # - Number of reverse paths from this state to 0
    # Total paths = sum of (forward_count * reverse_count) for all intersection states
    
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
            predecessors = find_predecessors(state, templates)
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
    parser = argparse.ArgumentParser(
        description="Bidirectional meet-in-the-middle search for V pentacube Macro paths"
    )
    parser.add_argument(
        "--target-depth",
        type=int,
        default=6,
        help="Target depth for paths (default: 6 for calibration)"
    )
    parser.add_argument(
        "--forward-depth",
        type=int,
        default=None,
        help="Forward search depth (default: target_depth // 2)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for results (JSON)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    if args.forward_depth is None:
        args.forward_depth = args.target_depth // 2
    
    if verbose:
        print("=" * 70)
        print("V PENTACUBE BIDIRECTIONAL MACRO SEARCH")
        print("=" * 70)
        print()
    
    # Build templates
    if verbose:
        print("Building templates...")
    
    templates, _, _, concrete_count, total_templates = build_templates()
    
    if verbose:
        print(f"  Concrete placements: {concrete_count}")
        print(f"  Total templates: {total_templates}")
        print()
    
    # Run bidirectional search
    start_time = time.time()
    path_count, stats = bidirectional_search(
        templates,
        args.target_depth,
        args.forward_depth,
        verbose=verbose
    )
    elapsed = time.time() - start_time
    
    if verbose:
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Target depth: {args.target_depth}")
        print(f"Forward depth: {args.forward_depth}")
        print(f"Reverse depth: {args.target_depth - args.forward_depth}")
        print(f"Total Macro paths: {path_count:,}")
        print(f"Elapsed time: {elapsed:.1f}s")
        print()
        
        if args.target_depth == 6:
            print("Calibration check:")
            print(f"  Expected: 80 paths")
            print(f"  Got: {path_count} paths")
            if path_count == 80:
                print("  ✓ MATCH")
            else:
                print("  ✗ MISMATCH")
    
    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"/tmp/v_5x5_bidirectional_depth{args.target_depth}.json")
    
    with open(output_path, "w") as f:
        json.dump({
            "target_depth": args.target_depth,
            "forward_depth": args.forward_depth,
            "path_count": path_count,
            "elapsed_seconds": elapsed,
            "stats": stats,
        }, f, indent=2)
    
    if verbose:
        print(f"\nResults saved to {output_path}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
