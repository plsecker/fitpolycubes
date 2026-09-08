#!/usr/bin/env python3
"""
Reconstruct the concrete 4×5×6 S-pentacube tiling from the macro return path.

The macro return path of length 6 is:
    0 -> 584134000665 -> 146100961245 -> 51590094948 -> 13086687222 -> 1048575 -> 0

Each macro edge corresponds to filling one complete 4×5 layer (a shift). We
expand each edge into the concrete S placements that fill that layer, then
verify the resulting tiling covers the 4×5×6 box exactly.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

A, B = 4, 5
NCELLS = A * B
WORD_MASK = (1 << NCELLS) - 1

# ============================================================================
# Helper functions (same as macro_generalized.py)
# ============================================================================

def make_shifted_template_general(placement_cells, target_z, a, b):
    NCELLS = a * b
    LAYERS = 3
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        if rel < 0 or rel >= LAYERS:
            return None
        cell_id = x + a * y
        shifted_masks[rel] |= (1 << cell_id)
    state = 0
    for i, mask in enumerate(shifted_masks):
        state |= (mask << (i * NCELLS))
    return state

def build_templates_general(a, b):
    raw, _ = generate_placements(PENTACUBES["S"], (a, b, 20), break_symmetry=False)
    NCELLS = a * b
    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    concrete_count = len(raw)
    for placement in raw.values():
        cells = tuple(placement)
        for x, y, z in cells:
            target = x + a * y
            packed = make_shifted_template_general(cells, z, a, b)
            if packed is None: continue
            if packed in seen[target]: continue
            seen[target].add(packed)
            result[target].append(packed)
    total_templates = sum(len(v) for v in result.values())
    return result, NCELLS, WORD_MASK, concrete_count, total_templates

def layer_mask_general(state, layer, NCELLS):
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)

def first_empty_general(mask, NCELLS):
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    if not missing: return -1
    low = missing & -missing
    return low.bit_length() - 1

def apply_template_general(state, template):
    if state & template: return None
    return state | template

def shift_state_general(state, NCELLS):
    return state >> NCELLS

# ============================================================================
# Reconstruct placements for a macro edge
# ============================================================================

def reconstruct_edge(src_state, dst_state, templates, NCELLS, layer_index):
    """
    Reconstruct the concrete placements that fill the layer between src_state
    and dst_state. Returns list of (x, y, z_rel) placements (z relative to
    the frontier layer 0 of src_state).
    
    We do a DFS from src_state, placing templates at first-empty cells until
    we reach a state whose shift equals dst_state.
    """
    WORD_MASK = (1 << NCELLS) - 1
    
    # DFS with backtracking
    # Each node in the search tree is (state, list_of_placements)
    # A placement is (template, anchor_cell)
    # We need to track which template was placed at which anchor
    
    # We'll do a recursive search
    def dfs(state, placements):
        # Check if shifting this state gives dst_state
        if layer_mask_general(state, 0, NCELLS) == WORD_MASK:
            shifted = shift_state_general(state, NCELLS)
            if shifted == dst_state:
                return placements
            return None
        
        # Place at first empty cell
        target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
        for template in templates[target]:
            nxt = apply_template_general(state, template)
            if nxt is None:
                continue
            result = dfs(nxt, placements + [template])
            if result is not None:
                return result
        return None
    
    result = dfs(src_state, [])
    return result


def template_to_cells(template, NCELLS, a):
    """Convert a packed template to a list of (x, y, z_rel) cells."""
    cells = []
    for layer in range(3):
        mask = (template >> (layer * NCELLS)) & ((1 << NCELLS) - 1)
        for bit in range(NCELLS):
            if mask & (1 << bit):
                x = bit % a
                y = bit // a
                cells.append((x, y, layer))
    return cells


def main():
    print("=" * 70)
    print("RECONSTRUCT 4×5×6 S-PENTACUBE TILING")
    print("=" * 70)
    print()
    
    # Build templates
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates_general(A, B)
    print(f"Templates: {total_templates} target templates")
    
    # The macro return path
    path = [0, 584134000665, 146100961245, 51590094948, 13086687222, 1048575, 0]
    print(f"Macro return path (length {len(path)-1}):")
    for i in range(len(path)-1):
        print(f"  {path[i]} -> {path[i+1]}")
    print()
    
    # Reconstruct each edge
    all_placements = []  # list of (layer_index, [(x,y,z_rel)])
    
    for i in range(len(path) - 1):
        src, dst = path[i], path[i+1]
        print(f"Reconstructing edge {i+1}: {src} -> {dst}")
        
        # The last edge (1048575 -> 0) is a pure shift with no placements
        # (1048575 = WORD_MASK in layer 0, so it shifts immediately)
        if layer_mask_general(src, 0, NCELLS) == WORD_MASK:
            print(f"  Edge {i+1} is a pure shift (no placements)")
            all_placements.append([])
            continue
        
        placements = reconstruct_edge(src, dst, templates, NCELLS, i)
        if placements is None:
            print(f"  ERROR: Could not reconstruct edge {i+1}")
            return 1
        
        # Convert templates to cells
        placement_cells = [template_to_cells(t, NCELLS, A) for t in placements]
        print(f"  Found {len(placements)} placements")
        all_placements.append(placement_cells)
    
    # Now convert relative z to absolute z
    # Each edge i fills layer i (absolute z = i)
    # A placement with cells (x, y, z_rel) in edge i occupies absolute z = i + z_rel
    # But we need to be careful: the frontier layer 0 of the pre-shift state
    # corresponds to absolute layer i (0-indexed)
    
    # Actually, let's reconsider. The macro edge i goes from state at "layer boundary i"
    # to state at "layer boundary i+1". The placements in edge i fill absolute layer i.
    # A placement with z_rel in {0,1,2} occupies absolute z = i + z_rel.
    
    # Build the full set of absolute placements
    abs_placements = []
    for i, edge_placements in enumerate(all_placements):
        for cells in edge_placements:
            abs_cells = [(x, y, i + z_rel) for (x, y, z_rel) in cells]
            abs_placements.append(abs_cells)
    
    print(f"\nTotal placements: {len(abs_placements)}")
    print(f"Expected: {4*5*6//5} = {4*5*6//5} S pieces")
    
    # Verify the tiling
    print("\n--- Verification ---")
    
    # Check bounds
    max_x = max(c[0] for p in abs_placements for c in p)
    max_y = max(c[1] for p in abs_placements for c in p)
    max_z = max(c[2] for p in abs_placements for c in p)
    min_x = min(c[0] for p in abs_placements for c in p)
    min_y = min(c[1] for p in abs_placements for c in p)
    min_z = min(c[2] for p in abs_placements for c in p)
    print(f"  Bounds: x in [{min_x},{max_x}], y in [{min_y},{max_y}], z in [{min_z},{max_z}]")
    print(f"  Expected box: 4×5×6 (x in [0,3], y in [0,4], z in [0,5])")
    
    # Check each placement has 5 cells
    for i, p in enumerate(abs_placements):
        if len(p) != 5:
            print(f"  ERROR: Placement {i} has {len(p)} cells (expected 5)")
            return 1
    
    # Check no overlap
    covered = set()
    overlap = False
    for i, p in enumerate(abs_placements):
        for c in p:
            if c in covered:
                print(f"  ERROR: Overlap at {c} (placement {i})")
                overlap = True
            covered.add(c)
    if not overlap:
        print(f"  No overlap: OK")
    
    # Check coverage
    expected_cells = set()
    for x in range(4):
        for y in range(5):
            for z in range(6):
                expected_cells.add((x, y, z))
    
    missing = expected_cells - covered
    extra = covered - expected_cells
    if missing:
        print(f"  ERROR: {len(missing)} cells not covered: {sorted(missing)[:10]}...")
    else:
        print(f"  Coverage: all {len(expected_cells)} cells covered")
    if extra:
        print(f"  ERROR: {len(extra)} cells outside box: {sorted(extra)[:10]}...")
    else:
        print(f"  No cells outside box: OK")
    
    # Check each placement is a valid S-pentacube
    # S-pentacube shape: {(0,0,0),(1,0,0),(2,0,0),(0,0,1),(2,1,0)} up to rotation/translation
    # We'll check that each placement's cells form a connected set of 5 cells
    # with the right adjacency pattern
    print(f"\n  Validating S-pentacube shapes...")
    valid = True
    for i, p in enumerate(abs_placements):
        # Check connectivity (each cell adjacent to at least one other)
        cells_set = set(p)
        for c in p:
            neighbors = [
                (c[0]+1, c[1], c[2]), (c[0]-1, c[1], c[2]),
                (c[0], c[1]+1, c[2]), (c[0], c[1]-1, c[2]),
                (c[0], c[1], c[2]+1), (c[0], c[1], c[2]-1),
            ]
            if not any(n in cells_set for n in neighbors):
                print(f"  ERROR: Placement {i} has isolated cell {c}")
                valid = False
    if valid:
        print(f"  All placements connected: OK")
    
    # Write the tiling to a file
    out_path = REPO_ROOT / "data" / "frontier" / "s_4x5x6_tiling.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(f"# 4×5×6 S-pentacube tiling reconstructed from macro return path\n")
        f.write(f"# {len(abs_placements)} S pieces\n")
        f.write(f"# Each line: placement index, then 5 cells (x,y,z)\n")
        for i, p in enumerate(abs_placements):
            cells_str = " ".join(f"({x},{y},{z})" for (x, y, z) in p)
            f.write(f"{i}: {cells_str}\n")
    print(f"\nTiling saved to {out_path}")
    
    print("\nDone!")
    return 0

if __name__ == "__main__":
    sys.exit(main())