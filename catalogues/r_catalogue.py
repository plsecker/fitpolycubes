from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    # 4x7
    Box(4, 7, 30),
    Box(4, 7, 35),
    Box(4, 7, 40),
    Box(4, 7, 45),
    Box(4, 7, 50),
    Box(4, 7, 55),

    # 4x8
    Box(4, 8, 10),  # prime minimal
    Box(4, 8, 15),

    # 4x9
    Box(4, 9, 20),
    Box(4, 9, 25),

    # 4x10
    Box(4, 10, 12),
    Box(4, 10, 13),
    Box(4, 10, 14),
    Box(4, 10, 15),

    # 4x11-13
    Box(4, 11, 15),
    Box(4, 12, 15),
    Box(4, 13, 15),

    # 5x6
    Box(5, 6, 12),
    Box(5, 6, 13),
    Box(5, 6, 14),
    Box(5, 6, 15),
    Box(5, 6, 16),
    Box(5, 6, 17),
    Box(5, 6, 18),
    Box(5, 6, 19),
    Box(5, 6, 20),
    Box(5, 6, 21),
    Box(5, 6, 22),
    Box(5, 6, 23),

    # 5x7
    Box(5, 7, 16),

    # 5x8
    Box(5, 8, 8),   # Postl 1998, prime minimal
    Box(5, 8, 11),
    Box(5, 8, 12),
    Box(5, 8, 13),
    Box(5, 8, 14),
    Box(5, 8, 15),

    # 5x10
    Box(5, 10, 10),
    Box(5, 10, 11),
    Box(5, 10, 12),
    Box(5, 10, 13),
    Box(5, 10, 14),
    Box(5, 10, 15),

    # 6x6
    Box(6, 6, 15),
    Box(6, 6, 20),
    Box(6, 6, 25),

    # 6x7
    Box(6, 7, 10),
    Box(6, 7, 15),

    # 6x8
    Box(6, 8, 10),
    Box(6, 8, 15),

    # 6x9
    Box(6, 9, 10),
    Box(6, 9, 15),

    # 6x10
    Box(6, 10, 10),
    Box(6, 10, 11),

    # 7x8
    Box(7, 8, 10),
    Box(7, 8, 15),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
}

#
# No published row-generator families.
#
ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class RCatalogue(Catalogue):

    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # Published impossible families (Shirakawa)
        #

        if a <= 1:
            return "published_impossible"

        # 2xMxN
        if a == 2:
            return "published_impossible"

        # 3xMxN
        if a == 3:
            return "published_impossible"

        # 4x[4-6]xN
        if a == 4 and 4 <= b <= 6:
            return "published_impossible"

        # 4x7x10,15,20,25
        if a == 4 and b == 7 and c in {10, 15, 20, 25}:
            return "published_impossible"

        # 5x5xN
        if a == 5 and b == 5:
            return "published_impossible"

        # 5x6x[6-11]
        if a == 5 and b == 6 and c <= 11:
            return "published_impossible"

        # 5x7x[7-14]
        if a == 5 and b == 7 and c <= 14:
            return "published_impossible"

        # 6x6x10
        if a == 6 and b == 6 and c == 10:
            return "published_impossible"

        return None


R_CATALOGUE = RCatalogue(
    catalogue_name="R",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)