#!/usr/bin/env python3
"""
Exact reachable-length analysis for the S z-frontier (4x8) from the empty
frontier state, using the completed (capped) portion of the macro graph.

For each macro state s, record R(s) = set of remaining distances d such
that the empty frontier state 0 is reachable from s in exactly d macro
edges.  Computed by backward DP over the capped closure (a DAG).

Reports:
  - reachable N up to the completeness limit (N = d+1, d <= 85)
  - first/last reachable N
  - gaps
  - the shortest path for N=20 (post-shift states + pre-shift states)
  - whether the same terminal state/path structure repeats

The solver is NOT modified; its pure functions are reused with identical
semantics.  The graph is NOT expanded beyond the existing capped closure
(15,000,000-state cap; per-source intermediate cap 1,000,000).

Completeness limit: paths of length <= 85 from first-gen sources stay
within distance-<=84 states (all fully processed), so R(s) is exact for
d <= 85.  Note: the true macro graph has a 20-cycle through 0
(0 -> source -> ... -> 0), but the capped closure's succ[0] is truncated
by the per-source intermediate cap, so the cycle is NOT in the capped
closure; through-0 paths (d = 79, ...) are therefore not visible.
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

COMPLETENESS_D = 85  # R(s) exact for d <= 85 (N <= 86)


def first_generation_sources(
    templates: dict,
) -> tuple[set[int], int, bool]:
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


def kahn_order(
    nodes: set[int],
    succ: dict[int, set[int]],
) -> list[int]:
    indeg = {n: 0 for n in nodes}

    for u in succ:
        for v in succ[u]:
            indeg[v] += 1

    queue = deque([n for n in nodes if indeg[n] == 0])
    order: list[int] = []

    while queue:
        u = queue.popleft()
        order.append(u)

        for v in succ.get(u, EMPTY):
            indeg[v] -= 1

            if indeg[v] == 0:
                queue.append(v)

    return order


def bits(mask: int):
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask ^= b


def firstgen_path_to_source(
    target_source: int,
    templates: dict,
) -> tuple[list[int], int]:
    """
    BFS from 0 with parent tracking; stop at the first pre-shift state p
    with p >> 32 == target_source.  Returns (path 0..p, p).
    """
    parent: dict[int, tuple[int, int]] = {}
    seen: set[int] = {0}
    queue: deque[int] = deque([0])

    while queue:
        state = queue.popleft()

        if layer_mask(state, 0) == WORD_MASK:
            if shift_state(state) == target_source:
                path = [state]

                while state in parent:
                    state = parent[state][0]
                    path.append(state)

                path.reverse()
                return path, path[-1]

            continue

        target = first_empty(layer_mask(state, 0))

        for template in templates[target]:
            nxt = apply_template(state, template)

            if nxt is None or nxt in seen:
                continue

            seen.add(nxt)
            parent[nxt] = (state, template)
            queue.append(nxt)

    raise RuntimeError(f"no first-gen path to source {target_source}")


def reconstruct_path(
    start: int,
    d: int,
    succ: dict[int, set[int]],
    R: dict[int, int],
) -> list[int]:
    """Walk from start toward 0 along d edges using R as a guide."""
    path = [start]
    cur = start
    rem = d

    while rem > 0:
        nxt = None

        for v in succ[cur]:
            if R.get(v, 0) & (1 << (rem - 1)):
                nxt = v
                break

        if nxt is None:
            raise RuntimeError("path reconstruction failed")

        path.append(nxt)
        cur = nxt
        rem -= 1

    assert path[-1] == 0
    return path


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
    del dist  # free memory

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
    del macro_states

    # ---- Step 5: backward DP ----
    # R(s) = bitmask: bit d set iff 0 reachable from s in exactly d edges.
    print("Backward DP: remaining distances to empty frontier (0)...", flush=True)
    t6 = time.perf_counter()
    R: dict[int, int] = {}

    for u in reversed(order):
        mask = 0

        for v in succ.get(u, EMPTY):
            rv = R.get(v, 0)

            if rv:
                mask |= rv << 1

        if u == 0:
            mask |= 1  # 0 reachable from 0 in 0 edges

        if mask:
            R[u] = mask

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
        print(f"Non-reachable N in [1, {COMPLETENESS_D + 1}]: {non_reachable}")

        # cell-count-possible but not reachable
        div_ok = [n for n in non_reachable if (32 * n) % 5 == 0]
        print(f"  of which pass the cell-count check (32N/5 integer): {div_ok}")

    # R(0): cycle check
    r0 = R.get(0, 0)
    print()
    print(f"R(0) = {sorted(bits(r0))}")
    print(
        f"  bit 20 set (cycle 0->...->0 of length 20 in capped closure): "
        f"{bool(r0 & (1 << 20))}"
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

    for s, ds in src_with_r:
        print(f"  source {s}: distances {ds}")

    # ---- Step 7: shortest path for N=20 (d=19) ----
    print()
    print("=== SHORTEST PATH FOR N=20 (d=19) ===")
    s20 = None

    for s in sources:
        if R.get(s, 0) & (1 << 19):
            s20 = s
            break

    if s20 is not None:
        path20 = reconstruct_path(s20, 19, succ, R)
        print(f"Source: {s20}")
        print(f"Macro path length: {len(path20) - 1} edges")
        print("step | post-shift state | L0 | L1 | L2 | pre-shift state")

        for i, v in enumerate(path20):
            l0 = layer_mask(v, 0)
            l1 = layer_mask(v, 1)
            l2 = layer_mask(v, 2)

            if i < len(path20) - 1:
                p = (
                    WORD_MASK
                    | (layer_mask(path20[i + 1], 0) << 32)
                    | (layer_mask(path20[i + 1], 1) << 64)
                )
            else:
                p = 0

            print(f"{i} | {v} | {l0:#x} | {l1:#x} | {l2:#x} | {p:#x}")

        # first-gen segment: 0 -> ... -> p0 -> s20
        fg_path, p0 = firstgen_path_to_source(s20, templates)
        print()
        print(
            f"First-gen segment: 0 -> [{len(fg_path) - 1} placements] -> "
            f"p0={p0:#x} -> s20"
        )
        print(
            f"  p0 layers: L0={layer_mask(p0, 0):#x} "
            f"L1={layer_mask(p0, 1):#x} L2={layer_mask(p0, 2):#x}"
        )
        print(f"  p0 >> 32 == s20: {shift_state(p0) == s20}")
    else:
        print("No source reaches 0 in 19 edges (unexpected)")

    # ---- Step 8: structure repetition ----
    print()
    print("=== STRUCTURE REPETITION ===")

    # terminal structure: every edge into 0 comes from WORD_MASK (immediate
    # shift) or from a state with layer0 == layer1 == 0 (flat fill).
    preds_of_zero = [u for u in succ if 0 in succ[u]]
    ok_preds = all(
        u == WORD_MASK or (layer_mask(u, 0) == 0 and layer_mask(u, 1) == 0)
        for u in preds_of_zero
    )
    print(f"States with an edge to 0: {len(preds_of_zero):,}")
    print(f"  all are WORD_MASK or have layer0==layer1==0: {ok_preds}")
    print(f"  WORD_MASK among them: {WORD_MASK in preds_of_zero}")

    # for each reachable N, reconstruct a path and check decomposition
    for N in reachable_N:
        d = N - 1
        sN = None

        for s in sources:
            if R.get(s, 0) & (1 << d):
                sN = s
                break

        if sN is None:
            print(f"N={N}: no path found (unexpected)")
            continue

        p = reconstruct_path(sN, d, succ, R)
        mid_zero = [i for i, v in enumerate(p) if v == 0 and 0 < i < len(p) - 1]
        print(
            f"N={N}: path length {d} edges from source {sN}, "
            f"intermediate visits to 0 at positions {mid_zero} "
            f"(decomposes into 20-layer segments: {bool(mid_zero)})"
        )

    # basin structure: paths from all sources with non-empty R
    print()
    print("=== BASIN OF 0 ===")
    print(f"Basin size: {len(R)} states; |R(s)| = 1 for every basin state")

    basin_paths: dict[int, list[int]] = {}

    for s, ds in src_with_r:
        basin_paths[s] = reconstruct_path(s, ds[0], succ, R)

    for s, p in basin_paths.items():
        print(f"  source {s}: path length {len(p) - 1}, states {len(p)}")

    # pairwise merge analysis
    if len(basin_paths) >= 2:
        keys = list(basin_paths.keys())
        print("  pairwise shared states between source paths:")

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                si, sj = keys[i], keys[j]
                shared = set(basin_paths[si]) & set(basin_paths[sj])
                print(
                    f"    {si} vs {sj}: {len(shared)} shared states "
                    f"(merge point: {sorted(shared)[:3]})"
                )

    # ---- Dump machine-readable results ----
    out = REPO_ROOT / "data" / "frontier" / "macro_length_analysis_results.txt"
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
        f"completeness_d={COMPLETENESS_D}",
        f"reachable_d_exact={exact_d}",
        f"reachable_d_partial={partial_d}",
        f"reachable_N={reachable_N}",
        f"first_reachable_N={reachable_N[0] if reachable_N else None}",
        f"last_reachable_N={reachable_N[-1] if reachable_N else None}",
        f"r0={sorted(bits(r0))}",
        f"r0_has_bit20={bool(r0 & (1 << 20))}",
        f"states_with_nonempty_R={len(R)}",
        f"R_size_distribution={dict(sorted(sizes.items()))}",
        f"max_remaining_distance={max_r}",
        f"sources_with_nonempty_R={[(s, ds) for s, ds in src_with_r]}",
        f"firstgen_elapsed={t1 - t0:.1f}",
        f"closure_elapsed={t3 - t2:.1f}",
        f"kahn_elapsed={t5 - t4:.1f}",
        f"backward_dp_elapsed={t7 - t6:.1f}",
    ]

    if s20 is not None:
        lines.append(f"n20_source={s20}")
        lines.append(f"n20_path={path20}")
        lines.append(f"n20_p0={p0}")
        lines.append(f"n20_firstgen_placements={len(fg_path) - 1}")

    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())