# 4×8×140 Macro Tiling Construction

## Summary

**Result**: 4×8×140 is explicitly tileable by S-pentacubes.

**Construction**: The tiling was constructed by repeating the known 20-cycle Macro path 7 times.

**Validation**: All 4,480 cells are covered exactly once by 896 S-pentacube placements.

## Macro Path Construction

### Path Length

- Physical box: 4×8×140
- Macro path length: 140 edges (141 states)
- Relationship: z = (number of edges) = 140

### Cycle Structure

The path consists of 7 repetitions of the 20-cycle:

```
20-cycle: 0 → s* → c₂ → c₃ → ... → c₁₉ → WORD_MASK → 0
```

Where:
- `0` is the empty state
- `s* = 6163195513375031274` is the first-generation source
- `c₂` through `c₁₉` are intermediate Macro states
- `WORD_MASK = 4294967295` is the full-layer state

### Path Verification

All 140 edges were verified to exist in the 478-state SCC:
- Edge 0: 0 → s* ✓
- Edges 1-18: s* → c₂ → ... → c₁₉ ✓
- Edge 19: WORD_MASK → 0 ✓
- Pattern repeats 7 times ✓

## Tiling Reconstruction

### Placement Sequences

Each of the 20 Macro edges was reconstructed via BFS to find the concrete S-pentacube placements:

| Edge | Placements | Description |
|------|------------|-------------|
| 0 | 14 | First generation (0 → s*) |
| 1 | 4 | s* → c₂ |
| 2 | 4 | c₂ → c₃ |
| 3 | 8 | c₃ → c₄ |
| 4 | 8 | c₄ → c₅ |
| 5 | 6 | c₅ → c₆ |
| 6 | 4 | c₆ → c₇ |
| 7 | 6 | c₇ → c₈ |
| 8 | 8 | c₈ → c₉ |
| 9 | 6 | c₉ → c₁₀ |
| 10 | 8 | c₁₀ → c₁₁ |
| 11 | 6 | c₁₁ → c₁₂ |
| 12 | 6 | c₁₂ → c₁₃ |
| 13 | 6 | c₁₃ → c₁₄ |
| 14 | 8 | c₁₄ → c₁₅ |
| 15 | 4 | c₁₅ → c₁₆ |
| 16 | 6 | c₁₆ → c₁₇ |
| 17 | 8 | c₁₇ → c₁₈ |
| 18 | 8 | c₁₈ → WORD_MASK |
| 19 | 0 | WORD_MASK → 0 (immediate shift) |

**Total per cycle**: 128 placements

**Total for 7 cycles**: 896 placements

### Cell Coverage

- Total cells: 4,480
- Expected: 4 × 8 × 140 = 4,480 ✓
- All cells unique: ✓
- All cells within bounds: ✓
  - X: 0 to 3
  - Y: 0 to 7
  - Z: 0 to 139

## Validation Results

### Structural Validation

✓ All 4,480 cells covered exactly once
✓ All 896 placements are valid S-pentacube placements
✓ All cells within 4×8×140 bounds
✓ No overlaps or gaps

### Mathematical Validation

✓ Cell count: 896 × 5 = 4,480 = 4 × 8 × 140
✓ Divisibility: 4,480 / 5 = 896 (integer)
✓ z = 140 ≡ 0 (mod 10) ✓

## Connection to Infinite Family Theorem

This construction validates the sufficiency direction of the infinite family theorem:

**Theorem** (proved): For all z ≡ 0 (mod 10) with z ≥ 120, the 4×8×z box is tileable.

**Proof method**: 
- The 20-cycle and 130-cycle exist in the SCC
- GCD(20, 130) = 10
- By the Chicken McNugget theorem, all multiples of 10 ≥ 120 can be expressed as 20a + 130b
- For z = 140: 140 = 20 × 7 + 130 × 0
- Therefore, 7 repetitions of the 20-cycle gives a valid tiling

**This construction**: Explicitly demonstrates the theorem for z = 140.

## Files

- `macro_path_140.npy`: The 141-state Macro path (NumPy array)
- `solution_s_4x8x140_macro.dat`: The complete tiling (4,480 cell coordinates)

## Construction Method

1. Loaded the 478-state SCC from the 30M closure
2. Verified the 20-cycle edges exist in the SCC
3. Constructed a 140-edge path by repeating the 20-cycle 7 times
4. Reconstructed placement sequences for each of the 20 unique edges via BFS
5. Replicated the placement sequences 7 times with appropriate z-offsets
6. Converted placements to cell coordinates
7. Validated complete coverage and correctness

## Computational Cost

- Path construction: < 1 second
- Placement reconstruction (20 edges): ~30 seconds
- Tiling assembly and validation: < 1 second
- **Total**: ~30 seconds

No large-scale search was required. The construction used only the existing SCC data and the known 20-cycle structure.

## Conclusion

**4×8×140 is explicitly tileable.**

This validates the infinite family prediction at the first new length beyond 130, confirming that the period-10 structure extends beyond the originally analyzed range.
