from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {
    #
    # 2x4
    #
    Box(2, 4, 10),
    Box(2, 4, 15),

    #
    # 2x5
    #
    Box(2, 5, 6),   # minimal Reid
    Box(2, 5, 10),
    Box(2, 5, 14),
    Box(2, 5, 15),
    Box(2, 5, 17),
    Box(2, 5, 19),

    #
    # 2x7
    #
    Box(2, 7, 10),
    Box(2, 7, 15),

    #
    # 3x3
    #
    Box(3, 3, 10),
    Box(3, 3, 15),

    #
    # minimal Reid
    #
    Box(3, 4, 5),

    #
    # 3x5
    #
    Box(3, 5, 5),
    Box(3, 5, 6),
    Box(3, 5, 7),

    #
    # 4x4
    #
    Box(4, 4, 5),

    #
    # 4x5
    #
    Box(4, 5, 5),

    #
    # 5x5
    #
    Box(5, 5, 5),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
    #
    # Published impossible
    #
    Box(2, 4, 5),

    Box(2, 5, 5),
    Box(2, 5, 7),
    Box(2, 5, 8),
    Box(2, 5, 9),
    Box(2, 5, 11),
    Box(2, 5, 13),

    Box(3, 3, 5),
}

ROW_FAMILIES = {
    (3, 5): Family(
        seeds=[5, 6, 7],
        period=1,
    ),
}

WIDTH_SPLITS = {
}


class JCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # Zero-volume / too small
        #
        if a <= 1:
            return "published_impossible"

        #
        # Volume must be divisible by 5
        #
        if (a * b * c) % 5 != 0:
            return "published_impossible"

        #
        # Published family:
        # 2x[2-3]xN
        #
        if a == 2 and b in {2, 3}:
            return "published_impossible"

        #
        # Explicit published impossibilities
        #
        if (a, b, c) == (2, 4, 5):
            return "published_impossible"

        if (a, b) == (2, 5):
            if c == 5:
                return "published_impossible"

            if c in {7, 8, 9, 11, 13}:
                return "published_impossible"

        if (a, b, c) == (3, 3, 5):
            return "published_impossible"

        return None


J_CATALOGUE = JCatalogue(
    catalogue_name="J",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
)