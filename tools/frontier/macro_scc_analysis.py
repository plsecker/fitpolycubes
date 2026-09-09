#!/usr/bin/env python3
"""
SCC analysis of the macro graph with complete succ[0].

This script:
1. Recomputes the 15M-state macro closure (with truncated succ[0])
2. Patches succ[0] with the complete first-generation sources
3. Runs Tarjan's SCC algorithm
4. Analyzes the SCC structure, especially the SCC containing state 0

The goal is to understand the cycle structure and whether paths of length
129 (N=130) are possible in the existing 15M-state graph.
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


def tarjan_scc(nodes, succ):
    """
    Iterative Tarjan's SCC algorithm.
    Returns list of SCCs (each SCC is a list of nodes).
    """
    index_counter = [0]
    stack = []
    on_stack = set()
    indices = {}
    lowlink = {}
    sccs = []

    for root in nodes:
        if root in indices:
            continue

        # Iterative DFS
        work = [(root, None, False)]  # (node, parent, processed)

        while work:
            node, parent, processed = work[-1]

            if not processed:
                # First visit
                if node in indices:
                    work.pop()
                    continue

                indices[node] = index_counter[0]
                lowlink[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)

                work[-1] = (node, parent, True)

                # Push successors
                for nxt in succ.get(node, EMPTY):
                    if nxt not in indices:
                        work.append((nxt, node, False))
                    elif nxt in on_stack:
                        lowlink[node] = min(lowlink[node], indices[nxt])
            else:
                # Post-processing
                work.pop()

                if parent is not None:
                    lowlink[parent] = min(lowlink[parent], lowlink[node])

                if lowlink[node] == indices[node]:
                    # Root of an SCC
                    comp = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        comp.append(w)
                        if w == node:
                            break
                    sccs.append(comp)

    return sccs


def main() -> int:
    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    # ---- Step 1: first-generation exploration ----
    print("\nStep 1: first-generation exploration from state 0...", flush=True)
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

    # ---- Step 2: macro closure (capped, with truncated succ[0]) ----
    print("\nStep 2: macro closure (capped)...", flush=True)
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

    succ_0_truncated = len(succ.get(0, set()))
    print(f"  succ[0] size (truncated): {succ_0_truncated:,}", flush=True)

    # ---- Step 3: compute complete succ[0] ----
    print("\nStep 3: computing complete succ[0]...", flush=True)
    t4 = time.perf_counter()
    complete_succ_0, intermediate_0, _ = explore_source(0, templates, MAX_INTERMEDIATE_0)
    t5 = time.perf_counter()
    print(
        f"  complete succ[0]: {len(complete_succ_0):,} successors, "
        f"{intermediate_0:,} intermediate states ({t5 - t4:.1f}s)",
        flush=True,
    )
    print(f"  s* in complete succ[0]: {S_STAR in complete_succ_0}", flush=True)

    # ---- Step 4: patch succ[0] ----
    print("\nStep 4: patching succ[0] with complete set...", flush=True)
    succ[0] = complete_succ_0
    print(f"  succ[0] now has {len(succ[0]):,} successors", flush=True)

    # ---- Step 5: Tarjan SCC ----
    print("\nStep 5: Tarjan SCC algorithm...", flush=True)
    t6 = time.perf_counter()
    sccs = tarjan_scc(macro_states, succ)
    t7 = time.perf_counter()
    print(f"  found {len(sccs):,} SCCs ({t7 - t6:.1f}s)", flush=True)

    # ---- Step 6: analyze SCC structure ----
    print("\n=== SCC ANALYSIS ===", flush=True)

    # Find SCC containing 0
    scc_of_0 = None
    for scc in sccs:
        if 0 in scc:
            scc_of_0 = set(scc)
            break

    if scc_of_0 is None:
        print("  ERROR: state 0 not found in any SCC!", flush=True)
        return 1

    print(f"\nSCC containing state 0:", flush=True)
    print(f"  size: {len(scc_of_0):,}", flush=True)
    print(f"  is s* in this SCC: {S_STAR in scc_of_0}", flush=True)
    print(f"  is WORD_MASK in this SCC: {WORD_MASK in scc_of_0}", flush=True)

    # Check if this SCC is exactly the 20-cycle
    # The 20-cycle should contain: 0, s*, and 18 other states on the path
    # We know the path from s* to 0 has length 19, so the cycle has 20 states
    print(f"  expected size for 20-cycle: 20", flush=True)
    print(f"  actual size: {len(scc_of_0)}", flush=True)

    if len(scc_of_0) == 20:
        print(f"  ✓ SCC size matches 20-cycle", flush=True)
    else:
        print(f"  ✗ SCC size does NOT match 20-cycle", flush=True)
        print(f"    additional states in SCC: {len(scc_of_0) - 20}", flush=True)

    # Count trivial vs nontrivial SCCs
    trivial_sccs = [scc for scc in sccs if len(scc) == 1]
    nontrivial_sccs = [scc for scc in sccs if len(scc) > 1]

    # Check for self-loops in trivial SCCs
    self_loop_sccs = []
    for scc in trivial_sccs:
        node = scc[0]
        if node in succ.get(node, set()):
            self_loop_sccs.append(node)

    print(f"\nSCC size distribution:", flush=True)
    print(f"  trivial SCCs (size 1): {len(trivial_sccs):,}", flush=True)
    print(f"  nontrivial SCCs (size > 1): {len(nontrivial_sccs):,}", flush=True)
    print(f"  trivial SCCs with self-loops: {len(self_loop_sccs):,}", flush=True)

    if nontrivial_sccs:
        print(f"\nNontrivial SCCs:", flush=True)
        for i, scc in enumerate(sorted(nontrivial_sccs, key=len, reverse=True)[:10]):
            print(f"  SCC {i+1}: size {len(scc)}", flush=True)
            if 0 in scc:
                print(f"    ✓ contains state 0", flush=True)
            if S_STAR in scc:
                print(f"    ✓ contains s*", flush=True)

    # ---- Step 7: build condensation graph ----
    print("\n=== CONDENSATION GRAPH ===", flush=True)

    # Map each node to its SCC index
    node_to_scc = {}
    for i, scc in enumerate(sccs):
        for node in scc:
            node_to_scc[node] = i

    # Build condensation graph
    cond_succ = {i: set() for i in range(len(sccs))}
    for u in succ:
        u_scc = node_to_scc[u]
        for v in succ[u]:
            v_scc = node_to_scc[v]
            if u_scc != v_scc:
                cond_succ[u_scc].add(v_scc)

    cond_edges = sum(len(s) for s in cond_succ.values())
    print(f"  condensation graph: {len(sccs):,} nodes, {cond_edges:,} edges", flush=True)

    # Verify condensation is a DAG
    # (Tarjan's algorithm produces SCCs in reverse topological order,
    # so we can check if edges only go from higher to lower index)
    is_cond_dag = True
    for u_scc in cond_succ:
        for v_scc in cond_succ[u_scc]:
            if v_scc >= u_scc:
                is_cond_dag = False
                break
        if not is_cond_dag:
            break

    print(f"  condensation is DAG: {is_cond_dag}", flush=True)

    # ---- Step 8: longest path in condensation ----
    print("\n=== LONGEST PATH IN CONDENSATION ===", flush=True)

    # Topological sort of condensation (reverse of Tarjan order)
    topo_order = list(range(len(sccs) - 1, -1, -1))

    # Longest path DP
    lp = {i: 0 for i in range(len(sccs))}
    for u_scc in topo_order:
        for v_scc in cond_succ[u_scc]:
            if lp[u_scc] + 1 > lp[v_scc]:
                lp[v_scc] = lp[u_scc] + 1

    max_lp = max(lp.values())
    print(f"  longest path in condensation: {max_lp} edges", flush=True)

    # Find SCCs at max distance
    max_sccs = [i for i, d in lp.items() if d == max_lp]
    print(f"  SCCs at max distance: {len(max_sccs)}", flush=True)

    # Check if the SCC containing 0 can contribute to a path of length 129
    scc_0_idx = node_to_scc[0]
    print(f"\n  SCC containing 0 is at index {scc_0_idx}", flush=True)
    print(f"  longest path from SCC(0): {lp[scc_0_idx]}", flush=True)

    # For a path of length 129, we need:
    # - A path in the condensation of length L
    # - Plus cycles within SCCs along the path
    # The SCC containing 0 has a 20-cycle, so it can contribute multiples of 20

    print(f"\n=== PATH LENGTH ANALYSIS ===", flush=True)
    print(f"  To achieve N=130 (distance 129):", flush=True)
    print(f"    - Need a path in condensation + cycles within SCCs", flush=True)
    print(f"    - SCC(0) has a 20-cycle, can contribute 20k for any k", flush=True)
    print(f"    - Longest path in condensation: {max_lp}", flush=True)
    print(f"    - Can we achieve 129?", flush=True)

    # Check if 129 is achievable
    # 129 = 20k + r, where r is the path length in condensation
    # We need r <= max_lp and r ≡ 129 (mod 20)
    # 129 mod 20 = 9
    # So we need a path of length 9, 29, 49, 69, 89, 109, ... in the condensation

    achievable = False
    for r in range(9, max_lp + 1, 20):
        if r <= max_lp:
            achievable = True
            print(f"    ✓ path of length {r} in condensation + 20k cycle = 129", flush=True)
            break

    if not achievable:
        print(f"    ✗ cannot achieve 129 with current structure", flush=True)
        print(f"      max path in condensation: {max_lp}", flush=True)
        print(f"      need path of length 9, 29, 49, ... but max is {max_lp}", flush=True)

    # ---- Dump results ----
    out = REPO_ROOT / "data" / "frontier" / "macro_scc_analysis_results.txt"
    lines = [
        f"macro_states={macro_state_count}",
        f"macro_edges={edge_count}",
        f"closure_hit_cap={closure_hit}",
        f"max_bfs_distance={max_dist}",
        f"succ_0_complete_size={len(complete_succ_0)}",
        f"num_sccs={len(sccs)}",
        f"num_trivial_sccs={len(trivial_sccs)}",
        f"num_nontrivial_sccs={len(nontrivial_sccs)}",
        f"num_self_loop_sccs={len(self_loop_sccs)}",
        f"scc_0_size={len(scc_of_0)}",
        f"scc_0_contains_s_star={S_STAR in scc_of_0}",
        f"scc_0_contains_word_mask={WORD_MASK in scc_of_0}",
        f"condensation_is_dag={is_cond_dag}",
        f"condensation_nodes={len(sccs)}",
        f"condensation_edges={cond_edges}",
        f"longest_path_condensation={max_lp}",
        f"can_achieve_129={achievable}",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
