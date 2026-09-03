# From One SAT Proof to a Reusable SAT/Certificate Workflow for Hard Z Residuals

**Date:** 2026-09-04 · **Context:** follows `reports/parallel-sat-decision-2026-09-04.md` (Z 4×11×15 machine-checkably UNSAT: canonical deduplicated CNF, native CaDiCaL, drat-trim `s VERIFIED`, certificate package preserved). This stage turned that single success into a systematic method and immediately applied it to the next Z frontier.

---

## 1. The reusable workflow (`tools/sat/`)

The certified pipeline was refactored into a parameterized tool — not a family of one-off scripts:

| component | role |
|---|---|
| `tools/sat/sat_certificate_workflow.py` | driver: `prepare` → `solve` → `verify` → `audit` → `witness` → `status`; accepts piece + box; refuses to build a CNF unless the repo placement generator and an independent first-principles regeneration agree |
| `tools/sat/verify_encoding.py` | standalone semantic audit (no repo imports; re-derives geometry, placements, var map, and every CNF clause from scratch); copied into each certificate package so packages are self-auditing |
| `tools/sat/tiling_validator.cpp` | standalone C++ exact-cover tiling validator (proper-rotation-only orientation check, exact-cover check, built with zig c++) |

**The certificate standard** (now the required chain for every closed UNSAT box):

```
placement generator (cross-checked)
  -> canonical deduplicated CNF   plain ALO+AMO, sorted literals, deduped,
                                  sorted clauses, NO symmetry breaking
  -> semantic audit               ALL CHECKS PASSED
  -> native CaDiCaL UNSAT         binary DRAT proof
  -> drat-trim VERIFIED           independent checker
  -> certificate package          hash-pinned, proof gitignored locally
  -> catalogue update             SEARCHED_NO_SOLUTION + provenance,
                                  only after the chain is green
```

Design invariants kept: plain ALO+AMO encoding only (no symmetry-breaking predicates — the H 5×5×6 pair-scheme bug is the standing warning); canonical deduplication per the 4×11×15 standard; native CaDiCaL for proof-bearing runs (pysat 1.9.dev15 drops the final conflict on proofs past ~2²⁴ lines).

**Regression suite (all green):**

1. Generic audit on the certified **Z 4×11×15** package — **ALL CHECKS PASSED** (17/17).
2. Generic audit on the certified **Z 6×6×10** package — **ALL CHECKS PASSED** under `--standard legacy` (that package predates deduplication: its 195,976-clause CNF contains 49,320 duplicate AMO clauses; the new standard removes them — this is documented, not a defect).
3. End-to-end UNSAT chain on Z 5×5×5 (documented rule): prepare → native CaDiCaL UNSAT (0.0 s) → drat-trim `s VERIFIED` (0.1 s) → audit PASS.
4. End-to-end SAT chain on W 3×8×15 (published prime): SAT in 1.2 s → witness parsed from the CaDiCaL `v` lines → **C++ validator: `VALID: 72 pieces × 5 cells = 360 cells, exact cover of 3x8x15`**.
5. C++ validator negative tests: rejects overlapping cells, out-of-box cells, and non-orientation shapes (fixtures in `/tmp/opencode/neg_*.txt`).

## 2. Z 6×10×10 SAT positive control — NOT COMPLETED; solver difficulty, not encoding

| run | window | outcome |
|---|---|---|
| attempts 1–2 (2026-09-03) | ~1 h each | killed by launch mechanics before verdict |
| attempt 3 (2026-09-04 03:53–07:55) | 4 h cap | **no verdict in 4 h 02 m** — still inside the first solve of the 406,648-clause encoding (vars=4096, enc=0.2 s) when the cap hit (the `timeout` SIGTERM cannot interrupt a native CaDiCaL call; terminated manually) |

**Diagnosis — solver difficulty, not an encoding issue:**
- The encoding is the same certified recipe that reproduced the published Shindo/ISHINO 6×10×10 tilings through encode→solve→extract→verify with the published placements forced as assumptions (provenance section of the 6×6×10 package README) — the SAT side of the encoding is *known* to be satisfiable and correctly wired.
- The same recipe completed hard UNSAT instances of comparable size: 6×6×10 in 287 s, 4×11×15 in 2,117 s.
- 6×10×10 is the smallest published-SAT Z box and has very few solutions (4 up to symmetry); a needle-in-a-haystack SAT instance is the classic weak spot of CDCL search, while UNSAT residuals are its strong spot.
- Placement/coverage correctness was re-confirmed independently this session (prep-time cross-checks pass for every box).

