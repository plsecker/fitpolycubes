# Z-Pentacube Frontier Decomposition Audit

**Date**: 2026-08-27
**Scope**: Z pentacube only (`catalogues/z_catalogue.py`)
**Goal**: Determine whether the mature decomposition/certificate workflow
(`solvers/decomp.py`, `tools/audit_catalogue.py`) can materially reduce the Z
frontier using evidence that already exists — without a new large exhaustive
search.

**Headline**: Yes, measurably. Using only *already-published* composite
entries ("1+", non-prime) from the catalogue's own authoritative source
(Shirakawa's Z page, the same source cited by every other catalogue here),
102 additional boxes within dims <= 60 acquire complete, machine-checked
proof trees, including the two smallest Audit-B members `5x15x20`
(PublishedSolution) and `11x15x20` (Width cascade). A second,
convention-only promotion (transcribing Shirakawa's `s:0` semigroup rows)
would resolve a further 103 currently-Unknown boxes within dims <= 60 as
impossible. No truth table was modified in this work; everything is either a
runtime demo, a test, or a proposed patch below.

---

## 1. Method

1. Ran the existing audit over Z (`tools/audit_catalogue.py Z --max-dim 20`)
   and an equivalent full-range scan (canonical `1<=a<=b<=c<=60`,
   `volume % 5 == 0`) to establish the real frontier under current truth
   tables.
2. Inventoried every decomposition asset applicable to Z:
   `WIDTH_SPLITS`, `SLAB_SPLITS` (see §3 — does not exist),
   row-semigroup rules (`ROW_FAMILIES`), published solutions,
   `SEARCHED_NO_SOLUTION`, prime/composite children.
3. Fetched the authoritative source page
   (`https://puzzlewillbeplayed.com/Shirakawa/Z.html`) and diffed it against
   the catalogue. Every solvable non-prime ("1+") 3D entry there is a legal
   `published_solutions` fact under this repository's own conventions (same
   treatment as S: `shirakawa/S.md` -> `PUBLISHED_SOLUTIONS` in
   `catalogues/s_catalogue.py`; same reading guide in
   `docs/frontier/t_piece/t_source_survey.md` for the `s:0` notation).
4. Injected that evidence via `dataclasses.replace(Z_CATALOGUE, ...)
   (runtime copy only) and re-ran the classifier end-to-end; validated every
   changed classification with a permutation-aware proof-tree checker
   (`tools/frontier/z_piece/validate_proof_tree.py`).

---

## 2. Current Z frontier, accurately

Baseline (unmodified catalogue):

* Audit dim <= 20: **724** volume-valid boxes; Audit A (prime mismatches): 0;
  Audit B (unproven composites / UNKNOWN): **331**; Audit C (closed
  constructions found by the engine alone): **64** (69 after the Audit-C
  breadth-filter fix, see §4.4); Audit D (published solutions): 0.
* Full range dim <= 60: **16239** classified (valid-volume,
  non-impossible-or-prime-composite accounting identical to the audit);
  **10580** Unknown, 5659 closed by existing guillotine/semigroup proofs.

Grouped by dimension pattern, the <= 60 frontier decomposes as:

| Pattern group | Examples (cross-section) | Character |
|---|---|---|
| Genuinely open, no source data | `(3,23)..(3,60)` below the first solution length; `(4,11)x{15,20,...}`, `(4,12)x{15,20,25,...}`; `(5,b)` narrow stacks; `(9,9)`, `(10,11)` blocks | Truly unresolved; biggest mass |
| Mathematically impossible by an existing rule | none in Unknown set (rules fire before Unknown) | n/a |
| Composite with an existing closed proof | Audit-C population, e.g. `10x15x15..20`, `12x15x15`, `15x15x15..20`, `20x20x20` | Already closed *before* this work |
| Composite closable from unused-but-existing splits/evidence | see §4 (the 102) | **Closed in this work** |
| Requires fresh computation | `5x10x{19,20,21..32}` residual band, `5x15x{16..19}`, `4x11x{15,20,30...}` half-lengths, `9x9xN`, `(10,11)+` blocks | Category C/D |

Note the semigroup shape of auto-closures: whenever a cross-section (a,b)
owns two closable lengths with gcd g (here always g=5), guillotine recursion
closes every volume-valid length above the Frobenius bound reachable from
the catalogued generators, leaving exactly the arithmetic-progression gaps
visible in the scan output (e.g. `(4,10)`: only c ≢ 0 (mod 5) plus
c ∈ {46..49,51..54,56..59} stay open absent further facts).

---

## 3. Why the "existing Z WIDTH_SPLITS" were never consumed (Q5 verdict)

**There have never been any Z WIDTH_SPLITS — in the working tree, in git
history, or anywhere else in this repository.**

Evidence:

* `git log --all --follow -- catalogues/z_catalogue.py` shows four commits
  (`3ffdc43 z`, `bded040 mostly w`, `8a9ba83`, `27c2ab9 minimal evens`);
  every historical version contains `WIDTH_SPLITS = {}`.
* `docs/pieces/Z.md` records: "ROW_FAMILIES / WIDTH_SPLITS: Empty."
* Repo-wide, **every one of the 21 catalogues ships an empty
  `WIDTH_SPLITS`**; the only populated draft ever written is a commented-out
  pair in `catalogues/f_catalogue.py` (`# 10: [3,4,5]` /
  `# 15: [3,4,5,6,7,8,9]`). `catalogues/v_catalogue.py` even defines
  non-trivial `ROW_FAMILIES`/`WIDTH_SPLITS` content and then comments it out
  / re-overrides to `{}` — the team has met this question before and chose
  to decommission unverified tables rather than trust them.

