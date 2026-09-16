# Shirakawa Corpus Gap Audit

Date: 2026-09-16
Scope: classify every existing NO-RECORD solver solution (witness-bearing `data/solutions_*.dat`) against the Shirakawa corpus (`shirakawa/*.md`) and the live published pages at `https://puzzlewillbeplayed.com/Shirakawa/`.

## Result

All 34 witnessed (piece, box) pairs are reconciled against the corpus. **No genuine corpus omissions remain:**

- 22 `EXPLICIT_RECORD`, 4 `OTHER_PUBLISHED_EVIDENCE`, 1 `COMPOSITE_EXPLAINED` case (S 5×6×28), 1 `UNRESOLVED` (I 1×1×5).
- The six apparent gaps (S 4×6×10, S 5×6×8, S 5×8×12, S 5×8×18, U 3×9×10, Y 2×5×10) are **all composite boxes derivable from published primes** on the same pages (prover-verified decompositions, see the investigation section). The Shirakawa pages are prime/decomposition catalogues, so absence of a concrete composite box is not evidence of a corpus omission.
- S 5×6×28 is **not a prime/corpus gap**: it is trivially composite because 5×6×28 = 7 × (4×5×6), and 4×5×6 is a published S prime. The local witness is therefore an explicit decomposition witness, not a new prime exception. The published `5x6x[25-28] = 0` range is still a data error for N = 28 (25–27 remain uncontradicted), but the error is simply failure to recognize the composite construction.
- I 1×1×5 remains **unresolved**: no I page exists in the corpus (live `I.html` is 404), so there is no published record to cite; the tiling itself is trivial.

## 1. Method

**Inputs.** 80 `data/solutions_*.dat` files; 41 contain witnesses (any non-header, non-count line with ≥5 coordinate tuples — handles both `((x,y,z),...)` and compact Shirakawa-SVG `(x,y,z)(x,y,z)...` formats). These cover 34 unique (piece, box) pairs. The previous audit's candidate list was **not durable**; it was rebuilt from scratch for this report.

**Corpus parsing.** `tools/frontier/shirakawa_gap_audit.py` (new, non-destructive, reusable) parses all 29 `shirakawa/*.md` files with a dual-format parser:
- Format A rows: `nump size [size:..] sols [sols href] [remark] date who` (status = field 3)
- Format B rows (R.md only): `nump size sols remark date who` (status = field 2)
- Detection: field 2 starts with `[size` → Format A, else Format B.

Family/range statements (e.g. `5x6x[25-28]`) are matched against candidate boxes by trying all 6 permutations of the canonical dimensions.

**Parser correction.** The older `tools/frontier/parse_shirakawa.py` mis-parses R.md (Format B) statuses: it reports 38 status-0 boxes, the corrected parse finds **70** (38 + 32 R.md rows). Record existence is unaffected (416 concrete records in both). Corrected corpus totals: **416 concrete records** (295 status `1+`, 70 status `0`, 51 with exact counts), **48 family statements**.

**Live-page verification.** F, U, V, N, W, Y, I pages fetched directly (2026-09-16). `I.html` returns 404 — no I page exists. All other pages confirmed current ("Complete." / "3D Complete.").

**Witness validation.** Every witness file re-checked: unique cells, bounding box, cell count divisible by 5. All 41 valid. The S 5×6×28 witness was additionally verified piece-wise: all 168 five-cell groups are congruent to the S pentacube (24 orientations), covering the 5×6×28 box exactly.

**Classification scheme.**
- `EXPLICIT_RECORD` — concrete corpus row or live-page row for the exact box
- `FAMILY_COVERED` — positive family/range statement covers the box
- `STATUS_0` — status-0 record or family statement covers the box
- `OTHER_PUBLISHED_EVIDENCE` — published 2D sections of the same corpus, documented live pages, or published solution files (SVGZ)
- `GENUINE_GAP` — genuinely absent from the complete corpus pages
- `UNRESOLVED` — the corpus does not let us decide

**Completeness caveat.** Only A, B, E, H, J, K, M, S have full raw inventories (plus R in plain format); 19 files are summaries only; **no I.md or Q.md ever existed in git** (verified `git log --all`). Where a piece's corpus file is incomplete, live pages were used as primary evidence.

## 2. Candidate table

