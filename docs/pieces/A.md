# Engineering History: A Pentacube Catalogue

## Catalogue Overview
The A-pentomino (5/24) catalogue tracks the tiling and packing data for the A piece in 3D boxes. The catalogue is responsible for maintaining a strict, mathematically sound historical record of prime boxes, impossible families, and published solutions.

## Authoritative Published Sources
- **Primary Source**: Shirakawa's Box Packing Collection (5-24)
- **URL**: `https://puzzlewillbeplayed.com/Shirakawa/5-24.html`
- **Credits**: Toshihiro Shirakawa (2014), Postl (1998?).
- **Status**: No explicit "Complete" statement is given.

## Initial Catalogue State
Prior to the audit, the `A_CATALOGUE` contained:
- 31 prime boxes.
- 0 published solutions.
- Several published impossible families (`a <= 1`, `a <= 3`, `4x[4-8]xN`, `4x10xN`, `5xMxN`, `6x6xN`).

## Every Investigation Performed
1. **Source Comparison**: Compared `catalogues/a_catalogue.py` against `shirakawa/5-24.md`.
2. **Live Source Verification**: Scraped the live Shirakawa website for 5-24 to verify the exact lengths of the `6x10xN` family, as the markdown summary only stated "individual lengths from 17 to 26".
3. **Solver Artifact Check**: Attempted to run `reduce_solutions.py` on `solutions_hybrid_a_6x7x10.dat` to check for solver evidence, but aborted because the file was an empty binary placeholder (0 bytes).

## Every Proposed Change
1. Add the `6x10xN` family (lengths 17 through 26) to `PUBLISHED_SOLUTIONS`.

## Every Accepted Change and Why
- **Added `6x10x[17-26]` to `PUBLISHED_SOLUTIONS`**: Accepted because these 10 specific boxes were explicitly listed as tileable (but not prime) on the authoritative Shirakawa webpage.

## Every Rejected Change and Why
- No changes were explicitly rejected during this audit session for piece A.

## Solver Results That Influenced the Catalogue
No direct solver results were used to modify the catalogue during this audit.

## Validation Results
- **CHECK 1**: All 31 primes classify correctly.
- **CHECK 2**: No primes marked impossible.
- **CHECK 3**: All 0 row generators classify as Prime.
- **CHECK 4**: Unique prime boxes: 31. All `RAW_PRIMES` entries are canonical. No orientation duplicates.
- **CHECK 5**: All 10 published solutions are consistent.
- **CHECK 6**: 1 redundant published solution found (`6x10x20` -> Slab). Retained per the rule forbidding the removal of published information just because it is derivable elsewhere.
- **Overall**: PASSED.

## Audit Results
- **Prime mismatches**: 0
- **Unproven composites**: 72
- **Discovered composites**: 16
- **Published solutions**: 10

## Remaining Unknown Composites
There are currently 72 unproven composites up to 15x15x15 (e.g., `6x7x10`, `6x7x15`, `6x8x10`, etc.). These are expected outputs representing boxes that are not prime, not impossible, and not yet proven composite by the decomposition engine.

## Piece-Specific Decomposition Rules
- None currently active.

## Piece-Specific Impossibility Results
- `a <= 1`: Published impossible.
- `a <= 3` (i.e., `2xMxN`, `3xMxN`): Published impossible.
- `4x[4-8]xN`: Published impossible.
- `4x10xN`: Published impossible.
- `5xMxN`: Published impossible.
- `6x6xN`: Published impossible.

## Open Questions
- Can the 72 unproven composites be resolved via new decomposition rules or exhaustive search?

## Lessons Learned
- **Retain derivable published solutions**: The validation script correctly identified `6x10x20` as a redundant published solution (it can be proven via a Slab decomposition). However, it must be retained in the catalogue to preserve the historical record of the published source.

## Current Catalogue Status
The A catalogue is fully validated and strictly adheres to published sources, including the explicit recording of non-prime published solutions.
