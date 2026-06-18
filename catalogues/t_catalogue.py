from catalogues.base import Box, Catalogue

RAW_PRIMES = {
    #
    # 3x7
    #
    Box(3, 7, 20),

    #
    # 3x8
    #
    Box(3, 8, 15),
    Box(3, 8, 35),
    Box(3, 8, 40),

    #
    # 3x10
    #
    Box(3, 10, 10),
    Box(3, 10, 14),
    Box(3, 10, 26),
    Box(3, 10, 27),
    Box(3, 10, 31),
    Box(3, 10, 32),
    Box(3, 10, 33),
    Box(3, 10, 35),
    Box(3, 10, 39),

    #
    # 3x11
    #
    Box(3, 11, 30),
    Box(3, 11, 35),
    Box(3, 11, 40),
    Box(3, 11, 45),
    Box(3, 11, 50),
    Box(3, 11, 55),

    #
    # 3x12
    #
    Box(3, 12, 15),
    Box(3, 12, 20),
    Box(3, 12, 25),

    #
    # 3x13
    #
    Box(3, 13, 20),
    Box(3, 13, 25),
    Box(3, 13, 30),
    Box(3, 13, 35),

    #
    # 3x14
    #
    Box(3, 14, 15),

    #
    # 3x15
    #
    Box(3, 15, 17),
    Box(3, 15, 18),
    Box(3, 15, 19),
    Box(3, 15, 21),
    Box(3, 15, 23),

    #
    # 3x16+
    #
    Box(3, 16, 20),
    Box(3, 16, 25),
    Box(3, 17, 25),
    Box(3, 18, 20),
    Box(3, 18, 25),
    Box(3, 19, 25),
    Box(3, 21, 25),
    Box(3, 22, 25),
    Box(3, 23, 25),

    #
    # 4x11
    #
    Box(4, 11, 80),
    Box(4, 11, 85),
    Box(4, 11, 100),
    Box(4, 11, 105),
    Box(4, 11, 110),
    Box(4, 11, 120),

    #
    # 4x12
    #
    Box(4, 12, 40),
    Box(4, 12, 45),
    Box(4, 12, 50),
    Box(4, 12, 55),
    Box(4, 12, 60),
    Box(4, 12, 65),
    Box(4, 12, 70),
    Box(4, 12, 75),

    #
    # 4x14
    #
    Box(4, 14, 20),
    Box(4, 14, 25),
    Box(4, 14, 30),
    Box(4, 14, 35),

    #
    # 4x15
    #
    Box(4, 15, 26),
    Box(4, 15, 28),

    #
    # 4x16, 4x18, 4x20
    #
    Box(4, 16, 20),
    Box(4, 18, 20),
    Box(4, 20, 20),
    Box(4, 20, 22),
    Box(4, 20, 24),

    #
    # 5x5
    #
    Box(5, 5, 12),

    #
    # 5x8
    #
    Box(5, 8, 100),
    Box(5, 8, 103),
    Box(5, 8, 114),
    Box(5, 8, 118),
    Box(5, 8, 121),
    Box(5, 8, 128),
    Box(5, 8, 130),
    Box(5, 8, 131),
    Box(5, 8, 132),
    Box(5, 8, 134),
    Box(5, 8, 136),

    #*[continue all explicitly-prime 5x8 entries through 199]*

    #
    # 5x9
    #
    Box(5, 9, 48),
    Box(5, 9, 60),

    #
    # 5x12
    #
    Box(5, 12, 13),

    #
    # 5x15
    #
    Box(5, 15, 18),

    #
    # 6x10
    #
    Box(6, 10, 15),

    #
    # 8x8, 8x10
    #
    Box(8, 8, 10),
    Box(8, 10, 10),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

SEARCHED_NO_SOLUTION = {
    Box(3, 7, 10),
    Box(3, 7, 15),

    Box(3, 8, 10),
    Box(3, 8, 20),
    Box(3, 8, 25),

    Box(3, 11, 15),
    Box(3, 11, 20),
    Box(3, 11, 25),

    Box(3, 13, 15),
    Box(3, 15, 15),

    Box(4, 11, 15),
    Box(4, 11, 20),
    Box(4, 11, 25),
    Box(4, 11, 30),
    Box(4, 11, 35),
    Box(4, 11, 40),
    Box(4, 11, 45),
    Box(4, 11, 50),
    Box(4, 11, 55),
    Box(4, 11, 60),
    Box(4, 11, 65),
    Box(4, 11, 70),
    Box(4, 11, 75),
    Box(4, 11, 90),
    Box(4, 11, 95),

    Box(4, 12, 15),
    Box(4, 12, 20),
    Box(4, 12, 25),
    Box(4, 12, 30),
    Box(4, 12, 35),
}

SEARCHED_NO_SOLUTION |= {
    #
    # 3x10
    #
    Box(3,10,11),
    Box(3,10,12),
    Box(3,10,13),
    Box(3,10,15),
    Box(3,10,16),
    Box(3,10,17),
    Box(3,10,18),
    Box(3,10,19),
    Box(3,10,21),
    Box(3,10,22),
    Box(3,10,23),
    Box(3,10,25),
    Box(3,10,29),

    #
    # 3x11
    #
    Box(3,11,15),
    Box(3,11,20),
    Box(3,11,25),

    #
    # 3x13
    #
    Box(3,13,15),

    #
    # 3x15
    #
    Box(3,15,15),

    #
    # 4x11
    #
    Box(4,11,15),
    Box(4,11,20),
    Box(4,11,25),
    Box(4,11,30),
    Box(4,11,35),
    Box(4,11,40),
    Box(4,11,45),
    Box(4,11,50),
    Box(4,11,55),
    Box(4,11,60),
    Box(4,11,65),
    Box(4,11,70),
    Box(4,11,75),
    Box(4,11,90),
    Box(4,11,95),

    #
    # 4x12
    #
    Box(4,12,15),
    Box(4,12,20),
    Box(4,12,25),
    Box(4,12,30),
    Box(4,12,35),

    #
    # 4x14
    #
    Box(4,14,15),

    #
    # 6x7
    #
    Box(6,7,10),
    Box(6,7,15),
    Box(6,7,25),
    Box(6,7,30),
    Box(6,7,35),
}

#
# 5x8x[8-99] = 0
#
for c in range(8, 100):
    SEARCHED_NO_SOLUTION.add(Box(5, 8, c))

#
# 5x8 exceptions that are prime
#
for c in {
    100,103,114,118,121,128,
    130,131,132,134,
    136,137,138,139,140,141,142,143,144,145,
    146,147,148,149,150,151,152,153,154,155,
    156,157,158,159,160,161,162,163,164,165,
    166,167,168,169,170,171,172,173,174,175,
    176,177,178,179,180,181,182,183,184,185,
    186,187,188,189,190,191,192,193,194,195,
    196,197,198,199,
}:
    SEARCHED_NO_SOLUTION.discard(Box(5, 8, c))

#
# 5x9x[9-32] = 0
#
for c in range(9, 33):
    SEARCHED_NO_SOLUTION.add(Box(5, 9, c))

ROW_FAMILIES = {}
WIDTH_SPLITS = {}


class TCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if (a * b * c) % 5 != 0:
            return "published_impossible"

        if a == 2:
            return "published_impossible"

        if a == 3 and b in {3, 4, 5, 6, 9}:
            return "published_impossible"

        if a == 4 and b in {4, 5, 6, 7, 8, 9}:
            return "published_impossible"

        if a == 5 and b in {6, 7}:
            return "published_impossible"

        if (a, b) == (6, 6):
            return "published_impossible"

        if (a, b) == (3, 7) and c % 20 != 0:
            return "published_impossible"

        if (a, b) == (5, 5) and c % 12 != 0:
            return "published_impossible"

        if (a, b) == (4, 10):
            return "published_impossible"

        if (a, b) == (4, 13):
            return "published_impossible"

        #
        # Published finite impossibility families (Sillke)
        #

        if (a, b) == (3, 10) and c in {
            7, 8,
            11, 12, 13,
            15, 16, 17, 18, 19,
            21, 22, 23,
            25,
            29,
        }:
            return "published_impossible"

        if (a, b) == (3, 15) and c in {
            7, 10, 11, 13, 15,
        }:
            return "published_impossible"

        if (a, b) == (3, 20) and c in {
            8, 11,
        }:
            return "published_impossible"

        if (a, b) == (3, 25) and 3 <= c <= 11:
            return "published_impossible"

        return None


T_CATALOGUE = TCatalogue(
    catalogue_name="T",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
)