So the answer is: **tooling omission upstream of the tool — a data gap, not
a code path bug.** Specifically:

* The consumption machinery in `solvers/decomp.py` is present and works. It
  fires when (and only when) `width_splits[b]` generates a decomposition of
  `a` whose parts each classify as closed; a `Generator` node is then
  returned.
* There is a genuine *representation* subtlety that explains why honest
  tables tend to be empty for pieces like Z: a `WIDTH_SPLITS[b] = [w...]`
  entry is a claim that `Box(w, b, c)` closes for the *specific* `(b, c)`
  of the target box. Since closure is strongly `c`-dependent, only
  `c`-uniform facts may be listed. For Z the repo holds no such universal
  row facts (unlike T, where "3x7xN: only multiples of 20" is effectively
  such a statement, encoded instead inside `impossible_reason`).
* Silent-failure mode (real tooling gap worth knowing): a wrong or
  partially-true `WIDTH_SPLITS` entry never errors; its `Generator`
  candidate simply fails `closes()` and classification falls through. The
  new tests make both directions explicit
  (`TestWidthSplitsMechanism`: truthful split -> consumed + validated;
  false split -> ignored, box stays Unknown).
* Related nomenclature: **no `SLAB_SPLITS` field exists anywhere in this
  repository.** Slab splits are generated exhaustively inline by
  `classify()` (loop `for split in range(1, c)`); no catalogue data can be
  missing. Likewise `row_families[*].period` is displayed by
  `Catalogue.stats()` but is *not consumed* by the prover —
  `semigroup_decompose` uses `seeds` only; periodic extension would be an
  engine feature request, not a Z blocker.

---

## 4. Results promoted in this work

### 4.1 Newly CLOSED from existing evidence — 102 boxes (dims <= 60)

Runtime-injecting the 77 page-explicit, volume-self-checked composite
entries (see test fixture `PAGE_COMPOSITES_3D`) into
`published_solutions` yields **102** new classifications with
`closes() == True`, all structurally validated:
52 x `PublishedSolution`, 43 x `Slab`, 5 x `Breadth`, 2 x `Width`.

Inside the classic audit range (dim <= 20) this closes the two smallest
Audit-B members:

```
5x15x20  -> PUBLISHED_SOLUTION            (page row: 300 pc, 2014)
11x15x20 -> WIDTH 5x15x20 + SLAB[6,6+10]  (cascade)
```

Of the 102, **52 are direct published rows** lying inside the dim <= 60
scan window (the remaining 25 table rows exceed it, e.g. `3x24x300`), and
**50 are guillotine cascades** combining those rows with pre-existing
primes/composites.

