# Z-Frontier Recurrence (from diagnostics)

Source: `docs/z_frontier_state_stats.md` — S 4x8, 100,000-state cap,
29,086 processed states. Per-state records are listed in processing
(BFS) order; record #N is the N-th processed state.

## 1. First duplicate transitions

The first duplicate transition occurs at processed state **#425**:
`627189299876219325951` (out-degree 6, one successor already seen).
The first 10 duplicate-transition states are listed in section 5.

## 2. Layer shift states

Exactly 4 states transition by layer shift (all with 0 successors
already seen):

| Processed # | State (packed) |
|---|---|
| 27,259 | 4774536927590219775 |
| 27,386 | 10378985188876091391 |
| 27,488 | 405482339087417343 |
| 28,454 | 10396579573943762943 |

## 3. Maximum layer-shift count

**4** — the diagnostic data contains exactly 4 layer-shift transitions
(one per shift state; the summary's "Layer shifts: 4").

## 4. Out-degrees of layer-shift states

All 4 layer-shift states have out-degree **1**: a layer shift is the
single outgoing edge of a state whose layer 0 is full.

## 5. First 10 duplicate transitions

Each of these states has exactly one successor already seen (all 21
duplicate transitions in the data are single duplicates):

| # | Processed # | State (packed) | Out-degree |
|---|---|---|---|
| 1 | 425 | 627189299876219325951 | 6 |
| 2 | 427 | 20070057553703525682687 | 5 |
| 3 | 3,699 | 17764214792996639537151 | 1 |
| 4 | 4,610 | 5137934733748386042609663 | 5 |
| 5 | 4,611 | 160560460768595615285247 | 6 |
| 6 | 5,451 | 924403239166692491849727 | 4 |
| 7 | 5,452 | 17708874323779216273407 | 3 |
| 8 | 6,136 | 324256867456558466891775 | 3 |
| 9 | 9,486 | 5141790103260130641313791 | 5 |
| 10 | 9,488 | 164415830280340213989375 | 6 |