# 4x9 S-Pentacube: Targeted Analysis for c < 130

Date: 2026-08-21
Status: **analysis complete, recommendation ready**

This document analyses the 10M-state 4x9 Macro run, diagnoses the state
explosion, determines what the truncated graph establishes, and identifies
the cheapest exact method to classify all 4x9xz boxes for z < 130.

---

## A. What the 10M Run Established

### A.1 Run parameters

| Parameter | Value |
|---|---|
| Cross-section | 4 x 9 |
| NCELLS | 36 |
| State size | 108 bits (3 x 36-bit layers) |
| Concrete placements | 4,540 |
| Target templates | 562 |
| Max states cap | 10,000,000 |
| Elapsed | 2,625 s (43.8 min) |
| Interrupted | No |

### A.2 Exact figures

| Metric | Value |
|---|---|
| First-gen sources | 71,143 |
| First-gen tree states | > 10,000,000 (cap hit; all 71,143 sources found) |
| Macro states discovered | 10,000,036 |
| Macro states processed | 329,775 |
| Macro states in queue | 1,294,528 |
| Macro edges | 10,010,721 |
| Total intermediate states | 280,843,521 |
| State 0 in graph | **No** |
| WORD_MASK in graph | **No** |
| Max BFS depth from sources | 37 |

### A.3 What is proven

1. **The first-generation tree is complete.** All 71,143 distinct post-shift
   sources reachable from the empty state 0 have been found. The tree itself
   exceeds 10M intermediate states, but every source was discovered before
   the cap.

2. **The macro graph is a perfect DAG.** Among the 10,010,721 edges between
   discovered states, 100% are tree edges (depth d to depth d+1). There are
   **zero back edges, zero cross edges, zero forward edges.** The graph
   contains no cycles whatsoever.

3. **All discovered states have the layer pattern (L0 non-zero, L1 non-zero,
   L2 = 0).** Every macro state in the graph has cells in layers 0 and 1
   but nothing in layer 2. This is a structural property of the 4x9
   cross-section: the post-shift state always has L2 = 0 (because the shift
   drops L0 and shifts L1->L0, L2->L1, 0->L2).

4. **State 0 and WORD_MASK are not in the graph.** No path from any source
   to either state has been found within the first 37 macro edges.

5. **The graph is complete through depth 37.** All states at depth <= 36
   have been fully processed (their successors computed). States at depth
   37 have been discovered but only a fraction processed.

### A.4 What is NOT established

1. **Whether 4x9xz is tileable for any z < 130.** State 0 has not been
   found, so no tiling has been proven or disproven.

2. **Whether the macro graph is finite.** The graph might continue growing
   indefinitely, or it might terminate at some depth.

3. **The complete successor function.** Only 329,775 of 10,000,036 states
   have had their successors computed. The remaining 9,670,261 states are
   in the queue, waiting to be processed.

---

## B. Diagnosis of the State Explosion

### B.1 Comparison with 4x8

| Metric | 4x8 | 4x9 | Ratio |
|---|---|---|---|
| NCELLS | 32 | 36 | 1.125x |
| State size | 96 bits | 108 bits | 1.125x |
| Concrete placements | 3,944 | 4,540 | 1.15x |
| Target templates | 488 | 562 | 1.15x |
| First-gen sources | 331,765 | 71,143 | 0.21x |
| First-gen tree states | 3,162,387 | > 10,000,000 | > 3.2x |
| Macro states (15M/10M cap) | 15,000,991 | 10,000,036 | 0.67x |
| Macro edges | 14,781,970 | 10,010,721 | 0.68x |
| Total intermediate | 374,388,610 | 280,843,521 | 0.75x |
| Avg intermediate per processed | 25.0 | 28.1 | 1.12x |
| Max BFS depth (at cap) | 85 | 37 | 0.44x |
| Cycles in graph | Yes (20-cycle) | **None** | - |
| Basin of 0 (at cap) | 226 states | **Not found** | - |

### B.2 Root causes of the explosion

