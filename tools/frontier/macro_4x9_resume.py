#!/usr/bin/env python3
"""
Resume 4x9 Macro search from binary checkpoint toward depth 60.
Uses pickle-based checkpoints for 108-bit state support.
"""

from __future__ import annotations

import argparse
import json
import pickle
import signal
import sys
import time
from collections import Counter, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

_interrupted = False

def signal_handler(signum, frame):
    global _interrupted
    _interrupted = True
    print(f"\nInterrupted. Saving checkpoint...")


def build_templates(a, b):
    NCELLS = a * b
    LAYERS = 3
    raw, _ = generate_placements(PENTACUBES["S"], (a, b, 20), break_symmetry=False)
    templates = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    for placement in raw.values():
        cells = tuple(placement)
        min_z = min(z for _, _, z in cells)
        for x, y, z in cells:
            target = x + a * y
            target_rel = z - min_z
            shifted_masks = [0] * LAYERS
            valid = True
            for cx, cy, cz in cells:
                rel = cz - min_z - target_rel
                if rel < 0 or rel >= LAYERS:
                    valid = False
                    break
                cell_id = cx + a * cy
                shifted_masks[rel] |= (1 << cell_id)
            if not valid:
                continue
            packed = 0
            for i, mask in enumerate(shifted_masks):
                packed |= (mask << (i * NCELLS))
            if packed in seen[target]:
                continue
            seen[target].add(packed)
            templates[target].append(packed)
    return templates, NCELLS, (1 << NCELLS) - 1


def layer_mask(state, layer, NCELLS):
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)


def first_empty(mask, NCELLS):
    wm = (1 << NCELLS) - 1
    missing = wm & ~mask
    if not missing:
        return -1
    return (missing & -missing).bit_length() - 1


def apply_template(state, t):
    if state & t:
        return None
    return state | t


def shift_state(state, NCELLS):
    return state >> NCELLS


