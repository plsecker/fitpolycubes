# 4x9 S-Pentacube Return Search

Date: 2026-08-22
Status: **NO RETURN TO STATE 0 FOUND THROUGH DEPTH 51**

## Search Summary

A targeted BFS search for the first return to state 0 in the 4x9 Macro
graph was conducted, reaching:

- **65,062,809 states** discovered (of 70M cap)
- **65,447,160 macro edges** recorded
- **Max depth**: 51
- **State 0**: NOT found
- **Queue**: 8,418,547 states pending
- **Total intermediate states**: 1,834,763,917
- **Elapsed**: ~95 minutes total (67 min initial + 28 min resumed)

## Checkpoint History

| Step | States | Depth | Notes |
|---|---|---|---|
| Initial 10M run (lost) | 10,000,036 | 37 | JSON checkpoint lost from /tmp |
| Fresh start (Phase 2) | 41,514,340 | 48 | JSON → pickle conversion |
| Verified binary | 41,514,340 | 48 | All checks passed |
| Resumed to 50M | 50,000,473 | 49 | Hit 50M cap |
| Resumed to 70M | 65,062,809 | 51 | Timed out at ~28 min |

## Depth Distribution (Final)

| Depth | States | Growth |
|---|---|---|
| 35 | 949,263 | — |
| 36 | 1,211,380 | +28% |
| 37 | 1,559,672 | +29% |
| 38 | 1,479,008 | -5% |
| 39 | 1,744,788 | +18% |
| 40 | 1,757,076 | +1% |
| 41 | 2,324,420 | +32% |
| 42 | 2,763,810 | +19% |
| 43 | 3,472,688 | +26% |
| 44 | 3,719,104 | +7% |
| 45 | 4,063,937 | +9% |
| 46 | 4,489,394 | +10% |
| 47 | 4,515,478 | +1% |
| 48 | 5,167,324 | +14% |
| 49 | 6,408,382 | +24% |
| 50 | 8,112,062 | +27% |
| 51 | ~3,200,000 | (in progress) |

The graph does not contract — it continues widening at ~8M states per
depth at depths 49-51.

## Comparison with 4x8

| Property | 4x8 | 4x9 |
|---|---|---|
| States explored | 30,000,015 | 65,062,809 |
| Max depth | 85 | 51 |
| State 0 found | Yes (at depth 19) | **No** |
| Cycles found | Yes (20, 130) | **None** |
| Recurrent SCC | 478 states | **None** |
| Graph type | DAG + recurrent SCC | **Pure DAG** |
| Return existence | Proved | **Not found** |

## Interpretation

The 4x9 Macro graph is a **widening DAG** with no detected cycles through
depth 51. The graph grows at ~1-8M states per depth, and there is no
evidence of contraction. State 0 and WORD_MASK are absent from all
explored depths.

**No return to state 0 was found within the explored state space.**

This does NOT prove 4x9xz is impossible. It only establishes that no
return path exists through depth 51 in the explored 65M-state subgraph.

## Growth Projection

To reach depth 60 would require processing approximately:
- Depths 52-60: ~10-15M states each × 9 depths ≈ 90-135M additional states
- Total: ~150-200M states
- Estimated time: 2-4 additional hours at current rate

## Recommendation

Do NOT continue the BFS to 200M states without a new structural insight.
The 4x9 graph is simply too wide for this approach.

## Key Checkpoints

| File | Size | Content |
|---|---|---|
| `/tmp/macro_4x9_binary.ckpt/` | ~2 GB | Final binary checkpoint (65M states) |
| `/home/.../4x9_live_backup/` | 3.1 GB | Live JSON backup |
| `/home/.../4x9_checkpoint_backup/` | 2.4 GB | Earlier backup |