#!/usr/bin/env python3
"""
Independent certificate validator for 5×6 S-pentacube tilings.

This validator does NOT share any code with the macro construction tool.
It independently checks geometric properties of a placement list.

Usage:
    python3 tools/frontier/macro_certificate.py <certificate.json>
    python3 tools/frontier/macro_certificate.py --placements <placements.txt>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ==========================================================================
# Independent S orientation generator
# ==========================================================================

def _generate_s_orientations() -> Set[Tuple[Tuple[int, int, int], ...]]:
    """Generate all 24 orientations of the S pentacube.
    
    This is a self-contained implementation that does NOT import
    from polycube_utils or any other project module.
    """
    # Canonical S piece: 5 cells
    # [[0,0,0],[1,0,0],[2,0,0],[0,0,1],[2,1,0]]
    base = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (0, 0, 1), (2, 1, 0)]
    
    orientations: Set[Tuple[Tuple[int, int, int], ...]] = set()
    
    # 8 sign flips × 6 permutations = 48, but many duplicates → 24 unique
    for sx in (1, -1):
        for sy in (1, -1):
            for sz in (1, -1):
                for perm in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
                    rotated = []
                    for p in base:
                        new_coord = [p[perm[0]] * sx, p[perm[1]] * sy, p[perm[2]] * sz]
                        rotated.append(new_coord)
                    
                    # Normalize: translate so min is at origin
                    min_x = min(c[0] for c in rotated)
                    min_y = min(c[1] for c in rotated)
                    min_z = min(c[2] for c in rotated)
                    normalized = tuple(sorted(
                        (c[0] - min_x, c[1] - min_y, c[2] - min_z) for c in rotated
                    ))
                    orientations.add(normalized)
    
    return orientations


_S_ORIENTATIONS = _generate_s_orientations()


# ==========================================================================
# Independent validator
# ==========================================================================

def validate_placement_list(
    placements: List[Tuple[int, int, int, int, int, int, int, int, int, int, int, int, int, int, int]],
    a: int,
    b: int,
    z: int,
) -> Dict:
    """Validate a list of S-pentacube placements independently.
    
    Each placement is a tuple of 15 ints: (x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4, x5,y5,z5)
    or a tuple of 5 (x,y,z) tuples.
    
    Returns dict with validation results.
    """
    errors: List[str] = []
    
    expected_cells = a * b * z
    expected_pieces = expected_cells // 5 if expected_cells % 5 == 0 else 0
    
    # Normalize placements to list of 5-cell tuples
    normalized: List[Tuple[Tuple[int, int, int], ...]] = []
    for p in placements:
        if len(p) == 15:
            # Flat format: (x1,y1,z1, x2,y2,z2, x3,y3,z3, x4,y4,z4, x5,y5,z5)
            cells = tuple(sorted((p[i], p[i+1], p[i+2]) for i in range(0, 15, 3)))
            normalized.append(cells)
        elif len(p) == 5 and all(isinstance(c, tuple) for c in p):
            cells = tuple(sorted(p))
            normalized.append(cells)
        else:
            errors.append(f"Unrecognized placement format: {p}")
    
    # 1. Check piece count
    actual_pieces = len(normalized)
    if expected_pieces and actual_pieces != expected_pieces:
        errors.append(
            f"Piece count: got {actual_pieces}, expected {expected_pieces}"
        )
    
    # 2. Check each placement
    all_cells: Set[Tuple[int, int, int]] = set()
    invalid_shapes = 0
    out_of_bounds = 0
    overlaps = 0
    
    for i, placement in enumerate(normalized):
        # Check length
        if len(placement) != 5:
            errors.append(f"Placement {i}: has {len(placement)} cells, expected 5")
            continue
        
        # Check bounds
        for x, y, zc in placement:
            if not (0 <= x < a and 0 <= y < b and 0 <= zc < z):
                out_of_bounds += 1
        
        # Check shape matches S pentacube
        # Normalize to origin
        min_x = min(c[0] for c in placement)
        min_y = min(c[1] for c in placement)
        min_z = min(c[2] for c in placement)
        canonical = tuple(sorted(
            (c[0] - min_x, c[1] - min_y, c[2] - min_z) for c in placement
        ))
        if canonical not in _S_ORIENTATIONS:
            invalid_shapes += 1
        
        # Check overlap
        for cell in placement:
            if cell in all_cells:
                overlaps += 1
            all_cells.add(cell)
    
    # 3. Check coverage
    expected_set = {(x, y, zc) for x in range(a) for y in range(b) for zc in range(z)}
    missing = expected_set - all_cells
    extra = all_cells - expected_set
    
    valid = (
        len(errors) == 0
        and invalid_shapes == 0
        and out_of_bounds == 0
        and overlaps == 0
        and len(missing) == 0
        and len(extra) == 0
        and len(all_cells) == expected_cells
    )
    
    return {
        "valid": valid,
        "a": a,
        "b": b,
        "z": z,
        "expected_cells": expected_cells,
        "expected_pieces": expected_pieces,
        "actual_pieces": actual_pieces,
        "actual_cells": len(all_cells),
        "errors": errors,
        "invalid_shapes": invalid_shapes,
        "out_of_bounds": out_of_bounds,
        "overlaps": overlaps,
        "missing_cells": len(missing),
        "extra_cells": len(extra),
    }


def validate_certificate_file(path: str) -> Dict:
    """Load and validate a certificate JSON file independently.
    
    Supports two certificate schemas:
    
    1. `generate_certificate` (macro_construction.py):
       {thickness, pieces, decomposition, validation: {a, b, valid}, ...}
    
    2. `certify_box` (macro_certify_box.py):
       {a, b, extracted_cycle_length, states, generators, family, ...}
    """
    with open(path) as f:
        cert = json.load(f)

    errors = []
    result = {
        "file": path,
        "schema": None,
        "provenance": cert.get("provenance", {}),
        "consistency_errors": errors,
    }

    # Detect schema
    if "thickness" in cert and "validation" in cert:
        # Schema 1: generate_certificate
        result["schema"] = "generate_certificate"
        a = cert.get("validation", {}).get("a", 5)
        b = cert.get("validation", {}).get("b", 6)
        z = cert.get("thickness", 0)
        result["thickness"] = z
        result["decomposition"] = cert.get("decomposition", "N/A")
        result["pieces_claimed"] = cert.get("pieces", 0)
        result["validation_claimed"] = cert.get("validation", {}).get("valid", False)

        if z <= 0:
            errors.append(f"Invalid thickness: {z}")
        vol = a * b * z
        if vol % 5 != 0:
            errors.append(f"Volume {vol} not divisible by 5")
        expected_pieces = vol // 5
        if cert.get("pieces", 0) != expected_pieces:
            errors.append(f"Claimed pieces {cert['pieces']} != expected {expected_pieces}")

    elif "extracted_cycle_length" in cert and "family" in cert:
        # Schema 2: certify_box
        result["schema"] = "certify_box"
        a = cert.get("a", 5)
        b = cert.get("b", 6)
        result["thickness"] = None
        result["decomposition"] = f"<{', '.join(map(str, cert.get('generators', [])))}>"
        # Validate each family member
        pieces_claimed = 0
        for member in cert.get("family", []):
            zz = member.get("z", 0)
            valid = member.get("valid", False)
            pieces = member.get("pieces", 0)
            if not valid:
                errors.append(f"Family member z={zz} not valid")
            if zz > 0:
                vol = a * b * zz
                expected = vol // 5 if vol % 5 == 0 else None
                if expected is not None and pieces != expected:
                    errors.append(
                        f"Family z={zz}: claimed {pieces} pieces != expected {expected}"
                    )
        result["pieces_claimed"] = pieces_claimed
        result["validation_claimed"] = cert.get("all_family_valid", False)

    else:
        errors.append("Unrecognized certificate schema")

    result["consistent"] = len(errors) == 0
    return result


# ==========================================================================
# CLI
# ==========================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independent certificate validator for 5×6 S-pentacube tilings"
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="?",
        help="Certificate JSON file to validate",
    )
    parser.add_argument(
        "--placements",
        type=str,
        help="Placement list file (one placement per line)",
    )
    parser.add_argument(
        "--box",
        type=int,
        nargs=3,
        default=[5, 6, 0],
        help="Box dimensions a b z (required with --placements)",
    )
    
    args = parser.parse_args()
    
    if args.input:
        result = validate_certificate_file(args.input)
        print(f"Certificate: {result['file']}")
        print(f"  Thickness: {result['thickness']}")
        print(f"  Decomposition: {result['decomposition']}")
        print(f"  Pieces claimed: {result['pieces_claimed']}")
        print(f"  Validation claimed: {result['validation_claimed']}")
        print(f"  Consistent: {result['consistent']}")
        if result['consistency_errors']:
            for err in result['consistency_errors']:
                print(f"  ERROR: {err}")
        return 0 if result['consistent'] else 1
    
    elif args.placements:
        a, b, z = args.box
        if z <= 0:
            print("Error: --box must include z > 0", file=sys.stderr)
            return 1
        
        # Load placements
        with open(args.placements) as f:
            lines = f.readlines()
        
        # Parse placements (each line is a JSON-like tuple)
        import ast
        placements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    p = ast.literal_eval(line)
                    placements.append(p)
                except (SyntaxError, ValueError):
                    pass
        
        result = validate_placement_list(placements, a, b, z)
        print(f"Placement validation for {a}×{b}×{z}:")
        print(f"  Pieces: {result['actual_pieces']} (expected {result['expected_pieces']})")
        print(f"  Cells: {result['actual_cells']} (expected {result['expected_cells']})")
        print(f"  Invalid shapes: {result['invalid_shapes']}")
        print(f"  Out of bounds: {result['out_of_bounds']}")
        print(f"  Overlaps: {result['overlaps']}")
        print(f"  Missing cells: {result['missing_cells']}")
        print(f"  Extra cells: {result['extra_cells']}")
        print(f"  VALID: {result['valid']}")
        if result['errors']:
            for err in result['errors']:
                print(f"  ERROR: {err}")
        return 0 if result['valid'] else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())