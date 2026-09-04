# Z 6x7x10 Certificate Package

**Claim:** OPEN QUESTION: decide tileability of the 6x7x10 box by Z polycubes

**Encoding:** plain ALO + pairwise AMO exact cover, canonical deduplicated, NO symmetry-breaking predicates

| fact | value |
|---|---|
| placements / variables | 2656 |
| clauses (deduplicated) | 186664 |
| box cells / pieces | 420 / 84 |
| generator cross-check | PASS (repo vs independent regeneration) |
| CNF sha256 | 8de99f059ac5da50... |

## Evidence chain

- prepare (CNF build + cross-check): **DONE**
- semantic audit (verify_encoding.py): **PASS**
- native CaDiCaL solve: **TIMEOUT**
- drat-trim verification: **NOT RUN**
- C++ witness validation: **NOT RUN**

Solve record: TIMEOUT in 7200.1 s (20451635 conflicts). See metadata.json for all runs.

## Contents

- `z_6x7x10.cnf` — the canonical encoding
- `placement_set.json`, `var_map.json` — encoding provenance
- `metadata.json` — full run history + sha256 pins
- `verify_encoding.py` — standalone semantic audit (no repo imports)
- `hashes.txt` — integrity pins (write after runs conclude)

## Status

**UNKNOWN — solver time cap reached without a verdict.** The encoding is audited; the instance exceeds the budget. This package documents the attempt; it is NOT a decision.
