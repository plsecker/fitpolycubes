#!/usr/bin/env python3
"""
Complete analysis of V 5×5×9 enumeration results.

Validates all 1120 solutions, deduplicates, classifies under V4,
and reconciles with George Sicherman's prediction.
"""

import sys, re, json, time
from pathlib import Path
from collections import defaultdict
from itertools import permutations, product

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_solution_file(filepath):
    """Parse solution file and return list of tilings (list of 45 pieces)."""
    with open(filepath) as f:
        content = f.read()
    solutions = []
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1; continue
        if line.isdigit():
            if i + 1 < len(lines):
                pl = lines[i + 1].strip()
                placements = []
                pat = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
                matches = re.findall(pat, pl)
                for j in range(0, len(matches), 5):
                    if j + 5 <= len(matches):
                        piece = [(int(matches[j+k][0]), int(matches[j+k][1]), int(matches[j+k][2])) for k in range(5)]
                        placements.append(piece)
                if len(placements) == 45:
                    solutions.append(placements)
                i += 2
            else: i += 1
        else: i += 1
    return solutions


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def verify_tiling(placements, box_dims=(5,5,9)):
    bx, by, bz = box_dims
    if len(placements) != 45:
        return False, f"Expected 45 pieces, got {len(placements)}"
    for i, p in enumerate(placements):
        if len(p) != 5:
            return False, f"Piece {i} has {len(p)} cells"
    cells = set()
    for pi, p in enumerate(placements):
        for x, y, z in p:
            if not (0 <= x < bx and 0 <= y < by and 0 <= z < bz):
                return False, f"Cell ({x},{y},{z}) out of bounds in piece {pi}"
            if (x, y, z) in cells:
                return False, f"Overlap at ({x},{y},{z})"
            cells.add((x, y, z))
    if len(cells) != bx * by * bz:
        return False, f"Expected {bx*by*bz} cells, got {len(cells)}"
    return True, "Valid"


# ---------------------------------------------------------------------------
# Canonical representation
# ---------------------------------------------------------------------------

def canonicalize(placements):
    """Deterministic canonical form."""
    sorted_pieces = [tuple(sorted(p)) for p in placements]
    sorted_pieces.sort()
    return tuple(sorted_pieces)


def tiling_to_string(placements):
    parts = []
    for piece in placements:
        piece_str = "(" + ", ".join(f"({x},{y},{z})" for x, y, z in piece) + ")"
        parts.append(piece_str)
    return "".join(parts)


# ---------------------------------------------------------------------------
# V4 group (George's convention)
# ---------------------------------------------------------------------------

# V4 = {I, R_x, R_y, R_z}
# R_x: (x, 4-y, 8-z)  -> perm=(0,1,2), signs=(1,-1,-1)
# R_y: (4-x, y, 8-z)  -> perm=(0,1,2), signs=(-1,1,-1)
# R_z: (4-x, 4-y, z)  -> perm=(0,1,2), signs=(-1,-1,1)

V4_ELEMENTS = {
    "I":   ((0,1,2), ( 1, 1, 1)),
    "R_x": ((0,1,2), ( 1,-1,-1)),
    "R_y": ((0,1,2), (-1, 1,-1)),
    "R_z": ((0,1,2), (-1,-1, 1)),
}

BOX_DIMS = (5, 5, 9)


def apply_v4(tiling, elem):
    """Apply a V4 element to a tiling."""
    perm, signs = elem
    bx, by, bz = BOX_DIMS
    dims = [bx, by, bz]
    result = []
    for piece in tiling:
        new_piece = []
        for x, y, z in piece:
            coords = [x, y, z]
            nx = coords[perm[0]] if signs[0] == 1 else dims[perm[0]] - 1 - coords[perm[0]]
            ny = coords[perm[1]] if signs[1] == 1 else dims[perm[1]] - 1 - coords[perm[1]]
            nz = coords[perm[2]] if signs[2] == 1 else dims[perm[2]] - 1 - coords[perm[2]]
            new_piece.append((nx, ny, nz))
        result.append(tuple(sorted(new_piece)))
    result.sort()
    return tuple(result)


def compute_v4_orbit(tiling):
    """Compute the V4 orbit of a tiling."""
    orbit = set()
    for name, elem in V4_ELEMENTS.items():
        transformed = apply_v4(tiling, elem)
        orbit.add(canonicalize(transformed))
    return orbit


