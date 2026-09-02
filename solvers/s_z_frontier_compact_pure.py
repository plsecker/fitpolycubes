#!/usr/bin/env python3
"""
Pure-Python compact z-frontier explorer for S in 4x8.

Purpose:
    Short-term robust implementation of the validated Frontier state model.

Differences from the Numba versions:
    * Python controls the search loop.
    * NumPy arrays hold the discovered 96-bit states compactly.
    * NumPy array holds an exact open-addressed hash table of state indices.
    * No Numba.
    * No np.memmap in the live search path.
    * Checkpoints store only the discovered state prefix, plus the full hash
      table, so checkpoint disk usage tracks the actual search size rather
      than the configured state capacity.

The mathematical transition model is the same as s_z_frontier_packed.py.
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
NCELLS = X_SIZE * Y_SIZE
WORD_MASK = (1 << NCELLS) - 1
EMPTY_INDEX = np.uint32(0xFFFFFFFF)


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def cell_id(x: int, y: int) -> int:
    return x + X_SIZE * y


def first_empty(mask: int) -> int:
    missing = WORD_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def make_shifted_template(
    placement_cells: Sequence[Tuple[int, int, int]],
    target_z: int,
) -> int | None:
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * 3
    target_rel = target_z - min_z

    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        if rel < 0 or rel >= 3:
            return None
        shifted_masks[rel] |= 1 << cell_id(x, y)

    return (
        shifted_masks[0]
        | (shifted_masks[1] << 32)
        | (shifted_masks[2] << 64)
    )


def build_templates():
    raw, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )

    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}

    concrete_count = len(raw)

    for placement in raw.values():
        cells = tuple(placement)
        for x, y, z in cells:
            target = cell_id(x, y)
            packed = make_shifted_template(cells, z)
            if packed is None:
                continue
            if packed in seen[target]:
                continue
            seen[target].add(packed)
            result[target].append(packed)

    flat_lo: List[int] = []
    flat_hi: List[int] = []
    offsets = [0]

    for cell in range(NCELLS):
        for template in result[cell]:
            flat_lo.append(template & ((1 << 64) - 1))
            flat_hi.append((template >> 64) & 0xFFFFFFFF)
        offsets.append(len(flat_lo))

    return (
        np.asarray(flat_lo, dtype=np.uint64),
        np.asarray(flat_hi, dtype=np.uint32),
        np.asarray(offsets, dtype=np.int32),
        concrete_count,
        sum(len(v) for v in result.values()),
    )


def mix_hash(lo: int, hi: int) -> int:
    # Same conceptual 64-bit mixing used by the compact implementation.
    x = (lo ^ ((hi & 0xFFFFFFFF) * 0x9E3779B185EBCA87)) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 30
    x = (x * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 27
    x = (x * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 31
    return x & 0xFFFFFFFFFFFFFFFF


def hash_lookup_or_insert(
    lo: int,
    hi: int,
    new_index: int,
    state_lo: np.ndarray,
    state_hi: np.ndarray,
    table: np.ndarray,
) -> int:
    mask = len(table) - 1
    slot = mix_hash(lo, hi) & mask

    while True:
        idx = int(table[slot])
        if idx == 0xFFFFFFFF:
            table[slot] = np.uint32(new_index)
            return -1

        if int(state_lo[idx]) == lo and int(state_hi[idx]) == hi:
            return idx

        slot = (slot + 1) & mask


def allocate_storage(state_capacity: int, hash_capacity: int):
    state_lo = np.empty(state_capacity, dtype=np.uint64)
    state_hi = np.empty(state_capacity, dtype=np.uint32)
    table = np.full(hash_capacity, EMPTY_INDEX, dtype=np.uint32)

    state_lo[0] = 0
    state_hi[0] = 0
    table[0] = np.uint32(0)

    return state_lo, state_hi, table


def checkpoint_arrays(
    checkpoint_dir: Path,
    state_lo: np.ndarray,
    state_hi: np.ndarray,
    table: np.ndarray,
    count: int,
):
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Store only the discovered prefix of the state arrays. The remaining
    # capacity is unused and need not consume checkpoint disk space.
    #
    # These files are rewritten in place to avoid requiring another full copy
    # of the checkpoint on a nearly-full filesystem. Metadata is written last,
    # so a successful metadata write means the files correspond to that state
    # count.
    lo_path = checkpoint_dir / "states_lo.u64"
    hi_path = checkpoint_dir / "states_hi.u32"
    hash_path = checkpoint_dir / "seen_index.u32"

    with open(lo_path, "wb") as f:
        state_lo[:count].tofile(f)

    with open(hi_path, "wb") as f:
        state_hi[:count].tofile(f)

    with open(hash_path, "wb") as f:
        table.tofile(f)


def save_metadata(
    checkpoint_dir: Path,
    *,
    capacity: int,
    hash_capacity: int,
    count: int,
    processed: int,
    generated: int,
    accepted: int,
    duplicates: int,
    shifts: int,
    branching: int,
    max_degree: int,
    elapsed: float,
):
    metadata = {
        "version": 3,
        "capacity": capacity,
        "hash_capacity": hash_capacity,
        "states": count,
        "processed": processed,
        "generated": generated,
        "accepted": accepted,
        "duplicates": duplicates,
        "shifts": shifts,
        "branching": branching,
        "max_degree": max_degree,
        "elapsed": elapsed,
    }

    tmp = checkpoint_dir / "metadata.json.tmp"
    tmp.write_text(json.dumps(metadata, indent=2) + "\n")
    os.replace(tmp, checkpoint_dir / "metadata.json")


def load_checkpoint(checkpoint_dir: Path):
    meta = json.loads((checkpoint_dir / "metadata.json").read_text())
    capacity = int(meta["capacity"])
    hash_capacity = int(meta["hash_capacity"])
    count = int(meta["states"])

    stored_lo = np.fromfile(
        checkpoint_dir / "states_lo.u64",
        dtype=np.uint64,
    )
    stored_hi = np.fromfile(
        checkpoint_dir / "states_hi.u32",
        dtype=np.uint32,
    )
    table = np.fromfile(
        checkpoint_dir / "seen_index.u32",
        dtype=np.uint32,
    )

    if len(stored_lo) < count or len(stored_lo) > capacity:
        raise RuntimeError(
            f"Unexpected states_lo length {len(stored_lo)}; "
            f"expected between {count} and {capacity}."
        )
    if len(stored_hi) < count or len(stored_hi) > capacity:
        raise RuntimeError(
            f"Unexpected states_hi length {len(stored_hi)}; "
            f"expected between {count} and {capacity}."
        )
    if len(table) != hash_capacity:
        raise RuntimeError("Hash checkpoint size does not match metadata")

    # Always restore capacity-sized live arrays for the search.
    state_lo = np.empty(capacity, dtype=np.uint64)
    state_hi = np.empty(capacity, dtype=np.uint32)
    state_lo[:count] = stored_lo[:count]
    state_hi[:count] = stored_hi[:count]

    return meta, state_lo, state_hi, table


def run(
    *,
    max_states: int,
    exhaustive: bool,
    state_capacity: int,
    hash_capacity: int,
    checkpoint_dir: Path,
    checkpoint_seconds: float,
    report_seconds: float,
    resume: bool,
):
    if hash_capacity <= state_capacity:
        raise ValueError("hash capacity must exceed state capacity")
    if hash_capacity & (hash_capacity - 1):
        raise ValueError("hash capacity must be a power of two")

    if resume:
        meta, state_lo, state_hi, table = load_checkpoint(checkpoint_dir)
        capacity = int(meta["capacity"])
        hash_capacity = int(meta["hash_capacity"])
        count = int(meta["states"])
        processed = int(meta["processed"])
        generated = int(meta["generated"])
        accepted = int(meta["accepted"])
        duplicates = int(meta["duplicates"])
        shifts = int(meta["shifts"])
        branching = int(meta["branching"])
        max_degree = int(meta["max_degree"])

        print(
            f"[resume] states={count:,} queue={count-processed:,} "
            f"processed={processed:,}",
            flush=True,
        )
    else:
        capacity = state_capacity
        count = 1
        processed = 0
        generated = 0
        accepted = 0
        duplicates = 0
        shifts = 0
        branching = 0
        max_degree = 0

        state_lo, state_hi, table = allocate_storage(
            capacity, hash_capacity
        )

    template_lo, template_hi, offsets, concrete_count, total_templates = (
        build_templates()
    )

    print(f"Concrete placements: {concrete_count}", flush=True)
    print(f"Target templates: {total_templates}", flush=True)
    raw_state_gib = capacity * 12 / (1024 ** 3)
    raw_hash_gib = hash_capacity * 4 / (1024 ** 3)
    print(f"State capacity: {capacity:,} ({raw_state_gib:.3f} GiB raw)", flush=True)
    print(
        f"Hash capacity: {hash_capacity:,} ({raw_hash_gib:.3f} GiB raw)",
        flush=True,
    )
    print(
        f"Expected compact storage: {raw_state_gib + raw_hash_gib:.3f} GiB",
        flush=True,
    )

    start_time = time.perf_counter()
    last_report = start_time
    last_checkpoint = start_time
    last_processed = processed

    while processed < count:
        if not exhaustive and count >= max_states:
            print(f"[limit] reached {max_states:,} states", flush=True)
            break

        lo = int(state_lo[processed])
        hi = int(state_hi[processed])
        processed += 1

        current = lo & 0xFFFFFFFF

        if current == WORD_MASK:
            nxt_lo = (lo >> 32) | ((hi & 0xFFFFFFFF) << 32)
            nxt_hi = (hi >> 32) & 0xFFFFFFFF
            shifts += 1

            idx = hash_lookup_or_insert(
                nxt_lo,
                nxt_hi,
                count,
                state_lo,
                state_hi,
                table,
            )
            if idx >= 0:
                duplicates += 1
            else:
                if count >= capacity:
                    raise RuntimeError("state capacity exhausted")
                state_lo[count] = np.uint64(nxt_lo)
                state_hi[count] = np.uint32(nxt_hi)
                count += 1

        else:
            target = first_empty(current)
            start_tpl = int(offsets[target])
            end_tpl = int(offsets[target + 1])

            outgoing = set()

            for j in range(start_tpl, end_tpl):
                generated += 1

                tlo = int(template_lo[j])
                thi = int(template_hi[j])

                if (lo & tlo) or (hi & thi):
                    continue

                accepted += 1
                nxt = lo | tlo | ((hi | thi) << 64)
                outgoing.add(nxt)

            degree = len(outgoing)
            if degree > 1:
                branching += 1
            if degree > max_degree:
                max_degree = degree

            for nxt in outgoing:
                nlo = nxt & ((1 << 64) - 1)
                nhi = (nxt >> 64) & 0xFFFFFFFF

                idx = hash_lookup_or_insert(
                    nlo,
                    nhi,
                    count,
                    state_lo,
                    state_hi,
                    table,
                )
                if idx >= 0:
                    duplicates += 1
                else:
                    if count >= capacity:
                        raise RuntimeError("state capacity exhausted")
                    state_lo[count] = np.uint64(nlo)
                    state_hi[count] = np.uint32(nhi)
                    count += 1

        now = time.perf_counter()

        if now - last_report >= report_seconds:
            dt = now - last_report
            delta = processed - last_processed
            rate = delta / dt if dt > 0 else 0.0
            print(
                f"[progress] states={count:,} "
                f"queue={count-processed:,} "
                f"processed={processed:,} "
                f"generated={generated:,} "
                f"accepted={accepted:,} "
                f"dup={duplicates:,} "
                f"shifts={shifts:,} "
                f"branch={branching:,} "
                f"maxdeg={max_degree} "
                f"rate={rate:,.0f}/s "
                f"rss={rss_mb():,.0f} MB",
                flush=True,
            )
            last_report = now
            last_processed = processed

        if now - last_checkpoint >= checkpoint_seconds:
            checkpoint_arrays(
                checkpoint_dir,
                state_lo,
                state_hi,
                table,
                count,
            )
            save_metadata(
                checkpoint_dir,
                capacity=capacity,
                hash_capacity=hash_capacity,
                count=count,
                processed=processed,
                generated=generated,
                accepted=accepted,
                duplicates=duplicates,
                shifts=shifts,
                branching=branching,
                max_degree=max_degree,
                elapsed=now - start_time,
            )
            print(
                f"[checkpoint] states={count:,} "
                f"queue={count-processed:,} "
                f"processed={processed:,}",
                flush=True,
            )
            last_checkpoint = now

    elapsed = time.perf_counter() - start_time

    checkpoint_arrays(
        checkpoint_dir,
        state_lo,
        state_hi,
        table,
        count,
    )
    save_metadata(
        checkpoint_dir,
        capacity=capacity,
        hash_capacity=hash_capacity,
        count=count,
        processed=processed,
        generated=generated,
        accepted=accepted,
        duplicates=duplicates,
        shifts=shifts,
        branching=branching,
        max_degree=max_degree,
        elapsed=elapsed,
    )

    if processed >= count:
        print("[complete] reachable frontier state space exhausted", flush=True)

    print(f"States: {count:,}")
    print(f"Processed: {processed:,}")
    print(f"Transitions generated: {generated:,}")
    print(f"Transitions accepted: {accepted:,}")
    print(f"Duplicate states: {duplicates:,}")
    print(f"Layer shifts: {shifts:,}")
    print(f"Branching states: {branching:,}")
    print(f"Maximum out-degree: {max_degree}")
    print(f"Queue remaining: {count-processed:,}")
    print(f"Elapsed: {elapsed:.3f} s")
    print(f"Peak RSS: {rss_mb():.0f} MB")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pure-Python compact 4x8 z-frontier explorer for S."
    )
    parser.add_argument("--max-states", type=int, default=10_000_000)
    parser.add_argument("--exhaustive", action="store_true")
    parser.add_argument("--state-capacity", type=int, default=40_000_000)
    parser.add_argument("--hash-capacity", type=int, default=134_217_728)
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default="frontier_compact_pure_checkpoint",
    )
    parser.add_argument("--checkpoint-seconds", type=float, default=60.0)
    parser.add_argument("--report-seconds", type=float, default=5.0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    print("Generating S placement templates...", flush=True)
    build_start = time.perf_counter()

    if args.resume:
        # run() will load checkpoint first, but template construction is still
        # required for the resumed search.
        pass

    run(
        max_states=args.max_states,
        exhaustive=args.exhaustive,
        state_capacity=args.state_capacity,
        hash_capacity=args.hash_capacity,
        checkpoint_dir=Path(args.checkpoint_dir),
        checkpoint_seconds=args.checkpoint_seconds,
        report_seconds=args.report_seconds,
        resume=args.resume,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
