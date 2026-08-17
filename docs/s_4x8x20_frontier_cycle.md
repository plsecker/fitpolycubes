# S 4x8x20: The 20-Layer Frontier Cycle 0 → … → 0

Run: standalone reconstruction script (`/tmp/opencode/extract_20layer_path.py`,
results in `/tmp/opencode/s_4x8x20_frontier_cycle_results.txt`).

This document extracts and verifies the complete 20-layer path
`0 -> source -> … -> 0` described in
`docs/s_z_frontier_length_analysis.md` (the N = 20 chain: 0, 14 first-gen
placements, pre-shift `p0`, source, then 19 macro edges back to 0).  It
reports every post-shift frontier state in order, the macro transition of
each pair, the S placements of every layer, the totals, and the final-state
confirmation.

Constraints honored:

* `solvers/s_z_frontier_packed.py` is **not modified**; its pure functions
  (`build_templates`, `apply_template`, `first_empty`, `layer_mask`,
  `shift_state`, `WORD_MASK`) are reused with identical semantics.
* **No new exhaustive search** was run.  Each segment is reconstructed by a
  targeted BFS confined to its own layer's placement interval (a few tens of
  thousands of states per layer), then verified by full simulation.
* Nothing is inferred about N = 40, 60, 80 or a general period; no new
  algorithm is proposed.

## State model (recap)

A state is one integer with three 32-bit layer masks: bits 0–31 = layer 0,
bits 32–63 = layer 1, bits 64–95 = layer 2.  Bit `x + 4y` of a mask is cell
(x, y), x ∈ [0, 4), y ∈ [0, 8).  A state is pre-shift iff layer 0 ==
`WORD_MASK` (0xffffffff); `shift_state(s) = s >> 32`.  A macro edge
`u -> v` is: apply S placements at `first_empty(layer0(u))` until layer 0 is
full (pre-shift state `p`), then shift: `v = p >> 32`.  For a given
pre-shift state the placement sequence is deterministic (first-empty cell +
template order), so the placements reported below are exactly the ones the
solver's transition uses.

## Method

* **First-generation segment** `0 -> p0 -> source`: targeted BFS from 0
  over states whose layer-0 mask is not yet full, stopping at the unique
  pre-shift state `p0 = 0x558811aa57ffffeaffffffff` (L0 full, L1 =
  0x57ffffea, L2 = 0x558811aa) with `p0 >> 32 == source`.  The BFS is
  restricted to the first layer's interval (~40K states), not the whole
  state space.
* **Macro edges** `u -> v`: for each consecutive pair from the N = 20 chain
  of `docs/s_z_frontier_length_analysis.md`, reconstruct the unique
  pre-shift state `p = WORD_MASK | (L0(v) << 32) | (L1(v) << 64)` by the
  same targeted BFS from `u`, then verify `p >> 32 == v`.
* **Verification**: every segment is re-simulated placement by placement
  (`apply_template` must never return None), and the full chain
  `0 -> ... -> 0` is simulated end to end; the final state must be exactly
  0.  All checks passed.

## The cycle at a glance

The path is a closed walk of 20 layers in the **true** macro graph:
`0 -> source -> … -> WORD_MASK -> 0` (0's macro successors are exactly the
first-generation sources, so the first segment is itself a macro edge).
The 20 post-shift states, in order:

