# Z Piece Catalogue Record

## Summary

Catalogue record for the Z-pentomino (5/11). The catalogue contains 55 prime boxes and extensive published impossibility families covering small widths. The Shirakawa source is very long and documents the 3D classification systematically.

## Catalogue Overview

The Z-pentomino catalogue (`catalogues/z_catalogue.py`) tracks tiling and packing data for the Z piece in 3D boxes.

## Authoritative Published Sources

- **Primary Source**: Shirakawa's Box Packing Collection (Z)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/Z.html`
- **Credits**: Shirakawa (2013-2015), Shindo (1997).
- **Status**: No explicit "Complete" statement is given.

## Catalogue Contents

### RAW_PRIMES (55 entries)

Organised by box family:

- **4x10**: 4x10x50, 4x10x55, 4x10x60, 4x10x65, 4x10x70, 4x10x75, 4x10x80, 4x10x85, 4x10x90, 4x10x95
- **4x11**: 4x11x50
- **4x14**: 4x14x25
- **4x16-22**: 4x16x25, 4x17x25, 4x18x25, 4x19x25, 4x20x20, 4x20x25, 4x21x25, 4x22x25
- **5x8**: 5x8x20, 5x8x35, 5x8x45, 5x8x50
- **5x9**: 5x9x15, 5x9x25, 5x9x35
- **5x10**: 5x10x33, 5x10x36, 5x10x37
- **5x12+**: 5x12x20, 5x12x25, 5x13x25, 5x14x20, 5x14x25, 5x15x17, 5x15x19, 5x16x25, 5x17x20
- **6x***: 6x6x25, 6x7x25, 6x8x25, 6x9x25, 6x10x10 (prime minimal), 6x10x15, 6x11x25, 6x15x15
- **7x***: 7x8x25, 7x9x25, 7x10x10, 7x10x15, 7x11x25
- **8x***: 8x8x25, 8x9x25, 8x10x10, 8x10x15, 8x15x15
- **9x***: 9x10x10
- **10x***: 10x10x10, 10x10x11

### SEARCHED_NO_SOLUTION

Empty.

### ROW_FAMILIES / WIDTH_SPLITS

Empty.

### Published Solutions

None.

## Impossibility Rules

Published impossible families:

- `a <= 2`: impossible
- `a == 3, 3 <= b <= 22` (`3x[3-22]xN`): impossible
- `a == 4, 4 <= b <= 9` (`4x[4-9]xN`): impossible
- `(a, b) == (4, 10), 10 <= c <= 45` (`4x10x[10-45]`): impossible
- `a == 5, b in {5, 6, 7}` (`5x{5,6,7}xN`): impossible
- `(a, b) == (5, 10), 10 <= c <= 18` (`5x10x[10-18]`): impossible — explicit
  zero block, Shirakawa 2013 (page row `5x10x[10-18]`, sols cell `0`,
  unlinked; no semigroup interpretation required).
- `a == 7, b == 7` (`7x7xN`): impossible

Published individual impossible boxes:

- `4x10x{10,15,20,25,30,35,40,45}`
- `4x11x25`
- `5x8x{10,15,25,30}`
- `5x9x{10,20}`
- `3x23x50` — per-box `s:0` (semigroup zero; 690 pieces, self-consistent
  with `3·23·50 = 5·690`), Shirakawa 2013. The only per-box zero row of the
  page not previously encoded.

### SEARCHED_NO_SOLUTION

- `6x6x10` — no tiling. Complete SAT decision (CaDiCaL, UNSAT in 287 s over
  the audited 2,176-placement encoding) with an **independently verified
  DRAT proof**: drat-trim `s VERIFIED` (455.2 s, upstream commit
  `2e3b2dc0`) and lrat-check `c VERIFIED` (25.2 s) on the emitted LRAT.
  Full certificate package and verification record:
  `docs/frontier/z_piece/z_6610_unsat_certificate.md`.