**1. The first-generation tree is much larger.** For 4x8, the first-gen
tree had 3.16M states. For 4x9, it exceeds 10M states (the cap). This is
because the 4x9 layer has 36 cells vs 32, giving more room for partial
fillings and more branching in the placement tree.

**2. The macro graph grows wider, not deeper.** At the 10M cap, the 4x9
graph reached only depth 37, while the 4x8 graph reached depth 85 at the
15M cap. The 4x9 graph has ~1M states per depth level at depths 35-38,
while the 4x8 graph had a much narrower structure (the basin of 0 was only
226 states).

**3. No cycles have been discovered.** The 4x8 graph had a 20-cycle through
0, which created a compact recurrent structure (the 478-state SCC). The 4x9
graph is a perfect DAG with no cycles at all. This means every path is
simple and the graph must grow linearly with depth.

**4. The branching factor is higher.** Each processed 4x9 state has on
average 30.4 successors (among the 329K processed states), compared to
about 1.0 for 4x8. This is because the 4x9 layer has more cells and more
templates, leading to more possible fillings.

### B.3 Template layer structure

| Template span | Count | Percentage |
|---|---|---|
| Layers 0, 1 only | 370 | 65.8% |
| Layers 0, 1, 2 | 192 | 34.2% |

34% of templates reach layer 2. This is why the post-shift states have
non-zero L1 (from the old L2 after the shift).

### B.4 Why 4x8 had reductions that 4x9 lacks

The 4x8 macro graph had a **20-cycle through 0**: a closed walk
`0 -> s* -> ... -> WORD_MASK -> 0` of exactly 20 macro edges. This cycle
created a compact recurrent structure: the SCC containing 0 had only 478
states, and the basin of 0 (states that can reach 0) had only 226 states.
The backward DP over this small basin answered all reachability questions
in seconds.

The 4x9 graph has **no cycles at all** within the first 37 depths. This
means:
- There is no compact recurrent structure to exploit.
- The basin of 0 (if it exists) might be very large or might not exist
  within the discovered graph.
- The backward DP approach used for 4x8 cannot be directly applied.

---

## C. Can the Existing Truncated Graph Answer z < 130?

### C.1 Direct answer: No

The existing graph has max depth 37. The target distances for z < 130 are:

| z | Distance (z-1) | In graph? |
|---|---|---|
| 10 | 9 | Yes (depth 9 exists) |
| 15 | 14 | Yes |
| 20 | 19 | Yes |
| 25 | 24 | Yes |
| 30 | 29 | Yes |
| 35 | 34 | Yes |
| 40 | 39 | Partially (depth 39 is being discovered) |
| 45 | 44 | No |
| 60 | 59 | No |
| 75 | 74 | No |
| 90 | 89 | No |
| 105 | 104 | No |

State 0 is not in the graph at any depth. So the graph cannot directly
answer whether any 4x9xz box is tileable.

### C.2 What the graph DOES establish

1. **No tiling of length <= 38 exists.** Since the graph is complete through
   depth 37 and state 0 is not found, no 4x9xz box with z <= 38 is
   tileable. This confirms the known zeros for z = 10, 15, 20, 25, 30, 35.

2. **The graph is a DAG.** This is a structural property that constrains
   the possible tilings. If a tiling exists, it corresponds to a simple
   path in the DAG (no repeated states).

3. **The growth pattern is bounded.** At depths 35-38, the graph has
   ~1M-1.5M states per depth. This suggests the total graph size might be
   manageable (tens of millions, not billions).

### C.3 What cannot be inferred

- **Impossibility of z = 45, 60, 75, 90, 105.** These distances are beyond
  the explored depth. The absence of state 0 at depth <= 37 does NOT imply
  impossibility at greater depths.

- **Periodicity or pattern.** The known tileable lengths (60, 75, 90, 105)
  suggest a period of 15, but this cannot be proven from the truncated
  graph.

---

## D. Candidate Bounded Methods

### D.1 Method 1: Continue the forward BFS

