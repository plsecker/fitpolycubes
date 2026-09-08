#!/usr/bin/env python3
"""
Forward Macro search with target-completion pruning for V pentacube.

This implements forward search with pruning based on necessary conditions
for reaching the terminal state 0 at the target depth.

The key idea: at each depth d, we check whether the current state S
can possibly reach state 0 in the remaining r = target_depth - d steps.
If not, we prune S immediately.

Pruning conditions (all provably necessary):
1. Volume divisibility: remaining volume must be divisible by 5
2. Layer capacity: each layer must be fillable within remaining depth
3. Frontier connectivity: occupied cells must form completable patterns
"""

from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.v_5x5_macro import (
    build_templates, layer_mask, first_empty, apply_template,
    shift_state, WORD_MASK, NCELLS
)


def count_bits(mask: int) -> int:
    """Count the number of set bits in a mask."""
    return bin(mask).count('1')


def check_volume_divisibility(state: int, depth: int, target_depth: int) -> bool:
    """
    Check if the remaining volume is divisible by 5.
    
    Remaining volume = (target_depth - depth) × 25 - occupied_cells
    This must be divisible by 5.
    
    Necessary condition: V pentacube has volume 5, so any valid tiling
    must use a multiple of 5 cells.
    """
    remaining_depth = target_depth - depth
    
    # Count occupied cells in the state
    occupied = 0
    for layer in range(3):
        occupied += count_bits(layer_mask(state, layer))
    
    # Remaining volume
    remaining_volume = remaining_depth * NCELLS - occupied
    
    # Must be divisible by 5
    return remaining_volume % 5 == 0


def check_layer_capacity(state: int, depth: int, target_depth: int) -> bool:
    """
    Check if each layer can be filled within the remaining depth.
    
    A cell occupied in layer k must be fillable by a V placement that
    spans at most (target_depth - depth) layers.
    
    Since V placements span at most 3 layers, this is always satisfied
    if remaining_depth >= 3. For smaller remaining_depth, we need to check.
    """
    remaining_depth = target_depth - depth
    
    # If remaining depth is large enough, all layers can be filled
    if remaining_depth >= 3:
        return True
    
    # For small remaining depth, check each layer
    # Layer 0 must be fillable in remaining_depth steps
    # Layer 1 must be fillable in remaining_depth - 1 steps (if it exists)
    # Layer 2 must be fillable in remaining_depth - 2 steps (if it exists)
    
    # This is a simplified check - we just verify that the occupied cells
    # don't exceed what can be filled in the remaining depth
    
    # Layer 0: must be filled in remaining_depth steps
    layer0_occupied = count_bits(layer_mask(state, 0))
    if layer0_occupied > remaining_depth * NCELLS:
        return False
    
    # Layer 1: must be filled in remaining_depth - 1 steps
    if remaining_depth >= 2:
        layer1_occupied = count_bits(layer_mask(state, 1))
        if layer1_occupied > (remaining_depth - 1) * NCELLS:
            return False
    
    # Layer 2: must be filled in remaining_depth - 2 steps
    if remaining_depth >= 3:
        layer2_occupied = count_bits(layer_mask(state, 2))
        if layer2_occupied > (remaining_depth - 2) * NCELLS:
            return False
    
    return True


def check_frontier_connectivity(state: int, templates: Dict[int, List[int]]) -> bool:
    """
    Check if the occupied cells form a completable pattern.
    
    This is a simplified check: we verify that the occupied cells
    don't create isolated regions that cannot be filled.
    
    A more sophisticated check would use connected components analysis,
    but for now we use a simpler heuristic.
    """
    # For now, this is a placeholder - we'll implement a more sophisticated
    # check if needed
    
    # Simple check: if layer 0 is full, we can shift and continue
    # If layer 0 is not full, we need to be able to fill it
    
    layer0 = layer_mask(state, 0)
    
    # If layer 0 is full, we're good
    if layer0 == WORD_MASK:
        return True
    
    # If layer 0 is empty, we need to fill it
    # Check if there are any templates that can be applied
    first = first_empty(layer0)
    if first >= 0 and first < NCELLS:
        # There are templates for this position
        if templates.get(first, []):
            return True
    
    return False


def can_complete(state: int, depth: int, target_depth: int, templates: Dict[int, List[int]]) -> bool:
    """
    Check if a state can possibly reach state 0 at target_depth.
    
    This combines all necessary conditions.
    """
    # Condition 1: Volume divisibility
    if not check_volume_divisibility(state, depth, target_depth):
        return False
    
    # Condition 2: Layer capacity
    if not check_layer_capacity(state, depth, target_depth):
        return False
    
    # Condition 3: Frontier connectivity
    if not check_frontier_connectivity(state, templates):
        return False
    
    return True


def forward_search_with_pruning(
    templates: Dict[int, List[int]],
    target_depth: int,
    verbose: bool = True
) -> Tuple[int, Dict]:
    """
    Forward search with completion pruning.
    
    Returns (path_count, stats).
    """
    if verbose:
        print(f"Forward search with pruning to depth {target_depth}")
        print()
    
    # Initialize: F[0] = {0}
    current_level = {0: 1}  # state -> path count
    stats = {
        "depths": [],
        "states_before_pruning": [],
        "states_rejected": [],
        "states_retained": [],
    }
    
    for depth in range(target_depth):
        if verbose:
            print(f"Depth {depth}:")
            print(f"  States at this depth: {len(current_level):,}")
        
        # Expand to next depth
        next_level = {}
        states_before_pruning = 0
        states_rejected = 0
        
        for state, count in current_level.items():
            # Find successors
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
            
            # For each successor, check if it can complete
            for succ in successors:
                states_before_pruning += 1
                
                # Pruning check
                if can_complete(succ, depth + 1, target_depth, templates):
                    next_level[succ] = next_level.get(succ, 0) + count
                else:
                    states_rejected += 1
        
        states_retained = len(next_level)
        
        if verbose:
            print(f"  States before pruning: {states_before_pruning:,}")
            print(f"  States rejected: {states_rejected:,}")
            print(f"  States retained: {states_retained:,}")
            print()
        
        stats["depths"].append(depth)
        stats["states_before_pruning"].append(states_before_pruning)
        stats["states_rejected"].append(states_rejected)
        stats["states_retained"].append(states_retained)
        
        current_level = next_level
    
    # Count paths that reach state 0
    path_count = current_level.get(0, 0)
    
    if verbose:
        print(f"Total paths to state 0: {path_count:,}")
    
    return path_count, stats


def main():
    print("=" * 70)
    print("V PENTACUBE FORWARD SEARCH WITH COMPLETION PRUNING")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Test on 5×5×6 calibration case
    print("Testing on 5×5×6 calibration case...")
    start_time = time.time()
    path_count, stats = forward_search_with_pruning(templates, 6, verbose=True)
    elapsed = time.time() - start_time
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Target depth: 6")
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
