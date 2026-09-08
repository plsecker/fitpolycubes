#!/usr/bin/env python3
"""
Debug test for parallel checkpoint/restart.
"""

import shutil
import subprocess
import sys
from pathlib import Path

def main():
    checkpoint_dir = Path("/tmp/mp_checkpoint_debug_simple")
    
    if checkpoint_dir.exists():
        shutil.rmtree(checkpoint_dir)
    
    # Run 1: Fresh parallel to 250K with checkpoint
    print("="*70)
    print("RUN 1: Fresh parallel to 250K")
    print("="*70)
    result1 = subprocess.run([
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", "parallel",
        "--workers", "2",
        "--max-closure-states", "250000",
        "--checkpoint-dir", str(checkpoint_dir),
        "--checkpoint-every", "100000",
        "--progress-every", "0",
    ], capture_output=True, text=True)
    print(result1.stdout)
    
    # Check checkpoint
    print("\n" + "="*70)
    print("CHECKPOINT STATE")
    print("="*70)
    for f in sorted(checkpoint_dir.glob("*")):
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
    
    # Run 2: Resume from checkpoint to 500K
    print("\n" + "="*70)
    print("RUN 2: Resume from checkpoint to 500K")
    print("="*70)
    result2 = subprocess.run([
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", "parallel",
        "--workers", "2",
        "--max-closure-states", "500000",
        "--checkpoint-dir", str(checkpoint_dir),
        "--checkpoint-every", "100000",
        "--progress-every", "0",
    ], capture_output=True, text=True)
    print(result2.stdout)
    
    # Run 3: Fresh parallel to 500K (baseline)
    print("\n" + "="*70)
    print("RUN 3: Fresh parallel to 500K (baseline)")
    print("="*70)
    result3 = subprocess.run([
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis_mp.py",
        "--mode", "parallel",
        "--workers", "2",
        "--max-closure-states", "500000",
        "--progress-every", "0",
    ], capture_output=True, text=True)
    print(result3.stdout)
    
    # Compare
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    
    def extract_metric(output, key):
        for line in output.split('\n'):
            if key in line and 'checkpoint' not in line:
                return int(line.split(':')[1].strip().replace(',', ''))
        return None
    
    resumed_states = extract_metric(result2.stdout, "Macro states:")
    fresh_states = extract_metric(result3.stdout, "Macro states:")
    resumed_edges = extract_metric(result2.stdout, "Macro edges:")
    fresh_edges = extract_metric(result3.stdout, "Macro edges:")
    resumed_expansions = extract_metric(result2.stdout, "Source expansions:")
    fresh_expansions = extract_metric(result3.stdout, "Source expansions:")
    
    print(f"\nResumed run:")
    print(f"  States: {resumed_states:,}")
    print(f"  Edges: {resumed_edges:,}")
    print(f"  Expansions: {resumed_expansions:,}")
    
    print(f"\nFresh run:")
    print(f"  States: {fresh_states:,}")
    print(f"  Edges: {fresh_edges:,}")
    print(f"  Expansions: {fresh_expansions:,}")
    
    print(f"\nDifferences:")
    print(f"  States: {resumed_states - fresh_states:+,}")
    print(f"  Edges: {resumed_edges - fresh_edges:+,}")
    print(f"  Expansions: {resumed_expansions - fresh_expansions:+,}")
    
    match = (
        resumed_states == fresh_states and
        resumed_edges == fresh_edges and
        resumed_expansions == fresh_expansions
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
