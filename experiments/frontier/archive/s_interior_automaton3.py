#!/usr/bin/env python3
"""
Interior solid-diagonal automaton for S in 4x8xN.

Important lattice fact:
    d = x+y+z
and translating a cell by (1,1,1) changes d by 3.

Therefore the lattice cross-section repeats with period 3 in d,
not period 1.  There are three interior plane phases.

This prototype:
  * finds the three stable (u,v) plane shapes;
  * represents the frontier as five consecutive phase-aware plane masks;
  * keeps the phase (d mod 3) in the state;
  * explores the translation-invariant interior graph;
  * reports branching and SCC structure.

It is still an automaton experiment, not the finite-box solver.
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
    slices: Tuple[Tuple[Tuple[int, int], ...], ...]


@dataclass
class Stats:
    processed: int = 0
    generated: int = 0
    accepted: int = 0
    duplicates: int = 0
    shifts: int = 0
    branching: int = 0
    max_degree: int = 0
    last_time: float = 0.0
    last_processed: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def solid_coords(x: int, y: int, z: int):
    return x + y + z, x - y, y - z


def plane_cells(Z: int):
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


def find_phase_shapes(
    planes: Dict[int, Tuple[Tuple[int, int], ...]]
):
    """
    Find a central run where:
        shape[d] == shape[d+3] == shape[d+6] ...
    """
    ds = sorted(planes)

    candidates = []

    for d in ds:
        if d + 12 > ds[-1]:
            break

        shape = planes[d]

        ok = True
        for k in range(d, d + 12, 3):
            if planes.get(k) != shape:
                ok = False
                break

        if ok:
            candidates.append(d)

    if not candidates:
        raise RuntimeError(
            "Could not find 3-periodic interior plane shapes"
        )

    base = candidates[len(candidates) // 2]

    phases = {
        phase: planes[base + phase]
        for phase in range(3)
    }

    return base, phases


def normalize_signature(
    placement: Sequence[Tuple[int, int, int]]
):
    encoded = [
        solid_coords(x, y, z)
        for x, y, z in placement
    ]

    min_d = min(d for d, _, _ in encoded)
    max_d = max(d for d, _, _ in encoded)

    slices = []
    for rel in range(max_d - min_d + 1):
        slices.append(
            tuple(sorted(
                (u, v)
                for d, u, v in encoded
                if d - min_d == rel
            ))
        )

    return Signature(tuple(slices))


def build_signatures():
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 30),
        break_symmetry=False,
    )

    return list({
        normalize_signature(p)
        for p in placements.values()
    })


def phase_index(
    phase_shapes,
):
    return {
        phase: {
            cell: i
            for i, cell in enumerate(shape)
        }
        for phase, shape in phase_shapes.items()
    }


def make_candidates(
    signatures: Sequence[Signature],
    phase_shapes,
):
    """
    For each target phase/cell, create placement masks translated so the
    target cell is on relative plane 0.

    The placement may start at relative slice 0..4.
    """
    indices = phase_index(phase_shapes)

    candidates = {
        phase: {i: [] for i in range(len(shape))}
        for phase, shape in phase_shapes.items()
    }

    for sig in signatures:
        for target_rel, cells in enumerate(sig.slices):
            if target_rel > SPAN:
                continue

            for target_cell in cells:
                masks = [0] * (SPAN + 1)
                valid = True

                for rel_d, slice_cells in enumerate(sig.slices):
                    out_d = rel_d - target_rel
                    if out_d < 0 or out_d > SPAN:
                        valid = False
                        break

                    phase = out_d % 3
                    idx = indices[phase]

                    bits = 0
                    for cell in slice_cells:
                        if cell not in idx:
                            valid = False
                            break
                        bits |= 1 << idx[cell]

                    if not valid:
                        break

                    masks[out_d] |= bits

                if not valid:
                    continue

                target_phase = 0
                target_idx = indices[target_phase].get(
                    target_cell
                )

                # The target cell is on the current plane after translation,
                # so it must exist in phase 0.
                if target_idx is None:
                    continue

                key = (
                    tuple(masks),
                    target_idx,
                )

                if key not in candidates[0][target_idx]:
                    candidates[0][target_idx].append(
                        tuple(masks)
                    )

    return candidates


def apply(
    state,
    pmask,
):
    out = []

    for a, b in zip(state, pmask):
        if a & b:
            return None
        out.append(a | b)

    return tuple(out)


def first_empty(
    state,
    full_mask,
):
    missing = full_mask & ~state[0]
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def report(stats, queue, seen):
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
        f"shift={stats.shifts:,} "
        f"branch={stats.branching:,} "
        f"maxdeg={stats.max_degree} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


def discover(
    phase_shapes,
    candidates,
    max_states,
):
    """
    State:
        (phase, mask0, mask1, ..., mask4)

    The first mask is the current diagonal phase.
    """
    full_masks = tuple(
        (1 << len(phase_shapes[p])) - 1
        for p in range(3)
    )

    start = (0, 0, 0, 0, 0, 0)

    queue = deque([start])
    seen = {start}
    graph = {}

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
        phase = state[0]
        masks = state[1:]
        stats.processed += 1

        full = full_masks[phase]

        if masks[0] == full:
            next_phase = (phase + 1) % 3
            shifted = (
                next_phase,
                *masks[1:],
                0,
            )
            stats.shifts += 1

            edges = graph.setdefault(state, set())
            edges.add(shifted)

            if shifted in seen:
                stats.duplicates += 1
            else:
                seen.add(shifted)
                queue.append(shifted)

            report(stats, queue, seen)
            continue

        bit = first_empty(masks, full)

        if bit < 0:
            continue

        outgoing = set()

        for pmask in candidates[0].get(bit, ()):
            stats.generated += 1

            nxt_masks = apply(
                masks,
                pmask,
            )

            if nxt_masks is None:
                continue

            stats.accepted += 1
            nxt = (phase, *nxt_masks)
            outgoing.add(nxt)

        if len(outgoing) > 1:
            stats.branching += 1

        stats.max_degree = max(
            stats.max_degree,
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


def tarjan(graph):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-states",
        type=int,
        default=1_000_000,
    )
    args = parser.parse_args()

    print(
        "Finding 3-periodic interior diagonal planes...",
        flush=True,
    )

    planes = plane_cells(30)
    base_d, phase_shapes = find_phase_shapes(planes)

    print(
        f"Interior phase base d={base_d}",
        flush=True,
    )

    for phase in range(3):
        print(
            f"  phase {phase}: "
            f"{len(phase_shapes[phase])} cells",
            flush=True,
        )

    print(
        "\nGenerating normalized S signatures...",
        flush=True,
    )

    start = time.perf_counter()
    signatures = build_signatures()

    print(
        f"Unique signatures: "
        f"{len(signatures)}",
        flush=True,
    )
    print(
        f"Generation time: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )

    candidates = make_candidates(
        signatures,
        phase_shapes,
    )

    nonempty = sum(
        len(v)
        for v in candidates[0].values()
    )

    print(
        f"Candidate entries: {nonempty}",
        flush=True,
    )

    print(
        f"\nStarting 3-phase interior automaton "
        f"(limit={args.max_states:,})...",
        flush=True,
    )

    start = time.perf_counter()

    states, graph, stats = discover(
        phase_shapes,
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
        f"Branching states: {stats.branching:,}"
    )
    print(
        f"Max out-degree: {stats.max_degree}"
    )
    print(
        f"Elapsed: {elapsed:.3f} s"
    )
    print(
        f"Peak RSS: {rss_mb():,.0f} MB"
    )

    if len(states) < args.max_states:
        comps = tarjan(graph)
        sizes = sorted(
            (len(c) for c in comps),
            reverse=True,
        )
        nontrivial = [
            c for c in comps
            if len(c) > 1
        ]
        self_loops = sum(
            1 for v, e in graph.items()
            if v in e
        )

        print(
            f"SCCs: {len(comps):,}"
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


if __name__ == "__main__":
    raise SystemExit(main())
