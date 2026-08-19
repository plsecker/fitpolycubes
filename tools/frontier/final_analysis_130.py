#!/usr/bin/env python3
"""
Final analysis: Can N=130 be achieved by combining the 20-cycle with DAG paths?

Key finding from previous analysis:
- Within the 226-state SCC, max distance is 59
- 129 can be decomposed as:
  * 129 = 20 * 4 + 49
  * 129 = 20 * 5 + 29
  * 129 = 20 * 6 + 9

This script checks if there are paths in the DAG that can achieve distances
49, 29, or 9 from SCC states back to 0.
"""

from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path("/home/philip/Work/fitpolycubes")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.s_z_frontier_packed import (
    WORD_MASK,
    apply_template,
    build_templates,
    first_empty,
    layer_mask,
    shift_state,
)

MAX_FIRSTGEN_STATES = 5_000_000
MAX_INTERMEDIATE = 1_000_000
MAX_INTERMEDIATE_0 = 4_000_000
MAX_CLOSURE_STATES = 15_000_000

S_STAR = 6163195513375031274
TARGET_DISTANCES = [9, 29, 49]  # For 129 = 20k + r


def first_generation_sources(templates):
    sources = set()
    seen = {0}
    queue = deque([0])

    while queue:
        if len(seen) >= MAX_FIRSTGEN_STATES:
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

    return sources


def explore_source(source, templates, max_intermediate=MAX_INTERMEDIATE):
    successors = set()
    seen = {source}
    queue = deque([source])

    while queue:
        if len(seen) - 1 >= max_intermediate:
            break

        state = queue.popleft()

        if layer_mask(state, 0) == WORD_MASK:
            successors.add(shift_state(state))
            continue

        target = first_empty(layer_mask(state, 0))

        for template in templates[target]:
            nxt = apply_template(state, template)

            if nxt is None or nxt in seen:
                continue

            seen.add(nxt)
            queue.append(nxt)

    return successors


def macro_closure(sources, templates):
    macro_seen = set(sources)
    queue = deque(sources)
    succ = {}

    while queue:
        if len(macro_seen) >= MAX_CLOSURE_STATES:
            break

        src = queue.popleft()
        successors = explore_source(src, templates)

        if successors:
            succ[src] = successors

        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                queue.append(s)

    return macro_seen, succ


def find_scc_containing_0(succ, macro_states):
    """Find the SCC containing state 0."""
    pred = {n: set() for n in macro_states}
    for u in succ:
        for v in succ[u]:
            if v in pred:
                pred[v].add(u)

    forward = set()
    stack = [0]
    while stack:
        u = stack.pop()
        if u in forward:
            continue
        forward.add(u)
        for v in succ.get(u, set()):
            if v not in forward and v in macro_states:
                stack.append(v)

    backward = set()
    stack = [0]
    while stack:
        u = stack.pop()
        if u in backward:
            continue
        backward.add(u)
        for v in pred.get(u, set()):
            if v not in backward and v in macro_states:
                stack.append(v)

    return forward & backward


def compute_backward_distances_full(macro_states, succ, scc_0, max_distance):
    """
    Compute backward distances from 0 in the full graph (SCC + DAG).
    Uses iterative approach to handle cycles in SCC.
    """
    # R[u] = set of distances d such that 0 is reachable from u in d steps
    R = {0: {0}}

    # First, compute distances within SCC (with cycle handling)
    for iteration in range(max_distance + 1):
        changed = False

        for u in scc_0:
            if u == 0:
                continue

            distances = set()
            for v in succ.get(u, set()) & scc_0:
                if v in R:
                    for d in R[v]:
                        if d + 1 <= max_distance:
                            distances.add(d + 1)

            if distances and distances != R.get(u, set()):
                R[u] = distances
                changed = True

        if not changed:
            break

    # Now propagate through DAG (states not in SCC)
    # Use topological order (reverse BFS from SCC)
    dag_states = macro_states - scc_0
    
    # BFS to find topological order
    visited = set(scc_0)
    queue = deque(scc_0)
    topo_order = []

    while queue:
        u = queue.popleft()
        if u not in scc_0:
            topo_order.append(u)

        for v in succ.get(u, set()):
            if v not in visited and v in macro_states:
                visited.add(v)
                queue.append(v)

    # Process in reverse topological order
    for u in reversed(topo_order):
        distances = set()
        for v in succ.get(u, set()):
            if v in R:
                for d in R[v]:
                    if d + 1 <= max_distance:
                        distances.add(d + 1)

        if distances:
            R[u] = distances

    return R


