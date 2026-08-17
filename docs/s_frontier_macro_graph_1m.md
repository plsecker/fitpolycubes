# S Z-Frontier: Macro Graph of Post-Shift States (1M run)

Run: standalone analysis script (`/tmp/opencode/macro_graph.py`) over the
2,451 recorded post-shift states from
`docs/z_frontier_all_shift_states_1m.md`
(`solvers/s_z_frontier_packed.py --postshift-diagnostics --max-states 1000000`).

The solver itself is NOT modified and its discovery loop is not run; the
script reuses the solver's pure functions (`build_templates`,
`apply_template`, `first_empty`, `layer_mask`, `shift_state`, `WORD_MASK`)
with identical semantics.

## Method

A **macro node** is a post-shift state: the state immediately after a layer
shift (`post_shift_state = pre_shift_state >> 32`).

From each source, the script explores the source's **placement interval**
exactly as the solver's `discover` loop does: repeatedly apply
`templates[first_empty(layer0)]` to the current state; when
`layer0 == WORD_MASK`, the shift successor `state >> 32` is recorded as a
macro edge and that path stops.  All intermediate (non-shift) states are
discarded; only distinct post-shift states are recorded.

Two graphs are reported:

* **One-level macro graph**: edges from the 2,451 recorded sources only.
* **Closure** (supplementary): the macro transition iterated from every
  reached post-shift state until no new states appear.  The closure run
  completed without hitting its state cap, so its cycle analysis is
  definitive for the reachable macro state space.

**Per-source safety limit**: `MAX_INTERMEDIATE = 1,000,000` distinct
non-shift states explored per source (calibration over the first 30 sources
showed a max of 40,399; 1,000,000 is ~25x that).  Any source hitting the
limit would be truncated and reported; **no source hit the limit**.

## Summary (one-level macro graph)

| Metric | Value |
|---|---|
| Sources (recorded post-shift states) | 2,451 |
| Macro states (sources ∪ successors) | 30,173 |
| Macro edges (distinct source → successor) | 27,982 |
| Zero-outgoing macro states | 29,763 |
| Max macro out-degree | 2,689 (1 state) |
| SCC count | 30,173 |
| Nontrivial SCCs (size > 1 or self-loop) | 0 |
| Largest SCCs | none |
| Total intermediate states explored | 762,858 |
| Max intermediate per source | 40,398 (source 2416545801) |
| Sources hitting safety limit (1,000,000) | 0 |

## Zero-outgoing states

29,763 of the 30,173 macro states have no outgoing macro edge:

* **2,041 of the 2,451 sources (83.3%)** dead-end: their placement
  intervals never reach a full layer 0, so they never trigger another
  layer shift.  These are terminal macro nodes.
* The remaining 27,722 zero-outgoing states are successors that are not
  among the 2,451 recorded sources; in the one-level graph they have no
  explored outgoing edges by construction.

Only **410 sources (16.7%)** reach at least one further layer shift.

## Max out-degree