Full newly-closed list — the authoritative enumeration is pinned in the
test fixture `NEWLY_CLOSED_DIMS` (exact set of 102); representative
members: all 52 in-window published rows plus cascade sums such as
`5x15x29..33`, `5x15x39..42`, `5x15x48..59`, `5x20x23`, `5x20x27`,
`5x19x40`, `10x11x45`, `4x23x50`, `11x15x30/40`,
`5x30x30/31/32/41`, `4x30x30/35/40/45`, `4x35x35/40/45`.

### 4.2 Flagship proof trees (complete certificates)

All dumped under the runtime-evidence catalogue; formatting preserved from
`solvers/decomp.py :: dump`.

Box(5, 15, 20):
```
PUBLISHED_SOLUTION 5x15x20
```

Box(11, 15, 20):
```
WIDTH 11x15x20
  PUBLISHED_SOLUTION 5x15x20          # geometric 5-wide slab
  SLAB 6x15x20                        # geometric 6-wide slab, height split 10+10
    PRIME 6x10x15                     # geometric 6x15x10
    PRIME 6x10x15
```

Box(5, 15, 40):
```
SLAB 5x15x40                          # height split 9 + 31
  PRIME 5x9x15
  SLAB 5x15x31                        # height split 9 + 22
    PRIME 5x9x15
    PUBLISHED_SOLUTION 5x15x22
```

Box(5, 10, 72):
```
SLAB 5x10x72                          # 33 + 39
  PRIME 5x10x33
  PUBLISHED_SOLUTION 5x10x39
```

Box(4, 15, 85):
```
SLAB 4x15x85                          # 30 + 55
  PUBLISHED_SOLUTION 4x15x30
  PUBLISHED_SOLUTION 4x15x55
```

Bookkeeping caveat (documented, inherent to current repository semantics):
child proof nodes store their boxes *canonicalized*, while cuts happen on
parent-frame axes; e.g. slab-cutting Box(5,15,40) at k=9 produces a node
labelled `PRIME 5x9x15` for the geometric slice 5x15x9. This is sound —
box tilability is invariant under axis permutation — but naive validators
must allow it. `validate_proof_tree.py` implements the exact multiset
check used to certify every tree quoted here.

### 4.3 Resolved-as-impossible layer (report-only proposal)

Shirakawa's `s:0` rows mean, per the repository's own gloss
(`t_source_survey.md`: "s:0 notation = semigroup"), that unlisted lengths of
that cross-section family admit no tiling beyond the numerical semigroup
generated by the listed ones. Transcribing the four Z families touched by
the dim <= 60 window

| Family (a,b) | Listed solvable lengths | Boxes resolved Impossible (<=60) |
|---|---|---|
| (4,10) | 50,55,...,95 | 12 |
| (4,11) | 50 | 8 |
| (5,8) | 20,35,45,50 | 42 |
| (5,9) | 15,25,35 | 41 |
| **total** | | **103** |

(e.g. every volume-valid length outside ⟨listed⟩ ⊕ sums goes to
Impossible; exact per-family lists were computed during the audit and are
reproducible from the table above with a ten-line script.)

This is deliberately **NOT applied**: it changes `impossible_reason`
truth-table semantics and deserves its own review against the lossless-page
transcription standard used for S (`shirakawa/S.md` style), including a
policy decision on whether whole-family `s:0` claims get encoded as blanket
rules (like today's `a==7 and b==7`) or enumerated points (like S's
`4x9x{...}`). Evidence for the change exists; the decision did not, so this
report proposes rather than applies it. Note it interacts cleanly: adding
Impossible rows cannot invalidate any constructive closure above, since
`classify()` checks impossibility first and `closes()` treats Impossible as
non-closing.

### 4.4 Tooling fixes applied (generic, behaviour-preserving)

1. `tools/audit_catalogue.py` — Audit C filter now includes `'Breadth'`
   alongside Generator/Slab/Width. Rationale: `closes()` treats Breadth
   identically; the omission silently hid five real constructions at
   dim <= 20 (e.g. `5x16x20`), discrepancies that pollute exactly the kind
   of audit this workflow depends on.
