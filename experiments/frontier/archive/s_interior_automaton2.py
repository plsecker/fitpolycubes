#!/usr/bin/env python3
"""
Discover the translation-invariant INTERIOR frontier automaton for S in
a 4x8xN prism.

This deliberately removes the finite-box end effects.

For a sufficiently long 4x8xN prism, the solid-diagonal cross-section
becomes constant in the middle.  We identify one such stable diagonal
plane, use its (u,v) cells as the fixed 2D cross-section, and represent a
frontier only by the occupancy of cells in the next few diagonal planes.

There is NO absolute d in the state.

The purpose is to answer the automaton question:
    do different histories converge to the same ragged frontier?
    do those states contain cycles/SCCs?

This is not yet a finite-box solver; it is the interior-state experiment.
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
SPAN = 4


@dataclass(frozen=True)
class Signature:
    # Each slice is a set of (u,v) cells, normalized relative to min d.
    slices: Tuple[Tuple[Tuple[int, int], ...], ...]


@dataclass
class Stats:
    processed: int = 0
    generated: int = 0
    accepted: int = 0
    duplicates: int = 0
    shifts: int = 0
    branching_states: int = 0
    max_out_degree: int = 0
    last_time: float = 0.0
    last_processed: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def solid_coords(
    x: int,
    y: int,
    z: int,
) -> Tuple[int, int, int]:
    return x + y + z, x - y, y - z


def plane_cells(
    Z: int,
) -> Dict[int, Tuple[Tuple[int, int], ...]]:
    grouped: Dict[int, set[Tuple[int, int]]] = {}

    for z in range(Z):
        for y in range(Y_SIZE):
            for x in range(X_SIZE):
                d, u, v = solid_coords(x, y, z)
                grouped.setdefault(d, set()).add((u, v))

    return {
        d: tuple(sorted(cells))
        for d, cells in grouped.items()
    }


def stable_plane(
    planes: Dict[int, Tuple[Tuple[int, int], ...]]
) -> Tuple[int, Tuple[Tuple[int, int], ...]]:
    """
    Find the longest run of identical diagonal-plane shapes and return
    the middle d and shape.
    """
    best_start = None
    best_len = 0

    ds = sorted(planes)

    start = ds[0]
    run_len = 1

    for prev, cur in zip(ds, ds[1:]):
        if planes[cur] == planes[prev]:
            run_len += 1
        else:
            if run_len > best_len:
                best_start = start
                best_len = run_len
            start = cur
            run_len = 1

    if run_len > best_len:
        best_start = start
        best_len = run_len

    if best_start is None:
        raise RuntimeError("No diagonal plane run found")

    d = best_start + best_len // 2
    return d, planes[d]


def normalize_signature(
    placement: Sequence[Tuple[int, int, int]],
) -> Signature:
    encoded = [
        solid_coords(x, y, z)
        for x, y, z in placement
    ]

    min_d = min(d for d, _, _ in encoded)
    max_d = max(d for d, _, _ in encoded)

    slices = []

    for rel_d in range(max_d - min_d + 1):
        cells = tuple(sorted(
            (u, v)
            for d, u, v in encoded
            if d - min_d == rel_d
        ))
        slices.append(cells)

    return Signature(tuple(slices))


def build_signatures() -> List[Signature]:
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 30),
        break_symmetry=False,
    )

    unique = {
        normalize_signature(p)
        for p in placements.values()
    }

    # Only signatures whose d-span fits our frontier window.
    return [
        sig for sig in unique
        if len(sig.slices) <= SPAN + 1
    ]


def build_shape_index(
    shape: Tuple[Tuple[int, int], ...]
) -> Dict[Tuple[int, int], int]:
    return {
        cell: i
        for i, cell in enumerate(shape)
    }


def candidate_masks(
    signature: Signature,
    target_cell: Tuple[int, int],
    target_rel_d: int,
    shape: Tuple[Tuple[int, int], ...],
) -> Tuple[int, ...] | None:
    """
    Translate a normalized placement so that the target cell lies on
    relative plane 0.  Return plane-local bitmasks.
    """
    if target_rel_d < 0 or target_rel_d >= len(signature.slices):
        return None

    if target_cell not in signature.slices[target_rel_d]:
        return None

    shift = target_rel_d
    idx = build_shape_index(shape)

    masks = [0] * (SPAN + 1)

    for rel_d, cells in enumerate(signature.slices):
        out_d = rel_d - shift

        if out_d < 0 or out_d > SPAN:
            return None

        for cell in cells:
            if cell not in idx:
                return None
            masks[out_d] |= 1 << idx[cell]

    return tuple(masks)


def make_candidate_index(
    signatures: Sequence[Signature],
    shape: Tuple[Tuple[int, int], ...],
) -> Dict[int, List[Tuple[int, ...]]]:
    idx = build_shape_index(shape)
    result = {i: [] for i in range(len(shape))}

    seen: set[Tuple[int, Tuple[int, ...]]] = set()

    for sig in signatures:
        for rel_d, cells in enumerate(sig.slices):
            for cell in cells:
                if cell not in idx:
                    continue

                target_bit = idx[cell]
                masks = candidate_masks(
                    sig,
                    cell,
                    rel_d,
                    shape,
                )

                if masks is None:
                    continue

                key = (target_bit, masks)

                if key in seen:
                    continue

                seen.add(key)
                result[target_bit].append(masks)

    return result


def apply(
    state: Tuple[int, ...],
    placement_masks: Tuple[int, ...],
) -> Tuple[int, ...] | None:
    out = []

    for a, b in zip(state, placement_masks):
        if a & b:
            return None
        out.append(a | b)

    return tuple(out)


def shift(
    state: Tuple[int, ...]
) -> Tuple[int, ...]:
    return state[1:] + (0,)


def first_empty(
    state: Tuple[int, ...],
    shape_bits: int,
) -> int:
    missing = shape_bits & ~state[0]
    if missing == 0:
        return -1

    low = missing & -missing
    return low.bit_length() - 1


def report(
    stats: Stats,
    queue: deque[Tuple[int, ...]],
    seen: set[Tuple[int, ...]],
) -> None:
    now = time.perf_counter()

    if now - stats.last_time < 2.0:
        return

    delta = stats.processed - stats.last_processed
    dt = now - stats.last_time
    rate = delta / dt if dt > 0 else 0.0

    stats.last_time = now
    stats.last_processed = stats.processed

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
    shape: Tuple[Tuple[int, int], ...],
    candidates: Dict[int, List[Tuple[int, ...]]],
    max_states: int,
):
    shape_bits = (1 << len(shape)) - 1

    start = (0,) * (SPAN + 1)

    queue: deque[Tuple[int, ...]] = deque([start])
    seen: set[Tuple[int, ...]] = {start}

    graph: Dict[Tuple[int, ...], set[Tuple[int, ...]]] = {}

    stats = Stats(
        last_time=time.perf_counter()
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

        if state[0] == shape_bits:
            next_state = shift(state)
            stats.shifts += 1

            edges = graph.setdefault(state, set())
            edges.add(next_state)

            if next_state in seen:
                stats.duplicates += 1
            else:
                seen.add(next_state)
                queue.append(next_state)

            report(stats, queue, seen)
            continue

        bit = first_empty(state, shape_bits)

        if bit < 0:
            continue

        outgoing = set()

        for pmask in candidates.get(bit, ()):
            stats.generated += 1

            next_state = apply(
                state,
                pmask,
            )

            if next_state is None:
                continue

            stats.accepted += 1
            outgoing.add(next_state)

        if len(outgoing) > 1:
            stats.branching_states += 1

        stats.max_out_degree = max(
            stats.max_out_degree,
            len(outgoing),
        )

        graph[state] = outgoing

        for next_state in outgoing:
            if next_state in seen:
                stats.duplicates += 1
                continue

            seen.add(next_state)
            queue.append(next_state)

        report(stats, queue, seen)

    return seen, graph, stats


def tarjan(
    graph: Dict[Tuple[int, ...], set[Tuple[int, ...]]]
) -> List[List[Tuple[int, ...]]]:
    index = 0
    indices: Dict[Tuple[int, ...], int] = {}
    low: Dict[Tuple[int, ...], int] = {}
    stack: List[Tuple[int, ...]] = []
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-states", type=int, default=1_000_000)
    args = parser.parse_args()

    print(
        "Finding stable solid-diagonal cross-section...",
        flush=True,
    )

    planes = plane_cells(30)
    stable_d, shape = stable_plane(planes)

    print(
        f"Stable plane: d={stable_d}, cells={len(shape)}",
        flush=True,
    )
    print(
        "Stable (u,v) cells:",
        " ".join(
            f"({u:+d},{v:+d})"
            for u, v in shape
        ),
        flush=True,
    )

    print(
        "\nGenerating normalized S signatures...",
        flush=True,
    )

    start = time.perf_counter()
    signatures = build_signatures()
    print(
        f"Unique signatures: {len(signatures)}",
        flush=True,
    )
    print(
        f"Generation time: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )

    candidates = make_candidate_index(
        signatures,
        shape,
    )

    print(
        "Candidate counts:",
        flush=True,
    )

    for bit, values in candidates.items():
        if values:
            print(
                f"  bit {bit:2d}: {len(values)}",
                flush=True,
            )

    print(
        f"\nStarting translation-invariant interior BFS "
        f"(limit={args.max_states:,})...",
        flush=True,
    )

    start = time.perf_counter()

    states, graph, stats = discover(
        shape,
        candidates,
        args.max_states,
    )

    elapsed = time.perf_counter() - start

    print()
    print(
        f"States: {len(states):,}"
    )
    print(
        f"Processed: {stats.processed:,}"
    )
    print(
        f"Transitions generated: {stats.generated:,}"
    )
    print(
        f"Transitions accepted: {stats.accepted:,}"
    )
    print(
        f"Duplicates: {stats.duplicates:,}"
    )
    print(
        f"Plane shifts: {stats.shifts:,}"
    )
    print(
        f"Branching states: {stats.branching_states:,}"
    )
    print(
        f"Max out-degree: {stats.max_out_degree}"
    )
    print(
        f"Elapsed: {elapsed:.3f} s"
    )
    print(
        f"Peak RSS: {rss_mb():,.0f} MB"
    )

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
            1
            for v, edges in graph.items()
            if v in edges
        )

        print(
            f"SCCs: {len(components):,}"
        )
        print(
            f"Largest SCCs: {sizes[:20]}"
        )
        print(
            f"Nontrivial SCCs: {len(nontrivial):,}"
        )
        print(
            f"Self-loops: {self_loops:,}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
