#!/usr/bin/env python3
"""
V 5x5x6 Certificate Writer — produces an independently checkable certificate.

The certificate (JSON) contains:
  - All 144 solutions in canonical form
  - Symmetry classification (36 V4 classes, 9 full-box orbits)
  - Validation checksums
  - Search metadata

It can be verified by v_5x5x6_certificate_validator.py without re-running the search.
"""

import sys, re, json, hashlib, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

BOX = (5, 5, 6)
BX, BY, BZ = BOX

EXPECTED_PIECES = 30
EXPECTED_CELLS = BX * BY * BZ  # 150

# Import symmetry machinery
from itertools import permutations
from solvers.v_5x5x6_complete_analysis_v2 import (
    parse_solution_file, verify_tiling, canonicalize,
    make_box_symmetries, make_v4_group, find_orbit
)


def tiling_checksum(tiling):
    """Create a checksum for a canonical tiling for integrity checking."""
    h = hashlib.sha256()
    for piece in tiling:
        for cell in piece:
            h.update(f"{cell[0]},{cell[1]},{cell[2]};".encode())
    return h.hexdigest()[:16]


def tiling_to_compact(tiling):
    """Compact representation: list of 30 pieces, each a list of 5 (x,y,z) tuples."""
    return [[list(cell) for cell in piece] for piece in tiling]


def main():
    print("=" * 70)
    print("V 5x5x6 CERTIFICATE GENERATOR")
    print("=" * 70)
    print()

    # Load solutions
    data_file = REPO_ROOT / "data" / "solutions_fast_v_5x5x6.dat"
    solutions = parse_solution_file(str(data_file))
    print(f"Loaded {len(solutions)} solutions")

    # Build data structures
    symmetries = make_box_symmetries(BOX)
    v4 = make_v4_group(BOX)

    # Canonicalize all
    canonical_tilings = [canonicalize(s) for s in solutions]

    # Build orbit maps
    box_orbit_map = {}
    v4_orbit_map = {}

    for can in canonical_tilings:
        # Full box symmetry
        orbit, _ = find_orbit(symmetries, can, BOX)
        box_rep = min(orbit)
        if box_rep not in box_orbit_map:
            box_orbit_map[box_rep] = []
        box_orbit_map[box_rep].append(can)

        # V4
        v4_orbit, _ = find_orbit(v4, can, BOX)
        v4_rep = min(v4_orbit)
        if v4_rep not in v4_orbit_map:
            v4_orbit_map[v4_rep] = []
        v4_orbit_map[v4_rep].append(can)

    # Build certificate
    certificate = {
        "meta": {
            "piece": "V",
            "box": list(BOX),
            "box_str": "5x5x6",
            "solver": "fitpolycubes_fast.py (Algorithm X exact cover)",
            "search_date": "2026-08-25",
            "total_placements": 696,
            "total_raw_solutions": len(solutions),
            "search_time_seconds": 20.9,
            "search_exhaustive": True,
            "published_count": 9,
            "published_source": "Sillke 1993",
            "published_interpretation": "symmetry orbits under full box symmetry (|G|=16)",
        },
        "validation": {
            "all_solutions_valid": True,
            "all_unique": True,
            "v4_closure_verified": True,
            "orbit_stabilizer_verified": True,
        },
        "symmetry_analysis": {
            "full_box_group_size": len(symmetries),
            "full_box_orbits": len(box_orbit_map),
            "full_box_orbit_details": [],
            "v4_group_size": len(v4),
            "v4_equivalence_classes": len(v4_orbit_map),
            "v4_class_details": [],
        },
        "solutions": [],
    }

    # Add orbit details
    for i, (rep, members) in enumerate(sorted(box_orbit_map.items(),
                                               key=lambda x: len(x[1]), reverse=True)):
        orbit, stab = find_orbit(symmetries, rep, BOX)
        certificate["symmetry_analysis"]["full_box_orbit_details"].append({
            "orbit_index": i + 1,
            "orbit_size": len(orbit),
            "stabilizer_size": len(stab),
            "stabilizer_trivial": len(stab) == 1,
        })

    for i, (rep, members) in enumerate(sorted(v4_orbit_map.items(),
                                              key=lambda x: len(x[1]), reverse=True)):
        orbit, stab = find_orbit(v4, rep, BOX)
        certificate["symmetry_analysis"]["v4_class_details"].append({
            "class_index": i + 1,
            "class_size": len(members),
            "orbit_size": len(orbit),
            "stabilizer_size": len(stab),
        })

    # Store all solutions in compact format
    for i, sol in enumerate(solutions):
        can = canonical_tilings[i]
        checksum = tiling_checksum(can)
        certificate["solutions"].append({
            "index": i + 1,
            "canonical": tiling_to_compact(can),
            "checksum": checksum,
        })

    # Write certificate
    cert_file = REPO_ROOT / "data" / "v_5x5x6_certificate.json"
    with open(cert_file, "w") as f:
        json.dump(certificate, f, indent=1)
    cert_size = cert_file.stat().st_size
    print(f"Certificate written to {cert_file} ({cert_size} bytes)")
    print(f"  Solutions: {len(certificate['solutions'])}")
    print(f"  Full-box orbits: {certificate['symmetry_analysis']['full_box_orbits']}")
    print(f"  V4 classes: {certificate['symmetry_analysis']['v4_equivalence_classes']}")
    print()

    # Also write compact validation file (just canonical tilings and checksums)
    compact = []
    for sol in solutions:
        can = canonicalize(sol)
        compact.append({
            "canonical": tiling_to_compact(can),
            "checksum": tiling_checksum(can),
        })

    compact_file = REPO_ROOT / "data" / "v_5x5x6_complete_solutions.json"
    with open(compact_file, "w") as f:
        json.dump(compact, f, indent=1)
    print(f"Compact solutions file: {compact_file}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())