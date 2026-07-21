# Audit Report: Piece B (Pentomino 5/19)

## Investigations Performed
- Audited `catalogues/b_catalogue.py` against the cached Shirakawa markdown (`shirakawa/5-19.md`).
- Checked the `impossible_reason` function for empirical rules lacking proof or published authority.
- Found that `Box(3, 10, 11)` was explicitly listed as impossible because the rule for the published impossible family `3x11xN` (Postl, 1993) was poorly implemented (it only checked `b` and not `c`).
- Ran `validate_catalogue` and `audit_catalogue`.

## Evidence Gathered
- `shirakawa/5-19.md` lists `2x5x5` as the 3D minimal prime.
- `shirakawa/5-19.md` mentions that Sillke overlooked `3x16x25`, `3x17x25`, and `5x9x9`.
- `shirakawa/5-19.md` states that `5x7x8` is composite (`2x5x8 + 2x5x5 * 4`).
- `catalogues/b_catalogue.py` contained an explicit list of impossible boxes. Some of these were redundant or covered by published impossible families.

## Accepted Changes
- Fixed the `3x11xN` rule in `impossible_reason` to correctly check both `b` and `c` for the set `{3, 4, 5, 6, 7, 8, 11}`.
- Removed `Box(3, 10, 11)` from the explicit `published_impossible` list as it is now covered by the fixed `3x11xN` rule.
- Removed redundant canonical duplicates `Box(2, 12, 5)` and `Box(2, 12, 10)` from the explicit `published_impossible` list.
- Removed `Box(2, 12, 5)`, `Box(2, 12, 10)`, `Box(2, 12, 15)`, `Box(3, 9, 10)`, `Box(3, 9, 15)`, `Box(3, 10, 10)`, `Box(3, 10, 13)`, `Box(3, 10, 14)`, `Box(3, 10, 16)`, `Box(3, 10, 17)`, `Box(4, 5, 6)`, `Box(4, 5, 7)`, `Box(4, 5, 9)`, `Box(5, 5, 5)`, `Box(5, 5, 7)`, `Box(5, 5, 9)`, and `Box(5, 6, 6)` from `SEARCHED_NO_SOLUTION` because they are already explicitly classified as `published_impossible`.

## Rejected Changes
- Did not remove the explicit list of impossible boxes, as they are transcriptions of published impossible families that are not otherwise covered by general rules.

## Validation and Audit Results
- **Validation**: PASSED. All 66 primes classify correctly, no primes marked impossible, all row generators classify as Prime, family periods are valid, no canonical/orientation duplicates, and published solutions are consistent.
- **Audit**: PASSED. No prime mismatches, no unproven composites. 179 discovered composites (expected).

## Remaining Open Questions
- None.
