# Z-Frontier: Sealed-Layer Invariant

Solver: `solvers/s_z_frontier_packed.py` (S pentacube, 4x8 box).
Placement generation: `common/polycube_utils.py::generate_placements`.

## Conclusion

**SAFE**

When layer 0 is full, the solver shifts the state by one z-layer and
the old layer 0 is discarded. No placement template accepted by the
solver can reach into that discarded layer from any future state.

## The invariant, restated

1. When layer 0 is full, the solver shifts the state by one z-layer.
2. After the shift, the old layer 0 is no longer stored.
3. No placement template accepted by the solver can reach into that
   discarded layer from a future state.

## Exact code logic

### State model (lines 5-11, 50-54)

```
State:
    one Python integer containing four 32-bit z-layer masks.
    bits   0..31   = layer 0
    bits  32..63   = layer 1
    bits  64..95   = layer 2
    bits  96..127  = layer 3
```

`NCELLS = 32`, `WORD_MASK = (1 << 32) - 1`.

### Shift discards layer 0 (lines 185-186, 238-242)

```
def shift_state(state: int) -> int:
    return state >> NCELLS
```

In `discover`:

```
current = layer_mask(state, 0)
if current == WORD_MASK:
    nxt = shift_state(state)
```

`state >> 32` moves old layer 1 into bits 0-31, old layer 2 into
bits 32-63, old layer 3 into bits 64-95, and leaves bits 96-127
empty. Old layer 0 (bits 0-31) is shifted out of the integer and is
no longer stored anywhere. The new layer 0 sits one z-level above the
discarded layer.

### Templates never contain cells below layer 0 (lines 98-130)

```
def make_shifted_template(placement_cells, target_z):
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel        # == z - target_z
        if rel < 0 or rel >= LAYERS:
            return None
        shifted_masks[rel] |= 1 << cell_id(x, y)
    return pack_layers(shifted_masks)
```

For the target cell, `rel = 0`: the template is anchored with the
target at layer 0. Every other cell must satisfy `0 <= rel < 4`
(layers 0-3); any placement cell with `rel < 0` (i.e. below the
target's z) causes the template to be rejected (`return None`).
Therefore every accepted template occupies only layers 0-3 of the
128-bit pattern, never below layer 0.

### Application only ORs into layers 0-3 of the current state (lines 175-182)

```
def apply_template(state: int, template: int) -> int | None:
    if state & template:
        return None
    return state | template
```

The template's layer-k bits land in the state's layer k. Since the
template has no bits below layer 0, a placement never writes below
the current state's layer 0.

### Templates are anchored at a layer-0 cell (lines 266-271)

```
target = first_empty(current)
for template in templates[target]:
    nxt = apply_template(state, template)
```

Templates are only ever applied for `target = first_empty(current)`,
a cell of the current layer 0, and only when layer 0 is not full
(the full case shifts instead).

## Why the discarded layer is unreachable

- The discarded layer is the old layer 0, which after the shift lies
  strictly below the new layer 0 (it was shifted out by
  `state >> NCELLS`).
- Every accepted template places all of its cells at
  `z >= (current layer 0's z)`: the anchor cell is at layer 0 and all
  other cells have `rel >= 0` (enforced by `make_shifted_template`).
- `apply_template` writes only into layers 0-3 of the current state,
  i.e. only at `z >= (current layer 0's z)`.
- Hence no future placement can occupy the discarded layer's z; the
  sealed layer can never be touched again. The same argument applies
  to any layer discarded by a later shift.

## Scope note

Only the sealed-layer invariant was investigated, as requested. No
other frontier optimizations were examined.