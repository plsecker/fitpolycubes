from catalogues.base import Box, Catalogue


RAW_PRIMES = {
    # 4x10 family
    Box(4,10,50),
    Box(4,10,55),
    Box(4,10,60),
    Box(4,10,65),
    Box(4,10,70),
    Box(4,10,75),
    Box(4,10,80),
    Box(4,10,85),
    Box(4,10,90),
    Box(4,10,95),

    Box(4,11,50),

    Box(4,14,25),

    Box(4,16,25),
    Box(4,17,25),
    Box(4,18,25),
    Box(4,19,25),

    Box(4,20,20),
    Box(4,20,25),

    Box(4,21,25),
    Box(4,22,25),

    # 5x8 family
    Box(5,8,20),
    Box(5,8,35),
    Box(5,8,45),
    Box(5,8,50),

    # 5x9 family
    Box(5,9,15),
    Box(5,9,25),
    Box(5,9,35),

    # 5x10 family
    Box(5,10,33),
    Box(5,10,36),
    Box(5,10,37),

    # 5x12+
    Box(5,12,20),
    Box(5,12,25),

    Box(5,13,25),

    Box(5,14,20),
    Box(5,14,25),

    Box(5,15,17),
    Box(5,15,19),

    Box(5,16,25),
    Box(5,17,20),

    # 6x*
    Box(6,6,25),
    Box(6,7,25),
    Box(6,8,25),
    Box(6,9,25),

    Box(6,10,10),  # prime minimal
    Box(6,10,15),

    Box(6,11,25),
    Box(6,15,15),

    # 7x*
    Box(7,8,25),
    Box(7,9,25),
    Box(7,10,10),
    Box(7,10,15),
    Box(7,11,25),

    # 8x*
    Box(8,8,25),
    Box(8,9,25),
    Box(8,10,10),
    Box(8,10,15),
    Box(8,15,15),

    # 9x*
    Box(9,10,10),

    # 10x*
    Box(10,10,10),
    Box(10,10,11),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(5, 9, 15)

# Smallest RAW_PRIME with all three dimensions even.
MINIMAL_EVEN = Box(6, 10, 10)

SEARCHED_NO_SOLUTION = set()

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class ZCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 2:
            return "published_impossible"

        #
        # Published impossible families
        #

        if a == 3 and 3 <= b <= 22:
            return "published_impossible"

        if a == 4 and 4 <= b <= 9:
            return "published_impossible"

        if (a, b) == (4, 10) and 10 <= c <= 45:
            return "published_impossible"

        if a == 5 and b in {5, 6, 7}:
            return "published_impossible"

        if a == 7 and b == 7:
            return "published_impossible"

        #
        # Published individual impossible boxes
        #

        if box in {
            Box(4,10,10),
            Box(4,10,15),
            Box(4,10,20),
            Box(4,10,25),
            Box(4,10,30),
            Box(4,10,35),
            Box(4,10,40),
            Box(4,10,45),

            Box(4,11,25),

            Box(5,8,10),
            Box(5,8,15),
            Box(5,8,25),
            Box(5,8,30),

            Box(5,9,10),
            Box(5,9,20),
        }:
            return "published_impossible"

        return None


Z_CATALOGUE = ZCatalogue(
    catalogue_name="Z",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
