# Z Next Step: Explicit Impossibilities + the 6×6×10 Search

**Date**: 2026-08-28
**Scope**: Part A — document two explicit Shirakawa impossibility rows
(proposal only, NOT applied). Part B — one bounded search for `6x6x10`.
Part C — model the combined frontier effect. The real catalogue truth
tables are unchanged (only the already-approved 77-row promotion diff
remains in `catalogues/z_catalogue.py`).

---

## Part A — explicit source impossibilities (proposal only)

### A.1 `5×10×[10–18]` — explicit zero block (9 boxes)

Verbatim HTML row (authoritative source, 3D section):

```html
<tr><td class="nump"></td><td class="size">5x10x[10-18]</td>
    <td class="sols">0</td><td class="remark"></td>
    <td class="date">2013</td><td class="who">Shirakawa</td></tr>
```

Semantics: sols cell `0` (unlinked) = Shirakawa asserts **zero solutions for
every length 10–18** of the `5×10` family. This is a *plain explicit zero* —
no semigroup interpretation involved — exactly the same class of fact as the
already-encoded `4x10x[10-45]` block. The nine boxes are currently all
`Unknown`; none is prime, published, or searched.

### A.2 `3×23×50` — per-box `s:0` (1 box)

```html
<tr><td class="nump">690</td><td class="size">3x23x50</td>
    <td class="sols">s:0</td><td class="remark"></td>
    <td class="date">2013</td><td class="who">Shirakawa</td></tr>
```

Semantics: per-box `s:0` (with piece count 690, self-consistent:
`3·23·50 = 5·690`) — semigroup-based zero for this single box. Consistency
check from the same page: the `3×23` family's only solvable rows are at
lengths 150–275 (`1+`), so `50` cannot be reached from listed constructions
(`gcd 25`), matching the semigroup reading codified in
`docs/frontier/t_piece/t_source_survey.md`. Box currently `Unknown`.

### A.3 Proposed catalogue change (REVIEW-READY, NOT APPLIED)

Addition inside `ZCatalogue.impossible_reason`, immediately after the
existing `4x10x[10-45]` rule (house style preserved):

```python
        #
        # 5x10x[10-18]: 0 -- Shirakawa 2013 (explicit zero block)
        #
        if (a, b) == (5, 10) and 10 <= c <= 18:
            return "published_impossible"

        #
        # 3x23x50: s:0 -- Shirakawa 2013 (per-box semigroup zero)
        #
        if box == Box(3, 23, 50):
            return "published_impossible"
```

Safety analysis (measured): the ten boxes are currently `Unknown`, so no
closed proof tree contains them (Unknown leaves never satisfy `closes()`);
adding the rules can therefore only convert those ten `Unknown → Impossible`
and change nothing else. Verified by the runtime model in Part C: exactly 10
transitions, zero side effects. No overlap with `RAW_PRIMES`,
`PUBLISHED_SOLUTIONS`, or `SEARCHED_NO_SOLUTION`.

---

## Part B — the 6×6×10 targeted search

### B.1 Pre-search constraint check (task 5)

* Classification: `Unknown` (engine exhausted: all 9 slab splits hit
  `Impossible` parts — thicknesses 1–9 are covered by the `a ≤ 2`,
  `3x[3-22]`, `4x[4-9]`, `5x{5,6,7}` families; no width/breadth route).
* `impossible_reason`: none; volume 360 = 72 pieces ✓.
* Not in `RAW_PRIMES` / `PUBLISHED_SOLUTIONS`; **absent from the Shirakawa
  page entirely** (no `6x6x10` row — no source claim either way).
* Piece structure: `Z` is flat (cells `(0,0,0),(1,0,0),(1,1,0),(1,2,0),
  (2,2,0)`), **12 orientations**, all planar; **2,176 placements** in the box.
