#!/usr/bin/env python3
"""
T-Pentacube Macro Preflight Strategy Selector.

Given a cross-section a×b, recommends the best exact method for determining
tileability/cyclicity.

Usage:
    python3 tools/frontier/t_piece/t_macro_preflight.py --a 3 --b 7
    python3 tools/frontier/t_piece/t_macro_preflight.py --a 3 --b 10
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.registry import PENTACUBES
from tools.frontier.piece_utils import build_templates


def estimate_method(a: int, b: int, piece: str = "T") -> dict:
    """Estimate the best method for a given cross-section."""
    area = a * b
    area_mod5 = area % 5
    
    # Build templates to get counts
    t0 = time.time()
    templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates(
        PENTACUBES[piece], a, b
    )
    template_time = time.time() - t0
    
    # Estimate state counts based on measured data
    # These are rough estimates from the T 3×N dataset
    if piece == "T" and a == 3:
        # T 3×N family
        if b <= 7:
            full_est = 10000
            first_gen_est = 100000
            recommended = "full_closure"
            expected_info = "GLOBAL theorem (period + semigroup)"
        elif b == 8:
            full_est = 1000000
            first_gen_est = 10000000
            recommended = "full_closure"
            expected_info = "GLOBAL theorem (period + semigroup)"
        elif b == 9:
            full_est = 10000
            first_gen_est = 200000
            recommended = "full_closure"
            expected_info = "GLOBAL (acyclic)"
        elif b == 10:
            full_est = 50000000
            first_gen_est = 200000
            recommended = "first_gen_cyclicity"
            expected_info = "CYCLICITY only (period unresolved)"
        elif b == 11:
            full_est = 100000000
            first_gen_est = 500000
            recommended = "first_gen_cyclicity"
            expected_info = "CYCLICITY only (period unresolved)"
        elif b == 12:
            full_est = 200000000
            first_gen_est = 2000000
            recommended = "first_gen_cyclicity"
            expected_info = "CYCLICITY only (period unresolved)"
        else:
            full_est = 10 ** (b - 5)  # rough exponential
            first_gen_est = 10 ** (b - 4)
            recommended = "first_gen_cyclicity"
            expected_info = "CYCLICITY only (period unresolved)"
    elif piece == "T" and a == 5 and b == 5:
        full_est = 60000
        first_gen_est = 100000
        recommended = "full_closure"
        expected_info = "GLOBAL theorem (period + semigroup)"
    else:
        # Unknown cross-section
        full_est = None
        first_gen_est = None
        recommended = "unknown"
        expected_info = "unknown"
    
    # Determine if piece-count integrality gives a period divisor
    if area_mod5 != 0:
        period_divisor = 5
    else:
        period_divisor = 1
    
    return {
        "cross_section": f"{a}x{b}",
        "piece": piece,
        "area": area,
        "area_mod5": area_mod5,
        "period_divisor": period_divisor,
        "placements": concrete_count,
        "templates": total_templates,
        "template_time": template_time,
        "estimated_full_closure_states": full_est,
        "estimated_first_gen_states": first_gen_est,
        "recommended_method": recommended,
        "expected_information": expected_info,
        "note": (
            "Full closure is preferred when feasible (gives period + semigroup). "
            "First-gen cyclicity test is preferred when full closure is too large "
            "(gives cyclicity only, not period)."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="T-Pentacube Macro Preflight Strategy Selector"
    )
    parser.add_argument("--a", type=int, required=True, help="First dimension")
    parser.add_argument("--b", type=int, required=True, help="Second dimension")
    parser.add_argument("--piece", type=str, default="T", help="Piece letter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    result = estimate_method(args.a, args.b, args.piece)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Preflight Estimate for {result['cross_section']} ({result['piece']}) ===")
        print(f"Area: {result['area']} (mod 5 = {result['area_mod5']})")
        print(f"Period divisor (piece-count): {result['period_divisor']}")
        print(f"Placements: {result['placements']}")
        print(f"Templates: {result['templates']}")
        print()
        print(f"Recommended method: {result['recommended_method']}")
        print(f"Expected information: {result['expected_information']}")
        if result['estimated_full_closure_states']:
            print(f"Estimated full closure states: {result['estimated_full_closure_states']:,}")
        if result['estimated_first_gen_states']:
            print(f"Estimated first-gen states: {result['estimated_first_gen_states']:,}")
        print()
        print(f"Note: {result['note']}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())