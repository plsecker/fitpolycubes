# Piece S Audit

## Summary

Re-audited the S catalogue against the live Shirakawa page
`https://puzzlewillbeplayed.com/Shirakawa/5-15.html` and the user's lossless
transcription `shirakawa/S.md` (both agree). Two-sided (2-sided) variants are
out of scope for this run and were ignored; all changes below follow the
one-sided 3D section of the page.

The previous catalogue contained 2-sided-only boxes as primes, was missing most
of the page's one-sided primes, and wrongly listed `8x8x10` (a page prime) as
searched-no-solution. These were corrected.

## Files Modified

- `catalogues/s_catalogue.py` — corrected to match the page's one-sided 3D data
- `docs/pieces/S.md` — this audit record

## Evidence Reviewed

- Live page: `https://puzzlewillbeplayed.com/Shirakawa/5-15.html` (fetched; "4D+ Complete."; 3D, 3D 2-sided, 4D sections)
- `shirakawa/S.md` — lossless transcription (matches the live page row for row)
- `common/registry.py` — S maps to `catalogues.s_catalogue`, Shirakawa page 5-15, piece 15
- Validation and audit tool output for catalogue S

## Accepted Changes

1. **Removed 2-sided-only primes** (page lists these only in "3D 2-sided"): `3x4x15`, `3x5x6`, `3x5x9`, `3x7x15`. This matches the user's edit which commented them out.
2. **Restored `4x5x6` as a prime** — the user's edit had commented it out as "2-sided", but the main 3D section lists `4x5x6` as "1 solution, prime, minimal — Hamlyn 1993" (it also appears in the 2-sided section, but it is a genuine one-sided prime).
3. **Added missing one-sided page primes** (all "1+ prime" in the main 3D section): `4x8x130`; `4x9x60`, `4x9x75`, `4x9x90`, `4x9x105`; `4x13x30`, `4x14x30`; `5x6x29`, `5x6x46`, `5x6x47`; `5x9x12`, `5x9x15`, `5x9x18`, `5x9x21`; `5x10x18`; `6x9x10`, `6x9x15`, `6x10x10`; `7x8x30`; `8x8x10`.
4. **Fixed `8x8x10`** — it was in `SEARCHED_NO_SOLUTION` but the page lists it as "1+ prime" (Shirakawa 2014); moved to primes.
5. **Encoded `3x[3-12]xN` = 0** (Sillke 1993) and `3x13xN` = 0 (Shirakawa 2014) as published impossible. This resolves the old "Interpretation unresolved" comment: the 3x4x15/3x5x6/3x5x9/3x7x15 "solutions" were 2-sided-only.
6. **Encoded `2xMxN` = 0** (Shirakawa 2014) in addition to `2x[2-20]xN` = 0 (Sillke 1993) — all width-2 boxes are impossible.
7. **Encoded the 5x6xN impossible families** from the page: `[6-7]`, `[9-11]`, `[13-15]` (Sillke 1993); `[17-19]`, `[21-23]`, `[25-28]`, `[30-31]`, `[34-35]`, `[38-39]`, `[42-43]` (Shirakawa 2014).
8. **Encoded `5x7x12` = 0 and `5x7x18` = 0** (Sillke 1993) as published impossible (previously only searched-no-solution).
9. **Added published solutions** (page "1+" entries, no prime marker): `3x26x180`, `4x15x45`, `8x9x15` (all Shirakawa 2014).
10. **Removed the duplicate `Box(5,7,24)`** entry.
11. Kept the correction-note impossibles `4x9x15`, `4x10x14`, `5x7x30` (the page notes Sillke's solutions for these were wrong).

## Rejected Changes

- **Encoding anything from the "3D 2-sided" section** (`3x4x15`, `3x5x6`, `3x5x9`, `3x7x15`, `4x4x10`, `5x5x6`): out of scope for this run.
- **Adding a `4x5x5` impossibility rule**: already covered by the odd-width theorem; the existing rule was retained unchanged.
- **Classifying page gaps** (e.g. `5x6x8`, `5x6x12`, `5x9x10`, `4x9x50`, ...): the page only lists 0-solutions and primes; gaps are left unknown (the page claims completeness only for 4D+, not 3D).

## Validation Results

Catalogue S validation PASSED:

- All 31 primes classify correctly.
- No primes are marked impossible.
- All 0 row generators classify as Prime; family periods valid.
- Raw prime entries: 31; unique prime boxes: 31; no orientation duplicates; all RAW_PRIMES canonical.
- All 3 published solutions are consistent; none redundant.

## Audit Results

Audit complete for S (max-dim 15):

- Prime mismatches: 0.
- Unproven composites: 10 (`3x14x15`, `3x15x15`, `4x15x15`, `5x11x12`, `5x15x15`, `7x9x15`, `7x15x15`, `9x9x10`, `9x9x15`, `10x14x14`) — none are on the page; left unknown.
- Discovered composites: 47 (sound guillotine decompositions into primes, e.g. `5x6x8` = two `4x5x6`, `4x5x12` = two `4x5x6`) — all fall in page gaps, none contradict the page.
- Published solutions: 3 (`3x26x180`, `4x15x45`, `8x9x15`).

## Remaining Open Questions

- The page claims "4D+ Complete." — the 3D section is not claimed complete, so unknown boxes in the gaps may have undisclosed solutions/primality.
- `5x7x30` appears as "1+ prime" (Sillke 1998) in the table but is contradicted by the page's own correction note; treated as impossible here (consistent with the page's intent).
- If 2-sided data is ever wanted, the removed 2-sided primes (`3x4x15`, `3x5x6`, `3x5x9`, `3x7x15`, `4x4x10`, `5x5x6`) are recorded in `shirakawa/S.md`.
