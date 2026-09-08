#!/usr/bin/env python3
"""
Simple forward search baseline for V pentacube Macro paths.

This establishes the baseline performance without any pruning.
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


def forward_search_baseline(
    templates: Dict[int, List[int]],
    target_depth: int,
    verbose: bool = True
) -> Tuple[int, Dict]:
    """
    Forward search without pruning (baseline).
    
    Returns (path_count, stats).
    """
    if verbose:
        print(f"Forward search (baseline) to depth {target_depth}")
        print()
    
    # Initialize: F[0] = {0}
    current_level = {0: 1}  # state -> path count
    stats = {
        "depths": [],
        "states_at_depth": [],
    }
    
    for depth in range(target_depth):
        if verbose:
            print(f"Depth {depth}:")
            print(f"  States at this depth: {len(current_level):,}")
        
        # Expand to next depth
        next_level = {}
        
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
            
            # Add successors to next level
            for succ in successors:
                next_level[succ] = next_level.get(succ, 0) + count
        
        if verbose:
            print(f"  States at next depth: {len(next_level):,}")
            print()
        
        stats["depths"].append(depth)
        stats["states_at_depth"].append(len(current_level))
        
        current_level = next_level
    
    # Count paths that reach state 0
    path_count = current_level.get(0, 0)
    
    if verbose:
        print(f"Total paths to state 0: {path_count:,}")
    
    return path_count, stats


def main():
    print("=" * 70)
    print("V PENTACUBE FORWARD SEARCH BASELINE")
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
    path_count, stats = forward_search_baseline(templates, 6, verbose=True)
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
