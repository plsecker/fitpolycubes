#!/usr/bin/env python3
"""
Interior ragged-profile automaton for S in a 4x8 prism.

This version models the frontier as 32 "heights":

    h[x,y] = the next diagonal d=x+y+z that is not yet filled
              in column (x,y).

All cells with d < h[x,y] are considered filled.

For the translationally-invariant interior:
    * absolute d is removed;
    * states are normalized by subtracting min(h);
    * an S placement is a transition if, in every column it touches,
      its occupied diagonal levels are a contiguous run starting exactly
      at that column's current h.

When a transition raises every column that was at the minimum, the
normalized profile changes and the edge has a positive "advance" weight.
That gives us an actual finite-state automaton candidate.

This is still an experimental interior model.  Start/end boundary
conditions for a finite 4x8xN box are deliberately not included yet.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
NCOLS = X_SIZE * Y_SIZE


@dataclass(frozen=True)
class ColumnRun:
    col: int
    start: int      # relative diagonal offset from placement minimum d
    length: int


@dataclass(frozen=True)
class Template:
    """
    An S placement normalized so its minimum diagonal is 0.

    Every touched (x,y) column contains a contiguous run of diagonal
    levels.  The template can be translated freely along z.
    """
    runs: Tuple[ColumnRun, ...]


@dataclass
class Stats:
    states: int = 0
    transitions: int = 0
    accepted: int = 0
    duplicates: int = 0
    positive_advance: int = 0
    zero_advance: int = 0
    max_queue: int = 0
    last_time: float = 0.0
    last_states: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def column_id(x: int, y: int) -> int:
    return x + X_SIZE * y


def make_template(
    placement: Sequence[Tuple[int, int, int]]
) -> Template | None:
    """
    Convert a concrete placement into a z-translation-invariant template.

    We normalize by the minimum solid-diagonal d=x+y+z.

    The placement can be used as a transition from a ragged frontier only
    when every column it touches contains a contiguous run of d-values.
    """
    encoded: List[Tuple[int, int, int]] = []

    for x, y, z in placement:
        col = column_id(x, y)
        d = x + y + z
        encoded.append((col, d, z))

    min_d = min(d for _, d, _ in encoded)

    # For every column, collect the diagonal levels it occupies.
    by_col: Dict[int, List[int]] = defaultdict(list)

    for col, d, _ in encoded:
        by_col[col].append(d - min_d)

    runs: List[ColumnRun] = []

    for col in sorted(by_col):
        levels = sorted(by_col[col])

        # The cells in a given (x,y) column must form a contiguous run.
        for a, b in zip(levels, levels[1:]):
            if b != a + 1:
                return None

        runs.append(
            ColumnRun(
                col=col,
                start=levels[0],
                length=len(levels),
            )
        )

    # The transition must have at least one cell on its minimum diagonal.
    if not any(run.start == 0 for run in runs):
        return None

    return Template(tuple(runs))


def build_templates() -> List[Template]:
    """
    Generate concrete S placements in a 4x8x20 box and collapse all z
    translations into unique ragged-profile transition templates.
    """
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    unique: set[Tuple[Tuple[int, int, int], ...]] = set()

    for placement in placements.values():
        template = make_template(placement)

        if template is None:
            continue

        key = tuple(
            (run.col, run.start, run.length)
            for run in template.runs
        )

        unique.add(key)

    return [
        Template(
            tuple(
                ColumnRun(
                    col=col,
                    start=start,
                    length=length,
                )
                for col, start, length in key
            )
        )
        for key in sorted(unique)
    ]


def template_summary(template: Template) -> str:
    pieces = []

    for run in template.runs:
        x = run.col % X_SIZE
        y = run.col // X_SIZE

        if run.length == 1:
            pieces.append(
                f"({x},{y}):{run.start}"
            )
        else:
            pieces.append(
                f"({x},{y}):"
                f"{run.start}+{run.length}"
            )

    return " ".join(pieces)


def transition(
    state: Tuple[int, ...],
    template: Template,
) -> Tuple[Tuple[int, ...], int] | None:
    """
    Apply a template to a normalized profile.

    State normalization means min(state) == 0.

    A touched column is valid iff:
        state[col] == template.start

    because template.start is measured relative to the global minimum
    diagonal of the placement, which is the current global minimum 0.

    Returns:
        normalized next state,
        edge advance = new minimum before normalization.
    """
    h = list(state)

    for run in template.runs:
        if h[run.col] != run.start:
            return None

    for run in template.runs:
        h[run.col] += run.length

    new_min = min(h)

    normalized = tuple(
        value - new_min
        for value in h
    )

    return normalized, new_min


def report(
    stats: Stats,
    queue: deque[Tuple[int, ...]],
    seen: set[Tuple[int, ...]],
) -> None:
    now = time.perf_counter()

    if now - stats.last_time < 2.0:
        return

    delta = stats.states - stats.last_states
    dt = now - stats.last_time
    rate = delta / dt if dt > 0 else 0.0

    stats.last_time = now
    stats.last_states = stats.states
    stats.max_queue = max(
        stats.max_queue,
        len(queue),
    )

    print(
        f"[progress] "
        f"states={stats.states:,} "
        f"queue={len(queue):,} "
        f"trans={stats.transitions:,} "
        f"accepted={stats.accepted:,} "
        f"dup={stats.duplicates:,} "
        f"+advance={stats.positive_advance:,} "
        f"zero={stats.zero_advance:,} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


def discover(
    templates: Sequence[Template],
    max_states: int,
) -> Tuple[set[Tuple[int, ...]], Stats]:
    """
    BFS over normalized ragged profiles.

    This is the actual automaton discovery experiment.
    """
    # Flat frontier: next cell in every column is d=0.
    start = (0,) * NCOLS

    queue: deque[Tuple[int, ...]] = deque([start])
    seen: set[Tuple[int, ...]] = {start}

    stats = Stats(
        states=1,
        last_time=time.perf_counter(),
    )

    while queue:
        if len(seen) >= max_states:
            print(
                f"[limit] reached {max_states:,} states",
                flush=True,
            )
            break

        state = queue.popleft()

        for template in templates:
            stats.transitions += 1

            result = transition(
                state,
                template,
            )

            if result is None:
                continue

            next_state, advance = result
            stats.accepted += 1

            if advance > 0:
                stats.positive_advance += 1
            else:
                stats.zero_advance += 1

            if next_state in seen:
                stats.duplicates += 1
                continue

            seen.add(next_state)
            queue.append(next_state)
            stats.states += 1

        report(
            stats,
            queue,
            seen,
        )

    stats.max_queue = max(
        stats.max_queue,
        len(queue),
    )

    return seen, stats


def strongly_connected_components(
    states: Sequence[Tuple[int, ...]],
    templates: Sequence[Template],
) -> List[List[int]]:
    """
    Tarjan SCC implementation over the discovered state graph.

    We rebuild adjacency here after discovery.  The graph is expected to be
    modest; this is analysis code, not the production solver.
    """
    index_of = {
        state: i
        for i, state in enumerate(states)
    }

    adjacency: List[List[int]] = [
        []
        for _ in states
    ]

    for i, state in enumerate(states):
        edges: set[int] = set()

        for template in templates:
            result = transition(
                state,
                template,
            )

            if result is None:
                continue

            next_state, _ = result
            j = index_of.get(next_state)

            if j is not None:
                edges.add(j)

        adjacency[i] = sorted(edges)

    index = 0
    indices = [-1] * len(states)
    lowlink = [0] * len(states)
    stack: List[int] = []
    on_stack = [False] * len(states)
    components: List[List[int]] = []

    def visit(v: int) -> None:
        nonlocal index

        indices[v] = index
        lowlink[v] = index
        index += 1

        stack.append(v)
        on_stack[v] = True

        for w in adjacency[v]:
            if indices[w] == -1:
                visit(w)
                lowlink[v] = min(
                    lowlink[v],
                    lowlink[w],
                )
            elif on_stack[w]:
                lowlink[v] = min(
                    lowlink[v],
                    indices[w],
                )

        if lowlink[v] == indices[v]:
            component: List[int] = []

            while True:
                w = stack.pop()
                on_stack[w] = False
                component.append(w)

                if w == v:
                    break

            components.append(component)

    for v in range(len(states)):
        if indices[v] == -1:
            visit(v)

    return components


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Discover the interior ragged-profile automaton "
            "for S in 4x8."
        )
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=1_000_000,
    )
    parser.add_argument(
        "--show-templates",
        type=int,
        default=0,
        help="print first N normalized transition templates",
    )
    parser.add_argument(
        "--scc",
        action="store_true",
        help="run SCC analysis after discovery",
    )
    args = parser.parse_args()

    print(
        "Generating S ragged-profile templates...",
        flush=True,
    )

    start = time.perf_counter()

    templates = build_templates()

    print(
        f"Unique templates: {len(templates)}",
        flush=True,
    )
    print(
        f"Template generation: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )

    if args.show_templates:
        print(
            f"\nFirst {min(args.show_templates, len(templates))} templates:",
            flush=True,
        )

        for i, template in enumerate(
            templates[:args.show_templates]
        ):
            print(
                f"  {i:3d}: "
                f"{template_summary(template)}",
                flush=True,
            )

    print(
        "\nStarting normalized ragged-profile BFS...",
        flush=True,
    )

    start = time.perf_counter()

    states, stats = discover(
        templates,
        args.max_states,
    )

    elapsed = time.perf_counter() - start

    print()
    print(
        f"States: {len(states):,}"
    )
    print(
        f"Transitions examined: "
        f"{stats.transitions:,}"
    )
    print(
        f"Accepted transitions: "
        f"{stats.accepted:,}"
    )
    print(
        f"Duplicate transitions: "
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
        f"Max queue: "
        f"{stats.max_queue:,}"
    )
    print(
        f"Elapsed: {elapsed:.3f} s"
    )
    print(
        f"Peak RSS: {rss_mb():,.0f} MB"
    )

    if args.scc and len(states) < args.max_states:
        print(
            "\nComputing SCCs...",
            flush=True,
        )

        ordered_states = list(states)

        components = strongly_connected_components(
            ordered_states,
            templates,
        )

        sizes = sorted(
            (len(c) for c in components),
            reverse=True,
        )

        print(
            f"SCC count: {len(components):,}"
        )
        print(
            f"Largest SCCs: "
            f"{sizes[:20]}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
