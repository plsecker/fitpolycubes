from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {
    # 2x2
    Box(2, 3, 5),  # discovered by solver
    Box(2, 2, 15),  # discovered prime (required for decomposition completeness)
    #
    # # 3x3
    # Box(3, 3, 5),  # impossible
    Box(3,3,10),
    Box(3,3,15),

    # 3x4
    Box(3,4,10),
    Box(3,4,15),

    # 3x5
    Box(3,5,6),
    Box(3,5,14),
    Box(3,5,15),
    Box(3,5,16),
    Box(3,5,17),
    Box(3,5,19),

    # 4x4
    Box(4,4,15),

    # 4x5
    Box(4,5,6),
    Box(4,5,9),

    # 5x5
    Box(5,5,6),
    Box(5,5,9),

    # 5x7
    Box(5,7,9),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
    Box(3, 3, 5),
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class QCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        #
        # Published impossible individual boxes
        #

        if box in {

            # 3x family (canonical)
            Box(3,3,5),
            Box(3,4,5),
            Box(3,5,5),
            Box(3,5,7),
            Box(3,5,8),
            Box(3,5,9),
            Box(3,5,10),
            Box(3,5,11),
            Box(3,5,13),
        }:
            return "published_impossible"

        if (a * b * c) % 3 != 0:
            return "published_impossible"

        return None


Q_CATALOGUE = QCatalogue(
    catalogue_name="Q",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
)