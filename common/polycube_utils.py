import numpy as np
from common.rotmatrix import RM

PENTACUBES = {
    "F": np.array([[1,0,0],[0,1,0],[1,1,0],[1,2,0],[2,2,0]]),
    "I": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0]]),
    "L": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [3, 1, 0]]),
    "N": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 0, 1], [3, 0, 1]]),
    "P": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]]),
    "T": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 2, 0]]),
    "U": np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0]]),
    "V": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [0, 2, 0]]),
    "W": np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]),
    "X": np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [1, 2, 0], [2, 1, 0]]),
    "Y": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [2, 1, 0]]),
    "Z": np.array([[0, 0, 0],[1, 0, 0],[1, 1, 0],[1, 2, 0],[2, 2, 0]]),
    "A": np.array([[0, 0, 0],[1, 0, 0],[1, 0, 1],[0, 1, 0],[0, 1, 1]]),         # piece 37, piece 24 of https://puzzlewillbeplayed.com/Shirakawa/5-24.html

    "K": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [2, 0, 1]]),     # piece 81 of https://www.math.uni-bielefeld.de/~sillke/PENTA/cube5 https://puzzlewillbeplayed.com/Shirakawa/5-13.html
    "M": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 1, 1]]),     # piece 51, piece 18 of https://puzzlewillbeplayed.com/Shirakawa/5-18.html
    "Q": np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[2,2,0]]),
    "E": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [1, 0, 1]]),     # piece 71 of https://www.math.uni-bielefeld.de/~sillke/PENTA/cube5 https://puzzlewillbeplayed.com/Shirakawa/5-14.html
    "S": np.array([[0,0,0],[1,0,0],[2,0,0],[2,1,0],[2,0,1],]),                  # piece 21 of https://www.math.uni-bielefeld.de/~sillke/PENTA/qu5.21, https://puzzlewillbeplayed.com/Shirakawa/5-15.html
    "J": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [2, 1, 1]]),     # piece 41 of https://www.math.uni-bielefeld.de/~sillke/PENTA/cube5
    "R": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [2, 1, 1]]),     # piece 33 of https://www.math.uni-bielefeld.de/~sillke/PENTA/qu5.33
    "H": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 1], [2, 0, 1],]),    # piece 31 of https://www.math.uni-bielefeld.de/~sillke/PENTA/qu5.21
    "G": np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1], [2, 1, 1]]),     # piece 35/36 of https://www.math.uni-bielefeld.de/~sillke/PENTA/qu5.35

}

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
    if break_symmetry and box_dims[0] == box_dims[1] == box_dims[2]:
        # if break_symmetry:
        # Symmetry breaking for a cube:
        # 1. Identify all placements that cover (0,0,0).
        # 2. Group them into orbits under the 3 rotations that fix (0,0,0).
        # 3. Only keep one representative from each orbit for the *first* column.
        
        p_000 = [p for p in placements.values() if (0,0,0) in p]
        
        # Rotations that fix (0,0,0) and the 5x5x5 box:
        # These are rotations that permute the axes x, y, z.
        # There are 3 such rotations (including identity):
        # (x,y,z) -> (x,y,z)
        # (x,y,z) -> (y,z,x)
        # (x,y,z) -> (z,x,y)
        
        canonical_p_000 = []
        seen_orbits = set()
        
        for p in p_000:
            # Generate the orbit of this placement under the 3 rotations
            orbit = []
            p_pts = set(p)
            # Rotation 1: (x,y,z) -> (y,z,x)
            p_rot1 = tuple(sorted([(pt[1], pt[2], pt[0]) for pt in p_pts]))
            # Rotation 2: (x,y,z) -> (z,x,y)
            p_rot2 = tuple(sorted([(pt[2], pt[0], pt[1]) for pt in p_pts]))
            
            p_tuple = tuple(sorted(p))
            orbit = sorted([p_tuple, p_rot1, p_rot2])
            canonical_rep = orbit[0]
            
            if canonical_rep not in seen_orbits:
                seen_orbits.add(canonical_rep)
                canonical_p_000.append(canonical_rep)
        
        # Now we need to tell the solver to only use canonical_p_000 for (0,0,0).
        # We can return this information.
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
