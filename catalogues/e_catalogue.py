from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {
    # Prime minimal
    Box(2, 2, 5),

    # Published primes
    Box(2, 7, 15),

    Box(3, 4, 10),
    Box(3, 4, 15),

    Box(3, 5, 6),
    Box(3, 5, 8),
    Box(3, 5, 9),
    Box(3, 5, 10),
    Box(3, 5, 11),
    Box(3, 5, 13),

    Box(3, 7, 10),
    Box(3, 7, 15),

    Box(4, 5, 5),

    Box(5, 5, 5),
    Box(5, 5, 7),
    Box(5, 7, 7),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(5, 5, 5)

# No RAW_PRIME with all three dimensions even exists in the current catalogue.
MINIMAL_EVEN = None

SEARCHED_NO_SOLUTION = {
}

PUBLISHED_SOLUTIONS = {
    Box(2, 2, 5),
        Box(2, 7, 15),
        Box(3, 4, 10),
        Box(3, 4, 15),
        Box(3, 5, 6),
        Box(3, 5, 8),
        Box(3, 5, 9),
        Box(3, 5, 10),
        Box(3, 5, 11),
        Box(3, 5, 13),
        Box(3, 7, 10),
        Box(4, 5, 5),
        Box(5, 5, 5),
        Box(5, 5, 7),
        Box(5, 7, 7),
}
#
# Published infinite prime families from Sillke (1993).
#
# Format:
#     (width, height): (period, [seed lengths])
#
ROW_FAMILIES = {
}
# ROW_FAMILIES = {
#     (2, 5): Family(seeds=[2], period=2),
#     (3, 5): Family(seeds=[8, 9, 10, 11, 12, 13], period=6),
#     (4, 5): Family(seeds=[5], period=2),
#     (5, 5): Family(seeds=[4, 5, 6, 7], period=4),
#     (6, 5): Family(seeds=[3], period=2),
#     (7, 5): Family(seeds=[5, 6, 7], period=4),
#     (8, 5): Family(seeds=[3], period=2),
# }

#
# No published width decompositions.
#
WIDTH_SPLITS = {
}


class ECatalogue(Catalogue):

    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # Published impossible families
        #

        if a <= 1:
            return "published_impossible"

        #
        # 2×3×5n
        #
        if a == 2 and b == 3:
            return "published_impossible"

        #
        # 3×3×5n
        #
        if a == 3 and b == 3:
            return "published_impossible"

        #
        # 2×5×odd
        #
        if a == 2 and b == 5 and (c % 2 == 1):
            return "published_impossible"

        #
        # Explicit published impossible boxes
        #
        if (a, b, c) in {
            (3, 4, 5),
            (3, 5, 5),
            (3, 5, 7),
        }:
            return "published_impossible"

        return None


E_CATALOGUE = ECatalogue(
    catalogue_name="E",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=PUBLISHED_SOLUTIONS,
)