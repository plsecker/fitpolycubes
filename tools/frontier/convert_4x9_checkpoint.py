#!/usr/bin/env python3
"""
Convert 4x9 Macro search checkpoint from JSON to compact binary format.
Uses numpy uint64 arrays instead of JSON text.
"""

import json, sys, time
from collections import deque
from pathlib import Path

import numpy as np

CHECKPOINT_VERSION = 2  # binary format version

def convert_checkpoint(src_dir: Path, dst_dir: Path):
    """Convert JSON checkpoint to binary numpy format."""
    print(f"Converting {src_dir} -> {dst_dir}")
    t0 = time.perf_counter()

    dst_dir.mkdir(parents=True, exist_ok=True)

    # Load metadata
    with open(src_dir / "metadata.json") as f:
        meta = json.load(f)
    meta["checkpoint_version"] = CHECKPOINT_VERSION

    # Convert macro_seen (sorted list of ints -> uint64 array)
    print("  Converting macro_seen...")
    with open(src_dir / "macro_seen.json") as f:
        macro_seen_list = json.load(f)
    macro_seen_arr = np.array(macro_seen_list, dtype=np.uint64)
    np.save(dst_dir / "macro_seen.npy", macro_seen_arr, allow_pickle=False)
    del macro_seen_list
    print(f"    {len(macro_seen_arr):,} states -> {macro_seen_arr.nbytes/1e6:.1f} MB")

    # Convert sources
    print("  Converting sources...")
    with open(src_dir / "sources.json") as f:
        sources_list = json.load(f)
    sources_arr = np.array(sources_list, dtype=np.uint64)
    np.save(dst_dir / "sources.npy", sources_arr, allow_pickle=False)
    del sources_list

    # Convert queue
    print("  Converting queue...")
    with open(src_dir / "queue.json") as f:
        queue_list = json.load(f)
    queue_arr = np.array(queue_list, dtype=np.uint64)
    np.save(dst_dir / "queue.npy", queue_arr, allow_pickle=False)
    del queue_list
    print(f"    {len(queue_arr):,} states")

    # Convert succ (dict -> flat array with markers)
    print("  Converting succ...")
    with open(src_dir / "succ.json") as f:
        succ_raw = json.load(f)
    succ_data = []
    for k in sorted(succ_raw.keys(), key=lambda x: int(x)):
        src = int(k)
        succs = sorted(int(v) for v in succ_raw[k])
        succ_data.append(src)
        succ_data.append(len(succs))
        succ_data.extend(succs)
    succ_arr = np.array(succ_data, dtype=np.uint64)
    np.save(dst_dir / "succ.npy", succ_arr, allow_pickle=False)
    del succ_raw, succ_data
    print(f"    {len(succ_arr):,} uint64s -> {succ_arr.nbytes/1e6:.1f} MB")

    # Convert depth_map
    print("  Converting depth_map...")
    with open(src_dir / "depth_map.json") as f:
        depth_raw = json.load(f)
    depth_data = []
    for k in sorted(depth_raw.keys(), key=lambda x: int(x)):
        depth_data.append(int(k))
        depth_data.append(depth_raw[k])
    depth_arr = np.array(depth_data, dtype=np.uint64)
    np.save(dst_dir / "depth_map.npy", depth_arr, allow_pickle=False)
    del depth_raw, depth_data
    print(f"    {len(depth_arr)//2:,} entries -> {depth_arr.nbytes/1e6:.1f} MB")

    # Save metadata
    with open(dst_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    t1 = time.perf_counter()
    print(f"\n  Conversion completed in {t1-t0:.1f}s")

    # Size comparison
    src_size = sum(f.stat().st_size for f in src_dir.glob("*.json")) / 1e9
    dst_size = sum(f.stat().st_size for f in dst_dir.glob("*.npy")) / 1e9
    print(f"  Source size: {src_size:.2f} GB (JSON)")
    print(f"  Dest size:   {dst_size:.2f} GB (numpy)")
    print(f"  Ratio:       {dst_size/src_size*100:.1f}%")


def verify_conversion(src_dir, dst_dir):
    """Verify binary checkpoint matches source."""
    print("\nVerifying conversion...")

    # Load JSON versions
    t0 = time.perf_counter()

    # macro_seen
    with open(src_dir / "macro_seen.json") as f:
        js_macro = set(json.load(f))
    np_macro = set(int(x) for x in np.load(dst_dir / "macro_seen.npy"))
    assert js_macro == np_macro, "macro_seen mismatch!"
    print(f"  ✓ macro_seen: {len(js_macro):,} states")

    # sources
    with open(src_dir / "sources.json") as f:
        js_sources = set(json.load(f))
    np_sources = set(int(x) for x in np.load(dst_dir / "sources.npy"))
    assert js_sources == np_sources, "sources mismatch!"
    print(f"  ✓ sources: {len(js_sources):,}")

    # queue
    with open(src_dir / "queue.json") as f:
        js_queue = list(json.load(f))
    np_queue = list(int(x) for x in np.load(dst_dir / "queue.npy"))
    assert js_queue == np_queue, "queue mismatch!"
    print(f"  ✓ queue: {len(js_queue):,}")

    # succ
    with open(src_dir / "succ.json") as f:
        js_succ_raw = json.load(f)
    js_succ = {}
    for k, v in js_succ_raw.items():
        js_succ[int(k)] = set(int(x) for x in v)

    np_succ_arr = np.load(dst_dir / "succ.npy")
    np_succ = {}
    i = 0
    while i < len(np_succ_arr):
        src = int(np_succ_arr[i])
        n = int(np_succ_arr[i + 1])
        succs = set(int(x) for x in np_succ_arr[i + 2:i + 2 + n])
        np_succ[src] = succs
        i += 2 + n
    assert js_succ == np_succ, "succ mismatch!"
    print(f"  ✓ succ: {len(js_succ):,} entries, {sum(len(v) for v in js_succ.values()):,} edges")

    # depth_map
    with open(src_dir / "depth_map.json") as f:
        js_depth = {int(k): v for k, v in json.load(f).items()}
    np_depth_arr = np.load(dst_dir / "depth_map.npy")
    np_depth = {}
    for i in range(0, len(np_depth_arr), 2):
        np_depth[int(np_depth_arr[i])] = int(np_depth_arr[i + 1])
    assert js_depth == np_depth, "depth_map mismatch!"
    print(f"  ✓ depth_map: {len(js_depth):,} entries, max={max(js_depth.values())}")

    t1 = time.perf_counter()
    print(f"  Verification completed in {t1-t0:.2f}s")
    print(f"\n  ALL CHECKS PASSED ✓")


if __name__ == "__main__":
    src = Path("/tmp/macro_4x9_search.ckpt")
    dst = Path("/tmp/macro_4x9_binary.ckpt")

    if not src.exists():
        print(f"Source checkpoint not found: {src}")
        sys.exit(1)

    convert_checkpoint(src, dst)
    verify_conversion(src, dst)

    print(f"\nBinary checkpoint ready at {dst}")
    print(f"  Total size: {sum(f.stat().st_size for f in dst.glob('*.npy'))/1e9:.2f} GB")