#!/usr/bin/env python3
"""
Experimental z-frontier / transfer-matrix solver for S in 4x8.

Interior state:
    four 32-bit masks for the next four z-layers.

The absolute z coordinate is deliberately absent, so identical interior
frontiers at different z positions can merge.

This prototype discovers the interior transition graph and reports SCCs.
Finite-box start/end caps are not yet included.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
NCELLS = X_SIZE * Y_SIZE
LAYERS = 4
FULL_MASK = (1 << NCELLS) - 1


@dataclass(frozen=True)
class Placement:
    cells: Tuple[Tuple[int, int, int], ...]
    masks: Tuple[int, ...]


@dataclass
class Stats:
    processed: int = 0
    generated: int = 0
    accepted: int = 0
    duplicates: int = 0
    shifts: int = 0
    branching_states: int = 0
    max_out_degree: int = 0
    last_report_time: float = 0.0
    last_report_processed: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def cell_id(x: int, y: int) -> int:
    return x + X_SIZE * y


def first_empty(mask: int) -> int:
    missing = FULL_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def placement_to_masks(
    placement: Sequence[Tuple[int, int, int]]
) -> Placement:
    min_z = min(z for _, _, z in placement)
    max_z = max(z for _, _, z in placement)

    span = max_z - min_z
    if span >= LAYERS:
        raise ValueError(
            f"S placement z-span {span} exceeds frontier width {LAYERS}"
        )

    masks = [0] * LAYERS

    for x, y, z in placement:
        rel = z - min_z
        masks[rel] |= 1 << cell_id(x, y)

    return Placement(
        cells=tuple(placement),
        masks=tuple(masks),
    )


def build_placements(
    n_z: int = 20,
) -> List[Placement]:
    raw, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, n_z),
        break_symmetry=False,
    )

    return [
        placement_to_masks(p)
        for p in raw.values()
    ]


def build_templates(
    placements: Sequence[Placement],
) -> Dict[int, List[Tuple[int, ...]]]:
    """
    For each target xy cell, produce unique placement masks translated so
    at least one occurrence of that target lies in the current z=0 layer.

    We need to consider each occurrence of the target cell in a placement,
    because translating the same shape by different z offsets changes which
    layer contains the target.
    """
    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}

    for placement in placements:
        min_z = min(z for _, _, z in placement.cells)

        for x, y, z in placement.cells:
            target = cell_id(x, y)
            target_rel = z - min_z

            shifted = [0] * LAYERS

            for rel, mask in enumerate(placement.masks):
                out_rel = rel - target_rel

                if out_rel < 0 or out_rel >= LAYERS:
                    break

                shifted[out_rel] |= mask
            else:
                tpl = tuple(shifted)

                if tpl not in seen[target]:
                    seen[target].add(tpl)
                    result[target].append(tpl)

    return result


def apply(
    state: Tuple[int, ...],
    template: Tuple[int, ...],
) -> Tuple[int, ...] | None:
    out = []

    for a, b in zip(state, template):
        if a & b:
            return None
        out.append(a | b)

    return tuple(out)


def shift_state(
    state: Tuple[int, ...],
) -> Tuple[int, ...]:
    return state[1:] + (0,)


def report(
    stats: Stats,
    queue: deque[Tuple[int, ...]],
    seen: set[Tuple[int, ...]],
) -> None:
    now = time.perf_counter()

    if now - stats.last_report_time < 2.0:
        return

    delta = (
        stats.processed -
        stats.last_report_processed
    )
    dt = now - stats.last_report_time
    rate = delta / dt if dt > 0 else 0.0

    stats.last_report_time = now
    stats.last_report_processed = stats.processed

    print(
        f"[progress] "
        f"states={len(seen):,} "
        f"queue={len(queue):,} "
        f"processed={stats.processed:,} "
        f"gen={stats.generated:,} "
        f"accept={stats.accepted:,} "
        f"dup={stats.duplicates:,} "
        f"shifts={stats.shifts:,} "
        f"branch={stats.branching_states:,} "
        f"maxdeg={stats.max_out_degree} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


def discover(
    templates: Dict[int, List[Tuple[int, ...]]],
    max_states: int,
):
    start = (0, 0, 0, 0)

    queue: deque[Tuple[int, ...]] = deque([start])
    seen: set[Tuple[int, ...]] = {start}

    graph: Dict[
        Tuple[int, ...],
        set[Tuple[int, ...]]
    ] = {}

    stats = Stats(
        last_report_time=time.perf_counter()
    )

    while queue:
        if len(seen) >= max_states:
            print(
                f"[limit] reached {max_states:,} states",
                flush=True,
            )
            break

        state = queue.popleft()
        stats.processed += 1

        if state[0] == FULL_MASK:
            nxt = shift_state(state)
            stats.shifts += 1

            edges = graph.setdefault(state, set())
            edges.add(nxt)

            if nxt in seen:
                stats.duplicates += 1
            else:
                seen.add(nxt)
                queue.append(nxt)

            report(stats, queue, seen)
            continue

        target = first_empty(state[0])
        if target < 0:
            continue

        outgoing = set()

        for template in templates[target]:
            stats.generated += 1

            nxt = apply(state, template)
            if nxt is None:
                continue

            stats.accepted += 1
            outgoing.add(nxt)

        if len(outgoing) > 1:
            stats.branching_states += 1

        stats.max_out_degree = max(
            stats.max_out_degree,
            len(outgoing),
        )

        graph[state] = outgoing

        for nxt in outgoing:
            if nxt in seen:
                stats.duplicates += 1
                continue

            seen.add(nxt)
            queue.append(nxt)

        report(stats, queue, seen)

    return seen, graph, stats


def tarjan(
    graph: Dict[
        Tuple[int, ...],
        set[Tuple[int, ...]]
    ],
):
    index = 0
    indices = {}
    low = {}
    stack = []
    on_stack = set()
    components = []

    def visit(v):
        nonlocal index

        indices[v] = index
        low[v] = index
        index += 1

        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, ()):
            if w not in indices:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])

        if low[v] == indices[v]:
            comp = []

            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.append(w)

                if w == v:
                    break

            components.append(comp)

    for v in graph:
        if v not in indices:
            visit(v)

    return components


def format_state(state: Tuple[int, ...]) -> str:
    lines = []

    for layer, mask in enumerate(state):
        lines.append(f"z+{layer}:")

        for y in range(Y_SIZE):
            lines.append(
                " ".join(
                    "#" if (
                        mask &
                        (1 << cell_id(x, y))
                    ) else "."
                    for x in range(X_SIZE)
                )
            )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover the interior z-frontier automaton for S in 4x8."
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=1_000_000,
    )
    args = parser.parse_args()

    print(
        "Generating S placements...",
        flush=True,
    )

    start = time.perf_counter()
    placements = build_placements()

    print(
        f"Concrete placements: {len(placements)}",
        flush=True,
    )
    print(
        f"Placement generation: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )

    templates = build_templates(placements)

    total_templates = sum(
        len(v) for v in templates.values()
    )

    print(
        f"Interior target templates: "
        f"{total_templates}",
        flush=True,
    )

    print(
        "\nStarting z-frontier automaton...",
        flush=True,
    )

    start = time.perf_counter()

    states, graph, stats = discover(
        templates,
        args.max_states,
    )

    elapsed = time.perf_counter() - start

    print()
    print(f"States: {len(states):,}")
    print(f"Processed: {stats.processed:,}")
    print(f"Transitions generated: {stats.generated:,}")
    print(f"Transitions accepted: {stats.accepted:,}")
    print(f"Duplicate states: {stats.duplicates:,}")
    print(f"Layer shifts: {stats.shifts:,}")
    print(f"Branching states: {stats.branching_states:,}")
    print(f"Maximum out-degree: {stats.max_out_degree}")
    print(f"Elapsed: {elapsed:.3f} s")
    print(f"Peak RSS: {rss_mb():,.0f} MB")

    if len(states) < args.max_states:
        components = tarjan(graph)

        sizes = sorted(
            (len(c) for c in components),
            reverse=True,
        )

        nontrivial = [
            c for c in components
            if len(c) > 1
        ]

        self_loops = sum(
            1 for v, edges in graph.items()
            if v in edges
        )

        print(f"SCCs: {len(components):,}")
        print(f"Largest SCCs: {sizes[:20]}")
        print(f"Nontrivial SCCs: {len(nontrivial):,}")
        print(f"Self-loops: {self_loops:,}")

        for state, edges in graph.items():
            if len(edges) > 1:
                print("\nExample branching state:")
                print(format_state(state))
                print(f"Outgoing states: {len(edges)}")
                break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
