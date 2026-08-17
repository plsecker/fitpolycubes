#!/usr/bin/env python3
"""
Ragged diagonal-frontier automaton prototype for S in a 4x8 prism.

The state is:
    cursor + five 32-bit diagonal occupancy masks.

Absolute diagonal/z is NOT stored: this is intended to model the
translation-invariant interior.

Important implementation detail:
    state packing and signature packing use the same bit offset, so overlap
    tests compare corresponding frontier diagonals.
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

CURSOR_BITS = 8
MASK_SHIFT = CURSOR_BITS
TOTAL_STATE_BITS = MASK_SHIFT + WORDS * PLANE_BITS


@dataclass(frozen=True)
class Signature:
    # masks[0] is the placement's minimum diagonal.
    masks: Tuple[int, ...]


@dataclass
class Stats:
    calls: int = 0
    memo_hits: int = 0
    tried: int = 0
    accepted: int = 0
    plane_advances: int = 0
    cursor_advances: int = 0
    last_report_time: float = 0.0
    last_report_calls: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def pack_state(
    cursor: int,
    masks: Sequence[int],
) -> int:
    state = cursor

    shift = MASK_SHIFT

    for mask in masks:
        state |= mask << shift
        shift += PLANE_BITS

    return state


def unpack_state(
    state: int,
) -> Tuple[int, List[int]]:
    cursor_mask = (1 << CURSOR_BITS) - 1
    cursor = state & cursor_mask

    masks = []
    shift = MASK_SHIFT

    for _ in range(WORDS):
        masks.append(
            (state >> shift) & PLANE_MASK
        )
        shift += PLANE_BITS

    return cursor, masks


def pack_signature(
    sig: Signature,
) -> int:
    """
    Pack a placement signature using exactly the same mask offset as a state.
    """
    packed = 0
    shift = MASK_SHIFT

    for mask in sig.masks:
        packed |= mask << shift
        shift += PLANE_BITS

    return packed


def first_unresolved(
    cursor: int,
    mask: int,
    order: Sequence[int],
) -> int | None:
    for i in range(cursor, len(order)):
        bit = order[i]

        if not (mask & (1 << bit)):
            return bit

    return None


def build_order() -> List[int]:
    """
    Deterministic order within the 4x8 diagonal cross-section:
    increasing x+y, then x, then y.
    """
    order: List[int] = []

    for xy_sum in range(
        (X_SIZE - 1) + (Y_SIZE - 1) + 1
    ):
        for x in range(X_SIZE):
            for y in range(Y_SIZE):
                if x + y == xy_sum:
                    order.append(
                        x + X_SIZE * y
                    )

    return order


ORDER = build_order()


def signature_from_placement(
    placement: Sequence[Tuple[int, int, int]],
) -> Signature:
    encoded = [
        (
            x + y + z,
            x + X_SIZE * y,
        )
        for x, y, z in placement
    ]

    min_d = min(d for d, _ in encoded)
    max_d = max(d for d, _ in encoded)

    if max_d - min_d > SPAN:
        raise ValueError(
            "S placement exceeds supported diagonal span"
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
        Signature(masks)
        for masks in sorted(unique)
    ]


def build_candidates(
    signatures: Sequence[Signature],
) -> Dict[int, List[Tuple[Signature, int]]]:
    """
    Index signatures by cells they occupy on relative diagonal 0.

    Each candidate includes its packed representation for fast overlap.
    """
    result: Dict[int, List[Tuple[Signature, int]]] = {
        bit: []
        for bit in ORDER
    }

    for sig in signatures:
        bits = sig.masks[0]
        packed = pack_signature(sig)

        while bits:
            low = bits & -bits
            bit = low.bit_length() - 1
            bits ^= low

            if bit in result:
                result[bit].append(
                    (sig, packed)
                )

    return result


def apply_signature(
    state: int,
    packed_signature: int,
) -> int | None:
    """
    Fast frontier collision check.

    Both values use the same 8-bit cursor prefix followed by the five
    32-bit frontier masks.
    """
    # Ignore the cursor bits in the state for occupancy comparison.
    occupancy_mask = (
        ((1 << WORDS * PLANE_BITS) - 1)
        << MASK_SHIFT
    )

    if (state & occupancy_mask & packed_signature) != 0:
        return None

    return state | packed_signature


def normalize(
    cursor: int,
    masks: List[int],
    stats: Stats,
) -> Tuple[int, List[int]]:
    """
    Advance over all consecutive occupied cells in the current diagonal.
    When the whole diagonal is resolved, shift the frontier.
    """
    while True:
        next_bit = first_unresolved(
            cursor,
            masks[0],
            ORDER,
        )

        if next_bit is not None:
            return cursor, masks

        # Current diagonal has no unresolved cells from cursor onward:
        # it is completely resolved.
        masks.pop(0)
        masks.append(0)

        cursor = 0
        stats.plane_advances += 1


def report(
    stats: Stats,
    memo: set[int],
    current_cursor: int,
) -> None:
    now = time.perf_counter()

    if (
        now - stats.last_report_time < 2.0
    ):
        return

    delta_calls = (
        stats.calls -
        stats.last_report_calls
    )

    dt = (
        now - stats.last_report_time
    )

    rate = (
        delta_calls / dt
        if dt > 0
        else 0.0
    )

    stats.last_report_time = now
    stats.last_report_calls = stats.calls

    print(
        f"[progress] "
        f"cursor={current_cursor:2d} "
        f"calls={stats.calls:,} "
        f"memo={len(memo):,} "
        f"memo_hits={stats.memo_hits:,} "
        f"try={stats.tried:,} "
        f"accept={stats.accepted:,} "
        f"cursor_adv={stats.cursor_advances:,} "
        f"plane_adv={stats.plane_advances:,} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


class RaggedAutomaton:
    def __init__(
        self,
        signatures: Sequence[Signature],
        candidates: Dict[int, List[Tuple[Signature, int]]],
        max_states: int,
    ) -> None:
        self.signatures = signatures
        self.candidates = candidates
        self.max_states = max_states

        self.memo: set[int] = set()
        self.stats = Stats()

    def run(self) -> None:
        start = time.perf_counter()

        # Empty initial interior frontier.
        start_state = pack_state(
            0,
            [0] * WORDS,
        )

        stack = [start_state]
        self.memo.add(start_state)

        self.stats.last_report_time = start

        while stack:
            if len(self.memo) >= self.max_states:
                print(
                    f"[limit] reached "
                    f"{self.max_states:,} states",
                    flush=True,
                )
                break

            state = stack.pop()

            self.stats.calls += 1

            cursor, masks = unpack_state(state)

            cursor, masks = normalize(
                cursor,
                masks,
                self.stats,
            )

            normalized_state = pack_state(
                cursor,
                masks,
            )

            if normalized_state != state:
                if normalized_state in self.memo:
                    self.stats.memo_hits += 1
                    report(
                        self.stats,
                        self.memo,
                        cursor,
                    )
                    continue

                self.memo.add(normalized_state)
                stack.append(normalized_state)

                report(
                    self.stats,
                    self.memo,
                    cursor,
                )
                continue

            missing_bit = first_unresolved(
                cursor,
                masks[0],
                ORDER,
            )

            if missing_bit is None:
                # normalize() should have consumed a complete plane.
                continue

            for sig, packed_sig in self.candidates.get(
                missing_bit,
                ()
            ):
                self.stats.tried += 1

                next_state = apply_signature(
                    state,
                    packed_sig,
                )

                if next_state is None:
                    continue

                self.stats.accepted += 1

                new_cursor = cursor

                # The selected cell is now covered. Advance through
                # consecutive occupied cells on the current diagonal.
                while (
                    new_cursor < len(ORDER)
                ):
                    bit = ORDER[new_cursor]

                    if not (
                        masks[0] &
                        (1 << bit)
                    ):
                        break

                    new_cursor += 1
                    self.stats.cursor_advances += 1

                # Pack candidate occupancy, with the new cursor.
                candidate_cursor, candidate_masks = unpack_state(
                    next_state
                )
                candidate_cursor = new_cursor

                candidate_cursor, candidate_masks = normalize(
                    candidate_cursor,
                    candidate_masks,
                    self.stats,
                )

                canonical_next = pack_state(
                    candidate_cursor,
                    candidate_masks,
                )

                if canonical_next in self.memo:
                    self.stats.memo_hits += 1
                    continue

                self.memo.add(canonical_next)
                stack.append(canonical_next)

            report(
                self.stats,
                self.memo,
                cursor,
            )

        elapsed = (
            time.perf_counter() - start
        )

        print()
        print(
            f"States: {len(self.memo):,}"
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
            f"Cursor advances: "
            f"{self.stats.cursor_advances:,}"
        )
        print(
            f"Plane advances: "
            f"{self.stats.plane_advances:,}"
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
    )
    args = parser.parse_args()

    print(
        "Generating normalized S signatures...",
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

    print(
        f"Diagonal order: "
        f"{len(ORDER)} cells",
        flush=True,
    )

    candidates = build_candidates(
        signatures
    )

    automaton = RaggedAutomaton(
        signatures,
        candidates,
        args.max_states,
    )

    print(
        f"Starting corrected ragged exploration "
        f"(limit={args.max_states:,})...",
        flush=True,
    )

    automaton.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