All 34 witnessed (piece, box) pairs, classified (initial pass; the six `GENUINE_GAP` entries are resolved in the dedicated investigation section below). "Witness" = local solver solution file(s).

| piece | box | witness file(s) | classification | evidence |
|---|---|---|---|---|
| F | 5×6×6 | `solutions_hybrid_f_6x5x6.dat` | EXPLICIT_RECORD | live F page: `36 \| 5x6x6 \| prime minimal \| 158 \| Sillke 1993` |
| I | 1×1×5 | `solutions_fast_i_1x1x5.dat` | UNRESOLVED | no I.md ever existed; live I.html is 404. I trivially tiles 1×1×5 (the piece IS the box), but no published record exists to cite |
| L | 1×2×5 | `solutions_fast_l_1x2x5.dat` | OTHER_PUBLISHED_EVIDENCE | L.md 2D 1-sided: "minimal prime is 2x5" (thickness-1 box = 2D rectangle) |
| N | 5×5×5 | `solutions_hybrid_n_5x5x5.dat`, `solutions_mp_n_5x5x5.dat` | EXPLICIT_RECORD | live N page: `25 \| 5x5x5 \| prime \| 4 \| Postl 1998`; N.md: "The 5x5x5 box has 4 solutions (prime)" |
| P | 1×2×5 | `solutions_fast_p_1x2x5.dat` | OTHER_PUBLISHED_EVIDENCE | P.md 2D: "Only the 2x5 minimal prime is listed for 2D 1-sided and 2D" |
| Q | 2×2×5 | `solutions_fast_q_2x2x5.dat` | OTHER_PUBLISHED_EVIDENCE | live 5-22 page (documented in `docs/frontier/q_piece/q_geometry_integrity_audit.md`): 2x2x5 prime minimal, Sillke 1993 |
| Q | 2×3×5 | `solutions_fast_q_2x3x5.dat` | OTHER_PUBLISHED_EVIDENCE | live 5-22 page: 2x3x5 prime, Sillke 1993 |
| S | 4×5×6 | `solutions_s_5x6x4.dat` | EXPLICIT_RECORD | S.md: `24 \| 4x5x6 \| prime minimal \| 1 \| Hamlyn 1993` |
| S | 4×6×10 | `solutions_s_4x10x6.dat` | GENUINE_GAP | S.md full transcription: no 4x6xN entries at all |
| S | 4×9×60 | `solutions_s_4x9x60_shirakawa.dat` | EXPLICIT_RECORD | S.md: `4x9x60 prime 1+ Shirakawa 2014` |
| S | 4×9×75 | `solutions_s_4x9x75_shirakawa.dat` | EXPLICIT_RECORD | S.md: `4x9x75 prime 1+ Shirakawa 2014` |
| S | 4×9×90 | `solutions_s_4x9x90_shirakawa.dat` | EXPLICIT_RECORD | S.md: `4x9x90 prime 1+ Shirakawa 2014` |
| S | 4×9×105 | `solutions_s_4x9x105_shirakawa.dat` | EXPLICIT_RECORD | S.md: `4x9x105 prime 1+ Shirakawa 2014` |
| S | 4×10×10 | `solutions_s_4x10x10.dat` | EXPLICIT_RECORD | S.md: `80 \| 4x10x10 \| prime \| 1+ \| Postl 1998` |
| S | 5×6×8 | `solutions_s_5x8x6.dat` | GENUINE_GAP | S.md full transcription: 5x6x8 absent, sits between impossible ranges `5x6x[6-7]` and `5x6x[9-11]` (both 0, Sillke 1993) |
| S | 5×6×28 | `solutions_s_5x6x28.dat` | COMPOSITE_EXPLAINED | S.md + live S page: `5x6x[25-28] = 0` (Shirakawa 2014); but 5×6×28 = 7 × (4×5×6), and 4×5×6 is a published S prime. The 168-piece witness is therefore a decomposition witness, not a new prime exception. |
| S | 5×7×24 | `solutions_s_5x7x24_shirakawa.dat` | EXPLICIT_RECORD | S.md: `168 \| 5x7x24 \| prime \| 1+ \| Sillke 1998` |
| S | 5×7×36 | `solutions_s_5x7x36_shirakawa.dat` | EXPLICIT_RECORD | S.md: `5x7x36 prime 1+ Sillke 1998` |
| S | 5×7×42 | `solutions_s_5x7x42_shirakawa.dat` | EXPLICIT_RECORD | S.md: `5x7x42 prime 1+ Sillke 1998` |
| S | 5×8×12 | `solutions_s_5x8x12.dat` | GENUINE_GAP | S.md full transcription: no 5x8xN entries at all |
| S | 5×8×18 | `solutions_s_5x8x18.dat` | GENUINE_GAP | S.md full transcription: no 5x8xN entries at all |
| S | 5×9×12 | `solutions_s_5x9x12_shirakawa.dat` | EXPLICIT_RECORD | S.md: `108 \| 5x9x12 \| prime \| 1+ \| Shirakawa 2014` |
| S | 5×9×15 | `solutions_s_5x9x15_shirakawa.dat` | EXPLICIT_RECORD | S.md: `5x9x15 prime 1+ Shirakawa 2014` |
| S | 5×9×18 | `solutions_s_5x9x18_shirakawa.dat` | EXPLICIT_RECORD | S.md: `5x9x18 prime 1+ Shirakawa 2014` |
| S | 5×9×21 | `solutions_s_5x9x21_shirakawa.dat` | EXPLICIT_RECORD | S.md: `5x9x21 prime 1+ Shirakawa 2014` |
| S | 5×10×18 | `solutions_s_5x10x18_shirakawa.dat` | EXPLICIT_RECORD | S.md: `180 \| 5x10x18 \| prime \| 1+ \| Shirakawa 2014` |
| U | 3×9×10 | `solutions_hybrid_u_3x9x10.dat` | GENUINE_GAP | live U page "Complete." lists only 10 3D primes (all Sillke 1993); 3x9x10 absent; valid local witness → tileable composite box not recorded |
| U | 4×5×5 | `solutions_hybrid_u_5x5x4.dat` | EXPLICIT_RECORD | live U page: `20 \| 4x5x5 \| prime \| 2 \| Sillke 1993` |
| U | 5×5×11 | `solutions_hybrid_u_5x5x11.dat` | EXPLICIT_RECORD | live U page: `55 \| 5x5x11 \| prime \| 1+ \| Sillke 1993` |
| V | 5×5×6 | `solutions_fast_v_5x5x6.dat`, `solutions_numba_v_5x5x6.dat` | EXPLICIT_RECORD | live V page: `30 \| 5x5x6 \| prime \| 9 \| Sillke 1993` |
| V | 5×5×9 | `solutions_fast_v_5x5x9.dat`, `solutions_fast_v_5x5x9_282_baseline.dat`, `solutions_fast_v_5x5x9_checkpoint.dat`, `solutions_hybrid_v_5x5x9.dat`, `solutions_v_5x5x9_complete.dat` | EXPLICIT_RECORD | live V page: `45 \| 5x5x9 \| prime \| 1+ \| Sillke 1993` |
| W | 5×7×9 | `solutions_cpp_w_5x7x9.dat`, `solutions_w_5x7x9_shirakawa.dat` | EXPLICIT_RECORD | live W page: `63 \| 5x7x9 \| prime \| 1+ \| Shirakawa 2014`; published SVGZ `https://puzzlewillbeplayed.com/Shirakawa/svgz/W/W-5x7x9.svgz` (see `docs/frontier/w_5x7x9_svgz_analysis.md`) |
| Y | 1×5×10 | `solutions_fast_y_1x5x10.dat` | EXPLICIT_RECORD | live Y page 2D: `5x10 \| prime minimal \| 4 \| Golomb 1966` (thickness-1 box = 2D rectangle) |
| Y | 2×5×10 | `solutions_hybrid_y_2x5x10.dat` | GENUINE_GAP | live Y page "3D Complete." lists 22 3D primes (2x5x6, 2x5x8, 2x5x11, 2x5x13, 2x5x15 among them); 2x5x10 absent; valid local witness → tileable composite box not recorded |

