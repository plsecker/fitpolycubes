#!/usr/bin/env python3
"""
Analyze all 22 repository solutions for V in 5×5×9.
Canonicalize under the 16-element symmetry group and determine orbits.
"""

import sys
import time
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def parse_solution_file(filepath):
    """Parse solution file and return list of tilings."""
    solutions = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by solution numbers
    # Format: number\nplacements\nnumber\nplacements...
    lines = content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Check if this is a solution number
        if line.isdigit():
            # Next line should be the placements
            if i + 1 < len(lines):
                placements_line = lines[i + 1].strip()
                
                # Parse the placements
                # Format: ((x,y,z), (x,y,z), ...)((x,y,z), ...)
                placements = []
                
                # Use regex to find all piece placements
                # Each piece is ((x,y,z), (x,y,z), (x,y,z), (x,y,z), (x,y,z))
                piece_pattern = r'\(\((\d+),\s*(\d+),\s*(\d+)\),\s*\((\d+),\s*(\d+),\s*(\d+)\),\s*\((\d+),\s*(\d+),\s*(\d+)\),\s*\((\d+),\s*(\d+),\s*(\d+)\),\s*\((\d+),\s*(\d+),\s*(\d+)\)\)'
                
                matches = re.findall(piece_pattern, placements_line)
                
                for match in matches:
                    piece = [
                        (int(match[0]), int(match[1]), int(match[2])),
                        (int(match[3]), int(match[4]), int(match[5])),
                        (int(match[6]), int(match[7]), int(match[8])),
                        (int(match[9]), int(match[10]), int(match[11])),
                        (int(match[12]), int(match[13]), int(match[14])),
                    ]
                    placements.append(piece)
                
                if len(placements) == 45:
                    solutions.append(placements)
                
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    return solutions


def canonicalize_tiling(placements):
    """Canonicalize a tiling by sorting pieces and coordinates."""
    # Sort coordinates within each piece
    sorted_pieces = [tuple(sorted(piece)) for piece in placements]
    # Sort pieces
    sorted_pieces.sort()
    return tuple(sorted_pieces)


def get_box_symmetries_5x5x9():
    """
    Generate all 16 symmetries of the 5×5×9 box.
    
    Symmetries:
    - 2 permutations of x,y axes (since both are 5)
    - 8 reflections (2^3 for x,y,z)
    - Total: 2 × 8 = 16
    """
    symmetries = []
    
    # Permutations of x,y (since both dimensions are 5)
    xy_perms = [
        (0, 1),  # identity
        (1, 0),  # swap x,y
    ]
    
    # Reflections for each axis
    for xy_perm in xy_perms:
        for reflect_x in [False, True]:
            for reflect_y in [False, True]:
                for reflect_z in [False, True]:
                    symmetries.append((xy_perm, reflect_x, reflect_y, reflect_z))
    
    return symmetries


def apply_symmetry(placements, symmetry, box_dims):
    """Apply a symmetry transformation to a tiling."""
    xy_perm, reflect_x, reflect_y, reflect_z = symmetry
    box_x, box_y, box_z = box_dims
    
    transformed = []
    for piece in placements:
        new_piece = []
        for x, y, z in piece:
            # Apply permutation
            if xy_perm == (0, 1):
                nx, ny = x, y
            else:  # (1, 0)
                nx, ny = y, x
            
            # Apply reflections
            if reflect_x:
                nx = box_x - 1 - nx
            if reflect_y:
                ny = box_y - 1 - ny
            if reflect_z:
                nz = box_z - 1 - z
            else:
                nz = z
            
            new_piece.append((nx, ny, nz))
        
        transformed.append(tuple(sorted(new_piece)))
    
    return canonicalize_tiling(transformed)


