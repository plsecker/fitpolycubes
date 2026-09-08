#!/usr/bin/env python3
"""
Macro orientation selection helper.

For a rectangular target box X × Y × Z, evaluates the three possible
choices of longitudinal axis and ranks them by cross-section area.

The default recommendation is the orientation with the smallest
cross-section area, based on the empirical observation that Macro
state-space complexity grows rapidly with cross-section area.

Usage:
    from tools.frontier.macro_orientation import choose_macro_orientation

    orientations = choose_macro_orientation((4, 5, 6))
    # Returns sorted list of candidate orientations

    best = choose_macro_orientation((4, 5, 6), recommend=True)
    # Returns the single best orientation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Sequence, Tuple

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

OrientationAxis = int  # 0, 1, or 2 (index into box dimensions)


@dataclass(order=True, frozen=True)
class MacroOrientation:
    """A candidate Macro slicing orientation for a rectangular box."""

    # Sorted for deterministic ordering: area first, then thickness, then dims
    cross_section_area: int = field(compare=True)
    thickness: int = field(compare=True)
    longitudinal_axis: OrientationAxis = field(compare=False)
    cross_section_dims: Tuple[int, int] = field(compare=False)
    box_dims: Tuple[int, int, int] = field(compare=False)

    def __repr__(self) -> str:
        a, b = self.cross_section_dims
        return (
            f"MacroOrientation("
            f"cross={a}×{b} area={self.cross_section_area}, "
            f"thickness={self.thickness}, "
            f"axis={self.longitudinal_axis})"
        )

    def describe(self) -> str:
        """Human-readable description."""
        a, b = self.cross_section_dims
        axis_name = ["X", "Y", "Z"][self.longitudinal_axis]
        return (
            f"Longitudinal axis {axis_name} (dim={self.thickness}): "
            f"cross-section {a}×{b} (area={self.cross_section_area})"
        )


# ---------------------------------------------------------------------------
# Heuristic warning levels
# ---------------------------------------------------------------------------

# Empirical measurements from the S-pentacube 4×5×6 box:
#   area 20  ->   1,538 states  (complete, 0.46 s)
#   area 24  ->  31,738 states  (complete, 1.63 s)
#   area 30  -> >5,000,000 states (cap hit at 5M, 229 s)
#
# These are empirical data points, not a proven scaling law.
# The warning levels below are conservative guidelines based on this data.

_AREA_THRESHOLDS = [
    ("small", 0, 20, "likely tractable (seconds)"),
    ("moderate", 21, 24, "tractable (seconds to minutes)"),
    ("large", 25, 28, "benchmark first; expect minutes"),
    ("very large", 29, 30, "expect rapid growth; may not complete"),
    ("extreme", 31, float("inf"), "likely infeasible for complete closure"),
]


def area_warning_level(area: int) -> str:
    """Return a heuristic warning level for a given cross-section area.

    Based on empirical measurements from S-pentacube Macro analysis.
    This is a practical heuristic, not a theorem.
    """
    for label, lo, hi, _ in _AREA_THRESHOLDS:
        if lo <= area <= hi:
            return label
    return "unknown"


def area_description(area: int) -> str:
    """Return a human-readable description of the expected tractability."""
    for label, lo, hi, desc in _AREA_THRESHOLDS:
        if lo <= area <= hi:
            return desc
    return "unknown"


# ---------------------------------------------------------------------------
# Core helper
# ---------------------------------------------------------------------------


def enumerate_orientations(box_dims: Tuple[int, int, int]) -> Iterator[MacroOrientation]:
    """Yield the three candidate Macro orientations for a box.

    Each orientation chooses a different axis as the longitudinal
    (thickness) direction. The cross-section is the product of the
    other two dimensions.

    Args:
        box_dims: (X, Y, Z) dimensions of the rectangular box.

    Yields:
        Three MacroOrientation instances, one per axis choice.
    """
    X, Y, Z = box_dims

    # Axis 0 (X): longitudinal = X, cross-section = Y × Z
    yield MacroOrientation(
        cross_section_area=Y * Z,
        thickness=X,
        longitudinal_axis=0,
        cross_section_dims=(Y, Z) if Y <= Z else (Z, Y),
        box_dims=box_dims,
    )

    # Axis 1 (Y): longitudinal = Y, cross-section = X × Z
    yield MacroOrientation(
        cross_section_area=X * Z,
        thickness=Y,
        longitudinal_axis=1,
        cross_section_dims=(X, Z) if X <= Z else (Z, X),
        box_dims=box_dims,
    )

    # Axis 2 (Z): longitudinal = Z, cross-section = X × Y
    yield MacroOrientation(
        cross_section_area=X * Y,
        thickness=Z,
        longitudinal_axis=2,
        cross_section_dims=(X, Y) if X <= Y else (Y, X),
        box_dims=box_dims,
    )


def choose_macro_orientation(
    box_dims: Tuple[int, int, int],
    recommend: bool = False,
) -> list[MacroOrientation] | MacroOrientation:
    """Evaluate and rank Macro orientations for a rectangular box.

    Orientations are sorted by increasing cross-section area (primary)
    and increasing thickness (secondary, for ties).

    Args:
        box_dims: (X, Y, Z) dimensions of the rectangular box.
        recommend: If True, return only the single best orientation.
                   If False (default), return the full sorted list.

    Returns:
        If recommend=False: list of MacroOrientation sorted by
            increasing cross-section area (best first).
        If recommend=True: the single best MacroOrientation.

    Examples:
        >>> orientations = choose_macro_orientation((4, 5, 6))
        >>> len(orientations)
        3
        >>> orientations[0].cross_section_area
        20
        >>> orientations[0].thickness
        6

        >>> best = choose_macro_orientation((4, 5, 6), recommend=True)
        >>> best.cross_section_area
        20
        >>> best.thickness
        6
    """
    orientations = sorted(enumerate_orientations(box_dims))

    if recommend:
        return orientations[0]

    return orientations


# ---------------------------------------------------------------------------
# Convenience: pretty-print
# ---------------------------------------------------------------------------


def print_orientation_report(box_dims: Tuple[int, int, int]) -> None:
    """Print a human-readable orientation report for a box."""
    X, Y, Z = box_dims
    print(f"Box: {X}×{Y}×{Z}")
    print(f"Volume: {X * Y * Z}")
    print()

    orientations = choose_macro_orientation(box_dims)

    for i, o in enumerate(orientations):
        rank = "BEST" if i == 0 else f"rank {i + 1}"
        a, b = o.cross_section_dims
        warning = area_warning_level(o.cross_section_area)
        desc = area_description(o.cross_section_area)
        print(f"  {rank}: {o.describe()}")
        print(f"       Warning level: {warning} — {desc}")
        print()

    best = orientations[0]
    a, b = best.cross_section_dims
    print(f"Recommendation: cross-section {a}×{b} (area={best.cross_section_area}), "
          f"thickness={best.thickness}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point: print orientation report for a given box."""
    import sys

    if len(sys.argv) != 4:
        print("Usage: python3 -m tools.frontier.macro_orientation X Y Z")
        print("Example: python3 -m tools.frontier.macro_orientation 4 5 6")
        return 1

    try:
        X, Y, Z = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    except ValueError:
        print("Error: dimensions must be integers", file=sys.stderr)
        return 1

    if X <= 0 or Y <= 0 or Z <= 0:
        print("Error: dimensions must be positive", file=sys.stderr)
        return 1

    print_orientation_report((X, Y, Z))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())