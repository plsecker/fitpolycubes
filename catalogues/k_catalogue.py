from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    Box(3, 4, 15),
    Box(3, 5, 6),
    Box(3, 5, 9),
    Box(3, 7, 15),

   #
    # 4x5
    #
    Box(4, 5, 6),

    #
    # 4x8
    #
    Box(4, 8, 20),

    #
    # 4x10
    #
    Box(4, 10, 10),

    #
    # 5x7
    #
    Box(5, 7, 24),
    Box(5, 7, 24),
    Box(5, 7, 36),
    Box(5, 7, 42),

    #
    # 6x6
    #
    Box(6, 6, 15),
    Box(6, 6, 20),
    Box(6, 6, 25),

    #
    # 6x7
    #
    Box(6, 7, 10),
    Box(6, 7, 15),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {

    # Box(3,3,5),

    Box(4, 5, 7),


    Box(5, 6, 6),
    Box(5, 6, 7),
    Box(5, 6, 9),
    Box(5, 6, 10),
    Box(5, 6, 11),
    Box(5, 6, 13),
    Box(5, 6, 14),
    Box(5, 6, 15),

    Box(5, 7, 12),
    Box(5, 7, 18),

    Box(6, 6, 10),

    #
    # Shirakawa corrections
    #
    Box(4, 9, 15),
    Box(4, 10, 14),

    #
    # Sillke claimed solution,
    # Shirakawa says wrong, but gives a solution
    #
    # Box(5, 7, 30),

    Box(8, 8, 10),
    Box(8, 10, 14),

}

ROW_FAMILIES = {}

WIDTH_SPLITS = {}


class KCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        #
        # 2xNx{2..20}
        #
        if a == 2 and 2 <= b <= 20:
            return "published_impossible"

        #
        # 3-wide boxes
        #
        # Sillke has a row:
        #
        #   3x[3-12]xN  0
        #
        # but this cannot mean all 3xbxc boxes with
        # b in [3,12] are impossible because
        #
        #   3x4x15
        #   3x5x6
        #   3x5x9
        #   3x7x15
        #
        # are known solutions.
        #
        # Interpretation unresolved.
        #

        if (a, b) == (3, 3):
            return "discovered_impossible"

        # Shirakawa 2014
        # 3x13xN impossible
        #
        if (a, b) == (3, 13):
            return "published_impossible"

        #
        # 4xNx{4,7}
        #
        if a == 4 and b in {4, 7}:
            return "published_impossible"

        if a == 4 and b == 8 and c in{10, 30, 50, 70, 90, 110}:
            return "published_impossible"

        if a == 4 and b == 9 and c in{10, 15, 20, 25, 30, 35, 40, 45,}:
            return "published_impossible"

        if a == 4 and b == 5 and c ==5:
            return "published_impossible"

        if a == 4 and b == 10 and c ==14:
            return "published_impossible"

        #
        # 5xNx5
        #
        if a == 5 and b == 5:
            return "published_impossible"

        if a == 5 and b == 9 and c == 9:
            return "published_impossible"

        if a == 6 and b == 6 and c == 10:
            return "published_impossible"

        # #
        # # 14x
        # #
        # if a == 8 and b == 10 and c == 14:
        #     return "published_impossible, due to 4x10x14"
        #
        # if a == 10 and b == 14 and c == 14:
        #     return "published_impossible, due to ?"


        #
        # odd-width theorem
        #
        if a % 2 == 1 and (b * c) % 3 != 0:
            return "published_impossible, odd-width theorem"
        if b % 2 == 1 and (a * c) % 3 != 0:
            return "published_impossible, odd-width theorem"
        if c % 2 == 1 and (a * b) % 3 != 0:
            return "published_impossible, odd-width theorem"

        if a == 8 and b == 10 and c == 14:
            return "published_impossible"  # as 8,10,14 was searched and it is needed

        if box in SEARCHED_NO_SOLUTION:
            return "SEARCHED_NO_SOLUTION"


        return None


K_CATALOGUE = KCatalogue(
    catalogue_name="21",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
)