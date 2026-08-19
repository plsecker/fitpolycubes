# Checkpoint/Restart Implementation Report

## Summary

Successfully added checkpoint/restart support to the SCC-aware macro closure analysis. The implementation allows the macro closure BFS to resume after process termination without restarting from state 0.

## Files Changed

1. **tools/frontier/scc_aware_analysis.py**
   - Added `save_checkpoint()` function for atomic checkpoint writes
   - Added `load_checkpoint()` function for checkpoint restoration
   - Modified `macro_closure()` to support checkpoint/restart
   - Added command-line arguments: `--checkpoint-dir`, `--checkpoint-every`, `--max-closure-states`

2. **tools/frontier/test_checkpoint_restart.py** (new)
   - Test script to verify checkpoint/restart functionality
   - Compares resumed run vs fresh run to ensure identical results

## Checkpoint Format

Checkpoints are stored as numpy binary arrays for compact representation:

| File | Format | Contents | Size at 2M states |
|------|--------|----------|-------------------|
| `macro_seen.npy` | uint64 array | All discovered macro states | 16 MB |
| `queue.npy` | uint64 array | BFS queue states | 0.3 MB |
| `succ.npy` | uint64 array | Successor edges (source, count, succ1, succ2, ...) | 15 MB |
| `dist.npy` | uint64 array | Distance pairs (state, distance, ...) | 32 MB |
| `counters.txt` | text | Cumulative counters (total_intermediate, edge_count, elapsed) | 65 bytes |

**Total checkpoint size at 2M states: ~63 MB**

## Estimated Checkpoint Sizes

| States | macro_seen | queue | succ | dist | Total |
|--------|------------|-------|------|------|-------|
| 2M | 16 MB | 0.3 MB | 15 MB | 32 MB | **63 MB** |
| 15M | 120 MB | ~2 MB | ~110 MB | ~240 MB | **~472 MB** |
| 30M | 240 MB | ~4 MB | ~220 MB | ~480 MB | **~944 MB** |

## Atomic Writes

Checkpoints are written atomically using the temp-file-then-rename pattern:
1. Write to temporary directory (`.checkpoint_temp/`)
2. Use `os.replace()` to atomically move files to final location
3. Clean up temporary directory

This ensures that a checkpoint is either complete or not present, preventing corruption from interrupted writes.

## Command-Line Interface

```bash
# Basic usage with checkpointing
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
  --max-closure-states 30000000 \
  --checkpoint-dir /tmp/opencode/macro130_checkpoints \
  --checkpoint-every 1000000

# Resume from checkpoint (automatic if checkpoint exists)
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
  --max-closure-states 30000000 \
  --checkpoint-dir /tmp/opencode/macro130_checkpoints
```

### Arguments

- `--max-closure-states`: Maximum number of macro states to discover (default: 15,000,000)
- `--checkpoint-dir`: Directory for checkpoints (default: None, disabled)
- `--checkpoint-every`: Checkpoint interval in newly discovered states (default: 1,000,000)

## Test Results

**Test: Checkpoint/Restart Correctness**

1. Fresh run to 1M states: 1,003,089 states, 678,635 edges
2. Resume from checkpoint to 2M states: 2,000,018 states, 1,683,966 edges ✓ (resumed)
3. Fresh run to 2M states: 2,000,018 states, 1,683,966 edges ✓ (comparison)

**Result: ✓ PASSED** - Resumed run produces identical results to fresh run.

## Resume Command for 30M Production Run

```bash
cd /home/philip/Work/fitpolycubes

# Start the 30M run with checkpointing
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
  --max-closure-states 30000000 \
  --checkpoint-dir /tmp/opencode/macro130_checkpoints \
  --checkpoint-every 1000000 \
  2>&1 | tee logs/macro_30m_run.log

# If interrupted, simply re-run the same command
# It will automatically resume from the last checkpoint
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
  --max-closure-states 30000000 \
  --checkpoint-dir /tmp/opencode/macro130_checkpoints \
  --checkpoint-every 1000000 \
  2>&1 | tee -a logs/macro_30m_run.log
```

## Memory Considerations

The checkpoint format uses compact numpy arrays (uint64) instead of Python objects, reducing memory overhead:
- Python set of 2M integers: ~112 MB (56 bytes per int + set overhead)
- Numpy array of 2M uint64: 16 MB (8 bytes per int)
- **Compression ratio: ~7x**

This makes checkpointing practical even for large state spaces.

## Next Steps

The checkpoint/restart infrastructure is ready for the 30M production run. The run can be safely interrupted and resumed without losing progress.
