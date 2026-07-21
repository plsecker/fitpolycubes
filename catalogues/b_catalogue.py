from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    #
    # 2x5
    #
    Box(2, 5, 5),
    Box(2, 5, 8),
    Box(2, 5, 11),
    Box(2, 5, 14),
    Box(2, 5, 17),
    Box(2, 5, 22),
    Box(2, 5, 27),
    Box(2, 5, 32),
    Box(2, 5, 37),

    #
    # 2x12
    #
    Box(2, 12, 20),
    Box(2, 12, 25),
    Box(2, 12, 30),
    Box(2, 12, 35),

    #
    # 3x9
    #
    Box(3, 9, 20),
    Box(3, 9, 25),
    Box(3, 9, 30),
    Box(3, 9, 35),

    #
    # 3x10
    #
    Box(3, 10, 12),
    Box(3, 10, 15),
    Box(3, 10, 18),
    Box(3, 10, 19),
    Box(3, 10, 20),
    Box(3, 10, 21),
    Box(3, 10, 22),
    Box(3, 10, 23),
    Box(3, 10, 25),
    Box(3, 10, 26),
    Box(3, 10, 28),
    Box(3, 10, 29),

    #
    # 3x12
    #
    Box(3, 12, 15),

    #
    # 3x13
    #
    Box(3, 13, 15),
    Box(3, 13, 20),
    Box(3, 13, 25),

    #
    # 3x14
    #
    Box(3, 14, 15),
    Box(3, 14, 20),
    Box(3, 14, 25),

    #
    # 3x15
    #
    Box(3, 15, 15),
    Box(3, 15, 16),
    Box(3, 15, 17),
    Box(3, 15, 18),
    Box(3, 15, 19),
    Box(3, 15, 21),

    #
    # 3x16
    #
    Box(3, 16, 20),
    Box(3, 16, 25),

    #
    # 3x17
    #
    Box(3, 17, 20),
    Box(3, 17, 25),

    #
    # 4x5
    #
    Box(4, 5, 12),
    Box(4, 5, 17),
    Box(4, 5, 22),
    Box(4, 5, 27),
    Box(4, 5, 32),
    Box(4, 5, 37),

    #
    # 4x6
    #
    Box(4, 6, 10),
    Box(4, 6, 15),

    #
    # 4x7
    #
    Box(4, 7, 10),
    Box(4, 7, 15),

    #
    # 4x9
    #
    Box(4, 9, 10),
    Box(4, 9, 15),

    #
    # 5x5
    #
    Box(5, 5, 11),

    #
    # 5x6
    #
    Box(5, 6, 7),
    Box(5, 6, 9),

    #
    # 5x7
    #
    Box(5, 7, 7),
    # 5x7x8 is composite
    Box(5, 7, 9),

    #
    # 5x9
    #
    Box(5, 9, 9),

    #
    # 6x6
    #
    Box(6, 6, 10),
    Box(6, 6, 15),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
    Box(2, 5, 10),
    Box(2, 5, 13),
    Box(2, 5, 15),
    Box(2, 5, 16),
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class BCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        box = box.canonical()
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if (a * b * c) % 5 != 0:
            return "published_impossible"

        #
        # 2 × N × {3,4,6,7,9}
        #
        if a == 2 and c in {3, 4, 6, 7, 9}:
            return "published_impossible"

        #
        # Canonical forms of 2×2×N, 2×3×N, 2×4×N,
        # 2×6×N, 2×7×N, 2×9×N.
        #
        if a == 2 and b in {2, 3, 4, 6, 7, 9}:
            return "published_impossible"


        #
        # 3 × N × {3,4,5,6,7,8,11}
        #
        if a == 3 and (b in {3, 4, 5, 6, 7, 8, 11} or c in {3, 4, 5, 6, 7, 8, 11}):
            return "published_impossible"

        #
        # 4 × N × 4
        #
        if a == 4 and b == 4:
            return "published_impossible"

        if box in {

            Box(2, 5, 12),
            Box(2, 10, 12),
            Box(2, 12, 15),

            Box(3, 9, 10),
            Box(3, 9, 15),

            Box(3, 10, 10),
            Box(3, 10, 13),
            Box(3, 10, 14),
            Box(3, 10, 16),
            Box(3, 10, 17),

            Box(4, 5, 6),
            Box(4, 5, 7),
            Box(4, 5, 9),

            Box(5, 5, 5),
            Box(5, 5, 7),
            Box(5, 5, 9),

            Box(5, 6, 6),
        }:
            return "published_impossible"
        return None


B_CATALOGUE = BCatalogue(
    catalogue_name="B",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)