| step | post-shift state | L0 | L1 | L2 |
|---|---|---|---|---|
| 0 | 6163195513375031274 | 0x57ffffea | 0x558811aa | 0x00000000 |
| 1 | 13835058072323104239 | 0xf7b81def | 0xc0000003 | 0x00000000 |
| 2 | 3993075831 | 0xee018077 | 0x00000000 | 0x00000000 |
| 3 | 55840897340952456 | 0x11f24f88 | 0x00c66300 | 0x00000000 |
| 4 | 9838132153049676753 | 0x8bdffbd1 | 0x88881111 | 0x00000000 |
| 5 | 2089671021646321023 | 0xfea8157f | 0x1d0000b8 | 0x00000000 |
| 6 | 13523993509333176 | 0x1d1188b8 | 0x00300c00 | 0x00000000 |
| 7 | 54046496222498049 | 0x80b24d01 | 0x00c00300 | 0x00000000 |
| 8 | 3430478137537398 | 0x6ecc3376 | 0x000c3000 | 0x00000000 |
| 9 | 2691607028413209 | 0x98cdb319 | 0x00099000 | 0x00000000 |
| 10 | 4934612199136503 | 0xef3bdcf7 | 0x00118800 | 0x00000000 |
| 11 | 612490719515897646 | 0x74f7ef2e | 0x08800110 | 0x00000000 |
| 12 | 16285016559841080657 | 0x8aae7551 | 0xe2000047 | 0x00000000 |
| 13 | 217229141722890951 | 0xe34182c7 | 0x0303c0c0 | 0x00000000 |
| 14 | 6729013160573166 | 0x771ff8ee | 0x0017e800 | 0x00000000 |
| 15 | 2297949969 | 0x88f7ef11 | 0x00000000 | 0x00000000 |
| 16 | 1224979683048584328 | 0x112e7488 | 0x11000088 | 0x00000000 |
| 17 | 17294878168733286543 | 0xf101808f | 0xf003c00f | 0x00000000 |
| 18 | 4294967295 | 0xffffffff | 0x00000000 | 0x00000000 |
| 19 | 0 | 0x00000000 | 0x00000000 | 0x00000000 |

Every post-shift state has L2 = 0 (the window never carries a third layer
along this path).  The final edge is an immediate shift from `WORD_MASK`
(L0 full, L1 = L2 = 0) to 0.

## Layer-by-layer placements

Cells are (x, y, z) with z relative to the frontier layer 0 of the
pre-shift state; the anchor is the first-empty cell of layer 0.

### Layer 1 (first generation): 0 → [14 placements] → p0 → source

`p0 = 0x558811aa57ffffeaffffffff` (L0 = 0xffffffff, L1 = 0x57ffffea,
L2 = 0x558811aa); `p0 >> 32 == source` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (1,0,0) (1,0,1) (1,0,2) (1,1,2) |
| 2 | (2,0) | (2,0,0) (3,0,0) (3,0,1) (3,0,2) (3,1,2) |
| 3 | (0,1) | (0,1,0) (0,2,0) (1,2,0) (2,2,0) (2,2,1) |
| 4 | (1,1) | (1,1,0) (2,1,0) (3,1,0) (3,2,0) (1,1,1) |
| 5 | (0,3) | (0,3,0) (1,3,0) (0,3,1) (0,2,2) (0,3,2) |
| 6 | (2,3) | (2,3,0) (2,3,1) (2,4,1) (2,5,1) (3,5,1) |
| 7 | (3,3) | (3,3,0) (2,1,1) (3,1,1) (3,2,1) (3,3,1) |
| 8 | (0,4) | (0,4,0) (0,4,1) (0,5,1) (0,6,1) (1,6,1) |
| 9 | (1,4) | (1,4,0) (0,2,1) (1,2,1) (1,3,1) (1,4,1) |
| 10 | (2,4) | (2,4,0) (3,4,0) (3,4,1) (3,4,2) (3,5,2) |
| 11 | (0,5) | (0,5,0) (0,6,0) (1,6,0) (2,6,0) (2,6,1) |
| 12 | (1,5) | (1,5,0) (2,5,0) (3,5,0) (3,6,0) (1,5,1) |
| 13 | (0,7) | (0,7,0) (1,7,0) (0,7,1) (0,6,2) (0,7,2) |
| 14 | (2,7) | (2,7,0) (3,7,0) (2,7,1) (2,6,2) (2,7,2) |

### Layer 2: 6163195513375031274 → [4] → p → 13835058072323104239

