from catalogues.base import Box, Catalogue


RAW_PRIMES = {
    # 4x10 family
    Box(4,10,50),
    Box(4,10,55),
    Box(4,10,60),
    Box(4,10,65),
    Box(4,10,70),
    Box(4,10,75),
    Box(4,10,80),
    Box(4,10,85),
    Box(4,10,90),
    Box(4,10,95),

    Box(4,11,50),

    Box(4,14,25),

    Box(4,16,25),
    Box(4,17,25),
    Box(4,18,25),
    Box(4,19,25),

    Box(4,20,20),
    Box(4,20,25),

    Box(4,21,25),
    Box(4,22,25),

    # 5x8 family
    Box(5,8,20),
    Box(5,8,35),
    Box(5,8,45),
    Box(5,8,50),

    # 5x9 family
    Box(5,9,15),
    Box(5,9,25),
    Box(5,9,35),

    # 5x10 family
    Box(5,10,33),
    Box(5,10,36),
    Box(5,10,37),

    # 5x12+
    Box(5,12,20),
    Box(5,12,25),

    Box(5,13,25),

    Box(5,14,20),
    Box(5,14,25),

    Box(5,15,17),
    Box(5,15,19),

    Box(5,16,25),
    Box(5,17,20),

    # 6x*
    Box(6,6,25),
    Box(6,7,25),
    Box(6,8,25),
    Box(6,9,25),

    Box(6,10,10),  # prime minimal
    Box(6,10,15),

    Box(6,11,25),
    Box(6,15,15),

    # 7x*
    Box(7,8,25),
    Box(7,9,25),
    Box(7,10,10),
    Box(7,10,15),
    Box(7,11,25),

    # 8x*
    Box(8,8,25),
    Box(8,9,25),
    Box(8,10,10),
    Box(8,10,15),
    Box(8,15,15),

    # 9x*
    Box(9,10,10),

    # 10x*
    Box(10,10,10),
    Box(10,10,11),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(5, 9, 15)

# Smallest RAW_PRIME with all three dimensions even.
MINIMAL_EVEN = Box(6, 10, 10)

SEARCHED_NO_SOLUTION = {
    # 6x6x10: no tiling -- complete SAT decision (CaDiCaL, UNSAT in 287 s)
    # with an independently verified DRAT proof (drat-trim s VERIFIED 455 s;
    # lrat-check c VERIFIED 25 s on the emitted LRAT). 2026-08-29.
    # See docs/frontier/z_piece/z_6610_unsat_certificate.md
    Box(6, 6, 10),
    # 4x11x15: no tiling -- native CaDiCaL 1.5.3 UNSAT in 2117.5 s on the
    # canonical deduplicated 265000-clause plain ALO+AMO encoding (4096
    # placements), binary-DRAT proof (3.61 GB, hash-pinned) independently
    # verified by drat-trim (s VERIFIED, 2458.2 s, 647,547,908 resolution
    # steps); standalone semantic audit ALL CHECKS PASSED. 2026-09-04.
    # See docs/frontier/z_piece/z_41115_certificate/
    Box(4, 11, 15),
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


# Published solvable, non-prime boxes: Shirakawa Z page rows
# carrying solution count '1+' with NO prime marker.
# Source: https://puzzlewillbeplayed.com/Shirakawa/Z.html
# (3D section, page last updated Feb 18, 2015).
# Each row self-checks as pieces * 5 == a*b*c.
# Proposed 2026-08-28; evidence:
#   docs/frontier/z_piece/z_catalogue_promotion_patch.md
#   docs/frontier/z_piece/z_promotion_evidence_package.md
#   docs/frontier/z_piece/z_promotion_semantics_audit.md
PUBLISHED_SOLUTIONS = {
    # 3x23
    Box(3, 23, 150),  # 1+ 2014 Shirakawa
    Box(3, 23, 175),  # 1+ 2014 Shirakawa
    Box(3, 23, 200),  # 1+ 2014 Shirakawa
    Box(3, 23, 225),  # 1+ 2014 Shirakawa
    Box(3, 23, 250),  # 1+ 2014 Shirakawa
    Box(3, 23, 275),  # 1+ 2014 Shirakawa
    # 3x24
    Box(3, 24, 300),  # 1+ 2014 Shirakawa
    # 3x25
    Box(3, 25, 63),  # 1+ 2014 Shirakawa
    Box(3, 25, 74),  # 1+ 2014 Shirakawa
    # 4x12
    Box(4, 12, 50),  # 1+ 2013 Shirakawa
    Box(4, 12, 75),  # 1+ 2013 Shirakawa
    # 4x13
    Box(4, 13, 50),  # 1+ 2013 Shirakawa
    Box(4, 13, 75),  # 1+ 2013 Shirakawa
    # 4x15
    Box(4, 15, 30),  # 1+ 2013 Shirakawa
    Box(4, 15, 35),  # 1+ 2013 Shirakawa
    Box(4, 15, 40),  # 1+ 2013 Shirakawa
    Box(4, 15, 45),  # 1+ 2013 Shirakawa
    Box(4, 15, 50),  # 1+ 2013 Shirakawa
    Box(4, 15, 55),  # 1+ 2013 Shirakawa
    # 4x20
    Box(4, 20, 30),  # 1+ 2013 Shirakawa
    Box(4, 20, 35),  # 1+ 2013 Shirakawa
    # 4x24
    Box(4, 24, 25),  # 1+ 2015 Shirakawa
    # 4x25
    Box(4, 25, 25),  # 1+ 2015 Shirakawa
    Box(4, 25, 26),  # 1+ 2015 Shirakawa
    # 5x10
    Box(5, 10, 39),  # 1+ 2013 Shirakawa
    Box(5, 10, 40),  # 1+ 2013 Shirakawa
    Box(5, 10, 41),  # 1+ 2013 Shirakawa
    Box(5, 10, 42),  # 1+ 2013 Shirakawa
    Box(5, 10, 43),  # 1+ 2013 Shirakawa
    Box(5, 10, 44),  # 1+ 2013 Shirakawa
    Box(5, 10, 45),  # 1+ 2013 Shirakawa
    Box(5, 10, 46),  # 1+ 2013 Shirakawa
    Box(5, 10, 47),  # 1+ 2013 Shirakawa
    Box(5, 10, 48),  # 1+ 2013 Shirakawa
    Box(5, 10, 49),  # 1+ 2013 Shirakawa
    Box(5, 10, 50),  # 1+ 2013 Shirakawa
    Box(5, 10, 51),  # 1+ 2013 Shirakawa
    Box(5, 10, 52),  # 1+ 2013 Shirakawa
    Box(5, 10, 53),  # 1+ 2013 Shirakawa
    Box(5, 10, 54),  # 1+ 2013 Shirakawa
    Box(5, 10, 55),  # 1+ 2013 Shirakawa
    Box(5, 10, 56),  # 1+ 2013 Shirakawa
    Box(5, 10, 57),  # 1+ 2013 Shirakawa
    Box(5, 10, 58),  # 1+ 2013 Shirakawa
    Box(5, 10, 59),  # 1+ 2013 Shirakawa
    Box(5, 10, 60),  # 1+ 2013 Shirakawa
    Box(5, 10, 61),  # 1+ 2013 Shirakawa
    Box(5, 10, 62),  # 1+ 2013 Shirakawa
    Box(5, 10, 63),  # 1+ 2013 Shirakawa
    Box(5, 10, 64),  # 1+ 2013 Shirakawa
    Box(5, 10, 65),  # 1+ 2013 Shirakawa
    Box(5, 10, 67),  # 1+ 2013 Shirakawa
    Box(5, 10, 68),  # 1+ 2013 Shirakawa
    Box(5, 10, 71),  # 1+ 2013 Shirakawa
    # 5x11
    Box(5, 11, 40),  # 1+ 2013 Shirakawa
    Box(5, 11, 60),  # 1+ 2013 Shirakawa
    Box(5, 11, 65),  # 1+ 2014 Shirakawa
    Box(5, 11, 70),  # 1+ 2013 Shirakawa
    Box(5, 11, 75),  # 1+ 2014 Shirakawa
    Box(5, 11, 85),  # 1+ 2014 Shirakawa
    Box(5, 11, 90),  # 1+ 2013 Shirakawa
    Box(5, 11, 95),  # 1+ 2014 Shirakawa
    # 5x12
    Box(5, 12, 30),  # 1+ 2013 Shirakawa
    Box(5, 12, 35),  # 1+ 2013 Shirakawa
    # 5x13
    Box(5, 13, 30),  # 1+ 2013 Shirakawa
    Box(5, 13, 35),  # 1+ 2014 Shirakawa
    Box(5, 13, 40),  # 1+ 2013 Shirakawa
    Box(5, 13, 45),  # 1+ 2014 Shirakawa
    # 5x14
    Box(5, 14, 30),  # 1+ 2013 Shirakawa
    Box(5, 14, 35),  # 1+ 2013 Shirakawa
    # 5x15
    Box(5, 15, 20),  # 1+ 2014 Shirakawa
    Box(5, 15, 21),  # 1+ 2014 Shirakawa
    Box(5, 15, 22),  # 1+ 2013 Shirakawa
    Box(5, 15, 23),  # 1+ 2014 Shirakawa
    Box(5, 15, 24),  # 1+ 2013 Shirakawa
    Box(5, 15, 25),  # 1+ 2014 Shirakawa
    # 5x16
    Box(5, 16, 30),  # 1+ 2014 Shirakawa
}

class ZCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 2:
            return "published_impossible"

        #
        # Published impossible families
        #

        if a == 3 and 3 <= b <= 22:
            return "published_impossible"

        if a == 4 and 4 <= b <= 9:
            return "published_impossible"

        if (a, b) == (4, 10) and 10 <= c <= 45:
            return "published_impossible"

        #
        # 5x10x[10-18]: 0 -- Shirakawa 2013 (explicit zero block)
        #
        if (a, b) == (5, 10) and 10 <= c <= 18:
            return "published_impossible"

        #
        # 3x23x50: s:0 -- Shirakawa 2013 (per-box semigroup zero)
        #
        if box == Box(3, 23, 50):
            return "published_impossible"

        if a == 5 and b in {5, 6, 7}:
            return "published_impossible"

        if a == 7 and b == 7:
            return "published_impossible"

        #
        # Published individual impossible boxes
        #

        if box in {
            Box(4,10,10),
            Box(4,10,15),
            Box(4,10,20),
            Box(4,10,25),
            Box(4,10,30),
            Box(4,10,35),
            Box(4,10,40),
            Box(4,10,45),

            Box(4,11,25),

            Box(5,8,10),
            Box(5,8,15),
            Box(5,8,25),
            Box(5,8,30),

            Box(5,9,10),
            Box(5,9,20),
        }:
            return "published_impossible"

        #
        # Exhaustively searched, no solution (complete SAT decision,
        # independently verified DRAT/LRAT certificate):
        # docs/frontier/z_piece/z_6610_unsat_certificate.md
        #
        if box in SEARCHED_NO_SOLUTION:
            return "SEARCHED_NO_SOLUTION"

        return None


Z_CATALOGUE = ZCatalogue(
    catalogue_name="Z",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=PUBLISHED_SOLUTIONS,
)
