#!/usr/bin/env python3
"""
Ragged-frontier / diagonal-sweep prototype for the S pentacube
in the interior of a 4x8 prism.

This is the next experiment after the whole-plane frontier model.

The processed/unprocessed boundary is RAGGED:
  * cells are ordered by diagonal d = x+y+z
  * within a diagonal, cells are ordered by x+y/x/y order
  * we advance the cursor cell-by-cell
  * a placement may extend into later diagonals, but may not touch
    an already-processed cell

The absolute diagonal number is deliberately NOT part of the state.
We are modelling the translationally invariant interior, not a finite
4x8xN boundary.

State:
    cursor = position of the next unresolved cell
    masks[0..4] = occupancy in the current + next four diagonals

The current diagonal's mask may already contain cells beyond the cursor:
those are the "ragged" part of the frontier.

This is exploratory only; it is not yet a finite-box solver.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
PLANE_BITS = X_SIZE * Y_SIZE
PLANE_MASK = (1 << PLANE_BITS) - 1
SPAN = 4
WORDS = SPAN + 1


@dataclass(frozen=True)
class Signature:
    masks: Tuple[int, ...]


@dataclass
class Stats:
    calls: int = 0
    memo_hits: int = 0
    tried: int = 0
    accepted: int = 0
    advances: int = 0
    max_queue: int = 0
    last_report_time: float = 0.0
    last_report_calls: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def pack_state(cursor: int, masks: Sequence[int]) -> int:
    """
    Pack cursor plus five 32-bit masks into one Python integer.
    """
    state = cursor

    shift = 8
    for mask in masks:
        state |= mask << shift
        shift += PLANE_BITS

    return state


def unpack_state(state: int) -> Tuple[int, List[int]]:
    cursor = state & 0xFF
    masks = []

    shift = 8
    for _ in range(WORDS):
        masks.append(
            (state >> shift) & PLANE_MASK
        )
        shift += PLANE_BITS

    return cursor, masks


def bit_for_xy(x: int, y: int) -> int:
    return 1 << (x + X_SIZE * y)


def xy_from_bit_index(index: int) -> Tuple[int, int]:
    return index % X_SIZE, index // X_SIZE


def diagonal_order() -> List[int]:
    """
    Return the 32 xy-bit indices in a deterministic order.

    We use increasing x+y, then x, then y.  Any fixed ordering would
    work for the automaton experiment; this one is easy to inspect.
    """
    cells = []

    for s in range((X_SIZE - 1) + (Y_SIZE - 1) + 1):
        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                if x + y == s:
                    cells.append(
                        x + X_SIZE * y
                    )

    return cells


ORDER = diagonal_order()
ORDER_INDEX = {
    bit_index: i
    for i, bit_index in enumerate(ORDER)
}


def first_unresolved(cursor: int, mask: int) -> int | None:
    """
    Return the bit index of the next cell in ORDER from cursor that
    is not occupied.  Returns None when everything from cursor onward
    is occupied.

    In a valid state, earlier positions should already be resolved.
    """
    for i in range(cursor, len(ORDER)):
        bit_index = ORDER[i]
        if not (mask & (1 << bit_index)):
            return bit_index

    return None


def signature_from_placement(
    placement: Sequence[Tuple[int, int, int]]
) -> Signature:
    encoded = [
        (x + y + z, x + X_SIZE * y)
        for x, y, z in placement
    ]

    min_d = min(d for d, _ in encoded)
    max_d = max(d for d, _ in encoded)

    if max_d - min_d > SPAN:
        raise ValueError(
            "Placement exceeds supported diagonal span"
        )

    masks = [0] * WORDS

    for d, bit in encoded:
        rel = d - min_d
        masks[rel] |= 1 << bit

    return Signature(tuple(masks))


def build_signatures() -> List[Signature]:
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    unique = {
        signature_from_placement(p).masks
        for p in placements.values()
    }

    return [
        Signature(m)
        for m in sorted(unique)
    ]


def build_candidates(
    signatures: Sequence[Signature],
) -> Dict[int, List[Signature]]:
    """
    Candidate placements indexed by every xy bit that they occupy on
    relative diagonal 0.

    A normalized signature can cover several cells on diagonal 0,
    and may therefore appear under several candidate bits.
    """
    result: Dict[int, List[Signature]] = {
        bit_index: []
        for bit_index in ORDER
    }

    for sig in signatures:
        bits = sig.masks[0]

        while bits:
            low = bits & -bits
            bit_index = low.bit_length() - 1
            bits ^= low

            if bit_index in result:
                result[bit_index].append(sig)

    return result


def apply_signature(
    masks: List[int],
    sig: Signature,
) -> bool:
    """
    OR signature into the current frontier if it has no collision.

    Returns True if applied.
    """
    for i, add_mask in enumerate(sig.masks):
        if masks[i] & add_mask:
            return False

    for i, add_mask in enumerate(sig.masks):
        masks[i] |= add_mask

    return True


def normalize_advance(
    cursor: int,
    masks: List[int],
) -> Tuple[int, List[int], int]:
    """
    Advance the ragged cursor over already-occupied cells.

    When the current diagonal is exhausted, shift the frontier by one
    diagonal and reset the cursor to zero.

    Returns:
        new cursor
        new masks
        number of cell/plane advances performed
    """
    advances = 0

    while True:
        next_bit = first_unresolved(
            cursor,
            masks[0]
        )

        if next_bit is not None:
            return cursor, masks, advances

        # Entire current diagonal is resolved.
        masks.pop(0)
        masks.append(0)
        cursor = 0

        advances += 1


def report(
    stats: Stats,
    memo: set[int],
    d: int,
) -> None:
    now = time.perf_counter()

    if now - stats.last_report_time < 2.0:
        return

    delta = stats.calls - stats.last_report_calls
    dt = now - stats.last_report_time

    rate = delta / dt if dt > 0 else 0.0

    stats.last_report_time = now
    stats.last_report_calls = stats.calls

    print(
        f"[progress] "
        f"cursor={d:2d} "
        f"calls={stats.calls:,} "
        f"memo={len(memo):,} "
        f"memo_hits={stats.memo_hits:,} "
        f"try={stats.tried:,} "
        f"accept={stats.accepted:,} "
        f"advances={stats.advances:,} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


class RaggedAutomaton:
    def __init__(
        self,
        signatures: Sequence[Signature],
        candidates: Dict[int, List[Signature]],
        max_states: int,
    ) -> None:
        self.signatures = signatures
        self.candidates = candidates
        self.max_states = max_states

        self.memo: set[int] = set()
        self.stats = Stats()

        # Starting state: nothing occupied, cursor at first cell.
        self.start_state = pack_state(
            0,
            [0] * WORDS,
        )

    def run(self) -> bool:
        """
        Explore until a state repeats or the state cap is reached.

        For the interior automaton experiment, reaching a repeated state is
        not a success/failure proof yet; it means we've found a cycle in the
        transition graph.
        """
        stack = [self.start_state]
        self.memo.add(self.start_state)

        start = time.perf_counter()
        self.stats.last_report_time = start

        while stack:
            if len(self.memo) >= self.max_states:
                print(
                    f"[limit] memo reached "
                    f"{self.max_states:,} states",
                    flush=True,
                )
                return False

            state = stack.pop()

            self.stats.calls += 1

            cursor, masks = unpack_state(state)

            cursor, masks, advances = normalize_advance(
                cursor,
                masks,
            )

            self.stats.advances += advances

            if advances:
                normalized = pack_state(
                    cursor,
                    masks,
                )

                if normalized not in self.memo:
                    self.memo.add(normalized)
                    stack.append(normalized)
                else:
                    self.stats.memo_hits += 1

                report(
                    self.stats,
                    self.memo,
                    cursor,
                )
                continue

            bit_index = first_unresolved(
                cursor,
                masks[0],
            )

            if bit_index is None:
                # Defensive; normalize_advance should have shifted.
                continue

            for sig in self.candidates.get(
                bit_index,
                (),
            ):
                self.stats.tried += 1

                new_masks = masks[:]

                if not apply_signature(
                    new_masks,
                    sig,
                ):
                    continue

                self.stats.accepted += 1

                # The cursor cell is now occupied. Advance over any
                # consecutive occupied cells.
                next_cursor = cursor

                while next_cursor < len(ORDER):
                    b = ORDER[next_cursor]

                    if not (
                        new_masks[0]
                        & (1 << b)
                    ):
                        break

                    next_cursor += 1

                new_cursor, new_masks, extra = normalize_advance(
                    next_cursor,
                    new_masks,
                )

                self.stats.advances += extra

                new_state = pack_state(
                    new_cursor,
                    new_masks,
                )

                if new_state in self.memo:
                    self.stats.memo_hits += 1
                    continue

                self.memo.add(new_state)
                stack.append(new_state)

            report(
                self.stats,
                self.memo,
                cursor,
            )

        elapsed = time.perf_counter() - start

        print()
        print(
            f"Interior ragged states: "
            f"{len(self.memo):,}"
        )
        print(
            f"Calls: {self.stats.calls:,}"
        )
        print(
            f"Memo hits: {self.stats.memo_hits:,}"
        )
        print(
            f"Placements tried: "
            f"{self.stats.tried:,}"
        )
        print(
            f"Placements accepted: "
            f"{self.stats.accepted:,}"
        )
        print(
            f"Cursor/plane advances: "
            f"{self.stats.advances:,}"
        )
        print(
            f"Elapsed: {elapsed:.3f} s"
        )
        print(
            f"Peak RSS: {rss_mb():,.0f} MB"
        )

        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ragged diagonal-frontier automaton "
            "prototype for S in 4x8."
        )
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=5_000_000,
    )
    args = parser.parse_args()

    print(
        "Generating normalized S signatures...",
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

    print(
        f"Diagonal cell order has {len(ORDER)} cells:",
        flush=True,
    )

    for i, bit_index in enumerate(ORDER):
        x, y = xy_from_bit_index(bit_index)
        print(
            f"  {i:2d}: ({x},{y})",
            flush=True,
        )

    candidates = build_candidates(signatures)

    print(
        "Candidate counts for first-cell positions:",
        flush=True,
    )

    for bit_index in ORDER:
        x, y = xy_from_bit_index(bit_index)
        print(
            f"  ({x},{y}): "
            f"{len(candidates[bit_index])}",
            flush=True,
        )

    automaton = RaggedAutomaton(
        signatures,
        candidates,
        args.max_states,
    )

    print(
        f"Starting ragged-frontier exploration "
        f"(limit={args.max_states:,})...",
        flush=True,
    )

    automaton.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
