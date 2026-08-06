from catalogues.base import Box, Catalogue

#
# S piece (pentomino 5/15).
#
# Ground truth: https://puzzlewillbeplayed.com/Shirakawa/5-15.html
# (lossless transcription: shirakawa/S.md)
#
# The page states "4D+ Complete." -- the 3D section below is the one-sided
# classification.  The separate "3D 2-sided" section is OUT OF SCOPE for this
# catalogue and is intentionally not encoded.  In particular:
#   3x4x15, 3x5x6, 3x5x9, 3x7x15  appear ONLY in the 2-sided section, so the
#   one-sided 3x[3-12]xN row (0 solutions) applies to them.
#
# Correction note on the page:
#   "Sillke says 4x10x14 and 4x9x15 are possible, but they are impossible.
#    The solutions of 4x10x14, 4x9x15 and 5x7x30 are wrong.
#    The right side part '2' needs the 22th pentacubes."
#   => 4x9x15, 4x10x14 and 5x7x30 are treated as impossible.
#

RAW_PRIMES = {
    #
    # 4x5
    #
    Box(4, 5, 6),             # 1 solution, prime, minimal -- Hamlyn 1993
                              # (listed in the main 3D section; also appears
                              #  in the 2-sided section, but this is the
                              #  one-sided minimal prime)

    #
    # 4x8
    #
    Box(4, 8, 20),            # 1+ prime -- Postl 1998
    Box(4, 8, 130),           # 1+ prime -- Shirakawa 2014

    #
    # 4x9
    #
    Box(4, 9, 60),            # 1+ prime -- Shirakawa 2014
    Box(4, 9, 75),            # 1+ prime -- Shirakawa 2014
    Box(4, 9, 90),            # 1+ prime -- Shirakawa 2014
    Box(4, 9, 105),           # 1+ prime -- Shirakawa 2014

    #
    # 4x10
    #
    Box(4, 10, 10),           # 1+ prime -- Postl 1998

    #
    # 4x13 / 4x14
    #
    Box(4, 13, 30),           # 1+ prime -- Shirakawa 2014
    Box(4, 14, 30),           # 1+ prime -- Shirakawa 2014

    #
    # 5x6
    #
    Box(5, 6, 29),            # 1+ prime -- Shirakawa 2014
    Box(5, 6, 46),            # 1+ prime -- Shirakawa 2014
    Box(5, 6, 47),            # 1+ prime -- Shirakawa 2014

    #
    # 5x7
    #
    Box(5, 7, 24),            # 1+ prime -- Sillke 1998
    Box(5, 7, 36),            # 1+ prime -- Sillke 1998
    Box(5, 7, 42),            # 1+ prime -- Sillke 1998
    # NB: 5x7x30 is listed on the page as 1+ prime (Sillke 1998) but the
    #     correction note says that solution is wrong -> impossible.

    #
    # 5x9
    #
    Box(5, 9, 12),            # 1+ prime -- Shirakawa 2014
    Box(5, 9, 15),            # 1+ prime -- Shirakawa 2014
    Box(5, 9, 18),            # 1+ prime -- Shirakawa 2014
    Box(5, 9, 21),            # 1+ prime -- Shirakawa 2014

    #
    # 5x10
    #
    Box(5, 10, 18),           # 1+ prime -- Shirakawa 2014

    #
    # 6x6
    #
    Box(6, 6, 15),            # 1+ prime -- Postl 1998
    Box(6, 6, 20),            # 1+ prime -- Postl 1998
    Box(6, 6, 25),            # 1+ prime -- Postl 1998

    #
    # 6x7
    #
    Box(6, 7, 10),            # 1+ prime -- Postl 1998
    Box(6, 7, 15),            # 1+ prime -- Postl 1998

    #
    # 6x9 / 6x10
    #
    Box(6, 9, 10),            # 1+ prime -- Shirakawa 2014
    Box(6, 9, 15),            # 1+ prime -- Shirakawa 2014
    Box(6, 10, 10),           # 1+ prime -- Shirakawa 2014

    #
    # 7x8 / 8x8
    #
    Box(7, 8, 30),            # 1+ prime -- Shirakawa 2014
    Box(8, 8, 10),            # 1+ prime -- Shirakawa 2014
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
    # Empirically searched without finding a solution; no explicit page entry.
    Box(4, 5, 7),

    # Empirically searched without finding a solution; related to the
    # impossible 4x10x14 (stacking 4x10x14 twice along the 8 dimension).
    Box(8, 10, 14),
}

