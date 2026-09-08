#!/usr/bin/env python3
"""
Simple bidirectional test for V 5×5×6.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from solvers.v_5x5_macro import build_templates
from solvers.v_5x5_bidirectional_correct import (
    explore_forward, find_predecessors_correct
)


def main():
    print("=" * 70)
    print("SIMPLE BIDIRECTIONAL TEST")
    print("=" * 70)
    print()
    
    # Build templates
    print("Building templates...")
    templates, _, _, _, _ = build_templates()
    print(f"  Templates built")
    print()
    
    # Forward: F[0] = {0}
    print("Forward search:")
    F0 = {0}
    print(f"  F[0] = {len(F0)} states")
    
    # F[1]
    start = time.time()
    F1 = set()
    for s in F0:
        F1.update(explore_forward(s, templates))
    print(f"  F[1] = {len(F1)} states ({time.time()-start:.1f}s)")
    
    # F[2]
    start = time.time()
    F2 = set()
    for s in F1:
        F2.update(explore_forward(s, templates))
    print(f"  F[2] = {len(F2)} states ({time.time()-start:.1f}s)")
    
    # F[3]
    start = time.time()
    F3 = set()
    for s in F2:
        F3.update(explore_forward(s, templates))
    print(f"  F[3] = {len(F3)} states ({time.time()-start:.1f}s)")
    print()
    
    # Reverse: R[0] = {0}
    print("Reverse search:")
    R0 = {0}
    print(f"  R[0] = {len(R0)} states")
    
    # R[1]
    start = time.time()
    R1 = set()
    for s in R0:
        R1.update(find_predecessors_correct(s, templates))
    print(f"  R[1] = {len(R1)} states ({time.time()-start:.1f}s)")
    
    # R[2]
    start = time.time()
    R2 = set()
    for s in R1:
        R2.update(find_predecessors_correct(s, templates))
    print(f"  R[2] = {len(R2)} states ({time.time()-start:.1f}s)")
    
    # R[3]
    start = time.time()
    R3 = set()
    for s in R2:
        R3.update(find_predecessors_correct(s, templates))
    print(f"  R[3] = {len(R3)} states ({time.time()-start:.1f}s)")
    print()
    
    # Intersection
    print("Intersection at depth 3:")
    intersection = F3 & R3
    print(f"  |F[3]| = {len(F3)}")
    print(f"  |R[3]| = {len(R3)}")
    print(f"  |Intersection| = {len(intersection)}")
    print()
    
    if len(intersection) > 0:
        print("✓ Bidirectional search is working!")
        print(f"  Found {len(intersection)} states at the meeting point")
    else:
        print("✗ No intersection found")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
