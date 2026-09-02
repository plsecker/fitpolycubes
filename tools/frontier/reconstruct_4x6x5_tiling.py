#!/usr/bin/env python3
"""
Reconstruct and validate the 4×6×5 tiling from the macro 5-cycle.

The 5-cycle in the macro graph is:
  0 → 222811427700735 → 13280595 → 25550359107624 → 16777215 → 0

Each macro edge corresponds to a sequence of S placements that fill one
complete layer. We reconstruct the full tiling by expanding each edge.
"""
from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

A, B = 4, 6
NCELLS = A * B
WORD_MASK = (1 << NCELLS) - 1

# ============================================================================
# Helper functions
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
    placement_map = {}
    for pid, placement in raw.items():
        cells = tuple(placement)
        for x, y, z in cells:
            target = x + a * y
            packed = make_shifted_template_general(cells, z, a, b)
            if packed is None: continue
            if packed in seen[target]: continue
            seen[target].add(packed)
            result[target].append(packed)
            if packed not in placement_map:
                placement_map[packed] = cells
    total_templates = sum(len(v) for v in result.values())
    return result, NCELLS, WORD_MASK, concrete_count, total_templates, placement_map

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

def state_to_layers(state, NCELLS):
    """Convert packed state to 3 layer masks."""
    return [layer_mask_general(state, i, NCELLS) for i in range(3)]

def layer_mask_to_cells(mask, a, b):
    """Convert a layer mask to list of (x, y) coordinates."""
    cells = []
    for i in range(a * b):
        if mask & (1 << i):
            x = i % a
            y = i // a
            cells.append((x, y))
    return cells


def reconstruct_edge(src_state, dst_state, templates, placement_map, a, b, NCELLS):
    """
    Reconstruct the S placements that transform src_state to dst_state.
    
    src_state is a post-shift state (layer 0 is empty, layers 1-2 have partial fill).
    We need to fill layer 0 completely, then shift, resulting in dst_state.
    
    Returns list of (x, y, z) placements.
    """
    # The edge goes: src_state → (fill layer 0) → shift → dst_state
    # So we need to find a sequence of templates that fills layer 0 of src_state
    # and results in a state whose shift equals dst_state
    
    placements = []
    current = src_state
    z_offset = 0  # We'll track the z offset as we go
    
    while True:
        # Check if layer 0 is full
        if layer_mask_general(current, 0, NCELLS) == WORD_MASK:
            # Shift and check if we reached dst_state
            shifted = shift_state_general(current, NCELLS)
            if shifted == dst_state:
                break
            else:
                # Unexpected state
                print(f"  ERROR: shifted state {shifted} != dst_state {dst_state}")
                return None
        
        # Find first empty cell in layer 0
        target = first_empty_general(layer_mask_general(current, 0, NCELLS), NCELLS)
        
        # Try each template for this target
        found = False
        for template in templates[target]:
            nxt = apply_template_general(current, template)
            if nxt is not None:
                # Check if this template leads toward dst_state
                # We need to verify that the shifted version of some continuation equals dst_state
                # For simplicity, just take the first valid template
                current = nxt
                
                # Record the placement
                # The template is a packed state; we need to find which placement it corresponds to
                if template in placement_map:
                    cells = placement_map[template]
                    # The cells are in absolute coordinates; we need to offset them
                    # based on the current z level
                    min_z = min(z for _, _, z in cells)
                    # The template was built with target_z = some value
                    # We need to figure out the actual z offset
                    # For now, record the relative placement
                    placements.append(cells)
                else:
                    print(f"  WARNING: template {template} not in placement_map")
                
                found = True
                break
        
        if not found:
            print(f"  ERROR: no valid template at target {target}")
            return None
    
    return placements


def expand_macro_edge(src_state, dst_state, templates, placement_map, a, b, NCELLS):
    """
    Expand a macro edge (src → dst) into a sequence of S placements.
    
    Returns list of (x, y, z) coordinates for all S pieces placed.
    """
    # BFS from src_state, looking for paths that fill layer 0 and shift to dst_state
    # We need to find the exact sequence of templates
    
    # State: (current_state, path_of_templates)
    queue = deque()
    queue.append((src_state, []))
    seen = {src_state}
    
    while queue:
        state, path = queue.popleft()
        
        # Check if layer 0 is full
        if layer_mask_general(state, 0, NCELLS) == WORD_MASK:
            shifted = shift_state_general(state, NCELLS)
            if shifted == dst_state:
                # Found the path!
                return path
            continue
        
        # Find first empty cell
        target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
        
        for template in templates[target]:
            nxt = apply_template_general(state, template)
            if nxt is not None and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, path + [template]))
    
    return None  # No path found


def template_to_placement(template, placement_map):
    """Convert a template (packed state) to placement cells."""
    if template in placement_map:
        return placement_map[template]
    return None


