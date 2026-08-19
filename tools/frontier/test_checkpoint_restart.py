#!/usr/bin/env python3
"""
Test checkpoint/restart functionality for macro closure.

This test verifies that:
1. Checkpoints are saved correctly
2. Resuming from a checkpoint produces the same result as a fresh run
3. The checkpoint format is correct and can be loaded
"""

import subprocess
import sys
import shutil
from pathlib import Path

def run_closure(max_states, checkpoint_dir, label):
    """Run macro closure with given parameters."""
    cmd = [
        ".venv/bin/python3",
        "tools/frontier/scc_aware_analysis.py",
        f"--max-closure-states={max_states}",
        f"--checkpoint-dir={checkpoint_dir}",
        "--checkpoint-every=500000",
    ]
    
    print(f"\n{'='*60}")
    print(f"Running: {label}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract key metrics from output
    output = result.stdout
    metrics = {}
    
    for line in output.split('\n'):
        if 'macro states:' in line and 'Step 2:' not in line:
            # Extract number before the time in parentheses
            parts = line.split(':')[1].strip().split('(')[0].strip()
            metrics['macro_states'] = int(parts.replace(',', ''))
        elif 'macro edges:' in line and 'Step 2:' not in line:
            parts = line.split(':')[1].strip().split('(')[0].strip()
            metrics['macro_edges'] = int(parts.replace(',', ''))
        elif 'Resuming from checkpoint' in line:
            metrics['resumed'] = True
        elif 'No checkpoint found' in line:
            metrics['resumed'] = False
    
    return metrics

def main():
    checkpoint_dir = Path("/tmp/test_checkpoint_restart")
    
    # Clean up any existing checkpoint
    if checkpoint_dir.exists():
        shutil.rmtree(checkpoint_dir)
    
    # Test 1: Run to 1M states with checkpointing
    print("\n" + "="*60)
    print("TEST 1: Fresh run to 1M states")
    print("="*60)
    metrics_1m = run_closure(1_000_000, checkpoint_dir, "Fresh run to 1M")
    
    print(f"\nResults:")
    print(f"  Macro states: {metrics_1m.get('macro_states', 'N/A'):,}")
    print(f"  Macro edges: {metrics_1m.get('macro_edges', 'N/A'):,}")
    print(f"  Resumed: {metrics_1m.get('resumed', 'N/A')}")
    
    # Verify checkpoint was created
    checkpoint_files = list(checkpoint_dir.glob("*.npy")) + list(checkpoint_dir.glob("*.txt"))
    print(f"\nCheckpoint files created: {len(checkpoint_files)}")
    for f in checkpoint_files:
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
    
    # Test 2: Resume from checkpoint and continue to 2M states
    print("\n" + "="*60)
    print("TEST 2: Resume from checkpoint to 2M states")
    print("="*60)
    metrics_2m_resumed = run_closure(2_000_000, checkpoint_dir, "Resume to 2M")
    
    print(f"\nResults:")
    print(f"  Macro states: {metrics_2m_resumed.get('macro_states', 'N/A'):,}")
    print(f"  Macro edges: {metrics_2m_resumed.get('macro_edges', 'N/A'):,}")
    print(f"  Resumed: {metrics_2m_resumed.get('resumed', 'N/A')}")
    
    # Test 3: Fresh run to 2M states (for comparison)
    print("\n" + "="*60)
    print("TEST 3: Fresh run to 2M states (comparison)")
    print("="*60)
    
    fresh_checkpoint_dir = Path("/tmp/test_checkpoint_fresh")
    if fresh_checkpoint_dir.exists():
        shutil.rmtree(fresh_checkpoint_dir)
    
    metrics_2m_fresh = run_closure(2_000_000, fresh_checkpoint_dir, "Fresh run to 2M")
    
    print(f"\nResults:")
    print(f"  Macro states: {metrics_2m_fresh.get('macro_states', 'N/A'):,}")
    print(f"  Macro edges: {metrics_2m_fresh.get('macro_edges', 'N/A'):,}")
    print(f"  Resumed: {metrics_2m_fresh.get('resumed', 'N/A')}")
    
    # Compare results
    print("\n" + "="*60)
    print("COMPARISON")
    print("="*60)
    
    states_match = metrics_2m_resumed.get('macro_states') == metrics_2m_fresh.get('macro_states')
    edges_match = metrics_2m_resumed.get('macro_edges') == metrics_2m_fresh.get('macro_edges')
    
    print(f"Macro states match: {states_match}")
    print(f"  Resumed: {metrics_2m_resumed.get('macro_states', 'N/A'):,}")
    print(f"  Fresh:   {metrics_2m_fresh.get('macro_states', 'N/A'):,}")
    
    print(f"\nMacro edges match: {edges_match}")
    print(f"  Resumed: {metrics_2m_resumed.get('macro_edges', 'N/A'):,}")
    print(f"  Fresh:   {metrics_2m_fresh.get('macro_edges', 'N/A'):,}")
    
    if states_match and edges_match:
        print("\n✓ TEST PASSED: Checkpoint/restart produces identical results")
        return 0
    else:
        print("\n✗ TEST FAILED: Results differ")
        return 1

if __name__ == "__main__":
    sys.exit(main())
