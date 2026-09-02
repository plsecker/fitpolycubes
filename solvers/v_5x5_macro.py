#!/usr/bin/env python3
"""
Macro state-graph solver for V pentacube in 5×5×N boxes.

This implements the generalized Macro technique for the V pentacube
with 5×5 cross-section, targeting the minimal odd box 5×5×9.

State representation:
    One Python integer containing three 25-bit z-layer masks.
    
    bits   0..24   = layer 0
    bits  25..49   = layer 1
    bits  50..74   = layer 2
    
The V pentacube spans at most 3 layers in any placement, so we need
exactly 3 layers to capture the frontier state.

Usage:
    # Build state graph and count paths
    python3 solvers/v_5x5_macro.py --target-depth 9
    
    # With checkpointing
    python3 solvers/v_5x5_macro.py --target-depth 9 \\
        --checkpoint /tmp/v_5x5.ckpt
    
    # Enumerate actual tilings
    python3 solvers/v_5x5_macro.py --target-depth 9 --enumerate-tilings
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

# Cross-section dimensions
X_SIZE = 5
Y_SIZE = 5
NCELLS = X_SIZE * Y_SIZE  # 25
LAYERS = 3
WORD_MASK = (1 << NCELLS) - 1  # 25 bits


def cell_id(x: int, y: int) -> int:
    """Convert (x, y) to linear cell index."""
    return x + X_SIZE * y


def layer_mask(state: int, layer: int) -> int:
    """Extract the mask for a specific layer from the state."""
    return (state >> (layer * NCELLS)) & WORD_MASK


def first_empty(mask: int) -> int:
    """Find the first empty cell in a layer mask."""
    missing = WORD_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def pack_layers(layers: List[int]) -> int:
    """Pack three layer masks into a single state integer."""
    state = 0
    for i, mask in enumerate(layers):
        state |= (mask << (i * NCELLS))
    return state


def shift_state(state: int) -> int:
    """Shift state down by one layer (discard layer 0, layer 1 -> 0, etc.)."""
    return state >> NCELLS


def make_shifted_template(
    placement_cells: List[Tuple[int, int, int]],
    target_z: int,
) -> Optional[int]:
    """
    Translate a concrete V placement so that the chosen target occurrence
    lies on frontier layer 0.
    
    Return packed 75-bit occupancy (three 25-bit layer masks).
    """
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        
        if rel < 0 or rel >= LAYERS:
            return None
        
        shifted_masks[rel] |= (1 << cell_id(x, y))
    
    return pack_layers(shifted_masks)


def build_templates() -> Tuple[Dict[int, List[int]], int, int, int, int]:
    """
    Generate templates for V pentacube in 5×5 cross-section.
    
    Returns:
        templates: dict mapping target cell -> list of template states
        NCELLS: number of cells per layer
        WORD_MASK: mask for a single layer
        concrete_count: number of concrete placements
        total_templates: total number of templates generated
    """
    raw, _ = generate_placements(
        PENTACUBES["V"],
        (X_SIZE, Y_SIZE, 20),  # 20 is arbitrary; just needs to be large enough
        break_symmetry=False,
    )
    
    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    
    concrete_count = len(raw)
    
    for placement in raw.values():
        cells = tuple(placement)
        
        for x, y, z in cells:
            target = cell_id(x, y)
            
            packed = make_shifted_template(cells, z)
            
            if packed is None:
                continue
            
            if packed in seen[target]:
                continue
            
            seen[target].add(packed)
            result[target].append(packed)
    
    total_templates = sum(len(v) for v in result.values())
    
    return result, NCELLS, WORD_MASK, concrete_count, total_templates


def apply_template(state: int, template: int) -> Optional[int]:
    """Apply template to state if disjoint (no overlapping cells)."""
    if state & template:
        return None
    return state | template


def explore_source(
    source: int,
    templates: Dict[int, List[int]],
    max_intermediate: int = 1_000_000,
) -> Tuple[Set[int], int, bool]:
    """
    Explore the placement interval from a post-shift source until the
    next layer shift.
    
    Returns:
        successors: distinct post-shift states reached
        intermediate_count: number of distinct non-shift states explored
        hit_limit: True if max_intermediate was reached
    """
    successors: Set[int] = set()
    seen: Set[int] = {source}
    queue: deque[int] = deque([source])
    hit_limit = False
    
    while queue:
        if len(seen) - 1 >= max_intermediate:
            hit_limit = True
            break
        
        state = queue.popleft()
        
        if layer_mask(state, 0) == WORD_MASK:
            successors.add(shift_state(state))
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None:
                continue
            
            if nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append(nxt)
    
    return successors, len(seen) - 1, hit_limit


def build_macro_graph(
    templates: Dict[int, List[int]],
    max_macro_states: int = 10_000_000,
    verbose: bool = True,
) -> Tuple[Set[int], Dict[int, Set[int]], Set[int], Dict]:
    """
    Build the complete Macro state graph for V in 5×5×N.
    
    Returns:
        macro_states: set of all reachable macro states
        succ: successor function (macro state -> set of macro states)
        sources: initial sources (states reachable from empty state)
        stats: computation statistics
    """
    start_time = time.perf_counter()
    
    if verbose:
        print("Phase 1: Finding first-generation sources...")
    
    # Phase 1: Find all sources reachable from empty state
    sources: Set[int] = set()
    seen: Set[int] = {0}
    queue: deque[int] = deque([0])
    
    while queue:
        if len(seen) >= max_macro_states:
            if verbose:
                print(f"  Cap hit at {len(seen):,} states")
            break
        
        state = queue.popleft()
        
        if layer_mask(state, 0) == WORD_MASK:
            sources.add(shift_state(state))
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append(nxt)
    
    if verbose:
        print(f"  First-generation sources: {len(sources):,}")
        print(f"  First-gen tree states: {len(seen):,}")
        print()
        print("Phase 2: Computing Macro closure...")
    
    # Phase 2: Compute Macro closure
    macro_seen: Set[int] = set(sources)
    queue = deque(sources)
    succ: Dict[int, Set[int]] = {}
    edge_count = 0
    total_intermediate = 0
    
    while queue:
        if len(macro_seen) >= max_macro_states:
            if verbose:
                print(f"  Macro closure cap hit at {len(macro_seen):,} states")
            break
        
        src = queue.popleft()
        successors, intermediate, hit_limit = explore_source(src, templates)
        total_intermediate += intermediate
        
        if successors:
            succ[src] = successors
            edge_count += len(successors)
        
        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                queue.append(s)
        
        if verbose and len(macro_seen) % 100_000 == 0:
            print(f"  Progress: {len(macro_seen):,} macro states, {edge_count:,} edges")
    
    elapsed = time.perf_counter() - start_time
    
    stats = {
        "NCELLS": NCELLS,
        "state_size_bits": LAYERS * NCELLS,
        "first_gen_sources": len(sources),
        "first_gen_tree_states": len(seen),
        "macro_states": len(macro_seen),
        "macro_edges": edge_count,
        "total_intermediate": total_intermediate,
        "zero_reachable": 0 in macro_seen,
        "elapsed": elapsed,
    }
    
    if verbose:
        print()
        print("=== Macro Graph Statistics ===")
        print(f"Macro states: {len(macro_seen):,}")
        print(f"Macro edges: {edge_count:,}")
        print(f"Total intermediate states: {total_intermediate:,}")
        print(f"State 0 reachable: {0 in macro_seen}")
        print(f"Elapsed: {elapsed:.2f} s")
    
    return macro_seen, succ, sources, stats


def count_paths_to_depth(
    succ: Dict[int, Set[int]],
    target_depth: int,
    verbose: bool = True,
) -> Tuple[int, Dict[int, int]]:
    """
    Count the number of paths from state 0 to state 0 at exactly target_depth.
    
    Uses dynamic programming: dp[depth][state] = number of paths to state at depth.
    
    Returns:
        total_paths: number of complete paths (0 -> ... -> 0 at target_depth)
        depth_counts: dict mapping depth -> number of paths to state 0 at that depth
    """
    if verbose:
        print(f"\nCounting paths to depth {target_depth}...")
    
    # dp[state] = number of paths to reach this state at current depth
    dp: Dict[int, int] = {0: 1}
    depth_counts: Dict[int, int] = {}
    
    for depth in range(1, target_depth + 1):
        new_dp: Dict[int, int] = {}
        
        for state, count in dp.items():
            if state in succ:
                for next_state in succ[state]:
                    new_dp[next_state] = new_dp.get(next_state, 0) + count
        
        dp = new_dp
        
        # Count paths to state 0 at this depth
        paths_to_zero = dp.get(0, 0)
        depth_counts[depth] = paths_to_zero
        
        if verbose:
            print(f"  Depth {depth}: {len(dp):,} reachable states, "
                  f"{paths_to_zero:,} paths to state 0")
    
    total_paths = depth_counts.get(target_depth, 0)
    
    if verbose:
        print(f"\nTotal paths to depth {target_depth}: {total_paths:,}")
    
    return total_paths, depth_counts


def enumerate_paths_to_depth(
    succ: Dict[int, Set[int]],
    target_depth: int,
    max_paths: int = 1000,
    verbose: bool = True,
) -> List[List[int]]:
    """
    Enumerate actual paths from state 0 to state 0 at exactly target_depth.
    
    Returns list of paths, where each path is a list of states.
    """
    if verbose:
        print(f"\nEnumerating paths to depth {target_depth} (max {max_paths})...")
    
    paths: List[List[int]] = []
    
    def dfs(state: int, depth: int, path: List[int]):
        if len(paths) >= max_paths:
            return
        
        if depth == target_depth:
            if state == 0:
                paths.append(list(path))
            return
        
        if state not in succ:
            return
        
        for next_state in succ[state]:
            path.append(next_state)
            dfs(next_state, depth + 1, path)
            path.pop()
    
    dfs(0, 0, [0])
    
    if verbose:
        print(f"  Enumerated {len(paths)} paths")
    
    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Macro state-graph solver for V pentacube in 5×5×N boxes."
    )
    
    parser.add_argument(
        "--target-depth",
        type=int,
        default=9,
        help="Target depth (thickness) for path counting (default: 9)",
    )
    
    parser.add_argument(
        "--max-states",
        type=int,
        default=10_000_000,
        help="Maximum macro states to discover (default: 10M)",
    )
    
    parser.add_argument(
        "--enumerate-tilings",
        action="store_true",
        help="Enumerate actual tiling paths (not just count)",
    )
    
    parser.add_argument(
        "--max-paths",
        type=int,
        default=100,
        help="Maximum paths to enumerate (default: 100)",
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for results (JSON)",
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    if verbose:
        print("=" * 70)
        print("V Pentacube Macro Solver")
        print(f"Cross-section: {X_SIZE}×{Y_SIZE}")
        print(f"Target depth: {args.target_depth}")
        print("=" * 70)
        print()
    
    # Build templates
    if verbose:
        print("Building templates...")
    
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates()
    
    if verbose:
        print(f"  Concrete placements: {concrete_count}")
        print(f"  Total templates: {total_templates}")
        print(f"  State size: {LAYERS * NCELLS} bits")
        print()
    
    # Build Macro graph
    macro_states, succ, sources, stats = build_macro_graph(
        templates,
        max_macro_states=args.max_states,
        verbose=verbose,
    )
    
    # Count paths
    total_paths, depth_counts = count_paths_to_depth(
        succ,
        args.target_depth,
        verbose=verbose,
    )
    
    # Enumerate paths if requested
    paths = []
    if args.enumerate_tilings and total_paths > 0:
        paths = enumerate_paths_to_depth(
            succ,
            args.target_depth,
            max_paths=args.max_paths,
            verbose=verbose,
        )
    
    # Prepare results
    results = {
        "piece": "V",
        "cross_section": [X_SIZE, Y_SIZE],
        "target_depth": args.target_depth,
        "total_paths": total_paths,
        "depth_counts": depth_counts,
        "stats": stats,
        "paths_enumerated": len(paths),
        "paths": paths[:10] if paths else [],  # Store first 10 for inspection
    }
    
    # Write results
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        if verbose:
            print(f"\nResults written to {output_path}")
    else:
        output_path = Path(f"/tmp/v_5x5_macro_depth{args.target_depth}.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        if verbose:
            print(f"\nResults written to {output_path}")
    
    # Summary
    if verbose:
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Piece: V pentacube")
        print(f"Box: {X_SIZE}×{Y_SIZE}×{args.target_depth}")
        print(f"Macro states: {stats['macro_states']:,}")
        print(f"Macro edges: {stats['macro_edges']:,}")
        print(f"Total paths to depth {args.target_depth}: {total_paths:,}")
        print(f"State 0 reachable: {stats['zero_reachable']}")
        print()
        
        if total_paths == 0:
            print("CONCLUSION: NO TILINGS EXIST")
        elif total_paths == 1:
            print("CONCLUSION: UNIQUE TILING (up to Macro path equivalence)")
        else:
            print(f"CONCLUSION: {total_paths} TILINGS FOUND")
            print("  (Symmetry reduction needed to determine uniqueness)")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
