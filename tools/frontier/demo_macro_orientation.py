#!/usr/bin/env python3
"""
Apply the orientation-selection helper to representative boxes
already used by the project.

This script does NOT launch any Macro searches. It only demonstrates
the orientation recommendation.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.frontier.macro_orientation import (
    choose_macro_orientation,
    print_orientation_report,
)


def main():
    print("=" * 60)
    print("MACRO ORIENTATION SELECTION — REPRESENTATIVE EXAMPLES")
    print("=" * 60)
    print()

    examples = [
        (4, 5, 6),    # Known prime minimal box (Hamlyn 1993)
        (4, 8, 20),   # Known tileable box (Postl 1998)
        (4, 8, 130),  # Known prime box (Shirakawa 2014)
        (4, 9, 60),   # Known prime box (Shirakawa 2014)
        (4, 10, 10),  # Known prime box (Postl 1998)
        (5, 6, 29),   # Known prime box (Shirakawa 2014)
        (5, 9, 12),   # Known prime box (Shirakawa 2014)
        (7, 8, 30),   # Known prime box (Shirakawa 2014)
    ]

    for dims in examples:
        print("─" * 50)
        print_orientation_report(dims)

    # Summary table
    print("=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print()
    header = f"{'Box':12s} {'Best cross-section':20s} {'Area':6s} {'Thickness':10s} {'Warning'}"
    print(header)
    print("-" * len(header))
    for dims in examples:
        best = choose_macro_orientation(dims, recommend=True)
        a, b = best.cross_section_dims
        from tools.frontier.macro_orientation import area_warning_level
        warning = area_warning_level(best.cross_section_area)
        box_str = f"{dims[0]}×{dims[1]}×{dims[2]}"
        cross_str = f"{a}×{b}"
        print(f"{box_str:12s} {cross_str:20s} {best.cross_section_area:6d} "
              f"{best.thickness:10d} {warning}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())