from catalogues.base import Box, Catalogue, Family

RAW_PRIMES = {

    # 3x10
    Box(3,6,10),
    Box(3,7,10),
    Box(3,8,10),
    Box(3,9,10),
    Box(3,10,10),
    Box(3,10,11),

    # 3x15
    Box(3,6,15),
    Box(3,7,15),
    Box(3,8,15),
    Box(3,9,15),
    Box(3,11,15),

    # 4x5
    Box(4,5,10),
    Box(4,5,12),
    Box(4,5,13),
    Box(4,5,14),
    Box(4,5,15),
    Box(4,5,16),
    Box(4,5,17),
    Box(4,5,18),
    Box(4,5,19),
    Box(4,5,21),

    # 4x6
    Box(4,6,20), # Shirakawa
    Box(4,6,25),

    # 4x10
    Box(4,7,10),
    Box(4,8,10),
    Box(4,9,10),
    Box(4,10,11),

    # 4x15
    Box(4,6,15),
    Box(4,7,15),
    Box(4,8,15),
    Box(4,9,15),

    # 5x5
    Box(5,5,8),
    Box(5,5,10),
    Box(5,5,11),
    Box(5,5,12),
    Box(5,5,13),
    Box(5,5,14),
    Box(5,5,15),
    Box(5,5,17),

    # 5x6
    Box(5,6,6),
    Box(5,6,7),
    Box(5,6,8),
    Box(5,6,9),
    Box(5,6,10),  # Shirakawa 2015 prime
    Box(5,6,11),

    # 5x7
    Box(5,7,8),
    Box(5,7,9),
    Box(5,7,10),
    Box(5,7,11),
    Box(5,7,13),

    # 5x8
    Box(5,8,8),
    Box(5,8,9),

    # 5x9
    Box(5,9,9),
    Box(5,9,11),

}

SEARCHED_NO_SOLUTION = {
    Box(4,6,10)
}

ROW_FAMILIES = {
    # (3,10): Family(seeds=[6,7,8,9,10,11], period=6),
    # (3,15): Family(seeds=[6,7,8,9,11], period=6),
    # (4,10): Family(seeds=[5,7,8,9,11], period=5),
    # (4,15): Family(seeds=[5,6,7,8,9], period=5),
    # (5,5): Family(seeds=[8,10,11,12,13,14,15,17], period=8),
    # (5,6): Family(seeds=[6,7,8,9,10,11], period=6),
    # (5,7): Family(seeds=[6,8,9,10,11,13], period=6),
    # (5,8): Family(seeds=[5,6,7,8,9], period=5),
    # (5,9): Family(seeds=[6,7,8,9,11], period=6),
    # (5,10): Family(seeds=[4,5,7], period=4),
    # (5,11): Family(seeds=[5,6,7,9], period=5),
}

WIDTH_SPLITS = {
    # 10: [3,4,5],
    # 15: [3,4,5,6,7,8,9],
}


class FCatalogue(Catalogue):
    def impossible_reason(self, box: Box) -> str | None:
        a, b, c = box.a, box.b, box.c

        if a == 1:
            return "published_impossible"

        # Historical note: An empirical rule for a == 2 ("Empirically, no thickness-2 
        # box is tileable by F") was removed because it generalized from finite search 
        # evidence without a formal proof or published authoritative source.

        if box in self.searched_no_solution:
            return "searched_no_solution"

        if a == 3 and b in {3, 4, 5}:
            return "published_impossible"

        if a == 4 and b in {3, 4}:
            return "published_impossible"

        if (a, b) == (4, 5):
            if c in {3, 4, 5, 6, 7, 8, 9, 11}:
                return "published_impossible"

        if (a, b) == (5, 5):
            if c in {3, 4, 5, 6, 7, 9}:
                return "published_impossible"

        if box == Box(5, 7, 7):
            return "published_impossible"

        return None


F_CATALOGUE = FCatalogue(
    catalogue_name="F",
    primes={b.canonical() for b in RAW_PRIMES},
    searched_no_solution={b.canonical() for b in SEARCHED_NO_SOLUTION},
    row_families=ROW_FAMILIES,
    width_splits=WIDTH_SPLITS,
    published_solutions=set(),
)