PUBLISHED_SOLUTIONS = {
    # Page "1+" entries: solvable boxes that are NOT prime (no prime marker).
    Box(3, 26, 180),   # 1+ -- Shirakawa 2014
    Box(4, 15, 45),    # 1+ -- Shirakawa 2014
    Box(8, 9, 15),     # 1+ -- Shirakawa 2014
}

ROW_FAMILIES = {}

WIDTH_SPLITS = {}


class SCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        #
        # 2xMxN: 0
        #   2x[2-20]xN -- Sillke 1993
        #   2xMxN     -- Shirakawa 2014
        #
        if a == 2:
            return "published_impossible"

        #
        # 3x[3-12]xN: 0 -- Sillke 1993
        # 3x13xN: 0    -- Shirakawa 2014
        #
        # The 3x4x15 / 3x5x6 / 3x5x9 / 3x7x15 boxes that were formerly in this
        # catalogue appear only in the page's "3D 2-sided" section, so the
        # one-sided 3x[3-12]xN row is indeed 0.
        #
        if a == 3 and 3 <= b <= 13:
            return "published_impossible"

        #
        # 4x4xN: 0 -- Sillke 1993
        # 4x7xN: 0 -- Sillke 1993
        #
        if a == 4 and b in {4, 7}:
            return "published_impossible"

        #
        # 4x8x{10,30,50,70,90,110}: 0 -- Shirakawa 2014
        #
        if a == 4 and b == 8 and c in {10, 30, 50, 70, 90, 110}:
            return "published_impossible"

        #
        # 4x9x{10,20,25,30,35,40,45}: 0 -- Shirakawa 2014
        # (4x9x15 handled below with the correction-note boxes)
        #
        if a == 4 and b == 9 and c in {10, 20, 25, 30, 35, 40, 45}:
            return "published_impossible"

        if a == 4 and b == 5 and c == 5:
            return "published_impossible"

        #
        # Correction note (page): Sillke's solutions for 4x9x15, 4x10x14 and
        # 5x7x30 are wrong; the boxes are impossible.
        #
        if a == 4 and b == 9 and c == 15:
            return "published_impossible"
        if a == 4 and b == 10 and c == 14:
            return "published_impossible"
        if a == 5 and b == 7 and c == 30:
            return "published_impossible"

        #
        # 5x5xN: 0 -- Sillke 1993
        #
        if a == 5 and b == 5:
            return "published_impossible"

        #
        # 5x6xN impossible families (page 3D section):
        #   [6-7], [9-11], [13-15] -- Sillke 1993
        #   [17-19], [21-23], [25-28], [30-31], [34-35], [38-39], [42-43]
        #     -- Shirakawa 2014
        # Primes in this family: 5x6x29, 5x6x46, 5x6x47.
        #
        if a == 5 and b == 6 and c in {
            6, 7, 9, 10, 11, 13, 14, 15,
            17, 18, 19, 21, 22, 23, 25, 26, 27, 28,
            30, 31, 34, 35, 38, 39, 42, 43,
        }:
            return "published_impossible"

        #
        # 5x7x12: 0, 5x7x18: 0 -- Sillke 1993
        #
        if a == 5 and b == 7 and c in {12, 18}:
            return "published_impossible"

        #
        # 5x9x9: 0 -- Shirakawa 2014
        #
        if a == 5 and b == 9 and c == 9:
            return "published_impossible"

        #
        # 6x6x10: 0 -- Postl 1998
        #
        if a == 6 and b == 6 and c == 10:
            return "published_impossible"

        #
        # odd-width theorem
        #
        if a % 2 == 1 and (b * c) % 3 != 0:
            return "published_impossible, odd-width theorem"
        if b % 2 == 1 and (a * c) % 3 != 0:
            return "published_impossible, odd-width theorem"
        if c % 2 == 1 and (a * b) % 3 != 0:
            return "published_impossible, odd-width theorem"

        if box in SEARCHED_NO_SOLUTION:
            return "SEARCHED_NO_SOLUTION"

        return None


S_CATALOGUE = SCatalogue(
    catalogue_name="21",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=PUBLISHED_SOLUTIONS,
)
