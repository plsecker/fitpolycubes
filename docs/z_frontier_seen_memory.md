# Z-Frontier: Memory Overhead of the `seen` Set

Solver: `solvers/s_z_frontier_packed.py` (current 96-bit state, LAYERS = 3).

## Current state type

Each state is a single Python `int` (arbitrary-precision integer).
With the 3-layer packing, a state occupies 96 bits (bits 0-31 layer 0,
32-63 layer 1, 64-95 layer 2). On 64-bit CPython a 96-bit int is
stored as 4 x 30-bit digits.

## Current seen-container type

- `seen = {start_state}` (line 203): a Python `set` of `int` objects.
- BFS queue: `deque[int]` (lines 200-202), holding references to the
  same int objects that are also in `seen`.

## Why it uses substantial memory

Per stored state, the `seen` set pays two costs:

1. **The int object itself**: a `PyLongObject` has a 24-byte header
   (refcount, type pointer, size) plus 4 x 4-byte digits = 40 bytes
   per state. For 1,000,000 states this is ~40 MB.
2. **The set's hash table**: CPython set entries are 16 bytes
   (hash + key pointer) and the table is resized to keep the load
   factor below ~2/3. For 1M entries the table grows to 2^21 =
   2,097,152 slots = ~33.5 MB.

The deque adds ~8 bytes per queued slot plus block overhead; in the
1M run up to ~590,000 states are queued (~5 MB). The int objects are
shared between `seen` and the deque, so they are not duplicated.

Total for `seen` + queue at 1M states: roughly 40 + 33.5 + 5 = ~79 MB.
The measured peak RSS of the 1M run is 111 MB; the remainder is the
template table, diagnostics records and the interpreter itself.

The dominant cost is Python-object overhead: ~40 bytes per state for
the int object plus ~33 bytes per state for the set slot, versus 12
raw bytes of actual state data.

## One concrete implementation option

Replace the `set[int]` with an **open-addressing hash set backed by a
flat numpy array of 2 x uint64 words** (numpy is already a dependency
via `common/polycube_utils.py`):

- Each 96-bit state is stored as two `uint64` words (low 64 bits,
  high 32 bits) in a flat `(capacity, 2)` array: 16 bytes per state,
  zero per-object overhead.
- Membership/insertion uses linear probing with a splitmix64-style
  mix of the two words as the probe hash; the array doubles as the
  hash table and is rehashed into a larger array when the load factor
  exceeds ~0.66.
- An empty slot must be marked explicitly (e.g. a parallel
  `uint8` occupied-flag array), because state 0 (all layers empty) is
  a valid state and cannot serve as an empty sentinel.
- The BFS queue can remain a `deque[int]` (transient) or be flattened
  the same way.

Memory at 1M states: ~16 MB of state data in a table of ~1.5M slots
(~24 MB) instead of ~73 MB for the int set, roughly a 3x reduction in
`seen` memory. The search algorithm, state semantics, first-empty-cell
rule and BFS order are unchanged.

## Does the option preserve exact state equality?

Yes. Membership is decided by comparing the full 96-bit value (both
uint64 words) at the probed slot; the hash is used only to choose the
probe sequence, never as a substitute for equality. There is no
truncation, no lossy hashing and no collision mis-resolution, so the
set contains exactly the same states as the current `set[int]`.

This is an analysis only; nothing has been implemented.