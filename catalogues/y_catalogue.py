from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    Box(2, 4, 10),
    Box(2, 4, 15),

    Box(2, 5, 6),
    Box(2, 5, 8),
    Box(2, 5, 11),
    Box(2, 5, 13),
    Box(2, 5, 15),

    Box(2, 7, 10),
    Box(2, 7, 15),

    Box(3, 4, 5),
    Box(3, 5, 9),
    Box(3, 5, 11),
    Box(3, 6, 10),
    Box(3, 6, 15),
    Box(3, 7, 10),
    Box(3, 7, 15),

    Box(4, 4, 5),
    Box(4, 5, 5),

    Box(5, 5, 5),
    Box(5, 5, 6),
    Box(5, 5, 7),
    Box(5, 7, 7),
}
# add 1x
RAW_PRIMES |= {

    #
    # 10 × n
    #
    Box(1,10,5),
    Box(1,10,14),

    # n ≡ 3 (mod 5), n >= 23
    *[Box(1,10,n) for n in range(23,101,5)],

    # n ≡ 2 (mod 5), n >= 27
    *[Box(1,10,n) for n in range(27,101,5)],


    #
    # 15 × n
    #
    Box(1,15,14),
    Box(1,15,15),
    Box(1,15,16),
    Box(1,15,17),

    # n ≡ 9 (mod 10), n >= 19
    *[Box(1,15,n) for n in range(19,101,10)],

    # n ≡ 1 (mod 10), n >= 21
    *[Box(1,15,n) for n in range(21,101,10)],

    # n ≡ 2 (mod 10), n >= 22
    *[Box(1,15,n) for n in range(22,101,10)],

    # n ≡ 3 (mod 10), n >= 23
    *[Box(1,15,n) for n in range(23,101,10)],


    #
    # 20 × n
    #
    Box(1,20,9),

    # n ≡ 3 (mod 5), n >= 13
    *[Box(1,20,n) for n in range(13,101,5)],

    # n ≡ 2 (mod 5), n >= 17
    *[Box(1,20,n) for n in range(17,101,5)],


    #
    # 25 × n
    #
    Box(1,25,17),
    Box(1,25,18),

    # n ≡ 2 (mod 10), n >= 22
    *[Box(1,25,n) for n in range(22,101,10)],


    #
    # 30 × n
    #
    Box(1,30,9),

    # n ≡ 3 (mod 5), n >= 13
    *[Box(1,30,n) for n in range(13,101,5)],


    #
    # 35 × n
    #
    Box(1,35,11),
    Box(1,35,13),
    Box(1,35,18),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(5, 5, 5)

# Smallest RAW_PRIME with all three dimensions even.
MINIMAL_EVEN = Box(2, 4, 10)

SEARCHED_NO_SOLUTION = {
    Box(1, 2, 5),
    Box(1, 2, 10),
    Box(1, 2, 15),

    Box(1, 3, 5),
    Box(1, 3, 10),
    Box(1, 3, 15),

    Box(1, 4, 5),
    Box(1, 4, 10),
    Box(1, 4, 15),

    Box(1, 5, 5),
    Box(1, 5, 6),
    Box(1, 5, 7),
    Box(1, 5, 8),
    Box(1, 5, 9),
    Box(1, 5, 11),
    Box(1, 5, 12),
    Box(1, 5, 13),
    Box(1, 5, 14),
    Box(1, 5, 15),

    Box(1, 6, 10),
    Box(1, 6, 15),

    Box(1, 7, 10),
    Box(1, 7, 15),

    Box(1, 8, 10),
    Box(1, 8, 15),

    Box(1, 9, 10),
    Box(1, 9, 15),

    Box(1, 10, 11),
    Box(1, 10, 12),
    Box(1, 10, 13),

    Box(1, 11, 15),
    Box(1, 12, 15),
    Box(1, 13, 15),
}

SEARCHED_NO_SOLUTION |= {
    Box(2, 2, 5),
    Box(2, 2, 10),
    Box(2, 2, 15),

    Box(2, 3, 5),
    Box(2, 3, 10),
    Box(2, 3, 15),

    Box(2, 4, 5),

    Box(2, 5, 5),
    Box(2, 5, 7),

    Box(3, 3, 5),
    Box(3, 3, 10),
    Box(3, 3, 15),

    Box(3, 5, 5),
    Box(3, 5, 6),
    Box(3, 5, 7),
}

#
# Published infinite solution families are known, but they have not yet
# been reduced to finite prime-generator families.
#
ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class YCatalogue(Catalogue):

    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        #
        # Published impossible families
        #

        if a <= 0:
            return "published_impossible"

        if a == 1 and b <= 4:
            return "published_impossible"

        if (a, b, c) == (2, 5, 4):
            return "published_impossible"

        if (a, b, c) == (2, 5, 9):
            return "published_impossible"

        return None


Y_CATALOGUE = YCatalogue(
    catalogue_name="Y",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)