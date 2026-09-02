# Z 6×7×10 — UNSAT Certification Audit

**Date**: 2026-08-31
**Purpose**: determine whether 6×7×10 has sufficiently strong independent
evidence to support a `SEARCHED_NO_SOLUTION` catalogue entry.

---

## Verdict

**NEEDS ADDITIONAL EVIDENCE**

No complete search of 6×7×10 has been performed. Every solver attempt was
terminated before reaching a verdict. The Z 6×7×10 box remains genuinely
UNKNOWN. It is **not** ready for `SEARCHED_NO_SOLUTION` promotion.

---

## 1. Evidence inventory (what exists)

### 1.1 Frontier-DP attempt

| parameter | value |
|---|---|
| implementation | `tools/frontier/z_piece/z_frontier_numba.py` (commit `b714c93`) |
| box | 6×7×10 (42-cell cross-section, 10 layers, 84 pieces) |
| placements | 2,656 (verified against `generate_placements`) |
| hash table | 2²⁵ = 33,554,432 entries |
| mod-5 pruning | enabled (validated) |
| symmetry reduction | disabled |
| wall cap | 900 s |
| boundaries processed | **3 of 10** |
| boundary 1 states | 27,067,552 |
| boundary 2 states | 1,419,442 |
| boundary 3 states | 14,467,846 |
| boundaries 4–10 | **not reached** |
| termination | **timeout** (900 s) |
| verdict | **INCONCLUSIVE** — not exhaustive |

The frontier was still growing when the cap was hit (boundary 3: 14.5M
states, with no sign of contraction). Boundaries 4–10 were never reached.
The search is **provably incomplete**: 7 of 10 layers were never processed.

### 1.2 SAT/CDCL attempt (original encoding)

| parameter | value |
|---|---|
| implementation | `Cadical153` via pysat 1.9.dev15 |
| variables | 2,656 (one per placement) |
| clauses | 248,644 (420 coverage ≥1 + 248,224 pairwise AMO) |
| proof logging | enabled (`with_proof=True`) |
| wall cap | 3,600 s |
| termination | **timeout** (3,600 s) |
| verdict | **none** — solver did not complete |

No DRAT proof was produced (the solve was killed before completion).

### 1.3 SAT/CDCL attempt (strengthened encoding)

| parameter | value |
|---|---|
| additional constraints | f_z ≤ 6 per layer (sequential counter, 10 layers) |
| total variables | 7,096 (2,656 placement + 4,440 aux) |
| total clauses | 258,204 |
| wall cap | 1,200 s |
| termination | **timeout** (1,200 s) |
| verdict | **none** |

The structural constraints (f_z ≤ 6) did not materially improve CDCL
performance within the tested budget.

### 1.4 CP-SAT attempt

| parameter | value |
|---|---|
| solver | OR-Tools CP-SAT |
| wall cap | 300 s |
| termination | **timeout** |
| verdict | **UNKNOWN** |

### 1.5 What does NOT exist

* No exhaustive frontier-DP closure of 6×7×10
* No complete SAT decision for 6×7×10
* No DRAT/LRAT proof for 6×7×10
* No published source evidence for 6×7×10 (absent from the Shirakawa page)
* No mathematical proof of impossibility for 6×7×10

## 2. What IS established about 6×7×10 (partial results)

| result | classification | source |
|---|---|---|
| 2,656 legal placements (all verified) | PROVED COMPUTATION | audit |
| placement set ≡ `generate_placements` | PROVED COMPUTATION | set equality |
| max flat pieces per layer = 6 | PROVED COMPUTATION | exhaustive tiling enumeration |
| per-layer vertical cells ≥ 12 | THEOREM (from max flat = 6) | mathematical corollary |
| v_z ≡ 2 (mod 5) for all z | THEOREM (from A = 5f + v) | mathematical corollary |
| mod-5 3D colouring is balanced (84/residue) | PROVED COMPUTATION | root-of-unity calculation |
| (x+y) mod 5 residues are (9,9,8,8,8) | PROVED COMPUTATION | direct enumeration |
| frontier width at boundary 1 = 27M | EMPIRICAL OBSERVATION | DP run |
| frontier width at boundary 3 = 14.5M | EMPIRICAL OBSERVATION | DP run |
| 6×7 packing density = 71% | PROVED COMPUTATION | flat-tiling enumeration |
| 6×7 is harder than 6×6 | EMPIRICAL OBSERVATION | all solver attempts |
| CaDiCaL > 3,600 s without verdict | EMPIRICAL OBSERVATION | solver run |

