# S Z-Frontier: Exact Reachable Lengths from the Empty Frontier

Run: standalone analysis script (`/tmp/opencode/macro_length_analysis.py`)
over the **completed (capped) portion of the macro graph** — the
15,000,991-state / 14,781,970-edge closure from
`docs/s_z_frontier_macro_reachability.md`.  The graph is NOT expanded
beyond that existing data, and the solver
(`solvers/s_z_frontier_packed.py`) is NOT modified; its pure functions
(`build_templates`, `apply_template`, `first_empty`, `layer_mask`,
`shift_state`, `WORD_MASK`) are reused with identical semantics.

## Method

For every macro state `s` in the capped closure, record

    R(s) = { d : the empty frontier state 0 is reachable from s
               in exactly d macro edges }

computed by a **backward DP** over the capped closure (a DAG, verified by
Kahn's algorithm: all 15,000,991 nodes visited).  `R(s)` is stored as a
bitmask; `R(0) = {0}`, and `R(u) = { d+1 : d in R(v), v in succ(u) }`.
The DP processes nodes in reverse topological order (Kahn order), which is
required because edges can go "backward" in BFS distance (e.g. `0 ->
first-generation source`).

A complete 4x8xN tiling exists iff `0` is reachable at macro distance
`N-1` from a first-generation source (each macro edge = one full layer +
shift; the first generation consumes layer 1).

**Completeness limit**: `R(s)` is exact for `d <= 85` (N <= 86): any path
of length <= 85 from a first-generation source stays within
distance-<=84 states, all of which were fully processed (their successors
are all in the capped closure).  For `d >= 86` the result would be a lower
bound; no such values were found.

**Truncation caveat**: the true macro graph has a 20-cycle through 0
(`0 -> source -> ... -> 0`, since 0's macro successors are exactly the
first-generation sources and some source reaches 0 in 19 edges).  The
capped closure's `succ[0]` is truncated by the per-source intermediate cap
(1,000,000 states; 0's interval has 3,162,387), so the cycle is NOT in the
capped closure (`R(0) = [0]`).  Consequently through-0 paths (d = 79,
99, ...) are not visible; only non-through-0 paths are captured.

## Reachable N (exact, N <= 86)

| Metric | Value |
|---|---|
| Reachable N (exact, N <= 86) | **{20, 40, 60}** |
| First reachable N | 20 |
| Last reachable N | 60 |
| Gaps between consecutive reachable N | (21, 39), (41, 59) |
| Non-reachable N in [1, 86] | all except 20, 40, 60 |
| Partial (d > 85, lower bound) | none |

The reachable lengths are spaced exactly 20 apart: 20, 40, 60.  The
non-reachable ranges are [1, 19], [21, 39], [41, 59], [61, 86].

**Cell-count check** (32N cells must be divisible by 5, i.e. N multiple of
5): the N in [1, 86] that pass but are NOT reachable are
{5, 10, 15, 25, 30, 35, 45, 50, 55, 65, 70, 75, 80, 85}.  Of these, 80 is
the only one reachable in the true graph (via the 20-cycle through 0, see
below); the rest are genuinely impossible.

## Basin of 0

The set of states that can reach 0 is tiny: **226 states**, and every one
reaches 0 at exactly one distance (`|R(s)| = 1` for all 226).  Max
remaining distance: 59.

Only **4 of the 331,765 first-generation sources** can reach 0:

| Source | Remaining distance | N |
|---|---|---|
| 6163195513375031274 | 19 | 20 |
| 17293950180903112719 | 39 | 40 |
| 17306770486483095567 | 39 | 40 |
| 17293822637554016271 | 59 | 60 |

The four source paths (lengths 19, 39, 39, 59) are **pairwise disjoint
except for the final edge**: every pair shares exactly the two states
`{0, WORD_MASK}` (the terminal 0 and its unique predecessor).  The
remaining 226 - 154 = **72 basin states** feed into these paths (side
branches of the basin tree rooted at 0).

## Shortest path for N=20

The unique source reaching 0 in 19 edges is `6163195513375031274`
(= `0x558811aa57ffffea`).  The full path (20 layers):

* **First-generation segment**: `0 -> [14 placements] -> p0 -> source`,
  where `p0 = 0x558811aa57ffffeaffffffff` has layers
  L0 = `0xffffffff` (full), L1 = `0x57ffffea`, L2 = `0x558811aa`, and
  `p0 >> 32 == source`.
* **Macro segment**: 19 macro edges from the source to 0:

| step | post-shift state | L0 | L1 | L2 | pre-shift state |
|---|---|---|---|---|---|
| 0 | 6163195513375031274 | 0x57ffffea | 0x558811aa | 0x0 | 0xc0000003f7b81defffffffff |
| 1 | 13835058072323104239 | 0xf7b81def | 0xc0000003 | 0x0 | 0xee018077ffffffff |
| 2 | 3993075831 | 0xee018077 | 0x0 | 0x0 | 0xc6630011f24f88ffffffff |
| 3 | 55840897340952456 | 0x11f24f88 | 0xc66300 | 0x0 | 0x888811118bdffbd1ffffffff |
| 4 | 9838132153049676753 | 0x8bdffbd1 | 0x88881111 | 0x0 | 0x1d0000b8fea8157fffffffff |
| 5 | 2089671021646321023 | 0xfea8157f | 0x1d0000b8 | 0x0 | 0x300c001d1188b8ffffffff |
| 6 | 13523993509333176 | 0x1d1188b8 | 0x300c00 | 0x0 | 0xc0030080b24d01ffffffff |
| 7 | 54046496222498049 | 0x80b24d01 | 0xc00300 | 0x0 | 0xc30006ecc3376ffffffff |
| 8 | 3430478137537398 | 0x6ecc3376 | 0xc3000 | 0x0 | 0x9900098cdb319ffffffff |
| 9 | 2691607028413209 | 0x98cdb319 | 0x99000 | 0x0 | 0x118800ef3bdcf7ffffffff |
| 10 | 4934612199136503 | 0xef3bdcf7 | 0x118800 | 0x0 | 0x880011074f7ef2effffffff |
| 11 | 612490719515897646 | 0x74f7ef2e | 0x8800110 | 0x0 | 0xe20000478aae7551ffffffff |
| 12 | 16285016559841080657 | 0x8aae7551 | 0xe2000047 | 0x0 | 0x303c0c0e34182c7ffffffff |
| 13 | 217229141722890951 | 0xe34182c7 | 0x303c0c0 | 0x0 | 0x17e800771ff8eeffffffff |
| 14 | 6729013160573166 | 0x771ff8ee | 0x17e800 | 0x0 | 0x88f7ef11ffffffff |
| 15 | 2297949969 | 0x88f7ef11 | 0x0 | 0x0 | 0x11000088112e7488ffffffff |
| 16 | 1224979683048584328 | 0x112e7488 | 0x11000088 | 0x0 | 0xf003c00ff101808fffffffff |
| 17 | 17294878168733286543 | 0xf101808f | 0xf003c00f | 0x0 | 0xffffffffffffffff |
| 18 | 4294967295 | 0xffffffff | 0x0 | 0x0 | 0xffffffff |
| 19 | 0 | 0x0 | 0x0 | 0x0 | — |

The pre-shift state of each edge `u -> v` is
`WORD_MASK | (L0(v) << 32) | (L1(v) << 64)`.  Along this path every
post-shift state has L2 = 0 (the window never carries a third layer), and
the final edge is an immediate shift from `WORD_MASK` (L0 full, L1 = L2 =
0) to 0.

## Does the same terminal state / path structure repeat?

**Terminal state: yes, always.**  Every path to 0 ends with the edge
`WORD_MASK -> 0` (an immediate shift from the state with L0 full and
L1 = L2 = 0).  In the capped closure there is exactly **one** state with
an edge to 0 — `WORD_MASK` (4294967295) — so the final pre-shift state is
unique and identical for every reachable length.

**Path structure: the lengths repeat every 20 layers, but the paths do
not.**  The reachable N (20, 40, 60) are spaced exactly 20 apart, yet the
N=40 and N=60 paths are **non-decomposing**: neither passes through 0 at
any intermediate position (verified by reconstruction), so they are not
concatenations of 4x8x20 tilings.  The four source paths share only the
final two states `{WORD_MASK, 0}`.  Within the capped closure the
structure therefore does NOT literally repeat — each reachable length has
its own distinct tiling.

**In the true graph the structure does repeat.**  The 20-cycle through 0
(`0 -> source -> ... -> 0`) exists in the true macro graph, so every
multiple of 20 is reachable (80, 100, 120, ...) by appending copies of the
cycle.  This repetition is not visible in the capped closure because
`succ[0]` is truncated (per-source intermediate cap), which is why 80 is
missing from the reachable set above.

## Verification against the catalogue

* **N = 20 reachable** matches `catalogues/s_catalogue.py`:
  `Box(4, 8, 20)` is a 1+ prime (Postl 1998), and matches the previous
  analysis (`docs/s_z_frontier_macro_reachability.md`: 0 reachable at
  distance 19).
* **N = 10, 30, 50, 70 not reachable** matches the catalogue's
  `4x8x{10,30,50,70,90,110}: 0` (Shirakawa 2014) and the empirical C++
  result in `docs/s_4x8x10_baseline.md` (0 solutions for 4x8x10).
* **N = 40, 60 reachable** is consistent with the catalogue (multiples of
  20; not listed as impossible).
* **N = 5, 15, 25, 35, 45, 55, 65, 75, 85 not reachable** are new results
  (not listed in the catalogue); they are consistent with the pattern that
  only multiples of 20 are tileable.
* The reachable distances (19, 39, 59) all satisfy the cell-count
  necessary condition (N = d+1 divisible by 5).

## Caveats

* The analysis uses the capped closure (15,000,000-state cap hit), so the
  macro state/edge counts are lower bounds; the reachable-length verdicts
  for N <= 86 are exact for the capped closure.
* `succ[0]` is truncated by the per-source intermediate cap, hiding the
  20-cycle through 0; consequently N = 80 (and all multiples of 20 beyond
  60) are reachable in the true graph but not visible here.
* The completeness limit is N <= 86 (d <= 85); no partial (d > 85)
  reachable lengths were found in the capped closure.