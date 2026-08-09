# Piece K Audit

## Summary
Audited the K catalogue against the Shirakawa transcription (5-13). The transcription appears to be severely incomplete regarding 3D data, so no modifications were made to the catalogue to avoid removing valid data without proper review.

## Files Modified
None (catalogue unchanged).

## Evidence Reviewed
- `common/registry.py` (K piece maps to Shirakawa piece 13)
- `shirakawa/5-13.md`
- `catalogues/k_catalogue.py`

## Accepted Changes
None.

## Rejected Changes
- **Removing all 3D prime boxes except 3x5x6**: The transcription mentions "The 3D minimal prime is 3x5x6", but `k_catalogue.py` contains many other prime boxes (like 2x8x10, 3x4x30, 4x4x10, etc.) and impossibility theorems. The transcription notes that the original page states "Complete." for the 3D classification and covers 3D prime box data, which strongly implies the transcription omitted the bulk of the 3D data. Thus, removing existing boxes from the catalogue based on their absence in the transcription is unsafe.

## Possible Transcription Issues
- `shirakawa/5-13.md` states "The page states "Complete." for the 3D classification. It covers 3D, 4D, and 5D with prime box data, primarily credited to Sillke (1993-1998) and Shirakawa (2015)" but only lists the minimal 3x5x6 prime for 3D. It appears the transcription is missing the rest of the 3D prime box data and the impossible families (which are present in `k_catalogue.py`).

## Validation Results
Catalogue K validation PASSED:
- All 18 primes classify correctly
- No primes marked impossible
- All RAW_PRIMES entries are canonical

## Audit Results
Audit complete for K:
- 0 Prime mismatches
- 0 Unproven composites
- 99 Discovered composites (e.g. 3x5x12 -> Slab, 4x8x10 -> Width, etc.)

## Remaining Open Questions
- Review the original Shirakawa page (https://puzzlewillbeplayed.com/Shirakawa/5-13.html) to properly transcribe the full 3D classification, including all prime boxes and impossibility theorems.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
