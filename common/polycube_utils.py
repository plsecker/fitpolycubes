import numpy as np
from common.rotmatrix import RM
from common.registry import PENTACUBES

def generate_placements(piece, box_size, break_symmetry=False):
    """
    Generates all valid placements of a piece in a box.
    If break_symmetry is True, it restricts the placements to avoid redundant solutions.
    """
    if isinstance(box_size, int):
        box_dims = (box_size, box_size, box_size)
    else:
        box_dims = box_size

    box_set = {(x, y, z) for x in range(box_dims[0]) 
                         for y in range(box_dims[1]) 
                         for z in range(box_dims[2])}
    
    placements = {}
    count = 0
    
    # Pre-calculate unique rotations of the piece
    unique_rotations = []
    seen_rotations = set()
    for rot in RM:
        rp = piece @ rot.T
        # Normalize: shift to origin and sort
        rp = rp - rp.min(axis=0)
        rp_tuple = tuple(sorted([tuple(map(int, p)) for p in rp]))
        if rp_tuple not in seen_rotations:
            seen_rotations.add(rp_tuple)
            unique_rotations.append(np.array(rp_tuple))

    # Identify the "canonical" corner to cover: (0,0,0)
    target_cell = (0, 0, 0)
    
    # For symmetry breaking, we can restrict the piece covering (0,0,0)
    # The rotations that fix (0,0,0) are those that permute x, y, z without reflections
    # Actually, the 24 cube rotations include 3 rotations that fix (0,0,0) and the corner.
    
    for cube in box_set:
        for rp in unique_rotations:
            # Shift rotated piece to current cube
            # Wait, if we use unique_rotations, we just need to shift
            # But the original code did: cube + p @ RM[rotindex].T
            # which means 'p' can be anywhere relative to its origin.
            
            # Let's use the logic from fitpolycubes.py but with unique rotations
            # To ensure we find all placements:
            # For each point in the piece, try placing THAT point at 'cube'
            for piece_point in rp:
                offset = np.array(cube) - piece_point
                shifted_rp = rp + offset
                
                # Check if all points are in box
                rpl = [tuple(map(int, pt)) for pt in shifted_rp]
                if all(pt in box_set for pt in rpl):
                    # Use a set to avoid duplicates (since different piece_points might result in same placement)
                    rpl_tuple = tuple(sorted(rpl))
                    if rpl_tuple not in placements.values():
                        placements[count] = rpl_tuple
                        count += 1
    if break_symmetry:
        # Identify all placements that cover (0,0,0).
        p_000 = [p for p in placements.values() if (0,0,0) in p]
        
        if box_dims[0] == box_dims[1] == box_dims[2]:
            # Cube case: use 3 cyclic rotations that fix (0,0,0)
            # Rotations that fix (0,0,0) and the box:
            # (x,y,z) -> (x,y,z), (y,z,x), (z,x,y)
            
            canonical_p_000 = []
            seen_orbits = set()
            
            for p in p_000:
                p_pts = set(p)
                p_rot1 = tuple(sorted([(pt[1], pt[2], pt[0]) for pt in p_pts]))
                p_rot2 = tuple(sorted([(pt[2], pt[0], pt[1]) for pt in p_pts]))
                
                p_tuple = tuple(sorted(p))
                orbit = sorted([p_tuple, p_rot1, p_rot2])
                canonical_rep = orbit[0]
                
                if canonical_rep not in seen_orbits:
                    seen_orbits.add(canonical_rep)
                    canonical_p_000.append(canonical_rep)
            
            return placements, canonical_p_000
        
        else:
            # General rectangular box: use D2h group with axis permutations
            # where dimensions match.
            # Build the list of valid permutations (those that map dims to matching dims)
            from itertools import permutations as iter_permutations
            
            dims = list(box_dims)
            valid_perms = []
            for p in iter_permutations(range(3)):
                if all(dims[i] == dims[p[i]] for i in range(3)):
                    valid_perms.append(p)
            
            def apply_symmetry(placement, perm, signs, box):
                """Apply symmetry element to a placement."""
                bx, by, bz = box
                result = []
                for x, y, z in placement:
                    coords = [x, y, z]
                    nx = coords[perm[0]]
                    ny = coords[perm[1]]
                    nz = coords[perm[2]]
                    if signs[0] == -1:
                        nx = bx - 1 - nx
                    if signs[1] == -1:
                        ny = by - 1 - ny
                    if signs[2] == -1:
                        nz = bz - 1 - nz
                    result.append((nx, ny, nz))
                return tuple(sorted(result))
            
            canonical_p_000 = []
            seen_orbits = set()
            
            for p in p_000:
                p_tuple = tuple(sorted(p))
                if p_tuple in seen_orbits:
                    continue
                
                # Generate orbit under the full box symmetry group
                orbit = set()
                for perm in valid_perms:
                    for sx in (1, -1):
                        for sy in (1, -1):
                            for sz in (1, -1):
                                transformed = apply_symmetry(p, perm, (sx, sy, sz), box_dims)
                                orbit.add(transformed)
                
                # Canonical representative: lexicographically smallest
                canonical_rep = min(orbit)
                
                if canonical_rep not in seen_orbits:
                    seen_orbits.add(canonical_rep)
                    canonical_p_000.append(canonical_rep)
            
            return placements, canonical_p_000
    
    return placements, None

def filter_and_reindex_placements(placements, canonical_p_000):
    if not canonical_p_000:
        return placements
        
    reverse_placements = {tuple(sorted(v)): k for k, v in placements.items()}
    canonical_indices = {reverse_placements[p] for p in canonical_p_000 if p in reverse_placements}
    
    filtered_placements = {}
    new_idx = 0
    removed_count = 0
    
    for r_id, cells in placements.items():
        if (0, 0, 0) in cells and r_id not in canonical_indices:
            removed_count += 1
            continue
        filtered_placements[new_idx] = cells
        new_idx += 1
        
    print(f"Symmetry breaking: Removed {removed_count} non-canonical placements covering (0, 0, 0)")
    return filtered_placements

def build_exact_cover_data(placements, box_size):
    if isinstance(box_size, int):
        box_dims = (box_size, box_size, box_size)
    else:
        box_dims = box_size
        
    box_list = [(x, y, z) for x in range(box_dims[0]) 
                         for y in range(box_dims[1]) 
                         for z in range(box_dims[2])]
    
    X = {cell: set() for cell in box_list}
    for row_id, cells in placements.items():
        for cell in cells:
            X[cell].add(row_id)
    return X, box_list
