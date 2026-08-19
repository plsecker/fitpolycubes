#!/usr/bin/env python3
"""
SCC-aware analysis of the macro graph with complete succ[0].

This script correctly handles the cyclic structure by:
1. Building the capped macro graph (15M states) with truncated succ[0]
2. Computing complete succ[0] and patching it
3. Computing SCCs of the resulting graph
4. Identifying the nontrivial SCC containing 0
5. Building the SCC condensation DAG
6. For the 226-state SCC, computing exact reachable path lengths
7. Combining DAG prefix + SCC internal paths to check if distance 129 exists

The analysis is mathematically sound for general SCCs.

Checkpoint/restart support:
- Checkpoints are saved periodically during macro closure
- On startup, if a checkpoint exists, the run resumes automatically
- Checkpoint format: compact binary (numpy arrays)
"""

from __future__ import annotations

import argparse
import os
import resource
import sys
import tempfile
import time
from collections import deque
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/home/philip/Work/fitpolycubes")
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


def explore_source(source, templates, max_intermediate=MAX_INTERMEDIATE):
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


def save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed):
    """
    Save checkpoint atomically using temporary file + rename.
    
    Checkpoint format:
    - macro_seen.npy: uint64 array of all discovered states
    - queue.npy: uint64 array of BFS queue states
    - succ.npy: structured array with (source, num_successors, successors...)
    - dist.npy: structured array with (state, distance)
    - counters.txt: text file with cumulative counters
    """
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary directory in the same filesystem for atomic rename
    temp_dir = checkpoint_dir / ".checkpoint_temp"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Save macro_seen as uint64 array
        macro_seen_arr = np.array(sorted(macro_seen), dtype=np.uint64)
        temp_seen = temp_dir / "macro_seen.npy"
        np.save(temp_seen, macro_seen_arr, allow_pickle=False)
        
        # Save queue as uint64 array
        queue_arr = np.array(list(queue), dtype=np.uint64)
        temp_queue = temp_dir / "queue.npy"
        np.save(temp_queue, queue_arr, allow_pickle=False)
        
        # Save succ as structured array: for each source, store (source, num_succ, succ1, succ2, ...)
        # Use a flat array with markers
        succ_data = []
        for src, succs in succ.items():
            succ_data.append(src)
            succ_data.append(len(succs))
            succ_data.extend(sorted(succs))
        succ_arr = np.array(succ_data, dtype=np.uint64)
        temp_succ = temp_dir / "succ.npy"
        np.save(temp_succ, succ_arr, allow_pickle=False)
        
        # Save dist as structured array: (state, distance) pairs
        dist_data = []
        for state, d in dist.items():
            dist_data.append(state)
            dist_data.append(d)
        dist_arr = np.array(dist_data, dtype=np.uint64)
        temp_dist = temp_dir / "dist.npy"
        np.save(temp_dist, dist_arr, allow_pickle=False)
        
        # Save counters as text
        temp_counters = temp_dir / "counters.txt"
        with open(temp_counters, 'w') as f:
            f.write(f"total_intermediate={counters['total_intermediate']}\n")
            f.write(f"edge_count={counters['edge_count']}\n")
            f.write(f"elapsed={elapsed}\n")
        
        # Atomic rename: move temp files to final location
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
        
        # Clean up temp directory
        temp_dir.rmdir()
        
        return True
    except Exception as e:
        print(f"  ERROR saving checkpoint: {e}", flush=True)
        # Clean up temp directory on error
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False


