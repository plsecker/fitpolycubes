#!/usr/bin/env python3
"""
Macro reachability analysis for the S z-frontier (4x8), starting from the
EMPTY 96-bit frontier state.

Steps:
  1. Explore all legal placement sequences from state 0 until the FIRST
     layer shift (each path stops at its first pre-shift state).
  2. Collect all resulting post-shift states (first-generation sources).
  3. Follow the macro-transition logic (placements until the next shift)
     from those sources until closure.
  4. The macro graph is a DAG; compute:
       - number of macro states
       - number of macro edges
       - longest path in macro edges
       - post-shift states attaining that longest path
       - whether a complete 4x8xN tiling is possible for N=1..20

Tiling condition: a complete 4x8xN tiling exists iff the empty state 0 is
reachable in exactly N-1 macro edges from a first-generation source
(each macro edge = one full layer filled + one shift; the last edge must
be an immediate shift from WORD_MASK, the only way to reach 0).

The reachable macro state space is very large (>= 15M states), so the
closure is computed with a safety cap and reported as truncated; the
tiling question (N=1..20) only needs distances <= 19, which is complete
within the capped closure because the closure BFS processes nodes in
non-decreasing distance order.

Reuses the solver's pure functions with identical semantics; the solver
itself is NOT modified and its discovery loop is not run.
"""

from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
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

# Safety caps (reported if hit).
MAX_FIRSTGEN_STATES = 5_000_000   # first-generation tree
MAX_INTERMEDIATE = 1_000_000      # per-source interval exploration
MAX_CLOSURE_STATES = 15_000_000   # macro closure

EMPTY = frozenset()


def first_generation_sources(
    templates: dict,
) -> tuple[set[int], int, bool]:
    """
    BFS from the empty state 0, stopping each path at its first layer
    shift.  Returns (sources, tree_states, hit_cap).
    """
    sources: set[int] = set()
    seen: set[int] = {0}
    queue: deque[int] = deque([0])
    hit_cap = False

    while queue:
        if len(seen) >= MAX_FIRSTGEN_STATES:
            hit_cap = True
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

    return sources, len(seen), hit_cap


def explore_source(
    source: int,
    templates: dict,
) -> tuple[set[int], int, bool]:
    """
    Explore the placement interval from a post-shift source until the
    next layer shift.  Returns (successors, intermediate_count, hit_limit).
    """
    successors: set[int] = set()
    seen: set[int] = {source}
    queue: deque[int] = deque([source])
    hit_limit = False

    while queue:
        if len(seen) - 1 >= MAX_INTERMEDIATE:
            hit_limit = True
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

    return successors, len(seen) - 1, hit_limit


def macro_closure(
    sources: list[int],
    templates: dict,
) -> tuple[set[int], dict[int, set[int]], int, bool, int, dict[int, int]]:
    """
    Iterate the macro transition to closure from the given sources.
    Returns (macro_states, succ, edge_count, hit_cap, total_intermediate,
    dist) where dist[v] = BFS distance (macro edges) from a source to v.
    """
    macro_seen: set[int] = set(sources)
    queue: deque[int] = deque(sources)
    succ: dict[int, set[int]] = {}
    dist: dict[int, int] = {s: 0 for s in sources}
    edge_count = 0
    hit_cap = False
    total_intermediate = 0

    while queue:
        if len(macro_seen) >= MAX_CLOSURE_STATES:
            hit_cap = True
            break

        src = queue.popleft()
        successors, intermediate, _ = explore_source(src, templates)
        total_intermediate += intermediate

        if successors:
            succ[src] = successors
            edge_count += len(successors)

        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                dist[s] = dist[src] + 1
                queue.append(s)

    return macro_seen, succ, edge_count, hit_cap, total_intermediate, dist


def kahn_dag_check(
    nodes: set[int],
    succ: dict[int, set[int]],
) -> tuple[bool, int]:
    """
    Kahn's algorithm: returns (is_dag, order_length).  If the graph has a
    cycle, order_length < len(nodes).
    """
    indeg = {n: 0 for n in nodes}

    for u in succ:
        for v in succ[u]:
            indeg[v] += 1

    queue = deque([n for n in nodes if indeg[n] == 0])
    count = 0

    while queue:
        u = queue.popleft()
        count += 1

        for v in succ.get(u, EMPTY):
            indeg[v] -= 1

            if indeg[v] == 0:
                queue.append(v)

    return count == len(nodes), count