The maximum macro out-degree is **2,689**, achieved by exactly one source:
state `2416545801` (shift event #2).  The top 10 sources by out-degree:

| Out-degree | Source state |
|---|---|
| 2,689 | 2416545801 |
| 1,988 | 17296215183446343705 |
| 1,154 | 3515200320483983385 |
| 914 | 17332402237125267465 |
| 781 | 69946604743393305 |
| 757 | 17294420780469395481 |
| 675 | 3676769300090889 |
| 675 | 2445316276727817 |
| 595 | 8358680910279315465 |
| 595 | 199985041422 |

## Out-degree distribution of the 2,451 sources

| Out-degree | Sources | Out-degree | Sources | Out-degree | Sources |
|---|---:|---:|---:|---:|---:|
| 0 | 2,041 | 21 | 4 | 61 | 2 |
| 1 | 26 | 22 | 3 | 62 | 2 |
| 2 | 31 | 23 | 2 | 63 | 2 |
| 3 | 12 | 24 | 2 | 64 | 4 |
| 4 | 32 | 25 | 2 | 65 | 3 |
| 5 | 7 | 27 | 6 | 66 | 1 |
| 6 | 18 | 28 | 1 | 72 | 1 |
| 7 | 9 | 29 | 1 | 76 | 2 |
| 8 | 15 | 30 | 5 | 80 | 5 |
| 9 | 9 | 31 | 3 | 81 | 2 |
| 10 | 13 | 32 | 7 | 83 | 1 |
| 12 | 18 | 34 | 2 | 84 | 4 |
| 13 | 7 | 35 | 1 | 85 | 1 |
| 14 | 4 | 36 | 3 | 86 | 3 |
| 15 | 3 | 38 | 1 | 87 | 1 |
| 16 | 17 | 39 | 2 | 88 | 2 |
| 17 | 4 | 40 | 7 | 96 | 1 |
| 18 | 8 | 42 | 1 | 97 | 1 |
| 19 | 1 | 43 | 2 | 100 | 2 |
| 20 | 3 | 45 | 3 | 103 | 2 |
| | | 46 | 1 | 110 | 1 |
| | | 47 | 1 | 112 | 1 |
| | | 48 | 6 | 114 | 3 |
| | | 49 | 1 | 125 | 1 |
| | | 50 | 2 | 130 | 2 |
| | | 52 | 3 | 133 | 1 |
| | | 53 | 1 | 140 | 1 |
| | | 55 | 5 | 141 | 2 |
| | | 56 | 1 | 144 | 2 |
| | | 60 | 1 | 151 | 1 |
| | | | | 169 | 3 |
| | | | | 172 | 2 |
| | | | | 178 | 2 |
| | | | | 185 | 1 |
| | | | | 198 | 2 |
| | | | | 199 | 2 |
| | | | | 201 | 2 |
| | | | | 261 | 2 |
| | | | | 315 | 1 |
| | | | | 317 | 1 |
| | | | | 364 | 1 |
| | | | | 365 | 1 |
| | | | | 379 | 2 |
| | | | | 392 | 2 |
| | | | | 582 | 2 |
| | | | | 595 | 2 |
| | | | | 675 | 2 |
| | | | | 757 | 1 |
| | | | | 781 | 1 |
| | | | | 914 | 1 |
| | | | | 1,154 | 1 |
| | | | | 1,988 | 1 |
| | | | | 2,689 | 1 |

## SCC and cycle analysis

Tarjan's algorithm on the one-level macro graph:

* **SCC count: 30,173** — exactly the number of macro states, so every
  SCC is a singleton.
* **Nontrivial SCCs: 0** — no SCC has size > 1 and no node has a
  self-loop.  In particular, no recorded source can reach itself through
  macro edges, and no pair of sources is mutually reachable.

### Closure (supplementary, definitive)

Iterating the macro transition to closure (complete; the 1,000,000-state
cap was NOT hit):

| Metric | Value |
|---|---|
| Closure macro states | 31,113 |
| Closure macro edges | 28,927 |
| Closure zero-outgoing states | 30,541 |
| Closure max out-degree | 2,689 |
| Closure SCC count | 31,113 |
| Closure nontrivial SCCs | 0 |
| Closure largest SCCs | none |
| Closure total intermediate states | 886,886 |
| Closure elapsed | 9.7 s |

The closure adds only 940 states over the one-level graph (31,113 vs
30,173), and its SCC analysis is identical in character: **every SCC is a
singleton and there are no nontrivial cycles**.  The macro graph of
post-shift states is therefore **acyclic (a DAG)**: the z-frontier process,
viewed at the layer-shift level, never revisits a post-shift state.

## Per-source safety limit report

* Limit: 1,000,000 distinct non-shift states per source.
* Sources hitting the limit: **0**.
* Max observed per source: 40,398 (source `2416545801`, the same state
  with the max out-degree).
* Total intermediate states explored: 762,858 (one-level) / 886,886
  (closure).

## Verification

* **Calibration check passed**: the successor counts for the first 30
  sources match the earlier calibration run exactly (e.g. source 2 →
  2,689 successors, source 20 → 582, source 28 → 675).
* The intermediate-state definition counts distinct non-shift states
  excluding the source itself; the earlier calibration figure of 40,399
  for source 2 includes the source state (40,398 + 1).
* All 2,451 sources were read from column 3 of the event table in
  `docs/z_frontier_all_shift_states_1m.md`; the reader skips the header
  and separator rows.