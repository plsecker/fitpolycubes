#!/usr/bin/env python3
"""
Investigate the relationship between Macro paths and tilings for V in 5×5×6.

This script enumerates actual Macro paths and tries to reconstruct tilings.
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


def explore_to_shift_with_path(state, templates, max_intermediate=1_000_000):
    """
    Explore from a state until we reach a shift (layer 0 full).
    Returns:
        successors: dict mapping post-shift state -> list of (pre-shift state, path of intermediate states)
    """
    successors = {}
    seen = {state: []}  # state -> path from initial state
    queue = deque([(state, [])])
    
    while queue:
        if len(seen) > max_intermediate:
            break
        
        s, path = queue.popleft()
        
        if layer_mask(s, 0) == WORD_MASK:
            succ = shift_state(s)
            if succ not in successors:
                successors[succ] = []
            successors[succ].append((s, path + [s]))
            continue
        
        target = first_empty(layer_mask(s, 0))
        
        for template in templates[target]:
            nxt = apply_template(s, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen[nxt] = path + [s]
            queue.append((nxt, path + [s]))
    
    return successors


def enumerate_macro_paths_depth_6(templates, max_paths=1000, verbose=True):
    """
    Enumerate Macro return paths from state 0 to state 0 at exactly depth 6.
    Returns list of paths, where each path is a list of states.
    """
    if verbose:
        print("Enumerating Macro return paths at depth 6...")
        print()
    
    paths = []
    
    def dfs(state, depth, path):
        if len(paths) >= max_paths:
            return
        
        if depth == 6:
            if state == 0:
                paths.append(list(path))
            return
        
        successors = explore_to_shift_with_path(state, templates)
        
        for succ in successors:
            # Get one representative path to this successor
            pre_shift_state, intermediate_path = successors[succ][0]
            dfs(succ, depth + 1, path + [succ])
    
    dfs(0, 0, [0])
    
    if verbose:
        print(f"Enumerated {len(paths)} Macro paths")
    
    return paths


def reconstruct_tiling_from_macro_path(macro_path, templates):
    """
    Reconstruct a tiling from a Macro path.
    
    A Macro path is a sequence of states: s_0 = 0, s_1, ..., s_6 = 0
    Each transition s_d -> s_{d+1} involves filling layer 0 and shifting.
    
    Returns a list of piece placements (each placement is a list of 5 cells).
    """
    placements = []
    
    for d in range(len(macro_path) - 1):
        start_state = macro_path[d]
        end_state = macro_path[d + 1]
        
        # Find a sequence of piece placements that transitions from start_state to end_state
        # This is a search problem: we need to find piece placements that fill layer 0
        # and result in end_state after shifting
        
        # For now, just find one valid sequence
        placement_sequence = find_placement_sequence(start_state, end_state, templates)
        
        if placement_sequence is None:
            return None
        
        placements.extend(placement_sequence)
    
    return placements


def find_placement_sequence(start_state, end_state, templates, max_steps=100):
    """
    Find a sequence of piece placements that transitions from start_state to end_state.
    """
    # BFS to find a path from start_state to a pre-shift state that shifts to end_state
    queue = deque([(start_state, [])])
    seen = {start_state}
    
    while queue:
        state, placements = queue.popleft()
        
        if len(placements) > max_steps:
            continue
        
        if layer_mask(state, 0) == WORD_MASK:
            if shift_state(state) == end_state:
                return placements
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            # The template represents a piece placement
            # We need to extract the actual cells from the template
            # For now, just store the template
            queue.append((nxt, placements + [template]))
    
    return None


def main():
    print("=" * 70)
    print("V PENTACUBE 5×5×6 - MACRO PATH INVESTIGATION")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, concrete_count, total_templates = build_templates()
    print(f"  Concrete placements: {concrete_count}")
    print(f"  Total templates: {total_templates}")
    print()
    
    # Enumerate Macro paths
    start_time = time.time()
    paths = enumerate_macro_paths_depth_6(templates, max_paths=100, verbose=True)
    elapsed = time.time() - start_time
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Macro paths enumerated: {len(paths)}")
    print(f"Elapsed time: {elapsed:.1f}s")
    print()
    
    # Try to reconstruct tilings from the first few paths
    print("Attempting to reconstruct tilings from Macro paths...")
    print()
    
    tilings = []
    for i, path in enumerate(paths[:10]):
        print(f"Path {i+1}: {path}")
        tiling = reconstruct_tiling_from_macro_path(path, templates)
        if tiling is not None:
            tilings.append(tiling)
            print(f"  ✓ Reconstructed tiling with {len(tiling)} piece placements")
        else:
            print(f"  ✗ Failed to reconstruct tiling")
        print()
    
    print(f"Successfully reconstructed {len(tilings)} tilings")
    
    # Save results
    output = {
        "piece": "V",
        "box": [5, 5, 6],
        "macro_paths_count": len(paths),
        "tilings_reconstructed": len(tilings),
        "elapsed_seconds": elapsed,
    }
    
    output_file = Path("/tmp/v_5x5x6_investigation.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
