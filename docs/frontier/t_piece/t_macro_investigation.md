# T-Pentacube Macro Investigation

**Date**: 2026-08-26  
**Status**: COMPLETE — First T Macro cycles extracted and verified

> **[PROVENANCE BANNER 2026-08-27]** The **3×8 figures in §1.1 and the
> Tractability table are capped-run values, not closure results**: that
> exploration stopped at exactly `max_states = 200,000` (table row
> "Macro states 200,004" is the cap boundary; `macro_cap_hit` was true; the
> quoted 3s runtime matches). The "SCC(0) size 273" for 3×8 is the partial
> ancestor set of state 0 on that truncated graph — reproduced exactly by
> rerun on 2026-08-27. The completed uncapped closure gives 916,153 states /
> 958,474 edges with SCC(0) = 2,939 (period 5, shortest closed walk 15,
> |pred(0)| = 4): see `t_3x8_global_theorem.md` and
> `data/frontier/t_piece/t_3x8_global_certificate.json`
> (`cap_hit=false`, `queue_exhausted=true`; all figures independently
> reproduced 2026-08-27). The other rows of these tables were computed at
> their stated sizes without caps. Original text below preserved verbatim.

---

## 1. Summary

The Macro proof framework has been successfully transferred from S-pentacube to T-pentacube. The transfer revealed both universal components and piece-specific differences.

### 1.1 Key results

| Cross-section | Area | SCC(0) size | Cycle lengths | GCD | Matches catalogue? |
|---------------|------|-------------|---------------|-----|-------------------|
| 3×7 | 21 | 39 | {20} | 20 | ✅ 3×7×20 prime |
| 3×8 | 24 | 273 | {15,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,150} | 5 | ✅ primes 15,35,40 |
| 3×10 | 30 | (bounded) | — | — | ✅ primes exist |
| 3×12 | 36 | (bounded) | — | — | ✅ primes 15,20,25 |
| 5×5 | 25 | 141 | {12} | 12 | ✅ 5×5×12 prime |

### 1.2 Concrete cycle extracted

- **Piece**: T
- **Cross-section**: 3×7
- **Cycle length**: 20
- **SCC size**: 39 states
- **Total macro states**: 6,163
- **Templates in cycle**: 82
- **File**: `tools/frontier/_t_3x7_concrete_cycles.json`

---

## 2. Tractability Comparison

| Metric | S 4×5 | S 5×6 | T 3×7 | T 3×8 | T 5×5 |
|--------|-------|-------|-------|-------|-------|
| Area | 20 | 30 | 21 | 24 | 25 |
| First-gen sources | 1,500 | 184,000 | 204 | 689 | 2,834 |
| Macro states | 1,500 | 8,000,000 | 6,163 | 200,004 | 54,434 |
| SCC(0) size | 11 | 1,606 | 39 | 273 | 141 |
| Runtime | seconds | minutes | 0.4s | 3s | 1.7s |

T 3×7 is the most tractable cross-section tested so far across both pieces.

---

## 3. Structural Observations

### 3.1 L2 is always empty in post-shift states

For T, every post-shift macro state has L2 = ∅. This is because:
- T has no z-span=2 orientations (unlike S)
- z-span=3 orientations place cells in L2, but these are shifted to L1 in the next edge
- Flat orientations (z-span=1) never touch L2

This means the effective state space is 2-layer (L0, L1) rather than 3-layer.

### 3.2 Flat orientations simplify filling

The 4 flat orientations allow a single piece to fill 5 cells in L0. This means:
- The "fill L0" phase can complete with fewer pieces
- The predecessors of 0 are states with L1 = L2 = ∅ (not just the gate state)
- The gate criterion is generalized

### 3.3 Cycle lengths are multiples of 5

For all T cross-sections tested, cycle lengths are multiples of 5:
- 3×7: 20 = 4 × 5
- 3×8: 15, 30, 35, 40, ... (all multiples of 5)
- 5×5: 12 (not a multiple of 5, but area=25 is divisible by 5)

This is because the area must be divisible by 5 for any tiling to exist (volume = a×b×z must be divisible by 5).

---

## 4. Global Theorem Status

### 4.1 T 3×7: GLOBAL THEOREM

**Status**: PROVEN — First global Macro theorem for a non-S pentacube

| Metric | Value |
|--------|-------|
| Total macro states | 6,163 |
| Macro edges | 6,187 |
| First-gen sources | 204 |
| SCC(0) size | 39 |
| SCC(0) edges | 40 |
| Graph period | 20 |
| Return lengths from 0 | {20} |
| Transient states | 6,124 |
| Recurrent SCCs | 1 (SCC(0)) |
| Queue exhausted | Yes |
| Cap hit | No |

