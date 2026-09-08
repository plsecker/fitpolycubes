#!/usr/bin/env python3
"""
Reconcile V 5×5×9 solutions with George's symmetry convention.

George uses the group of 180-degree rotations for a 5×5×9 box.
This is the Klein four-group V4 = {I, R_x, R_y, R_z} of order 4.

R_x: 180° about x-axis: (x,y,z) -> (x, 4-y, 8-z)
R_y: 180° about y-axis: (x,y,z) -> (4-x, y, 8-z)
R_z: 180° about z-axis: (x,y,z) -> (4-x, 4-y, z)   (long axis)

George predicts: 22 records = 5 asymmetric (|O|=4 each) + 1 symmetric (|O|=2)
                  = 5×4 + 1×2 = 22
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def parse_solution_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    solutions = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
        if line.isdigit():
            if i + 1 < len(lines):
                placements_line = lines[i + 1].strip()
                placements = []
                pat = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
                matches = re.findall(pat, placements_line)
                j = 0
                while j < len(matches):
                    if j + 5 <= len(matches):
                        piece = [(int(matches[j+k][0]), int(matches[j+k][1]), int(matches[j+k][2])) for k in range(5)]
                        placements.append(piece)
                    j += 5
                if len(placements) == 45:
                    solutions.append(placements)
                i += 2
            else:
                i += 1
        else:
            i += 1
    return solutions


def canonicalize(placements):
    sorted_pieces = [tuple(sorted(p)) for p in placements]
    sorted_pieces.sort()
    return tuple(sorted_pieces)


def generate_v4_group():
    """George's group: 180-degree rotations about x, y, z axes.
    Group V4 = {I, R_x, R_y, R_z}, order 4."""
    # R_x: perm=(0,1,2), signs=(1,-1,-1) -> (x, 4-y, 8-z)
    # R_y: perm=(0,1,2), signs=(-1,1,-1) -> (4-x, y, 8-z)
    # R_z: perm=(0,1,2), signs=(-1,-1,1) -> (4-x, 4-y, z)
    return [
        ((0,1,2), (1, 1, 1)),    # I: identity
        ((0,1,2), (1, -1, -1)),   # R_x: 180° about x-axis
        ((0,1,2), (-1, 1, -1)),   # R_y: 180° about y-axis
        ((0,1,2), (-1, -1, 1)),   # R_z: 180° about z-axis (long axis)
    ]


def apply_v4_to_tiling(tiling, elem, box_dims=(5,5,9)):
    """Apply a V4 element to an entire tiling."""
    perm, signs = elem
    bx, by, bz = box_dims
    dims = [bx, by, bz]
    
    transformed = []
    for piece in tiling:
        new_piece = []
        for x, y, z in piece:
            coords = [x, y, z]
            nx = coords[perm[0]] if signs[0] == 1 else dims[perm[0]] - 1 - coords[perm[0]]
            ny = coords[perm[1]] if signs[1] == 1 else dims[perm[1]] - 1 - coords[perm[1]]
            nz = coords[perm[2]] if signs[2] == 1 else dims[perm[2]] - 1 - coords[perm[2]]
            new_piece.append((nx, ny, nz))
        transformed.append(tuple(sorted(new_piece)))
    transformed.sort()
    return tuple(transformed)


def compute_orbit_v4(tiling, box_dims=(5,5,9)):
    group = generate_v4_group()
    orbit = set()
    for elem in group:
        transformed = apply_v4_to_tiling(tiling, elem, box_dims)
        orbit.add(canonicalize(transformed))
    return orbit


def compute_stabilizer_v4(tiling, box_dims=(5,5,9)):
    group = generate_v4_group()
    can = canonicalize(tiling)
    stabilizer = []
    for elem in group:
        transformed = apply_v4_to_tiling(tiling, elem, box_dims)
        if canonicalize(transformed) == can:
            stabilizer.append(elem)
    return stabilizer


def get_stabilizer_type(stabilizer):
    labels = {((0,1,2),(1,1,1)): 'I',
              ((0,1,2),(1,-1,-1)): 'R_x',
              ((0,1,2),(-1,1,-1)): 'R_y',
              ((0,1,2),(-1,-1,1)): 'R_z'}
    if len(stabilizer) == 1:
        return "asymmetric (trivial stabilizer)"
    names = [labels.get(e, str(e)) for e in stabilizer]
    names.sort()
    return f"symmetric ({'+'.join(names)})"


def main():
    print("=" * 70)
    print("V 5×5×9: George's Symmetry Convention Reconciliation")
    print("=" * 70)
    print()
    
    # Load solutions
    sol_file = Path("data/solutions_fast_v_5x5x9.dat")
    solutions = parse_solution_file(sol_file)
    print(f"Repository records: {len(solutions)}")
    print()
    
    # V4 group
    print("George's group: V4 = {I, R_x, R_y, R_z}")
    print("  Order: 4")
    print("  R_x: 180° about x-axis: (x,y,z) -> (x, 4-y, 8-z)")
    print("  R_y: 180° about y-axis: (x,y,z) -> (4-x, y, 8-z)")
    print("  R_z: 180° about z-axis: (x,y,z) -> (4-x, 4-y, z)")
    print()
    
    # Classify under V4
    box_dims = (5, 5, 9)
    classes = []
    processed = set()
    
    for idx, tiling in enumerate(solutions):
        can = canonicalize(tiling)
        if can in processed:
            continue
        
        orbit = compute_orbit_v4(tiling, box_dims)
        orbit_size = len(orbit)
        stabilizer = compute_stabilizer_v4(tiling, box_dims)
        stabilizer_size = len(stabilizer)
        
        # Find all solutions in this orbit
        orbit_solutions = []
        for j, other in enumerate(solutions):
            other_can = canonicalize(other)
            if other_can in orbit:
                orbit_solutions.append(j)
                processed.add(other_can)
        
        os_check = (orbit_size * stabilizer_size == 4)
        
        classes.append({
            'orbit_size': orbit_size,
            'stabilizer_size': stabilizer_size,
            'orbit_stabilizer_check': os_check,
            'solutions': sorted(orbit_solutions),
            'stabilizer_type': get_stabilizer_type(stabilizer),
            'stabilizer_elements': stabilizer,
        })
    
    print(f"Equivalence classes under V4: {len(classes)}")
    print()
    
    # Report
    asym_count = 0
    sym_count = 0
    for i, c in enumerate(classes):
        s_type = c['stabilizer_type']
        sols = c['solutions']
        os_str = str(c['orbit_size'] * c['stabilizer_size'])
        check = '✓' if c['orbit_stabilizer_check'] else '✗'
        print(f"  Class {i+1}: |O|={c['orbit_size']}, |S|={c['stabilizer_size']}, "
              f"|O|×|S|={os_str} {check}, "
              f"{s_type}, {len(sols)} solutions {sols}")
        if 'asymmetric' in s_type.lower():
            asym_count += 1
        else:
            sym_count += 1
    
    print()
    print(f"Asymmetric classes (|S|=1): {asym_count}")
    print(f"Symmetric classes (|S|>1): {sym_count}")
    print()
    
    # Verify total
    total_sols = sum(len(c['solutions']) for c in classes)
    total_expected = sum(c['orbit_size'] * c['stabilizer_size'] // 4 * len(c['solutions']) 
                        for c in classes)  # This doesn't make sense, just use sum
    print(f"Total solutions: {total_sols}")
    print()
    
    # Orbit-stabilizer check
    all_pass = all(c['orbit_stabilizer_check'] for c in classes)
    print(f"Orbit-stabilizer checks: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    print()
    
    # Check George's prediction: 5 asymmetric × 4 + 1 symmetric × 2 = 22
    print("=" * 70)
    print("TESTING GEORGE'S PREDICTION")
    print("=" * 70)
    print()
    
    # An class with orbit_size=4 means the tiling is fully asymmetric under V4
    # (all 4 V4 elements produce distinct tilings)
    # An class with orbit_size=2 means the tiling has one non-trivial symmetry
    # (2 V4 elements map it to itself)
    # An class with orbit_size=1 means the tiling is fixed by all V4 elements
    
    predicted_asym = asym_count  # classes with |O|=4
    predicted_sym = sym_count    # classes with |O|<4
    
    print(f"George predicts: 5 asymmetric classes × 4 + 1 symmetric class × 2 = 22")
    print(f"Actual: {asym_count} classes with |O|=4, {sym_count} classes with |O|<4")
    print()
    
    # Check if total matches 22
    total_under_v4 = sum(c['orbit_size'] for c in classes)
    # Actually, the number of records represented is sum(len(c['solutions']) for c in classes)
    # which should be 22
    
    print(f"Predicted: 5×4 + 1×2 = 22")
    
    # The prediction is about the number of solutions, not the number of classes
    # 5 asymmetric classes × 4 solutions each + 1 symmetric class × 2 solutions = 22
    predicted_solutions = asym_count * 4 + sym_count * 2
    print(f"Based on our classes: {asym_count}×4 + {sym_count}×2 = {predicted_solutions}")
    print(f"Actual solutions: {total_sols}")
    print()
    
    if total_sols == 22 and asym_count == 5 and sym_count == 1:
        print("✓ EXACT MATCH with George's prediction!")
    elif total_sols == 22 and asym_count + sym_count > 0:
        print(f"✓ Total matches 22, but structure is {asym_count}+{sym_count}")
        print(f"  (George predicted 5+1)")
    
    # Identify symmetric tilings
    print()
    print("=" * 70)
    print("SYMMETRIC TILINGS DETAIL")
    print("=" * 70)
    print()
    
    for i, c in enumerate(classes):
        if c['stabilizer_size'] > 1:
            print(f"Class {i+1}: {c['stabilizer_type']}")
            print(f"  Solutions: {c['solutions']}")
            print(f"  Orbit size: {c['orbit_size']}")
            
            # Check if R_z (long-axis rotation) is in the stabilizer
            for elem in c['stabilizer_elements']:
                if elem == ((0,1,2), (-1,-1,1)):
                    print("  ✓ Has R_z symmetry (180° rotation about long axis)")
            print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("George's convention: V4 = 180-degree rotations (order 4)")
    print(f"Equivalence classes: {len(classes)}")
    print(f"Asymmetric (|S|=1): {asym_count} classes, each with orbit size 4")
    print(f"Symmetric (|S|>1): {sym_count} class(es)")
    print()
    print(f"22 solutions → {len(classes)} equivalence classes under V4")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())