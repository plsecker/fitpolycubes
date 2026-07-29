# Piece U Audit

## Summary

Reran the U catalogue audit against the project sources requested for this workflow. The catalogue was left unchanged. No 2-sided requirements were considered for this run.

## Files Modified

- `docs/pieces/U.md` (created/updated audit record only)

## Evidence Reviewed

- `catalogues/u_catalogue.py`
- `common/registry.py` lines 51-56: U maps to catalogue module `catalogues.u_catalogue`, Shirakawa URL `https://puzzlewillbeplayed.com/Shirakawa/U.html`, and Shirakawa piece 5.
- `shirakawa/U.md`
- Validation output from `.venv/bin/python tools/validate_catalogue.py U`
- Audit output from `.venv/bin/python tools/audit_catalogue.py U`

## Accepted Changes

None. No catalogue changes were applied.

## Rejected Changes

- **Removing U catalogue entries not explicitly enumerated in the transcription**: rejected because `shirakawa/U.md` confirms a complete 3D classification exists (line 6 and line 21) and states that prime boxes are listed across 3D and 4D (line 6), but the transcription notes only selected details such as the 3D minimal prime 2x3x5 (line 23). Absence of individual catalogue entries from this summary is not Certain evidence for removal.
- **Promoting discovered composites into catalogue data**: rejected because the audit output reports derived composite classifications, not published prime or impossible evidence requiring catalogue edits.

## Possible Transcription Issues

- `shirakawa/U.md` appears to summarize rather than fully enumerate the complete 3D classification. It states that the page lists prime boxes across 3D and 4D (line 6), but the transcription does not include the individual 3D prime list beyond the minimal-prime note. This prevented a complete evidence-by-entry verification of the catalogue.

## Validation Results

Catalogue U validation PASSED:

- All 10 primes classify correctly.
- No primes are marked impossible.
- All 0 row generators classify as Prime.
- All family periods are valid.
- Raw prime entries: 10; unique prime boxes: 10.
- No orientation duplicates.
- All RAW_PRIMES entries are canonical.
- All 0 published solutions are consistent.
- No redundant published solutions.

## Audit Results

Audit complete for U:

- Prime mismatches: 0.
- Unproven composites: 0.
- Discovered composites: 239.
- Published solutions: 0.

No audit failures were observed for U.

## Remaining Open Questions

- Human review would be needed to fully transcribe or verify the individual 3D entries from the Shirakawa U source if catalogue-level changes are desired.