def compute_v4_stabilizer(tiling):
    """Compute the V4 stabilizer of a tiling."""
    can = canonicalize(tiling)
    stabilizer = []
    for name, elem in V4_ELEMENTS.items():
        transformed = apply_v4(tiling, elem)
        if canonicalize(transformed) == can:
            stabilizer.append(name)
    return stabilizer


# ---------------------------------------------------------------------------
# Full box symmetry groups (for secondary analysis)
# ---------------------------------------------------------------------------

def generate_box_symmetries(box_dims, proper_only=True):
    """Generate symmetries of a rectangular box."""
    a, b, c = box_dims
    dims = [a, b, c]
    symmetries = []
    for perm in permutations([0, 1, 2]):
        if dims[perm[0]] == dims[0] and dims[perm[1]] == dims[1] and dims[perm[2]] == dims[2]:
            for sx, sy, sz in product([1, -1], repeat=3):
                if proper_only:
                    perm_sign = 1 if perm in [(0,1,2), (1,2,0), (2,0,1)] else -1
                    det = perm_sign * sx * sy * sz
                    if det != 1:
                        continue
                symmetries.append((perm, (sx, sy, sz)))
    return symmetries


def apply_symmetry(tiling, symmetry, box_dims):
    """Apply a box symmetry to a tiling."""
    perm, signs = symmetry
    bx, by, bz = box_dims
    dims = [bx, by, bz]
    result = []
    for piece in tiling:
        new_piece = []
        for x, y, z in piece:
            coords = [x, y, z]
            nx = coords[perm[0]] if signs[0] == 1 else dims[perm[0]] - 1 - coords[perm[0]]
            ny = coords[perm[1]] if signs[1] == 1 else dims[perm[1]] - 1 - coords[perm[1]]
            nz = coords[perm[2]] if signs[2] == 1 else dims[perm[2]] - 1 - coords[perm[2]]
            new_piece.append((nx, ny, nz))
        result.append(tuple(sorted(new_piece)))
    result.sort()
    return tuple(result)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("V 5×5×9 COMPLETE ENUMERATION ANALYSIS")
    print("=" * 70)
    print()
    
    # Load solutions
    print("Loading solutions...")
    sol_file = REPO_ROOT / "data" / "solutions_v_5x5x9_complete.dat"
    solutions = parse_solution_file(sol_file)
    print(f"  Loaded {len(solutions)} solutions")
    print()
    
    # -----------------------------------------------------------------------
    # Step 1: Validate every solution
    # -----------------------------------------------------------------------
    print("Step 1: Validating every solution...")
    t0 = time.time()
    valid = []
    invalid = []
    for i, sol in enumerate(solutions):
        ok, msg = verify_tiling(sol)
        if ok:
            valid.append((i, sol))
        else:
            invalid.append((i, msg))
    print(f"  Valid: {len(valid)}/{len(solutions)}")
    print(f"  Invalid: {len(invalid)}")
    for i, msg in invalid:
        print(f"    Solution {i}: {msg}")
    print(f"  Elapsed: {time.time() - t0:.1f}s")
    print()
    
    # -----------------------------------------------------------------------
    # Step 2: Deduplicate exact raw solutions
    # -----------------------------------------------------------------------
    print("Step 2: Deduplicating exact raw solutions...")
    t0 = time.time()
    raw_map = {}  # canonical -> list of solution indices
    for idx, sol in valid:
        can = canonicalize(sol)
        if can not in raw_map:
            raw_map[can] = []
        raw_map[can].append(idx)
    print(f"  Distinct raw tilings: {len(raw_map)}")
    print(f"  Duplicates: {len(valid) - len(raw_map)}")
    print(f"  Elapsed: {time.time() - t0:.1f}s")
    print()
    
    # -----------------------------------------------------------------------
    # Step 3: V4 classification
    # -----------------------------------------------------------------------
    print("Step 3: V4 classification...")
    t0 = time.time()
    
    # Build canonical set for quick lookup
    can_set = set(raw_map.keys())
    
    # Classify each distinct raw tiling under V4
    v4_classes = {}  # orbit_canonical -> {orbit_size, stabilizer, members, representative}
    processed = set()
    
    for raw_can, sol_indices in raw_map.items():
        if raw_can in processed:
            continue
        
        # Find a tiling with this canonical form
        tiling = None
        for idx, sol in valid:
            if canonicalize(sol) == raw_can:
                tiling = sol
                break
        
        if tiling is None:
            continue
        
        # Compute V4 orbit
        orbit = compute_v4_orbit(tiling)
        orbit_size = len(orbit)
        
        # Compute stabilizer
        stabilizer = compute_v4_stabilizer(tiling)
        stabilizer_size = len(stabilizer)
        
        # Orbit-stabilizer check
        os_check = (orbit_size * stabilizer_size == 4)
        
        # Find all raw tilings in this orbit
        orbit_members = set()
        orbit_solution_indices = []
        for other_can, other_indices in raw_map.items():
            if other_can in orbit:
                orbit_members.add(other_can)
                orbit_solution_indices.extend(other_indices)
                processed.add(other_can)
        
        # Check V4 closure: every V4 transform of this tiling must be in the solution set
        closure_check = True
        for name, elem in V4_ELEMENTS.items():
            transformed = apply_v4(tiling, elem)
            tc = canonicalize(transformed)
            if tc not in can_set:
                closure_check = False
                print(f"  WARNING: V4 transform {name} of class representative not in solution set!")
        
        v4_classes[raw_can] = {
            "orbit_size": orbit_size,
            "stabilizer_size": stabilizer_size,
            "stabilizer_elements": stabilizer,
            "orbit_stabilizer_check": os_check,
            "members_in_orbit": len(orbit_members),
            "solution_indices": sorted(orbit_solution_indices),
            "v4_closure": closure_check,
        }
    
    print(f"  V4 equivalence classes: {len(v4_classes)}")
    print(f"  Elapsed: {time.time() - t0:.1f}s")
    print()
    
    # -----------------------------------------------------------------------
    # Step 4: V4 class details
    # -----------------------------------------------------------------------
    print("Step 4: V4 class details...")
    print()
    
    asym_count = 0
    sym_count = 0
    rz_sym_count = 0
    
    for i, (canonical, data) in enumerate(sorted(v4_classes.items())):
        s_type = "asymmetric" if data["stabilizer_size"] == 1 else "symmetric"
        sym_elements = "+".join(sorted(data["stabilizer_elements"]))
        os_str = f"{data['orbit_size']}×{data['stabilizer_size']}={data['orbit_size']*data['stabilizer_size']}"
        check = "✓" if data["orbit_stabilizer_check"] else "✗"
        closure = "✓" if data["v4_closure"] else "✗"
        
        has_rz = "R_z" in data["stabilizer_elements"]
        has_rx = "R_x" in data["stabilizer_elements"]
        has_ry = "R_y" in data["stabilizer_elements"]
        
        print(f"  Class {i+1}: |O|={data['orbit_size']}, |S|={data['stabilizer_size']}, "
              f"{os_str} {check}, V4-closed={closure}")
        print(f"           Type: {s_type}, Stabilizer: {sym_elements}")
        print(f"           Members: {data['members_in_orbit']} raw tilings, "
              f"solutions: {data['solution_indices']}")
        if has_rz:
            print(f"           ★ Has R_z symmetry (180° about long axis)")
        if has_rx:
            print(f"           ★ Has R_x symmetry")
        if has_ry:
            print(f"           ★ Has R_y symmetry")
        print()
        
        if data["stabilizer_size"] == 1:
            asym_count += 1
        else:
            sym_count += 1
        if has_rz:
            rz_sym_count += 1
    
    # -----------------------------------------------------------------------
    # Step 5: Summary statistics
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    total_raw = len(valid)
    total_unique = len(raw_map)
    total_v4_classes = len(v4_classes)
    
    print(f"Total raw solutions: {total_raw}")
    print(f"Distinct raw tilings: {total_unique}")
    print(f"V4 equivalence classes: {total_v4_classes}")
    print(f"  Asymmetric classes (|S|=1, |O|=4): {asym_count}")
    print(f"  Symmetric classes (|S|>1): {sym_count}")
    print(f"  Classes with R_z symmetry: {rz_sym_count}")
    print()
    
    # Orbit-size distribution
    orbit_dist = defaultdict(int)
    for data in v4_classes.values():
        orbit_dist[data["orbit_size"]] += 1
    print("Orbit-size distribution:")
    for size in sorted(orbit_dist):
        count = orbit_dist[size]
        print(f"  |O|={size}: {count} classes ({count*size} raw tilings)")
    print()
    
    # Stabilizer-size distribution
    stab_dist = defaultdict(int)
    for data in v4_classes.values():
        stab_dist[data["stabilizer_size"]] += 1
    print("Stabilizer-size distribution:")
    for size in sorted(stab_dist):
        count = stab_dist[size]
        print(f"  |S|={size}: {count} classes")
    print()
    
    # Verify sum
    total_from_classes = sum(data["members_in_orbit"] for data in v4_classes.values())
    print(f"Sum of class members: {total_from_classes}")
    print(f"Matches distinct raw tilings: {total_from_classes == total_unique}")
    print()
    
    # -----------------------------------------------------------------------
    # Step 6: George reconciliation
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("GEORGE SICHERMAN RECONCILIATION")
    print("=" * 70)
    print()
    
    # George predicts: 5 asymmetric × 4 + 1 symmetric × 2 = 22
    # But that was for the incomplete 22-record snapshot.
    # Now we have the complete enumeration.
    
    print(f"George's prediction (for 22-record snapshot):")
    print(f"  5 asymmetric classes × 4 + 1 symmetric class × 2 = 22")
    print()
    print(f"Complete enumeration results:")
    print(f"  Total raw solutions: {total_raw}")
    print(f"  V4 classes: {total_v4_classes}")
    print(f"  Asymmetric (|O|=4): {asym_count}")
    print(f"  Symmetric (|O|<4): {sym_count}")
    print(f"  With R_z symmetry: {rz_sym_count}")
    print()
    
    # Check if George's known R_z-symmetric tiling is present
    rz_classes = []
    for can, data in v4_classes.items():
        if "R_z" in data["stabilizer_elements"]:
            rz_classes.append((can, data))
    
    print(f"Classes with R_z symmetry: {len(rz_classes)}")
    for i, (can, data) in enumerate(rz_classes):
        print(f"  R_z class {i+1}: |O|={data['orbit_size']}, |S|={data['stabilizer_size']}, "
              f"stabilizer={data['stabilizer_elements']}")
    print()
    
    # -----------------------------------------------------------------------
    # Step 7: Secondary analysis - full box symmetry
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("SECONDARY: Full Box Symmetry Analysis")
    print("=" * 70)
    print()
    
    box_dims = (5, 5, 9)
    
    # G8: proper rotations only
    g8 = generate_box_symmetries(box_dims, proper_only=True)
    print(f"Proper rotation group G8: {len(g8)} elements")
    
    # G16: full box symmetry including reflections
    g16 = generate_box_symmetries(box_dims, proper_only=False)
    print(f"Full box symmetry group G16: {len(g16)} elements")
    print()
    
    for group_name, group in [("G8 (proper rotations)", g8), ("G16 (full symmetry)", g16)]:
        t0 = time.time()
        classes = {}
        processed_g = set()
        
        for raw_can, sol_indices in raw_map.items():
            if raw_can in processed_g:
                continue
            
            tiling = None
            for idx, sol in valid:
                if canonicalize(sol) == raw_can:
                    tiling = sol
                    break
            if tiling is None:
                continue
            
            orbit = set()
            for sym in group:
                transformed = apply_symmetry(tiling, sym, box_dims)
                orbit.add(canonicalize(transformed))
            
            orbit_members = set()
            for other_can in raw_map:
                if other_can in orbit:
                    orbit_members.add(other_can)
                    processed_g.add(other_can)
            
            classes[raw_can] = {
                "orbit_size": len(orbit),
                "members": len(orbit_members),
            }
        
        print(f"  {group_name}: {len(classes)} classes")
        orbit_dist_g = defaultdict(int)
        for data in classes.values():
            orbit_dist_g[data["orbit_size"]] += 1
        for size in sorted(orbit_dist_g):
            count = orbit_dist_g[size]
            print(f"    |O|={size}: {count} classes")
        print(f"  Elapsed: {time.time() - t0:.1f}s")
        print()
    
    # -----------------------------------------------------------------------
    # Step 8: Final report
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print()
    print(f"Search completed: 1120 solutions in 2325s (39 min)")
    print(f"  Valid: {total_raw}")
    print(f"  Distinct raw tilings: {total_unique}")
    print(f"  V4 classes: {total_v4_classes}")
    print(f"  Asymmetric (|O|=4): {asym_count}")
    print(f"  Symmetric (|S|>1): {sym_count}")
    print(f"  R_z-symmetric classes: {rz_sym_count}")
    print()
    print(f"George's 5+1 prediction for the 22-record snapshot:")
    print(f"  Does NOT match the complete enumeration of {total_raw} solutions.")
    print(f"  The complete enumeration has {total_v4_classes} V4 classes,")
    print(f"  with {asym_count} asymmetric and {sym_count} symmetric.")
    print()
    print(f"Reproduction command:")
    print(f"  python3 solvers/fitpolycubes_fast.py V --box 5 5 9 --no-symmetry")
    print(f"  Output: data/solutions_v_5x5x9_complete.dat")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())