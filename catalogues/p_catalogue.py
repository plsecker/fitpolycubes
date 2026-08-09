from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {
    Box(1, 2, 5),
    Box(1, 7, 15),

    # discovered by solver
    Box(3, 3, 5),

    # Box(2, 5, 5),   # composite
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(3, 3, 5)

# No RAW_PRIME with all three dimensions even exists in the current catalogue.
MINIMAL_EVEN = None

SEARCHED_NO_SOLUTION = {
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class PCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        box = box.canonical()
        a, b, c = box.a, box.b, box.c

        if box in PRIMES:
            return None

        if (a * b * c) % 5 != 0:
            return "volume_not_multiple_of_5"

        if a == 1 and b == 3:
            return "3xZ_impossible"

        if a == 1 and b == 5 and c % 2 == 1:
            return "1x5xu_odd_impossible"

        return None


P_CATALOGUE = PCatalogue(
    catalogue_name="P",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
