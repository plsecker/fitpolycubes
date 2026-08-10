# Engineering History: E Pentacube Catalogue

## Catalogue Overview
The E-pentomino (5/14) catalogue tracks the tiling and packing data for the E piece in 3D boxes. The catalogue is responsible for maintaining a strict, mathematically sound historical record of prime boxes, impossible families, and published solutions.

## Authoritative Published Sources
- **Primary Source**: Shirakawa's Box Packing Collection (5-14)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/5-14.html`
- **Credits**: Torsten Sillke (1993).
- **Status**: No explicit "Complete" statement is given.

## Initial Catalogue State
Prior to the audit, the `E_CATALOGUE` contained:
- 16 prime boxes (e.g., 2x2x5, 2x7x15, 3x4x10, 3x5x6, etc.).
- 15 published solutions.
- Several published impossible families (`a <= 1`, `2x3x5n`, `3x3x5n`, `2x5xodd`, and explicit boxes `3x4x5`, `3x5x5`, `3x5x7`).

## Every Investigation Performed
1. **Source Comparison**: Compared `catalogues/e_catalogue.py` against `shirakawa/5-14.md`.
2. **Discrepancy Identification**: Noted that `shirakawa/5-14.md` only lists `2x2x5` as the 3D minimal prime and two 4D entries. It does not contain the vast majority of primes, published solutions, or impossible families present in `e_catalogue.py`.
3. **Cross-Referencing**: Checked other Shirakawa markdown files (e.g., 5-23) to see if the data in `e_catalogue.py` might belong to another piece. Piece 5-23 mentions `2x7x15` as a composite, whereas `e_catalogue.py` lists it as a prime.

## Every Proposed Change
- None. The catalogue was left unchanged due to the significant discrepancy between the catalogue contents and the cached published source (`shirakawa/5-14.md`).

## Every Accepted Change and Why
- No changes were accepted.

## Every Rejected Change and Why
- No changes were made. The instructions dictate that if the published source appears incomplete or ambiguous, the discrepancy should be reported rather than assuming the catalogue is incorrect.

## Solver Results That Influenced the Catalogue
No direct solver results were used to modify the catalogue during this audit.

## Validation Results
- **CHECK 1**: All 16 primes classify correctly.
- **CHECK 2**: No primes marked impossible.
- **CHECK 3**: All 0 row generators classify as Prime.
- **CHECK 4**: Unique prime boxes: 16. All `RAW_PRIMES` entries are canonical. No orientation duplicates.
- **CHECK 5**: All 15 published solutions are consistent.
- **CHECK 6**: 15 redundant published solutions found (all 15 are Prime).
- **Overall**: PASSED.

## Audit Results
- **Prime mismatches**: 0
- **Unproven composites**: 0
- **Discovered composites**: 237
- **Published solutions**: 15

## Remaining Unknown Composites
There are currently 0 unproven composites up to 15x15x15.

## Piece-Specific Decomposition Rules
- None currently active.

## Piece-Specific Impossibility Results
- `a <= 1`: Published impossible.
- `2x3x5n`: Published impossible.
- `3x3x5n`: Published impossible.
- `2x5xodd`: Published impossible.
- `3x4x5`, `3x5x5`, `3x5x7`: Explicit published impossible boxes.

## Open Questions
- **Source Discrepancy**: The cached Shirakawa markdown for 5-14 (`shirakawa/5-14.md`) is extremely sparse compared to the rich data in `e_catalogue.py`. Where did the additional primes and impossible families in `e_catalogue.py` come from? Is the cached markdown incomplete, or does the catalogue contain data from another piece?

## Lessons Learned
- When a catalogue contains significantly more data than the cached published source, it is safer to report the discrepancy and leave the catalogue unchanged rather than deleting unverified data that might have come from a valid but uncached source.

## Current Catalogue Status
The E catalogue passes all validation and audit checks, but its contents cannot be fully verified against the cached `shirakawa/5-14.md` file due to a significant discrepancy in the amount of data.

## Chirality

Sicherman identifies **E / E′** as a chiral pair of pentacubes: this piece has a chiral counterpart, **E′**, in Sicherman's classification, and the two are mirror-image handed forms — one image cannot be repositioned to make the other. Source: George Sicherman, "Pentacube Nomenclature", https://sicherman.net/c5nomen/index.html (last revised 2024-01-19; pair table confirmed 2026-08-10). The Reconciliation table there lists exactly six mirror pairs, `EE′ SS′ JJ′ RR′ HH′ GG′`; `E′` is the primed (opposite-handedness) member of this pair and is not separately registered or documented in this repository. No other chiral pair is attributed to this piece.

**Repository treatment of chirality.** All piece-orientation generation uses only the 24 orientation-preserving cube rotations (`RM`, `common/rotmatrix.py`, consumed by `generate_placements` in `common/polycube_utils.py`), so this catalogue represents a single handedness and reflections are not considered equivalent by the solver: the mirrored placement set of `E′` is never enumerated. No existing catalogue explicitly accounts for the reflected piece, and none of the primed pieces appears in `common/registry.py` (whose 23 letters match Sicherman's 23 unprimed names). The only reflection handling in the repository is solution-level (whole-solution symmetry reduction in `solvers/reduce_solutions.py`; mirror helpers in `solvers/fitypolycubes.py` / `solvers/ycubes.py`), never piece-level. This leaves the catalogue's prime/impossible classification and solution counts valid for either handedness: every axis-aligned box is invariant under reflection in its midplanes, so a box is tileable by `E` iff tileable by `E′`, with equal numbers of tilings.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
