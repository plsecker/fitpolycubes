#!/usr/bin/env python3
"""
Ragged profile / finite-state prototype for S in 4x8.

This is the formulation we now want to test.

For each (x,y) column define:

    h[x,y] = smallest unfilled z.

Equivalently, the next unfilled solid-diagonal level is:

    d[x,y] = x + y + h[x,y].

Thus a flat z-frontier corresponds to a ragged surface when viewed in
planes perpendicular to (1,1,1).  This is the "ragged configuration"
description in a much simpler coordinate system.

A placement is a valid transition from a frontier when, for every column
it touches, its occupied z-levels form one contiguous run beginning exactly
at that column's current h.

We then normalize a state by subtracting min(h).  The normalized profile is
the finite automaton state; the amount subtracted is the transition's
forward progress.

This is an INTERIOR automaton experiment.  Absolute N is not part of the
state.  A cycle returning to the zero profile with total progress N would
correspond to a 4x8xN tiling, provided the boundary interpretation is valid.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from collections import defaultdict, deque
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
    transitions: int = 0
    accepted: int = 0
    duplicates: int = 0
    positive_advance: int = 0
    zero_advance: int = 0
    max_queue: int = 0
    max_height: int = 0
    last_report_time: float = 0.0
    last_report_states: int = 0


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
) -> Template | None:
    """
    Convert an S placement into a z-translation-invariant column template.

    For each (x,y), the piece must occupy a contiguous z-run.  If a column
    has a gap, this orientation cannot be applied at a monotone frontier,
    because it would jump over an unfilled cell.
    """
    by_col: Dict[int, List[int]] = defaultdict(list)

    for x, y, z in placement:
        by_col[col_id(x, y)].append(z)

    runs: List[Run] = []

    for col in sorted(by_col):
        levels = sorted(by_col[col])

        for a, b in zip(levels, levels[1:]):
            if b != a + 1:
                return None

        runs.append(
            Run(
                col=col,
                start=levels[0],
                length=len(levels),
            )
        )

    return Template(tuple(runs))


def build_templates() -> List[Template]:
    """
    Generate legal S placements in a 4x8x20 box and collapse pure z
    translations into unique templates.
    """
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
        if make_template(p) is not None
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


def template_string(template: Template) -> str:
    parts = []

    for run in template.runs:
        x, y = xy(run.col)

        if run.length == 1:
            parts.append(
                f"({x},{y}):{run.start}"
            )
        else:
            parts.append(
                f"({x},{y}):"
                f"{run.start}+{run.length}"
            )

    return " ".join(parts)


def build_candidate_index(
    templates: Sequence[Template],
) -> Dict[int, List[Template]]:
    """
    Index by every column touched by the template.

    At runtime, a template is legal only if the same z-translation works
    for all of its runs.
    """
    result: Dict[int, List[Template]] = {
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
    """
    Try placing template with target_col aligned to its frontier height.

    Since the state is normalized, min(state)=0.

    Translation t is determined by:
        state[target_col] = template.start(target_col) + t

    All other touched columns must agree with the same t.
    """
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
        expected = run.start + shift

        if state[run.col] != expected:
            return None

        new_state[run.col] += run.length

    new_min = min(new_state)

    normalized = tuple(
        h - new_min
        for h in new_state
    )

    return normalized, new_min


def report(
    stats: Stats,
    queue: deque[Tuple[int, ...]],
    seen: set[Tuple[int, ...]],
) -> None:
    now = time.perf_counter()

    if now - stats.last_report_time < 2.0:
        return

    delta = (
        stats.states -
        stats.last_report_states
    )

    dt = now - stats.last_report_time

    rate = (
        delta / dt
        if dt > 0
        else 0.0
    )

    stats.last_report_time = now
    stats.last_report_states = stats.states

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
    candidates: Dict[int, List[Template]],
    max_states: int,
) -> Tuple[set[Tuple[int, ...]], Stats]:
    """
    Discover the reachable normalized profile automaton.
    """
    start = (0,) * NCOLS

    queue: deque[Tuple[int, ...]] = deque([start])
    seen: set[Tuple[int, ...]] = {start}

    stats = Stats(
        states=1,
        last_report_time=time.perf_counter(),
    )

    while queue:
        if len(seen) >= max_states:
            print(
                f"[limit] reached {max_states:,} states",
                flush=True,
            )
            break

        state = queue.popleft()

        target_col = min(
            range(NCOLS),
            key=lambda c: (state[c], c),
        )

        for template in candidates[target_col]:
            stats.transitions += 1

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

    return seen, stats


def format_profile(
    state: Tuple[int, ...],
) -> str:
    rows = []

    for y in range(Y_SIZE):
        rows.append(
            " ".join(
                f"{state[col_id(x, y)]:2d}"
                for x in range(X_SIZE)
            )
        )

    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Discover the normalized ragged profile automaton "
            "for S in a 4x8 prism."
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
        default=10,
    )
    args = parser.parse_args()

    print(
        "Generating S column-profile templates...",
        flush=True,
    )

    start = time.perf_counter()
    templates = build_templates()

    print(
        f"Unique monotone templates: "
        f"{len(templates)}",
        flush=True,
    )

    print(
        f"Template generation: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )

    if args.show_templates:
        print(
            f"\nFirst "
            f"{min(args.show_templates, len(templates))}"
            f" templates:",
            flush=True,
        )

        for i, template in enumerate(
            templates[:args.show_templates]
        ):
            print(
                f"  {i:3d}: "
                f"{template_string(template)}",
                flush=True,
            )

    candidates = build_candidate_index(
        templates
    )

    print(
        "\nCandidate templates per column:",
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
        f"\nStarting normalized profile BFS "
        f"(limit={args.max_states:,})...",
        flush=True,
    )

    start = time.perf_counter()

    states, stats = discover(
        templates,
        candidates,
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
        f"Maximum normalized height: "
        f"{stats.max_height}"
    )
    print(
        f"Max queue: "
        f"{stats.max_queue:,}"
    )
    print(
        f"Elapsed: "
        f"{elapsed:.3f} s"
    )
    print(
        f"Peak RSS: "
        f"{rss_mb():,.0f} MB"
    )

    # Show a few non-flat states if we found any.
    interesting = [
        s
        for s in states
        if any(h != 0 for h in s)
    ]

    if interesting:
        print(
            "\nExample ragged state:"
        )
        print(
            format_profile(
                interesting[0]
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
