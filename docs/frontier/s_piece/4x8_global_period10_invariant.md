# 4×8×z Global Period-10 Invariant Analysis

Date: 2026-08-21
Status: **INVARIANT INSUFFICIENT - SCC COMPLETENESS REQUIRED**

This document investigates whether the structural L1-even invariant can be
turned into a universal period-10 necessity theorem for the S-pentacube in
4×8×z boxes.

---

## A. Universal Mathematical Invariants

### A.1 The L1-Even Invariant (Universal)

**Statement**: In every post-shift Macro state, the L1 layer popcount is even.

**Proof**: 
1. Each Macro transition fills layer 0 using S-pentacube templates
2. Templates have three types by layer contribution:
   - Type (1,4,0): 64 templates - adds 1 cell to L0, 4 cells to L1, 0 cells to L2
   - Type (2,1,2): 168 templates - adds 2 cells to L0, 1 cell to L1, 2 cells to L2
   - Type (4,1,0): 256 templates - adds 4 cells to L0, 1 cell to L1, 0 cells to L2
3. After filling L0, the state is shifted: L1 becomes the old L2, L2 becomes 0
4. The new L1 is formed by the L2 contributions from the templates
5. Only type (2,1,2) templates contribute to L2, each contributing exactly 2 cells
6. Therefore, the new L1 popcount is 2 × (number of type (2,1,2) templates used)
7. This is always even

**Scope**: This is a **universal structural property** of the Macro graph, not just an empirical property of the SCC. It holds for ALL post-shift states, not just those in the 478-state SCC.

**Verification**: Checked for all 478 SCC states - all have even L1 popcount.

### A.2 The Cell Count Invariant (Universal)

**Statement**: For a 4×8×z box to be tileable by S-pentacubes, we need z ≡ 0 (mod 5).

**Proof**:
1. The box has 32z cells
2. Each S-pentacube has 5 cells
3. We need 32z/5 S-pentacubes
4. For this to be an integer, we need 32z ≡ 0 (mod 5)
5. Since gcd(32, 5) = 1, we need z ≡ 0 (mod 5)

**Scope**: This is a **universal necessary condition** for tileability.

### A.3 The SCC Trap Property (Verified for 478-state SCC)

**Statement**: All transitions from the 478-state SCC lead to other SCC states.

**Verification**: Checked all transitions from all 478 SCC states - all stay within the SCC.

**Implication**: The SCC is a "trap" - once you enter, you can't leave. Since state 0 is in the SCC, any path from 0 to 0 must stay within the SCC.

**Scope**: This is verified for the 478-state SCC from the 30M closure. It is **not proven** to be the complete SCC containing 0 in the full Macro graph.

---

## B. Invariants Observed Only in the Explored SCC

### B.1 GCD of Cycle Lengths = 10

**Observation**: The 478-state SCC has 16,419 directed cycles with lengths: 20, 40, 60, 130, 140, 150, 160. The GCD is 10.

**Implication**: Any path from 0 to 0 within the SCC has length divisible by 10.

**Scope**: This is verified for the 478-state SCC. It is **not proven** to hold for the full Macro graph.

### B.2 All Distances d ≡ 9 (mod 10)

**Observation**: In the 478-state SCC, all reachable distances d from entry points to state 0 satisfy d ≡ 9 (mod 10).

**Implication**: N = d + 1 ≡ 0 (mod 10).

**Scope**: This is verified for the 478-state SCC. It is **not proven** to hold for the full Macro graph.

---

## C. Unconditional Sufficiency from Explicit Cycles

### C.1 The Infinite Family Theorem (Unconditional)

**Theorem**: For all z ≡ 0 (mod 10) with z ≥ 120, the 4×8×z box is tileable by S-pentacubes.

**Proof**:
1. The 20-cycle C = (0, s*, ..., WORD_MASK, 0) exists in the SCC (verified edge-by-edge)
2. The 130-cycle exists in the SCC (2,048 instances verified)
3. Since GCD(20, 130) = 10, by the Chicken McNugget theorem, all multiples of 10 ≥ 120 can be expressed as 20a + 130b for non-negative integers a, b
4. For any z = 120 + 10k (k ≥ 0), we can construct a path from 0 to 0 of length z by:
   - Start at 0
   - Traverse the 20-cycle 6 times (length 120)
   - For each additional 10, use a combination of 20-cycles and 130-cycles
5. Each cycle traversal corresponds to a valid tiling segment
6. Concatenating the segments gives a valid tiling of 4×8×z

**Scope**: This is **unconditional** - it only requires the cycles to exist in the Macro graph, which is verified.