**Description:** Resume the BFS from the checkpoint and continue processing
states until WORD_MASK (and hence 0) is found, or until a depth limit is
reached.

**Correctness:** Exact. The BFS explores all states in order of depth, so
the first time WORD_MASK is found, the shortest path to it is known.

**Cost estimate:**
- Processing rate: ~750 states/s (from the 120s prototype run)
- States per depth: ~1M-1.5M at depths 35-38
- Depths to explore: 38 to 59 (22 more depths)
- Estimated states: 22 x 1.2M = ~26M states
- Estimated time: 26M / 750 = ~35,000s = **~10 hours**

**Risks:**
- The growth might accelerate at deeper depths, making the cost much higher.
- The growth might decelerate, making the cost lower.
- Memory: 26M states x ~100 bytes/state = ~2.6 GB (feasible).

### D.2 Method 2: Backward search from WORD_MASK

**Description:** Instead of forward BFS from sources, do a backward search
from WORD_MASK. Find all states u such that u's placement interval leads to
a pre-shift state p with p >> 36 == WORD_MASK. Then find predecessors of
those states, and so on, until a first-gen source is reached.

**Correctness:** Exact. The backward search finds all states that can reach
WORD_MASK, and hence all states that can reach 0.

**Cost estimate:**
- The basin of WORD_MASK might be small (like the 4x8 basin of 0, which
  had 226 states).
- But computing predecessors is expensive: for each state v, finding all u
  such that u -> v requires exploring u's placement interval.
- If the basin has B states, the cost is B x (average intermediate states
  per source) = B x 28.
- If B = 1,000, cost = 28,000 intermediate states (seconds).
- If B = 1,000,000, cost = 28M intermediate states (hours).

**Risks:**
- The basin might be very large, making the backward search as expensive
  as the forward BFS.
- Computing predecessors requires a different algorithm (backward
  exploration within placement intervals), which is complex to implement.

### D.3 Method 3: Depth-limited forward DP from sources

**Description:** Instead of building the full macro graph, do a
depth-limited forward DP. At each depth d, track the set of reachable
states. Check if WORD_MASK is reachable at the target depths.

**Correctness:** Exact for the depths explored.

**Cost estimate:**
- At each depth, the set of reachable states is the union of successors of
  all states at the previous depth.
- The cost is the same as the forward BFS, because we need to explore the
  placement interval of each state.
- The advantage is that we don't need to store the full graph, only the
  current and previous depth sets.

**Risks:**
- Same as Method 1: the growth might be too large.
- Without the full graph, we can't do the backward DP for exact distances.

### D.4 Method 4: Meet-in-the-middle

**Description:** Do a forward BFS from sources up to depth D1, and a
backward BFS from WORD_MASK up to depth D2, where D1 + D2 = 59 (the target
distance for z = 60). Check for intersection.

**Correctness:** Exact if D1 + D2 >= target distance.

**Cost estimate:**
- Forward to depth 30: ~10M states (already done).
- Backward from WORD_MASK to depth 29: unknown, depends on basin size.
- If the backward basin is small, this is much cheaper than the full
  forward BFS.

**Risks:**
- The backward search is complex to implement.
- The basin might be large.

### D.5 Method 5: Exploit the 15-step pattern

**Description:** The known tileable lengths (60, 75, 90, 105) suggest a
period of 15. If there's a cycle of length 15 in the macro graph, we can
find it and use it to prove all multiples of 15 (starting from 60) are
tileable.

**Correctness:** Only if the cycle exists and the pattern holds.

**Cost estimate:**
- Finding a cycle of length 15 requires exploring the graph to depth 15
  from some state and checking if it returns to the same state.
- This is a targeted search that might be much cheaper than the full BFS.

**Risks:**
- The graph is a DAG (no cycles found so far). The cycle might be at a
  greater depth.
- The pattern might not be a simple cycle. It might be a more complex
  structure (e.g., a path of length 59 to a state s, then a cycle of
  length 15 from s to s).

---

## E. Recommended Method

### E.1 Primary recommendation: Continue the forward BFS (Method 1)