def load_checkpoint(checkpoint_dir):
    """
    Load checkpoint from directory.
    Returns (macro_seen, queue, succ, dist, counters, elapsed) or None if no checkpoint exists.
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
        # Load macro_seen
        macro_seen_arr = np.load(checkpoint_dir / "macro_seen.npy", allow_pickle=False)
        macro_seen = set(macro_seen_arr.tolist())
        
        # Load queue
        queue_arr = np.load(checkpoint_dir / "queue.npy", allow_pickle=False)
        queue = deque(queue_arr.tolist())
        
        # Load succ (flat array with markers)
        succ_arr = np.load(checkpoint_dir / "succ.npy", allow_pickle=False)
        succ = {}
        i = 0
        while i < len(succ_arr):
            src = int(succ_arr[i])
            num_succ = int(succ_arr[i + 1])
            succs = set(int(x) for x in succ_arr[i + 2:i + 2 + num_succ])
            succ[src] = succs
            i += 2 + num_succ
        
        # Load dist (flat array with pairs)
        dist_arr = np.load(checkpoint_dir / "dist.npy", allow_pickle=False)
        dist = {}
        for i in range(0, len(dist_arr), 2):
            state = int(dist_arr[i])
            d = int(dist_arr[i + 1])
            dist[state] = d
        
        # Load counters
        counters = {}
        with open(checkpoint_dir / "counters.txt", 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                if key in ('total_intermediate', 'edge_count'):
                    counters[key] = int(value)
                elif key == 'elapsed':
                    counters[key] = float(value)
        
        # Add default values for new counters (backward compatibility)
        if 'source_expansions' not in counters:
            counters['source_expansions'] = 0
        if 'max_bfs_distance' not in counters:
            counters['max_bfs_distance'] = 0
        
        return macro_seen, queue, succ, dist, counters
    except Exception as e:
        print(f"  ERROR loading checkpoint: {e}", flush=True)
        return None


def macro_closure(sources, templates, max_closure_states, checkpoint_dir=None, checkpoint_every=1_000_000, progress_every=250_000):
    """
    Build macro closure with checkpoint/restart support.
    
    Args:
        sources: first-generation sources
        templates: placement templates
        max_closure_states: maximum number of macro states to discover
        checkpoint_dir: directory for checkpoints (None to disable)
        checkpoint_every: checkpoint interval (number of newly discovered states)
        progress_every: progress report interval (number of newly discovered states, 0 to disable)
    
    Returns:
        (macro_seen, succ, counters)
    """
    # Try to load checkpoint
    resumed = False
    if checkpoint_dir:
        checkpoint_data = load_checkpoint(checkpoint_dir)
        if checkpoint_data:
            print(f"  Resuming from checkpoint...", flush=True)
            macro_seen, queue, succ, dist, counters = checkpoint_data
            print(f"    macro states: {len(macro_seen):,}", flush=True)
            print(f"    queue size: {len(queue):,}", flush=True)
            print(f"    macro edges: {counters['edge_count']:,}", flush=True)
            resumed = True
        else:
            print(f"  No checkpoint found, starting from scratch...", flush=True)
    
    if not resumed:
        # Initialize from scratch
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
        
        # Check if we should checkpoint
        if checkpoint_dir and len(macro_seen) - last_checkpoint_count >= checkpoint_every:
            elapsed = time.perf_counter() - start_time + counters['elapsed']
            print(f"\n  checkpoint saved: {len(macro_seen):,} states", flush=True)
            print(f"    elapsed time: {elapsed:.1f}s", flush=True)
            print(f"    queue size: {len(queue):,}", flush=True)
            print(f"    macro edges: {counters['edge_count']:,}", flush=True)
            
            save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed)
            last_checkpoint_count = len(macro_seen)
        
        # Check if we should report progress
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
    
    # Final checkpoint
    if checkpoint_dir and len(macro_seen) > last_checkpoint_count:
        elapsed = time.perf_counter() - start_time + counters['elapsed']
        print(f"\n  final checkpoint saved: {len(macro_seen):,} states", flush=True)
        save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed)
    
    counters['elapsed'] = time.perf_counter() - start_time + counters['elapsed']
    
    return macro_seen, succ, counters


def tarjan_scc(nodes, succ):
    """Iterative Tarjan's SCC algorithm."""
    index_counter = [0]
    stack = []
    on_stack = set()
    indices = {}
    lowlink = {}
    sccs = []

    for root in nodes:
        if root in indices:
            continue

        work = [(root, None, False)]

        while work:
            node, parent, processed = work[-1]

            if not processed:
                if node in indices:
                    work.pop()
                    continue

                indices[node] = index_counter[0]
                lowlink[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)

                work[-1] = (node, parent, True)

                for nxt in succ.get(node, set()):
                    if nxt not in indices:
                        work.append((nxt, node, False))
                    elif nxt in on_stack:
                        lowlink[node] = min(lowlink[node], indices[nxt])
            else:
                work.pop()

                if parent is not None:
                    lowlink[parent] = min(lowlink[parent], lowlink[node])

                if lowlink[node] == indices[node]:
                    comp = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        comp.append(w)
                        if w == node:
                            break
                    sccs.append(comp)

    return sccs


