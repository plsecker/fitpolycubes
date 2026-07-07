#!/usr/bin/env python3
"""
Decomposition Proof and Classifier for Polycubes

This tool proves if rectangular boxes can be tiled/packed by a given polycube
using semigroup decompositions, slab/width splits, and known prime boxes.
"""

import os
import sys
from dataclasses import dataclass
from functools import cache
from typing import Optional

# Set up path for common/catalogue imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.polycube_utils import PENTACUBES
from catalogues.base import Box, Catalogue
from catalogues.registry import CATALOGUES

# Global configuration variables
PIECE_NAME = "F"
PIECE_SIZE = len(PENTACUBES[PIECE_NAME])

catalogue = CATALOGUES[PIECE_NAME]

# ============================================================
# Proof nodes
# ============================================================

class ProofNode:
    pass


@dataclass
class Prime(ProofNode):
    box: Box


@dataclass
class PublishedSolution(ProofNode):
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
class Breadth(ProofNode):
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

    if isinstance(node, Breadth):
        return closes(node.left) and closes(node.right)
    return False


# ============================================================
# Generic Impossibility Rules
# ============================================================

def impossible_reason(box):
    a, b, c = box.a, box.b, box.c

    if a <= 0 or b <= 0 or c <= 0:
        return "dimension"

    if (a * b * c) % PIECE_SIZE != 0:
        return "volume"

    # Delegate piece-specific checks to the active catalogue
    return catalogue.impossible_reason(box)


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

    if box in catalogue.primes:
        return Prime(box)


    a, b, c = box.a, box.b, box.c

    #
    # Row semigroup
    # NOTE: row_families encodes the semigroup generators for fixed (a, b) cross-sections.
    #
    family = getattr(catalogue, "row_families", {}).get((a, b))
    if family:
        decomp = semigroup_decompose(c, family.seeds)
        if decomp and not (len(decomp) == 1 and decomp[0] == c):
            parts = []
            for g in decomp:
                parts.append(classify(Box(a, b, g)))

            candidate = Generator(box, parts)
            if closes(candidate):
                return candidate

    #
    # Width semigroup
    # NOTE: width_splits contains semigroup generators for splitting the 'a' dimension at fixed b.
    #
    width_splits = getattr(catalogue, "width_splits", None)
    if width_splits and b in width_splits:
        decomp = semigroup_decompose(a, width_splits[b])
        if decomp and not (len(decomp) == 1 and decomp[0] == a):
            parts = []
            for w in decomp:
                parts.append(classify(Box(w, b, c)))

            candidate = Generator(box, parts)
            if closes(candidate):
                return candidate

    #
    # Slab decomposition
    #
    for split in range(1, c):
        left = classify(Box(a, b, split))
        right = classify(Box(a, b, c - split))

        candidate = Slab(box, left, right)
        if closes(candidate):
            return candidate

    #
    # Width decomposition
    #
    for split in range(1, a):
        left = classify(Box(split, b, c))
        right = classify(Box(a - split, b, c))

        candidate = Width(box, left, right)
        if closes(candidate):
            return candidate

    #
    # Breadth decomposition
    #
    for split in range(1, b):
        left = classify(Box(a, split, c))
        right = classify(Box(a, b - split, c))

        candidate = Breadth(box, left, right)
        if closes(candidate):
            return candidate

    # Fallback: Check for published solutions only if no proof was found
    if box in {b.canonical() for b in catalogue.published_solutions}:
        return PublishedSolution(box)

    return Unknown(box)


# ============================================================
# Printer
# ============================================================

def dump(node, indent=0):
    pad = " " * indent

    if isinstance(node, PublishedSolution):
        print(f"{pad}PUBLISHED_SOLUTION {node.box}")
        return

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
            dump(p, indent + 2)
        return

    if isinstance(node, Slab):
        print(f"{pad}SLAB {node.box}")
        dump(node.left, indent + 2)
        dump(node.right, indent + 2)
        return

    if isinstance(node, Width):
        print(f"{pad}WIDTH {node.box}")
        dump(node.left, indent + 2)
        dump(node.right, indent + 2)
        return

    if isinstance(node, Breadth):
        print(f"{pad}BREADTH {node.box}")
        dump(node.left, indent + 2)
        dump(node.right, indent + 2)
        return

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Decomposition Proof and Classifier")
    parser.add_argument("piece", nargs="?", default="F", help="Piece name (e.g. F, I, L, N, Y, Z)")
    parser.add_argument("--box", nargs="+", type=int, help="Box dimensions (e.g. 5 5 5 or 5 10 6)")
    parser.add_argument("--stats", action="store_true", help="Print catalogue summary and exit")
    args = parser.parse_args()

    piece_name_upper = args.piece.upper()
    if piece_name_upper not in PENTACUBES:
        print(f"Error: Piece '{args.piece}' not found in PENTACUBES.")
        sys.exit(1)

    if piece_name_upper not in CATALOGUES:
        print(f"Error: No catalogue registered for piece '{piece_name_upper}'.")
        sys.exit(1)

    # Set dynamic globals
    PIECE_NAME = piece_name_upper
    PIECE_SIZE = len(PENTACUBES[PIECE_NAME])
    catalogue = CATALOGUES[PIECE_NAME]
    classify.cache_clear()

    if args.stats:
        catalogue.stats()
        sys.exit(0)

    print(f"Running decomposition proof for piece: {PIECE_NAME} (Size: {PIECE_SIZE})")

    if args.box:
        box_size = tuple(args.box) if len(args.box) == 3 else (args.box[0], args.box[0], args.box[0])
        test = Box(*box_size)
        print(f"Classifying box {test} for {PIECE_NAME}:")
        proof = classify(test)
        dump(proof)
    else:
        # Fallback default test box if none provided
        test = Box(11, 15, 17)
        print(f"Classifying default box {test} for {PIECE_NAME}:")
        proof = classify(test)
        dump(proof)