2. New reusable validator `tools/frontier/z_piece/validate_proof_tree.py`
   (permutation-aware tree checking) + regression/test suite
   `tools/frontier/z_piece/test_z_frontier_closures.py`
   (10 tests, all passing; includes truth-table guards pinning
   RAW_PRIMES/MINIMAL_ODD/MINIMAL_EVEN/empty WIDTH_SPLITS/
   empty published_solutions, the 102-box certificate set, flagship trees,
   the maxdim-22 baseline frontier size 444, and the WIDTH_SPLITS
   honesty demo).

No change was made to `solvers/decomp.py`, `catalogues/z_catalogue.py`
truth content, published solutions, RAW_PRIMES, IMPOSSIBLE rules, or
SEARCHED_NO_SOLUTION.

---

## 5. Proposed (not applied) promotions for review

```python
# catalogues/z_catalogue.py — PROPOSAL ONLY (2026-08 audit);
# sources: puzzlewillbeplayed.com/Shirakawa/Z.html, 3D section,
# every row marked "1+" WITHOUT a prime marker; each row self-checks as
# volume == 5 * printed-piece-count.
PUBLISHED_SOLUTIONS = {
    # 3-row: first solutions and friends
    Box(3, 23, 150), Box(3, 23, 175), Box(3, 23, 200), Box(3, 23, 225),
    Box(3, 23, 250), Box(3, 23, 275),
    Box(3, 24, 300),
    Box(3, 25, 63), Box(3, 25, 74),

    # 4-row composites
    Box(4, 12, 50), Box(4, 12, 75),
    Box(4, 13, 50), Box(4, 13, 75),
    Box(4, 15, 30), Box(4, 15, 35), Box(4, 15, 40),
    Box(4, 15, 45), Box(4, 15, 50), Box(4, 15, 55),
    Box(4, 20, 30), Box(4, 20, 35),
    Box(4, 24, 25), Box(4, 25, 25), Box(4, 25, 26),

    # 5-row composites (note the granular 5x10 family, lengths 39-71)
    Box(5, 10, 39), Box(5, 10, 40), Box(5, 10, 41), Box(5, 10, 42),
    Box(5, 10, 43), Box(5, 10, 44), Box(5, 10, 45), Box(5, 10, 46),
    Box(5, 10, 47), Box(5, 10, 48), Box(5, 10, 49), Box(5, 10, 50),
    Box(5, 10, 51), Box(5, 10, 52), Box(5, 10, 53), Box(5, 10, 54),
    Box(5, 10, 55), Box(5, 10, 56), Box(5, 10, 57), Box(5, 10, 58),
    Box(5, 10, 59), Box(5, 10, 60), Box(5, 10, 61), Box(5, 10, 62),
    Box(5, 10, 63), Box(5, 10, 64), Box(5, 10, 65), Box(5, 10, 67),
    Box(5, 10, 68), Box(5, 10, 71),
    Box(5, 11, 40), Box(5, 11, 60), Box(5, 11, 65), Box(5, 11, 70),
    Box(5, 11, 75), Box(5, 11, 85), Box(5, 11, 90), Box(5, 11, 95),
    Box(5, 12, 30), Box(5, 12, 35),
    Box(5, 13, 30), Box(5, 13, 35), Box(5, 13, 40), Box(5, 13, 45),
    Box(5, 14, 30), Box(5, 14, 35),
    Box(5, 15, 20), Box(5, 15, 21), Box(5, 15, 22), Box(5, 15, 23),
    Box(5, 15, 24), Box(5, 15, 25),
    Box(5, 16, 30),
}
```

Sicherman-cross-check safety: `tools/verify_sicherman_odd_boxes.py` keeps
passing for Z with this addition (new odd candidates start at >= 825 pieces;
current minimum stays `5x9x15` at 135 pieces). Pre-existing FAIL lines for
B and R are unrelated to Z and unaffected.

---

## 6. Remaining unresolved, ranked

