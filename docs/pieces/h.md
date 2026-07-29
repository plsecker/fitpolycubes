# Piece H (Kurnell 31, Shirakawa 5-23)

## Investigations Performed
- Audited `catalogues/h_catalogue.py` against `shirakawa/5-23.md`.
- Verified the decomposition of `2x7x15` into `2x5x13 + 2x2x5 * 4` as mentioned in the Shirakawa markdown.
- Investigated the `3x5xN` impossibility rule and its application to `3x4x5`.

## Evidence Gathered
- `shirakawa/5-23.md` explicitly mentions `2x2x5` as the 3D minimal prime.
- `shirakawa/5-23.md` mentions `2x7x15` is composite and decomposes into `2x5x13 + 2x2x5 * 4`. This implies `2x5x13` is prime.
- The Shirakawa markdown appears incomplete as it does not list all primes, but states "It covers 3D, 3D 2-sided, and 4D with prime box data, all credited to Sillke (1993)."
- The catalogue contains an empirical rule `3x5xN` (dies out after 40 steps) credited to Sillke.

## Accepted Changes
- Fixed the `impossible_reason` logic for `3x5xN` to correctly identify `3x4x5` (which canonicalizes to `a=3, b=4, c=5`) as impossible. This resolved an "Unproven composite" issue in the audit.

## Rejected Changes
- Did not remove the other primes listed in `RAW_PRIMES` despite them not being explicitly listed in the truncated `shirakawa/5-23.md` file, because the markdown file explicitly states it covers the prime box data but appears incomplete.
- Did not remove the `3x5xN` impossibility rule, as it is credited to Sillke and represents an exhaustive search proof ("dies out after 40 steps").
- Did not remove `3x7x15`, `5x5x5`, or `5x5x7` from `SEARCHED_NO_SOLUTION` as they are explicitly marked as impossible by Sillke.

## Validation and Audit Results
- Validation passed: All 17 primes classify correctly, no primes marked impossible, all row generators classify as prime, no duplicates.
- Audit passed: 0 prime mismatches, 0 unproven composites, 222 discovered composites.

## Remaining Open Questions
- The `shirakawa/5-23.md` file is truncated/incomplete and does not list all the primes. The primes in the catalogue are assumed to be sourced from Sillke's original results page (`qu5.31`).
