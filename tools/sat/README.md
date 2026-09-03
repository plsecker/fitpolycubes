# tools/sat — Reusable SAT/Certificate Workflow

Parameterized pipeline that turns the certified Z 6×6×10 / Z 4×11×15
results into a repeatable method for settling hard residual polycube boxes
with machine-checkable certificates.

## The certificate standard

Every closed UNSAT box MUST carry the full chain — "solver returned UNSAT"
alone is not a result:

```
placement generator          repo generate_placements, cross-checked
                             against an independent first-principles
                             regeneration (refuses to build on mismatch)
  -> canonical CNF           plain ALO + pairwise AMO exact cover,
                             sorted literals, DEDUPLICATED clause set,
                             sorted clause sequence, variable ids in
                             canonical placement order
  -> semantic audit          verify_encoding.py — standalone, re-derives
                             the geometry and the CNF from scratch
  -> native CaDiCaL UNSAT    binary DRAT proof streamed to disk
  -> drat-trim VERIFIED      independent checker, different codebase
  -> certificate package     CNF + proof (hash-pinned, gitignored) +
                             placement_set/var_map/metadata/hashes/
                             README/solve_command + audit script
  -> catalogue update        SEARCHED_NO_SOLUTION with provenance comment,
                             applied only after the chain is green
```

**No symmetry-breaking predicates.** The encoding is the plain certified
scheme. Symmetry clauses are a new proof obligation (the H 5×5×6
pair-scheme bug silently destroyed 21.8% of solution orbits); do not add
them for performance without dedicated correctness proofs AND a
dump-validation test.

## Components

| file | role |
|---|---|
| `sat_certificate_workflow.py` | driver: `prepare` / `solve` / `verify` / `audit` / `witness` / `status` |
| `verify_encoding.py` | standalone semantic audit (also copied into each package) |
| `tiling_validator.cpp` | standalone C++ exact-cover tiling validator (SAT witnesses) |

## Usage

```bash
# UNSAT path (full chain)
python3 tools/sat/sat_certificate_workflow.py prepare --piece Z --box 4 11 20 \
    --out docs/frontier/z_piece/z_41120_certificate
python3 tools/sat/sat_certificate_workflow.py solve --pkg <pkg> --time-cap 7200
python3 tools/sat/sat_certificate_workflow.py verify --pkg <pkg>      # drat-trim
python3 tools/sat/sat_certificate_workflow.py audit  --pkg <pkg>      # semantic audit

# SAT path (witness is validated by the standalone C++ validator)
python3 tools/sat/sat_certificate_workflow.py prepare --piece W --box 3 8 15 \
    --out /tmp/w3815 --expect SAT
python3 tools/sat/sat_certificate_workflow.py solve --pkg /tmp/w3815  # extracts witness
python3 tools/sat/sat_certificate_workflow.py witness --pkg /tmp/w3815
```

Solver/checker binaries: native CaDiCaL 1.5.3 (same build that produced the
certified 4×11×15 proof) at
`/tmp/opencode/pipdl/python_sat-1.9.dev15/solvers/cadical-rel-1.5.3/build/cadical`,
drat-trim at `/tmp/opencode/drat-trim-src/drat-trim`; both overridable via
`--cadical` / `--drattrim`.  (pysat 1.9.dev15's proof capture drops the
final conflict on proofs past ~2²⁴ lines — always use the native route for
proof-bearing runs.)

## Regression tests (must stay green)

```bash
# 1. the certified 4×11×15 package audits PASS under the canonical standard
python3 tools/sat/verify_encoding.py docs/frontier/z_piece/z_41115_certificate/
# 2. the certified 6×6×10 package audits PASS under the legacy standard
python3 tools/sat/verify_encoding.py docs/frontier/z_piece/z_6610_certificate/ \
    --piece-cells "0,0,0;1,0,0;1,1,0;1,2,0;2,2,0" --standard legacy
# 3. end-to-end UNSAT chain on a tiny box (seconds)
python3 tools/sat/sat_certificate_workflow.py prepare --piece Z --box 5 5 5 \
    --out /tmp/wf_z555 && \
python3 tools/sat/sat_certificate_workflow.py solve --pkg /tmp/wf_z555 && \
python3 tools/sat/sat_certificate_workflow.py verify --pkg /tmp/wf_z555 && \
python3 tools/sat/sat_certificate_workflow.py audit  --pkg /tmp/wf_z555
# 4. end-to-end SAT chain + C++ witness validation (seconds)
python3 tools/sat/sat_certificate_workflow.py prepare --piece W --box 3 8 15 \
    --out /tmp/wf_w3815 && \
python3 tools/sat/sat_certificate_workflow.py solve --pkg /tmp/wf_w3815
# 5. C++ validator rejects tampered tilings (overlap / out-of-box / wrong shape)
```

## Scaling notes (measured, Z pentacube, plain encoding)

| box | placements | clauses (deduped) | native CaDiCaL | drat-trim | proof |
|---|---|---|---|---|---|
| 6×6×10 | 2,176 | 195,976 (legacy, undeduped) | 287 s (pysat) | 455 s | 2.42 GB |
| 4×11×15 | 4,096 | 265,000 | 2,117 s | 2,458 s | 3.61 GB |

UNSAT proof size/time grow roughly with the placement count; budget
multi-GB proof storage and ~1 h checker time per mid-size box.