def verify_tiling(placements, box_dims):
    """Verify that a tiling is valid."""
    box_x, box_y, box_z = box_dims
    expected_cells = box_x * box_y * box_z
    
    # Check number of pieces
    if len(placements) != 45:
        return False, f"Expected 45 pieces, got {len(placements)}"
    
    # Check each piece has 5 cells
    for i, piece in enumerate(placements):
        if len(piece) != 5:
            return False, f"Piece {i} has {len(piece)} cells, expected 5"
    
    # Check all cells are within bounds
    all_cells = set()
    for piece in placements:
        for x, y, z in piece:
            if not (0 <= x < box_x and 0 <= y < box_y and 0 <= z < box_z):
                return False, f"Cell ({x},{y},{z}) out of bounds"
            if (x, y, z) in all_cells:
                return False, f"Cell ({x},{y},{z}) appears twice"
            all_cells.add((x, y, z))
    
    # Check all cells are covered
    if len(all_cells) != expected_cells:
        return False, f"Expected {expected_cells} cells, got {len(all_cells)}"
    
    return True, "Valid tiling"


def main():
    print("=" * 70)
    print("V 5×5×9 Repository Solution Analysis")
    print("=" * 70)
    print()
    
    # Load solutions
    solution_file = Path("data/solutions_fast_v_5x5x9.dat")
    if not solution_file.exists():
        print(f"ERROR: Solution file not found: {solution_file}")
        return 1
    
    print(f"Loading solutions from {solution_file}...")
    solutions = parse_solution_file(solution_file)
    print(f"Loaded {len(solutions)} solutions")
    print()
    
    # Verify all solutions
    print("Verifying solutions...")
    box_dims = (5, 5, 9)
    valid_solutions = []
    
    for i, sol in enumerate(solutions):
        is_valid, msg = verify_tiling(sol, box_dims)
        if is_valid:
            valid_solutions.append((i, sol))
        else:
            print(f"  Solution {i}: INVALID - {msg}")
    
    print(f"Valid solutions: {len(valid_solutions)}/{len(solutions)}")
    print()
    
    # Get symmetry group
    symmetries = get_box_symmetries_5x5x9()
    print(f"Symmetry group size: {len(symmetries)}")
    print()
    
    # Canonicalize all solutions
    print("Canonicalizing solutions under symmetry group...")
    canonical_forms = {}
    
    for idx, sol in valid_solutions:
        # Try all symmetries and find the lexicographically smallest
        best_canonical = None
        
        for sym in symmetries:
            transformed = apply_symmetry(sol, sym, box_dims)
            if best_canonical is None or transformed < best_canonical:
                best_canonical = transformed
        
        canonical_forms[idx] = best_canonical
    
    print(f"Canonicalized {len(canonical_forms)} solutions")
    print()
    
    # Group into orbits
    print("Grouping into symmetry orbits...")
    orbits = defaultdict(list)
    
    for idx, canonical in canonical_forms.items():
        orbits[canonical].append(idx)
    
    print(f"Found {len(orbits)} distinct symmetry orbits")
    print()
    
    # Report results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    for orbit_num, (canonical, solution_indices) in enumerate(orbits.items(), 1):
        print(f"Orbit {orbit_num}:")
        print(f"  Size: {len(solution_indices)} solutions")
        print(f"  Solutions: {sorted(solution_indices)}")
        print(f"  Representative (first 3 pieces):")
        for i, piece in enumerate(canonical[:3]):
            print(f"    Piece {i}: {piece}")
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Total repository solutions: {len(solutions)}")
    print(f"Valid solutions: {len(valid_solutions)}")
    print(f"Distinct symmetry orbits: {len(orbits)}")
    print()
    
    # Verify orbit sizes sum correctly
    total_in_orbits = sum(len(indices) for indices in orbits.values())
    print(f"Sum of orbit sizes: {total_in_orbits}")
    print(f"Matches valid solutions: {total_in_orbits == len(valid_solutions)}")
    print()
    
    # Conclusion
    if len(orbits) >= 2:
        print("✓ CONFIRMED: At least 2 symmetry orbits exist in repository")
        print(f"  Repository contains {len(orbits)} distinct orbits")
    else:
        print("✗ Only 1 orbit found in repository")
    
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
