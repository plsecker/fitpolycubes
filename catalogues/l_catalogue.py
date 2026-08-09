from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {

    # # 2D
    Box(1,7,15),
    Box(1,2,5),   # canonical form
    # 3D
    Box(3,5,5),

}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(3, 5, 5)

# No RAW_PRIME with all three dimensions even exists in the current catalogue.
MINIMAL_EVEN = None

SEARCHED_NO_SOLUTION = {
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class LCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # 2D families (thickness 1)
        #
        if a == 1:

            if b == 1:
                return "published_impossible"

            # 3×N rectangles
            if b == 3:
                return "published_impossible"

            # 5×odd rectangles
            if b == 5 and c % 2 == 1:
                return "published_impossible"

        a, b, c = sorted((box.a, box.b, box.c))
        if a == 3 and b == 3:
            return "published_impossible"

        return None


L_CATALOGUE = LCatalogue(
    catalogue_name="L",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
