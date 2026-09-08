#!/usr/bin/env python3
"""
Focused test for parallel checkpoint/restart correctness.
"""

import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, label):
    """Run a command and return output."""
    print(f"\n{'='*70}", flush=True)
    print(f"{label}", flush=True)
    print(f"Command: {' '.join(cmd)}", flush=True)
    print(f"{'='*70}", flush=True)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    
    return result.stdout

def extract_metrics(output):
    """Extract key metrics from output."""
    metrics = {}
    for line in output.split('\n'):
        if 'Macro states:' in line and 'checkpoint' not in line:
            metrics['macro_states'] = int(line.split(':')[1].strip().replace(',', ''))
        elif 'Macro edges:' in line and 'checkpoint' not in line:
            metrics['macro_edges'] = int(line.split(':')[1].strip().replace(',', ''))
        elif 'Source expansions:' in line:
            metrics['source_expansions'] = int(line.split(':')[1].strip().replace(',', ''))
        elif 'Max BFS distance:' in line:
            metrics['max_bfs_distance'] = int(line.split(':')[1].strip())
        elif line.strip().startswith('d='):
            parts = line.strip().split(':')
            d = int(parts[0].replace('d=', ''))
            count = int(parts[1].strip().replace(',', '').replace(' states', ''))
            if 'dist_hist' not in metrics:
                metrics['dist_hist'] = {}
            metrics['dist_hist'][d] = count
    
    return metrics

def main():
    checkpoint_dir_500k = Path("/tmp/mp_checkpoint_500k")
    checkpoint_dir_resume = Path("/tmp/mp_checkpoint_resume")
    
    if checkpoint_dir_500k.exists():
        shutil.rmtree(checkpoint_dir_500k)
    if checkpoint_dir_resume.exists():
        shutil.rmtree(checkpoint_dir_resume)
    
    print("="*70)
    print("PARALLEL CHECKPOINT/RESTART DEBUG TEST")
    print("="*70)
    
    # Test 1: Fresh parallel run to 500K with checkpoint
    print("\n\n### TEST 1: Fresh parallel run to 500K ###")
    output1 = run_command([
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", "parallel",
        "--workers", "2",
        "--max-closure-states", "500000",
        "--checkpoint-dir", str(checkpoint_dir_500k),
        "--checkpoint-every", "250000",
        "--progress-every", "0",
    ], "Fresh parallel run to 500K")
    
    metrics1 = extract_metrics(output1)
    print(f"\nMetrics: {metrics1}")
    
    # Check checkpoint files
    print(f"\nCheckpoint files at 500K:")
    for f in sorted(checkpoint_dir_500k.glob("*")):
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
    
    # Test 2: Resume from checkpoint to 1M (use different checkpoint dir)
    print("\n\n### TEST 2: Resume from checkpoint to 1M ###")
    output2 = run_command([
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", "parallel",
        "--workers", "2",
        "--max-closure-states", "1000000",
        "--checkpoint-dir", str(checkpoint_dir_resume),
        "--checkpoint-every", "250000",
        "--progress-every", "0",
    ], "Resume parallel from 500K checkpoint to 1M")
    
    metrics2 = extract_metrics(output2)
    print(f"\nMetrics: {metrics2}")
    
    # Test 3: Fresh parallel run to 1M (no checkpoint)
    print("\n\n### TEST 3: Fresh parallel run to 1M (baseline) ###")
    output3 = run_command([
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", "parallel",
        "--workers", "2",
        "--max-closure-states", "1000000",
        "--progress-every", "0",
    ], "Fresh parallel run to 1M (baseline)")
    
    metrics3 = extract_metrics(output3)
    print(f"\nMetrics: {metrics3}")
    
    # Compare
    print("\n\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    
    print(f"\nResumed run (Test 2):")
    print(f"  Macro states: {metrics2.get('macro_states', 'N/A'):,}")
    print(f"  Macro edges: {metrics2.get('macro_edges', 'N/A'):,}")
    print(f"  Source expansions: {metrics2.get('source_expansions', 'N/A'):,}")
    print(f"  Max BFS distance: {metrics2.get('max_bfs_distance', 'N/A')}")
    
    print(f"\nFresh run (Test 3):")
    print(f"  Macro states: {metrics3.get('macro_states', 'N/A'):,}")
    print(f"  Macro edges: {metrics3.get('macro_edges', 'N/A'):,}")
    print(f"  Source expansions: {metrics3.get('source_expansions', 'N/A'):,}")
    print(f"  Max BFS distance: {metrics3.get('max_bfs_distance', 'N/A')}")
    
    print(f"\nDistance histogram comparison:")
    if 'dist_hist' in metrics2 and 'dist_hist' in metrics3:
        all_dists = sorted(set(metrics2['dist_hist'].keys()) | set(metrics3['dist_hist'].keys()))
        for d in all_dists:
            resumed = metrics2['dist_hist'].get(d, 0)
            fresh = metrics3['dist_hist'].get(d, 0)
            match = "✓" if resumed == fresh else "✗"
            print(f"  d={d:2d}: resumed={resumed:7,d}  fresh={fresh:7,d}  {match}")
    
    match = (
        metrics2.get('macro_states') == metrics3.get('macro_states') and
        metrics2.get('macro_edges') == metrics3.get('macro_edges') and
        metrics2.get('source_expansions') == metrics3.get('source_expansions') and
        metrics2.get('max_bfs_distance') == metrics3.get('max_bfs_distance') and
        metrics2.get('dist_hist') == metrics3.get('dist_hist')
    )
    
    print(f"\n{'='*70}")
    if match:
        print("✓✓✓ CHECKPOINT/RESTART CORRECT ✓✓✓")
    else:
        print("✗✗✗ CHECKPOINT/RESTART INCORRECT ✗✗✗")
    print(f"{'='*70}")
    
    return 0 if match else 1

if __name__ == "__main__":
    sys.exit(main())