Counts by classification: **EXPLICIT_RECORD 22, OTHER_PUBLISHED_EVIDENCE 4, GENUINE_GAP 6, COMPOSITE_EXPLAINED 1, UNRESOLVED 1**. No `FAMILY_COVERED` (positive) cases with witnesses. **The six `GENUINE_GAP` entries are the initial classification only — all six are resolved as composite boxes in the investigation section below (0 remain genuine gaps).**

## 3. Genuine gaps

Six boxes are absent from the Shirakawa corpus pages yet have valid local tilings (initial classification `GENUINE_GAP`; all six are resolved below):

1. **S 4×6×10** — S.md is a full raw transcription; it contains no 4×6×N entries at all. Witness: `solutions_s_4x10x6.dat` (48 pieces, exact 4×10×6 box).
2. **S 5×6×8** — absent from S.md; sits between the impossible ranges `5x6x[6-7]` and `5x6x[9-11]` (both 0, Sillke 1993). The alternating impossible/tileable pattern (…[6-7], 8, [9-11], 12, [13-15]…) makes 8 the first tileable length. Witness: `solutions_s_5x8x6.dat` (48 pieces).
3. **S 5×8×12** — S.md contains no 5×8×N entries at all. Witness: `solutions_s_5x8x12.dat` (96 pieces).
4. **S 5×8×18** — same; no 5×8×N entries. Witness: `solutions_s_5x8x18.dat` (144 pieces).
5. **U 3×9×10** — the live U page states "Complete." and lists exactly 10 3D primes (2x3x5, 2x10x10, 2x10x14, 2x11x20, 2x11x25, 3x3x10, 3x5x7, 4x4x5, 4x5x5, 5x5x11, all Sillke 1993) plus 3 4D primes. 3×9×10 is absent; the page records primes only, so absence means "not prime". Witness: `solutions_hybrid_u_3x9x10.dat` (54 pieces) → tileable composite box not recorded.
6. **Y 2×5×10** — the live Y page states "3D Complete." and lists 22 3D primes (2x4x10, 2x4x15, 2x5x6, 2x5x8, 2x5x11, 2x5x13, 2x5x15, 2x7x10, 2x7x15, 3x4x5, 3x5x9, 3x5x11, 3x6x10, 3x6x15, 3x7x10, 3x7x15, 4x4x5, 4x5x5, 5x5x5, 5x5x6, 5x5x7, 5x7x7). 2×5×10 is absent (0 occurrences of `2x5x10`/`10x5x2` in the page). Witness: `solutions_hybrid_y_2x5x10.dat` (20 pieces) → tileable composite box not recorded.