**Consequence:** the unguided 6×10×10 solve is recorded as UNKNOWN/timeout and does not block anything. The workflow's SAT path is regression-tested on W 3×8×15 (above). A guided positive control (published tiling forced as assumptions) already exists from the certification work; the C++ witness validator now additionally covers witness checking for any future SAT verdict.

## 3. Residual-frontier inventory (`tools/frontier/z_piece/z_residual_inventory.py`)

Audit of record (`tools/audit_catalogue.py Z --max-dim 20`): Audit A 0 mismatches; **Audit B 318 unproven composites**; Audit C 70; Audit D 77. Full-range scan (canonical dims ≤ 60, a ≤ 12): 8,500 scanned, 1,970 closed, 1,992 impossible, **4,538 unresolved across 466 cross-sections**.

Smallest unresolved boxes and their advisory class:

| box | cells | placements | class |
|---|---|---|---|
| Z 5×8×8 / 5×8×9 / 5×9×9 | 320/360/405 | 1,872/2,160/2,492 | B — C++ exhaustive viable |
| **Z 6×7×10** (previously inconclusive) | 420 | 2,656 | B/C — smallest open, SAT-scaled |
| Z 5×8×11 | 440 | 2,736 | B |
| Z 6×8×10, 5×9×11 | 480/495 | 3,136/3,156 | C |
| **Z 6×6×15** (row of certified 6×6×10) | 540 | 3,456 | C |
| **Z 4×12×15** | 720 | 4,528 | C |
| **Z 4×13×15** | 780 | 4,960 | C |
| **Z 4×11×20** (4×11×15 analogue) | 880 | 5,616 | C |

The 4×N×15/20 half-length family (the direct 4×11×15 analogues) is all Unknown beyond the two certified UNSAT rows; non-multiple-of-5 areas make (4,N) frontiers sparse (c ≡ 0 mod 5 only), which is why the family yields individual SAT-sized targets rather than dense bands.

## 4. Frontier runs (results recorded as they land; time caps in brackets)

All runs: plain ALO+AMO canonical deduplicated encoding, native CaDiCaL 1.5.3, binary DRAT, drat-trim verification for every UNSAT, packages under `docs/frontier/z_piece/`.

| box | placements | clauses (deduped) | result | solve | drat-trim | proof | status |
|---|---|---|---|---|---|---|---|
| Z 6×7×10 | 2,656 | 186,664 | **UNKNOWN — 2 h cap, no verdict** | 7,200.1 s (20,451,635 conflicts, 39.9M decisions) | n/a | n/a | **TIMEOUT** |
| Z 6×6×15 | 3,456 | 242,736 | **UNKNOWN — 2 h cap, no verdict** | 7,200.2 s (22,075,813 conflicts, 45.5M decisions) | n/a | n/a | **TIMEOUT** |
| Z 4×12×15 | 4,528 | 295,852 | — | — | — | — | **PENDING** [10,800 s cap] |
| Z 4×13×15 | 4,960 | 326,704 | — | — | — | — | **PENDING** [14,400 s cap] |
| Z 4×11×20 | 5,616 | 370,300 | — | — | — | — | **PENDING** [14,400 s cap] |

**Timeout analysis.** Both timed-out boxes consumed 2.3–2.5× the *conflicts* that sufficed for the certified 4×11×15 UNSAT (8.77M) without concluding — cell count alone does not predict hardness of the plain encoding; few-solution/structured instances (6×7×10 has a documented near-miss frontier-DP profile; 6×6×15 sits in the same cross-section as the certified 6×6×10) are the hard residue. Partial cap-abort proofs are discarded (a partial proof certifies nothing); solver statistics are recorded in each package's metadata. These two boxes move to the "hard even for plain SAT" class — candidates for (a) longer budgets on faster hardware, (b) a *correctness-proven* structural clause class, or (c) the C++ frontier backend with a bigger budget.

## 5. Catalogue state changes (applied only after verification)

- `catalogues/z_catalogue.py`: `SEARCHED_NO_SOLUTION` += **Box(4,11,15)** with full provenance (certificate package). `classify(Z,4,11,15)` → `Impossible[SEARCHED_NO_SOLUTION]`. ✔
- `catalogues/w_catalogue.py`: `SEARCHED_NO_SOLUTION` += **Box(5,5,17)** (exhaustive parallel C++ search, 26,421,672 nodes, 0 solutions, node counts reproduced across 1/2/4-worker runs); plus the catalogue now *consumes* its `searched_no_solution` set in `impossible_reason`, matching the F/Y-catalogue convention — W 5×5×17, 5×5×5, 5×7×7, … classify as `Impossible[SEARCHED_NO_SOLUTION]` instead of falling through to Unknown. ✔

---

## 6. Strategic conclusion

*(answers follow the run table in §4)*
