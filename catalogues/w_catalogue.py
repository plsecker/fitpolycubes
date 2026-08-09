from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    #
    # 3x7
    #
    Box(3, 7, 20),
    Box(3, 7, 25),
    Box(3, 7, 30),
    Box(3, 7, 35),

    #
    # 3x8
    #
    Box(3, 8, 15),
    Box(3, 8, 20),
    Box(3, 8, 25),

    #
    # 3x9
    #
    Box(3, 9, 15),
    Box(3, 9, 20),
    Box(3, 9, 25),

    #
    # 3x10
    #
    Box(3, 10, 11),
    Box(3, 10, 12),
    Box(3, 10, 13),
    Box(3, 10, 14),
    Box(3, 10, 15),
    Box(3, 10, 16),
    Box(3, 10, 17),
    Box(3, 10, 18),
    Box(3, 10, 19),
    Box(3, 10, 20),
    Box(3, 10, 21),

    # 3x11x15
    Box(3, 11, 15),
    Box(3, 12, 15),
    Box(3, 13, 15),
    Box(3, 14, 15),
    Box(3, 15, 15),
    #
    # 3x15
   Box(3, 15, 15),

    #
    # 4x5
    #
    Box(4, 5, 19),
    Box(4, 5, 24),
    Box(4, 5, 26),
    Box(4, 5, 28),
    Box(4, 5, 29),
    Box(4, 5, 30),
    Box(4, 5, 31),
    Box(4, 5, 32),
    Box(4, 5, 33),
    Box(4, 5, 34),
    Box(4, 5, 35),
    Box(4, 5, 36),
    Box(4, 5, 37),
    Box(4, 5, 39),
    Box(4, 5, 40),
    Box(4, 5, 41),
    Box(4, 5, 42),
    Box(4, 5, 44),
    Box(4, 5, 46),

    #
    # 4x6
    #
    Box(4, 6, 10),
    Box(4, 6, 15),

    #
    # 4x7
    #
    Box(4, 7, 15),
    Box(4, 7, 20),
    Box(4, 7, 25),

    #
    # 4x8
    #
    Box(4, 8, 10),
    Box(4, 8, 15),


    #
    # 4x9
    #
    Box(4, 9, 10),
    Box(4, 9, 15),

    #
    # 4x10
    #
    Box(4, 10, 10),
    Box(4, 10, 11),
    Box(4, 10, 13),
    Box(4, 10, 15),

    #
    # 4x11
    #
    Box(4, 11, 15),

    #
    # 5x5
    #
    Box(5, 5, 14),
    Box(5, 5, 16),
    Box(5, 5, 18),
    Box(5, 5, 19),
    Box(5, 5, 20),
    Box(5, 5, 21),
    Box(5, 5, 22),
    Box(5, 5, 23),
    Box(5, 5, 24),
    Box(5, 5, 25),
    Box(5, 5, 26),
    Box(5, 5, 27),
    Box(5, 5, 29),
    Box(5, 5, 31),

    #
    # 5x6
    #
    Box(5, 6, 6),
    Box(5, 6, 7),
    Box(5, 6, 8),
    Box(5, 6, 9),
    Box(5, 6, 10),
    Box(5, 6, 11),

    #
    # 5x7
    #
    Box(5, 7, 9),
    Box(5, 7, 10),
    Box(5, 7, 11),
    Box(5, 7, 13),
    Box(5, 7, 14),

    #
    # 5x8
    #
    Box(5, 8, 8),
    Box(5, 8, 9),
    Box(5, 8, 10),
    Box(5, 8, 11),
    Box(5, 8, 13),

    #
    # 5x9
    #
    Box(5, 9, 9),
    Box(5, 9, 10),
    Box(5, 9, 11),

    #
    # 5x10
    #
    Box(5, 10, 10),
    Box(5, 10, 11),

    #
    # 5x11
    #
    Box(5, 11, 11),

    #
    # 7x7
    #
    Box(7, 7, 10),
    Box(7, 7, 15),

    #
    # 7x8
    #
    Box(7, 8, 10),

}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(5, 7, 9)

# Smallest RAW_PRIME with all three dimensions even.
MINIMAL_EVEN = Box(4, 6, 10)

SEARCHED_NO_SOLUTION = {
    #
    # Explicitly listed impossible by Sillke
    #
    Box(3, 7, 5),
    Box(3, 7, 10),
    Box(3, 7, 15),
    Box(4, 7, 10),

    Box(3, 8, 10),
    Box(3, 9, 10),
    Box(3, 10, 10),

    Box(5, 5, 5),
    Box(5, 5, 6),
    Box(5, 5, 7),
    Box(5, 5, 8),
    Box(5, 5, 9),
    Box(5, 5, 10),
    Box(5, 5, 11),
    Box(5, 5, 12),
    Box(5, 5, 13),
    Box(5, 5, 15),

    Box(5, 7, 7),
    Box(5, 7, 8),
}

ROW_FAMILIES = {

}

WIDTH_SPLITS = {
}


class WCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if (a * b * c) % 5 != 0:
            return "published_impossible"

        #
        # n*N impossible
        #
        if b == 2:
            return "published_impossible"

        if a == 2:
            return "published_impossible"

        #
        # 3*N*{3,4,5,6}
        #
        if a == 3 and b in {3, 4, 5, 6}:
            return "published_impossible"
        # 4 * N * {3, 4}
        if a == 4 and b == 4:
            return "published_impossible"
        #
        # Published impossible boxes
        #
        if box in {
            Box(3, 7, 5),
            Box(3, 7, 10),
            Box(3, 7, 15),
            Box(4, 7, 10),
        }:
            return "published_impossible"

        #
        # 4*N*{3,4}
        #
        if a == 4 and c in {3, 4}:
            return "published_impossible"

        #
        # 4*5*{1..18,20,21,22,23,25,27}
        #
        if (a, b) == (4, 5):
            if 1 <= c <= 18:
                return "published_impossible"

            if c in {20, 21, 22, 23, 25, 27}:
                return "published_impossible"

        #
        # 3*3*Z
        #
        if (a, b) == (3, 3):
            return "published_impossible"

        if (a, b) == (3, 7) and c in {5, 10, 15}:
            return "published_impossible"
        return None


W_CATALOGUE = WCatalogue(
    catalogue_name="W",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