`p = 0xc0000003f7b81defffffffff` (L0 = 0xffffffff, L1 = 0xf7b81def,
L2 = 0xc0000003); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (0,1,0) (0,0,1) (0,0,2) (1,0,2) |
| 2 | (2,0) | (2,0,0) (2,0,1) (2,1,1) (2,2,1) (3,2,1) |
| 3 | (3,6) | (3,6,0) (3,7,0) (3,7,1) (2,7,2) (3,7,2) |
| 4 | (1,7) | (1,7,0) (0,5,1) (1,5,1) (1,6,1) (1,7,1) |

### Layer 3: 13835058072323104239 → [4] → p → 3993075831

`p = 0xee018077ffffffff` (L0 = 0xffffffff, L1 = 0xee018077, L2 = 0x0);
`p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,1) | (0,1,0) (2,0,1) (0,1,1) (1,1,1) (2,1,1) |
| 2 | (1,2) | (1,2,0) (1,3,0) (2,3,0) (3,3,0) (3,3,1) |
| 3 | (0,4) | (0,4,0) (1,4,0) (2,4,0) (2,5,0) (0,4,1) |
| 4 | (3,6) | (3,6,0) (1,6,1) (2,6,1) (3,6,1) (1,7,1) |

### Layer 4: 3993075831 → [8] → p → 55840897340952456

`p = 0xc6630011f24f88ffffffff` (L0 = 0xffffffff, L1 = 0x11f24f88,
L2 = 0x00c66300); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (3,0) | (3,0,0) (3,1,0) (2,2,0) (3,2,0) (3,0,1) |
| 2 | (0,2) | (0,2,0) (0,3,0) (0,2,1) (0,2,2) (1,2,2) |
| 3 | (1,2) | (1,2,0) (3,1,1) (1,2,1) (2,2,1) (3,2,1) |
| 4 | (1,3) | (1,3,0) (2,3,0) (2,3,1) (2,3,2) (2,4,2) |
| 5 | (1,4) | (1,4,0) (2,4,0) (1,4,1) (1,3,2) (1,4,2) |
| 6 | (3,4) | (3,4,0) (3,5,0) (3,5,1) (2,5,2) (3,5,2) |
| 7 | (0,5) | (0,5,0) (1,5,0) (0,6,0) (0,7,0) (0,7,1) |
| 8 | (2,5) | (2,5,0) (0,5,1) (1,5,1) (2,5,1) (0,6,1) |

### Layer 5: 55840897340952456 → [8] → p → 9838132153049676753

`p = 0x888811118bdffbd1ffffffff` (L0 = 0xffffffff, L1 = 0x8bdffbd1,
L2 = 0x88881111); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (1,0,0) (2,0,0) (2,1,0) (0,0,1) |
| 2 | (0,1) | (0,1,0) (1,1,0) (0,1,1) (0,0,2) (0,1,2) |
| 3 | (0,3) | (0,3,0) (1,3,0) (0,3,1) (0,2,2) (0,3,2) |
| 4 | (3,3) | (3,3,0) (2,1,1) (3,1,1) (3,2,1) (3,3,1) |
| 5 | (0,4) | (0,4,0) (0,4,1) (0,5,1) (0,6,1) (1,6,1) |
| 6 | (2,4) | (2,4,0) (3,4,0) (3,4,1) (3,4,2) (3,5,2) |
| 7 | (1,6) | (1,6,0) (1,7,0) (2,7,0) (3,7,0) (3,7,1) |
| 8 | (2,6) | (2,6,0) (3,6,0) (3,6,1) (3,6,2) (3,7,2) |

### Layer 6: 9838132153049676753 → [6] → p → 2089671021646321023

`p = 0x1d0000b8fea8157fffffffff` (L0 = 0xffffffff, L1 = 0xfea8157f,
L2 = 0x1d0000b8); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (1,0) | (1,0,0) (1,1,0) (1,1,1) (0,1,2) (1,1,2) |
| 2 | (2,0) | (2,0,0) (3,0,0) (3,0,1) (3,0,2) (3,1,2) |
| 3 | (2,2) | (2,2,0) (1,0,1) (2,0,1) (2,1,1) (2,2,1) |
| 4 | (1,5) | (1,5,0) (1,5,1) (1,6,1) (1,7,1) (2,7,1) |
| 5 | (2,6) | (2,6,0) (2,7,0) (2,6,1) (2,6,2) (3,6,2) |
| 6 | (0,7) | (0,7,0) (1,7,0) (0,7,1) (0,6,2) (0,7,2) |

### Layer 7: 2089671021646321023 → [4] → p → 13523993509333176

`p = 0x300c001d1188b8ffffffff` (L0 = 0xffffffff, L1 = 0x1d1188b8,
L2 = 0x00300c00); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (3,1) | (3,1,0) (3,2,0) (3,2,1) (2,2,2) (3,2,2) |
| 2 | (1,2) | (1,2,0) (1,3,0) (2,3,0) (3,3,0) (3,3,1) |
| 3 | (0,4) | (0,4,0) (1,4,0) (2,4,0) (2,5,0) (0,4,1) |
| 4 | (0,5) | (0,5,0) (0,6,0) (0,5,1) (0,5,2) (1,5,2) |

### Layer 8: 13523993509333176 → [6] → p → 54046496222498049

`p = 0xc0030080b24d01ffffffff` (L0 = 0xffffffff, L1 = 0x80b24d01,
L2 = 0x00c00300); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (1,0,0) (2,0,0) (2,1,0) (0,0,1) |
| 2 | (0,2) | (0,2,0) (0,3,0) (0,2,1) (0,2,2) (1,2,2) |
| 3 | (1,2) | (1,2,0) (2,2,0) (1,3,0) (1,4,0) (1,4,1) |
| 4 | (2,3) | (2,3,0) (2,4,0) (1,5,0) (2,5,0) (2,3,1) |
| 5 | (3,4) | (3,4,0) (3,5,0) (3,5,1) (2,5,2) (3,5,2) |
| 6 | (1,6) | (1,6,0) (1,7,0) (2,7,0) (3,7,0) (3,7,1) |

### Layer 9: 54046496222498049 → [8] → p → 3430478137537398

`p = 0xc30006ecc3376ffffffff` (L0 = 0xffffffff, L1 = 0x6ecc3376,
L2 = 0x000c3000); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (1,0) | (1,0,0) (2,0,0) (3,0,0) (3,1,0) (1,0,1) |
| 2 | (0,1) | (0,1,0) (2,0,1) (0,1,1) (1,1,1) (2,1,1) |
| 3 | (1,1) | (1,1,0) (2,1,0) (1,2,0) (1,3,0) (1,3,1) |
| 4 | (0,3) | (0,3,0) (0,4,0) (0,3,1) (0,3,2) (1,3,2) |
| 5 | (3,3) | (3,3,0) (3,4,0) (3,4,1) (2,4,2) (3,4,2) |
| 6 | (2,4) | (2,4,0) (2,5,0) (1,6,0) (2,6,0) (2,4,1) |
| 7 | (0,6) | (0,6,0) (0,7,0) (1,7,0) (2,7,0) (2,7,1) |
| 8 | (3,6) | (3,6,0) (1,6,1) (2,6,1) (3,6,1) (1,7,1) |

### Layer 10: 3430478137537398 → [6] → p → 2691607028413209

`p = 0x9900098cdb319ffffffff` (L0 = 0xffffffff, L1 = 0x98cdb319,
L2 = 0x00099000); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (0,0,1) (0,1,1) (0,2,1) (1,2,1) |
| 2 | (3,0) | (3,0,0) (3,1,0) (2,2,0) (3,2,0) (3,0,1) |
| 3 | (2,3) | (2,3,0) (3,3,0) (3,3,1) (3,3,2) (3,4,2) |
| 4 | (0,4) | (0,4,0) (1,4,0) (0,4,1) (0,3,2) (0,4,2) |
| 5 | (0,5) | (0,5,0) (1,5,0) (0,6,0) (0,7,0) (0,7,1) |
| 6 | (3,7) | (3,7,0) (2,5,1) (3,5,1) (3,6,1) (3,7,1) |

### Layer 11: 2691607028413209 → [8] → p → 4934612199136503

`p = 0x118800ef3bdcf7ffffffff` (L0 = 0xffffffff, L1 = 0xef3bdcf7,
L2 = 0x00118800); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (1,0) | (1,0,0) (1,1,0) (2,1,0) (3,1,0) (3,1,1) |
| 2 | (2,0) | (2,0,0) (0,0,1) (1,0,1) (2,0,1) (0,1,1) |
| 3 | (2,2) | (2,2,0) (3,2,0) (3,2,1) (3,2,2) (3,3,2) |
| 4 | (2,3) | (2,3,0) (1,1,1) (2,1,1) (2,2,1) (2,3,1) |
| 5 | (1,4) | (1,4,0) (1,4,1) (1,5,1) (1,6,1) (2,6,1) |
| 6 | (0,5) | (0,5,0) (1,5,0) (0,5,1) (0,4,2) (0,5,2) |
| 7 | (0,6) | (0,6,0) (1,6,0) (2,6,0) (2,7,0) (0,6,1) |
| 8 | (1,7) | (1,7,0) (3,6,1) (1,7,1) (2,7,1) (3,7,1) |

### Layer 12: 4934612199136503 → [6] → p → 612490719515897646

`p = 0x880011074f7ef2effffffff` (L0 = 0xffffffff, L1 = 0x74f7ef2e,
L2 = 0x08800110); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (3,0) | (3,0,0) (1,0,1) (2,0,1) (3,0,1) (1,1,1) |
| 2 | (0,2) | (0,2,0) (1,2,0) (0,2,1) (0,1,2) (0,2,2) |
| 3 | (1,3) | (1,3,0) (1,3,1) (1,4,1) (1,5,1) (2,5,1) |
| 4 | (2,4) | (2,4,0) (1,2,1) (2,2,1) (2,3,1) (2,4,1) |
| 5 | (2,5) | (2,5,0) (3,5,0) (3,5,1) (3,5,2) (3,6,2) |
| 6 | (0,7) | (0,7,0) (2,6,1) (0,7,1) (1,7,1) (2,7,1) |

### Layer 13: 612490719515897646 → [6] → p → 16285016559841080657

`p = 0xe20000478aae7551ffffffff` (L0 = 0xffffffff, L1 = 0x8aae7551,
L2 = 0xe2000047); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (0,1,0) (0,0,1) (0,0,2) (1,0,2) |
| 2 | (2,1) | (2,1,0) (3,1,0) (2,1,1) (2,0,2) (2,1,2) |
| 3 | (0,3) | (0,3,0) (2,2,1) (0,3,1) (1,3,1) (2,3,1) |
| 4 | (3,4) | (3,4,0) (1,4,1) (2,4,1) (3,4,1) (1,5,1) |
| 5 | (0,6) | (0,6,0) (1,6,0) (1,6,1) (1,6,2) (1,7,2) |
| 6 | (3,6) | (3,6,0) (3,7,0) (3,7,1) (2,7,2) (3,7,2) |

### Layer 14: 16285016559841080657 → [6] → p → 217229141722890951

`p = 0x303c0c0e34182c7ffffffff` (L0 = 0xffffffff, L1 = 0xe34182c7,
L2 = 0x0303c0c0); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (1,0) | (1,0,0) (2,0,0) (1,1,0) (1,2,0) (1,2,1) |
| 2 | (3,0) | (3,0,0) (3,1,0) (3,1,1) (2,1,2) (3,1,2) |
| 3 | (3,2) | (3,2,0) (3,3,0) (3,3,1) (2,3,2) (3,3,2) |
| 4 | (0,4) | (0,4,0) (0,5,0) (0,4,1) (0,4,2) (1,4,2) |
| 5 | (2,5) | (2,5,0) (2,6,0) (1,7,0) (2,7,0) (2,5,1) |
| 6 | (0,6) | (0,6,0) (0,7,0) (0,6,1) (0,6,2) (1,6,2) |

### Layer 15: 217229141722890951 → [8] → p → 6729013160573166

`p = 0x17e800771ff8eeffffffff` (L0 = 0xffffffff, L1 = 0x771ff8ee,
L2 = 0x0017e800); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (3,0) | (3,0,0) (1,0,1) (2,0,1) (3,0,1) (1,1,1) |
| 2 | (0,1) | (0,1,0) (1,1,0) (0,2,0) (0,3,0) (0,3,1) |
| 3 | (2,2) | (2,2,0) (3,2,0) (3,2,1) (3,2,2) (3,3,2) |
| 4 | (1,3) | (1,3,0) (1,4,0) (1,3,1) (1,3,2) (2,3,2) |
| 5 | (2,3) | (2,3,0) (2,4,0) (2,4,1) (1,4,2) (2,4,2) |
| 6 | (3,4) | (3,4,0) (3,5,0) (2,6,0) (3,6,0) (3,4,1) |
| 7 | (0,5) | (0,5,0) (1,5,0) (0,5,1) (0,4,2) (0,5,2) |
| 8 | (0,7) | (0,7,0) (2,6,1) (0,7,1) (1,7,1) (2,7,1) |

### Layer 16: 6729013160573166 → [4] → p → 2297949969

`p = 0x88f7ef11ffffffff` (L0 = 0xffffffff, L1 = 0x88f7ef11, L2 = 0x0);
`p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (0,0,1) (0,1,1) (0,2,1) (1,2,1) |
| 2 | (0,1) | (0,1,0) (0,2,0) (1,2,0) (2,2,0) (2,2,1) |
| 3 | (1,5) | (1,5,0) (2,5,0) (3,5,0) (3,6,0) (1,5,1) |
| 4 | (3,7) | (3,7,0) (2,5,1) (3,5,1) (3,6,1) (3,7,1) |

