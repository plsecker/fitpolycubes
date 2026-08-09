from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    #
    # Complete prime list from Sillke / Shirakawa
    #
    Box(2, 3, 5),

    Box(2, 10, 10),
    Box(2, 10, 14),

    Box(2, 11, 20),
    Box(2, 11, 25),

    Box(3, 3, 10),
    Box(3, 5, 7),

    Box(4, 4, 5),
    Box(4, 5, 5),

    Box(5, 5, 11),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
MINIMAL_ODD = Box(3, 5, 7)

# Smallest RAW_PRIME with all three dimensions even.
MINIMAL_EVEN = Box(2, 10, 10)

SEARCHED_NO_SOLUTION = {
    #
    # Explicitly listed impossible by Sillke
    #
    Box(2, 10, 11),

    Box(5, 5, 3),
    Box(5, 5, 5),
    Box(5, 5, 7),
}

ROW_FAMILIES = {}

WIDTH_SPLITS = {}


class UCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if (a * b * c) % 5 != 0:
            return "published_impossible"

        if (a, b) == (2, 2):
            return "published_impossible"

        #
        # Published impossible:
        # 2x4xN
        #
        if (a, b) == (2, 4):
            return "published_impossible"

        #
        # Published impossible:
        # 2x7xN
        #
        if (a, b) == (2, 7):
            return "published_impossible"

        #
        # Published impossible:
        # 2x5xk, k = 1,2 (mod 3)
        #
        if (a, b) == (2, 5):
            if c % 3 in {1, 2}:
                return "published_impossible"

        #
        # Published impossible:
        # 2x8x5k, k = 1,2 (mod 3)
        #
        if (a, b) == (2, 8):
            if c % 5 == 0:
                k = c // 5
                if k % 3 in {1, 2}:
                    return "published_impossible"

        #
        # Published impossible:
        # 3x3x5u with u odd
        #
        if (a, b) == (3, 3):
            if c % 5 == 0 and ((c // 5) % 2 == 1):
                return "published_impossible"

        if box.canonical() in {
            Box(3, 5, 5),
            Box(5, 5, 5),
            Box(5, 5, 7),
        }:
            return "published_impossible"

        #
        # Explicit published impossible box
        #
        if box == Box(2, 10, 11):
            return "published_impossible"

        return None


U_CATALOGUE = UCatalogue(
    catalogue_name="U",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