**Theorem**: 3×7×z is tileable by T-pentacubes **iff** 20 | z.

**Certificate**: `data/frontier/t_piece/t_3x7_global_certificate.json` — GLOBAL, verified.

### 4.2 T 5×5: GLOBAL THEOREM

**Status**: PROVEN — Upgraded from SCC-local to GLOBAL

| Metric | Value |
|--------|-------|
| Total macro states | 54,434 |
| Macro edges | 56,192 |
| First-gen sources | 2,834 |
| SCC(0) size | 141 |
| SCC(0) edges | 168 |
| Graph period | 12 |
| Return lengths from 0 | {12, 36} |
| Queue exhausted | Yes |
| Cap hit | No |

**Theorem**: 5×5×z is tileable by T-pentacubes **iff** 12 | z.

**Certificate**: `data/frontier/t_piece/t_5x5_global_certificate.json` — GLOBAL, verified.

### 4.3 T 3×8: GLOBAL THEOREM

**Status**: PROVEN — Second global T theorem, first T example of period < shortest cycle

| Metric | Value |
|--------|-------|
| Total macro states | 916,153 |
| Macro edges | 958,474 |
| First-gen sources | 689 |
| SCC(0) size | 2,939 |
| SCC(0) edges | 3,288 |
| Graph period | **5** |
| Shortest cycle | **15** |
| Return lengths | {15, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 135} |
| Non-rep multiples of 5 | {5, 10, 20, 25} |
| Conductor | 30 |
| Queue exhausted | Yes |
| Cap hit | No |

**Theorem**: 3×8×z is tileable by T-pentacubes iff z is a multiple of 5 and z ∉ {5, 10, 20, 25}. All multiples of 5 ≥ 30 are tileable.

**Certificate**: `data/frontier/t_piece/t_3x8_global_certificate.json` — GLOBAL, verified.

---

## 5. Comparison of Three Complete T Systems

| Property | T 3×7 | T 5×5 | T 3×8 |
|----------|-------|-------|-------|
| Area | 21 | 25 | 24 |
| Area mod 5 | 1 | 0 | 4 |
| Macro states | 6,163 | 54,434 | 916,153 |
| Macro edges | 6,187 | 56,192 | 958,474 |
| First-gen sources | 204 | 2,834 | 689 |
| Sources in SCC(0) | 2 | 4 | 4 |
| Dead-end sources | 202 | 2,830 | 685 |
| SCC(0) size | 39 | 141 | 2,939 |
| SCC(0) edges | 40 | 168 | 3,288 |
| Graph period | 20 | 12 | **5** |
| Shortest cycle | 20 | 12 | **15** |
| Period < shortest cycle? | No | No | **Yes** |
| Gate predecessors | 2 | 2 | 4 |
| Gate = (FULL,0,0)? | No | No | No |
| Theorem status | GLOBAL | GLOBAL | GLOBAL |

### Key observations:

1. **Period does not correlate simply with area**: 3×7 (area 21) has period 20, 5×5 (area 25) has period 12, 3×8 (area 24) has period 5.

2. **Period < shortest cycle occurs for T**: T 3×8 (period 5, shortest 15) parallels S 4×8 (period 10, shortest 20). This is not S-specific.

3. **Gate structure is consistent**: All three T cross-sections have predecessors of 0 with L1 = L2 = ∅, and none have (FULL,0,0) as a macro state.

4. **SCC size grows with area but not monotonically**: 3×7 (area 21) → 39 states, 5×5 (area 25) → 141 states, 3×8 (area 24) → 2,939 states. The 3×8 SCC is disproportionately large.

5. **All three theorems are now GLOBAL**: T is the first pentacube with multiple global Macro theorems.

---

## 6. Open Questions

1. **T 3×10 and 3×12**: Can these be completely closed? Currently bounded.
2. **Period prediction**: Can the period be predicted from cross-section dimensions and piece geometry?
3. **Period < shortest cycle**: What determines when this occurs? It happens for S 4×8 and T 3×8 but not for other cross-sections.
4. **Catalogue completeness for 5×5**: The catalogue lists only 5×5×12 as prime. The theorem predicts all multiples of 12 are tileable. Are there published solutions for 5×5×24, ×36, etc.?

---

## 5. Data Files

| File | Contents |
|------|----------|
| `tools/frontier/_t_3x7_concrete_cycles.json` | Verified cycle data for T 3×7 |
| `data/frontier/t_piece/t_orientation_table.json` | T orientation feature table |
| `docs/frontier/t_piece/t_source_survey.md` | Source provenance survey |
| `docs/frontier/t_piece/t_macro_faithfulness.md` | Faithfulness theorem for T |
| `docs/frontier/t_piece/t_methodology_transfer.md` | Methodology transfer analysis |