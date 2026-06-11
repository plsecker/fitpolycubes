from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {

    # # 2D
    # Box(2,5,0),
    # Box(7,15,0),

    # 3D
    Box(3,5,5),

}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class LCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
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
)