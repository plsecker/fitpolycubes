from catalogues.base import Box, Catalogue

# ============================================================
# Raw Primes
# Only lengths explicitly marked "p" in the Sillke N summary.
# ============================================================

RAW_PRIMES = {

    # 2x5
    Box(2, 5, 4),
    Box(2, 5, 5),
    Box(2, 5, 6),
    Box(2, 5, 7),

    # 3x5
    Box(3, 5, 8),
    Box(3, 5, 12),
    Box(3, 5, 13),
    Box(3, 5, 14),
    Box(3, 5, 15),
    Box(3, 5, 17),
    Box(3, 5, 18),
    Box(3, 5, 19),

    # 4x5
    Box(4, 5, 2),

    # 5x5
    Box(5, 5, 2),
    Box(5, 5, 5),

    # 6x5
    Box(5, 6, 2),

    # 7x5
    Box(5, 7, 2),

    # 3x10
    Box(3, 10, 4),
    Box(3, 10, 6),
    Box(3, 10, 7),
    Box(3, 10, 9),

    # 3x15
    Box(3, 15, 4),
    Box(3, 15, 5),
    Box(3, 15, 6),
    Box(3, 15, 7),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}


# ============================================================
# Row semigroup generators
# Only lengths explicitly marked prime in the Sillke N summary.
# ============================================================

ROW_GENERATORS = {
    (2, 5):  [4, 5, 6, 7],
    (3, 5):  [8, 12, 13, 14, 15, 17, 18, 19],
    (4, 5):  [2],
    (5, 5):  [2, 5],
    (5, 6):  [2],
    (5, 7):  [2],
    (3, 10): [4, 6, 7, 9],
    (3, 15): [4, 5, 6, 7],
}


# ============================================================
# Width semigroup generators
# Leave empty - insufficient information in the supplied summary.
# ============================================================

WIDTH_GENERATORS = {}


# ============================================================
# Searched with no solution found
# Nothing explicit was supplied.
# ============================================================

SEARCHED_NO_SOLUTION = set()


# ============================================================
# N-specific catalogue with impossibility rules
# ============================================================

class NCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a <= 1:
            return "published_impossible"

        if (a, b) in {(2, 2), (2, 3), (3, 3)}:
            return "published_impossible"

        if (a, b) == (3, 5):
            if c in {4, 5, 6, 7, 9, 10, 11}:
                return "published_impossible"

        # TODO: decode N no-strip impossibility rule
        # TODO: decode Zx{3,5} impossibility rule

        return None


N_CATALOGUE = NCatalogue(
    catalogue_name="N",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_generators=ROW_GENERATORS,
    width_generators=WIDTH_GENERATORS,
)