None of these results constitutes a completeness or impossibility proof
for 6×7×10.

## 3. The 6×6×10 vs 6×7×10 comparison (why 6×7×10 is harder)

| metric | 6×6×10 | 6×7×10 | ratio |
|---|---|---|---|
| cross-section cells | 36 | 42 | 1.17× |
| pieces | 72 | 84 | 1.17× |
| placements | 2,176 | 2,656 | 1.22× |
| clauses | 195,976 | 248,644 | 1.27× |
| boundary-1 frontier states | 1,154,524 | **27,067,552** | **23.4×** |
| packing density | 83% | 71% | — |
| forced vertical cells/layer | ≥ 6 | ≥ 12 | 2× |
| SAT solve time | 287 s | > 3,600 s | > 12.5× |
| frontier-DP closure time | 242 s | > 900 s (incomplete) | — |

The 23.4× explosion in boundary-1 states is the root cause. The 7-column
cross-section provides dramatically more placement combinations per layer,
making both SAT and frontier-DP searches exponentially harder.

The 6×6×10 UNSAT certificate (SAT/DRAT + frontier DP) is **not transferable**
to 6×7×10 — the geometry, placement set, and encoding are different.

## 4. Are the frontier DP and SAT/DRAT evidence independent? (task 7)

**For 6×7×10: neither approach produced a complete result, so independence
is moot.**

For 6×6×10 (where both completed):

| aspect | SAT/DRAT | frontier DP | independent? |
|---|---|---|---|
| formulation | exact-cover SAT | transfer-matrix DP | ✅ different |
| search | CDCL clause learning | BFS over boundary states | ✅ different |
| placement generation | `generate_placements` | `z_layer_dp.gen` | ✅ different code, same set |
| data structures | CDCL watches + clause DB | hash set of (L0,L1) pairs | ✅ different |
| mathematical basis | Boolean satisfiability | dynamic programming over layered states | ✅ different |

The two methods are **genuinely independent**: different formulations,
different algorithms, different code paths. They share only the Z piece
definition (from `PENTACUBES["Z"]`). Their agreement on 6×6×10 UNSAT is
strong mutual confirmation.

For 6×7×10, only partial results exist from each method. No independence
claim can be made because neither method completed.

## 5. Completeness argument (task 6)

### 5.1 Frontier-DP completeness (for 6×6×10 — demonstrated)

**Theorem**: the planar-frontier DP, with exhaustive forward closure over
all reachable boundary states, decides SAT/UNSAT for any box.

*Proof*: by induction on z, the set of reachable boundary states at layer
z captures exactly the set of possible "interfaces" between layers 0..z−1
and layers z..NZ−1. A tiling exists iff a chain of transitions from
boundary 0 to boundary NZ exists. Exhaustive forward closure explores all
such chains. If the frontier becomes empty before boundary NZ, no tiling
exists (UNSAT). If boundary NZ is reached with the empty state, a tiling
exists (SAT). ∎

This was **demonstrated** for 6×6×10: the DP completed all 10 boundaries
with a non-empty frontier at boundary 9 (52 states) and empty at boundary
10 (UNSAT), matching the SAT/DRAT result.

### 5.2 Frontier-DP completeness for 6×7×10 (NOT demonstrated)

The frontier DP on 6×7×10 was terminated after 3 of 10 boundaries. The
remaining 7 boundaries were never explored. The search is **provably
incomplete** — it cannot establish either SAT or UNSAT.

**Critical unsound claim to avoid**: "the DP found no solution, therefore
6×7×10 is UNSAT." This is **false** — the DP did not exhaust the search
space. Boundaries 4–10 were never reached, and the frontier was still
growing at the point of termination.

### 5.3 SAT completeness (for 6×7×10 — NOT demonstrated)

CaDiCaL is a complete decision procedure: if allowed to run to completion,
it returns SAT or UNSAT. The solve was killed at 3,600 s without
completing. No verdict was obtained.