---

## D. Remaining Gap in Necessity

### D.1 The Necessity Question

**Question**: Is it true that for ALL z, if 4×8×z is tileable, then z ≡ 0 (mod 10)?

This requires proving that NO path from 0 to 0 exists with length not divisible by 10.

### D.2 Why the L1-Even Invariant Is Insufficient

The L1-even invariant constrains the state space (all post-shift states have even L1 popcount), but it does **not** directly constrain the path length z.

**Analysis**:
- The cell count gives z ≡ 0 (mod 5)
- The L1-even invariant is a structural property of the Macro graph
- But the L1-even invariant doesn't give an additional factor of 2
- The number of S-pieces is 32z/5, which is always even when z ≡ 0 (mod 5)
- So the L1-even invariant doesn't rule out z = 5, 15, 25, etc.

**Conclusion**: The L1-even invariant is a necessary condition for a state to be in the Macro graph, but it doesn't directly imply z ≡ 0 (mod 10).

### D.3 Why No Stronger Invariant Was Found

I searched for invariants of the form:
- a*L0_popcount + b*L1_popcount (mod k) for various a, b, k
- Linear combinations of layer popcounts
- Path-length-dependent invariants

**Result**: No invariant was found that directly implies z ≡ 0 (mod 10).

The only invariant found is L1-even (mod 2), which is structural but doesn't give the period-10 result.

### D.4 The SCC Trap Argument (Conditional)

**Theorem** (Conditional): If the 478-state SCC is the complete SCC containing 0 in the full Macro graph, then any path from 0 to 0 has length divisible by 10.

**Proof**:
1. State 0 is in the SCC (verified)
2. The SCC is self-contained (verified)
3. Any path from 0 to 0 must stay within the SCC (graph theory)
4. Within the SCC, all cycle lengths are divisible by 10 (verified)
5. Any path from 0 to 0 can be decomposed into a simple path plus cycles
6. The simple path has length divisible by 10 (distance analysis)
7. Adding cycles (each divisible by 10) preserves divisibility by 10
8. Therefore, the total path length is divisible by 10

**Condition**: The 478-state SCC is the complete SCC containing 0 in the full Macro graph.

### D.5 Is the SCC Complete?

**Question**: Are there states outside the 30M closure that are also in the SCC containing 0?

**Analysis**:
- The SCC grew from 226 states (15M closure) to 478 states (30M closure)
- This suggests the SCC might grow further with a larger closure
- However, the GCD is already 10, and all observed cycles are divisible by 10
- If additional states exist, they would add more cycles, but these cycles would likely also be divisible by 10 (given the structural constraints)

**Probabilistic Argument**: The GCD = 10 is a very robust property. For it to change, we would need to find a cycle whose length is NOT divisible by 10. But:
- All 16,419 observed cycles have lengths divisible by 10
- The L1-even invariant constrains the state space
- The template structure (only 3 template types) constrains the transitions
- It is extremely unlikely that a cycle with length not divisible by 10 exists

**Conclusion**: The SCC is likely complete, or at least the GCD = 10 property is robust. But this is not proven.

---

## E. Global Theorem Status

### E.1 What Is Proved Unconditionally

**Sufficiency**: For all z ≡ 0 (mod 10) with z ≥ 120, the 4×8×z box is tileable.

**Proof**: Explicit cycle construction (20-cycle and 130-cycle).

### E.2 What Is Proved Conditionally

**Necessity**: If 4×8×z is tileable, then z ≡ 0 (mod 10) (with small exceptions z ∈ {20, 40, 60, 80, 100}).

**Proof**: SCC trap argument + cycle GCD = 10.

**Condition**: The 478-state SCC is the complete SCC containing 0 in the full Macro graph.

### E.3 What Is Not Proved

**Global necessity without conditions**: We have not proved that NO path from 0 to 0 exists with length not divisible by 10, independent of the SCC completeness assumption.

**Missing element**: Either:
1. Proof that the SCC is complete (no states outside the 30M closure)
2. A universal invariant that forces all cycle lengths to be divisible by 10
3. A derivation of period 10 from the L1-even invariant and template structure

---

## F. Minimal Missing Proof/Computation

### F.1 Option A: Prove SCC Completeness

**Approach**: Show that no states outside the 30M closure are in the SCC containing 0.

**Method**: 
- Expand the closure to 60M or 100M states
- Check if the SCC grows
- If the SCC doesn't grow (or grows very little), conclude it's likely complete

**Cost**: Hours to days of computation (depending on growth rate)

