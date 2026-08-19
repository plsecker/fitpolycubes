# 4×8×130 Macro Closure Checkpoint — Location, Format, Recovery

The 30,000,015-state Macro closure checkpoint is **not** stored in Git
(~943 MB).  This document records its exact location, file format,
checksums, and how to regenerate or recover it.

## Location

    /tmp/opencode/macro130_checkpoints/

(Outside the repository; on the machine where the closure was run.
If the directory is lost, see "Regeneration" below.)

## Files and checksums (sha256)

| File | Size (bytes) | sha256 |
|---|---|---|
| `macro_seen.npy` | 240,000,248 | `40f44e7605c577a9213aacb7cce531e9a7b6ee3c28041a9a2772d9b16007c677` |
| `succ.npy` | 261,929,528 | `d8b7ab600c89dd619042fb9a6f0a36ad4125da8aa8f4f7f17bf75706910aadef` |
| `dist.npy` | 480,000,368 | `2c218385926661a405640d9130b63bc65603a89aad6fe0482edc44e446eb5d5e` |
| `queue.npy` | 6,119,520 | `d09595273709f743d1bd6eb151fa5e3b6f761e969ddfbde23be343c5060dabad` |
| `counters.txt` | 68 | `52e4b99a3f099a51813f6120fc98bad73e9607fb9869bc56a38910aac687bea3` |

## Exact format

All `.npy` files are numpy arrays, `allow_pickle=False`, `dtype=uint64`.

### macro_seen.npy

    shape (30,000,015,), sorted ascending
    the 30,000,015 MacroStates of the closure

### succ.npy

    flat array, one record per source state:
        [source, n, succ_1, ..., succ_n]
    sources appear in the same order as macro_seen.npy
    29,902,891 edges total, 1,419,142 sources with n > 0

**Important caveat:** `succ[0]` in the checkpoint is the *truncated*
closure version (first-generation cap).  It must be patched with the
complete successor list of 0 before any SCC/walk analysis:

    succ[0] = explore_source(0, templates, MAX_INTERMEDIATE_0 = 4_000_000)
    # 331,765 complete first-generation sources

### dist.npy

    shape (30,000,015, 2): [state, distance] pairs
    distance = BFS distance to 0 within the closure (capped)

### queue.npy

    BFS queue snapshot (restart support)

### counters.txt

    closure counters (processed/generated/accepted/duplicates/shifts)

## Regeneration / recovery

1. Re-run the 30M closure with `tools/frontier/scc_aware_analysis.py`
   (max_states = 30,000,000).  Run logs from the original run:
   `logs/macro_30m_run.log`, `logs/macro_30m_reported.log`.
   The closure run takes on the order of hours and ~11 GB RAM.
2. Verify the result: `macro_states = 30,000,015`,
   `num_sccs = 29,999,520`, `num_nontrivial_sccs = 3`,
   SCC sizes {10, 10, 478} (see `result.md` Section D).
3. Patch `succ[0]` as described above before running
   `tools/frontier/reconstruct_130_path.py`.

## Derived artifacts (in Git)

The small derived artifacts are retained in Git under
`docs/frontier/s_piece/4x8x130_macro/results/`:

    scc_130_states.npy   (478 SCC states)
    scc_130_succ.npy     (478 sources, 514 SCC-internal edges)
    walks_130.txt        (all 2048 walks)
    edge_realizations_130.txt
    ... (see README.md for the full list)

These are sufficient to reproduce every number in `result.md` without
the checkpoint, except the closure/SCC figures themselves (Section D),
which require the checkpoint or a re-run.