Each of these six is investigated in the dedicated section below; all six resolve as composite boxes derivable from published primes (none is a missing published solution).

## 4. Unresolved

**I 1×1×5** — the only unresolved case. No I.md ever existed in the repo (verified `git log --all`), and the live `I.html` returns 404: the Shirakawa collection has no I page at all. The I pentacube trivially tiles 1×1×5 (the piece is the box), and the local witness `solutions_fast_i_1x1x5.dat` confirms it, but there is no published record to cite. Classified UNRESOLVED because the corpus cannot decide; the triviality note above is the practical resolution.

**Flagged classification issue — S 5×6×28.** The corpus (S.md and the live S page) records `5x6x[25-28] = 0` (Shirakawa 2014). The local witness is valid, but it does not constitute a new prime exception: 5×6×28 = 7 × (4×5×6), and 4×5×6 is already a published S prime. The range-level `0` is therefore erroneous for N=28 because the box is composite/tileable, not because we discovered an overlooked prime case. See the dedicated section below.

**Corpus-internal inconsistency (context).** S.md's narrative note says: "Sillke says 4x10x14 and 4x9x15 are possible, but they are impossible. The solutions of 4x10x14, 4x9x15 and 5x7x30 are wrong." — while the S.md table lists `5x7x30 \| prime \| 1+ \| Sillke 1998`. The corpus itself contains corrections of Sillke's data, which is relevant context for how much weight to give published impossibility claims.

## S 5×6×28 composite-case resolution

**Verdict: COMPOSITE, VALID WITNESS** — the repository contains a genuine, independently verified S-pentacube tiling of 5×6×28, but this is exactly what should be expected from the published 4×5×6 prime: 5×6×28 = 7 × (4×5×6).

### Witness and provenance

