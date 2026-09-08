#!/usr/bin/env python3
"""Quick Macro feasibility assessment for T in 3×15×17."""

import sys, time
from collections import deque
sys.path.insert(0, '.')
from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE, Y_SIZE = 3, 15
NCELLS = X_SIZE * Y_SIZE  # 45
LAYERS = 3
WORD_MASK = (1 << NCELLS) - 1

def cell_id(x, y): return x + X_SIZE * y
def layer_mask(state, layer): return (state >> (layer * NCELLS)) & WORD_MASK
def first_empty(mask):
    missing = WORD_MASK & ~mask
    if not missing: return -1
    return (missing & -missing).bit_length() - 1
def apply_template(state, template):
    if state & template: return None
    return state | template
def shift_state(state): return state >> NCELLS
def pack_layers(layers):
    state = 0
    for i, mask in enumerate(layers): state |= (mask << (i * NCELLS))
    return state

def make_shifted_template(placement_cells, target_z):
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        if rel < 0 or rel >= LAYERS: return None
        shifted_masks[rel] |= (1 << cell_id(x, y))
    return pack_layers(shifted_masks)

print("Building T templates for 3×15 cross-section...")
t0 = time.time()
raw, _ = generate_placements(PENTACUBES['T'], (X_SIZE, Y_SIZE, 20), break_symmetry=False)
print(f"  Placements: {len(raw)} ({time.time()-t0:.1f}s)")

templates = {cell: [] for cell in range(NCELLS)}
seen = {cell: set() for cell in range(NCELLS)}
total_templates = 0

for placement in raw.values():
    cells = tuple(placement)
    for x, y, z in cells:
        target = cell_id(x, y)
        packed = make_shifted_template(cells, z)
        if packed is None: continue
        if packed in seen[target]: continue
        seen[target].add(packed)
        templates[target].append(packed)
        total_templates += 1

print(f"  Templates: {total_templates} ({time.time()-t0:.1f}s)")
print(f"  State: {LAYERS * NCELLS} bits")

# First generation (bounded)
print(f"\nFirst generation (bounded to 2M states)...")
state = 0; seen_states = {0}; queue = deque([0]); sources = set()
t0 = time.time()

while queue and len(seen_states) < 2000000:
    state = queue.popleft()
    if layer_mask(state, 0) == WORD_MASK:
        sources.add(shift_state(state))
        continue
    target = first_empty(layer_mask(state, 0))
    for template in templates[target]:
        nxt = apply_template(state, template)
        if nxt is None or nxt in seen_states: continue
        seen_states.add(nxt); queue.append(nxt)
    if len(seen_states) % 500000 == 0:
        print(f"  {len(seen_states):,} states, {len(sources)} sources ({time.time()-t0:.1f}s)", flush=True)

elapsed = time.time() - t0
print(f"Final: {len(seen_states):,} states, {len(sources)} sources ({elapsed:.1f}s)")
print(f"Queue empty: {len(queue)==0}")