The strengthened encoding (f_z ≤ 6 per layer) was also killed before
completion.

**No SAT verdict exists for 6×7×10.**

## 6. Placement-generation audit (task 5)

| check | result |
|---|---|
| `gen(6,7,10)` placements ≡ `generate_placements` | ✅ 2,656 = 2,656 (frozenset equality) |
| every placement is a legal Z orientation | ✅ 0 bad shapes in 2,656 |
| every placement is inside the box | ✅ 0 out-of-bounds |
| every cell has ≥ 1 covering placement | ✅ 420/420 |
| no duplicate placements | ✅ (set-based dedup) |
| orientation count = 12 | ✅ |

The placement generation is **verified correct** for both the SAT encoding
and the frontier DP. The same generator was used for the certified 6×6×10
result.

## 7. Catalogue conventions (task 8)

The S-catalogue precedent for `SEARCHED_NO_SOLUTION`:

```python
# catalogues/s_catalogue.py
SEARCHED_NO_SOLUTION = {
    # Empirically searched without finding a solution; no explicit page entry.
    Box(4, 5, 7),
    # Empirically searched ...; related to the impossible 4x10x14 ...
    Box(8, 10, 14),
}
```

The S-precedent standard: **empirical search with no solution found**.
The searches need not be provably exhaustive (the S comments say
"empirically searched"), but they must be genuine searches that completed
without finding a solution.

**For 6×7×10**: no search completed. The frontier DP was killed at 3/10
boundaries. The SAT solve was killed at 3,600 s. **No genuine search of
6×7×10 has completed.** The S-precedent standard is not met.

## 8. What additional evidence is needed

To reach `SEARCHED_NO_SOLUTION` for 6×7×10, at minimum ONE of:

1. **A completed frontier-DP closure** — process all 10 boundaries,
   showing the frontier empties (UNSAT) or contains an accepting state
   (SAT). Estimated: several hours to days (the frontier is growing).
2. **A completed SAT decision** — CaDiCaL (or another complete solver)
   returning SAT or UNSAT. Estimated: hours on current hardware.
3. **A mathematical proof** — showing that 6×7×10 cannot be tiled
   (or must be tileable) from the geometry alone.
4. **A published source** — Shirakawa or another authority listing
   6×7×10 as solved or impossible.

None of these have been obtained.

## 9. Exact proposed catalogue edit (NOT APPLIED)

If a complete search were performed and found no tiling, the change would
be:

```python
# catalogues/z_catalogue.py
SEARCHED_NO_SOLUTION = {
    # ... existing entries ...
    # 6x7x10: no tiling found in bounded frontier-DP probe (3/10 boundaries)
    # and SAT/CDCL solve (>3600s, no verdict). Status: SEARCHED, NOT PROVEN.
    # See docs/frontier/z_piece/z_6x7x10_unsat_certification.md
    Box(6, 7, 10),
}
```

**This edit is NOT ready to apply.** The searches were incomplete. The
proposal is included here only for completeness of the certification
document.

---

## 10. Summary of evidence status

| box | frontier DP | SAT/DRAT | structural constraints | status |
|---|---|---|---|---|
| 6×6×10 | ✅ complete UNSAT (242 s) | ✅ complete UNSAT (287 s, DRAT verified) | f_z ≤ 5 proved | **CERTIFIED UNSAT** |
| 6×7×10 | ❌ INCONCLUSIVE (3/10 boundaries) | ❌ INCONCLUSIVE (> 3,600 s) | f_z ≤ 6 proved | **UNKNOWN** |
| 5×5×5 | ✅ complete UNSAT (0.3 s) | ✅ complete UNSAT (0.0 s) | rule 5x{5,6,7} | **CERTIFIED UNSAT** |
| 6×6×5 | ✅ complete UNSAT (343 s) | ✅ complete UNSAT (0.3 s) | rule 5x{5,6,7} | **CERTIFIED UNSAT** |

## 11. Conclusion

**NEEDS ADDITIONAL EVIDENCE.**

6×7×10 remains genuinely UNKNOWN. No complete search, no mathematical
proof, and no published source evidence exists for or against tilability.
The partial results (frontier growth, SAT non-completion) are consistent
with either outcome. The box should remain in the UNKNOWN frontier until
a complete search or a mathematical argument resolves it.
