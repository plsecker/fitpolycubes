#!/usr/bin/env python3
"""
Multiprocessing prototype for macro closure BFS.

This prototype implements batch-parallel BFS closure while preserving
exactly the existing MacroState/MacroEdge semantics and BFS discovery order.

Architecture:
- Parent maintains macro_seen, queue, succ, dist (authoritative)
- Workers receive batches of sources, run explore_source(), return successors
- Parent merges results in FIFO order with per-source cap checks
- Checkpoint format unchanged (compatible with serial implementation)

Key design decisions:
1. FIFO batch processing (not strict level-by-level) preserves BFS distances
2. Per-source cap checks in merge order give exact serial equivalence
3. Workers=1 runs the new code path in-process (no pool overhead)
4. Templates inherited via fork (COW), no per-task pickling
5. Wave-based submission with configurable wave_size for pipelining

Usage:
    # Serial baseline (verbatim copy of original implementation)
    python scc_aware_analysis_mp.py --mode serial --max-closure-states 1000000

    # Parallel with 1 worker (in-process, validates merge logic)
    python scc_aware_analysis_mp.py --mode parallel --workers 1 --max-closure-states 1000000

    # Parallel with 2 workers
    python scc_aware_analysis_mp.py --mode parallel --workers 2 --max-closure-states 1000000

    # Parallel with 4 workers
    python scc_aware_analysis_mp.py --mode parallel --workers 4 --max-closure-states 1000000

    # Compare serial vs parallel (runs both and compares)
    python scc_aware_analysis_mp.py --mode compare --max-closure-states 1000000

    # With checkpointing
    python scc_aware_analysis_mp.py --mode parallel --workers 2 --max-closure-states 1000000 \
        --checkpoint-dir /tmp/mp_proto_checkpoints --checkpoint-every 250000
"""

from __future__ import annotations

import argparse
import multiprocessing
import os
import resource
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from solvers.s_z_frontier_packed import (
    WORD_MASK,
    apply_template,
    build_templates,
    first_empty,
    layer_mask,
    shift_state,
)

MAX_FIRSTGEN_STATES = 5_000_000
MAX_INTERMEDIATE = 1_000_000
MAX_INTERMEDIATE_0 = 4_000_000

S_STAR = 6163195513375031274
TARGET_DISTANCE = 129  # For N=130


# ============================================================================
# Worker globals and functions
# ============================================================================

_WORKER_TEMPLATES = None
_WORKER_MAX_INTERMEDIATE = MAX_INTERMEDIATE


def _init_worker(templates, max_intermediate):
    """Initialize worker process with templates."""
    global _WORKER_TEMPLATES, _WORKER_MAX_INTERMEDIATE
    _WORKER_TEMPLATES = templates
    _WORKER_MAX_INTERMEDIATE = max_intermediate


def _worker_explore(batch):
    """
    Worker function: explore a batch of sources.
    
    Args:
        batch: tuple of source states
    
    Returns:
        list of (src, successors_tuple) where successors_tuple is a tuple of ints
    """
    results = []
    for src in batch:
        successors = set()
        seen = {src}
        queue = deque([src])
        
        while queue:
            if len(seen) - 1 >= _WORKER_MAX_INTERMEDIATE:
                break
            
            state = queue.popleft()
            
            if layer_mask(state, 0) == WORD_MASK:
                successors.add(shift_state(state))
                continue
            
            target = first_empty(layer_mask(state, 0))
            
            for template in _WORKER_TEMPLATES[target]:
                nxt = apply_template(state, template)
                
                if nxt is None or nxt in seen:
                    continue
                
                seen.add(nxt)
                queue.append(nxt)
        
        results.append((src, tuple(successors)))
    
    return results


# ============================================================================
# explore_source (unchanged from original)
# ============================================================================

def explore_source(source, templates, max_intermediate=MAX_INTERMEDIATE):
    """
    Explore from a single source state.
    
    Returns set of successor states (shifted states with full layer 0).
    """
    successors = set()
    seen = {source}
    queue = deque([source])
    
    while queue:
        if len(seen) - 1 >= max_intermediate:
            break
        
        state = queue.popleft()
        
        if layer_mask(state, 0) == WORD_MASK:
            successors.add(shift_state(state))
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append(nxt)
    
    return successors


# ============================================================================
# first_generation_sources (unchanged from original)
# ============================================================================

