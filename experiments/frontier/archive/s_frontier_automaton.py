#!/usr/bin/env python3
"""
Discover the finite-state frontier automaton for S in a 4x8 prism.

This is deliberately an INTERIOR automaton experiment.

Key idea:
    In the middle of a long 4x8xN prism, diagonal planes are identical.
    Translating a frontier one diagonal along z should not create a new
    state. Therefore the absolute diagonal number must NOT be part of
    the state key.

A state is five 32-bit masks, packed into one Python integer:
    mask[0] = current diagonal
    mask[1] = next diagonal
    ...
    mask[4] = furthest diagonal touched by an S placement

When mask[0] is full, the frontier shifts by one diagonal.

We generate normalized S placement signatures from the existing authoritative
placement generator.  A signature is translated along z so its minimum
diagonal is zero; therefore it describes a possible interior transition.

This prototype discovers the reachable interior state graph.  It does not
yet prove a finite-box result by itself; the next stage is to connect the
start/end boundary regions to this graph.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements


X_SIZE = 4
Y_SIZE = 8
PLANE_BITS = X_SIZE * Y_SIZE
PLANE_MASK = (1 << PLANE_BITS) - 1
FRONTIER_SPAN = 4
WORDS = FRONTIER_SPAN + 1
WORD_BITS = PLANE_BITS
STATE_BITS = WORDS * WORD_BITS
STATE_MASK = (1 << STATE_BITS) - 1


@dataclass(frozen=True)
class Signature:
    """
    Normalized placement signature.

    masks[k] is the occupancy mask on relative diagonal k,
    with min diagonal normalized to k=0.
    """

    masks: Tuple[int, ...]


@dataclass
class Stats:
    processed: int = 0
    generated: int = 0
    duplicate: int = 0
    accepted: int = 0
    shifts: int = 0
    max_queue: int = 0
    max_states: int = 0
    last_report: float = 0.0
    last_processed: int = 0


def pack_masks(masks: Iterable[int]) -> int:
    state = 0
    shift = 0

    for mask in masks:
        state |= mask << shift
        shift += WORD_BITS

    return state


def unpack_masks(state: int) -> List[int]:
    masks = []
    mask = PLANE_MASK

    for i in range(WORDS):
        masks.append((state >> (i * WORD_BITS)) & mask)

    return masks


def shift_state(state: int) -> int:
    return state >> WORD_BITS


def first_empty_bit(mask: int) -> int:
    missing = PLANE_MASK & ~mask

    if missing == 0:
        return -1

    low = missing & -missing
    return low.bit_length() - 1


def make_signature(
    placement: Tuple[Tuple[int, int, int], ...]
) -> Signature | None:
    encoded = [
        (x + y + z, x + X_SIZE * y)
        for x, y, z in placement
    ]

    min_d = min(d for d, _ in encoded)
    max_d = max(d for d, _ in encoded)

    span = max_d - min_d

    if span > FRONTIER_SPAN:
        return None

    masks = [0] * WORDS

    for d, bit in encoded:
        rel = d - min_d
        if not (0 <= rel < WORDS):
            return None

        masks[rel] |= 1 << bit

    return Signature(tuple(masks))


def build_signatures() -> List[Signature]:
    """
    Generate S placements in a finite 4x8xN box and collapse translations
    along z into unique normalized interior signatures.
    """
    # N=20 is large enough to expose all ordinary orientations/translations
    # while keeping placement generation cheap.
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    unique: set[Tuple[int, ...]] = set()

    for placement in placements.values():
        sig = make_signature(tuple(placement))
        if sig is not None:
            unique.add(sig.masks)

    return [Signature(masks) for masks in sorted(unique)]


def build_candidates(
    signatures: List[Signature],
) -> Dict[int, List[Signature]]:
    """
    Index signatures by the first empty cell they can cover on relative
    diagonal 0.

    A normalized signature must contain at least one cell on diagonal 0.
    """
    candidates: Dict[int, List[Signature]] = defaultdict(list)

    for sig in signatures:
        mask0 = sig.masks[0]

        if mask0 == 0:
            continue

        bits = mask0
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
    OR the signature into the frontier if it does not overlap.
    """
    masks = unpack_masks(state)
    new_masks = masks[:]

    for i, add_mask in enumerate(sig.masks):
        if new_masks[i] & add_mask:
            return None
        new_masks[i] |= add_mask

    return pack_masks(new_masks)


