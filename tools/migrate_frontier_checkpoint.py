#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from numba import njit

EMPTY = np.uint32(0xFFFFFFFF)


@njit(cache=True)
def mix_hash(lo, hi):
    x = lo ^ (np.uint64(hi) * np.uint64(0x9E3779B185EBCA87))
    x ^= x >> np.uint64(30)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
    return x


@njit(cache=True)
def rebuild_hash(state_lo, state_hi, count, table):
    mask = np.uint64(len(table) - 1)
    for i in range(count):
        lo = state_lo[i]
        hi = np.uint64(state_hi[i])
        slot = mix_hash(lo, hi) & mask
        while True:
            if table[slot] == EMPTY:
                table[slot] = np.uint32(i)
                break
            slot = (slot + np.uint64(1)) & mask


def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate a compact Frontier checkpoint to larger capacities."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("dest", type=Path)
    parser.add_argument("--state-capacity", type=int, required=True)
    parser.add_argument("--hash-capacity", type=int, required=True)
    args = parser.parse_args()

    if args.state_capacity <= 0:
        raise SystemExit("--state-capacity must be positive")
    if not is_power_of_two(args.hash_capacity):
        raise SystemExit("--hash-capacity must be a positive power of two")

    meta = json.loads((args.source / "metadata.json").read_text())
    count = int(meta["states"])
    old_capacity = int(meta["capacity"])
    old_hash_capacity = int(meta["hash_capacity"])

    if args.state_capacity < count:
        raise SystemExit(
            f"state capacity {args.state_capacity:,} < existing states {count:,}"
        )
    if args.hash_capacity <= count * 2:
        raise SystemExit(
            f"hash capacity {args.hash_capacity:,} is too small; "
            f"choose more than 2x {count:,}"
        )
    if args.dest.exists():
        raise SystemExit(f"destination already exists: {args.dest}")

    print(f"Existing states:    {count:,}")
    print(f"Old state capacity: {old_capacity:,}")
    print(f"Old hash capacity:  {old_hash_capacity:,}")
    print(f"New state capacity: {args.state_capacity:,}")
    print(f"New hash capacity:  {args.hash_capacity:,}")
    print(f"New hash load:      {count / args.hash_capacity:.3f}")
    print(
        f"New RAM arrays:     "
        f"{args.state_capacity * 12 / (1024**3):.2f} GiB states + "
        f"{args.hash_capacity * 4 / (1024**3):.2f} GiB hash",
        flush=True,
    )

    args.dest.mkdir(parents=True)
    start = time.perf_counter()

    print("Loading existing states...", flush=True)
    old_lo = np.fromfile(args.source / "states_lo.u64", dtype=np.uint64)
    old_hi = np.fromfile(args.source / "states_hi.u32", dtype=np.uint32)

    if len(old_lo) < count or len(old_hi) < count:
        raise SystemExit("source state files are shorter than metadata states")

    print("Allocating enlarged state arrays...", flush=True)
    state_lo = np.empty(args.state_capacity, dtype=np.uint64)
    state_hi = np.empty(args.state_capacity, dtype=np.uint32)
    state_lo[:count] = old_lo[:count]
    state_hi[:count] = old_hi[:count]
    del old_lo, old_hi

    print("Allocating enlarged hash table...", flush=True)
    table = np.full(args.hash_capacity, EMPTY, dtype=np.uint32)

    print("Rebuilding hash table...", flush=True)
    t0 = time.perf_counter()
    rebuild_hash(state_lo, state_hi, count, table)
    print(f"Hash rebuild: {time.perf_counter() - t0:.1f}s", flush=True)

    print("Writing migrated checkpoint...", flush=True)
    state_lo[:count].tofile(args.dest / "states_lo.u64")
    state_hi[:count].tofile(args.dest / "states_hi.u32")
    table.tofile(args.dest / "seen_index.u32")

    new_meta = dict(meta)
    new_meta["version"] = 4
    new_meta["capacity"] = args.state_capacity
    new_meta["hash_capacity"] = args.hash_capacity

    tmp = args.dest / "metadata.json.tmp"
    tmp.write_text(json.dumps(new_meta, indent=2) + "\n")
    os.replace(tmp, args.dest / "metadata.json")

    print(f"Migration complete: {time.perf_counter() - start:.1f}s")
    print(f"Destination: {args.dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
