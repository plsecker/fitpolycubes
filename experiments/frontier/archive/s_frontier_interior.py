#!/usr/bin/env python3
"""
Interior finite-state experiment for the S pentacube in a 4x8 prism.

Important: this models the MIDDLE of a long prism, where every diagonal
cross-section is the same 4x8 set of 32 cells.  There is deliberately no
absolute z/d coordinate in the state.

That is the translationally invariant automaton idea we want to test.

A state is five 32-bit diagonal masks:
    mask[0] = current frontier diagonal
    mask[1] = next diagonal
    ...
    mask[4] = furthest diagonal affected by an S placement

When mask[0] becomes completely full (32 bits), we shift the frontier one
diagonal and continue.

This is an exploratory state-graph generator, not yet a finite-box solver.
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

BITS_PER_PLANE = X_SIZE * Y_SIZE
PLANE_MASK = (1 << BITS_PER_PLANE) - 1
SPAN = 4
WORDS = SPAN + 1


@dataclass(frozen=True)
class Signature:
    masks: Tuple[int, ...]


@dataclass
class Stats:
    processed: int = 0
    generated: int = 0
    accepted: int = 0
    duplicates: int = 0
    shifts: int = 0
    last_report: float = 0.0
    last_processed: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def pack(masks: Sequence[int]) -> int:
    state = 0
    for i, mask in enumerate(masks):
        state |= mask << (i * BITS_PER_PLANE)
    return state


def first_mask(state: int) -> int:
    return state & PLANE_MASK


def shift(state: int) -> int:
    return state >> BITS_PER_PLANE


def bit_index(mask: int) -> int:
    low = mask & -mask
    return low.bit_length() - 1


def signature_from_placement(
    placement: Sequence[Tuple[int, int, int]]
) -> Signature:
    encoded = [
        (x + y + z, x + X_SIZE * y)
        for x, y, z in placement
    ]

    min_d = min(d for d, _ in encoded)
    max_d = max(d for d, _ in encoded)

    masks = [0] * WORDS

    for d, bit in encoded:
        rel = d - min_d
        if not (0 <= rel < WORDS):
            raise ValueError("S placement exceeds expected diagonal span")
        masks[rel] |= 1 << bit

    return Signature(tuple(masks))


def build_signatures() -> List[Signature]:
    # Large enough that all translations/orientations are represented;
    # absolute z is discarded immediately by normalization.
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    unique = {
        signature_from_placement(p).masks
        for p in placements.values()
    }

    return [Signature(m) for m in sorted(unique)]


def build_candidates(
    signatures: Sequence[Signature],
) -> Dict[int, List[Signature]]:
    candidates: Dict[int, List[Signature]] = {
        bit: []
        for bit in range(BITS_PER_PLANE)
    }

    for sig in signatures:
        # A normalized placement has at least one cell in plane 0.
        bits = sig.masks[0]

        while bits:
            low = bits & -bits
            bit = low.bit_length() - 1
            candidates[bit].append(sig)
            bits ^= low

    return candidates


def apply_signature(
    state: int,
    sig: Signature,
) -> int | None:
    """
    Return state | sig if there is no overlap in any of the five planes.
    """
    sig_state = pack(sig.masks)

    # Fast whole-state overlap test.
    # The masks occupy disjoint 32-bit fields, so ordinary AND is valid.
    if state & sig_state:
        return None

    return state | sig_state


def report(
    stats: Stats,
    queue: deque[int],
    seen: set[int],
) -> None:
    now = time.perf_counter()

    if now - stats.last_report < 2.0:
        return

    delta = stats.processed - stats.last_processed
    elapsed = (
        now - stats.last_report
        if stats.last_report
        else 0.0
    )

    rate = delta / elapsed if elapsed > 0 else 0.0

    stats.last_report = now
    stats.last_processed = stats.processed

    print(
        f"[progress] "
        f"processed={stats.processed:,} "
        f"states={len(seen):,} "
        f"queue={len(queue):,} "
        f"generated={stats.generated:,} "
        f"accepted={stats.accepted:,} "
        f"duplicates={stats.duplicates:,} "
        f"shifts={stats.shifts:,} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


def discover(
    candidates: Dict[int, List[Signature]],
    max_states: int,
) -> None:
    start = time.perf_counter()

    queue: deque[int] = deque([0])
    seen: set[int] = {0}
    stats = Stats(last_report=start)

    while queue:
        if len(seen) >= max_states:
            print(
                f"[limit] reached {max_states:,} states",
                flush=True,
            )
            break

        state = queue.popleft()
        stats.processed += 1

        current = first_mask(state)

        # In the infinite interior, every diagonal has all 32 cells.
        if current == PLANE_MASK:
            next_state = shift(state)
            stats.shifts += 1

            if next_state in seen:
                stats.duplicates += 1
            else:
                seen.add(next_state)
                queue.append(next_state)

            report(stats, queue, seen)
            continue

        missing = PLANE_MASK & ~current

        if missing == 0:
            continue

        bit = bit_index(missing)

        for sig in candidates[bit]:
            stats.generated += 1

            next_state = apply_signature(
                state,
                sig,
            )

            if next_state is None:
                continue

            stats.accepted += 1

            if next_state in seen:
                stats.duplicates += 1
                continue

            seen.add(next_state)
            queue.append(next_state)

        report(stats, queue, seen)

    elapsed = time.perf_counter() - start

    print()
    print(
        f"Interior states: {len(seen):,}"
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
        f"Duplicate transitions/states: {stats.duplicates:,}"
    )
    print(
        f"Plane shifts: {stats.shifts:,}"
    )
    print(
        f"Elapsed: {elapsed:.3f} s"
    )
    print(
        f"Peak RSS: {rss_mb():,.0f} MB"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-states",
        type=int,
        default=5_000_000,
        help="hard memory safety limit",
    )
    args = parser.parse_args()

    print(
        "Generating normalized S interior signatures...",
        flush=True,
    )

    start = time.perf_counter()
    signatures = build_signatures()

    print(
        f"Unique signatures: {len(signatures)}",
        flush=True,
    )
    print(
        f"Generation time: {time.perf_counter() - start:.3f} s",
        flush=True,
    )

    candidates = build_candidates(signatures)

    print(
        f"Candidate cell classes: "
        f"{sum(bool(v) for v in candidates.values())}",
        flush=True,
    )
    print(
        f"Starting translationally-invariant interior BFS "
        f"(limit={args.max_states:,})...",
        flush=True,
    )

    discover(
        candidates,
        args.max_states,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
