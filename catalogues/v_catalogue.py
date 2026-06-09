from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {

    # 3x5
    Box(3,5,6),
    Box(3,5,8),

    # 4x5
    Box(4,5,6),
    Box(4,5,7),
    Box(4,5,8),
    Box(4,5,9),
    Box(4,5,10),
    Box(4,5,11),

    # 5x5
    Box(5,5,6),
    Box(5,5,9),
    Box(5,5,10),
    Box(5,5,11),
    # Box(5,5,12),#by Shirakawa
    Box(5,5,13),
    Box(5,5,14),

    # 5x6
    # Box(5,6,3), #  have 5,6,3
    # Box(5,6,4), #have 4,5,6
    # Box(5,6,5), #  have 5,5,6

    # 5x7
    # Box(5,7,4),# have 4,5,7
    Box(5,7,7),
    Box(5,7,9),

    # 5x8
    # Box(5,8,3),# have 3,5,8
    # Box(5,8,4),# have 4,5,8

    # 5x9
    # Box(5,9,4),# have 4,5,9
    # Box(5,9,5),# have 5,9,5
    # Box(5,9,7),# have 5,7,,9

    # 5x10
    # Box(5,10,4),# have 44,5,10
    # Box(5,10,5),# have 5,5,10

    # 5x11
    # Box(5,11,4), # have 4,5,11
    # Box(5,11,5),# have 45,5,11

    # 3x10
    Box(3,10,9),
    Box(3,10,10),
    Box(3,10,11),
    Box(3,10,13),

    # 3x15
    Box(3,15,9),
    Box(3,15,11),
    Box(3,15,13),

    # 3x20
    Box(3,20,7),

    # 3x25
    Box(3,25,7),

    # 3x30
    Box(3,30,7),

    # 3x35
    Box(3,35,7),
}

SEARCHED_NO_SOLUTION = {
}


ROW_FAMILIES = {

    (3,5): Family(
        seeds=[6,8],
        period=6,
    ),

    (4,5): Family(
        seeds=[6,7,8,9,10,11],
        period=6,
    ),

    (5,5): Family(
        seeds=[6,9,10,11,13,14],
        period=6,
    ),

    (5,6): Family(
        seeds=[3,4,5],
        period=3,
    ),

    (5,7): Family(
        seeds=[4,7,9],
        period=4,
    ),

    (5,8): Family(
        seeds=[3,4],
        period=3,
    ),

    (5,9): Family(
        seeds=[4,5,7],
        period=4,
    ),

    (5,10): Family(
        seeds=[4,5],
        period=4,
    ),

    (5,11): Family(
        seeds=[4,5],
        period=4,
    ),

    (3,10): Family(
        seeds=[9,10,11,13],
        period=6,
    ),

    (3,15): Family(
        seeds=[9,11,13],
        period=6,
    ),

    (3,20): Family(
        seeds=[7],
        period=5,
    ),

    (3,25): Family(
        seeds=[7],
        period=6,
    ),

    (3,30): Family(
        seeds=[7],
        period=5,
    ),

    (3,35): Family(
        seeds=[7],
        period=6,
    ),
}



WIDTH_SPLITS = {
}
PRIMES = {b.canonical() for b in RAW_PRIMES}


WIDTH_SPLITS = {}

SEARCHED_NO_SOLUTION = set()


class VCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if a == b == c:
            return "cube"

        if (a, b) == (3, 3):
            return "published_impossible"

        if (a, b) == (3, 4):
            return "published_impossible"

        return None


V_CATALOGUE = VCatalogue(
    catalogue_name="V",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
)