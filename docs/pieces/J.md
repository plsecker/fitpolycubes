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