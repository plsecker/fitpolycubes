#!/usr/bin/env python3
"""
Macro Preflight Estimator for S-pentacube cross-sections.

Given a, b, estimates:
- Expected first-generation source count
- Likely branching regime
- Expected closure difficulty
- Whether full enumeration is recommended
- Whether to use targeted cycle extraction instead

Uses the authoritative complexity dataset to make estimates.
"""

import sys, math, json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.frontier.macro_generalized import build_templates_general


def estimate_tractability(a: int, b: int) -> dict:
    """Estimate Macro closure difficulty for cross-section a×b."""
    
    # Build templates to get placement/template counts
    templates, NCELLS, _, concrete_count, total_templates = \
        build_templates_general(a, b)
    
    area = a * b
    perimeter = 2 * (a + b)
    aspect = max(a, b) / min(a, b)
    
    # Known reference points from the complexity dataset
    # These calibrate the estimator
    tractable_cases = {
        20: "SMALL",    # 4×5
        30: "MEDIUM",   # 5×6
        32: "LARGE",    # 4×8
        35: "MEDIUM",   # 5×7
        36: "INTRACTABLE",  # 4×9
        40: "MEDIUM",   # 4×10, 5×8 (both MEDIUM)
        45: "INTRACTABLE",  # 5×9
    }
    
    # Estimate source count
    # Empirical observation: source count grows rapidly with area
    # 4×5 (area 20): 1.5K sources, complete
    # 5×6 (area 30): 184K sources, complete
    # 4×8 (area 32): 332K sources, complete
    # 4×9 (area 36): 71K sources at 10M cap (not complete)
    # 5×7 (area 35): 58 sources at 3M cap (not complete)
    # 5×8 (area 40): 480 sources at 30M cap (not complete)
    # 4×10 (area 40): 14M sources at 15M cap (not complete)
    # 5×9 (area 45): 0 sources at 25M cap
    # 5×10 (area 50): unknown
    
    # Source density by area
    if area <= 20:
        first_gen_estimate = 1500
        macro_estimate = 1500
        scc_estimate = 11
        estimate_confidence = "HIGH"
        recommendation = "full_closure"
    elif area <= 30:
        first_gen_estimate = 200000
        macro_estimate = 8000000
        scc_estimate = 2000
        estimate_confidence = "HIGH"
        recommendation = "full_closure"
    elif area <= 32:
        first_gen_estimate = 350000
        macro_estimate = 30000000
        scc_estimate = 500
        estimate_confidence = "HIGH"
        recommendation = "full_closure"
    elif area <= 35:
        first_gen_estimate = 100  # sparse (like 5×7)
        macro_estimate = 1000
        scc_estimate = 100
        estimate_confidence = "LOW"
        recommendation = "targeted_closure"
    elif area <= 36:
        first_gen_estimate = 100000
        macro_estimate = 65000000
        scc_estimate = None
        estimate_confidence = "MEDIUM"
        recommendation = "svg_extraction"
    elif area <= 40:
        if aspect > 2.0:  # 4×10-like: tall (many rows) vs wide
            first_gen_estimate = 15000000
            macro_estimate = 100000
            scc_estimate = None
            estimate_confidence = "LOW"
            recommendation = "svg_extraction"
        else:  # 5×8-like: wider
            first_gen_estimate = 500
            macro_estimate = 25000
            scc_estimate = None
            estimate_confidence = "LOW"
            recommendation = "svg_extraction"
    elif area <= 45:
        first_gen_estimate = None  # essentially zero
        macro_estimate = None
        scc_estimate = None
        estimate_confidence = "HIGH"
        recommendation = "svg_extraction_only"
    else:
        first_gen_estimate = None
        macro_estimate = None
        scc_estimate = None
        estimate_confidence = "LOW"
        recommendation = "svg_extraction_only"
    
    # Tractability class
    if area < 30:
        tractability = "SMALL"
    elif area == 30:
        tractability = "MEDIUM"
    elif area <= 32:
        tractability = "LARGE"
    elif area <= 35:
        tractability = "MEDIUM"
    elif area == 36:
        tractability = "INTRACTABLE"
    elif area <= 40:
        tractability = "MEDIUM"
    elif area <= 45:
        tractability = "INTRACTABLE"
    else:
        tractability = "UNKNOWN"
    
    return {
        "cross_section": f"{a}×{b}",
        "area": area,
        "perimeter": perimeter,
        "aspect_ratio": round(aspect, 2),
        "concrete_placements": concrete_count,
        "total_templates": total_templates,
        "estimated_first_gen_sources": first_gen_estimate,
        "estimated_macro_states": macro_estimate,
        "estimated_scc_size": scc_estimate,
        "tractability": tractability,
        "estimate_confidence": estimate_confidence,
        "recommendation": recommendation,
        "basis": [
            "area-based calibration from 9 known cross-sections",
            f"templates={total_templates}",
            f"aspect_ratio={aspect:.2f}",
        ],
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 macro_preflight.py <a> <b>")
        print("       Estimates Macro closure difficulty for a×b cross-section.")
        sys.exit(1)
    
    a, b = int(sys.argv[1]), int(sys.argv[2])
    result = estimate_tractability(a, b)
    
    print(f"\nMacro Preflight Estimate for {a}×{b}")
    print("=" * 50)
    for k, v in result.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        elif isinstance(v, list):
            print(f"  {k}:")
            for item in v:
                print(f"    • {item}")
        else:
            print(f"  {k}: {v}")
    
    print(f"\nTractability: {result['tractability']}")
    print(f"Recommendation: {result['recommendation']}")