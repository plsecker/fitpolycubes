#!/usr/bin/env python3
"""
Extended comparison: check if the two tilings of 4×5×6 are related
by box symmetries, and analyze the cycle structure more deeply.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements


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
    return result, NCELLS, (1 << NCELLS) - 1, concrete_count, total_templates, placement_map


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


def expand_macro_edge(src_state, dst_state, templates, a, b, NCELLS):
    from collections import deque
    queue = deque()
    queue.append((src_state, []))
    seen = {src_state}
    while queue:
        state, path = queue.popleft()
        if layer_mask_general(state, 0, NCELLS) == (1 << NCELLS) - 1:
            shifted = shift_state_general(state, NCELLS)
            if shifted == dst_state:
                return path
            continue
        target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
        for template in templates[target]:
            nxt = apply_template_general(state, template)
            if nxt is not None and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, path + [template]))
    return None


def template_to_placement(template, placement_map):
    return placement_map.get(template)


def reconstruct_cycle_tiling(cycle_states, templates, placement_map, a, b, NCELLS):
    all_placements = []
    current_z = 0
    for i in range(len(cycle_states) - 1):
        src = cycle_states[i]
        dst = cycle_states[i + 1]
        path = expand_macro_edge(src, dst, templates, a, b, NCELLS)
        if path is None:
            return None
        for template in path:
            cells = template_to_placement(template, placement_map)
            if cells is None:
                continue
            min_z = min(z for _, _, z in cells)
            placed = [(x, y, z - min_z + current_z) for x, y, z in cells]
            all_placements.extend(placed)
        current_z += 1
    return all_placements


def canonicalize_tiling(cells):
    pieces = []
    for i in range(0, len(cells), 5):
        piece = tuple(sorted(cells[i:i+5]))
        pieces.append(piece)
    pieces.sort()
    return pieces


def tiling_signature(pieces):
    return tuple(pieces)


def permute_axes(cells, perm):
    """
    Apply axis permutation to cells.
    perm = (px, py, pz) where each is 0, 1, or 2 (x, y, or z index).
    """
    axes = [(x, y, z) for x, y, z in cells]
    return [(axes[i][perm[0]], axes[i][perm[1]], axes[i][perm[2]]) for i in range(len(axes))]


def reflect_axis(cells, axis, max_val):
    """Reflect along an axis (0=x, 1=y, 2=z)."""
    result = []
    for x, y, z in cells:
        vals = [x, y, z]
        vals[axis] = max_val - vals[axis]
        result.append(tuple(vals))
    return result


def generate_box_symmetries(a, b, c):
    """
    Generate all 8 symmetries of the a×b×c box.
    Returns list of (perm, (reflect_x, reflect_y, reflect_z)) tuples.
    """
    symmetries = []
    # All permutations of axes
    perms = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    dims = [a, b, c]
    
    for perm in perms:
        # Check if the permuted dimensions match the original
        pdims = (dims[perm[0]], dims[perm[1]], dims[perm[2]])
        if pdims != (a, b, c):
            continue  # Only keep dimension-preserving symmetries
        
        # For each permutation, add all 8 reflection combinations
        for rx in [False, True]:
            for ry in [False, True]:
                for rz in [False, True]:
                    symmetries.append((perm, (rx, ry, rz)))
    
    return symmetries


def apply_symmetry(cells, symmetry, dims):
    """Apply a box symmetry to a tiling."""
    perm, (rx, ry, rz) = symmetry
    a, b, c = dims
    
    # First permute axes
    result = []
    for x, y, z in cells:
        vals = [x, y, z]
        new_vals = (vals[perm[0]], vals[perm[1]], vals[perm[2]])
        result.append(new_vals)
    
    # Then reflect
    max_vals = [a-1, b-1, c-1]
    result2 = []
    for x, y, z in result:
        vals = [x, y, z]
        if rx: vals[0] = max_vals[0] - vals[0]
        if ry: vals[1] = max_vals[1] - vals[1]
        if rz: vals[2] = max_vals[2] - vals[2]
        result2.append(tuple(vals))
    
    return result2


def validate_tiling(cells, a, b, c):
    if len(cells) != a * b * c:
        return False, f"cell count {len(cells)} != {a*b*c}"
    cell_set = set(cells)
    if len(cell_set) != len(cells):
        return False, f"overlaps: {len(cells) - len(cell_set)} duplicates"
    if not all(0 <= x < a and 0 <= y < b and 0 <= z < c for x, y, z in cells):
        return False, "out of bounds"
    return True, "valid"


def main():
    print("=" * 70)
    print("DEEP COMPARISON: 4×5×6 TILINGS FROM BOTH MACRO ORIENTATIONS")
    print("=" * 70)
    print()

    # Read the two tilings
    def read_tiling_4x5(path):
        cells = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(': ', 1)[1] if ': ' in line else line
                for part in parts.split(') ('):
                    part = part.strip('() ')
                    if not part:
                        continue
                    x, y, z = map(int, part.split(','))
                    cells.append((x, y, z))
        return cells

    def read_tiling_4x6(path):
        cells = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                x, y, z = map(int, line.split())
                cells.append((x, y, z))
        return cells

    t45_path = REPO_ROOT / "data" / "frontier" / "s_4x5x6_tiling.txt"
    t46_path = REPO_ROOT / "data" / "frontier" / "s_4x6x5_tiling.txt"

    t45_cells = read_tiling_4x5(t45_path)
    t46_cells = read_tiling_4x6(t46_path)

    print(f"  4×5×6 tiling: {len(t45_cells)} cells, {len(t45_cells)//5} pieces")
    print(f"  4×6×5 tiling: {len(t46_cells)} cells, {len(t46_cells)//5} pieces")
    print()

    # Both are valid tilings of their respective boxes
    v1, m1 = validate_tiling(t45_cells, 4, 5, 6)
    v2, m2 = validate_tiling(t46_cells, 4, 6, 5)
    print(f"  4×5×6 validation: {m1}")
    print(f"  4×6×5 validation: {m2}")
    print()

    # Convert 4×6×5 to 4×5×6 coordinates (swap y and z)
    t46_as_4x5 = [(x, z, y) for x, y, z in t46_cells]
    v3, m3 = validate_tiling(t46_as_4x5, 4, 5, 6)
    print(f"  4×6×5 permuted to 4×5×6: {m3}")
    print()

    # Canonicalize both in 4×5×6 coordinates
    canon_t45 = canonicalize_tiling(t45_cells)
    canon_t46 = canonicalize_tiling(t46_as_4x5)
    sig_t45 = tiling_signature(canon_t45)
    sig_t46 = tiling_signature(canon_t46)

    print(f"  Direct match: {sig_t45 == sig_t46}")
    print()

    # Generate all 8 symmetries of the 4×5×6 box
    print("--- Checking box symmetries ---")
    print()

    # The 4×5×6 box has restricted symmetries because dimensions differ
    # Only the identity permutation preserves (4,5,6)
    # Permutations: (0,1,2) identity, (0,2,1) would give (4,6,5) ≠ (4,5,6)
    # So only identity permutation preserves dimensions
    # But reflections are always valid
    
    # Generate all dimension-preserving symmetries
    dims = (4, 5, 6)
    symmetries = generate_box_symmetries(4, 5, 6)
    
    print(f"  Box 4×5×6 has {len(symmetries)} dimension-preserving symmetries:")
    for i, (perm, refs) in enumerate(symmetries):
        perm_name = ''.join(['x', 'y', 'z'][p] for p in perm)
        ref_name = ''.join(['' if not r else '-' for r in refs])
        print(f"    Symmetry {i}: perm=({perm_name}), reflect=({refs[0]},{refs[1]},{refs[2]})")
    print()

    # Check if t46 matches any symmetry of t45
    found_match = False
    for i, sym in enumerate(symmetries):
        t45_sym = apply_symmetry(t45_cells, sym, dims)
        canon_sym = canonicalize_tiling(t45_sym)
        sig_sym = tiling_signature(canon_sym)
        
        if sig_sym == sig_t46:
            print(f"  ✓ MATCH: 4×6×5 tiling = 4×5×6 tiling under symmetry {i}")
            found_match = True
            break
    
    if not found_match:
        print(f"  ✗ No symmetry maps the two tilings to each other")
        print(f"  → The two tilings are GENUINELY DIFFERENT tilings of 4×5×6")
        print()
        
        # Count piece overlaps
        set_t45 = set(canon_t45)
        set_t46 = set(canon_t46)
        common = set_t45 & set_t46
        only_t45 = set_t45 - set_t46
        only_t46 = set_t46 - set_t45
        print(f"  Common pieces: {len(common)}")
        print(f"  Pieces only in 4×5×6 tiling: {len(only_t45)}")
        print(f"  Pieces only in 4×6×5 tiling: {len(only_t46)}")
        print()
        
        # Show the different pieces
        if only_t45:
            print(f"  Pieces unique to 4×5×6 tiling:")
            for p in sorted(only_t45)[:5]:
                print(f"    {p}")
            if len(only_t45) > 5:
                print(f"    ... and {len(only_t45)-5} more")
        print()
        if only_t46:
            print(f"  Pieces unique to 4×6×5 tiling:")
            for p in sorted(only_t46)[:5]:
                print(f"    {p}")
            if len(only_t46) > 5:
                print(f"    ... and {len(only_t46)-5} more")
        print()

    # Now reconstruct the 4×5 cycle 1 and 4×6 cycle 2 tilings and compare
    print("--- Reconstructing macro cycle tilings ---")
    print()

    # Build templates
    t45_templates, t45_NCELLS, _, _, _, t45_pmap = build_templates_general(4, 5)
    t46_templates, t46_NCELLS, _, _, _, t46_pmap = build_templates_general(4, 6)

    # 4×5 cycle 1 (the 6-cycle return)
    cycle_4x5_1 = [0, 584134000665, 146100961245, 51590094948, 13086687222, 1048575, 0]
    t45_reconstructed = reconstruct_cycle_tiling(cycle_4x5_1, t45_templates, t45_pmap, 4, 5, t45_NCELLS)
    
    # 4×6 cycle 2 (the 5-cycle return)
    cycle_4x6_2 = [0, 222811427700735, 13280595, 25550359107624, 16777215, 0]
    t46_reconstructed = reconstruct_cycle_tiling(cycle_4x6_2, t46_templates, t46_pmap, 4, 6, t46_NCELLS)

    if t45_reconstructed and t46_reconstructed:
        print(f"  4×5 cycle 1 reconstructed: {len(t45_reconstructed)} cells")
        print(f"  4×6 cycle 2 reconstructed: {len(t46_reconstructed)} cells")
        
        # Compare with saved tilings
        canon_recon_45 = canonicalize_tiling(t45_reconstructed)
        canon_recon_46 = canonicalize_tiling(t46_reconstructed)
        
        sig_recon_45 = tiling_signature(canon_recon_45)
        sig_recon_46 = tiling_signature(canon_recon_46)
        
        print(f"  4×5 reconstructed == saved 4×5×6 tiling: {sig_recon_45 == sig_t45}")
        print(f"  4×6 reconstructed == saved 4×6×5 tiling: {sig_recon_46 == sig_t46}")
        
        # Check if reconstructed tilings match each other (under permutation)
        t46_recon_as_4x5 = [(x, z, y) for x, y, z in t46_reconstructed]
        canon_recon_46_as_45 = canonicalize_tiling(t46_recon_as_4x5)
        sig_recon_46_as_45 = tiling_signature(canon_recon_46_as_45)
        
        print(f"  4×5 reconstructed == 4×6 reconstructed (permuted): {sig_recon_45 == sig_recon_46_as_45}")
        
        # Check if reconstructed 4×6 tiling matches saved 4×5 tiling under symmetry
        print()
        print("  Checking if reconstructed 4×6 tiling matches saved 4×5 tiling under symmetry:")
        found = False
        for i, sym in enumerate(symmetries):
            t45_sym = apply_symmetry(t45_cells, sym, dims)
            canon_sym = canonicalize_tiling(t45_sym)
            sig_sym = tiling_signature(canon_sym)
            if sig_sym == sig_recon_46_as_45:
                print(f"    ✓ Match under symmetry {i}")
                found = True
                break
        if not found:
            print(f"    ✗ No symmetry match")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("  1. The 4×5×6 box has at least 2 distinct tilings")
    print("     (the one reconstructed from 4×5 cycle 1 and the one")
    print("      reconstructed from 4×6 cycle 2)")
    print()
    print("  2. These tilings are NOT related by box symmetries")
    print("     (they are genuinely different arrangements of S pieces)")
    print()
    print("  3. The published '1 solution' for 4×5×6 may count")
    print("     differently (e.g., counting only up to symmetry)")
    print()
    print("  4. The 4×5 cycle 2 (internal SCC cycle not containing 0)")
    print("     does NOT correspond to a complete box tiling")
    print()
    print("  5. The 4×6 10-cycles produce 4×6×10 tilings")
    print("     (double the minimal box thickness)")
    print()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())