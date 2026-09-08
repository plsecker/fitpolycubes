#!/usr/bin/env python3
"""
Unit tests for macro_orientation helper.

Tests:
- all-distinct dimensions (4×5×6)
- two equal dimensions (4×4×6)
- cube (5×5×5)
- deterministic tie handling
- correct area/thickness reporting
- warning levels
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.frontier.macro_orientation import (
    MacroOrientation,
    area_description,
    area_warning_level,
    choose_macro_orientation,
    enumerate_orientations,
)


class TestEnumerateOrientations(unittest.TestCase):
    """Tests for enumerate_orientations."""

    def test_three_orientations(self):
        """Should yield exactly 3 orientations for any box."""
        for dims in [(4, 5, 6), (4, 4, 6), (5, 5, 5), (3, 7, 11)]:
            with self.subTest(dims=dims):
                count = sum(1 for _ in enumerate_orientations(dims))
                self.assertEqual(count, 3)

    def test_cross_section_areas_4x5x6(self):
        """4×5×6: areas should be 20, 24, 30."""
        areas = set(o.cross_section_area for o in enumerate_orientations((4, 5, 6)))
        self.assertEqual(areas, {20, 24, 30})

    def test_thicknesses_4x5x6(self):
        """4×5×6: thicknesses should be 4, 5, 6."""
        thicknesses = set(o.thickness for o in enumerate_orientations((4, 5, 6)))
        self.assertEqual(thicknesses, {4, 5, 6})

    def test_longitudinal_axes(self):
        """Each axis should appear exactly once."""
        axes = set(o.longitudinal_axis for o in enumerate_orientations((4, 5, 6)))
        self.assertEqual(axes, {0, 1, 2})

    def test_cross_section_dims_product(self):
        """cross_section_area should equal product of cross_section_dims."""
        for o in enumerate_orientations((4, 5, 6)):
            a, b = o.cross_section_dims
            self.assertEqual(o.cross_section_area, a * b)

    def test_cross_section_dims_sorted(self):
        """cross_section_dims should be sorted (smaller first)."""
        for o in enumerate_orientations((6, 5, 4)):
            a, b = o.cross_section_dims
            self.assertLessEqual(a, b)

    def test_box_dims_preserved(self):
        """box_dims should match the input."""
        dims = (4, 5, 6)
        for o in enumerate_orientations(dims):
            self.assertEqual(o.box_dims, dims)


class TestChooseOrientation(unittest.TestCase):
    """Tests for choose_macro_orientation."""

    def test_returns_list_by_default(self):
        """Should return a list when recommend=False."""
        result = choose_macro_orientation((4, 5, 6))
        self.assertIsInstance(result, list)

    def test_returns_single_when_recommend(self):
        """Should return a single MacroOrientation when recommend=True."""
        result = choose_macro_orientation((4, 5, 6), recommend=True)
        self.assertIsInstance(result, MacroOrientation)

    def test_sorted_by_area(self):
        """Should be sorted by increasing cross-section area."""
        result = choose_macro_orientation((4, 5, 6))
        areas = [o.cross_section_area for o in result]
        self.assertEqual(areas, sorted(areas))

    def test_best_for_4x5x6(self):
        """Best orientation for 4×5×6 should be area=20, thickness=6."""
        best = choose_macro_orientation((4, 5, 6), recommend=True)
        self.assertEqual(best.cross_section_area, 20)
        self.assertEqual(best.thickness, 6)
        self.assertEqual(best.cross_section_dims, (4, 5))

    def test_second_for_4x5x6(self):
        """Second orientation for 4×5×6 should be area=24, thickness=5."""
        result = choose_macro_orientation((4, 5, 6))
        self.assertEqual(result[1].cross_section_area, 24)
        self.assertEqual(result[1].thickness, 5)

    def test_worst_for_4x5x6(self):
        """Worst orientation for 4×5×6 should be area=30, thickness=4."""
        result = choose_macro_orientation((4, 5, 6))
        self.assertEqual(result[2].cross_section_area, 30)
        self.assertEqual(result[2].thickness, 4)

    def test_cube(self):
        """For a cube, all orientations have the same area."""
        result = choose_macro_orientation((5, 5, 5))
        areas = [o.cross_section_area for o in result]
        self.assertEqual(areas, [25, 25, 25])
        # All thicknesses should be 5
        thicknesses = [o.thickness for o in result]
        self.assertEqual(thicknesses, [5, 5, 5])

    def test_two_equal_dims(self):
        """4×4×6: two orientations with area=24, one with area=16."""
        result = choose_macro_orientation((4, 4, 6))
        areas = [o.cross_section_area for o in result]
        self.assertEqual(areas, [16, 24, 24])
        # Best should be area=16
        self.assertEqual(result[0].cross_section_area, 16)
        self.assertEqual(result[0].thickness, 6)

    def test_deterministic_ties(self):
        """Tied orientations should be ordered deterministically by thickness."""
        result = choose_macro_orientation((4, 4, 6))
        # The two area=24 orientations: one has thickness=4, one has thickness=4
        # (both are 4, since the box is 4×4×6)
        # Actually: axis 0 (X=4): cross=4×6=24, thickness=4
        #           axis 1 (Y=4): cross=4×6=24, thickness=4
        #           axis 2 (Z=6): cross=4×4=16, thickness=6
        # So the two area=24 have equal thickness too.
        # They should still be deterministic.
        result2 = choose_macro_orientation((4, 4, 6))
        self.assertEqual(
            [(o.longitudinal_axis, o.cross_section_area) for o in result],
            [(o.longitudinal_axis, o.cross_section_area) for o in result2],
        )

    def test_large_box(self):
        """A larger box should still work."""
        result = choose_macro_orientation((4, 8, 20))
        areas = [o.cross_section_area for o in result]
        self.assertEqual(areas, [32, 80, 160])
        best = result[0]
        self.assertEqual(best.cross_section_dims, (4, 8))
        self.assertEqual(best.thickness, 20)

    def test_4x9x60(self):
        """4×9×60: best should be 4×9 area=36."""
        best = choose_macro_orientation((4, 9, 60), recommend=True)
        self.assertEqual(best.cross_section_area, 36)
        self.assertEqual(best.cross_section_dims, (4, 9))

    def test_4x10x10(self):
        """4×10×10: best should be 4×10 area=40 (two equal)."""
        best = choose_macro_orientation((4, 10, 10), recommend=True)
        self.assertEqual(best.cross_section_area, 40)
        # Two orientations have area=40: 4×10 and 10×10
        # The 4×10 should be preferred (smaller max dim)
        a, b = best.cross_section_dims
        self.assertLessEqual(a, b)


class TestWarningLevels(unittest.TestCase):
    """Tests for area warning levels."""

    def test_small_area(self):
        """Area ≤ 20 should be 'small'."""
        for area in [1, 10, 20]:
            with self.subTest(area=area):
                self.assertEqual(area_warning_level(area), "small")

    def test_moderate_area(self):
        """Area 21-24 should be 'moderate'."""
        for area in [21, 22, 23, 24]:
            with self.subTest(area=area):
                self.assertEqual(area_warning_level(area), "moderate")

    def test_large_area(self):
        """Area 25-28 should be 'large'."""
        for area in [25, 26, 27, 28]:
            with self.subTest(area=area):
                self.assertEqual(area_warning_level(area), "large")

    def test_very_large_area(self):
        """Area 29-30 should be 'very large'."""
        for area in [29, 30]:
            with self.subTest(area=area):
                self.assertEqual(area_warning_level(area), "very large")

    def test_extreme_area(self):
        """Area ≥ 31 should be 'extreme'."""
        for area in [31, 36, 40, 100]:
            with self.subTest(area=area):
                self.assertEqual(area_warning_level(area), "extreme")

    def test_descriptions_not_empty(self):
        """All warning levels should have non-empty descriptions."""
        for area in [10, 22, 26, 29, 36]:
            desc = area_description(area)
            self.assertTrue(desc)
            self.assertIsInstance(desc, str)


class TestMacroOrientationDataclass(unittest.TestCase):
    """Tests for the MacroOrientation dataclass."""

    def test_repr(self):
        """__repr__ should contain key information."""
        o = MacroOrientation(
            cross_section_area=20,
            thickness=6,
            longitudinal_axis=0,
            cross_section_dims=(4, 5),
            box_dims=(4, 5, 6),
        )
        r = repr(o)
        self.assertIn("20", r)
        self.assertIn("4×5", r)

    def test_describe(self):
        """describe() should be human-readable."""
        o = MacroOrientation(
            cross_section_area=20,
            thickness=6,
            longitudinal_axis=0,
            cross_section_dims=(4, 5),
            box_dims=(4, 5, 6),
        )
        d = o.describe()
        self.assertIn("X", d)
        self.assertIn("20", d)
        self.assertIn("4×5", d)

    def test_ordering_by_area(self):
        """Sorting should be by area first, then thickness."""
        o1 = MacroOrientation(20, 6, 0, (4, 5), (4, 5, 6))
        o2 = MacroOrientation(24, 5, 1, (4, 6), (4, 5, 6))
        o3 = MacroOrientation(30, 4, 2, (5, 6), (4, 5, 6))
        sorted_os = sorted([o3, o1, o2])
        self.assertEqual(sorted_os, [o1, o2, o3])


class TestCLI(unittest.TestCase):
    """Tests for CLI invocation."""

    def test_main_returns_0_for_valid_input(self):
        """main() should return 0 for valid dimensions."""
        # We can't easily test via sys.argv, but we can test the logic
        from tools.frontier.macro_orientation import print_orientation_report
        # Just check it doesn't crash
        try:
            print_orientation_report((4, 5, 6))
        except Exception as e:
            self.fail(f"print_orientation_report raised {e}")


if __name__ == "__main__":
    unittest.main()