def main() -> int:
    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    # ---- Step 1-2: first-generation exploration from the empty state ----
    print("Step 1-2: first-generation exploration from state 0...", flush=True)
    t0 = time.perf_counter()
    sources, tree_states, fg_hit = first_generation_sources(templates)
    t1 = time.perf_counter()
    print(
        f"  first-generation tree states: {tree_states:,} "
        f"(cap {MAX_FIRSTGEN_STATES:,} hit: {fg_hit})",
        flush=True,
    )
    print(
        f"  first-generation post-shift sources: {len(sources):,} "
        f"({t1 - t0:.1f}s)",
        flush=True,
    )

    # ---- Step 3: macro closure (capped) ----
    print("Step 3: macro closure (capped)...", flush=True)
    t2 = time.perf_counter()
    macro_states, succ, edge_count, closure_hit, total_intermediate, dist = (
        macro_closure(sorted(sources), templates)
    )
    t3 = time.perf_counter()
    print(
        f"  macro states: {len(macro_states):,} "
        f"(cap {MAX_CLOSURE_STATES:,} hit: {closure_hit})",
        flush=True,
    )
    print(
        f"  macro edges: {edge_count:,} "
        f"total intermediate: {total_intermediate:,} ({t3 - t2:.1f}s)",
        flush=True,
    )

    # Distance-<=19 completeness: the closure BFS processes nodes in
    # non-decreasing distance order, so if the max processed distance is
    # >= 20 (or the closure is complete), the distance-<=19 subgraph is
    # fully explored.
    max_dist_processed = max(dist.values()) if dist else 0
    complete_through_19 = (not closure_hit) or max_dist_processed >= 20
    print(
        f"  max BFS distance in capped closure: {max_dist_processed}",
        flush=True,
    )
    print(
        f"  distance-<=19 subgraph complete: {complete_through_19}",
        flush=True,
    )

    # ---- Step 4: DAG check + longest path ----
    print("DAG check (Kahn) on capped closure...", flush=True)
    t4 = time.perf_counter()
    is_dag, order_len = kahn_dag_check(macro_states, succ)
    t5 = time.perf_counter()
    print(
        f"  is_dag={is_dag} (order {order_len:,}/{len(macro_states):,}) "
        f"({t5 - t4:.1f}s)",
        flush=True,
    )

    # Longest path (edges) from sources: dist is BFS distance (shortest).
    # For the longest path we need a longest-path DP over the DAG.
    # Reuse Kahn's order: recompute a topological order.
    print("Longest-path DP...", flush=True)
    indeg = {n: 0 for n in macro_states}

    for u in succ:
        for v in succ[u]:
            indeg[v] += 1

    queue = deque([n for n in macro_states if indeg[n] == 0])
    order: list[int] = []

    while queue:
        u = queue.popleft()
        order.append(u)

        for v in succ.get(u, EMPTY):
            indeg[v] -= 1

            if indeg[v] == 0:
                queue.append(v)

    lp: dict[int, int] = {n: 0 for n in macro_states}

    for u in order:
        for v in succ.get(u, EMPTY):
            if lp[u] + 1 > lp[v]:
                lp[v] = lp[u] + 1

    longest = max(lp.values())
    endpoints = sorted(n for n in macro_states if lp[n] == longest)

    # fwd[v] = longest path from v to a terminal.
    fwd: dict[int, int] = {n: 0 for n in macro_states}

    for u in reversed(order):
        for v in succ.get(u, EMPTY):
            if fwd[v] + 1 > fwd[u]:
                fwd[u] = fwd[v] + 1

    longest_sources = sorted(
        s for s in sources if lp[s] + fwd[s] == longest
    )

    print()
    print("=== MACRO GRAPH (from empty state, capped) ===")
    print(f"First-generation sources: {len(sources):,}")
    print(f"Macro states (capped): {len(macro_states):,}")
    print(f"Macro edges (capped): {edge_count:,}")
    print(f"Longest path (macro edges, capped): {longest}")
    print(f"Endpoints attaining longest path: {len(endpoints):,}")
    print(f"Sources starting longest paths: {len(longest_sources):,}")
    print(f"DAG: {is_dag}")

    # ---- Tiling question: 0 reachable in exactly N-1 edges ----
    # Layer BFS: layer_d = nodes reachable from a source in exactly d edges.
    print()
    print("=== TILING QUESTION (4x8xN, N=1..20) ===")
    print(f"Empty state 0 in macro states: {0 in macro_states}")

    zero_dists: list[int] = []
    layer: set[int] = set(sources)

    for d in range(0, 21):
        if 0 in layer:
            zero_dists.append(d)

        nxt_layer: set[int] = set()

        for u in layer:
            nxt_layer.update(succ.get(u, EMPTY))

        layer = nxt_layer

    print(f"Distances at which 0 is reachable: {zero_dists}")

    print()
    print("| N | 32N/5 integer | 0 reachable in N-1 edges | 4x8xN tileable |")
    print("|---|---|---|---|")

    tiling_results = []

    for N in range(1, 21):
        div_ok = (32 * N) % 5 == 0
        reach = (N - 1) in zero_dists
        tileable = div_ok and reach
        tiling_results.append((N, div_ok, reach, tileable))
        print(
            f"| {N} | {'yes' if div_ok else 'no'} | "
            f"{'yes' if reach else 'no'} | "
            f"{'YES' if tileable else 'no'} |"
        )

    # ---- Dump machine-readable results ----
    out = REPO_ROOT / "docs" / "frontier" / "results" / "macro_reachability_results.txt"
    lines = [
        f"firstgen_tree_states={tree_states}",
        f"firstgen_hit_cap={fg_hit}",
        f"firstgen_sources={len(sources)}",
        f"macro_states={len(macro_states)}",
        f"macro_edges={edge_count}",
        f"closure_hit_cap={closure_hit}",
        f"total_intermediate={total_intermediate}",
        f"max_bfs_distance={max_dist_processed}",
        f"complete_through_19={complete_through_19}",
        f"is_dag={is_dag}",
        f"longest_path={longest}",
        f"endpoints_count={len(endpoints)}",
        f"longest_sources_count={len(longest_sources)}",
        f"zero_in_macro={0 in macro_states}",
        f"zero_distances={zero_dists}",
        f"firstgen_elapsed={t1 - t0:.1f}",
        f"closure_elapsed={t3 - t2:.1f}",
        f"dag_elapsed={t5 - t4:.1f}",
    ]

    for N, div_ok, reach, tileable in tiling_results:
        lines.append(
            f"tiling_N{N}={tileable} (div={div_ok}, reach={reach})"
        )

    lines.append(f"endpoints={endpoints[:50]}")
    lines.append(f"longest_sources={longest_sources[:50]}")
    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())