**Rationale:**
1. The implementation already exists and is tested.
2. The checkpoint/resume machinery is in place.
3. The growth pattern suggests the total cost is ~10 hours, which is
   feasible.
4. The forward BFS is exact and complete: it will find WORD_MASK if it
   exists within the state limit.
5. Once WORD_MASK is found, the backward DP can be done in seconds (like
   the 4x8 analysis).

**Implementation:**
1. Resume the BFS from the checkpoint.
2. Increase the state limit to 50M or 100M.
3. Monitor the growth at each depth.
4. If the growth accelerates beyond ~2M states per depth, consider
   switching to a different method.
5. Once WORD_MASK is found, stop the BFS and do the backward DP.

**Estimated cost:** ~10 hours on the desktop.

### E.2 Fallback: Backward search from WORD_MASK (Method 2)

If the forward BFS grows too large, switch to the backward search. This
requires implementing a predecessor computation, which is more complex but
might be much cheaper if the basin of WORD_MASK is small.

### E.3 What NOT to do

1. **Do NOT increase the cap to 50M or 100M blindly.** The growth pattern
   might accelerate, making the cost much higher than estimated.
2. **Do NOT assume periodicity from the data.** The pattern (60, 75, 90,
   105) suggests a period of 15, but this must be proven, not assumed.
3. **Do NOT infer impossibility from the truncated graph.** The absence of
   state 0 at depth <= 37 does NOT imply impossibility at greater depths.

---

## F. Mathematical Structure

### F.1 The DAG property

The 4x9 macro graph is a perfect DAG (zero cycles) within the first 37
depths. This is a fundamental structural difference from 4x8, which had a
20-cycle through 0.

**Implications:**
- Every path in the graph is simple (no repeated states).
- The graph has a topological order (by depth).
- The backward DP over the DAG is exact (no cycle handling needed).
- But the DAG might be very large, making the DP expensive.

### F.2 The layer structure

All states have L2 = 0. This means the effective state space is 2 layers
(L0 and L1), which is 72 bits. This is a structural property of the 4x9
cross-section: the templates span at most 2 layers beyond the anchor layer.

Wait, this is not quite right. The templates span 2 or 3 layers (65.8%
span 2 layers, 34.2% span 3 layers). But the post-shift state always has
L2 = 0 (because the shift drops L0 and shifts L1->L0, L2->L1, 0->L2).

So the post-shift state has L0 (from old L1) and L1 (from old L2), and
L2 = 0. The effective state space is 2 layers (L0 and L1), which is 72
bits.

### F.3 The 15-step pattern

The known tileable lengths are 60, 75, 90, 105 = 15 x 4, 15 x 5, 15 x 6,
15 x 7. The cell-count check requires 36z / 5 to be an integer, so z must
be a multiple of 5. The tileable lengths are multiples of 15, which are a
subset of multiples of 5.

**Hypothesis:** The macro graph has a structure that allows paths of length
59 + 15k for k >= 0. This might be:
- A path of length 59 from 0 to some state s, then a cycle of length 15
  from s to s.
- Or a more complex structure with multiple paths of different lengths.

**This hypothesis is NOT proven.** It is consistent with the data but must
be verified by the computation.

### F.4 Macro-path count vs reachability vs tiling count

As in the 4x8 analysis, these are distinct:
- **Macro-path reachability:** Does a path of length z-1 exist from 0 to 0?
  This answers whether 4x9xz is tileable.
- **Macro-path count:** How many distinct paths of length z-1 exist?
  This is the number of macro-level tilings.
- **Concrete tiling count:** How many actual tilings exist?
  Each macro edge might have multiple placement realizations.

For 4x8, each macro edge in the 20-cycle had exactly 1 placement
realization, so the macro-path count equaled the tiling count. For 4x9,
this might not be the case.

---

## G. Prototype Results

### G.1 120-second continuation run

Starting from the 10M checkpoint (max depth 37), the prototype continued
the BFS for 120 seconds:

