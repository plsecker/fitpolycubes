#!/usr/bin/env python3

from dataclasses import dataclass
from functools import cache
from typing import Optional


# ============================================================
# Box
# ============================================================

@dataclass(frozen=True, order=True)
class Box:
    a: int
    b: int
    c: int

    def canonical(self):
        return Box(*sorted((self.a, self.b, self.c)))

    def __str__(self):
        return f"{self.a}x{self.b}x{self.c}"


# ============================================================
# Proof nodes
# ============================================================

class ProofNode:
    pass


@dataclass
class Prime(ProofNode):
    box: Box


@dataclass
class Impossible(ProofNode):
    box: Box
    reason: str


@dataclass
class Unknown(ProofNode):
    box: Box


@dataclass
class Slab(ProofNode):
    box: Box
    left: ProofNode
    right: ProofNode


@dataclass
class Width(ProofNode):
    box: Box
    left: ProofNode
    right: ProofNode


@dataclass
class Generator(ProofNode):
    box: Box
    parts: list



# ============================================================
# Proof closure
# ============================================================

def closes(node):

    if isinstance(node, Prime):
        return True

    if isinstance(node, Impossible):
        return False

    if isinstance(node, Unknown):
        return False

    if isinstance(node, Generator):
        return all(closes(p) for p in node.parts)

    if isinstance(node, Slab):
        return closes(node.left) and closes(node.right)

    if isinstance(node, Width):
        return closes(node.left) and closes(node.right)

    return False

# ============================================================
# Prime database
# ============================================================

RAW_PRIMES = {

    # 3x10
    Box(3,10,10),
    Box(3,10,11),
    Box(3,10,12),
    Box(3,10,13),
    Box(3,10,14),
    Box(3,10,15),

    # 3x15
    Box(3, 15, 6),
    Box(3, 15, 7),
    Box(3, 15, 8),
    Box(3, 15, 9),
    Box(3, 15, 10),
    Box(3, 15, 11),

    # 4x10
    Box(4,10,10),
    Box(4,10,12),
    Box(4,10,13),
    Box(4,10,14),
    Box(4,10,15),

    # 4x15
    Box(4,15,5),
    Box(4,15,6),
    Box(4,15,7),
    Box(4,15,8),
    Box(4,15,9),

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
    # Box(5,6,10),
    Box(5,6,11),

    # 5x7
    Box(5,7,8),
    Box(5,7,9),
    Box(5,7,10),
    Box(5,7,11),
    Box(5,7,12),
    Box(5,7,13),

    # 5x8
    Box(5,8,5),
    Box(5,8,6),
    Box(5,8,7),
    Box(5,8,8),
    Box(5,8,9),

    # 5x9
    Box(5,9,6),
    Box(5,9,7),
    Box(5,9,8),
    Box(5,9,9),
    Box(5,9,10),
    Box(5,9,11),

    # 5x10
    Box(5,10,4),
    Box(5,10,5),
    # Box(5,10,6),
    Box(5,10,7),

    # 5x11
    Box(5,11,5),
    Box(5,11,6),
    Box(5,11,7),
    # Box(5,11,8),
    Box(5,11,9),
}

PRIMES = {b.canonical() for b in RAW_PRIMES}

# ============================================================
# Special cases
# ============================================================

SEARCHED_NO_SOLUTION = {
    Box(4,6,10)
}


# ============================================================
# Row semigroups
# ============================================================

ROW_GENERATORS = {

    (3,10): [10,11,12,13,14,15],
    (3,15): [6,7,8,9,10,11],

    (4,10): [10,12,13,14,15],
    (4,15): [5,6,7,8,9],

    (5,6): [6,7,8,9,10,11],
    (5,7): [8,9,10,11,12,13],
    (5,8): [5,6,7,8,9],
    (5,9): [6,7,8,9,10,11],
    (5,10): [4,5,6,7],
    (5,11): [5,6,7,8,9],

    # examples
    (6,6): [5],
    (6,7): [5],
    (6,8): [5],
    (6,9): [5],

    (3,7): [10,15],
}


