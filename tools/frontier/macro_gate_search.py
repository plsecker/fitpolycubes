#!/usr/bin/env python3
"""
Gate-directed macro cycle finder.

Searches for the shortest path from state 0 to the gate state (FULL,0,0)
in an a×b S-pentacube macro graph, without enumerating the full graph.

A return cycle exists iff the gate is reachable; its length is
gate_distance + 1 (the final gate -> 0 edge is a pure shift).

For cross-sections with large first-generation trees (e.g. 5×8), a pure
forward BFS is not tractable; the physical-tiling extraction path
(extract_cycle_from_tiling.py) should be used instead.

Usage:
    python3 tools/frontier/macro_gate_search.py --a 4 --b 5 --max-depth 10
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.frontier.macro_generalized import (
    build_templates_general,
    layer_mask_general,
    first_empty_general,
    apply_template_general,
    shift_state_general,
)


def one_edge_successors(state, templates, NCELLS, WORD_MASK):
    """All post-shift states reachable in exactly one macro edge."""
    fill_seen = {state}
    fq = deque([state])
    succs = set()
    while fq:
        s = fq.popleft()
        l0 = layer_mask_general(s, 0, NCELLS)
        if l0 == WORD_MASK:
            succs.add(shift_state_general(s, NCELLS))
            continue
        target = first_empty_general(l0, NCELLS)
        for t in templates[target]:
            nxt = apply_template_general(s, t)
            if nxt is not None and nxt not in fill_seen:
                fill_seen.add(nxt)
                fq.append(nxt)
    return succs


def gate_search(a: int, b: int, max_depth: int = 30, verbose: bool = True) -> dict:
    """BFS from state 0 seeking the gate state (FULL,0,0)."""
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1
    GATE = WORD_MASK

    templates, _, _, _, _ = build_templates_general(a, b)

    t0 = time.time()
    seen = {0}
    dist = {0: 0}
    parents = {0: None}
    queue = deque([0])
    gate_distance = None
    gate_node = None

    while queue:
        state = queue.popleft()
        d = dist[state]
        if d >= max_depth:
            continue

        succs = one_edge_successors(state, templates, NCELLS, WORD_MASK)
        for succ in succs:
            if succ not in seen:
                seen.add(succ)
                dist[succ] = d + 1
                parents[succ] = state
                queue.append(succ)
                if succ == GATE:
                    gate_distance = d + 1
                    gate_node = succ
                    queue.clear()
                    break
        if gate_distance is not None:
            break

    elapsed = time.time() - t0

    # Reconstruct path if found
    path = None
    if gate_node is not None:
        path = []
        cur = gate_node
        while cur is not None:
            path.append(cur)
            cur = parents[cur]
        path.reverse()

    result = {
        "a": a,
        "b": b,
        "gate_state": GATE,
        "gate_distance": gate_distance,
        "return_length": (gate_distance + 1) if gate_distance is not None else None,
        "gate_path": path,
        "states_explored": len(seen),
        "elapsed": elapsed,
    }

    if verbose:
        print(f"=== Gate search {a}×{b} (max-depth {max_depth}) ===")
        print(f"  Gate state: {GATE}")
        print(f"  Gate distance: {gate_distance}")
        print(f"  Return length: {result['return_length']}")
        print(f"  States explored: {len(seen):,}")
        print(f"  Elapsed: {elapsed:.1f}s")
        if path:
            print(f"  Path length: {len(path)} states")
            for i, s in enumerate(path):
                l0 = bin(layer_mask_general(s, 0, NCELLS)).count("1")
                l1 = bin(layer_mask_general(s, 1, NCELLS)).count("1")
                l2 = bin(layer_mask_general(s, 2, NCELLS)).count("1")
                print(f"    s{i}: ({l0},{l1},{l2})")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gate-directed macro cycle finder"
    )
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)
    parser.add_argument("--max-depth", type=int, default=30)
    args = parser.parse_args()

    gate_search(args.a, args.b, args.max_depth)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())