def main() -> int:
    print("Building templates...", flush=True)
    templates, _ = build_templates()

    print("\nStep 1: first-generation exploration...", flush=True)
    t0 = time.perf_counter()
    sources = first_generation_sources(templates)
    t1 = time.perf_counter()
    print(f"  sources: {len(sources):,} ({t1 - t0:.1f}s)", flush=True)

    print("\nStep 2: macro closure...", flush=True)
    t2 = time.perf_counter()
    macro_states, succ = macro_closure(sources, templates)
    t3 = time.perf_counter()
    print(f"  macro states: {len(macro_states):,} ({t3 - t2:.1f}s)", flush=True)

    print("\nStep 3: complete succ[0]...", flush=True)
    t4 = time.perf_counter()
    complete_succ_0 = explore_source(0, templates, MAX_INTERMEDIATE_0)
    t5 = time.perf_counter()
    print(f"  complete succ[0]: {len(complete_succ_0):,} ({t5 - t4:.1f}s)", flush=True)

    print("\nStep 4: patch succ[0]...", flush=True)
    succ[0] = complete_succ_0

    print("\nStep 5: find SCC containing 0...", flush=True)
    t6 = time.perf_counter()
    scc_0 = find_scc_containing_0(succ, macro_states)
    t7 = time.perf_counter()
    print(f"  SCC size: {len(scc_0):,} ({t7 - t6:.1f}s)", flush=True)

    print("\nStep 6: compute backward distances in full graph...", flush=True)
    t8 = time.perf_counter()
    R_full = compute_backward_distances_full(macro_states, succ, scc_0, max(TARGET_DISTANCES))
    t9 = time.perf_counter()
    print(f"  computed distances for {len(R_full)} states ({t9 - t8:.1f}s)", flush=True)

    # Check which first-gen sources can reach 0 at target distances
    print("\n=== CHECKING TARGET DISTANCES ===", flush=True)
    for target_d in TARGET_DISTANCES:
        sources_at_d = [s for s in sources if target_d in R_full.get(s, set())]
        print(f"\nDistance {target_d} (for N={target_d + 1}):", flush=True)
        print(f"  First-gen sources reaching 0: {len(sources_at_d)}", flush=True)

        if sources_at_d:
            print(f"  ✓ Distance {target_d} IS achievable!", flush=True)
            for s in sources_at_d[:3]:
                print(f"    source {s}: distances {sorted(R_full[s])}", flush=True)

    # Check if 129 is achievable
    print("\n=== CHECKING N=130 (distance 129) ===", flush=True)
    sources_at_129 = []

    for target_d in TARGET_DISTANCES:
        k = (129 - target_d) // 20
        sources_at_d = [s for s in sources if target_d in R_full.get(s, set())]

        if sources_at_d:
            print(f"\n✓ 129 = 20 * {k} + {target_d} is achievable!", flush=True)
            print(f"  {len(sources_at_d)} sources can reach 0 at distance {target_d}", flush=True)
            sources_at_129.extend(sources_at_d)

    if sources_at_129:
        print(f"\n✓✓✓ N=130 IS ACHIEVABLE! ✓✓✓", flush=True)
        print(f"Total sources that can achieve N=130: {len(set(sources_at_129))}", flush=True)
    else:
        print(f"\n✗✗✗ N=130 is NOT achievable in the current 15M-state closure ✗✗✗", flush=True)
        print(f"\nReason: No paths of length 9, 29, or 49 exist from first-gen sources to 0", flush=True)
        print(f"The 15M-state closure does not contain the necessary DAG structure", flush=True)

    # Summary
    print("\n=== SUMMARY ===", flush=True)
    print(f"SCC size: {len(scc_0)}", flush=True)
    print(f"Macro states: {len(macro_states):,}", flush=True)
    print(f"First-gen sources: {len(sources):,}", flush=True)
    print(f"Max distance in SCC: {max(max(d) for d in R_full.values() if d) if R_full else 0}", flush=True)
    print(f"States with computed distances: {len(R_full):,}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
