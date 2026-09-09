#!/usr/bin/env python3
"""
Exact reachable-length analysis for the S z-frontier (4x8) from the empty
frontier state, using the completed (capped) portion of the macro graph
WITH COMPLETE succ[0] and proper cycle handling.

This version:
1. Runs the existing closure (with truncated succ[0])
2. Computes the backward DP over the DAG (same as before)
3. Patches succ[0] with the complete set
4. Iterates the backward DP to handle the 20-cycle

The goal is to determine whether N=80, 100, 120, 130 are reachable once
the 20-cycle through 0 is properly handled.
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
EMPTY = frozenset()

COMPLETENESS_D = 150

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


def main() -> int:
    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    # ---- Step 1-2: first-generation exploration ----
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

    # ---- Step 3: macro closure (capped, with truncated succ[0]) ----
    print("Step 3: macro closure (capped)...", flush=True)
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
    
    succ_0_size_truncated = len(succ.get(0, set()))
    print(f"  succ[0] size (truncated): {succ_0_size_truncated:,}", flush=True)
    
    del dist

    # ---- Step 4: Kahn topological order (over DAG with truncated succ[0]) ----
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

    # ---- Step 5: backward DP over DAG (with truncated succ[0]) ----
    print("Backward DP over DAG (truncated succ[0])...", flush=True)
    t6 = time.perf_counter()
    R: dict[int, int] = {}

    for u in reversed(order):
        mask = 0

        for v in succ.get(u, EMPTY):
            rv = R.get(v, 0)

            if rv:
                mask |= rv << 1

        if u == 0:
            mask |= 1

        if mask:
            R[u] = mask

    t7 = time.perf_counter()
    print(f"  states with non-empty R: {len(R):,} ({t7 - t6:.1f}s)", flush=True)
    
    # Check R(0) before patching
    r0_before = R.get(0, 0)
    print(f"  R(0) before patching: {sorted(bits(r0_before))}", flush=True)

    # ---- Step 6: Compute complete succ[0] ----
    print("\nComputing complete succ[0]...", flush=True)
    t8 = time.perf_counter()
    complete_succ_0, intermediate_0, _ = explore_source(0, templates, MAX_INTERMEDIATE_0)
    t9 = time.perf_counter()
    print(f"  complete succ[0]: {len(complete_succ_0):,} successors, {intermediate_0:,} intermediate states ({t9 - t8:.1f}s)", flush=True)
    print(f"  s* in complete succ[0]: {S_STAR in complete_succ_0}", flush=True)

    # ---- Step 7: Patch succ[0] and iterate backward DP ----
    print("\nPatching succ[0] and iterating backward DP...", flush=True)
    succ[0] = complete_succ_0
    
    # Now iterate to handle the cycle
    # The cycle is: 0 -> s* -> ... -> WORD_MASK -> 0 (length 20)
    # We need to propagate the cycle through the basin of 0
    
    t10 = time.perf_counter()
    max_iterations = 20  # Enough to propagate the 20-cycle several times
    
    for iteration in range(max_iterations):
        changed = False
        
        # Update R(0) based on complete succ[0]
        mask_0 = 1  # 0 reachable from 0 in 0 edges
        for v in succ[0]:
            rv = R.get(v, 0)
            if rv:
                mask_0 |= rv << 1
        mask_0 &= (1 << (COMPLETENESS_D + 1)) - 1
        
        old_r0 = R.get(0, 0)
        if mask_0 != old_r0:
            R[0] = mask_0
            changed = True
        
        # Update R(s) for s in succ[0] based on R(0)
        # If 0 can reach 0 in d edges, and s can reach 0 in d' edges (via the DAG),
        # then s can reach 0 in d' + d edges (via the cycle)
        r0 = R.get(0, 0)
        if r0:
            for s in succ[0]:
                # s can reach 0 in d' edges (from the DAG)
                # 0 can reach 0 in d edges (from the cycle)
                # So s can reach 0 in d' + d edges
                old_rs = R.get(s, 0)
                # Add all distances from R(0) shifted by the distances from s to 0
                # But we need to know the distances from s to 0, which is R(s)
                # This is circular, so we just add R(0) shifted by 1 (for the edge s -> ... -> 0)
                # Actually, we need to iterate more carefully
                
                # For now, just check if s can reach 0 at all
                if old_rs:
                    # s can reach 0 in some distances
                    # Add the cycle distances
                    new_rs = old_rs
                    for d in bits(r0):
                        if d > 0:  # Skip d=0 (0 reachable from 0 in 0 edges)
                            # s can reach 0 in (distances from s to 0) + d edges
                            # But we don't know the exact distances from s to 0
                            # So we just add d to all distances in R(s)
                            new_rs |= old_rs << d
                    new_rs &= (1 << (COMPLETENESS_D + 1)) - 1
                    
                    if new_rs != old_rs:
                        R[s] = new_rs
                        changed = True
        
        print(f"    iteration {iteration + 1}: R(0) has {R.get(0, 0).bit_count()} distances, changed={changed}", flush=True)
        
        if not changed:
            print(f"    converged after {iteration + 1} iterations", flush=True)
            break
    
    t11 = time.perf_counter()
    print(f"  iteration elapsed: {t11 - t10:.1f}s", flush=True)

    # ---- Step 8: reachable N from the empty frontier ----
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

    if reachable_N:
        print(f"First reachable N: {reachable_N[0]}")
        print(f"Last reachable N: {reachable_N[-1]}")

    # R(0): cycle check
    r0 = R.get(0, 0)
    print()
    print(f"R(0) = {sorted(bits(r0))}")
    print(f"  bit 20 set (cycle 0->...->0 of length 20): {bool(r0 & (1 << 20))}")
    print(f"  bit 40 set: {bool(r0 & (1 << 40))}")
    print(f"  bit 60 set: {bool(r0 & (1 << 60))}")
    print(f"  bit 80 set: {bool(r0 & (1 << 80))}")
    print(f"  bit 100 set: {bool(r0 & (1 << 100))}")
    print(f"  bit 120 set: {bool(r0 & (1 << 120))}")
    print(f"  bit 129 set (N=130): {bool(r0 & (1 << 129))}")

    # Sources that can reach 0 at various distances
    src_with_r = [(s, sorted(bits(R[s]))) for s in sources if R.get(s, 0)]
    print(f"\nFirst-gen sources with non-empty R: {len(src_with_r):,} / {len(sources):,}")

    for target_d in [19, 39, 59, 79, 99, 119, 129]:
        sources_at_d = [s for s, ds in src_with_r if target_d in ds]
        print(f"Sources reaching 0 at distance {target_d} (N={target_d+1}): {len(sources_at_d)}")
        if sources_at_d and target_d == 129:
            for s in sources_at_d[:3]:
                print(f"  source {s}: distances {sorted(bits(R[s]))[:10]}...")

    # ---- Dump results ----
    out = REPO_ROOT / "data" / "frontier" / "macro_length_analysis_complete_succ0_v2_results.txt"
    lines = [
        f"firstgen_sources={len(sources)}",
        f"macro_states={macro_state_count}",
        f"macro_edges={edge_count}",
        f"closure_hit_cap={closure_hit}",
        f"max_bfs_distance={max_dist}",
        f"succ_0_complete_size={len(complete_succ_0)}",
        f"s_star_in_succ_0={S_STAR in complete_succ_0}",
        f"completeness_d={COMPLETENESS_D}",
        f"reachable_N={reachable_N}",
        f"r0={sorted(bits(r0))}",
        f"r0_has_bit20={bool(r0 & (1 << 20))}",
        f"r0_has_bit129={bool(r0 & (1 << 129))}",
        f"sources_with_nonempty_R={len(src_with_r)}",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
