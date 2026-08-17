#!/usr/bin/env python3
"""
Corrected ragged-frontier prototype for the S pentacube in a 4x8 prism.

Key correction:
A placement covering the current unresolved cell does NOT have to begin on
the current diagonal. Its target cell may lie on relative diagonal 0..4
inside the normalized placement.

We therefore index each normalized placement signature by:
    (target_xy_bit, target_relative_diagonal)

and translate the signature so that the target cell is on frontier diagonal 0.

The state is:
    cursor + five 32-bit occupancy masks.

Absolute diagonal/z is intentionally absent from the interior state.
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

# Current + four future diagonal planes.
SPAN = 4
WORDS = SPAN + 1

CURSOR_BITS = 8
MASK_SHIFT = CURSOR_BITS


@dataclass(frozen=True)
class Signature:
    # masks[0] is the placement's minimum diagonal.
    masks: Tuple[int, ...]


@dataclass(frozen=True)
class Candidate:
    # Placement translated so that its target cell is on diagonal 0.
    packed: int
    target_bit: int
    target_rel_diag: int


@dataclass
class Stats:
    calls: int = 0
    memo_hits: int = 0
    tried: int = 0
    accepted: int = 0
    cursor_advances: int = 0
    plane_advances: int = 0
    last_report_time: float = 0.0
    last_report_calls: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def pack_masks(masks: Sequence[int]) -> int:
    packed = 0
    shift = MASK_SHIFT

    for mask in masks:
        packed |= mask << shift
        shift += PLANE_BITS

    return packed


def pack_state(cursor: int, masks: Sequence[int]) -> int:
    return cursor | pack_masks(masks)


def unpack_state(state: int) -> Tuple[int, List[int]]:
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


def shift_signature_to_target(
    sig: Signature,
    target_rel_diag: int,
) -> Tuple[int, ...] | None:
    """
    Translate a normalized signature so that target_rel_diag becomes
    frontier diagonal 0.

    The translated placement must still fit entirely in the five-plane
    frontier.
    """
    shifted = [0] * WORDS

    for src_diag, mask in enumerate(sig.masks):
        dst_diag = src_diag - target_rel_diag

        if mask == 0:
            continue

        if dst_diag < 0 or dst_diag >= WORDS:
            return None

        shifted[dst_diag] |= mask

    return tuple(shifted)


def signature_from_placement(
    placement: Sequence[Tuple[int, int, int]],
) -> Signature:
    encoded = [
        (x + y + z, x + X_SIZE * y)
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
) -> Dict[int, List[Candidate]]:
    """
    For every target cell in the current diagonal, generate candidates
    for every relative diagonal on which that cell could occur.

    This is the crucial correction over the previous prototype.
    """
    result: Dict[int, List[Candidate]] = {
        bit: []
        for bit in range(PLANE_BITS)
    }

    seen: set[Tuple[int, int, int]] = set()

    for sig in signatures:
        for rel_diag, mask in enumerate(sig.masks):
            bits = mask

            while bits:
                low = bits & -bits
                target_bit = low.bit_length() - 1
                bits ^= low

                shifted = shift_signature_to_target(
                    sig,
                    rel_diag,
                )

                if shifted is None:
                    continue

                packed = pack_masks(shifted)

                key = (
                    target_bit,
                    rel_diag,
                    packed,
                )

                if key in seen:
                    continue

                seen.add(key)

                result[target_bit].append(
                    Candidate(
                        packed=packed,
                        target_bit=target_bit,
                        target_rel_diag=rel_diag,
                    )
                )

    return result


def first_unresolved(
    cursor: int,
    current_mask: int,
    order: Sequence[int],
) -> int | None:
    for i in range(cursor, len(order)):
        bit = order[i]

        if not (current_mask & (1 << bit)):
            return bit

    return None


def build_order() -> List[int]:
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


def normalize(
    cursor: int,
    masks: List[int],
    stats: Stats,
) -> Tuple[int, List[int]]:
    """
    Advance the ragged cursor through occupied cells.

    When the cursor reaches the end of the current diagonal, the diagonal
    is retired and the frontier shifts by one.
    """
    while True:
        bit = first_unresolved(
            cursor,
            masks[0],
            ORDER,
        )

        if bit is not None:
            return cursor, masks

        masks.pop(0)
        masks.append(0)
        cursor = 0
        stats.plane_advances += 1


def report(
    stats: Stats,
    memo: set[int],
    cursor: int,
) -> None:
    now = time.perf_counter()

    if now - stats.last_report_time < 2.0:
        return

    delta = (
        stats.calls -
        stats.last_report_calls
    )

    dt = (
        now -
        stats.last_report_time
    )

    rate = delta / dt if dt > 0 else 0.0

    stats.last_report_time = now
    stats.last_report_calls = stats.calls

    print(
        f"[progress] "
        f"cursor={cursor:2d} "
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
        candidates: Dict[int, List[Candidate]],
        max_states: int,
    ) -> None:
        self.candidates = candidates
        self.max_states = max_states

        self.memo: set[int] = set()
        self.stats = Stats()

    def run(self) -> None:
        start = time.perf_counter()

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

            normalized = pack_state(
                cursor,
                masks,
            )

            if normalized != state:
                if normalized in self.memo:
                    self.stats.memo_hits += 1
                else:
                    self.memo.add(normalized)
                    stack.append(normalized)

                report(
                    self.stats,
                    self.memo,
                    cursor,
                )
                continue

            missing = first_unresolved(
                cursor,
                masks[0],
                ORDER,
            )

            if missing is None:
                continue

            for candidate in self.candidates.get(
                missing,
                (),
            ):
                self.stats.tried += 1

                occupancy_mask = (
                    ((1 << (WORDS * PLANE_BITS)) - 1)
                    << MASK_SHIFT
                )

                if (
                    state &
                    occupancy_mask &
                    candidate.packed
                ):
                    continue

                self.stats.accepted += 1

                next_state = (
                    state |
                    candidate.packed
                )

                next_cursor = cursor

                # The target cell is guaranteed occupied by the candidate.
                # Advance over consecutive occupied cells in the current
                # plane, preserving the ragged boundary.
                while next_cursor < len(ORDER):
                    bit = ORDER[next_cursor]

                    if not (
                        (
                            next_state >>
                            MASK_SHIFT
                        ) &
                        (1 << bit)
                    ):
                        break

                    next_cursor += 1
                    self.stats.cursor_advances += 1

                candidate_cursor, candidate_masks = unpack_state(
                    next_state
                )

                candidate_cursor = next_cursor

                candidate_cursor, candidate_masks = normalize(
                    candidate_cursor,
                    candidate_masks,
                    self.stats,
                )

                canonical = pack_state(
                    candidate_cursor,
                    candidate_masks,
                )

                if canonical in self.memo:
                    self.stats.memo_hits += 1
                    continue

                self.memo.add(canonical)
                stack.append(canonical)

            report(
                self.stats,
                self.memo,
                cursor,
            )

        elapsed = time.perf_counter() - start

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

    candidates = build_candidates(
        signatures
    )

    total_candidates = sum(
        len(values)
        for values in candidates.values()
    )

    print(
        f"Candidate entries: "
        f"{total_candidates:,}",
        flush=True,
    )

    print(
        "Starting corrected ragged-frontier exploration...",
        flush=True,
    )

    automaton = RaggedAutomaton(
        candidates,
        args.max_states,
    )

    automaton.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
