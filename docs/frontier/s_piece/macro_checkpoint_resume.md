# Macro Checkpoint/Resume Procedure

## Overview

Long-running Macro computations can be interrupted and resumed from checkpoints. This enables:
- Moving computations between machines (laptop → desktop)
- Recovering from crashes or power failures
- Pausing work and continuing later

## Starting a Run

```bash
python3 tools/frontier/macro_generalized.py \
    --a 4 --b 9 \
    --max-states 10000000 \
    --checkpoint /path/to/checkpoint.ckpt \
    --checkpoint-interval 500000
```

**Parameters:**
- `--a`, `--b`: Cross-section dimensions
- `--max-states`: Maximum states to explore (total, not incremental)
- `--checkpoint`: Path where checkpoint will be saved (directory)
- `--checkpoint-interval`: Save checkpoint every N states (default: 500000)

## Stopping a Run

**Graceful stop (Ctrl-C):**
```bash
^C
```

The program will:
1. Catch SIGINT signal
2. Save final checkpoint
3. Exit cleanly

**Verify checkpoint was saved:**
```bash
ls -lh /path/to/checkpoint.ckpt/
```

You should see:
- `metadata.json` - Run metadata
- `seen.json` - Discovered states
- `queue.json` - Pending work queue
- `sources.json` - First-generation sources (if applicable)
- `macro_seen.json` - Macro states (if applicable)
- `succ.json` - Successor graph (if applicable)

## Copying to Desktop

**From laptop:**
```bash
# Copy checkpoint directory
scp -r /path/to/checkpoint.ckpt user@desktop:/path/to/

# Copy the script (if needed)
scp tools/frontier/macro_generalized.py user@desktop:/path/to/
```

**On desktop:**
```bash
# Verify checkpoint integrity
ls -lh /path/to/checkpoint.ckpt/
cat /path/to/checkpoint.ckpt/metadata.json
```

## Resuming a Run

```bash
python3 tools/frontier/macro_generalized.py \
    --resume /path/to/checkpoint.ckpt \
    --max-states 10000000
```

**Notes:**
- Dimensions (`--a`, `--b`) are read from checkpoint metadata
- `--max-states` must be ≥ checkpoint's max_states
- Computation continues from exact saved state

## Recognizing Completion

**Check results file:**
```bash
cat /tmp/macro_generalized_4x9_results.txt
```

**Completion indicators:**
- `macro_cap_hit=False` - Did not hit state limit
- `interrupted=False` - Not interrupted
- `macro_states=N` - Final state count

**Example completed output:**
```
a=4
b=9
NCELLS=36
macro_states=7916335
macro_edges=8005581
macro_cap_hit=False
zero_reachable=True
interrupted=False
```

## Using the Test Script

The `test_cross_sections.sh` script automates checkpoint/resume:

```bash
# Run full test matrix (with automatic checkpoint/resume)
bash tools/frontier/test_cross_sections.sh
```

**Features:**
- Automatically resumes from existing checkpoints
- Skips completed cross-sections
- Saves logs separately from checkpoints
- Never overwrites existing checkpoints

**Manual single cross-section:**
```bash
# Start 4×9 with checkpointing
bash tools/frontier/test_cross_sections.sh 4 9 10000000 600

# If interrupted, rerun same command - it will resume automatically
bash tools/frontier/test_cross_sections.sh 4 9 10000000 600
```

## Checkpoint Locations

**Default locations:**
- Checkpoints: `/tmp/macro_checkpoints/`
- Results: `/tmp/macro_cross_section_tests/`
- Logs: `/tmp/macro_cross_section_tests/*.log`

**Checkpoint structure:**
```
/tmp/macro_checkpoints/4x9.ckpt/
├── metadata.json       # Run parameters and state
├── seen.json          # Discovered states (sorted)
├── queue.json         # Pending work queue
├── sources.json       # First-generation sources
├── macro_seen.json    # Macro closure states
└── succ.json          # Successor graph
```

## Troubleshooting

**Checkpoint not found:**
```bash
# Check if checkpoint directory exists
ls -ld /path/to/checkpoint.ckpt

# Verify metadata
cat /path/to/checkpoint.ckpt/metadata.json
```

**Resume fails with dimension mismatch:**
- Checkpoint dimensions must match `--a` and `--b`
- Dimensions are stored in checkpoint metadata
- Use `--resume` without specifying dimensions

**Resume fails with max_states too small:**
- `--max-states` must be ≥ checkpoint's max_states
- Check checkpoint metadata: `cat checkpoint.ckpt/metadata.json | grep max_states`

**Checkpoint appears corrupted:**
```bash
# Verify JSON files are valid
python3 -c "import json; json.load(open('checkpoint.ckpt/metadata.json'))"
python3 -c "import json; json.load(open('checkpoint.ckpt/seen.json'))"
```

## Portability

**Cross-machine compatibility:**
- Checkpoints use JSON format (portable)
- No machine-specific paths or pointers
- Works across Python versions (3.8+)
- Works across operating systems

**Moving between machines:**
1. Stop computation gracefully (Ctrl-C)
2. Copy checkpoint directory to new machine
3. Resume with `--resume` flag
4. Computation continues from exact saved state

## Example Workflow

**On laptop:**
```bash
# Start 4×9 computation
python3 tools/frontier/macro_generalized.py \
    --a 4 --b 9 \
    --max-states 10000000 \
    --checkpoint /tmp/macro_checkpoints/4x9.ckpt \
    --checkpoint-interval 500000

# Let it run for a while, then stop
^C

# Verify checkpoint
ls -lh /tmp/macro_checkpoints/4x9.ckpt/
```

**Transfer to desktop:**
```bash
scp -r /tmp/macro_checkpoints/4x9.ckpt desktop:/tmp/
```

**On desktop:**
```bash
# Resume computation
python3 tools/frontier/macro_generalized.py \
    --resume /tmp/4x9.ckpt \
    --max-states 10000000

# Monitor progress
tail -f /tmp/macro_generalized_4x9_results.txt
```

## Notes

- Checkpoints are atomic (write-to-temp + rename)
- No data loss on interruption
- Checkpoint size scales with state count (~100MB per million states)
- Resume is exact (no recomputation of saved states)
