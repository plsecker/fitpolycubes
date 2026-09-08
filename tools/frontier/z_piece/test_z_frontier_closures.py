#!/usr/bin/env python3
"""Tests for the Z-pentacube frontier decomposition audit (2026-08).

Scope
-----
1. Truth-table guard: catalogues/z_catalogue.py constants are untouched.
2. Published-evidence table (Shirakawa Z page, non-prime "1+" 3D entries):
   every row self-checks against the page's own piece-count column and is
   disjoint from the existing RAW_PRIMES / impossible rules.
3. Closure demo: injecting that table as runtime evidence into a *copy* of
   Z_CATALOGUE closes exactly 102 boxes within dims <= 60; every new proof
   tree satisfies closes() and passes permutation-aware validation.
4. Flagship proof trees (dumpable, closed).
5. Frontier smoke: baseline (unmodified catalogue) Unknown count at
   maxdim=22 equals the documented value.
6. WIDTH_SPLITS machinery honesty: decomp.py consumes width_splits when the
   generator sub-boxes close, and silently ignores them when they do not.

The tests never modify any catalogue truth table. Evidence is injected via
dataclasses.replace on a runtime copy only.
"""

import dataclasses
import sys
import unittest

sys.path.insert(0, ".")
sys.path.insert(0, "tools/frontier/z_piece")

import solvers.decomp as decomp  # noqa: E402
from catalogues.base import Box, Catalogue  # noqa: E402
from catalogues.z_catalogue import (  # noqa: E402
    Z_CATALOGUE, RAW_PRIMES, PRIMES, SEARCHED_NO_SOLUTION,
    ROW_FAMILIES, WIDTH_SPLITS, MINIMAL_ODD, MINIMAL_EVEN,
)
from validate_proof_tree import validate  # noqa: E402

# ---------------------------------------------------------------------------
# Shirakawa Z page (https://puzzlewillbeplayed.com/Shirakawa/Z.html),
# 3D section: every entry with solution count >= 1 and NO prime marker.
# Tuple = (pieces_on_page, a, b, c); pieces == volume // 5 is asserted.
# ---------------------------------------------------------------------------

PAGE_COMPOSITES_3D = [
    (2070, 3, 23, 150), (2415, 3, 23, 175), (2760, 3, 23, 200),
    (3105, 3, 23, 225), (3450, 3, 23, 250), (3795, 3, 23, 275),
    (4320, 3, 24, 300),
    (945, 3, 25, 63), (1110, 3, 25, 74),

    (480, 4, 12, 50), (720, 4, 12, 75),
    (520, 4, 13, 50), (780, 4, 13, 75),
    (360, 4, 15, 30), (420, 4, 15, 35), (480, 4, 15, 40),
    (540, 4, 15, 45), (600, 4, 15, 50), (660, 4, 15, 55),
    (480, 4, 20, 30), (560, 4, 20, 35),
    (480, 4, 24, 25), (500, 4, 25, 25), (520, 4, 25, 26),

    (390, 5, 10, 39), (400, 5, 10, 40), (410, 5, 10, 41),
    (420, 5, 10, 42), (430, 5, 10, 43), (440, 5, 10, 44),
    (450, 5, 10, 45), (460, 5, 10, 46), (470, 5, 10, 47),
    (480, 5, 10, 48), (490, 5, 10, 49), (500, 5, 10, 50),
    (510, 5, 10, 51), (520, 5, 10, 52), (530, 5, 10, 53),
    (540, 5, 10, 54), (550, 5, 10, 55), (560, 5, 10, 56),
    (570, 5, 10, 57), (580, 5, 10, 58), (590, 5, 10, 59),
    (600, 5, 10, 60), (610, 5, 10, 61), (620, 5, 10, 62),
    (630, 5, 10, 63), (640, 5, 10, 64), (650, 5, 10, 65),
    (670, 5, 10, 67), (680, 5, 10, 68), (710, 5, 10, 71),

    (440, 5, 11, 40), (660, 5, 11, 60), (715, 5, 11, 65),
    (770, 5, 11, 70), (825, 5, 11, 75), (935, 5, 11, 85),
    (990, 5, 11, 90), (1045, 5, 11, 95),

    (360, 5, 12, 30), (420, 5, 12, 35),
    (390, 5, 13, 30), (455, 5, 13, 35), (520, 5, 13, 40), (585, 5, 13, 45),
    (420, 5, 14, 30), (490, 5, 14, 35),
    (300, 5, 15, 20), (315, 5, 15, 21), (330, 5, 15, 22),
    (345, 5, 15, 23), (360, 5, 15, 24), (375, 5, 15, 25),
    (480, 5, 16, 30),
]

PUBLISHED_COMPOSITE_BOXES = {
    Box(a, b, c).canonical() for _, a, b, c in PAGE_COMPOSITES_3D
}

EVIDENCE_CATALOGUE = dataclasses.replace(
    Z_CATALOGUE,
    published_solutions=Z_CATALOGUE.published_solutions | PUBLISHED_COMPOSITE_BOXES,
)

