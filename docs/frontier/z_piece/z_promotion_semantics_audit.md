# Z Promotion Package — Source-Semantics Audit

**Date**: 2026-08-28
**Scope**: resolves the four human-review semantics questions of
`docs/frontier/z_piece/z_promotion_evidence_package.md` §6. Evidence-only;
no catalogue truth table, source entry, closure, or certificate was modified.
No solver behaviour is used as evidence.

**Primary source**: https://puzzlewillbeplayed.com/Shirakawa/Z.html
(raw HTML fetched 2026-08-28, `Feb 18, 2015 by k16@chiba.email.ne.jp`;
saved locally during the audit). Structural analysis of the 3D solution-list
table below is from that HTML.

## Source structure (measured, not inferred)

The 3D table is `<table class="sollist">` with row cells
`nump | size | sols | remark | date | who`. Programmatic counts:

| structure | count | notes |
|---|---|---|
| sols cells = linked numeric count | 137 | `<a href="html/Z-*.html">` — every numeric count links to a published solution drawing |
| sols cells = unlinked `0` / `s:0` | 18 | 10 family rows + 8 per-box zero rows; no link (nothing to show) |
| rows with `class="size prime"` (+ optional ` minimal`) and remark " prime" | 60 | bidirectional 1:1 with `RAW_PRIMES` (package §4: 0/0 mismatches) |
| rows with plain `class="size"`, empty remark, linked `1+` | 77 | the promotion set |
| composite rows carrying ANY remark text | 0 | no hidden qualifiers exist |
| sections on page | 3D, 4D, 5D | **no "3D 2-sided" section** (contrast S) |

Key HTML examples:

```html
<!-- promotion row (composite, 1+ linked) -->
<tr><td class="nump">2,070</td><td class="size">3x23x150</td>
    <td class="sols"><a href="html/Z-150x23x3.html">1+</a></td>
    <td class="remark"></td><td class="date">2014</td><td class="who">Shirakawa</td></tr>

<!-- prime row (structurally different: class + remark) -->
<tr><td class="nump">400</td><td class="size prime">4x10x50</td>
    <td class="sols"><a href="html/Z-50x10x4.html">2</a></td>
    <td class="remark"> prime</td><td class="date">2014</td><td class="who">Shirakawa</td></tr>

<!-- the "ambiguous" flattened run, unambiguous in HTML -->
<tr><td class="nump">120</td><td class="size prime minimal">6x10x10</td>
    <td class="sols"><a href="../Pentominoes/Z-10x10x6.html">11+</a></td>
    <td class="remark"> prime minimal</td><td class="date">1997</td><td class="who">Shindo</td></tr>

<!-- explicit impossibility rows (unlinked 0 / s:0) -->
<tr><td class="nump"></td><td class="size">4x11x25</td><td class="sols">0</td>...</tr>
<tr><td class="nump"></td><td class="size">5x10x[10-18]</td><td class="sols">0</td>...</tr>
<tr><td class="nump"></td><td class="size">5x8xN</td><td class="sols">s:0</td>...</tr>
<tr><td class="nump">690</td><td class="size">3x23x50</td><td class="sols">s:0</td>...</tr>
```

---

## Q1 — `1+` semantics:  **CONFIRMED**

**Claim**: `1+` means "at least one published solution / solvable" and is
suitable for `PUBLISHED_SOLUTIONS` without implying primality.

**Source evidence**:

1. Every numeric sols cell — including every `1+` — is a hyperlink to a
   published solution-drawing page (`html/Z-<dims>.html`), e.g.
   `3x23x150 -> html/Z-150x23x3.html`. `1+` is therefore a *solution count*
   ("one or more, drawing supplied"), structurally identical to the exact
   counts `2` (4x10x50), `10` (5x8x20) and `11+` (6x10x10); the `+` only
   replaces an exact upper enumeration. There are **0 unlinked numeric
   counts** on the page.
2. Primality is carried by entirely different fields: `class="size prime"`
   on the size cell and the remark cell " prime" / " prime minimal". All 77
   promotion rows have plain `class="size"` and an **empty** remark cell
   (verified: 0 composite rows carry any remark). The sols cell itself makes
   no primality statement.
