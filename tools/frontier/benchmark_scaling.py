#!/usr/bin/env python3
"""
Comprehensive benchmark for multiprocessing macro closure.

Runs benchmarks at 1M, 5M, 10M states with serial, workers=1, 2, 4.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_benchmark(mode, workers, max_states, label):
    """Run a single benchmark and return metrics."""
    cmd = [
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", mode,
        "--max-closure-states", str(max_states),
        "--progress-every", "0",
    ]
    
    if mode == "parallel":
        cmd.extend(["--workers", str(workers)])
    
    print(f"\n{'='*70}", flush=True)
    print(f"{label}", flush=True)
    print(f"Command: {' '.join(cmd)}", flush=True)
    print(f"{'='*70}", flush=True)
    
    start = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    
    print(result.stdout)
    
    # Extract metrics
    metrics = {'wall_time': elapsed}
    for line in result.stdout.split('\n'):
        if 'Macro states:' in line and 'checkpoint' not in line:
            metrics['macro_states'] = int(line.split(':')[1].strip().replace(',', ''))
        elif 'Macro edges:' in line and 'checkpoint' not in line:
            metrics['macro_edges'] = int(line.split(':')[1].strip().replace(',', ''))
        elif 'Source expansions:' in line:
            metrics['source_expansions'] = int(line.split(':')[1].strip().replace(',', ''))
        elif 'Max BFS distance:' in line:
            metrics['max_bfs_distance'] = int(line.split(':')[1].strip())
        elif 'Elapsed:' in line:
            metrics['elapsed'] = float(line.split(':')[1].strip().replace('s', ''))
        elif 'Peak RSS (parent):' in line:
            metrics['rss_parent_mb'] = float(line.split(':')[1].strip().replace('MB', '').replace(',', '').strip())
        elif 'Peak RSS (children):' in line:
            metrics['rss_children_mb'] = float(line.split(':')[1].strip().replace('MB', '').replace(',', '').strip())
    
    return metrics

def main():
    benchmarks = [
        # 1M states
        ("serial", None, 1_000_000, "1M Serial"),
        ("parallel", 1, 1_000_000, "1M Parallel workers=1"),
        ("parallel", 2, 1_000_000, "1M Parallel workers=2"),
        ("parallel", 4, 1_000_000, "1M Parallel workers=4"),
        
        # 5M states
        ("serial", None, 5_000_000, "5M Serial"),
        ("parallel", 1, 5_000_000, "5M Parallel workers=1"),
        ("parallel", 2, 5_000_000, "5M Parallel workers=2"),
        ("parallel", 4, 5_000_000, "5M Parallel workers=4"),
        
        # 10M states
        ("serial", None, 10_000_000, "10M Serial"),
        ("parallel", 1, 10_000_000, "10M Parallel workers=1"),
        ("parallel", 2, 10_000_000, "10M Parallel workers=2"),
        ("parallel", 4, 10_000_000, "10M Parallel workers=4"),
    ]
    
    results = []
    
    for mode, workers, max_states, label in benchmarks:
        metrics = run_benchmark(mode, workers, max_states, label)
        metrics['label'] = label
        metrics['mode'] = mode
        metrics['workers'] = workers
        metrics['max_states'] = max_states
        results.append(metrics)
    
    # Print summary table
    print("\n\n" + "="*100)
    print("BENCHMARK SUMMARY")
    print("="*100)
    
    for max_states in [1_000_000, 5_000_000, 10_000_000]:
        print(f"\n{'='*100}")
        print(f"MAX STATES: {max_states:,}")
        print(f"{'='*100}")
        print(f"{'Configuration':<30} {'States':>12} {'Edges':>12} {'Time(s)':>10} {'States/s':>12} {'RSS Parent':>12} {'RSS Child':>12}")
        print("-"*100)
        
        baseline_time = None
        for r in results:
            if r['max_states'] == max_states:
                label = r['label']
                states = r.get('macro_states', 0)
                edges = r.get('macro_edges', 0)
                elapsed = r.get('elapsed', 0)
                states_per_sec = states / elapsed if elapsed > 0 else 0
                rss_parent = r.get('rss_parent_mb', 0)
                rss_children = r.get('rss_children_mb', 0)
                
                if r['mode'] == 'serial':
                    baseline_time = elapsed
                
                speedup = baseline_time / elapsed if baseline_time and elapsed > 0 else 1.0
                
                print(f"{label:<30} {states:>12,} {edges:>12,} {elapsed:>10.2f} {states_per_sec:>12,.0f} {rss_parent:>10.0f}MB {rss_children:>10.0f}MB  ({speedup:.2f}x)")
    
    # Write results to file
    output_file = Path("/tmp/opencode/benchmark_results.txt")
    with open(output_file, 'w') as f:
        f.write("Benchmark Results\n")
        f.write("="*100 + "\n\n")
        
        for r in results:
            f.write(f"{r['label']}\n")
            for key, value in r.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
    
    print(f"\n\nResults written to {output_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
