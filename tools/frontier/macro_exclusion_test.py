#!/usr/bin/env python3
"""
Macro-path uniqueness test for the verified 4x8x20 tiling.

Tests two exclusions against the macro graph (the same capped closure as
docs/s_z_frontier_macro_reachability.md / s_z_frontier_length_analysis.md):

  E0: forbid the verified first-generation edge 0 -> 6163195513375031274
  E1: forbid the verified macro edge
      13835058072323104239 -> 3993075831

For each exclusion (and a no-exclusion baseline):
  - does any path from the empty state 0 return to 0 in exactly 20
    completed layers?  (20 layers = 1 first-generation edge 0 -> s plus
    19 macro edges s -> ... -> 0, i.e. a first-gen source s with
    19 in R(s), where R(s) is the set of macro distances from s to 0 in
    the graph with the exclusion applied)
  - the number of surviving macro paths (distinct 19-edge macro walks
    s -> 0) and the number of surviving sources
  - the surviving source states

First-generation edges are modeled exactly: the first-generation tree
from 0 is complete (3,162,387 states, no cap hit; 331,765 sources), so
E0 is applied by removing s* from the allowed starting sources.  The
macro closure is the standard capped construction (15,000,000-state cap,
1,000,000 per-source intermediate cap); distances <= 85 are exact, so
the 20-layer question (distance 19) is exact.

The solver is NOT modified; its pure functions are reused with identical
semantics.  This is a macro-path-level test only (no placement-level
enumeration): surviving macro paths are distinct sequences of post-shift
states, NOT distinct tilings.
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
MAX_CLOSURE_STATES = 15_000_000
EMPTY = frozenset()

LAYERS_TOTAL = 20          # completed layers in a 4x8x20 tiling
MACRO_D = LAYERS_TOTAL - 1  # 19 macro edges from the first-gen source

S_STAR = 6163195513375031274              # verified first-gen source
E1_U = 13835058072323104239               # verified macro edge (layer 3)
E1_V = 3993075831


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


def explore_source(source, templates):
    successors = set()
    seen = {source}
    queue = deque([source])
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


def macro_closure(sources, templates):
    macro_seen = set(sources)
    queue = deque(sources)
    succ = {}
    dist = {s: 0 for s in sources}
    edge_count = 0
    hit_cap = False
    total_intermediate = 0
    sources_hit_intermediate = 0

    while queue:
        if len(macro_seen) >= MAX_CLOSURE_STATES:
            hit_cap = True
            break

        src = queue.popleft()
        successors, intermediate, hit_limit = explore_source(src, templates)
        total_intermediate += intermediate

        if hit_limit:
            sources_hit_intermediate += 1

        if successors:
            succ[src] = successors
            edge_count += len(successors)

        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                dist[s] = dist[src] + 1
                queue.append(s)

    return macro_seen, succ, edge_count, hit_cap, total_intermediate, dist, sources_hit_intermediate


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


def backward_dp(order, succ, skip_edges):
    """R(u) = bitmask of macro distances d with 0 reachable from u in
    exactly d edges, with the given edges removed."""
    R = {}

    for u in reversed(order):
        mask = 0

        for v in succ.get(u, EMPTY):
            if (u, v) in skip_edges:
                continue

            rv = R.get(v, 0)

            if rv:
                mask |= rv << 1

        if u == 0:
            mask |= 1

        if mask:
            R[u] = mask

    return R


def count_macro_paths(sources, R, succ, skip_edges, d):
    """For each source s with d in R(s), count distinct d-edge macro walks
    s -> 0 (edge-exact DP over the basin of 0; the basin is tiny)."""
    basin = set(R)
    ways = {0: 1}

    for depth in range(1, d + 1):
        new = {}

        for u in basin:
            total = 0

            for v in succ.get(u, EMPTY):
                if (u, v) in skip_edges:
                    continue

                total += ways.get(v, 0)

            if total:
                new[u] = total

        ways = new

    return {s: ways.get(s, 0) for s in sources}


def main() -> int:
    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    # ---- first generation (complete) ----
    print("First generation from state 0...", flush=True)
    t0 = time.perf_counter()
    sources, tree_states, fg_hit = first_generation_sources(templates)
    t1 = time.perf_counter()
    print(
        f"  tree states: {tree_states:,} (cap hit: {fg_hit})  "
        f"sources: {len(sources):,} ({t1 - t0:.1f}s)",
        flush=True,
    )
    assert not fg_hit
    assert S_STAR in sources

    # ---- macro closure ----
    print("Macro closure (capped)...", flush=True)
    t2 = time.perf_counter()
    macro_states, succ, edge_count, closure_hit, total_intermediate, dist, src_int_hit = (
        macro_closure(sorted(sources), templates)
    )
    t3 = time.perf_counter()
    macro_state_count = len(macro_states)
    max_dist = max(dist.values())
    print(
        f"  macro states: {macro_state_count:,} (cap hit: {closure_hit})  "
        f"edges: {edge_count:,}  intermediate: {total_intermediate:,}  "
        f"({t3 - t2:.1f}s)",
        flush=True,
    )
    print(f"  max BFS distance: {max_dist}", flush=True)
    print(f"  sources that hit the intermediate cap: {src_int_hit}", flush=True)
    del dist

    # ---- Kahn ----
    print("Kahn topological order...", flush=True)
    t4 = time.perf_counter()
    order = kahn_order(macro_states, succ)
    t5 = time.perf_counter()
    is_dag = len(order) == macro_state_count
    print(f"  is_dag={is_dag} ({t5 - t4:.1f}s)", flush=True)
    del macro_states

    # ---- exclusion scenarios ----
    scenarios = [
        ("baseline (no exclusion)", frozenset()),
        ("E0: forbid first-gen edge 0 -> s*", frozenset()),
        ("E1: forbid macro edge (u, v)", frozenset({(E1_U, E1_V)})),
    ]

    # E0 removes s* from the allowed starting sources (first-gen edge
    # 0 -> s* forbidden); the macro graph itself is unchanged.
    e0_sources = {s for s in sources if s != S_STAR}

    results = {}

    for name, skip in scenarios:
        print(f"\n=== {name} ===", flush=True)
        t6 = time.perf_counter()
        R = backward_dp(order, succ, skip)
        t7 = time.perf_counter()
        print(f"  backward DP: {len(R)} states with non-empty R ({t7 - t6:.1f}s)")

        if name.startswith("E0"):
            allowed = e0_sources
        else:
            allowed = sources

        surviving = sorted(s for s in allowed if R.get(s, 0) & (1 << MACRO_D))
        print(f"  surviving sources (19 in R(s)): {len(surviving)}")
        counts = count_macro_paths(surviving, R, succ, skip, MACRO_D)
        total_paths = sum(counts.values())

        for s in surviving:
            print(f"    source {s}: {counts[s]} distinct {MACRO_D}-edge macro paths")

        print(f"  any path 0 -> 0 in exactly {LAYERS_TOTAL} completed layers: {bool(surviving)}")
        print(f"  surviving macro paths: {total_paths}")

        results[name] = {
            "surviving_sources": surviving,
            "path_counts": counts,
            "total_paths": total_paths,
            "R_states": len(R),
        }

        if name == "baseline (no exclusion)":
            r0 = R.get(0, 0)
            print(f"  R(0) = {[b for b in range(r0.bit_length()) if r0 >> b & 1]}")

    # ---- E1 detail: did s* itself survive? ----
    e1 = results["E1: forbid macro edge (u, v)"]
    print()
    print("=== E1 detail ===", flush=True)
    print(f"  edge (u, v) present in succ[u]: {E1_V in succ.get(E1_U, set())}")
    print(f"  s* among surviving sources: {S_STAR in e1['surviving_sources']}")

    if S_STAR in e1["path_counts"]:
        print(f"  s* macro paths avoiding the edge: {e1['path_counts'][S_STAR]}")

    # ---- E0 detail ----
    e0 = results["E0: forbid first-gen edge 0 -> s*"]
    print()
    print("=== E0 detail ===", flush=True)
    print(f"  s* excluded from allowed sources: {S_STAR not in e0['surviving_sources']}")

    # ---- dump ----
    out = REPO_ROOT / "data" / "frontier" / "macro_exclusion_test_results.txt"
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
        f"layers_total={LAYERS_TOTAL}",
        f"macro_d={MACRO_D}",
        f"s_star={S_STAR}",
        f"e1_u={E1_U}",
        f"e1_v={E1_V}",
        f"e1_edge_present={E1_V in succ.get(E1_U, set())}",
        f"firstgen_elapsed={t1 - t0:.1f}",
        f"closure_elapsed={t3 - t2:.1f}",
        f"kahn_elapsed={t5 - t4:.1f}",
    ]

    for name, res in results.items():
        tag = name.split(":")[0].replace(" ", "_").replace("(", "").replace(")", "")
        lines.append(f"{tag}_surviving_sources={res['surviving_sources']}")
        lines.append(f"{tag}_path_counts={res['path_counts']}")
        lines.append(f"{tag}_total_paths={res['total_paths']}")

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