def report(
    stats: Stats,
    queue_len: int,
    states_len: int,
) -> None:
    now = time.perf_counter()

    if now - stats.last_report < 2.0:
        return

    delta = stats.processed - stats.last_processed
    elapsed = now - stats.last_report

    rate = delta / elapsed if elapsed > 0 else 0.0

    stats.last_report = now
    stats.last_processed = stats.processed
    stats.max_queue = max(stats.max_queue, queue_len)
    stats.max_states = max(stats.max_states, states_len)

    print(
        f"[progress] "
        f"processed={stats.processed:,} "
        f"states={states_len:,} "
        f"queue={queue_len:,} "
        f"generated={stats.generated:,} "
        f"accepted={stats.accepted:,} "
        f"duplicate={stats.duplicate:,} "
        f"shifts={stats.shifts:,} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


def rss_mb() -> float:
    """
    Linux process resident set size.
    """
    import resource

    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def discover(
    signatures: List[Signature],
    candidates: Dict[int, List[Signature]],
    max_states: int,
) -> Stats:
    stats = Stats()

    start_state = 0

    # A regular BFS gives us a real transition graph.
    queue: List[int] = [start_state]
    head = 0

    seen: set[int] = {start_state}

    print(
        f"Initial state: 0x{start_state:x}",
        flush=True,
    )

    while head < len(queue):
        state = queue[head]
        head += 1

        stats.processed += 1

        if len(seen) > max_states:
            print(
                f"[limit] reached max_states={max_states:,}",
                flush=True,
            )
            break

        masks = unpack_masks(state)

        # A completed current plane advances the frontier.
        if masks[0] == PLANE_MASK:
            shifted = shift_state(state)

            stats.shifts += 1

            if shifted not in seen:
                seen.add(shifted)
                queue.append(shifted)
            else:
                stats.duplicate += 1

            report(stats, len(queue) - head, len(seen))
            continue

        bit = first_empty_bit(masks[0])

        if bit < 0:
            # Defensive; should have been handled by the full-plane case.
            report(stats, len(queue) - head, len(seen))
            continue

        for sig in candidates.get(bit, ()):
            stats.generated += 1

            new_state = apply_signature(
                state,
                sig,
            )

            if new_state is None:
                continue

            stats.accepted += 1

            if new_state in seen:
                stats.duplicate += 1
                continue

            seen.add(new_state)
            queue.append(new_state)

        report(stats, len(queue) - head, len(seen))

    stats.max_queue = max(stats.max_queue, len(queue) - head)
    stats.max_states = len(seen)

    elapsed = 0.0
    if stats.last_report:
        elapsed = time.perf_counter() - stats.last_report

    print(
        f"[final] states={len(seen):,} "
        f"processed={stats.processed:,} "
        f"queue_remaining={len(queue)-head:,} "
        f"generated={stats.generated:,} "
        f"accepted={stats.accepted:,} "
        f"duplicate={stats.duplicate:,} "
        f"shifts={stats.shifts:,} "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Discover the interior frontier automaton "
            "for S in a 4x8 prism."
        )
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=5_000_000,
        help="hard memory-safety cap",
    )
    args = parser.parse_args()

    print(
        "Generating normalized S interior signatures...",
        flush=True,
    )

    start = time.perf_counter()
    signatures = build_signatures()
    gen_time = time.perf_counter() - start

    print(
        f"Unique normalized signatures: {len(signatures)}",
        flush=True,
    )
    print(
        f"Signature generation: {gen_time:.3f} s",
        flush=True,
    )

    candidates = build_candidates(signatures)

    candidate_counts = sorted(
        (bit, len(sigs))
        for bit, sigs in candidates.items()
    )

    print(
        f"Candidate cell classes: {len(candidate_counts)}",
        flush=True,
    )

    for bit, count in candidate_counts:
        x = bit % X_SIZE
        y = bit // X_SIZE
        print(
            f"  bit={bit:2d} ({x},{y}) -> {count} signatures",
            flush=True,
        )

    print(
        f"Starting BFS, max_states={args.max_states:,}...",
        flush=True,
    )
    search_start = time.perf_counter()

    discover(
        signatures,
        candidates,
        args.max_states,
    )

    print(
        f"Total elapsed: "
        f"{time.perf_counter() - search_start:.3f} s",
        flush=True,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