def save_checkpoint(dir_path, sources, seen_macro, queue, succ, depth_map,
                    edge_count, total_intermediate, meta_extra):
    """Atomic pickle checkpoint."""
    dir_path = Path(dir_path)
    tmp_path = Path(str(dir_path) + ".tmp")
    tmp_path.mkdir(parents=True, exist_ok=True)

    with open(tmp_path / "macro_seen.pkl", "wb") as f:
        pickle.dump(seen_macro, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open(tmp_path / "sources.pkl", "wb") as f:
        pickle.dump(sources, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open(tmp_path / "queue.pkl", "wb") as f:
        pickle.dump(list(queue), f, protocol=pickle.HIGHEST_PROTOCOL)
    with open(tmp_path / "succ.pkl", "wb") as f:
        pickle.dump(succ, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open(tmp_path / "depth_map.pkl", "wb") as f:
        pickle.dump(depth_map, f, protocol=pickle.HIGHEST_PROTOCOL)

    meta = {
        "checkpoint_version": 3, "a": 4, "b": 9,
        "edge_count": edge_count, "total_intermediate": total_intermediate,
        "states": len(seen_macro), "queue_len": len(queue),
        "timestamp": time.time(), **meta_extra
    }
    with open(tmp_path / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Atomic rename
    import shutil
    if dir_path.exists():
        shutil.rmtree(dir_path)
    tmp_path.rename(dir_path)
    print(f"  [ckpt] {len(seen_macro):,} states, {len(queue):,} queue, "
          f"edg={edge_count}")


def load_checkpoint(dir_path):
    """Load pickle checkpoint."""
    p = Path(dir_path)
    if not p.exists():
        return None
    try:
        with open(p / "metadata.json") as f:
            meta = json.load(f)
        with open(p / "macro_seen.pkl", "rb") as f:
            seen_macro = pickle.load(f)
        with open(p / "sources.pkl", "rb") as f:
            sources = pickle.load(f)
        with open(p / "queue.pkl", "rb") as f:
            queue = deque(pickle.load(f))
        with open(p / "succ.pkl", "rb") as f:
            succ = pickle.load(f)
        with open(p / "depth_map.pkl", "rb") as f:
            depth_map = pickle.load(f)
        return {
            "meta": meta, "sources": sources, "seen_macro": seen_macro,
            "queue": queue, "succ": succ, "depth_map": depth_map,
            "edge_count": meta["edge_count"],
            "total_intermediate": meta.get("total_intermediate", 0),
        }
    except Exception as e:
        print(f"  ERROR loading checkpoint: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="4x9 return search")
    parser.add_argument("--max-states", type=int, default=50_000_000)
    parser.add_argument("--max-time", type=int, default=14400)
    parser.add_argument("--target-depth", type=int, default=60)
    parser.add_argument("--checkpoint-dir", type=str,
                        default="/tmp/macro_4x9_binary.ckpt")
    parser.add_argument("--checkpoint-interval", type=int, default=500_000)
    parser.add_argument("--report-interval", type=int, default=25_000)
    args = parser.parse_args()

    a, b = 4, 9
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1
    ckpt_dir = Path(args.checkpoint_dir)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Resume from checkpoint
    ckpt = load_checkpoint(ckpt_dir)
    if not ckpt:
        print("No checkpoint found at", ckpt_dir)
        return 1

    print("Resumed from checkpoint.")
    print(f"  States: {len(ckpt['seen_macro']):,}")
    print(f"  Queue: {len(ckpt['queue']):,}")
    print(f"  Edges: {ckpt['edge_count']:,}")
    max_depth = max(ckpt['depth_map'].values()) if ckpt['depth_map'] else 0
    print(f"  Max depth: {max_depth}")

    sources = ckpt['sources']
    seen_macro = ckpt['seen_macro']
    queue = ckpt['queue']
    succ = ckpt['succ']
    depth_map = ckpt['depth_map']
    edge_count = ckpt['edge_count']
    total_intermediate = ckpt['total_intermediate']

    # Build templates
    print("\nBuilding templates...", end=" ", flush=True)
    templates, NCELLS, WORD_MASK = build_templates(a, b)
    print("done.")

    # ============================================================
    # Macro closure BFS
    # ============================================================
    global _interrupted
    zero_found = 0 in seen_macro
    last_checkpoint = len(seen_macro)
    last_report = len(seen_macro)
    start_time = time.perf_counter()

    while queue and not _interrupted and not zero_found:
        elapsed = time.perf_counter() - start_time
        if elapsed > args.max_time:
            print(f"\nTime limit ({args.max_time}s)")
            break
        if len(seen_macro) >= args.max_states:
            print(f"\nState limit ({args.max_states:,})")
            break
        if max_depth >= args.target_depth:
            print(f"\nTarget depth {args.target_depth} reached!")
            break

        src = queue.popleft()
        sd = depth_map.get(src, 0)

        # Explore placement interval
        successors = set()
        es = {src}
        eq = deque([src])
        while eq:
            state = eq.popleft()
            l0 = layer_mask(state, 0, NCELLS)
            if l0 == WORD_MASK:
                successors.add(shift_state(state, NCELLS))
                continue
            target = first_empty(l0, NCELLS)
            for template in templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in es:
                    continue
                es.add(nxt)
                eq.append(nxt)

        total_intermediate += len(es) - 1

        if successors:
            succ[src] = successors
            edge_count += len(successors)

        for s in successors:
            if s not in seen_macro:
                seen_macro.add(s)
                depth_map[s] = sd + 1
                if sd + 1 > max_depth:
                    max_depth = sd + 1
                queue.append(s)
            if s == 0:
                zero_found = True
                print(f"\n*** STATE 0 FOUND at depth {sd + 1}! ***")

        # Progress report
        if len(seen_macro) - last_report >= args.report_interval:
            elapsed = time.perf_counter() - start_time
            dc = Counter(depth_map.values())
            top = sorted(dc.items(), key=lambda x: -x[1])[:5]
            print(f"  [{len(seen_macro):,}] depth={max_depth} "
                  f"q={len(queue):,} e={edge_count:,} "
                  f"t={elapsed:.0f}s top={top}")
            last_report = len(seen_macro)

        # Checkpoint
        if len(seen_macro) - last_checkpoint >= args.checkpoint_interval:
            save_checkpoint(ckpt_dir, sources, seen_macro, queue, succ,
                           depth_map, edge_count, total_intermediate,
                           {"max_states": args.max_states})
            last_checkpoint = len(seen_macro)

    # Final save
    elapsed = time.perf_counter() - start_time
    save_checkpoint(ckpt_dir, sources, seen_macro, queue, succ,
                   depth_map, edge_count, total_intermediate,
                   {"max_states": args.max_states})

    print(f"\n{'='*60}")
    print("SEARCH RESULTS")
    print(f"{'='*60}")
    print(f"  States: {len(seen_macro):,}")
    print(f"  Edges: {edge_count:,}")
    print(f"  Max depth: {max_depth}")
    print(f"  Queue: {len(queue):,}")
    print(f"  State 0 found: {zero_found}")
    print(f"  Elapsed: {elapsed:.0f}s")

    dc = Counter(depth_map.values())
    for d in sorted(dc.keys()):
        print(f"  depth {d}: {dc[d]:,}")

    if zero_found:
        # Find the predecessor chain to reconstruct path
        print(f"\nState 0 found! Reconstructing path...")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())