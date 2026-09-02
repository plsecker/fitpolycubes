# S-Pentacube Macro Research: Consolidated Status

**Date**: 2026-08-25  
**Status**: COMPLETE — Proof framework established; certificates for 3 global theorems independently verifiable

---

## 1. What Has Been Established

### 1.1 Verified Macro Cycles

| Cross-section | Area | Recovered cycles | Source | Cycle data file |
|---------------|------|-----------------|--------|-----------------|
| 4×5 | 20 | {6} | Hamlyn 1993 (catalogue prime) | — |
| 5×6 | 30 | {4, 29, 46, 47} | Numba solver + catalogue primes | `_5x6_concrete_cycles.json` |
| 4×8 | 32 | {20, 130} | Postl 1998, Shirakawa 2014 | — |
| 5×8 | 40 | {6} | Numba solver (new discovery) | `_5x8_concrete_cycles.json` |
| 4×9 | 36 | {60, 75, 90, 105} | Shirakawa SVG extraction | `_4x9_concrete_cycles.json` |
| 4×10 | 40 | {6, 10} | Numba solver + Postl 1998 | `_4x10_concrete_cycles.json` |
| 5×7 | 35 | {24, 36, 42} | Sillke SVG extraction | `_5x7_concrete_cycles.json` |
| 5×9 | 45 | {12, 15, 18, 21} | Shirakawa SVG extraction | `_5x9_concrete_cycles.json` |
| 5×10 | 50 | {18} | Shirakawa SVG extraction | `_5x10_concrete_cycles.json` |

### 1.2 Numerical Semigroups

| Cross-section | Semigroup | GCD | Frobenius | Conductor |
|---------------|-----------|-----|-----------|-----------|
| 4×5 | ⟨6⟩ | 6 | — | 6 |
| 5×6 | ⟨4, 29, 46, 47⟩ | 1 | 43 | 44 |
| 4×8 | ⟨20, 130⟩ | 10 | 110 | 120 |
| 5×8 | ⟨6⟩ | 6 | — | 6 |
| 4×9 | ⟨60, 75, 90, 105⟩ | 15 | 45 | 60 |
| 4×10 | ⟨6, 10⟩ | 2 | 14 | 16 |
| 5×7 | ⟨24, 36, 42⟩ | 6 | 54 | 60 |
| 5×9 | ⟨12, 15, 18, 21⟩ | 3 | 9 | 12 |
| 5×10 | ⟨18⟩ | 18 | — | 18 |

**All catalogue primes are explained by the recovered semigroups.**

### 1.3 Graph Periods

| Cross-section | SCC size | Graph period | Determined from |
|---------------|----------|-------------|-----------------|
| 4×5 | 11 | **6** | Complete SCC |
| 5×6 | 1,606 | **1** | Complete SCC |
| 4×8 | 478 | **10** | Bounded SCC |
| Others | ? | (inferred from cycles) | Not computed from graph |

### 1.4 Invariants

| Invariant | Status | Scope |
|-----------|--------|-------|
| L1-even (|L1| always even) | **THEOREM** | All post-shift states, all cross-sections |
| Piece-count integrality | **THEOREM** | All cross-sections; gives mod-5/gcd(area,5) restriction |
| Gate structure | **THEOREM** | (AREA,0,0) is unique predecessor of state 0 |
| Mod-3 conservation | **THEOREM** | Conserved iff area ≡ 0 mod 3 |
| 4×8 global period = 10 | **PROVEN THEOREM** | Full graph (see 4x8_global_period10.md) |
| F1=F2 balance | **STRONG OBSERVATION** | 10/12 cycles exact; ±5 in remaining 2 |
| Orientation palette similarity | **EXPLAINED** | Sample size effect + family structure |

---

## 2. New Discoveries

| Discovery | Cross-section | By |
|-----------|---------------|-----|
| 5×6×4 tileable (new box) | 5×6 | Numba solver |
| 5×8×6 tileable (new cross-section) | 5×8 | Numba solver |
| 4×10×6 tileable (shorter than catalogue prime) | 4×10 | Numba solver |
| 5×6×28 tileable (catalogue said impossible) | 5×6 | Macro construction |

## 3. Catalogue Corrections

