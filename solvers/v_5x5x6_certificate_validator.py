#!/usr/bin/env python3
"""
V 5x5x6 Certificate Validator — independently verifies the certificate.

Verifies:
  1. Every listed solution is valid (30 pieces, 150 cells, no overlaps, no gaps)
  2. Every solution is unique (no duplicate canonical forms)
  3. Total solution count matches the claim
  4. Symmetry classification is consistent (orbit-stabilizer theorem)
  5. Checksum integrity
"""

import sys, json, hashlib
from pathlib import Path
from itertools import permutations

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

BOX = (5, 5, 6)
BX, BY, BZ = BOX
EXPECTED_PIECES = 30
EXPECTED_CELLS = BX * BY * BZ


def canonicalize(placements):
    sorted_pieces = [tuple(sorted(tuple(c) for c in p)) for p in placements]
    sorted_pieces.sort()
    return tuple(sorted_pieces)


def verify_tiling(placements):
    if len(placements) != EXPECTED_PIECES:
        return False, f"Expected {EXPECTED_PIECES} pieces, got {len(placements)}"
    for i, p in enumerate(placements):
        if len(p) != 5:
            return False, f"Piece {i} has {len(p)} cells"
    cells = set()
    for pi, p in enumerate(placements):
        for x, y, z in p:
            if not (0 <= x < BX and 0 <= y < BY and 0 <= z < BZ):
                return False, f"Cell ({x},{y},{z}) out of bounds"
            if (x, y, z) in cells:
                return False, f"Overlap at ({x},{y},{z})"
            cells.add((x, y, z))
    if len(cells) != EXPECTED_CELLS:
        return False, f"Expected {EXPECTED_CELLS} cells, got {len(cells)}"
    return True, "Valid"


def checksum(tiling):
    h = hashlib.sha256()
    for piece in tiling:
        for cell in piece:
            h.update(f"{cell[0]},{cell[1]},{cell[2]};".encode())
    return h.hexdigest()[:16]


def main():
    cert_file = REPO_ROOT / "data" / "v_5x5x6_certificate.json"
    if not cert_file.exists():
        print(f"ERROR: Certificate not found at {cert_file}")
        return 1

    print("=" * 70)
    print("V 5x5x6 CERTIFICATE VALIDATOR (Independent Check)")
    print("=" * 70)
    print()

    with open(cert_file) as f:
        cert = json.load(f)

    meta = cert["meta"]
    print(f"  Piece: {meta['piece']}")
    print(f"  Box:  {meta['box_str']}")
    print(f"  Solver: {meta['solver']}")
    print(f"  Claimed raw solutions: {meta['total_raw_solutions']}")
    print(f"  Published count: {meta['published_count']} ({meta['published_source']})")
    print()

    # Phase 1: Validate every solution
    print("PHASE 1: SOLUTION VALIDATION")
    print("-" * 40)
    valid_count = 0
    invalid_count = 0
    checksum_mismatch = 0

    for entry in cert["solutions"]:
        placements = entry["canonical"]
        ok, msg = verify_tiling(placements)
        if ok:
            valid_count += 1
        else:
            invalid_count += 1
            print(f"  Solution {entry['index']}: INVALID - {msg}")

        can = canonicalize(placements)
        expected_cs = entry["checksum"]
        actual_cs = checksum(can)
        if actual_cs != expected_cs:
            checksum_mismatch += 1
            if checksum_mismatch <= 5:
                print(f"  Solution {entry['index']}: CHECKSUM MISMATCH")

    print(f"  Valid solutions: {valid_count}")
    print(f"  Invalid solutions: {invalid_count}")
    print(f"  Checksum mismatches: {checksum_mismatch}")
    print()

    # Phase 2: Uniqueness
    print("PHASE 2: UNIQUENESS CHECK")
    print("-" * 40)
    canonical_set = set()
    duplicate_count = 0
    for entry in cert["solutions"]:
        can = canonicalize(entry["canonical"])
        if can in canonical_set:
            duplicate_count += 1
            print(f"  Duplicate solution {entry['index']}")
        canonical_set.add(can)
    print(f"  Unique tilings: {len(canonical_set)}")
    print(f"  Duplicates: {duplicate_count}")
    print()

    # Phase 3: Total count
    print("PHASE 3: COUNT CHECK")
    print("-" * 40)
    claimed = meta["total_raw_solutions"]
    actual = len(cert['solutions'])
    print(f"  Claimed: {claimed}")
    print(f"  Actual: {actual}")
    count_match = (claimed == actual)
    print(f"  {'COUNT: MATCH' if count_match else 'COUNT: MISMATCH'} {'✓' if count_match else '✗'}")
    print()

    # Phase 4: Symmetry classification
    print("PHASE 4: SYMMETRY CLASSIFICATION")
    print("-" * 40)
    sa = cert["symmetry_analysis"]
    print(f"  Full box orbits: {sa['full_box_orbits']} (|G|={sa['full_box_group_size']})")
    print(f"  V4 classes: {sa['v4_equivalence_classes']} (|V4|={sa['v4_group_size']})")
    print()

    group_size = sa['full_box_group_size']
    os_pass = True
    for orbit_info in sa['full_box_orbit_details']:
        o = orbit_info['orbit_size']
        s = orbit_info['stabilizer_size']
        if o * s != group_size:
            print(f"  FAIL: Orbit {orbit_info['orbit_index']}: {o} x {s} != {group_size}")
            os_pass = False
    if os_pass:
        print("  Orbit-stabilizer theorem: ALL PASS ✓")
    print()

    # Summary
    print("=" * 70)
    all_pass = (invalid_count == 0 and duplicate_count == 0 and
                count_match and os_pass and checksum_mismatch == 0)
    if all_pass:
        print("CERTIFICATE VALIDATION: ALL 5 CHECKS PASSED ✓")
    else:
        checks = ["Valid" if invalid_count == 0 else "INVALID",
                   "Unique" if duplicate_count == 0 else "DUPLICATES",
                   "Count OK" if count_match else "COUNT WRONG",
                   "Orbit-Stab OK" if os_pass else "ORBIT-STAB FAIL",
                   "Checksums OK" if checksum_mismatch == 0 else "CHECKSUM FAIL"]
        print(f"CERTIFICATE VALIDATION: {sum(1 for c in checks if c.startswith('INVALID') or c.startswith('DUPL') or c.startswith('COUNT') or c.startswith('ORBIT') or c.startswith('CHECK'))}/5 FAILED")
        for check in checks:
            print(f"  {check}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())