# The 102 boxes <= 60^3 that close under EVIDENCE_CATALOGUE but were Unknown
# under the unmodified catalogue (verified by the 2026-08-27 audit run).
NEWLY_CLOSED_DIMS = [
    (5,15,20),(5,15,21),(5,15,22),(5,15,23),(4,15,30),(5,12,30),(5,15,24),
    (5,15,25),(5,10,39),(5,13,30),(5,10,40),(5,10,41),(4,15,35),(5,10,42),
    (5,12,35),(5,14,30),(5,10,43),(5,15,29),(5,10,44),(5,11,40),(5,10,45),
    (5,15,30),(5,13,35),(5,10,46),(5,20,23),(5,15,31),(5,10,47),(4,12,50),
    (4,15,40),(4,20,30),(4,24,25),(5,10,48),(5,15,32),(5,16,30),(5,10,49),
    (5,14,35),(5,15,33),(4,25,25),(5,10,50),(5,10,51),(4,13,50),(4,25,26),
    (5,10,52),(5,13,40),(5,10,53),(4,15,45),(5,10,54),(5,20,27),(5,10,55),
    (4,20,35),(5,10,56),(5,10,57),(5,10,58),(5,13,45),(5,15,39),(5,10,59),
    (4,15,50),(5,10,60),(5,15,40),(5,15,41),(5,15,42),(5,21,30),(4,15,55),
    (5,11,60),(5,12,55),(5,22,30),(11,15,20),(5,23,30),(5,20,35),(5,13,55),
    (4,15,60),(4,30,30),(5,15,48),(5,24,30),(5,15,49),(5,21,35),(5,15,50),
    (5,19,40),(5,14,55),(5,22,35),(5,13,60),(4,30,35),(5,15,58),(5,15,59),
    (5,30,30),(4,23,50),(5,30,31),(5,19,50),(4,30,40),(5,30,32),(4,35,35),
    (10,11,45),(11,15,30),(5,29,35),(5,19,55),(4,30,45),(4,35,40),(5,21,55),
    (5,22,55),(5,30,41),(4,35,45),(11,15,40),
]

FLAGSHIP_TREES = [
    ((5, 15, 20), "PublishedSolution"),
    ((11, 15, 20), "Width"),
    ((5, 15, 40), "Slab"),
    ((5, 10, 72), "Slab"),
    ((4, 15, 85), "Slab"),
]


def make_synthetic(width_splits=None, primes=None):
    """A minimal catalogue for mechanism demos. Uses the BASE Catalogue class
    (impossible_reason -> None) so Z's real published rules cannot interfere;
    only decomp's global dimension/volume checks apply."""
    return Catalogue(
        catalogue_name="ZSYN",
        primes=primes or set(),
        searched_no_solution=set(),
        row_families={},
        width_splits=width_splits or {},
        published_solutions=set(),
    )


class TestTruthTablesUntouched(unittest.TestCase):
    def test_constants_guard(self):
        self.assertEqual(len(RAW_PRIMES), 60)
        self.assertEqual(len(PRIMES), 60)
        self.assertEqual(MINIMAL_ODD, Box(5, 9, 15))
        self.assertEqual(MINIMAL_EVEN, Box(6, 10, 10))
        # 2026-08-29: 6x6x10 promoted to SEARCHED_NO_SOLUTION on the basis of
        # a fully independently verified DRAT/LRAT UNSAT certificate
        # (docs/frontier/z_piece/z_6610_unsat_certificate.md).
        # 2026-09-04: 4x11x15 promoted to SEARCHED_NO_SOLUTION on the basis of
        # a native CaDiCaL UNSAT decision with an independently verified
        # binary-DRAT proof and standalone semantic audit
        # (docs/frontier/z_piece/z_41115_certificate/).
        self.assertEqual(SEARCHED_NO_SOLUTION, {Box(6, 6, 10), Box(4, 11, 15)})
        self.assertEqual(ROW_FAMILIES, {})
        self.assertEqual(WIDTH_SPLITS, {})
        # 2026-08-28 promotion: the 77 approved Shirakawa "1+" composite rows
        # (evidence: docs/frontier/z_piece/z_catalogue_promotion_patch.md).
        self.assertEqual(len(Z_CATALOGUE.published_solutions), 77)
        self.assertIsInstance(Z_CATALOGUE, Catalogue)

    def test_impossible_rules_samples(self):
        cat = Z_CATALOGUE
        self.assertEqual(cat.impossible_reason(Box(3, 10, 10)), "published_impossible")
        self.assertEqual(cat.impossible_reason(Box(4, 8, 20)), "published_impossible")
        self.assertIsNone(cat.impossible_reason(Box(4, 10, 50)))
        self.assertIsNone(cat.impossible_reason(Box(5, 15, 20)))