| Correction | Details |
|------------|---------|
| 5×6×28 is tileable | Shirakawa listed [25-28] as impossible, but 28 = 7×4 is tileable |
| 4×9 "acyclic" was search-depth artifact | Four cycles now extracted from SVG |
| 5×7×30 is impossible | Correction note (Sillke's solution was wrong) |

## 4. What Remains Open

| Question | Status |
|----------|--------|
| 4×8 global period-10? | **PROVEN** (see 4x8_global_period10.md) | First-gen sources complete → SCC(0) is all recurrent behaviour |
| Generator completeness for bounded SCCs? | **UNKNOWN** for 4×9, 4×10, 5×7, 5×8, 5×9, 5×10 |
| F1=F2 theorem? | **NOT PROVED** (strong observation only) |
| 4×9/5×9 scaling relationship? | **REFUTED** (numerical coincidence) |
| Orientation palette invariant? | **REFUTED** (sample size effect) |

## 5. Available SVG Solutions: EXHAUSTED

All S-pentacube catalogue cross-sections with SVG solutions have been extracted. No further SVG witnesses remain.

Remaining uninvestigated catalogue cross-sections:
- 6×6 (area 36): primes {15, 20, 25} — no SVG known
- 6×7 (area 42): primes {10, 15} — no SVG known
- 4×13 (area 52): prime {30} — no SVG known
- 4×14 (area 56): prime {30} — no SVG known
- 6×9 (area 54): primes {10, 15} — no SVG known
- 6×10 (area 60): prime {10} — no SVG known
- 7×8 (area 56): prime {30} — no SVG known
- 8×8 (area 64): prime {10} — no SVG known

Investigating these would require new solver searches or alternative source data.

## 6. Period-Geometry Analysis

| Question | Answer |
|----------|--------|
| Can period be predicted from (a,b) alone? | **NO** — proven negative result |
| Is there a simple formula for period? | **NO** |
| Can the piece-count factor be predicted? | **YES** — when area ∤ 5, period divisible by 5/gcd(area,5) |
| Can the remaining factor be predicted? | **NO** — depends on SCC structure |
| Are same-area → same period? | **NO** — 4×10 vs 5×8 counterexample |

See `docs/frontier/s_piece/macro_period_geometry_analysis.md` for full analysis.

The Macro proof methodology has been formalised as a reusable framework:

| Component | File |
|-----------|------|
| **Methodology document** | `docs/frontier/macro_proof_methodology.md` |
| **Certificate verifier** | `tools/frontier/verify_macro_proof.py` |
| **4×5 proof certificate** | `data/frontier/s_piece/certificates/4x5_proof.json` |
| **5×6 proof certificate** | `data/frontier/s_piece/certificates/5x6_proof.json` |
| **4×8 proof certificate** | `data/frontier/s_piece/certificates/4x8_proof.json` |
| **4×9 cycle certificate** | `data/frontier/s_piece/certificates/4x9_cycles.json` |

### Completeness levels supported

| Level | Meaning |
|-------|---------|
| `global` | Full theorem: necessary AND sufficient conditions proven |
| `scc-local` | Period and cycles verified for SCC; globality unproven |
| `cycle-only` | Recovered cycles verified; no SCC analysis |

All three global theorem certificates pass independent verification.

### Data files
- `data/solutions_s_5x7x*_shirakawa.dat` through `_5x10*` — SVG-extracted solutions
- `data/frontier/s_piece/consolidated_results.json` — Consolidated cross-section data
- `data/frontier/s_piece/macro_scc_period_analysis.json` — Graph period data
- `data/frontier/s_piece/4x8_period10_invariant.json` — 4×8 period-10 certificate

### Tool files
- `tools/frontier/_5x*_concrete_cycles.json` — Verified cycle data
- `tools/frontier/_4x*_concrete_cycles.json` — Verified cycle data
- `tools/frontier/macro_construction.py` — Tiling constructor
- `tools/frontier/macro_scc_period.py` — Period analysis tool

### Documentation
- `docs/frontier/s_piece/5x7_investigation.md`
- `docs/frontier/s_piece/5x10_investigation.md`
- `docs/frontier/s_piece/complete_scc_structural_analysis.md`
- `docs/frontier/s_piece/macro_scc_period_analysis.md`
- `docs/frontier/s_piece/4x8_period10_invariant.md`
- `docs/frontier/s_piece/4x8_global_parity_theorem.md`
- `docs/frontier/s_piece/cross_section_scaling_analysis.md`
- `docs/frontier/s_piece/orientation_palette_analysis.md`
- `docs/frontier/s_piece/f1_f2_balance_analysis.md`
- `docs/frontier/s_piece/f1_f2_symmetry_proof.md`
- `docs/frontier/s_piece/macro_width_survey.md`

### Tool files (continued)
- `tools/frontier/macro_local_period.py` — Template-level period analysis

## 7. Local Period Analysis

| Question | Answer |
|----------|--------|
| Can period be determined from templates alone? | **NO** — proven negative result |
| What CAN be proved from templates? | **Piece-count integrality only** |
| What REQUIRES SCC analysis? | **All remaining period factors** |
| Why? | Period = gcd of BFS distances through SCC — a global property |

See `docs/frontier/s_piece/macro_local_period_analysis.md` for full analysis.

## 8. Best Next Target

**No further S-pentacube SVG witnesses remain.** The most valuable next computation would be either:

1. **Complete the 4×8 Macro closure**: Extend the bounded closure to confirm whether the 478-state SCC is genuinely complete. This would settle the global period-10 question for 4×8.

2. **Analyse the 5×6 SCC in depth**: With 1,606 states and complete closure, this SCC is the richest available target for understanding Macro graph structure. Its period-1, mixed-parity behaviour contrasts sharply with 4×8's period-10 structure.

3. **Investigate a new piece**: One of the 22 other pentacubes (F, I, L, N, P, T, U, V, W, X, Y, Z, etc.) could be studied using the same Macro methodology, potentially revealing whether the observed structural patterns are piece-specific or universal.