3. Repo precedent (the convention cited by the package):
   `catalogues/s_catalogue.py` encodes exactly the S page's non-prime `1+`
   rows as `PUBLISHED_SOLUTIONS` with the governing comment — *"Page `1+`
   entries: solvable boxes that are NOT prime (no prime marker)"*
   (3x26x180, 4x15x45, 8x9x15, Shirakawa 2014).
4. Repo semantics: `tools/validate_catalogue.py` CHECK 5 validates
   `published_solutions` as solvable-box records (volume divisible by 5,
   not impossible, not in `searched_no_solution`); primality is not part of
   the check, and CHECK 6 treats decomposition-redundant entries as
   informational only. Nothing in the validator couples `PUBLISHED_SOLUTIONS`
   to primality.

## Q2 — the three 2015-dated rows:  **CONFIRMED**

**Claim**: `4x24x25`, `4x25x25`, `4x25x26` (all `1+`, 2015, Shirakawa) are
acceptable provenance; no special handling needed.

**Source evidence**:

1. Structurally identical to every other promotion row: linked `1+` sols,
   plain `class="size"`, empty remark, `date=2015`, `who=Shirakawa`
   (e.g. `<td class="sols"><a href="html/Z-25x24x4.html">1+</a></td>`). The
   page's marker vocabulary contains no "provisional"/"unverified" concept —
   the only markers in use are `prime`, `prime minimal`, `0`, `s:0`.
2. The date column is Shirakawa's per-row attribution year, same semantics
   as 1997 (Shindo rows) and 2013/2014. The page footer "Feb 18, 2015" is
   the page's last-update date; the three rows are simply the newest
   additions current at that update.