- **Witness file**: `data/solutions_s_5x6x28.dat` (gitignored via `data/*.dat` — untracked by design; created 2026-08-23 14:25). Header: `# Polycube solutions - Macro construction (5x6x28, 168 pieces)`; one solution line, 168 pieces. Filename, header, and content agree (5×6×28, 168 pieces = 840/5) — no mislabelling.
- **Generator**: `tools/frontier/macro_construction.py`, fed with the verified length-4 macro cycle from `tools/frontier/_5x6_concrete_cycles.json` (extraction date 2026-08-23; verified cycle lengths {4, 29, 46, 47}; Frobenius number 43, conductor 44; complete 5×6 macro graph, SCC size 1606).
- **Reproduction**: `construct_tiling(28, cycle_data=...)` from the documented pipeline reproduces the witness **piece-for-piece identically** (168/168 pieces match).
- **Cycle structure**: the tiling is 7 concatenated copies of the length-4 cycle `0 → 864691132618894599 → 37155264724603827 → 1073741823 (FULL) → 0`; `extract_cycle_from_tiling.extract_cycle` verifies every layer transition is a legal macro edge and the gate (FULL,0,0) state is visited (gate index 3). The extracted state sequence matches the stored cycle path exactly.

### Independent validation chain (four independent implementations)

1. **Trusted repo machinery** — `common/polycube_utils.generate_placements(PENTACUBES['S'], (5,6,28), break_symmetry=False)` (the same machinery used by `tools/verify_witness_00_001.py`): generates 5428 valid S placements in the box under the 24 proper rotations (RM, det=+1, no reflections). All 168 witness pieces are in the placement set; union = exactly the 840 box cells; no duplicates, no missing, no out-of-bounds.
2. **Stdlib-only checker** (signed permutation matrices with det=+1 filter; same style as `tools/frontier/check_macro_certificate_independent.py`): S has 12 distinct orientations under proper rotations (chiral; mirror not reachable). All 168 pieces are congruent to S under proper rotations; exact disjoint cover of 5×6×28.
3. **`tools/frontier/macro_certificate.py --placements`** (independent S validator; "does NOT share any code with the macro construction tool"): 168 pieces, 840 cells, 0 invalid shapes, 0 out of bounds, 0 overlaps, 0 missing, 0 extra → VALID.
4. **`tools/frontier/macro_construction.validate_construction`**: valid=True, 168 pieces, 840 cells, no errors.

### Convention checks

- **No reflections**: S is chiral (proper-rotation orbit size 12; mirror absent — confirmed by the chirality note in `data/frontier/certificates/s_4x5x6_solution01_macro_walk.json` and behaviourally in `docs/frontier/certificate_interop_report.md`: "mirror-of-S rejected"). Paths 1 and 2 both restrict to proper rotations (det=+1) and both pass → the witness uses only proper rotations, consistent with the repo's canonical convention and with the Shirakawa page's one-sided 3D classification (per `catalogues/s_catalogue.py`).
- **Catalogue conventions**: the repo's certificate machinery rejects improper-rotation (x-reflected) fill pieces on S (certificate_interop_report.md); the witness passes under this convention. The S catalogue is a classification catalogue (no placement convention of its own); placement conventions are defined by `generate_placements` (proper rotations) and the certificate machinery (det=+1).
- **Piece identity**: the witness uses the registry S geometry (`common/registry.py`: Kuenzell 21 = Shirakawa 5-15), the same geometry the macro pipeline and catalogue use. No stale or malformed data: the file parses cleanly and every check above passes on the raw file.

### The Shirakawa source statement (unchanged)

