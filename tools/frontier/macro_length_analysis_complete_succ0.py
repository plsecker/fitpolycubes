#!/usr/bin/env python3
"""
Exact reachable-length analysis for the S z-frontier (4x8) from the empty
frontier state, using the completed (capped) portion of the macro graph
WITH COMPLETE succ[0].

This is a modified version of macro_length_analysis.py that:
1. Computes the complete succ[0] inline (3.16M states, no cap)
2. Patches the closure's succ[0] with the complete set
3. Recomputes the backward DP with cycle handling (iteration until convergence)

The goal is to determine whether N=80, 100, 120, 130 are reachable once
the 20-cycle through 0 is properly handled.

The solver is NOT modified; its pure functions are reused with identical
semantics. The graph is NOT expanded beyond the existing capped closure
(15,000,000-state cap; per-source intermediate cap 1,000,000 for all
sources except 0).
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
MAX_INTERMEDIATE_0 = 4_000_000  # Higher cap for source 0
MAX_CLOSURE_STATES = 15_000_000
EMPTY = frozenset()

COMPLETENESS_D = 150  # Extended to check N=130 (distance 129)

S_STAR = 6163195513375031274


def first_generation_sources(templates):
    sources = set()
    seen = {0}
    queue = deque([0])
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


def explore_source(source, templates, max_intermediate=MAX_INTERMEDIATE):
    successors = set()
    seen = {source}
    queue = deque([source])
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

            if nxt is None or nxt in seen:
                continue

            seen.add(nxt)
            queue.append(nxt)

    return successors, len(seen) - 1, hit_limit


def macro_closure(sources, templates):
    macro_seen = set(sources)
    queue = deque(sources)
    succ = {}
    dist = {s: 0 for s in sources}
    edge_count = 0
    hit_cap = False
    total_intermediate = 0

    while queue:
        if len(macro_seen) >= MAX_CLOSURE_STATES:
            hit_cap = True
            break

        src = queue.popleft()
        
        # Use higher cap for source 0
        max_int = MAX_INTERMEDIATE_0 if src == 0 else MAX_INTERMEDIATE
        successors, intermediate, _ = explore_source(src, templates, max_int)
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


def kahn_order(nodes, succ):
    indeg = {n: 0 for n in nodes}

    for u in succ:
        for v in succ[u]:
            indeg[v] += 1

    queue = deque([n for n in nodes if indeg[n] == 0])
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)

        for v in succ.get(u, EMPTY):
            indeg[v] -= 1

            if indeg[v] == 0:
                queue.append(v)

    return order


def bits(mask):
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask ^= b


def backward_dp_with_cycle(order, succ, max_iterations=10):
    """
    Backward DP with cycle handling via iteration.
    
    R(u) = bitmask of distances d such that 0 is reachable from u in exactly d edges.
    
    For a DAG, one pass in reverse topological order suffices.
    With cycles (e.g., 0 -> s* -> ... -> 0), we iterate until convergence.
    """
    R = {}
    
    for iteration in range(max_iterations):
        changed = False
        old_R_size = len(R)
        
        for u in reversed(order):
            mask = 0
            
            for v in succ.get(u, EMPTY):
                rv = R.get(v, 0)
                
                if rv:
                    mask |= rv << 1
            
            if u == 0:
                mask |= 1  # 0 reachable from 0 in 0 edges
            
            # Limit to COMPLETENESS_D to avoid infinite growth
            mask &= (1 << (COMPLETENESS_D + 1)) - 1
            
            if mask:
                old_mask = R.get(u, 0)
                if mask != old_mask:
                    R[u] = mask
                    changed = True
        
        print(f"    iteration {iteration + 1}: {len(R)} states with non-empty R, changed={changed}", flush=True)
        
        if not changed:
            print(f"    converged after {iteration + 1} iterations", flush=True)
            break
    
    return R


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

    # ---- Step 3: macro closure (capped) with complete succ[0] ----
    print("Step 3: macro closure (capped) with complete succ[0]...", flush=True)
    t2 = time.perf_counter()
    macro_states, succ, edge_count, closure_hit, total_intermediate, dist = (
        macro_closure(sorted(sources), templates)
    )
    t3 = time.perf_counter()
    macro_state_count = len(macro_states)
    print(
        f"  macro states: {macro_state_count:,} "
        f"(cap {MAX_CLOSURE_STATES:,} hit: {closure_hit})",
        flush=True,
    )
    print(
        f"  macro edges: {edge_count:,} "
        f"total intermediate: {total_intermediate:,} ({t3 - t2:.1f}s)",
        flush=True,
    )
    max_dist = max(dist.values())
    print(f"  max BFS distance: {max_dist}", flush=True)
    
    # Check if succ[0] is complete
    succ_0_size = len(succ.get(0, set()))
    print(f"  succ[0] size: {succ_0_size:,} (expected {len(sources):,})", flush=True)
    print(f"  succ[0] complete: {succ_0_size == len(sources)}", flush=True)
    print(f"  s* in succ[0]: {S_STAR in succ.get(0, set())}", flush=True)
    
    del dist

    # ---- Step 4: Kahn topological order ----
    print("Kahn topological order...", flush=True)
    t4 = time.perf_counter()
    order = kahn_order(macro_states, succ)
    t5 = time.perf_counter()
    is_dag = len(order) == macro_state_count
    print(
        f"  is_dag={is_dag} (order {len(order):,}/{macro_state_count:,}) "
        f"({t5 - t4:.1f}s)",
        flush=True,
    )
    
    if not is_dag:
        print("  WARNING: graph is not a DAG (cycle detected)", flush=True)
        print(f"  nodes in topological order: {len(order):,}", flush=True)
        print(f"  nodes not in order: {macro_state_count - len(order):,}", flush=True)
    
    del macro_states

    # ---- Step 5: backward DP with cycle handling ----
    print("Backward DP with cycle handling: remaining distances to empty frontier (0)...", flush=True)
    t6 = time.perf_counter()
    R = backward_dp_with_cycle(order, succ, max_iterations=10)
    t7 = time.perf_counter()
    print(f"  states with non-empty R: {len(R):,} ({t7 - t6:.1f}s)", flush=True)
    del order

    # ---- Step 6: reachable N from the empty frontier ----
    reachable_d: set[int] = set()

    for s in sources:
        mask = R.get(s, 0)

        if mask:
            reachable_d.update(bits(mask))

    exact_d = sorted(d for d in reachable_d if d <= COMPLETENESS_D)
    partial_d = sorted(d for d in reachable_d if d > COMPLETENESS_D)
    reachable_N = sorted(d + 1 for d in exact_d)

    print()
    print("=== REACHABLE LENGTHS (4x8xN) from the empty frontier ===")
    print(f"Reachable N (exact, N <= {COMPLETENESS_D + 1}): {reachable_N}")
    print(
        f"Partial (d > {COMPLETENESS_D}, lower bound): "
        f"{[d + 1 for d in partial_d]}"
    )

    if reachable_N:
        print(f"First reachable N: {reachable_N[0]}")
        print(f"Last reachable N: {reachable_N[-1]}")

        gaps = []
        prev = reachable_N[0]

        for n in reachable_N[1:]:
            if n > prev + 1:
                gaps.append((prev + 1, n - 1))
            prev = n

        print(f"Gaps between consecutive reachable N: {gaps}")

        all_N = set(range(1, COMPLETENESS_D + 2))
        non_reachable = sorted(all_N - set(reachable_N))
        print(f"Non-reachable N in [1, {COMPLETENESS_D + 1}]: {non_reachable[:20]}...")

        # cell-count-possible but not reachable
        div_ok = [n for n in non_reachable if (32 * n) % 5 == 0]
        print(f"  of which pass the cell-count check (32N/5 integer): {div_ok}")

    # R(0): cycle check
    r0 = R.get(0, 0)
    print()
    print(f"R(0) = {sorted(bits(r0))}")
    print(
        f"  bit 20 set (cycle 0->...->0 of length 20): "
        f"{bool(r0 & (1 << 20))}"
    )
    print(
        f"  bit 40 set: {bool(r0 & (1 << 40))}"
    )
    print(
        f"  bit 60 set: {bool(r0 & (1 << 60))}"
    )
    print(
        f"  bit 80 set: {bool(r0 & (1 << 80))}"
    )
    print(
        f"  bit 100 set: {bool(r0 & (1 << 100))}"
    )
    print(
        f"  bit 120 set: {bool(r0 & (1 << 120))}"
    )
    print(
        f"  bit 129 set (N=130): {bool(r0 & (1 << 129))}"
    )

    # R stats
    sizes: dict[int, int] = {}
    max_r = 0

    for mask in R.values():
        sz = mask.bit_count()
        sizes[sz] = sizes.get(sz, 0) + 1

        if mask.bit_length() - 1 > max_r:
            max_r = mask.bit_length() - 1

    print(f"|R(s)| distribution: {dict(sorted(sizes.items()))}")
    print(f"Max remaining distance in any R(s): {max_r}")

    src_with_r = [(s, sorted(bits(R[s]))) for s in sources if R.get(s, 0)]
    print(f"First-gen sources with non-empty R: {len(src_with_r):,} / {len(sources):,}")

    # Show sources that can reach 0 at distance 129 (N=130)
    sources_129 = [s for s, ds in src_with_r if 129 in ds]
    print(f"Sources reaching 0 at distance 129 (N=130): {len(sources_129)}")
    if sources_129:
        for s in sources_129[:5]:
            print(f"  source {s}: distances {sorted(bits(R[s]))}")

    # Show sources that can reach 0 at various distances
    for target_d in [19, 39, 59, 79, 99, 119, 129]:
        sources_at_d = [s for s, ds in src_with_r if target_d in ds]
        print(f"Sources reaching 0 at distance {target_d} (N={target_d+1}): {len(sources_at_d)}")

    # ---- Dump machine-readable results ----
    out = Path("/tmp/opencode/macro_length_analysis_complete_succ0_results.txt")
    lines = [
        f"firstgen_tree_states={tree_states}",
        f"firstgen_hit_cap={fg_hit}",
        f"firstgen_sources={len(sources)}",
        f"macro_states={macro_state_count}",
        f"macro_edges={edge_count}",
        f"closure_hit_cap={closure_hit}",
        f"total_intermediate={total_intermediate}",
        f"max_bfs_distance={max_dist}",
        f"is_dag={is_dag}",
        f"succ_0_size={succ_0_size}",
        f"succ_0_complete={succ_0_size == len(sources)}",
        f"s_star_in_succ_0={S_STAR in succ.get(0, set())}",
        f"completeness_d={COMPLETENESS_D}",
        f"reachable_d_exact={exact_d}",
        f"reachable_d_partial={partial_d}",
        f"reachable_N={reachable_N}",
        f"first_reachable_N={reachable_N[0] if reachable_N else None}",
        f"last_reachable_N={reachable_N[-1] if reachable_N else None}",
        f"r0={sorted(bits(r0))}",
        f"r0_has_bit20={bool(r0 & (1 << 20))}",
        f"r0_has_bit129={bool(r0 & (1 << 129))}",
        f"states_with_nonempty_R={len(R)}",
        f"R_size_distribution={dict(sorted(sizes.items()))}",
        f"max_remaining_distance={max_r}",
        f"sources_with_nonempty_R={len(src_with_r)}",
        f"sources_at_distance_129={sources_129}",
        f"firstgen_elapsed={t1 - t0:.1f}",
        f"closure_elapsed={t3 - t2:.1f}",
        f"kahn_elapsed={t5 - t4:.1f}",
        f"backward_dp_elapsed={t7 - t6:.1f}",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