* Colouring sanity: each piece covers residues `x+y+z ∈ {0,1,2,3,4} mod 5`
  exactly once, and the box has exactly 72 cells per residue → no mod-5
  obstruction; checkerboard splits 3/2 per piece, 180/180 box, 36/36 pieces
  → no parity obstruction.

Conclusion: a fresh search is genuinely necessary.

### B.2 Method

`solvers/fitpolycubes_hybrid.py` (repo standard: multiprocessing + Numba
Algorithm X, min-remaining-values column choice, symmetry breaking — 3
non-canonical `(0,0,0)` placements removed), 3 workers on a 4-core box,
**bounded: `--max-solutions 1`, hard 3600 s wall timeout**. 56 depth-4
parallel tasks were generated. Solution output would have landed in
`data/solutions_hybrid_z_6x6x10.dat`; a `SOLUTION_FOUND` flag is raised by
the writer on first solution.

### B.3 Result and completeness status

* **No solution found within the bounded window.**
* **The search was NOT exhaustive**: at timeout one worker was still inside
  a single **depth-1** branch (placement prefix `(765,)`) after
  **20m38s / 189,037,866 nodes**; another had spent >91M nodes on
  `(2169, 181, 1842, 58)`. Aggregate rate ≈ 435k nodes/s across workers
  (~1.5B nodes over the hour, buffered heartbeats).
* Therefore `6x6x10` remains **Unknown / inconclusive**. Per the task rules
  it is **not** classified impossible, and no catalogue change was made.
* Evidence artifacts: search log `/tmp/opencode/z6610_search.log`
  (out-of-repo); the empty result file was removed; no
  `SOLUTION_FOUND` flag exists (correct for a negative/inconclusive run).

### B.4 What an exhaustive answer would require (task 9 estimate)

The MRV heuristic is already in place; the deficit is raw tree size and
parallel width:

1. **CPU**: linear scale-up — 32–64 workers instead of 3 (≈ 10–20×).
2. **Planar-structure pruning**: every placement lies in a *single
   axis-parallel plane* (the piece is flat in all 12 orientations). A
   layer/pair-of-layers DP over plane occupancy — the same frontier
   technique the repo already used for S `4×8` — would replace flat DLX and
   likely cut the tree by orders of magnitude.
3. **Alternative engine**: a SAT/CP encoding (e.g. kissat) of the 2,176×360
   cover would probably settle existence in minutes-to-hours.

Honest estimate on this box as-is: an exhaustive DLX proof is tens of hours;
with (1)+(2) or (3) it is a few hours or less. **Decision: STOP — no
uncontrolled search.**

---

## Part C — strategic effect (modeled, not applied)

Model M1 (runtime `ZCatalogue` subclass adding the two Part-A rules; full
≤60³ rescan against the real catalogue):

| transition | count |
|---|---|
| `Unknown → Impossible` | **10** (exactly the ten Part-A boxes) |
| any other change | **0** |
| Unknown total | 10,478 → **10,468** |

Model M2 (`6x6x10` solvable → promoted evidence) is **moot**: the search was
inconclusive, so no certified fact exists to model. Had a tiling been found,
the measured leverage was **+8 in-window closures**
(`6x6x10` itself plus `20,30,35,40,45,55,60` via slab chains).

Combined with the earlier frontier numbers: the ten Part-A boxes are the
cheapest certified frontier reduction available today; everything else waits
on the §7 shortlist of `z_post_promotion_frontier.md`.

---

## Bottom line

* Part A: two explicit source impossibilities documented; **review-ready
  patch proposed and NOT applied** (10 boxes, zero-risk by construction).
* Part B: `6x6x10` was already unconstrained; the bounded search ran
  **60 minutes, found nothing, and was not exhaustive** → box remains
  `Unknown`; **STOP** honoured; optimisation estimate recorded.
* Part C: modeled effect of the 10 impossibilities = −10 Unknown, no side
  effects; the real catalogue is unchanged apart from the approved promotion.