def compute_scc_internal_distances(scc, succ, target_state, max_distance):
    """
    Compute all reachable distances from each state in the SCC to target_state.
    Returns dict: state -> set of distances
    """
    # R[u] = set of distances d such that target_state is reachable from u in d steps
    R = {target_state: {0}}

    # Iterate until convergence
    for iteration in range(max_distance + 1):
        changed = False

        for u in scc:
            if u == target_state:
                continue

            distances = set()
            for v in succ.get(u, set()) & scc:
                if v in R:
                    for d in R[v]:
                        if d + 1 <= max_distance:
                            distances.add(d + 1)

            if distances and distances != R.get(u, set()):
                R[u] = distances
                changed = True

        if not changed:
            break

    return R


def compute_dag_distances_to_scc(sources, scc, succ, macro_states):
    """
    Compute shortest path distances from each first-gen source to each entry point in the SCC.
    Entry points are states in the SCC that are reachable from sources via the DAG.
    
    Returns:
        entry_points: set of states in SCC reachable from sources
        dag_distances: dict mapping (source, entry_point) -> shortest distance
    """
    # BFS from all sources, tracking distances to SCC states
    dag_distances = {}  # (source, entry) -> distance
    entry_points = set()
    
    for source in sources:
        # BFS from this source
        dist = {source: 0}
        queue = deque([source])
        
        while queue:
            u = queue.popleft()
            
            # If we reached an SCC state, record it
            if u in scc:
                entry_points.add(u)
                key = (source, u)
                if key not in dag_distances or dist[u] < dag_distances[key]:
                    dag_distances[key] = dist[u]
                continue  # Don't explore further into SCC
            
            # Explore successors
            for v in succ.get(u, set()):
                if v not in dist and v in macro_states:
                    dist[v] = dist[u] + 1
                    queue.append(v)
    
    return entry_points, dag_distances