`shirakawa/S.md` (lossless transcription of https://puzzlewillbeplayed.com/Shirakawa/5-15.html), summary table:

```
|  | 5x6x[25-28] |  | 0 |  |  | 2014 | Shirakawa |
```

raw table:

```
	5x6x[25-28]	[size: ]	0	[sols href: ]	[remark: ]	2014	Shirakawa
```

Live page (fetched 2026-09-16) row: `5x6x[25-28] | 0 | 2014 | Shirakawa`. Adjacent rows: `5x6x[21-23] = 0` (Shirakawa 2014), `5x6x29 = prime, 1+` (Shirakawa 2014), `5x6x[30-31] = 0` (Shirakawa 2014).

### What this means for the Shirakawa `0` claim

The published claim `5x6x[25-28] = 0` (Shirakawa 2014) is **wrong for N = 28**, but for a simple reason: 5×6×28 = 7 × (4×5×6), and 4×5×6 is a published S prime (Hamlyn 1993). Thus N=28 is a composite tileable case and should not be treated as a prime/corpus-gap anomaly. Our independently verified 168-piece witness is consistent with this decomposition; the macro implementation realizes it as seven copies of the verified length-4 cycle. The claim may still hold for N = 25, 26, 27 (no local witnesses exist for those), but those are separate questions. No new prime exception is established here.

## Historical status of the S 5×6×28 discrepancy

### Exact published claim

`5x6x[25-28] = 0` (Shirakawa 2014), i.e. the S-pentacube boxes 5×6×25 through 5×6×28 are claimed impossible. It appears in exactly one published source, the Shirakawa S page (https://puzzlewillbeplayed.com/Shirakawa/5-15.html), and is recorded in the repository as:

- `shirakawa/S.md` line 86 (summary table) and line 197 (raw table) — the lossless transcription;
- the live page (fetched 2026-09-16): row `5x6x[25-28] | 0 | 2014 | Shirakawa`, adjacent to `5x6x[21-23] = 0` and `5x6x29 = prime, 1+` (both Shirakawa 2014);
- `catalogues/s_catalogue.py` — the range is encoded as `published_impossible`, which currently includes 5×6×28.

No earlier source exists in the repository (the `shirakawa/*.md` files are transcriptions of the current live pages; there is no older edition of the S page in the repo). The claim is a **range-level** statement: the page lists the range with a single `0` and no per-N breakdown.

### Exact verified local construction

`data/solutions_s_5x6x28.dat` — 168 S-pentacubes covering the 5×6×28 box exactly (840 cells), validated by four independent implementations and reproduced piece-for-piece from the documented macro pipeline (7 concatenated copies of the verified length-4 cycle `0→s1→s2→FULL→0`). This is a concrete witness of the obvious decomposition into seven 4×5×6 blocks; it does not establish a new prime case.

### Is a later correction already present in the corpus?

- **In the corpus transcription files (`shirakawa/*.md`): no.** The `5x6x[25-28]` row carries no annotation, and the live page (last updated Feb 18, 2015) has no correction for it. The page's only correction note concerns Sillke's data (4x10x14, 4x9x15, 5x7x30).
- **In the repository's research documentation: yes, already recorded (2026-08-23 survey; committed 2026-09-03/09):**
  - `docs/frontier/s_piece/macro_width_survey.md` — "Catalogue comparison — 5×6×28 resolution": provenance analysis ("The source data lists the range [25-28] with 0 solutions. This is a range-level classification, not an individual check for z=28. The 4-cycle was not known to Shirakawa (2014), so 28 = 7×4 could not have been identified as tileable.") and a **Correction** note: "The catalogue's IMPOSSIBLE classification for 5×6×28 is incorrect… The values 25, 26, 27 remain correctly classified as impossible (they are not in the semigroup ⟨4,29,46,47⟩)." The z<44 classification table marks 28 as **CORRECTED — tileable**.
  - `docs/frontier/s_piece/consolidated_results.md` — "5×6×28 catalogue 'impossible' | **RESOLVED** | Catalogue error; 28 = 7×4 is tileable via Macro construction"; "1 catalogue error corrected (5×6×28)".
  - `docs/frontier/s_piece/macro_research_status.md` — "5×6×28 tileable (catalogue said impossible)".
  - `data/frontier/s_piece/macro_width_survey.json` — machine-readable `catalogue_contradiction_resolved: "5x6x28 is tileable; source range [25-28] had error for z=28"`; its `published_impossible` list already reads `…25-27,30-31…` (28 excluded).
  - Regression tests `tools/frontier/test_macro_construction.py` and `test_macro_semigroup.py` already treat 28 as representable and exclude it from the non-representable list (25, 26, 27 remain).

### Correct interpretation

The published range row is still erroneous for N=28, but it should be interpreted as a **composite/tileability classification error**, not as evidence of a missing prime. Before treating any solver witness absent from Shirakawa as a corpus anomaly, the decomposition check against already-published primes should be applied first. For N=28 that check is immediate: 28 = 7×4, with 4×5×6 already published as prime. Any future catalogue annotation should state this explicitly.

### What remains open

No additional verification is needed to establish the basic point about N=28: the published 4×5×6 prime already gives a seven-block construction. The existing witness and independent validations are useful confirmation, but they are not necessary to recognize compositeness. N = 25, 26, 27 remain separate published-impossible cases; nothing in this audit changes them.

## Investigation of the six genuine gaps

The six `GENUINE_GAP` candidates from §3 are boxes that are **absent from the corpus pages** yet have valid local tilings. This section determines, for each, whether the absence is a genuinely missing published solution or is explained by evidence already present in the repository / Shirakawa material. **No new solver searches were run.** The analysis uses (a) the full transcriptions and live pages, (b) the repository's decomposition prover `solvers/decomp.py` (`classify`), and (c) existing macro surveys and witnesses.

**Key structural facts.** The Shirakawa pages are **prime catalogues**: they list prime boxes and impossible ranges, not every tileable box — composite tileable boxes are omitted by design (e.g. U's 2×10×20 = 2×(2×10×10) is not listed). The S page claims completeness only for **"4D+ Complete."** — 3D is not claimed complete. The decomposition prover classifies **all six boxes as composite**, each decomposable into published primes listed on the same page.

| Piece | Box | Shirakawa evidence | Existing repo evidence | Classification | Conclusion |
|---|---|---|---|---|---|
| S | 4×6×10 | S page: no 4×6×N entries at all; "4D+ Complete." only (3D not claimed complete) | `classify`: Slab 4×6×10 = 4×5×6 + 4×5×6 (both Prime — 4×5×6 is the S page's prime minimal, Hamlyn 1993); 4×6 macro survey `data/frontier/s_4x6_summary.json` (tileable_N=[5]); witness `solutions_s_4x10x6.dat` (48 pieces) | COMPUTATIONAL_CORRECTION | Composite (2 × published prime 4×5×6); absence explained; **not a gap** |
| S | 5×6×8 | S page: sits between impossible ranges `5x6x[6-7]` and `5x6x[9-11]` (both 0, Sillke 1993); 4x5x6 prime minimal listed | `classify`: Slab 5×6×8 = 4×5×6 + 4×5×6; macro survey z=8 tileable (matches solver for [4, 8]); witness `solutions_s_5x8x6.dat` (48 pieces) | COMPUTATIONAL_CORRECTION | Composite (2 × published prime 4×5×6); first tileable length of the 5×6 family; absence explained; **not a gap** |
| S | 5×8×12 | S page: no 5×8×N entries at all; 3D not claimed complete | `classify`: Slab 5×8×12 = 5×6×8 + 5×6×8 (= 4 × 4×5×6); 5×8 macro survey (fundamental 6-cycle, generators [6], `tools/frontier/_5x8_concrete_cycles.json`); witness header "Stacked 5x8x6 tilings" (96 pieces) | COMPUTATIONAL_CORRECTION | Composite (2 × 5×8×6); absence explained; **not a gap** |
| S | 5×8×18 | same | `classify`: Slab 5×8×18 = 5×6×8 + 5×8×12 (= 6 × 4×5×6); witness header "Stacked 5x8x6 tilings" (144 pieces) | COMPUTATIONAL_CORRECTION | Composite (3 × 5×8×6); absence explained; **not a gap** |
| U | 3×9×10 | U page "Complete." prime catalogue: 10 3D primes (2x3x5, 3x5x7 among them, all Sillke 1993); 3×9×10 absent | `classify`: Slab 3×9×10 = 3×5×9 + 3×5×9; 3×5×9 = 2×3×5 + 3×5×7 (both published U primes); witness `solutions_hybrid_u_3x9x10.dat` (23,936 solutions, 54 pieces; no plane-split in any) | COMPUTATIONAL_CORRECTION | Composite (2 × (2×3×5 + 3×5×7)); correctly absent from a prime catalogue; **not a gap** |
| Y | 2×5×10 | Y page "2D Complete. 3D Complete. 4D Complete."; 2D section lists `5x10 \| prime minimal \| 4 \| Golomb 1966`; 3D lists 22 primes; 2×5×10 absent | `classify`: Width 2×5×10 = 1×5×10 + 1×5×10 (both Prime — 1×5×10 is the thickness-1 box of the 2D 5×10); witness `solutions_hybrid_y_2x5x10.dat` (20 pieces) | PUBLISHED_ELSEWHERE | Composite (2 × published 2D prime 1×5×10); thickness lift of published 2D data; **not a gap** |

### S 4×6×10 — composite, 2 × published prime

`classify` proves: Slab split along the 10-axis into two 4×6×5 halves, each canonical to **4×5×6** — the S page's prime minimal (24 pieces, 1 solution, Hamlyn 1993). So 4×6×10 = 2 × 4×5×6 is tileable and composite. This is consistent with the 4×6 macro survey (`data/frontier/s_4x6_summary.json`: tileable_N=[5], 5-cycle) and the witness `solutions_s_4x10x6.dat` (48 pieces). The S page contains no 4×6×N entries and claims completeness only for 4D+; a composite box is doubly explained. **Not a gap.**

### S 5×6×8 — composite, 2 × published prime

`classify` proves: Slab split along the 8-axis into two 5×6×4 halves, each canonical to **4×5×6** (published prime). So 5×6×8 = 2 × 4×5×6. It sits between the published impossible ranges `5x6x[6-7]` and `5x6x[9-11]`; the 5×6 family structure on the page (impossible ranges skipping multiples of 4, prime 4×5×6 listed) makes 8 the first tileable length. The macro survey confirms z=8 tileable and solver-matched. **Not a gap.**

### S 5×8×12 — composite, 2 × 5×8×6

`classify` proves: Slab split along the 12-axis into two 5×8×6 halves; each 5×8×6 = 2 × 4×5×6 (as above). So 5×8×12 = 4 × 4×5×6. The 5×8 macro survey (fundamental 6-cycle, generators [6], `tools/frontier/_5x8_concrete_cycles.json`) and the witness header "Stacked 5x8x6 tilings" (96 pieces) confirm. The S page has no 5×8×N entries and no 3D completeness claim. **Not a gap.**

### S 5×8×18 — composite, 3 × 5×8×6

`classify` proves: Slab split along the 18-axis into 5×8×6 + 5×8×12 (= 6 × 4×5×6). Same evidence as 5×8×12; witness header "Stacked 5x8x6 tilings" (144 pieces). **Not a gap.**

### U 3×9×10 — composite, built from two published primes (closest call)

The U page claims "Complete." and 3×9×10 is tileable (23,936 witness solutions), so this was the strongest candidate. But `classify` proves it composite: Slab split along the 10-axis into two 3×9×5 halves, and each 3×9×5 = 3×5×9 = **2×3×5 + 3×5×7** (split along the 9-axis) — both published U primes (Sillke 1993). The page is a prime catalogue, so a composite box is correctly absent. The absence of any plane-split in the 23,936 solver solutions is not evidence of primality: the decomposition is a different construction. **Not a gap.**

### Y 2×5×10 — composite, thickness lift of published 2D data

`classify` proves: Width split along the 2-axis into two 1×5×10 slabs, each the thickness-1 box of the 2D 5×10 rectangle — published on the Y page's 2D section as `5x10 | prime minimal | 4 | Golomb 1966`. So 2×5×10 = 2 × 1×5×10 is a trivial thickness lift of published 2D data; the Y 3D section is a prime catalogue and correctly omits it. **Not a gap.**

### Final summary

**0 of the 6 remain genuine gaps.** All six are composite tileable boxes whose tileability follows from published primes (or published 2D data) on the same pages; the pages are prime catalogues, and the S page does not even claim 3D completeness. The §3 list should be read as "absent from the corpus pages", not as "missing published solutions". The closest calls were U 3×9×10 (complete prime catalogue + tileable + absent) and Y 2×5×10 (complete 3D catalogue), both resolved by decompositions into published primes. **No candidate remains a strong target for further historical investigation.**

## 5. Conclusion

The Shirakawa corpus audit is complete for the witness-bearing cases examined here. No genuine corpus omissions remain among the six apparent gaps: all six are composite tileable boxes derivable from published primes or published 2D data. The 5×6×28 case is likewise composite, with the immediate decomposition 7 × (4×5×6); its valid witness is a confirmation of that construction, not a new prime exception. The only remaining historical oddity in the audit is the range-level `5x6x[25-28] = 0` statement, which is simply wrong for N=28 because it overlooks this composite construction.