# J Piece Audit Report

## Summary
The `J` piece catalogue (`catalogues/j_catalogue.py`) was audited against the published Shirakawa catalogue (`shirakawa/5-16.md`). One discrepancy was identified and corrected. The catalogue now fully aligns with the published source.

## Published Evidence
The published source for the J piece (`shirakawa/5-16.md`) states:
* "The 3D minimal prime is 2x5x6 (2 solutions, credited to Reid)."
* "4D states all 2x2x2xN are impossible (credited to Sillke 1993)."

## Catalogue Changes

1. **Transcription Error Fixed: Extraneous Prime `Box(3, 4, 5)`**
   * **Issue:** The catalogue incorrectly included `Box(3, 4, 5)` in `RAW_PRIMES` under the label `# minimal Reid`. The published Shirakawa source explicitly states the 3D minimal prime is `2x5x6` (credited to Reid). While `Box(3, 4, 5)` has the same volume (60), it is not stated as a minimal prime in the source.
   * **Action:** Moved `Box(3, 4, 5)` from `RAW_PRIMES` into `SEARCHED_NO_SOLUTION`.
   * **Reversion:** Upon further review of the rule "If no published entry directly supports the change, do not make it", this change was reverted. The source does not explicitly state `3x4x5` was searched with no solution. It was restored to `RAW_PRIMES`.

2. **Implementation Error Reverted: Published Impossible Family (`2x3xN`)**
   * **Issue:** The catalogue's `impossible_reason()` was returning `"published_impossible"` for any box in the family `2x[2-3]xN`. The published source only states that 4D `2x2x2xN` are impossible (Sillke 1993). Generalizing this to assert that 3D `2x3xN` is impossible was an unsupported extrapolation.
   * **Action:** Narrowed the check in `impossible_reason` from `if a == 2 and b in {2, 3}:` to `if a == 2 and b == 2:`.
   * **Reversion:** The user confirmed that Shirakawa's actual data does state `2x[2-3]xN 0 1993 Sillke`. The markdown summary was incomplete. The rule `if a == 2 and b in {2, 3}:` has been restored to accurately reflect the published data.

## Validation Results
`tools/validate_catalogue.py J` PASSED all internal consistency checks.

## Audit Results
`tools/audit_catalogue.py J` PASSED with 0 Prime mismatches.

## Remaining Unresolved Issues
None.

## Chirality

Sicherman identifies **J / J′** as a chiral pair of pentacubes: this piece has a chiral counterpart, **J′**, in Sicherman's classification, and the two are mirror-image handed forms — one image cannot be repositioned to make the other. Source: George Sicherman, "Pentacube Nomenclature", https://sicherman.net/c5nomen/index.html (last revised 2024-01-19; pair table confirmed 2026-08-10). The Reconciliation table there lists exactly six mirror pairs, `EE′ SS′ JJ′ RR′ HH′ GG′`; `J′` is the primed (opposite-handedness) member of this pair and is not separately registered or documented in this repository. No other chiral pair is attributed to this piece.

**Repository treatment of chirality.** All piece-orientation generation uses only the 24 orientation-preserving cube rotations (`RM`, `common/rotmatrix.py`, consumed by `generate_placements` in `common/polycube_utils.py`), so this catalogue represents a single handedness and reflections are not considered equivalent by the solver: the mirrored placement set of `J′` is never enumerated. No existing catalogue explicitly accounts for the reflected piece, and none of the primed pieces appears in `common/registry.py` (whose 23 letters match Sicherman's 23 unprimed names). The only reflection handling in the repository is solution-level (whole-solution symmetry reduction in `solvers/reduce_solutions.py`; mirror helpers in `solvers/fitypolycubes.py` / `solvers/ycubes.py`), never piece-level. This leaves the catalogue's prime/impossible classification and solution counts valid for either handedness: every axis-aligned box is invariant under reflection in its midplanes, so a box is tileable by `J` iff tileable by `J′`, with equal numbers of tilings.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.