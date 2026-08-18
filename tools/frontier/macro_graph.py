#!/usr/bin/env python3
"""
Macro-graph analysis for the S z-frontier (4x8).

Starting from the 2,451 recorded post-shift states
(docs/z_frontier_all_shift_states_1m.md), explore each source's
placement interval (applying templates at first_empty(layer0)) until
the next layer shift, record the distinct post-shift states reached,
and build the macro directed graph:

    nodes = union of the 2,451 sources and all reached post-shift states
    edges = distinct (source -> successor) pairs

Report: macro state count, macro edge count, zero-outgoing states,
max macro out-degree, SCC count, largest SCCs, nontrivial cycles.

Per-source safety limit: MAX_INTERMEDIATE states explored per source;
any source hitting the limit is reported (and its exploration is
truncated at the limit).

Reuses the solver's pure functions (build_templates, apply_template,
first_empty, layer_mask, shift_state, WORD_MASK) with identical
semantics; the solver itself is NOT modified and its discovery loop is
not run.
"""

from __future__ import annotations

import sys
import time
from collections import Counter, deque
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

SHIFT_DOC = REPO_ROOT / "docs" / "z_frontier_all_shift_states_1m.md"

# Per-source safety limit: maximum number of intermediate (non-shift)
# states explored from a single source before truncating that source's
# exploration.  Calibration over the first 30 sources showed a max of
# 40,399 intermediate states (source 2); 1,000,000 is ~25x that and
# matches the 1M-state theme of the source run.
MAX_INTERMEDIATE = 1_000_000


def read_postshift_states(path: Path) -> list[int]:
    """Read the post-shift states (column 3) from the shift-events doc."""
    states: list[int] = []
    in_table = False

    for line in path.read_text().splitlines():
        if line.startswith("## All"):
            in_table = True
            continue

        if not in_table:
            continue

        if not line.startswith("|"):
            continue

        cols = [c.strip() for c in line.split("|")]

        if len(cols) < 4:
            continue

        if cols[1] in ("#", "---"):
            continue

        states.append(int(cols[3]))

    return states


