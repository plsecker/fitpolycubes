# Z-Frontier: Compact `seen` Set — Implementation Result

Solver: `solvers/s_z_frontier_packed.py` (96-bit state, LAYERS = 3).
Follows the analysis in `docs/z_frontier_seen_memory.md`.

## What was implemented

`seen` is now a `SeenSet` (new class in the solver): an exact
open-addressing hash table backed by a flat numpy array of
`2 x uint64` words (16 bytes per slot, zero per-object overhead).

- Each 96-bit state is stored as two `uint64` words (low 64 bits,
  high 32 bits).
- Membership is decided by **full 96-bit comparison** of both words at
  the probed slot; the splitmix64-style hash of `(lo, hi)` is used
  only to choose the probe sequence. No truncation, no lossy hashing.
- An empty slot is marked by the sentinel `2**64 - 1` in the high
  word. This is safe because every valid state has its high word
  `< 2**32`; state 0 is stored normally (`lo = 0, hi = 0`).
- The table doubles and rehashes when the load factor exceeds 0.66
  (2^20 -> 2^21 slots during the 1M run). Deletion is not supported
  (the search never removes states).
- The BFS queue remains a `deque[int]`; the search algorithm,
  transitions, first-empty-cell rule, diagnostics and BFS order are
  unchanged. The Python `set[int]` path is kept behind
  `compact_seen=False` for the smoke test only.

## Smoke test (--smoke-test, 100,000 states)

`--smoke-test` runs both implementations at `--max-states 100000`
with diagnostics on and compares:

- all nine summary metrics (states, processed, generated, accepted,
  duplicates, shifts, branching, max out-degree, queue remaining);
- the out-degree histogram and the first 100 duplicate-transition and
  layer-shift records;
- the exact set of seen states (100,001 states);
- the exact BFS queue order.

Result: **SMOKE TEST PASSED** — identical metrics, diagnostics, seen
states and BFS order. The compact table contains exactly the same
states as the Python set.

## Run: --max-states 1000000

| Metric | Value |
|---|---|
| States | 1,000,000 |
| Processed | 409,873 |
| Duplicate states | 353 |
| Layer shifts | 2,451 |
| Branching states | 267,139 |
| Maximum out-degree | 11 |
| Elapsed | 4.97 s |
| Peak RSS | 101 MB |

All search metrics are identical to the 128-bit and 96-bit baseline
runs (1,000,000 / 409,873 / 353 / 2,451 / 267,139), confirming the
replacement changes nothing about the search.

## Comparison with the Python set[int] baseline

Same machine, fresh process per implementation, `--max-states 1000000`:

| | Python set[int] | Compact SeenSet | Delta |
|---|---|---|---|
| Peak RSS | 110 MB | 101 MB | -9 MB (-8%) |
| Elapsed | 1.38 s | 4.97 s | +3.6x |

Notes:

- The `seen` container itself shrank from ~73.5 MB (40 MB of int
  objects + 33.5 MB set table at 2^21 slots) to 33.5 MB (2^21 x 16
  bytes), about a 2.2x reduction. The total-RSS gain is smaller
  because the BFS queue still holds transient Python ints (~590,000 x
  40 B ~ 24 MB at peak) that were previously shared with the set.
- The elapsed-time cost (~3.6x) comes from per-element numpy scalar
  access in the probe loop; the Python set is C-optimized.
- Peak RSS was cross-checked two ways: the solver's `ru_maxrss`
  report and a `/proc/<pid>/status` VmHWM poller agree (101 MB
  compact, 110 MB set). `ru_maxrss` was observed to be unreliable in
  this environment (transient spurious ~830 MB readings at
  interpreter start while VmHWM showed ~9 MB), so the VmHWM
  cross-check was used to confirm the reported numbers.

## Trade-off summary

- Exactness: preserved (full 96-bit equality, no lossy hashing).
- Search behavior: preserved (identical metrics, diagnostics, BFS
  order; verified by the smoke test).
- Memory: -9 MB peak RSS (-8%) at 1M states; the seen container alone
  is ~2.2x smaller.
- Speed: ~3.6x slower; the queue's transient int objects are now the
  dominant remaining Python-object cost.

No other optimization was made.