# Scope

The purpose of this role is to audit the mathematical content of a single catalogue.

Do not perform general software engineering or code cleanup as part of the audit.

Examples that are OUT OF SCOPE unless they affect mathematical correctness:

- refactoring Python code
- simplifying implementations
- reorganizing data structures
- canonicalizing internal data solely for style
- changing comments for readability

Only inspect:

- the requested catalogue
- `docs/pieces/<piece>.md` (if it exists)
- the corresponding Shirakawa markdown
- validation output
- audit output

Do **not** inspect unrelated catalogue files.

Do **not** inspect unrelated source code.

Do **not** browse the live web.

Use the corresponding `shirakawa/*.md` file as the project's transcription of the published source.

Do not reinterpret or reconstruct the original publication.

If the transcription appears incomplete, ambiguous, or appears to contradict existing catalogue evidence, report a possible transcription issue rather than modifying the catalogue.

---

# Source Discovery

Before beginning the audit:

1. Read `catalogues/<piece>_catalogue.py`.
2. Read `docs/pieces/<piece>.md` if it exists.
3. Read `common/registry.py`.
4. Determine the corresponding Shirakawa document from the registry.
5. Read the corresponding file in `shirakawa/`.
6. Treat these as the only sources required for the audit.
7. Do not search unrelated files to determine piece mappings.

---

# Standard Workflow

1. Read the requested catalogue.
2. Read `docs/pieces/<piece>.md` if present.
3. Read the corresponding Shirakawa markdown.
4. Compare the catalogue against the transcription.
5. Identify every proposed change before editing.
6. Apply only evidence-backed changes.
7. Run catalogue validation.
8. Run catalogue audit.
9. Update `docs/pieces/<piece>.md`.
10. Produce the final report.
11. Stop.

Do not continue investigating after the audit completes.

---

# Evidence Requirements

Every mathematical change must have explicit evidence.

Evidence may be:

- Shirakawa markdown
- existing project theorem
- existing decomposition proof
- existing documented search record

For every proposed mathematical change:

1. Locate the supporting evidence.
2. Quote or reference the exact entry.
3. Explain how it maps to the catalogue.
4. Check that no conflicting evidence exists.
5. Only then modify the catalogue.

If evidence cannot be identified, do not make the change.

Never infer what the published source "must mean."

---

# Transcription Integrity

The files under `shirakawa/` are project transcriptions of the published sources.

Assume they are authoritative for this audit, but not infallible.

If a proposed catalogue change depends on the absence of published evidence rather than the presence of published evidence:

1. Verify that the transcription appears complete.
2. If there is any indication that the transcription may be incomplete or internally inconsistent, do not modify the catalogue.
3. Record a "Possible transcription issue" in the report.
4. Leave the catalogue unchanged pending review.

Never remove published catalogue information solely because it is absent from a potentially incomplete transcription.

---

# Confidence Levels

Certain
: directly supported by authoritative evidence

Likely
: strong evidence but requires human review

Possible
: plausible but insufficient evidence

Speculation
: unsupported

Only Certain changes may be applied automatically.

---

# Validation

After editing, run:

- catalogue validation
- catalogue audit

If validation fails:

Undo the changes.

---

# Reporting

Update `docs/pieces/<piece>.md`.

This document is the permanent engineering history for the piece.

It should contain:

## Summary

## Files Modified

## Evidence Reviewed

## Accepted Changes

For every accepted change include:

- evidence
- rationale

## Rejected Changes

Record proposed changes that were not applied and explain why.

## Possible Transcription Issues

Record any suspected omissions, ambiguities, or inconsistencies in the `shirakawa/*.md` transcription that prevented a confident catalogue change.

These are documentation issues, not catalogue issues.

## Validation Results

Summarize validation.

## Audit Results

Summarize audit.

## Remaining Open Questions

Record anything requiring human review.

Do not speculate.

Do not continue after reporting.

---

# Final Output

At the end of the run, output the contents of the updated
`docs/pieces/<piece>.md`.
