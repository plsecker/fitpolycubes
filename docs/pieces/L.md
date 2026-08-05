# L Piece Impossibility Rules Audit

## Summary

Reviewed only the `L` catalogue impossibility rules against the project's Shirakawa transcription for the L piece. No catalogue changes were applied.

The current impossibility rules in `catalogues/l_catalogue.py` are:

- thickness-1 boxes with second dimension `1` (`1×1×N`): `published_impossible`
- thickness-1 boxes with second dimension `3` (`1×3×N`): `published_impossible`
- thickness-1 boxes with second dimension `5` and odd third dimension (`1×5×odd`): `published_impossible`
- sorted boxes with first two dimensions `3,3` (`3×3×N`): `published_impossible`

The Shirakawa transcription available in `shirakawa/L.md` does not contain explicit impossibility statements for these families. It only summarizes listed solution entries and notes that the page is short. Because removal or alteration would depend on absence of evidence in a summarized transcription, no impossibility rule was changed.

## Files Modified

- `L.md` created.

## Evidence Reviewed

- `catalogues/l_catalogue.py`
  - Lines 32-47 define the L-piece impossibility rules.
- `common/registry.py`
  - Lines 27-31 identify the L piece as `shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/L.html"` with `shirakawa_piece=2`.
- `shirakawa/L.md`
  - Lines 23-26 state:
    - “The page is relatively short compared to other pieces, with only a handful of box dimensions listed.”
    - “2D 1-sided minimal prime is 2x5. 2D minimal prime is 7x15 (80 solutions).”
    - “3D data includes 3x5x5 (820 solutions, prime) and 5x5x5 (432,382 solutions, composite).”
    - “4D data lists only two box configurations: 3x3x3x30 and 3x3x3x45, both credited to Sillke (1993).”

## Accepted Changes

None.

## Rejected Changes

- Do not remove or narrow any current L-piece impossibility rule.
  - Evidence: `shirakawa/L.md` does not explicitly confirm the impossibility families, but it is a short summary transcription rather than a full detailed table of all entries.
  - Rationale: Under the audit rules, absence of published evidence in a possibly incomplete or summarized transcription is not sufficient grounds to remove published catalogue information.

## Possible Transcription Issues

- `shirakawa/L.md` may be incomplete for auditing impossibility rules. It summarizes listed solutions and notes minimal primes, but it does not transcribe explicit impossible-family statements for `1×1×N`, `1×3×N`, `1×5×odd`, or `3×3×N` boxes. This prevents a Certain confirmation or correction of the current `published_impossible` rules.

## Validation Results

- `python tools/validate_catalogue.py L` was run.
- It did not complete because the environment is missing `numpy`:
  - `ModuleNotFoundError: No module named 'numpy'`
- No catalogue changes were made, so there were no mathematical edits to undo.

## Audit Results

- `python tools/audit_catalogue.py L` was run.
- It did not complete because the environment is missing `numpy`:
  - `ModuleNotFoundError: No module named 'numpy'`

## Remaining Open Questions

- Human review is needed to determine whether the current L-piece impossibility rules are supported by the original Shirakawa page or another accepted project source not present in `shirakawa/L.md`.