def first_generation_sources(templates):
    sources = set()
    seen = {0}
    queue = deque([0])
    
    while queue:
        if len(seen) >= MAX_FIRSTGEN_STATES:
            break
        
        state = queue.popleft()
        
        if layer_mask(state, 0) == WORD_MASK:
            sources.add(shift_state(state))
            continue
        
        target = first_empty(layer_mask(state, 0))
        
        for template in templates[target]:
            nxt = apply_template(state, template)
            
            if nxt is None or nxt in seen:
                continue
            
            seen.add(nxt)
            queue.append(nxt)
    
    return sources


# ============================================================================
# Checkpoint functions (unchanged from original)
# ============================================================================

def save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed, unprocessed_wave=None):
    """Save checkpoint atomically using temporary file + rename.
    
    Args:
        unprocessed_wave: list of sources that were popped from queue into current wave
                         but haven't been processed yet (for parallel mode)
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    temp_dir = checkpoint_dir / ".checkpoint_temp"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        macro_seen_arr = np.array(sorted(macro_seen), dtype=np.uint64)
        temp_seen = temp_dir / "macro_seen.npy"
        np.save(temp_seen, macro_seen_arr, allow_pickle=False)
        
        queue_arr = np.array(list(queue), dtype=np.uint64)
        temp_queue = temp_dir / "queue.npy"
        np.save(temp_queue, queue_arr, allow_pickle=False)
        
        # Save unprocessed wave sources (for parallel mode)
        if unprocessed_wave is not None:
            wave_arr = np.array(unprocessed_wave, dtype=np.uint64)
            temp_wave = temp_dir / "unprocessed_wave.npy"
            np.save(temp_wave, wave_arr, allow_pickle=False)
        
        succ_data = []
        for src, succs in succ.items():
            succ_data.append(src)
            succ_data.append(len(succs))
            succ_data.extend(sorted(succs))
        succ_arr = np.array(succ_data, dtype=np.uint64)
        temp_succ = temp_dir / "succ.npy"
        np.save(temp_succ, succ_arr, allow_pickle=False)
        
        dist_data = []
        for state, d in dist.items():
            dist_data.append(state)
            dist_data.append(d)
        dist_arr = np.array(dist_data, dtype=np.uint64)
        temp_dist = temp_dir / "dist.npy"
        np.save(temp_dist, dist_arr, allow_pickle=False)
        
        temp_counters = temp_dir / "counters.txt"
        with open(temp_counters, 'w') as f:
            f.write(f"total_intermediate={counters['total_intermediate']}\n")
            f.write(f"edge_count={counters['edge_count']}\n")
            f.write(f"elapsed={elapsed}\n")
        
        final_seen = checkpoint_dir / "macro_seen.npy"
        final_queue = checkpoint_dir / "queue.npy"
        final_succ = checkpoint_dir / "succ.npy"
        final_dist = checkpoint_dir / "dist.npy"
        final_counters = checkpoint_dir / "counters.txt"
        
        os.replace(temp_seen, final_seen)
        os.replace(temp_queue, final_queue)
        os.replace(temp_succ, final_succ)
        os.replace(temp_dist, final_dist)
        os.replace(temp_counters, final_counters)
        
        if unprocessed_wave is not None:
            final_wave = checkpoint_dir / "unprocessed_wave.npy"
            os.replace(temp_wave, final_wave)
        else:
            # Remove old unprocessed_wave.npy if it exists
            final_wave = checkpoint_dir / "unprocessed_wave.npy"
            if final_wave.exists():
                final_wave.unlink()
        
        temp_dir.rmdir()
        
        return True
    except Exception as e:
        print(f"  ERROR saving checkpoint: {e}", flush=True)
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False


def load_checkpoint(checkpoint_dir):
    """Load checkpoint from directory.
    
    Returns:
        (macro_seen, queue, succ, dist, counters, unprocessed_wave) or None if no checkpoint exists.
        unprocessed_wave is a list of sources that were popped from queue but not yet processed
        (for parallel mode), or None if not present (serial mode or old checkpoint).
    """
    checkpoint_dir = Path(checkpoint_dir)
    
    required_files = [
        "macro_seen.npy",
        "queue.npy",
        "succ.npy",
        "dist.npy",
        "counters.txt",
    ]
    
    for fname in required_files:
        if not (checkpoint_dir / fname).exists():
            return None
    
    try:
        macro_seen_arr = np.load(checkpoint_dir / "macro_seen.npy", allow_pickle=False)
        macro_seen = set(macro_seen_arr.tolist())
        
        queue_arr = np.load(checkpoint_dir / "queue.npy", allow_pickle=False)
        queue = deque(queue_arr.tolist())
        
        succ_arr = np.load(checkpoint_dir / "succ.npy", allow_pickle=False)
        succ = {}
        i = 0
        while i < len(succ_arr):
            src = int(succ_arr[i])
            num_succ = int(succ_arr[i + 1])
            succs = set(int(x) for x in succ_arr[i + 2:i + 2 + num_succ])
            succ[src] = succs
            i += 2 + num_succ
        
        dist_arr = np.load(checkpoint_dir / "dist.npy", allow_pickle=False)
        dist = {}
        for i in range(0, len(dist_arr), 2):
            state = int(dist_arr[i])
            d = int(dist_arr[i + 1])
            dist[state] = d
        
        counters = {}
        with open(checkpoint_dir / "counters.txt", 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                if key in ('total_intermediate', 'edge_count'):
                    counters[key] = int(value)
                elif key == 'elapsed':
                    counters[key] = float(value)
        
        if 'source_expansions' not in counters:
            counters['source_expansions'] = 0
        if 'max_bfs_distance' not in counters:
            counters['max_bfs_distance'] = 0
        
        # Load unprocessed wave sources (for parallel mode)
        unprocessed_wave = None
        wave_file = checkpoint_dir / "unprocessed_wave.npy"
        if wave_file.exists():
            wave_arr = np.load(wave_file, allow_pickle=False)
            unprocessed_wave = wave_arr.tolist()
        
        return macro_seen, queue, succ, dist, counters, unprocessed_wave
    except Exception as e:
        print(f"  ERROR loading checkpoint: {e}", flush=True)
        return None


# ============================================================================
# Serial macro_closure (verbatim copy of original for baseline comparison)
# ============================================================================

def macro_closure_serial(sources, templates, max_closure_states, checkpoint_dir=None, checkpoint_every=1_000_000, progress_every=250_000):
    """
    Serial macro closure (verbatim copy of original implementation).
    
    Returns:
        (macro_seen, succ, dist, counters)
    """
    resumed = False
    if checkpoint_dir:
        checkpoint_data = load_checkpoint(checkpoint_dir)
        if checkpoint_data:
            print(f"  Resuming from checkpoint...", flush=True)
            macro_seen, queue, succ, dist, counters, _ = checkpoint_data  # Ignore unprocessed_wave for serial
            print(f"    macro states: {len(macro_seen):,}", flush=True)
            print(f"    queue size: {len(queue):,}", flush=True)
            print(f"    macro edges: {counters['edge_count']:,}", flush=True)
            resumed = True
        else:
            print(f"  No checkpoint found, starting from scratch...", flush=True)
    
    if not resumed:
        macro_seen = set(sources)
        queue = deque(sources)
        succ = {}
        dist = {s: 0 for s in sources}
        counters = {
            'total_intermediate': 0,
            'edge_count': 0,
            'elapsed': 0.0,
            'source_expansions': 0,
            'max_bfs_distance': 0,
        }
    
    start_time = time.perf_counter()
    last_checkpoint_count = len(macro_seen)
    last_progress_count = len(macro_seen)
    
    while queue:
        if len(macro_seen) >= max_closure_states:
            break
        
        src = queue.popleft()
        current_bfs_distance = dist.get(src, 0)
        counters['source_expansions'] += 1
        
        successors = explore_source(src, templates)
        
        if successors:
            succ[src] = successors
            counters['edge_count'] += len(successors)
        
        for s in successors:
            if s not in macro_seen:
                macro_seen.add(s)
                new_dist = dist[src] + 1
                dist[s] = new_dist
                if new_dist > counters['max_bfs_distance']:
                    counters['max_bfs_distance'] = new_dist
                queue.append(s)
        
        if checkpoint_dir and len(macro_seen) - last_checkpoint_count >= checkpoint_every:
            elapsed = time.perf_counter() - start_time + counters['elapsed']
            print(f"\n  checkpoint saved: {len(macro_seen):,} states", flush=True)
            print(f"    elapsed time: {elapsed:.1f}s", flush=True)
            print(f"    queue size: {len(queue):,}", flush=True)
            print(f"    macro edges: {counters['edge_count']:,}", flush=True)
            
            save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed, unprocessed_wave=None)
            last_checkpoint_count = len(macro_seen)
        
        if progress_every > 0 and len(macro_seen) - last_progress_count >= progress_every:
            elapsed = time.perf_counter() - start_time + counters['elapsed']
            states_per_sec = len(macro_seen) / elapsed if elapsed > 0 else 0
            edges_per_sec = counters['edge_count'] / elapsed if elapsed > 0 else 0
            rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
            
            print(f"\n  progress:", flush=True)
            print(f"    macro states = {len(macro_seen):,}", flush=True)
            print(f"    macro edges = {counters['edge_count']:,}", flush=True)
            print(f"    queue size = {len(queue):,}", flush=True)
            print(f"    elapsed = {elapsed:.1f}s", flush=True)
            print(f"    states/sec = {states_per_sec:,.0f}", flush=True)
            print(f"    edges/sec = {edges_per_sec:,.0f}", flush=True)
            print(f"    memory RSS = {rss_mb:,.0f} MB", flush=True)
            print(f"    current BFS distance = {current_bfs_distance}", flush=True)
            print(f"    max BFS distance seen = {counters['max_bfs_distance']}", flush=True)
            print(f"    source expansions = {counters['source_expansions']:,}", flush=True)
            
            last_progress_count = len(macro_seen)
    
    if checkpoint_dir and len(macro_seen) > last_checkpoint_count:
        elapsed = time.perf_counter() - start_time + counters['elapsed']
        print(f"\n  final checkpoint saved: {len(macro_seen):,} states", flush=True)
        save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed)
    
    counters['elapsed'] = time.perf_counter() - start_time + counters['elapsed']
    
    return macro_seen, succ, dist, counters


# ============================================================================
# Parallel macro_closure (new implementation)
# ============================================================================

def macro_closure_parallel(sources, templates, max_closure_states, checkpoint_dir=None, checkpoint_every=1_000_000, progress_every=250_000, workers=1, batch_size=64, wave_size=8192):
    """
    Parallel macro closure with batch-parallel BFS.
    
    Args:
        sources: first-generation sources
        templates: placement templates
        max_closure_states: maximum number of macro states to discover
        checkpoint_dir: directory for checkpoints (None to disable)
        checkpoint_every: checkpoint interval (number of newly discovered states)
        progress_every: progress report interval (number of newly discovered states, 0 to disable)
        workers: number of worker processes (1 = in-process, no pool)
        batch_size: number of sources per batch
        wave_size: number of sources per wave (for pipelining)
    
    Returns:
        (macro_seen, succ, dist, counters)
    """
    resumed = False
    if checkpoint_dir:
        checkpoint_data = load_checkpoint(checkpoint_dir)
        if checkpoint_data:
            print(f"  Resuming from checkpoint...", flush=True)
            macro_seen, queue, succ, dist, counters, _ = checkpoint_data  # Ignore unprocessed_wave
            print(f"    macro states: {len(macro_seen):,}", flush=True)
            print(f"    queue size: {len(queue):,}", flush=True)
            print(f"    macro edges: {counters['edge_count']:,}", flush=True)
            resumed = True
        else:
            print(f"  No checkpoint found, starting from scratch...", flush=True)
    
    if not resumed:
        macro_seen = set(sources)
        queue = deque(sources)
        succ = {}
        dist = {s: 0 for s in sources}
        counters = {
            'total_intermediate': 0,
            'edge_count': 0,
            'elapsed': 0.0,
            'source_expansions': 0,
            'max_bfs_distance': 0,
        }
    
    start_time = time.perf_counter()
    last_checkpoint_count = len(macro_seen)
    last_progress_count = len(macro_seen)
    
    pool = None
    if workers > 1:
        ctx = multiprocessing.get_context("fork")
        pool = ctx.Pool(processes=workers, initializer=_init_worker, initargs=(templates, MAX_INTERMEDIATE))
        print(f"  Created pool with {workers} workers", flush=True)
    else:
        # workers=1: in-process execution, initialize worker globals directly
        _init_worker(templates, MAX_INTERMEDIATE)
    
    try:
        if workers == 1:
            # workers=1: process one source at a time, exactly like serial
            while queue:
                if len(macro_seen) >= max_closure_states:
                    break
                
                src = queue.popleft()
                current_bfs_distance = dist.get(src, 0)
                counters['source_expansions'] += 1
                
                # Explore source using worker function (in-process)
                results = _worker_explore((src,))
                src_result, successors_tuple = results[0]
                
                successors = set(successors_tuple)
                
                if successors:
                    succ[src] = successors
                    counters['edge_count'] += len(successors)
                
                # Iterate over successors in sorted order to ensure deterministic behavior
                # This matches the serial implementation's behavior within a single process
                for s in sorted(successors):
                    if s not in macro_seen:
                        macro_seen.add(s)
                        new_dist = dist[src] + 1
                        dist[s] = new_dist
                        if new_dist > counters['max_bfs_distance']:
                            counters['max_bfs_distance'] = new_dist
                        queue.append(s)
                
                # Checkpoint after each source (matches serial exactly)
                if checkpoint_dir and len(macro_seen) - last_checkpoint_count >= checkpoint_every:
                    elapsed = time.perf_counter() - start_time + counters['elapsed']
                    print(f"\n  checkpoint saved: {len(macro_seen):,} states", flush=True)
                    print(f"    elapsed time: {elapsed:.1f}s", flush=True)
                    print(f"    queue size: {len(queue):,}", flush=True)
                    print(f"    macro edges: {counters['edge_count']:,}", flush=True)
                    
                    save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed, unprocessed_wave=None)
                    last_checkpoint_count = len(macro_seen)
                
                # Progress
                if progress_every > 0 and len(macro_seen) - last_progress_count >= progress_every:
                    elapsed = time.perf_counter() - start_time + counters['elapsed']
                    states_per_sec = len(macro_seen) / elapsed if elapsed > 0 else 0
                    edges_per_sec = counters['edge_count'] / elapsed if elapsed > 0 else 0
                    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
                    
                    print(f"\n  progress:", flush=True)
                    print(f"    macro states = {len(macro_seen):,}", flush=True)
                    print(f"    macro edges = {counters['edge_count']:,}", flush=True)
                    print(f"    queue size = {len(queue):,}", flush=True)
                    print(f"    elapsed = {elapsed:.1f}s", flush=True)
                    print(f"    states/sec = {states_per_sec:,.0f}", flush=True)
                    print(f"    edges/sec = {edges_per_sec:,.0f}", flush=True)
                    print(f"    memory RSS = {rss_mb:,.0f} MB", flush=True)
                    print(f"    current BFS distance = {current_bfs_distance}", flush=True)
                    print(f"    max BFS distance seen = {counters['max_bfs_distance']}", flush=True)
                    print(f"    source expansions = {counters['source_expansions']:,}", flush=True)
                    
                    last_progress_count = len(macro_seen)
        else:
            # workers > 1: use wave-based parallel processing
            while queue:
                if len(macro_seen) >= max_closure_states:
                    break
                
                # Take a wave of sources from the queue
                wave = []
                while queue and len(wave) < wave_size:
                    wave.append(queue.popleft())
                
                # Split wave into batches
                batches = [tuple(wave[i:i+batch_size]) for i in range(0, len(wave), batch_size)]
                
                # Process batches
                results_iter = pool.imap(_worker_explore, batches, chunksize=1)
                
                # Merge results in FIFO order with per-source cap checks
                processed_in_wave = 0
                for results in results_iter:
                    for src, successors_tuple in results:
                        # Cap check before merging (matches serial exactly)
                        if len(macro_seen) >= max_closure_states:
                            break
                        
                        current_bfs_distance = dist.get(src, 0)
                        counters['source_expansions'] += 1
                        
                        successors = set(successors_tuple)
                        
                        if successors:
                            succ[src] = successors
                            counters['edge_count'] += len(successors)
                        
                        # Iterate over successors in sorted order for deterministic queue ordering
                        for s in sorted(successors):
                            if s not in macro_seen:
                                macro_seen.add(s)
                                new_dist = dist[src] + 1
                                dist[s] = new_dist
                                if new_dist > counters['max_bfs_distance']:
                                    counters['max_bfs_distance'] = new_dist
                                queue.append(s)
                        
                        processed_in_wave += 1
                        
                        # Progress
                        if progress_every > 0 and len(macro_seen) - last_progress_count >= progress_every:
                            elapsed = time.perf_counter() - start_time + counters['elapsed']
                            states_per_sec = len(macro_seen) / elapsed if elapsed > 0 else 0
                            edges_per_sec = counters['edge_count'] / elapsed if elapsed > 0 else 0
                            rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
                            rss_children_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024.0
                            
                            print(f"\n  progress:", flush=True)
                            print(f"    macro states = {len(macro_seen):,}", flush=True)
                            print(f"    macro edges = {counters['edge_count']:,}", flush=True)
                            print(f"    queue size = {len(queue):,}", flush=True)
                            print(f"    elapsed = {elapsed:.1f}s", flush=True)
                            print(f"    states/sec = {states_per_sec:,.0f}", flush=True)
                            print(f"    edges/sec = {edges_per_sec:,.0f}", flush=True)
                            print(f"    memory RSS (parent) = {rss_mb:,.0f} MB", flush=True)
                            print(f"    memory RSS (children) = {rss_children_mb:,.0f} MB", flush=True)
                            print(f"    current BFS distance = {current_bfs_distance}", flush=True)
                            print(f"    max BFS distance seen = {counters['max_bfs_distance']}", flush=True)
                            print(f"    source expansions = {counters['source_expansions']:,}", flush=True)
                            
                            last_progress_count = len(macro_seen)
                    
                    # Check if cap was reached during this batch
                    if len(macro_seen) >= max_closure_states:
                        break
                
                # Checkpoint at wave boundary (not in middle of wave)
                if checkpoint_dir and len(macro_seen) - last_checkpoint_count >= checkpoint_every:
                    elapsed = time.perf_counter() - start_time + counters['elapsed']
                    print(f"\n  checkpoint saved: {len(macro_seen):,} states", flush=True)
                    print(f"    elapsed time: {elapsed:.1f}s", flush=True)
                    print(f"    queue size: {len(queue):,}", flush=True)
                    print(f"    macro edges: {counters['edge_count']:,}", flush=True)
                    
                    # At wave boundary, unprocessed_wave is empty
                    save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed, unprocessed_wave=None)
                    last_checkpoint_count = len(macro_seen)
                
                # Check if cap was reached during this wave
                if len(macro_seen) >= max_closure_states:
                    break
    
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    
    # Final checkpoint
    if checkpoint_dir and len(macro_seen) > last_checkpoint_count:
        elapsed = time.perf_counter() - start_time + counters['elapsed']
        print(f"\n  final checkpoint saved: {len(macro_seen):,} states", flush=True)
        save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed, unprocessed_wave=None)
    
    counters['elapsed'] = time.perf_counter() - start_time + counters['elapsed']
    
    return macro_seen, succ, dist, counters


# ============================================================================
# Comparison and benchmarking
# ============================================================================

def compute_distance_histogram(dist):
    """Compute histogram of BFS distances."""
    hist = {}
    for d in dist.values():
        hist[d] = hist.get(d, 0) + 1
    return hist


def compare_results(serial_result, parallel_result, label):
    """Compare serial and parallel results."""
    s_states, s_succ, s_dist, s_counters = serial_result
    p_states, p_succ, p_dist, p_counters = parallel_result
    
    print(f"\n{'=' * 70}", flush=True)
    print(f"CORRECTNESS COMPARISON: {label}", flush=True)
    print(f"{'=' * 70}", flush=True)
    
    # State count
    states_match = len(s_states) == len(p_states)
    print(f"\nMacro states:", flush=True)
    print(f"  Serial:   {len(s_states):,}", flush=True)
    print(f"  Parallel: {len(p_states):,}", flush=True)
    print(f"  Match: {states_match} {'✓' if states_match else '✗'}", flush=True)
    
    # Edge count
    edges_match = s_counters['edge_count'] == p_counters['edge_count']
    print(f"\nMacro edges:", flush=True)
    print(f"  Serial:   {s_counters['edge_count']:,}", flush=True)
    print(f"  Parallel: {p_counters['edge_count']:,}", flush=True)
    print(f"  Match: {edges_match} {'✓' if edges_match else '✗'}", flush=True)
    
    # Source expansions
    expansions_match = s_counters['source_expansions'] == p_counters['source_expansions']
    print(f"\nSource expansions:", flush=True)
    print(f"  Serial:   {s_counters['source_expansions']:,}", flush=True)
    print(f"  Parallel: {p_counters['source_expansions']:,}", flush=True)
    print(f"  Match: {expansions_match} {'✓' if expansions_match else '✗'}", flush=True)
    
    # Max BFS distance
    max_dist_match = s_counters['max_bfs_distance'] == p_counters['max_bfs_distance']
    print(f"\nMax BFS distance:", flush=True)
    print(f"  Serial:   {s_counters['max_bfs_distance']}", flush=True)
    print(f"  Parallel: {p_counters['max_bfs_distance']}", flush=True)
    print(f"  Match: {max_dist_match} {'✓' if max_dist_match else '✗'}", flush=True)
    
    # Distance histogram
    s_hist = compute_distance_histogram(s_dist)
    p_hist = compute_distance_histogram(p_dist)
    hist_match = s_hist == p_hist
    print(f"\nDistance histogram:", flush=True)
    print(f"  Match: {hist_match} {'✓' if hist_match else '✗'}", flush=True)
    if not hist_match:
        print(f"  Serial histogram:   {dict(sorted(s_hist.items()))}", flush=True)
        print(f"  Parallel histogram: {dict(sorted(p_hist.items()))}", flush=True)
    else:
        print(f"  Histogram: {dict(sorted(s_hist.items()))}", flush=True)
    
    # State set comparison (if sizes match)
    if states_match:
        states_identical = s_states == p_states
        print(f"\nState sets identical: {states_identical} {'✓' if states_identical else '✗'}", flush=True)
    else:
        print(f"\nState sets: (skipped, sizes differ)", flush=True)
    
    # Overall
    all_match = states_match and edges_match and expansions_match and max_dist_match and hist_match
    print(f"\n{'=' * 70}", flush=True)
    if all_match:
        print(f"✓✓✓ ALL CHECKS PASSED ✓✓✓", flush=True)
    else:
        print(f"✗✗✗ SOME CHECKS FAILED ✗✗✗", flush=True)
    print(f"{'=' * 70}", flush=True)
    
    return all_match


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Multiprocessing prototype for macro closure BFS")
    parser.add_argument("--mode", choices=["serial", "parallel", "compare"], default="parallel",
                        help="Run mode: serial (baseline), parallel (new), or compare (both)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of worker processes (parallel mode only, default: 1)")
    parser.add_argument("--batch-size", type=int, default=64,
                        help="Number of sources per batch (parallel mode only, default: 64)")
    parser.add_argument("--wave-size", type=int, default=8192,
                        help="Number of sources per wave (parallel mode only, default: 8192)")
    parser.add_argument("--max-closure-states", type=int, default=15_000_000,
                        help="Maximum number of macro states to discover (default: 15M)")
    parser.add_argument("--checkpoint-dir", type=str, default=None,
                        help="Directory for checkpoints (default: None, disabled)")
    parser.add_argument("--checkpoint-every", type=int, default=1_000_000,
                        help="Checkpoint interval in newly discovered states (default: 1M)")
    parser.add_argument("--progress-every", type=int, default=250_000,
                        help="Progress report interval in newly discovered states (default: 250K, 0 to disable)")
    args = parser.parse_args()
    
    print("=" * 70, flush=True)
    print(f"Multiprocessing prototype for macro closure BFS", flush=True)
    print(f"Mode: {args.mode}", flush=True)
    if args.mode in ["parallel", "compare"]:
        print(f"Workers: {args.workers}", flush=True)
        print(f"Batch size: {args.batch_size}", flush=True)
        print(f"Wave size: {args.wave_size}", flush=True)
    print(f"Max closure states: {args.max_closure_states:,}", flush=True)
    print("=" * 70, flush=True)
    
    print("\nBuilding templates...", flush=True)
    t0 = time.perf_counter()
    templates, _ = build_templates()
    t1 = time.perf_counter()
    print(f"  templates built in {t1 - t0:.2f}s", flush=True)
    
    print("\nStep 1: first-generation exploration...", flush=True)
    t2 = time.perf_counter()
    sources = first_generation_sources(templates)
    t3 = time.perf_counter()
    print(f"  sources: {len(sources):,} ({t3 - t2:.1f}s)", flush=True)
    
    if args.mode == "compare":
        # Run serial first
        print(f"\nStep 2a: macro closure (serial baseline)...", flush=True)
        t4 = time.perf_counter()
        serial_result = macro_closure_serial(
            sources,
            templates,
            max_closure_states=args.max_closure_states,
            checkpoint_dir=None,  # No checkpointing for comparison
            progress_every=args.progress_every,
        )
        t5 = time.perf_counter()
        print(f"\nSerial elapsed: {t5 - t4:.2f}s", flush=True)
        
        # Run parallel
        print(f"\nStep 2b: macro closure (parallel, workers={args.workers})...", flush=True)
        t6 = time.perf_counter()
        parallel_result = macro_closure_parallel(
            sources,
            templates,
            max_closure_states=args.max_closure_states,
            checkpoint_dir=None,  # No checkpointing for comparison
            progress_every=args.progress_every,
            workers=args.workers,
            batch_size=args.batch_size,
            wave_size=args.wave_size,
        )
        t7 = time.perf_counter()
        print(f"\nParallel elapsed: {t7 - t6:.2f}s", flush=True)
        
        # Compare
        all_match = compare_results(serial_result, parallel_result, f"workers={args.workers}")
        
        # Performance summary
        s_states, s_succ, s_dist, s_counters = serial_result
        p_states, p_succ, p_dist, p_counters = parallel_result
        
        print(f"\n{'=' * 70}", flush=True)
        print(f"PERFORMANCE SUMMARY", flush=True)
        print(f"{'=' * 70}", flush=True)
        print(f"\nSerial:", flush=True)
        print(f"  Wall time: {t5 - t4:.2f}s", flush=True)
        print(f"  States/sec: {len(s_states) / (t5 - t4):,.0f}", flush=True)
        print(f"  Edges/sec: {s_counters['edge_count'] / (t5 - t4):,.0f}", flush=True)
        
        print(f"\nParallel (workers={args.workers}):", flush=True)
        print(f"  Wall time: {t7 - t6:.2f}s", flush=True)
        print(f"  States/sec: {len(p_states) / (t7 - t6):,.0f}", flush=True)
        print(f"  Edges/sec: {p_counters['edge_count'] / (t7 - t6):,.0f}", flush=True)
        
        speedup = (t5 - t4) / (t7 - t6) if (t7 - t6) > 0 else 0
        print(f"\nSpeedup: {speedup:.2f}x", flush=True)
        
        return 0 if all_match else 1
    
    else:
        # Single mode (serial or parallel)
        print(f"\nStep 2: macro closure ({args.mode})...", flush=True)
        t4 = time.perf_counter()
        
        if args.mode == "serial":
            macro_states, succ, dist, counters = macro_closure_serial(
                sources,
                templates,
                max_closure_states=args.max_closure_states,
                checkpoint_dir=args.checkpoint_dir,
                checkpoint_every=args.checkpoint_every,
                progress_every=args.progress_every,
            )
        else:
            macro_states, succ, dist, counters = macro_closure_parallel(
                sources,
                templates,
                max_closure_states=args.max_closure_states,
                checkpoint_dir=args.checkpoint_dir,
                checkpoint_every=args.checkpoint_every,
                progress_every=args.progress_every,
                workers=args.workers,
                batch_size=args.batch_size,
                wave_size=args.wave_size,
            )
        
        t5 = time.perf_counter()
        
        print(f"\n{'=' * 70}", flush=True)
        print(f"RESULTS ({args.mode})", flush=True)
        print(f"{'=' * 70}", flush=True)
        print(f"Macro states: {len(macro_states):,}", flush=True)
        print(f"Macro edges: {counters['edge_count']:,}", flush=True)
        print(f"Source expansions: {counters['source_expansions']:,}", flush=True)
        print(f"Max BFS distance: {counters['max_bfs_distance']}", flush=True)
        print(f"Elapsed: {counters['elapsed']:.2f}s", flush=True)
        print(f"Wall time: {t5 - t4:.2f}s", flush=True)
        
        states_per_sec = len(macro_states) / counters['elapsed'] if counters['elapsed'] > 0 else 0
        edges_per_sec = counters['edge_count'] / counters['elapsed'] if counters['elapsed'] > 0 else 0
        print(f"States/sec: {states_per_sec:,.0f}", flush=True)
        print(f"Edges/sec: {edges_per_sec:,.0f}", flush=True)
        
        rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        rss_children_mb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024.0
        print(f"Peak RSS (parent): {rss_mb:,.0f} MB", flush=True)
        print(f"Peak RSS (children): {rss_children_mb:,.0f} MB", flush=True)
        
        # Distance histogram
        dist_hist = compute_distance_histogram(dist)
        print(f"\nDistance histogram:", flush=True)
        for d in sorted(dist_hist.keys()):
            print(f"  d={d}: {dist_hist[d]:,} states", flush=True)
        
        print(f"\n{'=' * 70}", flush=True)
        
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