# ============================================================
# Width semigroups
# ============================================================

WIDTH_GENERATORS = {
    10: [3,4,5],
    15: [3,4,5,6,7,8,9],
}


# ============================================================
# Impossibility rules
# ============================================================

def impossible_reason(box):

    a,b,c = box.a, box.b, box.c

    if box in SEARCHED_NO_SOLUTION:
        return "searched_no_solution"

    if (a*b*c) % 5:
        return "volume"

    if a == b == c:
        return "cube"

    if a == 3 and b in {3,4,5}:
        return "published_impossible"

    if a == 4 and b in {3,4}:
        return "published_impossible"

    if (a,b) == (4,5):
        if c in {3,4,5,6,7,8,9,11}:
            return "published_impossible"

    if (a,b) == (5,5):
        if c in {3,4,5,6,7,9}:
            return "published_impossible"

    if box == Box(5,7,7):
        return "published_impossible"

    return None


# ============================================================
# Semigroup decomposition
# ============================================================

def semigroup_decompose(target, generators):

    generators = sorted(generators, reverse=True)

    result = []

    def dfs(remaining, start):

        if remaining == 0:
            return True

        for i in range(start, len(generators)):

            g = generators[i]

            if g > remaining:
                continue

            result.append(g)

            if dfs(remaining - g, i):
                return True

            result.pop()

        return False

    if dfs(target, 0):
        return result

    return None


# ============================================================
# Classifier
# ============================================================

@cache
def classify(box):

    box = box.canonical()

    reason = impossible_reason(box)

    if reason:
        return Impossible(box, reason)

    if box in PRIMES:
        return Prime(box)

    a,b,c = box.a, box.b, box.c

    #
    # Row semigroup
    #

    gens = ROW_GENERATORS.get((a,b))

    if gens:

        decomp = semigroup_decompose(c, gens)

        if decomp and not (len(decomp) == 1 and decomp[0] == c):

            parts = []

            for g in decomp:
                parts.append(classify(Box(a,b,g)))

            candidate = Generator(box, parts)

            if closes(candidate):
                return candidate

    #
    # Width semigroup
    #

    if b in WIDTH_GENERATORS:

        decomp = semigroup_decompose(a, WIDTH_GENERATORS[b])

        if decomp and not (len(decomp) == 1 and decomp[0] == a):

            parts = []

            for w in decomp:
                parts.append(classify(Box(w,b,c)))

            candidate = Generator(box, parts)

            if closes(candidate):
                return candidate

    #
    # Slab decomposition
    #

    for split in range(1, c):

        left = classify(Box(a,b,split))
        right = classify(Box(a,b,c-split))

        candidate = Slab(box, left, right)

        if closes(candidate):
            return candidate

    #
    # Width decomposition
    #

    for split in range(1, a):

        left = classify(Box(split,b,c))
        right = classify(Box(a-split,b,c))

        candidate = Width(box, left, right)

        if closes(candidate):
            return candidate

    return Unknown(box)


# ============================================================
# Printer
# ============================================================

def dump(node, indent=0):

    pad = " " * indent

    if isinstance(node, Prime):
        print(f"{pad}PRIME {node.box}")
        return

    if isinstance(node, Impossible):
        print(f"{pad}IMPOSSIBLE {node.box} [{node.reason}]")
        return

    if isinstance(node, Unknown):
        print(f"{pad}UNKNOWN {node.box}")
        return

    if isinstance(node, Generator):
        print(f"{pad}GENERATOR {node.box}")
        for p in node.parts:
            dump(p, indent+2)
        return

    if isinstance(node, Slab):
        print(f"{pad}SLAB {node.box}")
        dump(node.left, indent+2)
        dump(node.right, indent+2)
        return

    if isinstance(node, Width):
        print(f"{pad}WIDTH {node.box}")
        dump(node.left, indent+2)
        dump(node.right, indent+2)
        return


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print(classify(Box(5,10,6)))
    print(classify(Box(5,11,8)))
    test = Box(5,10,6)

    proof = classify(test)

    dump(proof)