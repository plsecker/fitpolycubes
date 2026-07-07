from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    Box(4, 9, 15),  # prime minimal?
    Box(4, 9, 20),  # Postl
    Box(4, 9, 25),
    Box(4, 11, 15),
    Box(4, 11, 20),
    Box(4, 11, 25),
    Box(4, 12, 15),
    Box(4, 12, 20),
    Box(4, 12, 25),
    Box(4, 13, 15),
    Box(4, 13, 20),
    Box(4, 13, 25),
    Box(4, 14, 15),
    Box(4, 14, 20),
    Box(4, 14, 25),
    Box(4, 15, 15),
    Box(4, 15, 16),
    Box(4, 15, 17),
    Box(4, 15, 19),
    Box(4, 16, 20),
    Box(4, 16, 25),
    Box(4, 17, 20),
    Box(4, 17, 25),
    Box(4, 19, 20),
    Box(4, 19, 25),
    Box(6, 10, 10),
    Box(6, 11, 15),
    Box(6, 12, 15),
    Box(6, 13, 15),
    Box(8, 8, 15),
    Box(8, 10, 10),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
}

#
# None yet. The published infinite solution families are not known
# to be generated from prime seeds, so leave this empty until proven.
#
ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class ACatalogue(Catalogue):

    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # Published impossible families
        #

        if a <= 1:
            return "published_impossible"

        # 2xMxN, 3xMxN
        if a <= 3:
            return "published_impossible"

        # 4x[4-8]xN
        if a == 4 and 4 <= b <= 8:
            return "published_impossible"

        # 4x10xN
        if a == 4 and (b == 10 or c == 10):
            return "published_impossible"

        # 5xMxN
        if a == 5:
            return "published_impossible"

        # 6x6xN
        if a == 6 and b == 6:
            return "published_impossible"

        return None


A_CATALOGUE = ACatalogue(
    catalogue_name="A",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
