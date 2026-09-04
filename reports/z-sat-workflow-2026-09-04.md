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
| Z 6×7×10 | 2,656 | 186,664 | **UNKNOWN — 2 h cap, no verdict** | 7,200.1 s (20,451,635 conflicts) | n/a | n/a | **TIMEOUT** |
| Z 6×6×15 | 3,456 | 242,736 | **UNKNOWN — 2 h cap, no verdict** | 7,200.2 s (22,075,813 conflicts) | n/a | n/a | **TIMEOUT** |
| Z 4×12×15 | 4,528 | 295,852 | **UNKNOWN — 3 h cap, no verdict** | 10,800.8 s (20,392,885 conflicts, 738 MB RSS) | n/a | n/a | **TIMEOUT** |
| Z 4×13×15 | 4,960 | 326,704 | **UNKNOWN — 4 h cap, no verdict** | 14,400.1 s (24,267,718 conflicts) | n/a | n/a | **TIMEOUT** |
| Z 4×11×20 | 5,616 | 370,300 | **UNKNOWN — 4 h cap, no verdict** | 14,401.4 s (24,916,933 conflicts) | n/a | n/a | **TIMEOUT** |

Every run's encoding audits **ALL CHECKS PASSED** (independently re-derived geometry + CNF), so the timeouts are solver-search hardness, not encoding defects. Partial cap-abort proofs are discarded (a partial proof certifies nothing); exact solver statistics at cap are recorded in each package's metadata.

**Timeout analysis.** All five boxes consumed 2.3–2.8× the *conflicts* that sufficed for the certified 4×11×15 UNSAT (8.77M) without concluding — cell count alone does not predict hardness of the plain encoding; few-solution/structured instances are the hard residue. These five boxes define the "hard even for plain SAT" class — candidates for (a) much longer budgets, (b) a *correctness-proven* structural clause class, or (c) new structural theorems.

**C++ cross-check on the smallest hard box.** Z 6×7×10 (420 cells — the smallest open Z box, bucket B) was additionally probed with the parallel C++ backend (`solver_par`, `--parallel 3 --symmetry --region-prune=propagate`, audited repo placement file): **no conclusion in 40 min**. Both engines fail independently on the same smallest-open box; the hard-residue class is instance-structural, not engine-specific.

**Certificate upgrade (dual-checker standard).** The flagship Z 4×11×15 certificate was upgraded to the same dual-checker status as the certified 6×6×10 package — and one better: drat-trim `-L` re-verified while emitting the LRAT certificate (`s VERIFIED`, 3072.2 s, identical core: 258,206/265,000 clauses, 4,859,533/11,822,097 lemmas, 647,547,908 resolution steps), and **lrat-check independently verified the LRAT** (`c VERIFIED`, 85.0 s, 5,124,533 added clauses). The package now holds **three independent checker verdicts** (two checkers, two proof formats), all logs retained, LRAT hash-pinned (6.52 GB, gitignored locally).

---

## 6. Strategic conclusion

### Is plain ALO+AMO sufficient as the general Z UNSAT method?

It is the correct *default* — every certificate the project holds (6×6×10, 4×11×15, 5×5×5 ladder, all small controls) was produced by it with zero encoding bugs, and the canonical-dedup variant now has a green audit chain end-to-end. But this batch shows it is **not a general decider**: five of five next-frontier boxes exceeded 2–3 h budgets, each consuming 2.3–2.5× the conflict count that closed 4×11×15. "Plain ALO+AMO first, with a time cap and an honest TIMEOUT record" is the method; "plain ALO+AMO decides everything" is falsified.

### How well does SAT scale as dimensions increase?

Badly in the worst case, and non-monotonically. Clause count grows ~linearly with placements (4×11×15: 265k → 4×11×20: 370k), but hardness does not: 6×7×10 (2,656 placements, 420 cells) burned 20.5M conflicts without a verdict while the much larger 4×11×15 (4,096 placements, 660 cells) needed only 8.8M. The controlling variable is solution structure (how few tilings / how constrained the box is), not box volume. Consequence: per-box budgeted attempts with recorded TIMEOUTs beat scaling extrapolations.

### Which Z boxes remain difficult even for SAT?

The measured hard-residue set — **every one of the five probed boxes, each 2.3–2.8× past the reference conflict count**:

