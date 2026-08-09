from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    #
    # First known solution (Postl, 1998)
    #
    Box(7, 8, 20),

    #
    # Marked "prime minimal?" by Shirakawa
    #
    Box(6, 11, 15),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# No RAW_PRIME with all three dimensions odd exists in the current catalogue.
MINIMAL_ODD = None

# No RAW_PRIME with all three dimensions even exists in the current catalogue.
MINIMAL_EVEN = None

SEARCHED_NO_SOLUTION = {
    #
    # Explicitly published impossible examples
    #
    Box(6, 8, 10),
    Box(6, 8, 15),
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


PUBLISHED_SOLUTIONS = {
    #
    # 4x19
    #
    Box(4, 19, 60),
    Box(4, 19, 70),
    Box(4, 19, 80),
    Box(4, 19, 90),
    Box(4, 19, 100),
    Box(4, 19, 110),

    #
    # 6x10
    #
    Box(6, 10, 25),
    Box(6, 10, 26),
    Box(6, 10, 27),
    Box(6, 10, 30),
    Box(6, 10, 32),
    Box(6, 10, 33),
    Box(6, 10, 34),
    Box(6, 10, 35),
    Box(6, 10, 36),
    Box(6, 10, 37),
    Box(6, 10, 38),
    Box(6, 10, 39),
    Box(6, 10, 40),
    Box(6, 10, 41),
    Box(6, 10, 42),
    Box(6, 10, 43),
    Box(6, 10, 44),
    Box(6, 10, 45),
    Box(6, 10, 46),
    Box(6, 10, 47),
    Box(6, 10, 48),
    Box(6, 10, 49),

    #
    # 6x11
    #
    Box(6, 11, 15),
    Box(6, 11, 20),

    #
    # 6x12
    #
    Box(6, 12, 25),
    Box(6, 12, 30),
    Box(6, 12, 35),
    Box(6, 12, 40),
    Box(6, 12, 45),

    #
    # 7x8
    #
    Box(7, 8, 20),
    Box(7, 8, 25),
    Box(7, 8, 30),
    Box(7, 8, 35),

    #
    # 7x10
    #
    Box(7, 10, 18),
    Box(7, 10, 20),
    Box(7, 10, 22),
    Box(7, 10, 24),
    Box(7, 10, 26),
    Box(7, 10, 28),
    Box(7, 10, 30),
    Box(7, 10, 32),
    Box(7, 10, 34),

    #
    # 8x8
    #
    Box(8, 8, 30),
    Box(8, 8, 35),
    Box(8, 8, 40),
    Box(8, 8, 45),
    Box(8, 8, 50),
    Box(8, 8, 55),

    #
    # 8x9
    #
    Box(8, 9, 20),
    Box(8, 9, 30),

    #
    # George Sicherman
    #
    Box(10, 10, 12),
}

class MCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # Degenerate
        #
        if a <= 1:
            return "published_impossible"

        #
        # Volume
        #
        if (a * b * c) % 5 != 0:
            return "published_impossible"

        #
        # No 2-wide or 3-wide boxes (Sillke)
        #
        if a <= 3:
            return "published_impossible"

        #
        # Checkerboard theorem
        #
        if (a * b * c) % 2 == 1:
            return "published_impossible"

        #
        # 4×N×{4..12}
        #
        if a == 4 and 4 <= b <= 12:
            return "published_impossible"

        #
        # 5×N×M
        #
        if a == 5:
            return "published_impossible"
        #
        # 6×6×N
        #
        if (a, b) == (6, 6):
            return "published_impossible"
        if (a, b) == (6, 7):
            return "published_impossible"

        #
        # Explicitly searched
        #
        if box in {
            Box(6, 8, 10),
            Box(6, 8, 15),
        }:
            return "published_impossible"

        return None


M_CATALOGUE = MCatalogue(
    catalogue_name="M",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=PUBLISHED_SOLUTIONS,
)
