#!/usr/bin/env python3
"""
Targeted 4x9 Macro search for first return path to state 0.
Target depth: 60 (for z=60, the first known tileable length).
Uses checkpoint/resume.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from collections import Counter, deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

CHECKPOINT_VERSION = 1
_interrupted = False

def signal_handler(signum, frame):
    global _interrupted
    _interrupted = True
    print(f"\nInterrupted (signal {signum}). Saving checkpoint and exiting...")

def build_templates_general(a, b):
    """Generate templates for a×b cross-section."""
    NCELLS = a * b
    LAYERS = 3
    raw, _ = generate_placements(PENTACUBES["S"], (a, b, 20), break_symmetry=False)
    templates = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    concrete_count = len(raw)
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
                if rel < 0 or rel >= LAYERS: valid = False; break
                cell_id = cx + a * cy
                shifted_masks[rel] |= (1 << cell_id)
            if not valid: continue
            packed = 0
            for i, mask in enumerate(shifted_masks):
                packed |= (mask << (i * NCELLS))
            if packed in seen[target]: continue
            seen[target].add(packed)
            templates[target].append(packed)
    total_templates = sum(len(v) for v in templates.values())
    return templates, NCELLS, (1 << NCELLS) - 1, concrete_count, total_templates

def layer_mask(state, layer, NCELLS):
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)

def first_empty(mask, NCELLS):
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    if not missing: return -1
    low = missing & -missing
    return low.bit_length() - 1

def apply_template(state, template):
    if state & template: return None
    return state | template

def shift_state(state, NCELLS):
    return state >> NCELLS

def save_checkpoint(path, phase, a, b, NCELLS, WORD_MASK, max_states,
                    sources, seen_macro, queue, succ, edge_count,
                    total_intermediate, fg_states, depth_map):
    """Save checkpoint atomically."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    meta = {
        "version": CHECKPOINT_VERSION, "phase": phase,
        "a": a, "b": b, "NCELLS": NCELLS, "WORD_MASK": WORD_MASK,
        "max_states": max_states, "edge_count": edge_count,
        "total_intermediate": total_intermediate,
        "fg_states_so_far": fg_states,
        "timestamp": time.time(),
    }
    with open(path / "metadata.json", "w") as f:
        json.dump(meta, f)
    with open(path / "sources.json", "w") as f:
        json.dump(sorted(sources), f)
    with open(path / "macro_seen.json", "w") as f:
        json.dump(sorted(seen_macro), f)
    with open(path / "queue.json", "w") as f:
        json.dump(list(queue), f)
    succ_ser = {str(k): sorted(v) for k, v in succ.items()}
    with open(path / "succ.json", "w") as f:
        json.dump(succ_ser, f)
    with open(path / "depth_map.json", "w") as f:
        json.dump({str(k): v for k, v in depth_map.items()}, f)
    print(f"  [checkpoint] Saved: {len(seen_macro):,} macro states, {len(queue):,} queue")