def compute_placement_z(cells, current_z):
    """
    Given placement cells in absolute coordinates and a current z offset,
    compute the relative z positions.
    """
    min_z = min(z for _, _, z in cells)
    return [(x, y, z - min_z + current_z) for x, y, z in cells]


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("4×6×5 TILING RECONSTRUCTION FROM MACRO 5-CYCLE")
    print("=" * 70)
    print()
    
    # The 5-cycle
    cycle = [0, 222811427700735, 13280595, 25550359107624, 16777215, 0]
    print(f"Macro 5-cycle:")
    for i in range(len(cycle) - 1):
        print(f"  {cycle[i]} → {cycle[i+1]}")
    print()
    
    # Build templates
    print("Building templates...")
    t0 = time.perf_counter()
    templates, NCELLS, WORD_MASK, concrete_count, total_templates, placement_map = \
        build_templates_general(A, B)
    print(f"  NCELLS={NCELLS}, concrete placements={concrete_count}, templates={total_templates}")
    print(f"  Placement map size: {len(placement_map)}")
    print()
    
    # Expand each macro edge
    all_placements = []  # List of (x, y, z) for each S piece
    current_z = 0
    
    for i in range(len(cycle) - 1):
        src = cycle[i]
        dst = cycle[i+1]
        
        print(f"Expanding edge {i}: {src} → {dst}...")
        t1 = time.perf_counter()
        
        path = expand_macro_edge(src, dst, templates, placement_map, A, B, NCELLS)
        
        if path is None:
            print(f"  FAILED: no path found for edge {i}")
            return 1
        
        elapsed = time.perf_counter() - t1
        print(f"  Found path with {len(path)} templates ({elapsed:.3f}s)")
        
        # Convert templates to placements
        for template in path:
            cells = template_to_placement(template, placement_map)
            if cells is None:
                print(f"  WARNING: template {template} not in placement map")
                continue
            
            # Compute z offset
            min_z = min(z for _, _, z in cells)
            placed_cells = [(x, y, z - min_z + current_z) for x, y, z in cells]
            all_placements.extend(placed_cells)
        
        # Each macro edge fills one layer, so advance z by 1
        current_z += 1
    
    print()
    print(f"Total S pieces placed: {len(all_placements) // 5}")
    print(f"Total cells placed: {len(all_placements)}")
    print(f"Box dimensions: {A}×{B}×{current_z}")
    
    # Validate the tiling
    print()
    print("--- Validation ---")
    
    # Check all cells are within bounds
    max_x = max(x for x, y, z in all_placements)
    max_y = max(y for x, y, z in all_placements)
    max_z = max(z for x, y, z in all_placements)
    print(f"  X range: 0-{max_x} (expected 0-{A-1})")
    print(f"  Y range: 0-{max_y} (expected 0-{B-1})")
    print(f"  Z range: 0-{max_z} (expected 0-{current_z-1})")
    
    in_bounds = all(0 <= x < A and 0 <= y < B and 0 <= z < current_z for x, y, z in all_placements)
    print(f"  All cells in bounds: {in_bounds}")
    
    # Check no overlaps
    cell_set = set(all_placements)
    no_overlaps = len(cell_set) == len(all_placements)
    print(f"  No overlaps: {no_overlaps}")
    
    # Check complete fill
    expected_cells = A * B * current_z
    complete_fill = len(cell_set) == expected_cells
    print(f"  Complete fill: {complete_fill} ({len(cell_set)}/{expected_cells})")
    
    # Check each S piece has 5 cells
    # Group by piece (every 5 consecutive cells)
    pieces_valid = True
    for i in range(0, len(all_placements), 5):
        piece = all_placements[i:i+5]
        if len(piece) != 5:
            pieces_valid = False
            print(f"  Piece {i//5} has {len(piece)} cells (expected 5)")
            break
        # Check that the piece forms a valid S shape
        # (This is complex; skip for now)
    
    print(f"  All pieces have 5 cells: {pieces_valid}")
    
    # Save the tiling
    output_path = REPO_ROOT / "data" / "frontier" / "s_4x6x5_tiling.txt"
    with open(output_path, "w") as f:
        f.write(f"# S pentacube tiling: {A}×{B}×{current_z}\n")
        f.write(f"# Macro 5-cycle reconstruction\n")
        f.write(f"# Total S pieces: {len(all_placements) // 5}\n")
        f.write(f"# Format: x y z (one cell per line, 5 consecutive lines = 1 S piece)\n")
        f.write(f"#\n")
        for x, y, z in all_placements:
            f.write(f"{x} {y} {z}\n")
    
    print(f"\nTiling saved to: {output_path}")
    print(f"\nTotal elapsed: {time.perf_counter() - t0:.2f}s")
    
    if in_bounds and no_overlaps and complete_fill:
        print("\n✓ TILING VALIDATED SUCCESSFULLY")
        return 0
    else:
        print("\n✗ TILING VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())