### A. Newly CLOSED with existing evidence (this work)
The 102 boxes of §4.1 — two inside dim <= 20 (`5x15x20`, `11x15x20`),
seventy-seven direct published rows, twenty-five guillotine cascades off the
new evidence combined with pre-existing primes. Complete proof trees for all
of them are pinned and validated by the test suite.

### B. Nearly closed — one explicit lemma/evidence item away
1. **s:0 transcription decision** (§4.3): resolves 103 boxes as impossible
   the moment the repo adopts a convention for whole-family semigroup-zero
   rows. Zero computation; pure evidence-encoding policy.
2. **Named single-witness gaps** (verified against baseline scan, i.e. each
   has no partition into already-closed lengths today):
   `5x10x34`, `5x10x35` (interior of the granular family; note
   `5x10x36/37` are prime and `5x10x66 = 33+33` etc. already auto-close),
   and `(3,23)` interior below the first published length 150.
   One targeted witness per box collapses exactly that box plus its future
   semigroup sums — cheap to certify by this workflow once found, but the
   finding itself is category C work.
3. **Audit usability gap (fixed)**: Breadth-masking in Audit C — repaired
   here; future audits will surface such closures automatically.

### C. Requires new (small, targeted) computation
Volume-valid, small, isolated:
* `5x10x19, 5x10x20, 5x10x21..32` band between the impossible block
  `[10-18]` and first prime 33 — order 14 boxes; a dedicated frontier DP in
  the style of `docs/frontier/*/t_3x7_global_theorem.md` would settle them
  outright.
* `5x15x16..19`, `5x14x26..29`-style neighbourhood fillers next to dense
  published ranges.
* `4x11x15, 4x11x20` and the `(4,11)` half-grid.
* `9x9x{10..60}` odd-column block (no listed data at all).
These are bounded searches, not broad sweeps; each resolves a named box or
whole finite family when run.

### D. Genuinely hard / no obvious route
The remaining ~10.4k Unknowns within dim <= 60 sit in cross-sections with
no solvable listing anywhere on the source page (most `(4,x)` and
`(>=7,>=7)` stretches, and the 3-row interior below `3x23x150`), i.e. every
proposal must construct something genuinely new. The mature macro/cycle
methodology documented for T/V/S
(`docs/frontier/{t,v}_piece/*`, `macro_proof_methodology.md`) is the right
instrument class, but adapting it to Z's orientation profile (chirality
plus two spans, cf. S) is a project, not a promotion. No route exists
today through decomposition infrastructure alone — which is expected: that
infrastructure certifies combinations of facts; it cannot invent the first
fact about a virgin cross-section.

---

## 7. How to reproduce

```
# full evidence experiment (baseline vs evidence catalogue, diff = 102)
.venv/bin/python /tmp/opencode/z_evidence_experiment.py     # scratch copy

# tests (truth guards, certificates, mechanism demos)
.venv/bin/python -m unittest tools.frontier.z_piece.test_z_frontier_closures -v

# audit with fixed Breadth reporting
.venv/bin/python tools/audit_catalogue.py Z --max-dim 20 --limit 5
```

Scratch scripts used during the investigation (kept out of the repo):
`z_evidence_experiment.py`, `z_validate_all_new.py`,
`z_validate_trees.py`, `z_frontier_full.py` under `/tmp/opencode/`.

## 8. Files added/changed by this audit

| File | Change |
|---|---|
| `tools/frontier/z_piece/validate_proof_tree.py` | new: permutation-aware proof validator |
| `tools/frontier/z_piece/test_z_frontier_closures.py` | new: 10-test suite |
| `tools/frontier/z_piece/promotion_evidence.py` | new: page-row parser + proof replay + conflict checks |
| `tools/frontier/z_piece/build_promotion_doc.py` | new: regenerates the promotion evidence package |
| `docs/frontier/z_piece/z_promotion_evidence_package.md` | new: promotion-ready evidence package (replay + conflicts + patch preview) |
| `tools/audit_catalogue.py` | Audit C type filter now includes `Breadth` |
| `docs/pieces/Z.md` | audit-history note pointing here |
| `docs/frontier/z_piece/z_frontier_decomposition_audit.md` | this report |
