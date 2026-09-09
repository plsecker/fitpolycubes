#!/usr/bin/env python3
"""
Check if distance 129 (N=130) is achievable in the macro graph.

This script:
1. Recomputes the 15M-state closure
2. Patches succ[0] with complete set
3. Identifies the 226-state SCC
4. Computes backward reachability from 0 within the SCC
5. Computes backward reachability from SCC states in the DAG
6. Checks if any first-gen source can reach 0 at distance 129
"""

from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
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
TARGET_DISTANCE = 129  # For N=130


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
    # Build reverse graph
    pred = {n: set() for n in macro_states}
    for u in succ:
        for v in succ[u]:
            if v in pred:
                pred[v].add(u)

    # Forward DFS from 0
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

    # Backward DFS from 0
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


def compute_backward_distances(scc, succ, max_distance):
    """
    Compute backward distances from 0 within the SCC.
    Returns dict: state -> set of distances at which 0 is reachable
    """
    # R[u] = set of distances d such that 0 is reachable from u in d steps
    R = {0: {0}}

    # Iterate until convergence or max_distance
    for iteration in range(max_distance + 1):
        changed = False

        for u in scc:
            if u == 0:
                continue

            distances = set()
            for v in succ.get(u, set()) & scc:
                if v in R:
                    for d in R[v]:
                        if d + 1 <= max_distance:
                            distances.add(d + 1)

            if distances and distances != R.get(u, set()):
                R[u] = distances
                changed = True

        if not changed:
            break

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

    print("\nStep 6: compute backward distances within SCC...", flush=True)
    t8 = time.perf_counter()
    R_scc = compute_backward_distances(scc_0, succ, TARGET_DISTANCE)
    t9 = time.perf_counter()
    print(f"  computed distances for {len(R_scc)} states ({t9 - t8:.1f}s)", flush=True)

    # Check which states can reach 0 at distance 129
    states_at_129 = [s for s, distances in R_scc.items() if TARGET_DISTANCE in distances]
    print(f"\n  States in SCC reaching 0 at distance {TARGET_DISTANCE}: {len(states_at_129)}", flush=True)

    # Check which first-gen sources are in the SCC
    sources_in_scc = sources & scc_0
    print(f"  First-gen sources in SCC: {len(sources_in_scc)}", flush=True)

    # Check if any source can reach 0 at distance 129
    sources_at_129_in_scc = [s for s in sources_in_scc if TARGET_DISTANCE in R_scc.get(s, set())]
    print(f"  Sources reaching 0 at distance {TARGET_DISTANCE}: {len(sources_at_129_in_scc)}", flush=True)

    if sources_at_129_in_scc:
        print(f"\n✓ N=130 IS ACHIEVABLE within the SCC!", flush=True)
        for s in sources_at_129_in_scc[:5]:
            print(f"  source {s}: distances {sorted(R_scc[s])}", flush=True)
    else:
        print(f"\n✗ N=130 is NOT achievable within the SCC", flush=True)
        print(f"  Need to check paths through the DAG", flush=True)

    # Analyze the distance structure
    print("\n=== DISTANCE ANALYSIS ===", flush=True)
    all_distances = set()
    for distances in R_scc.values():
        all_distances.update(distances)

    print(f"Distinct distances found: {len(all_distances)}", flush=True)
    print(f"Max distance: {max(all_distances) if all_distances else 0}", flush=True)
    print(f"Distances: {sorted(all_distances)[:50]}...", flush=True)

    # Check multiples of 20
    multiples_of_20 = [d for d in all_distances if d % 20 == 0]
    print(f"\nMultiples of 20 found: {sorted(multiples_of_20)}", flush=True)

    # Check if 129 is achievable by combining cycles
    # 129 = 20 * k + r, where r is a distance in the SCC
    print(f"\n=== CHECKING 129 = 20k + r ===", flush=True)
    for k in range(7):  # 20 * 6 = 120, 20 * 7 = 140
        r = TARGET_DISTANCE - 20 * k
        if r >= 0 and r in all_distances:
            print(f"  129 = 20 * {k} + {r} ✓", flush=True)
        elif r >= 0:
            print(f"  129 = 20 * {k} + {r} ✗ (distance {r} not found)", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
