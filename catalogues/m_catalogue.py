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
    Box(6, 8, 25),
    Box(7, 8, 20),
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