def explore_source(
    source: int,
    templates: dict,
) -> tuple[set[int], int, bool]:
    """
    Explore the placement interval from a post-shift source until the
    next layer shift.

    Returns (successors, intermediate_count, hit_limit):
      successors        distinct post-shift states reached
      intermediate_count number of distinct non-shift states explored
      hit_limit         True if MAX_INTERMEDIATE was reached
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

            if nxt is None:
                continue

            if nxt in seen:
                continue

            seen.add(nxt)
            queue.append(nxt)

    return successors, len(seen) - 1, hit_limit


def explore_closure(
    sources: list[int],
    templates: dict,
    max_macro_states: int,
) -> tuple[set[int], set[tuple[int, int]], bool, int]:
    """
    Iterate the macro transition to closure: from every reached
    post-shift state, explore its placement interval and collect the
    next post-shift states, until no new states appear.

    Returns (macro_states, closure_edges, hit_cap, total_intermediate).
    """
    macro_seen: set[int] = set(sources)
    queue: deque[int] = deque(sources)
    closure_edges: set[tuple[int, int]] = set()
    hit_cap = False
    total_intermediate = 0

    while queue:
        if len(macro_seen) >= max_macro_states:
            hit_cap = True
            break

        src = queue.popleft()
        succs, intermediate, _ = explore_source(src, templates)
        total_intermediate += intermediate

        for succ in succs:
            closure_edges.add((src, succ))

            if succ not in macro_seen:
                macro_seen.add(succ)
                queue.append(succ)

    return macro_seen, closure_edges, hit_cap, total_intermediate


def tarjan_scc(adj: dict[int, set[int]]) -> list[list[int]]:
    """Iterative Tarjan SCC on the macro graph. Returns SCCs (node lists)."""
    index_counter = [0]
    stack: list[int] = []
    on_stack: set[int] = set()
    indices: dict[int, int] = {}
    lowlink: dict[int, int] = {}
    sccs: list[list[int]] = []

    for root in adj:
        if root in indices:
            continue

        work: list[tuple[int, int | None]] = [(root, None)]

        while work:
            node, parent = work[-1]

            if node not in indices:
                indices[node] = index_counter[0]
                lowlink[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)

            pushed = False

            for nxt in adj[node]:
                if nxt not in indices:
                    work.append((nxt, node))
                    pushed = True
                    break

                if nxt in on_stack:
                    lowlink[node] = min(lowlink[node], indices[nxt])

            if pushed:
                continue

            work.pop()

            if parent is not None:
                lowlink[parent] = min(lowlink[parent], lowlink[node])

            if lowlink[node] == indices[node]:
                comp: list[int] = []

                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)

                    if w == node:
                        break

                sccs.append(comp)

    return sccs


def main() -> int:
    print("Reading post-shift states...", flush=True)
    sources = read_postshift_states(SHIFT_DOC)
    print(f"  {len(sources):,} sources", flush=True)

    print("Building templates...", flush=True)
    templates, concrete_count = build_templates()
    total_templates = sum(len(v) for v in templates.values())
    print(
        f"  concrete placements={concrete_count} "
        f"target templates={total_templates}",
        flush=True,
    )

    start = time.perf_counter()

    edges: set[tuple[int, int]] = set()
    successors_by_source: dict[int, set[int]] = {}
    hit_sources: list[tuple[int, int, int]] = []
    total_intermediate = 0
    max_intermediate = 0
    max_intermediate_source = None

    for i, source in enumerate(sources, 1):
        successors, intermediate, hit = explore_source(source, templates)

        successors_by_source[source] = successors

        for succ in successors:
            edges.add((source, succ))

        total_intermediate += intermediate

        if intermediate > max_intermediate:
            max_intermediate = intermediate
            max_intermediate_source = source

        if hit:
            hit_sources.append((i, source, intermediate))

        if i % 250 == 0 or i == len(sources):
            elapsed = time.perf_counter() - start
            print(
                f"  [{i:,}/{len(sources):,}] "
                f"edges={len(edges):,} "
                f"intermediate={total_intermediate:,} "
                f"elapsed={elapsed:.1f}s",
                flush=True,
            )

    elapsed = time.perf_counter() - start

    # Macro graph nodes: sources union successors.
    nodes: set[int] = set(sources)
    nodes.update(succ for succs in successors_by_source.values() for succ in succs)

    out_degree: Counter = Counter()
    adj: dict[int, set[int]] = {n: set() for n in nodes}

    for src, succs in successors_by_source.items():
        for succ in succs:
            adj[src].add(succ)

    for n in nodes:
        out_degree[len(adj[n])] += 1

    zero_outgoing = [n for n in nodes if not adj[n]]
    max_deg = max(len(adj[n]) for n in nodes)
    max_deg_nodes = [n for n in nodes if len(adj[n]) == max_deg]

    print("Running Tarjan SCC...", flush=True)
    scc_start = time.perf_counter()
    sccs = tarjan_scc(adj)
    scc_elapsed = time.perf_counter() - scc_start

    nontrivial = [c for c in sccs if len(c) > 1 or (len(c) == 1 and c[0] in adj[c[0]])]
    nontrivial_sorted = sorted(nontrivial, key=len, reverse=True)

    # Supplementary: iterate the macro transition to closure.
    print("Running closure exploration...", flush=True)
    closure_start = time.perf_counter()
    MAX_CLOSURE_STATES = 1_000_000
    closure_states, closure_edges, closure_hit_cap, closure_intermediate = (
        explore_closure(sources, templates, MAX_CLOSURE_STATES)
    )
    closure_elapsed = time.perf_counter() - closure_start

    closure_adj: dict[int, set[int]] = {n: set() for n in closure_states}

    for src, succ in closure_edges:
        closure_adj[src].add(succ)

    closure_sccs = tarjan_scc(closure_adj)
    closure_nontrivial = [
        c
        for c in closure_sccs
        if len(c) > 1 or (len(c) == 1 and c[0] in closure_adj[c[0]])
    ]
    closure_nontrivial_sorted = sorted(closure_nontrivial, key=len, reverse=True)
    closure_zero_outgoing = sum(1 for n in closure_states if not closure_adj[n])
    closure_max_deg = max((len(closure_adj[n]) for n in closure_states), default=0)

    print()
    print("=== MACRO GRAPH SUMMARY ===")
    print(f"Sources (starting post-shift states): {len(sources):,}")
    print(f"Macro states (sources union successors): {len(nodes):,}")
    print(f"Macro edges (distinct source->successor): {len(edges):,}")
    print(f"Zero-outgoing macro states: {len(zero_outgoing):,}")
    print(f"Max macro out-degree: {max_deg} (states: {len(max_deg_nodes)})")
    print(f"SCC count: {len(sccs):,}")
    print(f"Nontrivial SCCs (size>1 or self-loop): {len(nontrivial):,}")
    print(f"Largest SCCs: {[len(c) for c in nontrivial_sorted[:10]]}")
    print(f"Total intermediate states explored: {total_intermediate:,}")
    print(f"Max intermediate per source: {max_intermediate:,} (source {max_intermediate_source})")
    print(f"Sources hitting safety limit ({MAX_INTERMEDIATE:,}): {len(hit_sources)}")
    print(f"Exploration elapsed: {elapsed:.1f}s; SCC elapsed: {scc_elapsed:.1f}s")
    print()
    print("=== CLOSURE (supplementary) ===")
    print(f"Closure macro states: {len(closure_states):,}")
    print(f"Closure macro edges: {len(closure_edges):,}")
    print(f"Closure zero-outgoing: {closure_zero_outgoing:,}")
    print(f"Closure max out-degree: {closure_max_deg}")
    print(f"Closure SCC count: {len(closure_sccs):,}")
    print(f"Closure nontrivial SCCs: {len(closure_nontrivial):,}")
    print(f"Closure largest SCCs: {[len(c) for c in closure_nontrivial_sorted[:10]]}")
    print(f"Closure hit cap ({MAX_CLOSURE_STATES:,}): {closure_hit_cap}")
    print(f"Closure total intermediate: {closure_intermediate:,}")
    print(f"Closure elapsed: {closure_elapsed:.1f}s")

    # Verification: first 30 sources must match calibration.
    calib = {
        1: 0, 2: 2689, 3: 0, 4: 9, 5: 0, 6: 0, 7: 0, 8: 1, 9: 16, 10: 0,
        11: 0, 12: 0, 13: 88, 14: 0, 15: 0, 16: 0, 17: 84, 18: 7, 19: 55,
        20: 582, 21: 0, 22: 10, 23: 12, 24: 169, 25: 0, 26: 103, 27: 130,
        28: 675, 29: 141, 30: 0,
    }
    mismatches = []

    for idx, expected in calib.items():
        got = len(successors_by_source[sources[idx - 1]])

        if got != expected:
            mismatches.append(f"source {idx}: expected={expected} got={got}")

    if mismatches:
        print("CALIBRATION MISMATCH:", flush=True)

        for m in mismatches:
            print(f"  - {m}", flush=True)
    else:
        print("Calibration check PASSED (first 30 sources match)", flush=True)

    # Dump machine-readable summary for the doc writer.
    out = Path("/tmp/opencode/macro_graph_results.txt")
    lines = [
        f"sources={len(sources)}",
        f"macro_states={len(nodes)}",
        f"macro_edges={len(edges)}",
        f"zero_outgoing={len(zero_outgoing)}",
        f"max_out_degree={max_deg}",
        f"max_out_degree_states={len(max_deg_nodes)}",
        f"scc_count={len(sccs)}",
        f"nontrivial_scc_count={len(nontrivial)}",
        f"largest_scc_sizes={[len(c) for c in nontrivial_sorted[:10]]}",
        f"total_intermediate={total_intermediate}",
        f"max_intermediate={max_intermediate}",
        f"max_intermediate_source={max_intermediate_source}",
        f"hit_limit_count={len(hit_sources)}",
        f"exploration_elapsed={elapsed:.1f}",
        f"scc_elapsed={scc_elapsed:.1f}",
        f"calibration_ok={not mismatches}",
        f"closure_states={len(closure_states)}",
        f"closure_edges={len(closure_edges)}",
        f"closure_zero_outgoing={closure_zero_outgoing}",
        f"closure_max_out_degree={closure_max_deg}",
        f"closure_scc_count={len(closure_sccs)}",
        f"closure_nontrivial_scc_count={len(closure_nontrivial)}",
        f"closure_largest_scc_sizes={[len(c) for c in closure_nontrivial_sorted[:10]]}",
        f"closure_hit_cap={closure_hit_cap}",
        f"closure_total_intermediate={closure_intermediate}",
        f"closure_elapsed={closure_elapsed:.1f}",
    ]

    for i, c in enumerate(nontrivial_sorted[:10], 1):
        lines.append(f"largest_scc_{i}={sorted(c)}")

    out.write_text("\n".join(lines) + "\n")
    print(f"Results written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())