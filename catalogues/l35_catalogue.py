from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {

    # 2x8
    Box(2,8,10),

    # 2x9
    Box(2,9,15),

    # 2x10
    Box(2,10,10),
    Box(2,10,12),
    Box(2,10,14),

    # 2x11
    Box(2,11,30),

    # 2x12
    Box(2,12,15),

    # 2x13
    Box(2,13,30),

    # 2x15
    Box(2,15,15),

    # 3x4
    Box(3,4,30),
    Box(3,4,45),

    # 3x5
    Box(3,5,6),
    Box(3,5,9),

    # 3x7
    Box(3,7,15),

    # 3x8
    Box(3,8,15),

    # 4x4
    Box(4,4,10),

    # 4x5
    Box(4,5,6),

    # 5x5
    Box(5,5,6),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
}

ROW_FAMILIES = {
    # (3,5): Family(seeds=[6,9], period=6),
    # (4,5): Family(seeds=[6], period=6),
    # (5,5): Family(seeds=[6], period=6),
}

WIDTH_SPLITS = {
}


class L35Catalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if a == b == c:
            return "cube"

        #
        # Published impossible families
        #

        # 2 x N x {2..7}
        if a == 2 and c <= 7:
            return "published_impossible"

        # 3 x N x 3
        if a == 3 and c == 3:
            return "published_impossible"

        # odd width theorem:
        # uxpxq with u odd and pq not divisible by 3
        if (a % 2) == 1 and ((b * c) % 3) != 0:
            return "published_impossible"

        #
        # Published impossible individual boxes
        #

        if box in {
            Box(3,4,15),
        }:
            return "published_impossible"

        return None


L35_CATALOGUE = L35Catalogue(
    catalogue_name="L35",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
)