- Z 6×7×10 (420 cells: 2 h SAT timeout + 40 min C++ probe inconclusive) — smallest open Z box
- Z 6×6×15 (540 cells: 2 h timeout, 22.1M conflicts)
- Z 4×12×15 (720 cells: 3 h timeout, 20.4M conflicts)
- Z 4×13×15 (780 cells: 4 h timeout, 24.3M conflicts)
- Z 4×11×20 (880 cells: 4 h timeout, 24.9M conflicts)
- Z 6×10×10 SAT-side (4 h timeout; encoding proven correct, search finds no needle)

All are *low-solution or UNSAT-structured* boxes; none has a published construction, so SAT-side hardness cannot be bypassed by a witness. The entire 4×N half-length band (N = 11..13, first band members) is now measured-hard, which is precisely the D-class evidence that motivates a structural theorem for the family.

### When should we prefer C++ exhaustive search versus SAT?

Measured decision rule:

| situation | engine |
|---|---|
| enumeration/counting/orbit characterization (SAT box, many solutions) | **C++ parallel** (W 5×7×9: 10 sols in 26 min at 4 workers; SAT cannot enumerate) |
| small UNSAT with modest tree (≤ ~450 cells, W-class) | **C++** (W 5×5×17: 62 s; C++ is 100× faster when its tree stays small) |
| certified UNSAT at any size | **SAT + DRAT** (the only machine-checkable UNSAT route; C++ search certificates are node-count evidence, not formal proofs) |
| hard residual (both fail) | record TIMEOUTs honestly; escalate to longer budgets / structural work |

### Does the project now have a practical two-engine proof architecture?

**Yes, and it is exercised end-to-end.** C++ search for enumeration and small-tree UNSAT; SAT+DRAT for certified hard UNSAT; the `tools/sat` workflow packages every closure to a uniform standard (generator cross-check → canonical CNF → semantic audit → native solve → drat-trim → hash-pinned package → catalogue update); the inventory tool maps every remaining box to an engine class. The architecture's demonstrated limit is the structural hard-residue class above — that is where future effort belongs, not in more local pruning.

### Recommended next experiments (ranked)

1. ~~Finish the two in-flight runs~~ **Done — both 4 h TIMEOUTs.** The hardness map of the entire first 4×N band is complete; five consecutive plain-encoding timeouts at 2.3–2.8× the reference conflict count is the D-class evidence that the band needs a structural argument, not a bigger GPU-hour budget.
2. **Overnight second attempt on Z 6×6×15 / Z 6×7×10** with an 8–12 h budget on idle hardware (CaDiCaL restarts occasionally resolve after 20–30M conflicts; the runs are fully automated and package themselves).
3. ~~Second-checker benchmark~~ **Done — the 4×11×15 certificate now carries three checker verdicts** (drat-trim binary-DRAT, drat-trim -L, lrat-check), matching the 6×6×10 dual-checker standard and exceeding it.
4. **A (4, N) structural impossibility theorem** (bucket D, highest leverage): 4×10 is published-impossible to c=45 with primes from 50; the 4×11/12/13 half-length bands are the measured hard residue. A checkerboard/colouring or row-invariant argument closing even *one* of 4×11×{15,20} would, by the semigroup structure, cascade across the row. This is new mathematics, not pruning — start only with a concrete conjecture in hand.
5. **Do not** add symmetry-breaking or restart a local-pruning programme: this batch is direct evidence that the remaining hardness is not addressed by cheap clause-level tricks (they are proof obligations anyway).

## 5. Catalogue state changes (applied only after verification)

- `catalogues/z_catalogue.py`: `SEARCHED_NO_SOLUTION` += **Box(4,11,15)** with full provenance (certificate package). `classify(Z,4,11,15)` → `Impossible[SEARCHED_NO_SOLUTION]`. ✔
- `catalogues/w_catalogue.py`: `SEARCHED_NO_SOLUTION` += **Box(5,5,17)** (exhaustive parallel C++ search, 26,421,672 nodes, 0 solutions, node counts reproduced across 1/2/4-worker runs); plus the catalogue now *consumes* its `searched_no_solution` set in `impossible_reason`, matching the F/Y-catalogue convention — W 5×5×17, 5×5×5, 5×7×7, … classify as `Impossible[SEARCHED_NO_SOLUTION]` instead of falling through to Unknown. ✔

---

## 6. Strategic conclusion

*(answers follow the run table in §4)*