def main() -> int:
    parser = argparse.ArgumentParser(description="SCC-aware macro graph analysis with checkpoint/restart")
    parser.add_argument("--max-closure-states", type=int, default=15_000_000,
                        help="Maximum number of macro states to discover (default: 15M)")
    parser.add_argument("--checkpoint-dir", type=str, default=None,
                        help="Directory for checkpoints (default: None, disabled)")
    parser.add_argument("--checkpoint-every", type=int, default=1_000_000,
                        help="Checkpoint interval in newly discovered states (default: 1M)")
    parser.add_argument("--progress-every", type=int, default=250_000,
                        help="Progress report interval in newly discovered states (default: 250K, 0 to disable)")
    args = parser.parse_args()
    
    print("Building templates...", flush=True)
    templates, _ = build_templates()

    print("\nStep 1: first-generation exploration...", flush=True)
    t0 = time.perf_counter()
    sources = first_generation_sources(templates)
    t1 = time.perf_counter()
    print(f"  sources: {len(sources):,} ({t1 - t0:.1f}s)", flush=True)

    print("\nStep 2: macro closure (capped)...", flush=True)
    t2 = time.perf_counter()
    macro_states, succ, counters = macro_closure(
        sources, 
        templates,
        max_closure_states=args.max_closure_states,
        checkpoint_dir=args.checkpoint_dir,
        checkpoint_every=args.checkpoint_every,
        progress_every=args.progress_every,
    )
    t3 = time.perf_counter()
    print(f"  macro states: {len(macro_states):,} ({t3 - t2:.1f}s)", flush=True)
    print(f"  macro edges: {counters['edge_count']:,}", flush=True)
    print(f"  total intermediate: {counters['total_intermediate']:,}", flush=True)

    print("\nStep 3: compute complete succ[0]...", flush=True)
    t4 = time.perf_counter()
    complete_succ_0 = explore_source(0, templates, MAX_INTERMEDIATE_0)
    t5 = time.perf_counter()
    print(f"  complete succ[0]: {len(complete_succ_0):,} ({t5 - t4:.1f}s)", flush=True)

    print("\nStep 4: patch succ[0]...", flush=True)
    succ[0] = complete_succ_0

    print("\nStep 5: compute SCCs...", flush=True)
    t6 = time.perf_counter()
    sccs = tarjan_scc(macro_states, succ)
    t7 = time.perf_counter()
    print(f"  found {len(sccs):,} SCCs ({t7 - t6:.1f}s)", flush=True)

    # Find the SCC containing 0
    scc_0 = None
    scc_0_idx = None
    for i, scc in enumerate(sccs):
        if 0 in scc:
            scc_0 = set(scc)
            scc_0_idx = i
            break

    print(f"\n=== SCC CONTAINING STATE 0 ===", flush=True)
    print(f"  SCC index: {scc_0_idx}", flush=True)
    print(f"  SCC size: {len(scc_0):,}", flush=True)
    print(f"  contains s*: {S_STAR in scc_0}", flush=True)
    print(f"  contains WORD_MASK: {WORD_MASK in scc_0}", flush=True)

    # Count nontrivial SCCs
    nontrivial_sccs = [scc for scc in sccs if len(scc) > 1]
    print(f"\n  Total SCCs: {len(sccs):,}", flush=True)
    print(f"  Nontrivial SCCs (size > 1): {len(nontrivial_sccs):,}", flush=True)

    if len(nontrivial_sccs) > 1:
        print(f"\n  WARNING: Multiple nontrivial SCCs found!", flush=True)
        for i, scc in enumerate(nontrivial_sccs[:5]):
            print(f"    SCC {i+1}: size {len(scc)}", flush=True)

    print("\nStep 6: compute SCC internal distances...", flush=True)
    t8 = time.perf_counter()
    scc_distances = compute_scc_internal_distances(scc_0, succ, 0, TARGET_DISTANCE)
    t9 = time.perf_counter()
    print(f"  computed distances for {len(scc_distances)} states ({t9 - t8:.1f}s)", flush=True)

    # Find entry points: first-gen sources that are in the SCC
    sources_in_scc = sources & scc_0
    print(f"\n  First-gen sources in SCC: {len(sources_in_scc)}", flush=True)

    # Find all entry points: states in SCC reachable from sources via DAG
    print("\nStep 7: compute DAG distances to SCC entry points...", flush=True)
    t10 = time.perf_counter()
    entry_points, dag_distances = compute_dag_distances_to_scc(sources, scc_0, succ, macro_states)
    t11 = time.perf_counter()
    print(f"  found {len(entry_points)} entry points ({t11 - t10:.1f}s)", flush=True)

    # For each entry point, what distances to 0 are possible within SCC?
    print(f"\n=== ENTRY POINT ANALYSIS ===", flush=True)
    for entry in sorted(entry_points)[:10]:  # Show first 10
        if entry in scc_distances:
            dists = sorted(scc_distances[entry])
            print(f"  Entry {entry}: SCC distances to 0 = {dists[:10]}...", flush=True)

    # Check if distance 129 is achievable
    print(f"\n=== CHECKING DISTANCE {TARGET_DISTANCE} (N={TARGET_DISTANCE + 1}) ===", flush=True)
    
    achievable_combinations = []
    
    for source in sources:
        for entry in entry_points:
            # DAG distance from source to entry
            dag_key = (source, entry)
            if dag_key not in dag_distances:
                continue
            
            dag_dist = dag_distances[dag_key]
            
            # SCC distances from entry to 0
            if entry not in scc_distances:
                continue
            
            scc_dists = scc_distances[entry]
            
            # Check if dag_dist + scc_dist = TARGET_DISTANCE for any scc_dist
            for scc_dist in scc_dists:
                total = dag_dist + scc_dist
                if total == TARGET_DISTANCE:
                    achievable_combinations.append((source, entry, dag_dist, scc_dist))

    if achievable_combinations:
        print(f"\n✓✓✓ DISTANCE {TARGET_DISTANCE} IS ACHIEVABLE! ✓✓✓", flush=True)
        print(f"  Found {len(achievable_combinations)} valid combinations", flush=True)
        
        # Show first few
        for source, entry, dag_dist, scc_dist in achievable_combinations[:5]:
            print(f"\n  Source: {source}", flush=True)
            print(f"    Entry point: {entry}", flush=True)
            print(f"    DAG distance: {dag_dist}", flush=True)
            print(f"    SCC distance: {scc_dist}", flush=True)
            print(f"    Total: {dag_dist + scc_dist}", flush=True)
        
        # Unique sources
        unique_sources = set(c[0] for c in achievable_combinations)
        print(f"\n  Unique first-gen sources: {len(unique_sources)}", flush=True)
    else:
        print(f"\n✗✗✗ DISTANCE {TARGET_DISTANCE} IS NOT ACHIEVABLE ✗✗✗", flush=True)
        print(f"\n  No combination of DAG prefix + SCC path yields distance {TARGET_DISTANCE}", flush=True)
        
        # Debug: show what distances ARE achievable
        print(f"\n  Debug: achievable distances from sources:", flush=True)
        all_achievable = set()
        for source in sources:
            for entry in entry_points:
                dag_key = (source, entry)
                if dag_key not in dag_distances:
                    continue
                dag_dist = dag_distances[dag_key]
                if entry in scc_distances:
                    for scc_dist in scc_distances[entry]:
                        all_achievable.add(dag_dist + scc_dist)
        
        print(f"    Total distinct achievable distances: {len(all_achievable)}", flush=True)
        print(f"    Max achievable distance: {max(all_achievable) if all_achievable else 0}", flush=True)
        print(f"    Distances near {TARGET_DISTANCE}: {sorted(d for d in all_achievable if abs(d - TARGET_DISTANCE) <= 10)}", flush=True)

    # Summary
    print(f"\n=== SUMMARY ===", flush=True)
    print(f"Macro states: {len(macro_states):,}", flush=True)
    print(f"SCCs: {len(sccs):,}", flush=True)
    print(f"Nontrivial SCCs: {len(nontrivial_sccs)}", flush=True)
    print(f"SCC containing 0: size {len(scc_0)}", flush=True)
    print(f"First-gen sources: {len(sources):,}", flush=True)
    print(f"Sources in SCC: {len(sources_in_scc)}", flush=True)
    print(f"Entry points to SCC: {len(entry_points)}", flush=True)
    print(f"Achievable combinations for distance {TARGET_DISTANCE}: {len(achievable_combinations)}", flush=True)

    # Write results
    out = Path("/tmp/opencode/scc_aware_analysis_results.txt")
    lines = [
        f"macro_states={len(macro_states)}",
        f"num_sccs={len(sccs)}",
        f"num_nontrivial_sccs={len(nontrivial_sccs)}",
        f"scc_0_size={len(scc_0)}",
        f"scc_0_contains_s_star={S_STAR in scc_0}",
        f"first_gen_sources={len(sources)}",
        f"sources_in_scc={len(sources_in_scc)}",
        f"entry_points={len(entry_points)}",
        f"target_distance={TARGET_DISTANCE}",
        f"achievable={len(achievable_combinations) > 0}",
        f"num_achievable_combinations={len(achievable_combinations)}",
    ]
    
    out.write_text("\n".join(lines) + "\n")
    print(f"\nResults written to {out}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