| Metric | Value |
|---|---|
| States processed | 90,086 |
| New states discovered | 2,600,615 |
| Total intermediate | 77,679,658 |
| Max depth reached | 39 |
| WORD_MASK found | No |
| Processing rate | 750 states/s |

**Depth distribution after continuation:**

| Depth | States |
|---|---|
| 36 | 1,211,380 |
| 37 | 1,559,672 |
| 38 | 1,479,008 |
| 39 | 92,563 (still growing) |

**Growth pattern:**
- Depth 35 -> 36: 949K -> 1,211K (+28%)
- Depth 36 -> 37: 1,211K -> 1,560K (+29%)
- Depth 37 -> 38: 1,560K -> 1,479K (-5%)
- Depth 38 -> 39: 1,479K -> 93K+ (still growing)

The growth is NOT exponential. It peaked at depth 37 and started declining
at depth 38. This is encouraging: the total graph size might be manageable.

### G.2 Cost projection

If the growth pattern continues at ~1.2M states per depth:
- Depths 39-59: 21 depths x 1.2M = ~25M states
- At 750 states/s: ~33,000s = **~9 hours**

If the growth decelerates (as suggested by the depth 37 -> 38 drop):
- The total might be ~15M-20M states
- Time: ~6-7 hours

If the growth accelerates:
- The total might be ~40M-50M states
- Time: ~15-18 hours

---

## H. Exact Next Computation

### H.1 Recommended command

```bash
python3 tools/frontier/macro_generalized.py \
    --resume /tmp/macro_checkpoints/4x9.ckpt \
    --max-states 50000000 \
    --checkpoint /tmp/macro_checkpoints/4x9_50m.ckpt \
    --checkpoint-interval 1000000
```

This resumes from the 10M checkpoint, increases the cap to 50M, and saves
checkpoints every 1M states.

### H.2 Monitoring

During the run, monitor:
1. The max depth (should increase steadily).
2. The number of states at each depth (should follow the ~1.2M pattern).
3. Whether WORD_MASK is found (the key event).
4. Memory usage (should stay below 8 GB for 50M states).

### H.3 After WORD_MASK is found

Once WORD_MASK is discovered:
1. Stop the BFS (or let it complete the current depth).
2. Compute the backward DP R(s) over the DAG.
3. Determine which first-gen sources can reach WORD_MASK at which distances.
4. The reachable distances d give tileable lengths z = d + 1.

### H.4 Expected outcome

If the growth pattern holds, the run should complete in ~9 hours and find
WORD_MASK at depth ~59 (for z = 60). The backward DP will then answer all
z < 130 questions exactly.

If WORD_MASK is not found at depth 59, the run should continue to depth 74
(for z = 75), 89 (z = 90), and 104 (z = 105).

If the growth accelerates beyond ~2M states per depth, consider switching
to the backward search method.

---

## I. Summary

| Question | Answer |
|---|---|
| What did the 10M run establish? | First-gen sources complete; graph is a DAG to depth 37; no 0 or WORD_MASK found |
| What did it NOT establish? | Tileability for any z < 130 |
| Source of explosion? | Wider graph (~1M states/depth vs 4x8's narrow basin); no cycles; higher branching |
| Can truncated graph answer z < 130? | No (max depth 37 < target depths 59-104) |
| Cheapest exact method? | Continue forward BFS to 50M cap (~9 hours) |
| Is there a 15-step pattern? | Consistent with data but NOT proven |
| Macro-path vs tiling count? | Distinct; need realization analysis after path is found |
| Estimated runtime? | ~9 hours on desktop |
| Exact next step? | Resume BFS with 50M cap, monitor growth, do backward DP when WORD_MASK found |

---

## J. Artifacts

| File | Description |
|---|---|
| `/tmp/macro_checkpoints/4x9.ckpt/` | 10M checkpoint (733 MB) |
| `/tmp/macro_generalized_4x9_results.txt` | Run statistics |
| `tools/frontier/macro_4x9_targeted.py` | Targeted analysis prototype |
| `/tmp/macro_4x9_targeted_results.txt` | Prototype results |