## Shirakawa Transcription Notes

`shirakawa/Z.md` confirms:
- No explicit "Complete" statement
- 3D section systematically documents impossibility for small widths
- First solutions at 3x23x150 (after 3x[3-22]xN all impossible)
- 3D minimal prime is 6x10x10 (11+ solutions, Shindo 1997)
- 5x10xN family documented with extraordinary granularity (individual lengths 33-71)
- 4D data extensive (Shirakawa 2013-2014), minimal prime 3x4x5x5
- 5D: single entry 3x3x3x5x5 (Shirakawa 2014)

## Remaining Open Questions

- A formal validation and audit run has not been performed on this catalogue.
- The 3D 2-sided and 4D/5D data in the Shirakawa transcription are not reflected in the catalogue (out of scope per project convention for 2-sided; 4D/5D not yet catalogued).
- The 5x10xN family is documented with extraordinary granularity in the Shirakawa source (individual lengths 33-71) but the catalogue only contains 3 entries (5x10x33, 5x10x36, 5x10x37). The discrepancy may indicate the catalogue is incomplete for this family, or the Shirakawa data may include non-prime entries.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
- **2026-08-27**: Frontier decomposition audit (`docs/frontier/z_piece/z_frontier_decomposition_audit.md`). Established the UNKNOWN frontier programmatically (331 boxes at dim<=20; 10580 at dim<=60); confirmed `WIDTH_SPLITS`/`ROW_FAMILIES` have always been empty for Z and verified the consumption mechanism separately; demonstrated 102 additional closures via runtime injection of the source page's published composite ("1+") entries — including frontier members `5x15x20` and `11x15x20`; catalogued a report-only proposal to transcribe those entries into `PUBLISHED_SOLUTIONS` plus an `s:0` convention decision resolving 103 further boxes as impossible. Truth tables unchanged by the audit itself; see report §5 for the proposed patch and tests in `tools/frontier/z_piece/test_z_frontier_closures.py`.
- **2026-08-28 (promotion)**: Applied the approved 77-row `PUBLISHED_SOLUTIONS` patch (Shirakawa `1+` non-prime rows; evidence: `docs/frontier/z_piece/z_catalogue_promotion_patch.md`, `z_promotion_evidence_package.md`, `z_promotion_semantics_audit.md`). Verified: validate PASSED, Audit B 331→329, C 69→70, D 0→77, Unknown dim<=60 10580→10478, 102 promotions, 0 regressions, 0 Impossible changes.
- **2026-08-29 (6x6x10 UNSAT promotion)**: `6x6x10` promoted to
  `SEARCHED_NO_SOLUTION` on the basis of a fully independently verified
  DRAT/LRAT UNSAT certificate (complete SAT decision over the audited
  2,176-placement encoding; drat-trim `s VERIFIED`; lrat-check `c VERIFIED`
  on the emitted LRAT; encoding pipeline additionally validated against the
  four published machine-readable 6x10x10 tilings). Certificate package:
  `docs/frontier/z_piece/z_6610_certificate/`; certification record:
  `docs/frontier/z_piece/z_6610_unsat_certification.md`. Measured effect:
  Audit B 320 -> 319; Unknown dim<=60 10468 -> 10467; exactly one
  classification change; all other truth tables unchanged.
- **2026-08-28 (explicit impossibilities)**: Transcribed the two explicit source zero rows into `impossible_reason`: the `5x10x[10-18]` explicit zero block (Shirakawa 2013, sols `0`) and the per-box `3x23x50` `s:0` row (Shirakawa 2013, 690 pieces). Evidence and pre-apply verification: `docs/frontier/z_piece/z_next_step_6x6x10.md` (Part A/C). Measured effect: exactly 10 `Unknown→Impossible`, zero other classification changes; Unknown dim<=60 10478→10468. No other `s:0`/family rows were encoded (103-box semigroup layer remains a separate policy question).