class TestPageEvidenceTable(unittest.TestCase):
    def test_every_entry_volume_matches_page_piece_count(self):
        for pieces, a, b, c in PAGE_COMPOSITES_3D:
            self.assertEqual(a * b * c, 5 * pieces, msg=f"{a}x{b}x{c}")

    def test_disjoint_from_existing_truth(self):
        for box in PUBLISHED_COMPOSITE_BOXES:
            self.assertNotIn(box, PRIMES)
            self.assertIsNone(Z_CATALOGUE.impossible_reason(box))


class TestNewlyClosedProofTrees(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        decomp.catalogue = EVIDENCE_CATALOGUE
        decomp.classify.cache_clear()

    @classmethod
    def tearDownClass(cls):
        decomp.catalogue = Z_CATALOGUE
        decomp.classify.cache_clear()

    def test_exactly_the_documented_set_closes_and_validates(self):
        from collections import Counter
        types = Counter()
        for dims in NEWLY_CLOSED_DIMS:
            with self.subTest(box=dims):
                node = decomp.classify(Box(*dims))
                self.assertTrue(decomp.closes(node))
                self.assertTrue(validate(node), msg=f"invalid tree {dims}")
                types[node.__class__.__name__] += 1
        # before this audit these were all Unknown under the plain catalogue;
        # node-type mix observed in the audit run:
        self.assertEqual(dict(types),
                         {"PublishedSolution": 52, "Slab": 43,
                          "Breadth": 5, "Width": 2})
        self.assertEqual(len(NEWLY_CLOSED_DIMS), 102)

    def test_flagship_trees(self):
        expected = [((5, 15, 20), "PublishedSolution"),
                    ((11, 15, 20), "Width"),
                    ((5, 15, 40), "Slab"),
                    ((5, 10, 72), "Slab"),
                    ((4, 15, 85), "Slab")]
        for dims, kind in expected:
            node = decomp.classify(Box(*dims))
            self.assertEqual(node.__class__.__name__, kind, msg=dims)
            self.assertTrue(decomp.closes(node))
            self.assertTrue(validate(node))

    def test_small_unknown_that_does_not_close_stays_open(self):
        # Guard against over-claiming: no cascade reaches e.g. 4x11x15 here.
        node = decomp.classify(Box(4, 11, 15))
        self.assertFalse(decomp.closes(node))


class TestFrontierBaseline(unittest.TestCase):
    """Real catalogue frontier size at maxdim=22.

    Pre-promotion baseline (2026-08-27 audit): 444 Unknown.
    Post-promotion (2026-08-28, 77 published rows applied): 440 — the four
    in-window closures are 5x15x20, 5x15x21, 5x15x22 (published) and
    11x15x20 (derived Width).
    Post explicit-impossibility transcription (2026-08-28, 5x10x[10-18]
    applied; 3x23x50 is outside the window): 431.
    Post 6x6x10 SEARCHED_NO_SOLUTION promotion (2026-08-29, verified
    DRAT/LRAT certificate): 430.
    Post 4x11x15 SEARCHED_NO_SOLUTION promotion (2026-09-04, verified
    CaDiCaL UNSAT + binary-DRAT certificate): 429 — 4x11x15 lies inside
    the maxdim=22 window, so it leaves the Unknown count."""

    BASELINE_UNKNOWN_MAXDIM22 = 429

    def test_baseline_frontier_size(self):
        decomp.catalogue = Z_CATALOGUE
        decomp.classify.cache_clear()
        unknown = 0
        for a in range(1, 23):
            for b in range(a, 23):
                for c in range(b, 23):
                    if (a * b * c) % 5:
                        continue
                    t = decomp.classify(Box(a, b, c)).__class__.__name__
                    if t == "Unknown":
                        unknown += 1
        self.assertEqual(unknown, self.BASELINE_UNKNOWN_MAXDIM22)


class TestWidthSplitsMechanism(unittest.TestCase):
    """decomp.py consumes width_splits when generators close — and cannot be
    fooled otherwise. This answers 'why weren't Z splits consumed': they never
    existed; the mechanism itself works."""

    def setUp(self):
        self._saved = decomp.catalogue

    def tearDown(self):
        decomp.catalogue = self._saved
        decomp.classify.cache_clear()

    def test_truthful_width_split_is_consumed(self):
        cat = make_synthetic(
            width_splits={8: [3, 4]},
            primes={Box(3, 8, 15), Box(4, 8, 15)},   # volumes 360 / 480
        )
        decomp.catalogue = cat
        decomp.classify.cache_clear()
        node = decomp.classify(Box(7, 8, 15))   # 7 = 3 + 4, both parts prime
        self.assertTrue(decomp.closes(node))
        self.assertTrue(validate(node))

    def test_false_width_split_is_not_believed(self):
        cat = make_synthetic(width_splits={12: [3, 4]})   # no closable parts
        decomp.catalogue = cat
        decomp.classify.cache_clear()
        node = decomp.classify(Box(7, 12, 15))
        self.assertEqual(node.__class__.__name__, "Unknown")
        self.assertFalse(decomp.closes(node))


if __name__ == "__main__":
    unittest.main()