def load_checkpoint(path):
    """Load checkpoint. Returns dict or None."""
    path = Path(path)
    if not path.exists(): return None
    try:
        with open(path / "metadata.json") as f: meta = json.load(f)
        with open(path / "sources.json") as f: sources = set(json.load(f))
        with open(path / "macro_seen.json") as f: seen_macro = set(json.load(f))
        with open(path / "queue.json") as f: queue = deque(json.load(f))
        with open(path / "succ.json") as f:
            succ_raw = json.load(f)
            succ = {int(k): set(v) for k, v in succ_raw.items()}
        with open(path / "depth_map.json") as f:
            depth_raw = json.load(f)
            depth_map = {int(k): v for k, v in depth_raw.items()}
        return {
            "metadata": meta, "sources": sources, "seen_macro": seen_macro,
            "queue": queue, "succ": succ, "depth_map": depth_map,
            "edge_count": meta["edge_count"],
            "total_intermediate": meta["total_intermediate"],
        }
    except Exception as e:
        print(f"  ERROR loading checkpoint: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="4x9 first-return Macro search")
    parser.add_argument("--max-states", type=int, default=50_000_000)
    parser.add_argument("--max-time", type=int, default=7200)
    parser.add_argument("--target-depth", type=int, default=60)
    parser.add_argument("--checkpoint-dir", type=str,
                        default="/tmp/macro_4x9_search.ckpt")
    parser.add_argument("--checkpoint-interval", type=int, default=500_000)
    parser.add_argument("--report-interval", type=int, default=100_000)
    args = parser.parse_args()

    a, b = 4, 9
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1
    ckpt_dir = Path(args.checkpoint_dir)
    start_time = time.perf_counter()

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Try loading checkpoint
    ckpt_data = load_checkpoint(ckpt_dir)
    if ckpt_data:
        print("Resuming from checkpoint...")
        print(f"  {len(ckpt_data['seen_macro']):,} macro states, "
              f"{len(ckpt_data['queue']):,} queue")
        sources = ckpt_data["sources"]
        seen_macro = ckpt_data["seen_macro"]
        queue = ckpt_data["queue"]
        succ = ckpt_data["succ"]
        depth_map = ckpt_data["depth_map"]
        edge_count = ckpt_data["edge_count"]
        total_intermediate = ckpt_data["total_intermediate"]
        max_depth_sofar = max(depth_map.values()) if depth_map else 0
        print(f"  Max depth so far: {max_depth_sofar}")
        phase = "macro_closure"
        # Build templates (needed for explore_source)
        templates, NCELLS, WORD_MASK, _, _ = build_templates_general(a, b)
        fg_states = 0
    else:
        print("Starting fresh...")
        print(f"Building templates for {a}x{b}...")
        t0 = time.perf_counter()
        templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates_general(a, b)
        t1 = time.perf_counter()
        print(f"  Templates: {total_templates}, Build: {t1-t0:.1f}s")

        # Phase 1: First generation
        print("\nPhase 1: First generation...")
        phase = "first_generation"
        sources = set()
        seen_fg = {0}
        queue = deque([0])
        fg_states = 0

        while queue:
            if len(seen_fg) >= 10_000_000:
                print(f"  First-gen cap hit at {len(seen_fg):,} states")
                break
            state = queue.popleft()
            l0 = layer_mask(state, 0, NCELLS)
            if l0 == WORD_MASK:
                sources.add(shift_state(state, NCELLS))
                continue
            target = first_empty(l0, NCELLS)
            for template in templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in seen_fg: continue
                seen_fg.add(nxt)
                queue.append(nxt)

        print(f"  Sources: {len(sources):,}, Tree states: {len(seen_fg):,}")
        fg_states = len(seen_fg)

        # Phase 2: Macro closure
        print("\nPhase 2: Macro closure (target depth {})...".format(args.target_depth))
        phase = "macro_closure"
        seen_macro = set(sources)
        queue = deque(sources)
        succ = {}
        depth_map = {s: 0 for s in sources}
        edge_count = 0
        total_intermediate = 0

    # ============================================================
    # Macro closure BFS
    # ============================================================
    global _interrupted
    max_depth = max(depth_map.values()) if depth_map else 0
    zero_found = 0 in seen_macro
    last_checkpoint = len(seen_macro)
    last_report = len(seen_macro)
    processed = 0

    while queue and not _interrupted and not zero_found:
        elapsed = time.perf_counter() - start_time
        if elapsed > args.max_time:
            print(f"\nTime limit ({args.max_time}s) reached")
            break
        if len(seen_macro) >= args.max_states:
            print(f"\nState limit ({args.max_states:,}) reached")
            break
        if max_depth >= args.target_depth:
            print(f"\nTarget depth {args.target_depth} reached!")
            break

        src = queue.popleft()
        sd = depth_map.get(src, 0)
        processed += 1

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
                if nxt is None or nxt in es: continue
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
            dc = Counter(depth_map.values())
            current_depth_stats = {d: dc[d] for d in sorted(dc.keys())}
            top_depths = sorted(dc.items(), key=lambda x: -x[1])[:15]
            print(f"  [{len(seen_macro):,}] processed={processed:,} "
                  f"max_depth={max_depth} queue={len(queue):,} "
                  f"edges={edge_count:,} "
                  f"top={top_depths} "
                  f"elapsed={elapsed:.0f}s")
            last_report = len(seen_macro)

        # Checkpoint
        if len(seen_macro) - last_checkpoint >= args.checkpoint_interval:
            save_checkpoint(ckpt_dir, phase, a, b, NCELLS, WORD_MASK,
                           args.max_states, sources, seen_macro, queue,
                           succ, edge_count, total_intermediate, fg_states, depth_map)
            last_checkpoint = len(seen_macro)

    # Final checkpoint
    elapsed = time.perf_counter() - start_time
    save_checkpoint(ckpt_dir, phase, a, b, NCELLS, WORD_MASK,
                   args.max_states, sources, seen_macro, queue,
                   succ, edge_count, total_intermediate, fg_states, depth_map)

    print(f"\n{'='*60}")
    print(f"SEARCH RESULTS")
    print(f"{'='*60}")
    print(f"  Sources: {len(sources):,}")
    print(f"  Macro states: {len(seen_macro):,}")
    print(f"  Macro edges: {edge_count:,}")
    print(f"  Processed sources: {processed:,}")
    print(f"  Max depth: {max_depth}")
    print(f"  Queue remaining: {len(queue):,}")
    print(f"  State 0 found: {zero_found}")
    print(f"  Elapsed: {elapsed:.0f}s")

    # Depth distribution
    print(f"\nDepth distribution:")
    dc = Counter(depth_map.values())
    for d in sorted(dc.keys()):
        print(f"  depth {d}: {dc[d]:,}")
    print(f"  Total: {len(depth_map):,}")

    # Save stats
    out = REPO_ROOT / "data" / "frontier" / "4x9_return_search_results.txt"
    lines = [
        f"sources={len(sources)}",
        f"macro_states={len(seen_macro)}",
        f"macro_edges={edge_count}",
        f"processed={processed}",
        f"max_depth={max_depth}",
        f"queue_remaining={len(queue)}",
        f"zero_found={zero_found}",
        f"elapsed={elapsed:.0f}",
    ]
    for d in sorted(dc.keys()):
        lines.append(f"depth_{d}={dc[d]}")
    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())