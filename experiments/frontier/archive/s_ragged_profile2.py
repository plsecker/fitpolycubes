#!/usr/bin/env python3
"""
Profile the normalized ragged frontier automaton for S in 4x8.

This version fixes an important detail in the previous prototype:
placement templates are normalized by their minimum z-offset, so pure
translation along the prism does not create separate templates.

It also measures the OUT-DEGREE of each state.  A real automaton should
have states with multiple possible outgoing transitions and, for long
prisms, recurrent components/cycles.

State:
    h[x,y] = next unfilled z in each of 32 columns.

Normalize each state by subtracting min(h).

A placement template is:
    start[col], length[col]
normalized so min(start)=0.

A transition is possible when one global z-translation makes every touched
column start exactly at that column's current h.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from collections import defaultdict, deque, Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
NCOLS = X_SIZE * Y_SIZE


@dataclass(frozen=True)
class Run:
    col: int
    start: int
    length: int


@dataclass(frozen=True)
class Template:
    runs: Tuple[Run, ...]


@dataclass
class Stats:
    states: int = 0
    transitions_examined: int = 0
    accepted: int = 0
    duplicates: int = 0
    positive_advance: int = 0
    zero_advance: int = 0
    branching_states: int = 0
    max_out_degree: int = 0
    max_height: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def col_id(x: int, y: int) -> int:
    return x + X_SIZE * y


def xy(col: int) -> Tuple[int, int]:
    return col % X_SIZE, col // X_SIZE


def make_template(
    placement: Sequence[Tuple[int, int, int]]
) -> Template:
    by_col: Dict[int, List[int]] = defaultdict(list)

    for x, y, z in placement:
        by_col[col_id(x, y)].append(z)

    runs: List[Run] = []

    min_z = min(z for z in (
        z
        for levels in by_col.values()
        for z in levels
    ))

    for col in sorted(by_col):
        levels = sorted(by_col[col])

        # A monotone sweep cannot skip an unfilled cell.
        for a, b in zip(levels, levels[1:]):
            if b != a + 1:
                raise ValueError(
                    "Unexpected non-contiguous S column"
                )

        runs.append(
            Run(
                col=col,
                start=levels[0] - min_z,
                length=len(levels),
            )
        )

    return Template(tuple(runs))


def build_templates() -> List[Template]:
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    unique = {
        tuple(
            (run.col, run.start, run.length)
            for run in make_template(p).runs
        )
        for p in placements.values()
    }

    return [
        Template(
            tuple(
                Run(
                    col=col,
                    start=start,
                    length=length,
                )
                for col, start, length in key
            )
        )
        for key in sorted(unique)
    ]


def build_candidate_index(
    templates: Sequence[Template],
) -> Dict[int, List[Template]]:
    result = {
        col: []
        for col in range(NCOLS)
    }

    for template in templates:
        for run in template.runs:
            result[run.col].append(template)

    return result


def try_template(
    state: Tuple[int, ...],
    template: Template,
    target_col: int,
) -> Tuple[Tuple[int, ...], int] | None:
    target_run = None

    for run in template.runs:
        if run.col == target_col:
            target_run = run
            break

    if target_run is None:
        return None

    shift = state[target_col] - target_run.start

    if shift < 0:
        return None

    new_state = list(state)

    for run in template.runs:
        if state[run.col] != run.start + shift:
            return None

        new_state[run.col] += run.length

    advance = min(new_state)

    normalized = tuple(
        h - advance
        for h in new_state
    )

    return normalized, advance


def state_outgoing(
    state: Tuple[int, ...],
    candidates: Dict[int, List[Template]],
    stats: Stats,
) -> Dict[Tuple[int, ...], int]:
    target_col = min(
        range(NCOLS),
        key=lambda c: (state[c], c),
    )

    outgoing: Dict[Tuple[int, ...], int] = {}

    for template in candidates[target_col]:
        stats.transitions_examined += 1

        result = try_template(
            state,
            template,
            target_col,
        )

        if result is None:
            continue

        next_state, advance = result
        stats.accepted += 1

        if advance > 0:
            stats.positive_advance += 1
        else:
            stats.zero_advance += 1

        stats.max_height = max(
            stats.max_height,
            max(next_state),
        )

        outgoing[next_state] = outgoing.get(
            next_state,
            0,
        ) + 1

    return outgoing


def discover(
    candidates: Dict[int, List[Template]],
    max_states: int,
) -> Tuple[set[Tuple[int, ...]], Dict[
    Tuple[int, ...],
    Dict[Tuple[int, ...], int]
], Stats]:
    start = (0,) * NCOLS

    queue: deque[Tuple[int, ...]] = deque([start])
    seen: set[Tuple[int, ...]] = {start}

    graph: Dict[
        Tuple[int, ...],
        Dict[Tuple[int, ...], int]
    ] = {}

    stats = Stats(states=1)

    while queue:
        if len(seen) >= max_states:
            print(
                f"[limit] reached {max_states:,} states",
                flush=True,
            )
            break

        state = queue.popleft()

        outgoing = state_outgoing(
            state,
            candidates,
            stats,
        )

        graph[state] = outgoing

        degree = len(outgoing)

        if degree > 1:
            stats.branching_states += 1

        stats.max_out_degree = max(
            stats.max_out_degree,
            degree,
        )

        for next_state in outgoing:
            if next_state in seen:
                stats.duplicates += 1
                continue

            seen.add(next_state)
            queue.append(next_state)
            stats.states += 1

        if stats.states % 5000 == 0:
            print(
                f"[progress] "
                f"states={stats.states:,} "
                f"queue={len(queue):,} "
                f"branching={stats.branching_states:,} "
                f"max_degree={stats.max_out_degree} "
                f"dup={stats.duplicates:,} "
                f"advance={stats.positive_advance:,} "
                f"rss={rss_mb():,.0f} MB",
                flush=True,
            )

    return seen, graph, stats


def tarjan_scc(
    graph: Dict[
        Tuple[int, ...],
        Dict[Tuple[int, ...], int]
    ]
) -> List[List[Tuple[int, ...]]]:
    index = 0
    indices: Dict[Tuple[int, ...], int] = {}
    lowlink: Dict[Tuple[int, ...], int] = {}
    stack: List[Tuple[int, ...]] = []
    on_stack: set[Tuple[int, ...]] = set()
    components: List[List[Tuple[int, ...]]] = []

    def visit(v: Tuple[int, ...]) -> None:
        nonlocal index

        indices[v] = index
        lowlink[v] = index
        index += 1

        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, {}):
            if w not in indices:
                visit(w)
                lowlink[v] = min(
                    lowlink[v],
                    lowlink[w],
                )
            elif w in on_stack:
                lowlink[v] = min(
                    lowlink[v],
                    indices[w],
                )

        if lowlink[v] == indices[v]:
            component = []

            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.append(w)

                if w == v:
                    break

            components.append(component)

    for v in graph:
        if v not in indices:
            visit(v)

    return components


def format_state(
    state: Tuple[int, ...],
) -> str:
    return "\n".join(
        " ".join(
            f"{state[col_id(x, y)]:2d}"
            for x in range(X_SIZE)
        )
        for y in range(Y_SIZE)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-states",
        type=int,
        default=1_000_000,
    )
    args = parser.parse_args()

    print(
        "Generating z-normalized S profile templates...",
        flush=True,
    )

    start = time.perf_counter()
    templates = build_templates()

    print(
        f"Unique normalized templates: "
        f"{len(templates)}",
        flush=True,
    )
    print(
        f"Generation time: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )

    candidates = build_candidate_index(
        templates
    )

    print(
        "Candidate templates per column:",
        flush=True,
    )

    for col in range(NCOLS):
        x, y = xy(col)
        print(
            f"  ({x},{y}): "
            f"{len(candidates[col])}",
            flush=True,
        )

    print(
        "\nDiscovering automaton...",
        flush=True,
    )

    start = time.perf_counter()

    states, graph, stats = discover(
        candidates,
        args.max_states,
    )

    elapsed = time.perf_counter() - start

    degree_counts = Counter(
        len(edges)
        for edges in graph.values()
    )

    print()
    print(
        f"States: {len(states):,}"
    )
    print(
        f"Transitions examined: "
        f"{stats.transitions_examined:,}"
    )
    print(
        f"Accepted placement transitions: "
        f"{stats.accepted:,}"
    )
    print(
        f"Distinct state transitions: "
        f"{sum(len(e) for e in graph.values()):,}"
    )
    print(
        f"Duplicate state transitions: "
        f"{stats.duplicates:,}"
    )
    print(
        f"Positive-advance transitions: "
        f"{stats.positive_advance:,}"
    )
    print(
        f"Zero-advance transitions: "
        f"{stats.zero_advance:,}"
    )
    print(
        f"Branching states: "
        f"{stats.branching_states:,}"
    )
    print(
        f"Maximum out-degree: "
        f"{stats.max_out_degree}"
    )
    print(
        f"Out-degree distribution: "
        f"{dict(sorted(degree_counts.items()))}"
    )
    print(
        f"Maximum normalized height: "
        f"{stats.max_height}"
    )
    print(
        f"Elapsed: {elapsed:.3f} s"
    )
    print(
        f"Peak RSS: {rss_mb():,.0f} MB"
    )

    if graph:
        print(
            "\nRunning SCC analysis...",
            flush=True,
        )

        components = tarjan_scc(graph)

        sizes = sorted(
            (len(c) for c in components),
            reverse=True,
        )

        cyclic = [
            c
            for c in components
            if len(c) > 1
        ]

        self_loops = 0
        for state, edges in graph.items():
            if state in edges:
                self_loops += 1

        print(
            f"SCCs: {len(components):,}"
        )
        print(
            f"Largest SCC sizes: "
            f"{sizes[:20]}"
        )
        print(
            f"Nontrivial SCCs: "
            f"{len(cyclic):,}"
        )
        print(
            f"Self-loop states: "
            f"{self_loops:,}"
        )

        # Show an example branching state, if any.
        for state, edges in graph.items():
            if len(edges) > 1:
                print(
                    "\nExample branching state:"
                )
                print(
                    format_state(state)
                )
                print(
                    f"\nOutgoing states: "
                    f"{len(edges)}"
                )
                break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