3. Repo precedent: a 2015-dated Shirakawa claim is already encoded in a
   truth table — `catalogues/f_catalogue.py`:
   `Box(5, 6, 10),  # Shirakawa 2015 prime`. 2015-dated Shirakawa data is
   also transcribed repo-wide (`shirakawa/5-30.md`, `5-31.md`, `5-32.md`,
   `5-47.md`, `5-51.md`, e.g. "All four entries are prime, credited
   entirely to Shirakawa (2015)").
4. No other 2015 row exists on the Z page, so nothing else changes.

*Qualification (cosmetic only)*: keep the `# 1+ 2015 Shirakawa` comment in
the promotion patch (already present) so the provenance survives in-code.

## Q3 — prime-marked rows excluded from `PUBLISHED_SOLUTIONS`:  **CONFIRMED WITH QUALIFICATION**

**Claim**: rows marked `prime` (including the flattened run `11+ prime
minimal`) must not enter `PUBLISHED_SOLUTIONS`; they belong to `RAW_PRIMES`.

**Source evidence**:

1. In HTML the ambiguity disappears: the run is
   `class="size prime minimal"` + linked sols `11+` + remark " prime
   minimal" (6x10x10, Shindo 1997). Primality is doubly explicit
   (size-cell class AND remark cell) on all 60 prime rows.
2. The 60 prime-marked rows correspond bidirectionally 1:1 with
   `RAW_PRIMES` (package §4 conflict matrix: 0 page-primes missing, 0
   catalogue primes unmarked). Encoding them as "published solutions" would
   misstate their role: they are primitive constructions, catalogued as
   `RAW_PRIMES`, and are already excluded from the promotion set.
3. `RAW_PRIMES` membership fully explains those rows' solvability under the
   catalogue (`classify` -> `Prime`, `closes()`), so no solvability
   information is lost by the exclusion.

**Qualification**: repo precedent is not uniform. The S precedent (cited by
the package) encodes *only* non-prime rows — exclusion, as proposed here.
The M precedent deliberately *mirrors* prime-marked rows into
`PUBLISHED_SOLUTIONS` as well, under the documented project rule
"`RAW_PRIMES` and `PUBLISHED_SOLUTIONS` are independent historical records"
(`docs/pieces/M.md`; M keeps `6x11x15` and `7x8x20` in both), and
`validate_catalogue.py` CHECK 6 passes with such redundancy. So exclusion is
a **valid, S-consistent, conservative policy choice** — not the only
repo-sanctioned style. It requires no change for this promotion; if the
M-style were ever preferred, that is a separate, repo-wide policy decision,
not a Z-specific necessity.

## Q4 — absence of a listed solution is not impossibility (except explicit `0`/`s:0`):  **CONFIRMED WITH QUALIFICATION**

**Claim**: the source convention does not treat an unlisted length as
impossible; impossibility is asserted only by explicit `0` rows (per-box /
block) and `s:0` family rows.

**Source evidence**:

1. Impossibility is *always* explicit: 18 unlinked zero cells — per-box `0`
   (4x11x25; 5x8x10, 15, 25, 30; 5x9x10, 20), block `0`
   (`4x10x[10-45]`, `5x10x[10-18]`), family `s:0`
   (`3x[3-22]xN`, `4x[4-9]xN`, `4x10xN`, `4x11xN`, `5x[5-7]xN`, `5x8xN`,
   `5x9xN`, `7x7xN`), and per-box `s:0` (3x23x50, with piece count 690).
   If mere absence meant zero, these rows would be redundant; their
   existence shows Shirakawa asserts zeros only where he proves them
   (individually, by range block, or by semigroup argument).
2. The Z page contains **no completeness statement** (the repo already
   records this: `docs/pieces/Z.md`, "No explicit 'Complete' statement is
   given"; contrast S's "4D+ Complete."). Shirakawa therefore does not claim
   his Z lists are exhaustive, and unlisted lengths — e.g. `5x10x19..32`,
   `5x11x41..59` — carry no sign either way. The current catalogue
   correctly leaves exactly those `Unknown`.
3. Repo precedent: `catalogues/s_catalogue.py` transcribes only *explicit*
   zero entries into `impossible_reason` (never absence), and
   `docs/frontier/t_piece/t_source_survey.md` glosses the notation as
   "s:0 notation = semigroup".

**Qualification**: the phrase "intentionally one-sided" is documented for S
(`shirakawa/S.md`: the 3D section is the one-sided classification, with a
separate "3D 2-sided" section that the repo excludes by convention). The Z
page has **no** 2-sided section (sections: 3D, 4D, 5D only), so (a) nothing
is being excluded under that convention, and (b) whether Shirakawa's Z 3D
list is one- or two-sided in his own taxonomy is *not stated on the page*
and is NOT ESTABLISHED — but it is immaterial here: each of the 77 rows
asserts a published solution *for the box*, which is what
`PUBLISHED_SOLUTIONS` records. Any future 2-sided Z section would be
governed by the existing S-style out-of-scope convention.

---

## Verdict summary

| point | verdict |
|---|---|
| Q1 `1+` = published-solvable, no primality | **CONFIRMED** |
| Q2 2015-dated rows acceptable, no special handling | **CONFIRMED** |
| Q3 prime-marked rows excluded from `PUBLISHED_SOLUTIONS` | **CONFIRMED WITH QUALIFICATION** (S-style exclusion valid; M-style mirroring exists as an alternative repo convention; no change needed) |
| Q4 absence ≠ impossibility except explicit `0`/`s:0` | **CONFIRMED WITH QUALIFICATION** (core claim confirmed; the one/two-sided taxonomy for Z's own table is unstated on the page and immaterial to the promotion) |

## Conclusion

All four questions are resolved with source evidence at the level required
for promotion; neither qualification blocks the patch (Q3's is a policy-style
note, Q4's concerns a taxonomy label the page does not assert and the
promotion does not need). **The existing promotion patch
(`PUBLISHED_SOLUTIONS` += the 77 rows of package §5) is semantically ready
for human approval.**

Reproduction of the structural counts:

```bash
curl -s https://puzzlewillbeplayed.com/Shirakawa/Z.html -o /tmp/z_page.html
# counts above are computed from the 3D sollist table of that file
```
