# Z 4x12x15 Certificate Package

**Claim:** OPEN QUESTION: decide tileability of the 4x12x15 box by Z polycubes

**Encoding:** plain ALO + pairwise AMO exact cover, canonical deduplicated, NO symmetry-breaking predicates

| fact | value |
|---|---|
| placements / variables | 4528 |
| clauses (deduplicated) | 295852 |
| box cells / pieces | 720 / 144 |
| generator cross-check | PASS (repo vs independent regeneration) |
| CNF sha256 | 9b9ea841e364142b... |

## Evidence chain

- prepare (CNF build + cross-check): **DONE**
- semantic audit (verify_encoding.py): **PASS**
- native CaDiCaL solve: **TIMEOUT**
- drat-trim verification: **NOT RUN**
- C++ witness validation: **NOT RUN**

Solve record: TIMEOUT in 10800.8 s (20392885 conflicts). See metadata.json for all runs.

## Contents

- `z_4x12x15.cnf` — the canonical encoding
- `placement_set.json`, `var_map.json` — encoding provenance
- `metadata.json` — full run history + sha256 pins
- `verify_encoding.py` — standalone semantic audit (no repo imports)
- `hashes.txt` — integrity pins (write after runs conclude)

## Status

**UNKNOWN — solver time cap reached without a verdict.** The encoding is audited; the instance exceeds the budget. This package documents the attempt; it is NOT a decision.
