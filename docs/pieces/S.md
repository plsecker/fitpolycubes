# Piece S Audit

## Summary

Reran the S catalogue audit against the project sources requested for this workflow. The catalogue was left unchanged. The Shirakawa transcription for piece S (`5-15`) is a high-level summary and includes a 3D 2-sided section; per the user clarification, 2-sided variants were ignored for this run.

## Files Modified

- `docs/pieces/S.md` (created/updated audit record only)

## Evidence Reviewed

- `catalogues/s_catalogue.py`
- `common/registry.py` lines 117-122: S maps to catalogue module `catalogues.s_catalogue`, Shirakawa URL `https://puzzlewillbeplayed.com/Shirakawa/5-15.html`, and Shirakawa piece 15.
- `shirakawa/5-15.md`
- Validation output from `.venv/bin/python tools/validate_catalogue.py S`
- Audit output from `.venv/bin/python tools/audit_catalogue.py S`

## Accepted Changes

None. No catalogue changes were applied.

## Rejected Changes

- **Applying or removing entries based on the 3D 2-sided section**: rejected as out of scope for this rerun. `shirakawa/5-15.md` lists a `3D 2-sided` section at lines 10-13 and notes it at line 25, but the user clarified that 2-sided variants are not in scope.
- **Removing S catalogue entries not explicitly enumerated in the transcription**: rejected because `shirakawa/5-15.md` is a summary transcription, not a detailed box-by-box list. It states that the 3D section is very long and systematically lists impossible families (line 6), gives only selected notes (lines 23-28), and therefore absence of an individual catalogue entry in the transcription is not evidence for removal.

## Possible Transcription Issues

- `shirakawa/5-15.md` appears to summarize rather than fully transcribe the 3D classification. It says the 3D section is very long and systematically lists many impossible configurations (line 6), but does not enumerate the catalogue's prime boxes or all finite impossibility details. This prevented a Certain evidence-backed catalogue change.

## Validation Results

Catalogue S validation PASSED:

- All 15 primes classify correctly.
- No primes are marked impossible.
- All 0 row generators classify as Prime.
- All family periods are valid.
- Raw prime entries: 15; unique prime boxes: 15.
- No orientation duplicates.
- All RAW_PRIMES entries are canonical.
- All 0 published solutions are consistent.
- No redundant published solutions.

## Audit Results

Audit complete for S:

- Prime mismatches: 0.
- Unproven composites: 1 (`10x14x14 -> Unknown`).
- Discovered composites: 73.
- Published solutions: 0.

The audit finding `10x14x14 -> Unknown` was not converted into a catalogue change because no explicit supporting Shirakawa or other allowed evidence was identified in the reviewed sources.

## Remaining Open Questions

- Human review would be needed to fully transcribe or verify the detailed non-2-sided 3D entries from the Shirakawa source if catalogue-level changes are desired.
