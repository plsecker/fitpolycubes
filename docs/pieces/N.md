# N Piece Catalogue Audit

## Summary

Audited `catalogues/n_catalogue.py` against the project registry and the corresponding Shirakawa transcription `shirakawa/N.md`. No catalogue changes were made.

The check was blocked from reaching a fully confident source comparison because `shirakawa/N.md` appears to be a summary rather than a full transcription of the N page's prime-box table: it says the page "lists prime boxes across 3D and 4D" but records only the 3D minimal prime, the `5x5x5` prime, and one 4D entry. The catalogue contains many additional 3D primes and published-impossible rules that cannot be confirmed or rejected from the current transcription alone.

## Files Modified

- `docs/pieces/n.md` — created this audit record.

## Evidence Reviewed

- `catalogues/n_catalogue.py`
  - `RAW_PRIMES` contains 20 canonicalized prime boxes.
  - `NCatalogue.impossible_reason` marks `a <= 1`, pairs `(2,2)`, `(2,3)`, `(3,3)`, box `3x4x5`, and `3x5x{5,6,7,9,10,11}` as `published_impossible`.
  - `ROW_FAMILIES`, `WIDTH_SPLITS`, `SEARCHED_NO_SOLUTION`, and `published_solutions` are empty.
- `common/registry.py`
  - Registry maps piece `N` to `catalogues.n_catalogue`, Shirakawa URL `https://puzzlewillbeplayed.com/Shirakawa/N.html`, and Shirakawa piece `8`.
- `shirakawa/N.md`
  - Lines 3-6 identify the N page and state that it lists prime boxes across 3D and 4D.
  - Lines 21-26 state: "3D Complete.", no 2D data, 3D minimal prime `2x4x5`, all 3D entries credited to Postl (1998), `5x5x5` has 4 solutions and is prime, and 4D has only `3x3x4x5`.
- Validation output from `.venv/bin/python tools/validate_catalogue.py N`.
- Audit output from `.venv/bin/python tools/audit_catalogue.py N`.

## Accepted Changes

No mathematical catalogue changes were accepted.

## Rejected Changes

- No catalogue entries were removed or altered solely because they are absent from `shirakawa/N.md`.
  - Evidence: `shirakawa/N.md` line 6 says the page lists prime boxes, but the transcription contains no detailed prime table; lines 23 and 25 mention only `2x4x5` and `5x5x5` among 3D entries.
  - Rationale: this absence is not reliable negative evidence because the transcription appears incomplete for the detailed 3D prime list.
- The validation warning about non-canonical `RAW_PRIMES` entries was not changed.
  - Evidence: validation reported 8 non-canonical raw entries, but also reported 20 unique canonical prime boxes and passed overall.
  - Rationale: canonicalizing raw entries would be an internal style/maintenance change, not a mathematical correctness change.

## Possible Transcription Issues

- `shirakawa/N.md` appears incomplete for the N prime-box table. It states that the page lists prime boxes across 3D and 4D, but does not transcribe the detailed 3D prime entries needed to verify the catalogue's 20 primes.
- The catalogue's published-impossible rules cannot be checked against the current Shirakawa transcription because no corresponding impossible-box table or theorem text is transcribed.

## Validation Results

Command: `.venv/bin/python tools/validate_catalogue.py N`

Result: passed.

Notable output:

- All 20 primes classify correctly.
- No primes are marked impossible.
- No canonical or orientation duplicates after canonicalization.
- Warning: 8 `RAW_PRIMES` entries are not canonical, but the catalogue still passed validation.

## Audit Results

Command: `.venv/bin/python tools/audit_catalogue.py N`

Result: completed.

Notable output:

- Prime mismatches: 0.
- Unproven composites: 0.
- Discovered composites: 239.
- Published solutions: 0.

## Remaining Open Questions

- Human review is needed to decide whether `shirakawa/N.md` should be expanded with the full published N prime-box table and any published impossibility information before a source-backed mathematical audit of the full catalogue can be completed.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
