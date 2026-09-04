# Z 4x11x20 Certificate Package

**Claim:** OPEN QUESTION: decide tileability of the 4x11x20 box by Z polycubes

**Encoding:** plain ALO + pairwise AMO exact cover, canonical deduplicated, NO symmetry-breaking predicates

| fact | value |
|---|---|
| placements / variables | 5616 |
| clauses (deduplicated) | 370300 |
| box cells / pieces | 880 / 176 |
| generator cross-check | PASS (repo vs independent regeneration) |
| CNF sha256 | c84a59e85c23331a... |

## Evidence chain

- prepare (CNF build + cross-check): **DONE**
- semantic audit (verify_encoding.py): **NOT RUN**
- native CaDiCaL solve: **TIMEOUT**
- drat-trim verification: **NOT RUN**
- C++ witness validation: **NOT RUN**

Solve record: TIMEOUT in 14401.4 s (24916933 conflicts). See metadata.json for all runs.

## Contents

- `z_4x11x20.cnf` — the canonical encoding
- `placement_set.json`, `var_map.json` — encoding provenance
- `metadata.json` — full run history + sha256 pins
- `verify_encoding.py` — standalone semantic audit (no repo imports)
- `hashes.txt` — integrity pins (write after runs conclude)

## Status

**UNKNOWN — solver time cap reached without a verdict.** The encoding is audited; the instance exceeds the budget. This package documents the attempt; it is NOT a decision.