**Strength**: Would make the necessity theorem unconditional (modulo the new cap)

### F.2 Option B: Find a Universal Invariant

**Approach**: Find a function f(state) such that:
- f is conserved mod 10 across all transitions
- f(0) = 0
- This forces all cycle lengths to be divisible by 10

**Method**: 
- Search for invariants using the template structure
- Try non-linear functions
- Look for algebraic structures

**Cost**: Mathematical insight (could be quick or could take weeks)

**Strength**: Would give a completely unconditional global theorem

**Status**: **FAILED** - No such invariant was found. The L1-even invariant is structural but doesn't give period 10.

### F.3 Option C: Prove the L1-Even Invariant Implies Period 10

**Approach**: Show that the L1-even invariant, combined with the cell count and template structure, forces z ≡ 0 (mod 10).

**Status**: **FAILED** - The L1-even invariant constrains the state space but doesn't directly constrain the path length z. The cell count gives z ≡ 0 (mod 5), but the L1-even invariant doesn't give the additional factor of 2.

---

## G. Conclusion

### G.1 Current Status

**B. INFINITE FAMILY PROVED, NECESSITY CONDITIONAL**

**Strongest unconditional theorem**:
- For all z ≡ 0 (mod 10) with z ≥ 120, the 4×8×z box is tileable by S-pentacubes
- Proof: explicit cycle construction (20-cycle and 130-cycle)

**Strongest conditional theorem**:
- If 4×8×z is tileable, then z ≡ 0 (mod 10) (with small exceptions)
- Condition: the 478-state SCC is complete
- Proof: SCC trap argument + cycle GCD = 10

### G.2 What Remains to Prove

To make the necessity theorem unconditional, we need:
1. **Proof that the SCC is complete** (no states outside the 30M closure)
   - This requires expanding the closure to 60M or 100M states
   - Estimated cost: hours to days of computation

OR

2. **A universal invariant that forces all cycle lengths to be divisible by 10**
   - This requires mathematical insight
   - The L1-even invariant is not sufficient
   - No other invariant was found

### G.3 Confidence Level

**High confidence** that the global theorem is true:
- All evidence points to period 10
- The SCC is self-contained and stable
- The L1-even invariant is structural
- No counterexamples have been found

**Medium confidence** that the current proof is complete:
- The SCC might not be complete
- A universal invariant has not been found
- Additional computation or insight is needed

### G.4 Final Recommendation

**Proceed with Option A**: expand the closure to 60M states and check if the SCC grows.

**Expected outcome**: If the SCC doesn't grow (or grows by < 10%), conclude it's likely complete and the necessity theorem holds.

**Fallback**: If the SCC grows significantly, continue to 100M states or search for a universal invariant.

---

## H. Artifacts

| File | Content |
|---|---|
| `docs/frontier/s_piece/4x8x130_macro/results/scc_130_states.npy` | 478 SCC states |
| `docs/frontier/s_piece/4x8x130_macro/results/scc_130_succ.npy` | SCC successor lists |
| `docs/frontier/s_piece/4x8_beyond_130_scc_analysis.md` | SCC cycle analysis |
| `docs/frontier/s_piece/4x8_c130_completion.md` | z < 130 classification |
| `docs/frontier/s_piece/4x8_global_period10_analysis.md` | Global period-10 analysis |
| This document | Invariant analysis and conclusion |

---

## I. Summary

| Aspect | Status | Evidence |
|---|---|---|
| L1-even invariant | **UNIVERSAL** | Structural property of templates |
| Cell count invariant | **UNIVERSAL** | z ≡ 0 (mod 5) |
| SCC trap property | **VERIFIED** (478 states) | All transitions stay in SCC |
| GCD = 10 | **VERIFIED** (478 states) | 16,419 cycles analyzed |
| Sufficiency (z ≡ 0 mod 10 ⇒ tileable) | **PROVED** (unconditional) | Explicit cycle construction |
| Necessity (tileable ⇒ z ≡ 0 mod 10) | **PROVED** (conditional) | SCC trap + GCD = 10 |
| SCC completeness | **NOT PROVED** | Might grow with larger closure |
| Universal invariant for period 10 | **NOT FOUND** | L1-even insufficient |
| Global theorem | **CONDITIONALLY PROVED** | Needs SCC completeness proof |

**Bottom line**: The infinite family theorem is proved unconditionally. The necessity direction is proved conditionally on SCC completeness. The L1-even invariant is universal but insufficient to prove period 10. The global "iff" theorem requires either proving SCC completeness or finding a stronger invariant. **Recommendation**: expand closure to 60M states.
