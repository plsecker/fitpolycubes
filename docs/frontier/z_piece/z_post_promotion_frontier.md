# Z Post-Promotion Frontier — Strategic Map

**Date**: 2026-08-28
**State**: post-promotion (77 Shirakawa `1+` rows in `PUBLISHED_SOLUTIONS`,
applied and verified 2026-08-28). Read-only analysis; no catalogue, rule,
or certificate changes. No solver searches were performed.

## 1. Current audit state (re-run for the record)

| audit (dim ≤ 20) | count |
|---|---|
| A prime mismatches | 0 |
| B unproven composites (Unknown) | **329** (was 331) |
| C discovered composites (engine-closed) | **70** (was 69) |
| D published solutions | **77** (was 0) |

Full canonical scan, dims ≤ 60 (18,220 volume-valid boxes):

| class | count |
|---|---|
| Impossible | 1,981 |
| **Unknown** | **10,478** |
| Prime | 53 |
| PublishedSolution | 52 |
| Slab | 5,506 |
| Width | 100 |
| Breadth | 50 |

Closed constructions total 5,761; every currently-Unknown box is one where
the exhaustive decomposition engine has already failed all guillotine /
semigroup routes over the complete evidence set. **Bucket (a) — boxes
immediately solvable by existing decomposition — is empty by construction**;
the 102 promoted closures were the last of that kind.

## 2. Frontier by structural group (dims ≤ 60)

Unknown mass concentrates in 1,473 cross-sections `(a, b)`:

| group | rows | Unknown boxes | character |
|---|---|---|---|
| G-A virgin-in-window | 372 | **787** | no closable length ≤ 60 in the row (first witness needed) |
| G-B evidence rows, residual gaps | 1,101 | **9,691** | row has ≥1 closed length; gaps are what sums cannot reach |
| — fully-impossible rows (no frontier) | 149 | 0 | entirely covered by encoded rules |

G-A hotspots (all `3`-width rows below the published first solutions, plus
small even blocks): `(3,25)` 36u, `(3,30)` 31u, `(3,35)` 26u, `(3,40)` 21u,
`(3,45)` 16u, `(3,50)` 11u, `(9,9)` 11u, `(7,13)` 10u, `(3,23)/(3,24)` 8u each
(these two rows have published solutions at 150/175/…/300 — *out of window*),
`(3,26)..(3,29)` 7u each.

G-B hotspots: `(5,11)` 48u (closed only at 40, 60), `(10,11)` 43u, `(5,8)` 42u,
`(5,9)` 41u, `(5,12)/(5,13)/(6,10)/(7,10)/(8,10)/(9,10)` 40u each,
`(4,15)` 39u, `(10,12)` 39u, `(5,14)` 38u, `(10,13)` 38u, `(7,15)` 37u.

A decisive structural splitter is area mod 5:

* `area ≡ 0 (mod 5)` rows — *every* length `c` is volume-valid, so the
  residual frontier is dense and includes non-multiple-of-5 thicknesses:
  `(4,10)` 12u (all non-mult-5), `(5,8)` 42u (all), `(5,9)` 41u (all),
  `(5,10)` 26u (20 non-mult-5), `(5,11)` 48u (40 non-mult-5), `(4,15)` 39u (36).
* `area ≢ 0 (mod 5)` rows — only `c ≡ 0 (mod 5)` is volume-valid, so the
  frontier is a sparse lattice of multiples of 5: `(4,11)` 8u, `(4,12)` 9u,
  `(4,13)` 9u, `(9,9)` 11u, `(6,6)` 9u, `(6,7)/(7,8)` 9u each.

## 3. Bucket classification of the remaining frontier

| bucket | count | content |
|---|---|---|
| (a) immediately solvable by existing decomposition | **0** | engine is exhaustive; see §1 |
| (b) one missing published/source fact away | **113** as-impossible + named single witnesses as-closable | L1 explicit zeros (10) + L2 `s:0` layer (103); positive witnesses tabled in §6/§7 |
| (c) small targeted search candidates | ~15 named boxes | single-witness levers with 1–8 in-window payoffs each (§6) |
| (d) new Macro/structural mathematics | **10,365** (787 + 9,691 minus the §6 overlaps) | everything else |

## 4. Named bands from the earlier audit — post-promotion status

| band | status after promotion | change |
|---|---|---|
| `5×10×19..32` | all **14 Unknown** | unchanged |
| `5×10×34/35` | both **Unknown** | unchanged |
| `5×15×16..19` | `16` Unknown; `17`, `19` prime; **`18` closed** (`Slab 9+9` = two `5×9×15` primes — pre-existing closure; the earlier band description was imprecise here) | residual is `5×15×16` alone |
| `(4,11)` gaps | `15,20,30,35,40,45,55,60` **8 Unknown**; `25` impossible; `50` prime | unchanged |
| `9×9×N` | **11 Unknown** (`N = 10..60`, multiples of 5) | unchanged |

No named band changed status through the promotion — as expected, since the
promoted evidence lives in other cross-sections.

## 5. The `s:0` evidence layer (re-evaluated; NOT encoded)