### Layer 17: 2297949969 → [6] → p → 1224979683048584328

`p = 0x11000088112e7488ffffffff` (L0 = 0xffffffff, L1 = 0x112e7488,
L2 = 0x11000088); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (1,0) | (1,0,0) (1,1,0) (2,1,0) (3,1,0) (3,1,1) |
| 2 | (2,0) | (2,0,0) (3,0,0) (3,0,1) (3,0,2) (3,1,2) |
| 3 | (0,3) | (0,3,0) (2,2,1) (0,3,1) (1,3,1) (2,3,1) |
| 4 | (3,4) | (3,4,0) (1,4,1) (2,4,1) (3,4,1) (1,5,1) |
| 5 | (0,6) | (0,6,0) (1,6,0) (2,6,0) (2,7,0) (0,6,1) |
| 6 | (0,7) | (0,7,0) (1,7,0) (0,7,1) (0,6,2) (0,7,2) |

### Layer 18: 1224979683048584328 → [8] → p → 17294878168733286543

`p = 0xf003c00ff101808fffffffff` (L0 = 0xffffffff, L1 = 0xf101808f,
L2 = 0xf003c00f); `p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,0) | (0,0,0) (0,1,0) (0,0,1) (0,0,2) (1,0,2) |
| 2 | (1,0) | (1,0,0) (1,1,0) (0,2,0) (1,2,0) (1,0,1) |
| 3 | (2,0) | (2,0,0) (2,1,0) (2,0,1) (2,0,2) (3,0,2) |
| 4 | (3,2) | (3,2,0) (3,3,0) (3,3,1) (2,3,2) (3,3,2) |
| 5 | (0,4) | (0,4,0) (0,5,0) (0,4,1) (0,4,2) (1,4,2) |
| 6 | (2,5) | (2,5,0) (3,5,0) (2,6,0) (2,7,0) (2,7,1) |
| 7 | (1,6) | (1,6,0) (1,7,0) (1,7,1) (0,7,2) (1,7,2) |
| 8 | (3,6) | (3,6,0) (3,7,0) (3,7,1) (2,7,2) (3,7,2) |

### Layer 19: 17294878168733286543 → [8] → p → 4294967295

`p = 0xffffffffffffffff` (L0 = 0xffffffff, L1 = 0xffffffff, L2 = 0x0);
`p >> 32 == v` ✓

| # | anchor | cells |
|---|---|---|
| 1 | (0,1) | (0,1,0) (1,1,0) (0,2,0) (0,3,0) (0,3,1) |
| 2 | (2,1) | (2,1,0) (0,1,1) (1,1,1) (2,1,1) (0,2,1) |
| 3 | (1,2) | (1,2,0) (3,1,1) (1,2,1) (2,2,1) (3,2,1) |
| 4 | (2,2) | (2,2,0) (3,2,0) (2,3,0) (2,4,0) (2,4,1) |
| 5 | (1,3) | (1,3,0) (1,4,0) (0,5,0) (1,5,0) (1,3,1) |
| 6 | (3,4) | (3,4,0) (3,5,0) (2,6,0) (3,6,0) (3,4,1) |
| 7 | (2,5) | (2,5,0) (0,5,1) (1,5,1) (2,5,1) (0,6,1) |
| 8 | (1,6) | (1,6,0) (3,5,1) (1,6,1) (2,6,1) (3,6,1) |

### Layer 20: 4294967295 → [0 placements] → p → 0

`p = 0xffffffff` (L0 = 0xffffffff, L1 = L2 = 0x0); `p >> 32 == v` ✓.
This is an **immediate shift**: layer 0 is already full and layers 1–2 are
empty, so no placement is needed; `WORD_MASK >> 32 == 0`.

## Totals

| Metric | Value |
|---|---|
| Total S placements | **128** |
| Layer 1 (first generation) | 14 |
| Layers 2–20 (macro edges) | 114 |
| Total layers completed | **20** |
| Final state | **0** |

Cell-count check: 128 placements × 5 cells = 640 = 32 × 20 ✓.

## Final-state confirmation

The chain `0 -> … -> 0` was re-simulated end to end with the solver's own
`apply_template`/`shift_state` semantics: every placement applied without
overlap, every pre-shift state satisfies `p >> 32 == v`, and the final
state is **exactly 0** (`ALL CHECKS PASSED: True`).

## Caveat: capped-closure visibility

The 20-edge cycle `0 -> source -> … -> WORD_MASK -> 0` exists in the
**true** macro graph (0's macro successors are exactly the first-generation
sources, and the chain above returns to 0 in 19 further edges).  It is
**not** visible in the capped closure of
`docs/s_z_frontier_macro_reachability.md` (15,000,991 states): `succ[0]` is
truncated by the per-source intermediate cap (1,000,000 states; 0's
interval has 3,162,387), so the closure contains no edge out of 0 and
`R(0) = [0]` there.  This document therefore makes **no claim of
closure-cycle membership**; it reports the reconstructed path from the
N = 20 chain of `docs/s_z_frontier_length_analysis.md` (0 → 14 placements →
`p0` → 19 macro edges → 0), verified by targeted reconstruction and full
simulation.

## Verification summary

* First-generation segment `0 -> p0 -> source`: ✓
* Macro edges 2–20 (`u -> placements -> p -> v`, `p >> 32 == v`): ✓ (19/19)
* Final state == 0: ✓
* Full simulation `0 -> ... -> 0` returns exactly 0: ✓
* All checks passed: **True**