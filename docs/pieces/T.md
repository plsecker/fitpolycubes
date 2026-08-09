# Piece T Audit

## Summary

Reran the T catalogue audit against the project sources requested for this workflow. The catalogue was left unchanged. No 2-sided requirements were considered for this run.

## Files Modified

- `docs/pieces/T.md` (created/updated audit record only)

## Evidence Reviewed

- `catalogues/t_catalogue.py`
- `common/registry.py` lines 45-50: T maps to catalogue module `catalogues.t_catalogue`, Shirakawa URL `https://puzzlewillbeplayed.com/Shirakawa/T.html`, and Shirakawa piece 7.
- `shirakawa/T.md`
- Validation output from `.venv/bin/python tools/validate_catalogue.py T`
- Audit output from `.venv/bin/python tools/audit_catalogue.py T`

## Accepted Changes

None. No catalogue changes were applied.

## Rejected Changes

- **Removing T catalogue entries not explicitly enumerated in the transcription**: rejected because `shirakawa/T.md` is a high-level summary. It states that the 3D section is extremely long and covers thousands of line items (lines 22-23), and that the 5x8xN family is documented with extraordinary granularity (line 26), but it does not transcribe those line items. Absence of individual entries from this summary is not Certain evidence for removal.
- **Adding audit-reported unproven composites as primes or impossibles**: rejected because the audit output only reports `Unknown` classifications; it does not provide published evidence for a prime or impossible status.

## Possible Transcription Issues

- `shirakawa/T.md` appears incomplete for catalogue auditing because it summarizes the page instead of enumerating the many 3D line items. It specifically says the 3D section covers thousands of line items (lines 22-23), while the transcription provides only selected notes such as minimal primes and family descriptions. This prevented Certain evidence-backed catalogue changes.

## Validation Results

Catalogue T validation PASSED:

- All 85 primes classify correctly.
- No primes are marked impossible.
- All 0 row generators classify as Prime.
- All family periods are valid.
- Raw prime entries: 85; unique prime boxes: 85.
- No orientation duplicates.
- All RAW_PRIMES entries are canonical.
- All 0 published solutions are consistent.
- No redundant published solutions.

## Audit Results

Audit complete for T:

- Prime mismatches: 0.
- Unproven composites: 82.
- Discovered composites: 26.
- Published solutions: 0.

The audit-reported unproven composites were not converted into catalogue changes because no explicit supporting Shirakawa or other allowed evidence was identified in the reviewed sources.

## Remaining Open Questions

- Human review would be needed to fully transcribe or verify the detailed 3D entries from the Shirakawa T source if catalogue-level changes are desired.

## Audit History

- **2026-08-10**: Added `MINIMAL_ODD` and `MINIMAL_EVEN` metadata identifying the smallest RAW_PRIME in each parity class, or `None` where no such RAW_PRIME exists. Metadata only; `RAW_PRIMES` and mathematical rules unchanged.
