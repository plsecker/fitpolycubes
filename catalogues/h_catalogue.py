from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {

    #
    # Minimal
    #
    Box(2, 2, 5),

    #
    # 2x5
    #
    Box(2, 5, 13),

    #
    # 3x4
    #
    Box(3, 4, 5),
    Box(3, 4, 10),
    Box(3, 4, 15),

    #
    # 3x6
    #
    Box(3, 6, 10),
    Box(3, 6, 15),

    #
    # 3x7
    #
    Box(3, 7, 10),
    Box(3, 7, 25),

    #
    # 3x9
    #
    Box(3, 9, 10),
    Box(3, 9, 15),

    #
    # 3x11
    #
    Box(3, 11, 15),

    #
    # 4x5
    #
    Box(4, 5, 5),

    #
    # 5x5
    #
    Box(5, 5, 6),
    Box(5, 5, 9),
    Box(5, 5, 11),

    #
    # 5x7
    #
    Box(5, 7, 7),
    Box(5, 7, 9),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {

    #
    # Explicitly impossible (Sillke)
    #
    Box(3, 7, 15),

    Box(5, 5, 5),
    Box(5, 5, 7),
}

ROW_FAMILIES = {

    #
    # 2x5x13p, ... 12..13+2n
    #
    (2, 5): Family(
        seeds=[13],
        period=2,
    ),

    #
    # 4x5x5p, ... 4..5+2n
    #
    (4, 5): Family(
        seeds=[5],
        period=2,
    ),

    #
    # 5x5x6p,9p,11p, ... 8..11+4n
    #
    (5, 5): Family(
        seeds=[6, 9, 11],
        period=4,
    ),

    #
    # 5x7x7p,9p, ... 6..9+4n
    #
    (5, 7): Family(
        seeds=[7, 9],
        period=4,
    ),

    #
    # 3x10x4p,6p,7p,9p, ... 6..9+4n
    #
    (3, 10): Family(
        seeds=[4, 6, 7, 9],
        period=4,
    ),

    #
    # 3x15x4p,6p,9p,11p, ... 8..11+4n
    #
    (3, 15): Family(
        seeds=[4, 6, 9, 11],
        period=4,
    ),

    #
    # 3x25x7p, ... 6..9+4n
    #
    (3, 25): Family(
        seeds=[7],
        period=4,
    ),
}

WIDTH_SPLITS = {}


class HCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        #
        # 2x3xN
        #
        if (a, b) == (2, 3):
            return "published_impossible"

        #
        # 3x3xN
        #
        if (a, b) == (3, 3):
            return "published_impossible"

        #
        # 3x5xN
        #
        # Sillke:
        # "3x5xN (dies out after 40 steps)"
        #
        if (a, b) == (3, 5):
            return "published_impossible"

        #
        # 2x5x{3,5,7,9,11}
        #
        if (a, b) == (2, 5) and c in {3, 5, 7, 9, 11}:
            return "published_impossible"

        #
        # 5x5x{5,7}
        #
        if (a, b) == (5, 5) and c in {5, 7}:
            return "published_impossible"

        #
        # Isolated impossible box
        #
        if (a, b, c) == (3, 7, 15):
            return "published_impossible"

        if box in SEARCHED_NO_SOLUTION:
            return "published_impossible"

        return None


H_CATALOGUE = HCatalogue(
    catalogue_name="31",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