| family | candidates ≤60 | still Unknown | already otherwise classified |
|---|---|---|---|
| `(4,10)` tail | 12 | 12 | 0 |
| `(4,11)` tail | 8 | 8 | 0 |
| `(5,8)` tail | 42 | 42 | 0 |
| `(5,9)` tail | 41 | 41 | 0 |
| **total** | **103** | **103** | **0** |

The promotion did not intersect this layer at all: adopting the `s:0`
semigroup convention would remove **exactly 103 Unknown boxes** (3.3% of the
remaining dim ≤ 60 frontier; 100% of the four families' non-semigroup tails),
with zero interaction with the 102 closures. Still a policy decision only.

## 6. Explicit, source-backed but untranscribed evidence (task 6)

From the raw page HTML (no searches performed):

1. **`5x10x[10-18]` block, sols `0`** — an *explicit* impossibility row
   (plain `0`, not even an `s:0` inference), currently **not encoded**:
   9 Unknown boxes would become Impossible. This is the same class of fact
   as the already-encoded `4x10x[10-45]`.
2. **`3x23x50` per-box `s:0`** (690 pieces) — 1 Unknown box; the only
   per-box zero row on the page not yet encoded (the other seven are).
3. Exact solution counts and witness links on already-catalogued rows
   (`4x10x50` count 2, `5x9x15` count 2, `5x8x20` count 10, `6x10x10`
   count `11+ minimal`) — provenance enrichment for `RAW_PRIMES` comments;
   no frontier effect.
4. Nothing else numeric on the 3D page is untranscribed: every other row is
   already represented in `RAW_PRIMES`, `PUBLISHED_SOLUTIONS`, or
   `impossible_reason`. (4D/5D data out of scope per project convention.)

Layers L1 (10 boxes, explicit) and L2 (103 boxes, semigroup-scoped) are
disjoint; together 113 boxes.

## 7. Ranked next actions (max ten)

| # | action | target | payoff (dims ≤ 60) | evidence already available | cost | needs |
|---|---|---|---|---|---|---|
| 1 | Transcribe explicit `0` block | `5x10x[10-18]` | 9 Unknown → Impossible | explicit page row (plain `0`) | minutes | human approval + transcription |
| 2 | Transcribe per-box `s:0` | `3x23x50` | 1 | explicit page row | minutes | human approval + transcription |
| 3 | `s:0` family-layer policy decision | `(4,10)/(4,11)/(5,8)/(5,9)` tails | **103** Unknown → Impossible | page rows + repo gloss (`t_source_survey.md`) | transcription script once decided | **human policy approval** |
| 4 | Targeted exact-cover search | `6x6x10` (72 pieces) | closes itself + **8** in-window (`10,20,30,35,40,45,55,60`) | none needed; leverage measured | small (existing solver infra) | decomposition only |
| 5 | Targeted search | `6x7x10` (84 pc) | +8 | — | small | decomposition only |
| 6 | Targeted search | `7x8x10` (112 pc) | +8 | — | moderate | decomposition only |
| 7 | Targeted search | `8x8x10` (128 pc) | +8 | — | moderate | decomposition only |
| 8 | Targeted search | `4x11x15` (132 pc) | +4 (`15,30,45,60`); unlocks the `(4,11)` gap structure | — | moderate | decomposition only |
| 9 | Targeted search | `9x9x10` (162 pc) | +6; unlocks virgin row `(9,9)` | — | moderate | decomposition only |
| 10 | Macro/structural program | `3`-width band (pre-first-solution), `(≥10,≥10)` blocks, dense `(5,·)` residuals | 10,365 remaining | methodology precedents (`t/v/s_piece` docs) | large | new mathematics |

Leverage table for the search candidates (gains are measured by simulating
guillotine closure over the real post-promotion row data):

| witness | in-window gains |
|---|---|
| `6x6x10` | 10, 20, 30, 35, 40, 45, 55, 60 |
| `6x7x10` | 10, 20, 30, 35, 40, 45, 55, 60 |
| `7x8x10` | 10, 20, 30, 35, 40, 45, 55, 60 |
| `8x8x10` | 10, 20, 30, 35, 40, 45, 55, 60 |
| `9x9x10` | 10, 20, 30, 40, 50, 60 |
| `4x11x15` | 15, 30, 45, 60 |
| `4x12x15` / `4x13x15` | 15, 30, 45, 60 |
| `4x14x15` / `4x16x15` | 15, 30, 40, 45, 55, 60 |
| `5x10x34` / `5x10x35` / `5x15x16` | the box itself |
| `5x15x18` | — (already closed 9+9) |

## 8. What was not done

No truth table (`RAW_PRIMES`, `PUBLISHED_SOLUTIONS`,
`SEARCHED_NO_SOLUTION`, impossible rules) was modified; `ROW_FAMILIES`,
`WIDTH_SPLITS`, and the certificate protocol are untouched; no `s:0`/
family-row evidence was encoded; no searches were run. All numbers derive
from `classify()` over the real catalogue plus the archived page HTML.
