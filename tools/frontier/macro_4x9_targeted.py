#!/usr/bin/env python3
"""
Targeted analysis for 4x9 S-pentacube macro graph.

This script:
1. Loads the 4x9 checkpoint (10M states, max depth 37)
2. Continues the BFS from the queue, monitoring growth at each depth
3. Checks if WORD_MASK is discovered
4. Estimates the cost of reaching depth 59 (for z=60)
5. Optionally does a backward search from WORD_MASK

Usage:
    python3 tools/frontier/macro_4x9_targeted.py [--max-depth 60] [--max-time 300]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements


def build_templates(a: int, b: int):
    """Build templates for a×b cross-section."""
    NCELLS = a * b
    LAYERS = 3
    WORD_MASK = (1 << NCELLS) - 1

    raw, _ = generate_placements(
        PENTACUBES["S"],
        (a, b, 20),
        break_symmetry=False,
    )

    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    concrete_count = len(raw)

    for placement in raw.values():
        cells = tuple(placement)
        min_z = min(z for _, _, z in cells)

        for x, y, z in cells:
            target = x + a * y
            target_rel = z - min_z

            shifted_masks = [0] * LAYERS
            valid = True
            for cx, cy, cz in cells:
                rel = cz - min_z - target_rel
                if rel < 0 or rel >= LAYERS:
                    valid = False
                    break
                cell_id = cx + a * cy
                shifted_masks[rel] |= (1 << cell_id)

            if not valid:
                continue

            packed = 0
            for i, mask in enumerate(shifted_masks):
                packed |= (mask << (i * NCELLS))

            if packed in seen[target]:
                continue
            seen[target].add(packed)
            result[target].append(packed)

    total_templates = sum(len(v) for v in result.values())
    return result, NCELLS, WORD_MASK, concrete_count, total_templates


def layer_mask(state: int, layer: int, NCELLS: int) -> int:
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)


def first_empty(mask: int, NCELLS: int) -> int:
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def apply_template(state: int, template: int) -> int | None:
    if state & template:
        return None
    return state | template


def shift_state(state: int, NCELLS: int) -> int:
    return state >> NCELLS


def explore_source(source: int, templates: dict, NCELLS: int, WORD_MASK: int):
    """Explore the placement interval from a source until the next layer shift."""
    successors = set()
    seen = {source}
    queue = deque([source])

    while queue:
        state = queue.popleft()

        if layer_mask(state, 0, NCELLS) == WORD_MASK:
            successors.add(shift_state(state, NCELLS))
            continue

        target = first_empty(layer_mask(state, 0, NCELLS), NCELLS)

        for template in templates[target]:
            nxt = apply_template(state, template)
            if nxt is None or nxt in seen:
                continue
            seen.add(nxt)
            queue.append(nxt)

    return successors, len(seen) - 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Targeted 4x9 macro analysis")
    parser.add_argument("--max-depth", type=int, default=60,
                        help="Maximum BFS depth to explore (default: 60)")
    parser.add_argument("--max-time", type=int, default=300,
                        help="Maximum time in seconds (default: 300)")
    parser.add_argument("--max-states", type=int, default=50_000_000,
                        help="Maximum total states (default: 50M)")
    parser.add_argument("--backward", action="store_true",
                        help="Do backward search from WORD_MASK")
    args = parser.parse_args()

    a, b = 4, 9
    checkpoint_path = Path("/tmp/macro_checkpoints/4x9.ckpt")

    # Build templates
    print("Building templates...")
    t0 = time.perf_counter()
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates(a, b)
    t1 = time.perf_counter()
    print(f"  Templates: {total_templates} ({t1-t0:.1f}s)")

    # Load checkpoint
    print("Loading checkpoint...")
    t2 = time.perf_counter()
    with open(checkpoint_path / "macro_seen.json") as f:
        macro_seen = set(json.load(f))
    with open(checkpoint_path / "succ.json") as f:
        succ_raw = json.load(f)
    succ = {int(k): set(v) for k, v in succ_raw.items()}
    del succ_raw
    with open(checkpoint_path / "queue.json") as f:
        queue_list = json.load(f)
    with open(checkpoint_path / "sources.json") as f:
        sources = set(json.load(f))
    t3 = time.perf_counter()
    print(f"  Loaded: {len(macro_seen):,} states, {len(succ):,} succ entries, "
          f"{len(queue_list):,} in queue ({t3-t2:.1f}s)")

    # Compute BFS depths
    print("Computing BFS depths...")
    t4 = time.perf_counter()
    depth = {s: 0 for s in sources}
    q = deque(sources)
    while q:
        u = q.popleft()
        d = depth[u]
        if u in succ:
            for v in succ[u]:
                if v not in depth:
                    depth[v] = d + 1
                    q.append(v)
    t5 = time.perf_counter()
    max_depth = max(depth.values())
    print(f"  Max depth: {max_depth} ({t5-t4:.1f}s)")

    # Check if WORD_MASK is in the graph
    print(f"WORD_MASK in graph: {WORD_MASK in macro_seen}")
    print(f"0 in graph: {0 in macro_seen}")

    # Continue BFS from queue
    print(f"\n=== Continuing BFS from depth {max_depth} ===")
    print(f"Target: depth {args.max_depth}, time limit {args.max_time}s, "
          f"state limit {args.max_states:,}")

    queue = deque()
    for s in queue_list:
        if s in depth:
            queue.append(s)

    depth_counts = Counter(depth.values())
    total_intermediate = 0
    start_time = time.perf_counter()
    states_at_start = len(macro_seen)
    processed_at_start = len(succ)

    wordmask_found = False
    zero_found = False

    while queue:
        # Check limits
        elapsed = time.perf_counter() - start_time
        if elapsed > args.max_time:
            print(f"\nTime limit reached ({elapsed:.1f}s)")
            break
        if len(macro_seen) >= args.max_states:
            print(f"\nState limit reached ({len(macro_seen):,})")
            break

        src = queue.popleft()
        src_depth = depth.get(src, -1)

        # Skip if already processed
        if src in succ:
            continue

        # Explore source
        successors, intermediate = explore_source(src, templates, NCELLS, WORD_MASK)
        total_intermediate += intermediate

        if successors:
            succ[src] = successors

            # Check for WORD_MASK and 0
            if WORD_MASK in successors:
                wordmask_found = True
                print(f"\n*** WORD_MASK found as successor of depth-{src_depth} state! ***")
            if 0 in successors:
                zero_found = True
                print(f"\n*** 0 found as successor of depth-{src_depth} state! ***")

        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                s_depth = src_depth + 1
                depth[s] = s_depth
                depth_counts[s_depth] += 1
                if s_depth <= args.max_depth:
                    queue.append(s)

        # Progress report
        if len(succ) % 10000 == 0:
            elapsed = time.perf_counter() - start_time
            current_max_depth = max(depth.values())
            print(f"  processed={len(succ):,} states={len(macro_seen):,} "
                  f"max_depth={current_max_depth} "
                  f"depth{current_max_depth}={depth_counts.get(current_max_depth, 0):,} "
                  f"elapsed={elapsed:.1f}s", flush=True)

    elapsed = time.perf_counter() - start_time
    final_max_depth = max(depth.values())

    print(f"\n=== Results ===")
    print(f"Processed this run: {len(succ) - processed_at_start:,}")
    print(f"Total states: {len(macro_seen):,}")
    print(f"Total intermediate: {total_intermediate:,}")
    print(f"Max depth: {final_max_depth}")
    print(f"WORD_MASK found: {wordmask_found}")
    print(f"0 found: {zero_found}")
    print(f"Elapsed: {elapsed:.1f}s")

    print(f"\nDepth distribution:")
    for d in range(final_max_depth + 1):
        count = depth_counts.get(d, 0)
        if count > 0:
            print(f"  depth {d}: {count:,}")

    # Save results
    out = Path("/tmp/macro_4x9_targeted_results.txt")
    lines = [
        f"processed_this_run={len(succ) - processed_at_start}",
        f"total_states={len(macro_seen)}",
        f"total_intermediate={total_intermediate}",
        f"max_depth={final_max_depth}",
        f"wordmask_found={wordmask_found}",
        f"zero_found={zero_found}",
        f"elapsed={elapsed:.1f}",
    ]
    for d in range(final_max_depth + 1):
        lines.append(f"depth_{d}={depth_counts.get(d, 0)}")
    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
