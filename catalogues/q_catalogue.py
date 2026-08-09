from catalogues.base import Box, Catalogue, Family

# Piece Q = Shirakawa 5-22 (registry: kurnell=61, shirakawa_piece=22).
#
# Sources (evidence hierarchy):
#   1. Live Shirakawa page 5-22 ("Complete."):
#      https://puzzlewillbeplayed.com/Shirakawa/5-22.html
#   2. No lossless transcription exists in shirakawa/.
#   3. Sillke qu5.61 (complete):
#      http://www.mathematik.uni-bielefeld.de/~sillke/PENTA/qu5.61
#
# Both sources agree on the one-sided 3D prime boxes (all Sillke 1993):
#   2x2x5 (prime minimal), 2x3x5, 3x7x25, 3x9x15, 5x5x9, 5x7x7.
# (Sillke's summary line omits 3x9x15, but his family listing marks
#  "3x15x 9p" = 3x9x15 as prime, and Shirakawa lists it too.)
#
# Sillke also gives the one-sided 4D prime 3x3x3x5, which is out of scope
# for this 3D catalogue.
#
# Impossible families (Sillke qu5.61):
#   (A) 3x3xN strip (two sides open)  -> all 3x3xN
#   (B) 3x5xu with u odd              -> 3x5xN, N odd
#   (C) 5x5x5, 5x5x7, 3x7x15
#
# The previous catalogue carried many solver-discovered primes (e.g.
# 3x3x10, 3x3x15, 3x5x6, 3x5x14, 4x5x6, 5x7x9, ...) that are not
# supported by any published source and, for the 3x3xN and odd 3x5xN
# families, are actually impossible. They have been removed.

RAW_PRIMES = {
    # 2x2
    Box(2, 2, 5),  # prime minimal -- Sillke 1993 / Shirakawa 5-22
    # 2x3
    Box(2, 3, 5),  # prime -- Sillke 1993 / Shirakawa 5-22
    # 3x7
    Box(3, 7, 25),  # prime -- Sillke 1993 / Shirakawa 5-22
    # 3x9
    Box(3, 9, 15),  # prime -- Sillke 1993 / Shirakawa 5-22
    # 5x5
    Box(5, 5, 9),  # prime -- Sillke 1993 / Shirakawa 5-22
    # 5x7
    Box(5, 7, 7),  # prime -- Sillke 1993 / Shirakawa 5-22
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# Smallest RAW_PRIME with all three dimensions odd.
# 5x5x9 is a published prime (Sillke 1993 / Shirakawa 5-22, see RAW_PRIMES
# above) and matches Sicherman's published minimum for Q.
MINIMAL_ODD = Box(5, 5, 9)

# No RAW_PRIME with all three dimensions even exists in the current
# catalogue: the even-volume prime 2x2x5 has an odd third dimension and all
# other primes are odd boxes. MINIMAL_ODD / MINIMAL_EVEN denote primitive
# boxes only, so the derived composite 2x2x10 (two stacked 2x2x5 primes) is
# deliberately not reported here.
MINIMAL_EVEN = None

# Every published impossibility is encoded in impossible_reason below, so
# there is no separate searched-no-solution set.
SEARCHED_NO_SOLUTION = {
}

ROW_FAMILIES = {
}

WIDTH_SPLITS = {
}


class QCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.canonical().a, box.canonical().b, box.canonical().c

        # Sillke (A): 3x3xN strip (two sides open) is impossible for all N.
        if a == 3 and b == 3:
            return "published_impossible"

        # Sillke (B): 3x5xN with N odd is impossible.
        if a == 3 and b == 5 and c % 2 == 1:
            return "published_impossible"

        # Sillke (C): specific impossible boxes.
        if box in {
            Box(5, 5, 5),
            Box(5, 5, 7),
            Box(3, 7, 15),
        }:
            return "published_impossible"

        return None


Q_CATALOGUE = QCatalogue(
    catalogue_name="Q",
    primes=PRIMES,
    searched_no_solution=SEARCHED_NO_SOLUTION,
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
