# M Pentacube (5-18)

## Investigations Performed
- Audited `catalogues/m_catalogue.py` against the authoritative published source: [Shirakawa's 5-18 Box Packing Collection](https://puzzlewillbeplayed.com/Shirakawa/5-18.html).
- Cross-referenced `PUBLISHED_SOLUTIONS` and `RAW_PRIMES` with the published data to ensure fidelity and completeness.
- Investigated the presence of `Box(6, 8, 25)` in the catalogue, which appeared anomalous.

## Evidence Gathered
- The Shirakawa 5-18 page does not list `6x8x25` as a solution. Furthermore, it explicitly lists `6x8x10` and `6x8x15` as having 0 solutions (impossible).
- `Box(6, 11, 15)` and `Box(7, 8, 20)` are explicitly listed as published solutions in the source but were commented out in the catalogue's `PUBLISHED_SOLUTIONS` because they were already present in `RAW_PRIMES`.
- `Box(10, 10, 12)` is attributed to George Sicherman and is not part of the Shirakawa dataset.

## Accepted Changes
- **Removed `Box(6, 8, 25)`** from `PUBLISHED_SOLUTIONS` as it was a transcription error and not present in the authoritative source.
- **Restored `Box(6, 11, 15)` and `Box(7, 8, 20)`** to `PUBLISHED_SOLUTIONS`. As per project rules, `RAW_PRIMES` and `PUBLISHED_SOLUTIONS` are independent historical records, and one should not be omitted just because the other exists.

## Rejected Changes
- No changes were rejected. `Box(10, 10, 12)` was retained as it represents independent historical evidence from George Sicherman.

## Validation and Audit Results
- **Validation**: PASSED. All 2 primes classify correctly. No primes marked impossible. All 57 published solutions are consistent. `Box(6, 11, 15)` and `Box(7, 8, 20)` are correctly identified as redundant published solutions since they are proven by the decomposition engine (being primes).
- **Audit**: PASSED. 0 prime mismatches. 79 unproven composites. 0 discovered composites. 57 published solutions.

## Remaining Open Questions
- 79 unproven composites remain in the catalogue.
- The exact original publication link/citation for George Sicherman's `Box(10, 10, 12)` solution could be formally documented if found, though the attribution is currently preserved.
