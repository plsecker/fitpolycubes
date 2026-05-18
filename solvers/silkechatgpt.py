#!/usr/bin/env python3

"""
Translate Torsten Sillke's cube5 N-pentomino solutions into
explicit coordinate notation.

Input format:
- 4 solutions printed side-by-side
- each solution consists of 5 layers
- each layer is 5x5
- layers separated vertically every 5 rows

Output format:
[
    [(x,y,z), ... 5 coords ...],
    ...
]

Assumptions:
- each repeated integer label is one pentomino
- 0 means "blank formatting cell" and is ignored
"""

from collections import defaultdict
import re


RAW = r"""
58 58 58 48 48 | 59 50 50 43 40 | 59 47 43 42 38 | 58 59 56 56 38
 59 59 58 58 39 | 59 59 50 50 50 | 59 47 43 42 39 | 58 59 44 44 44
 60 59 59 59 39 | 60 59 48 48 48 | 59 59 43 42 39 | 59 59 45 45 45
 60 49 49 43 39 | 60 59 51 51 51 | 60 59 48 48 48 | 59 47 47 46 46
 60 50 49 49 49 | 60 51 51 41 38 | 60 48 48 46 46 | 60 60 47 47 47

 55 48 48 48 42 | 56 53 43 43 40 | 57 57 57 41 38 | 56 56 56 40 38
 60 53 53 53 38 | 60 47 47 47 37 | 60 47 57 57 38 | 58 44 44 41 38
 60 54 54 54 38 | 60 48 48 47 47 | 60 47 43 42 39 | 58 45 45 41 41
 56 56 56 43 39 | 57 49 58 58 38 | 60 47 43 42 39 | 58 46 46 46 41
 57 50 56 56 39 | 58 58 58 41 38 | 58 46 46 46 39 | 57 60 60 60 41

 55 47 47 42 42 | 56 53 43 40 40 | 54 54 54 41 41 | 53 53 53 40 40
 53 53 47 47 47 | 56 46 46 46 37 | 55 55 55 40 38 | 54 54 54 39 38
 54 54  0  0 38 |  0  0  0 46 46 |  0  0  0 40 40 |  0  0  0 39 39
  0  0  0 43 38 | 57 49  0  0 38 | 56 56  0  0 40 | 55 55  0  0 39
 57 50 50 43 38 | 55 55 55 41 41 | 58 56 56 56 40 | 57 55 55 55 39

 55 55 46 42 37 | 53 53 43 40 37 | 51 51 54 54 41 | 50 50 53 53 40
 52 46 46 41 37 | 56 45 45 45 37 | 52 52 55 55 38 | 51 51 54 54 38
 52 46 44 41 37 | 54 54 54 45 45 | 53 53 53 44 44 | 52 52 52 42 42
 52 46 44 41 41 | 57 49 54 54 38 | 58 44 44 44 37 | 57 42 42 42 37
 57 57 50 43 41 | 57 49 55 55 41 | 58 45 45 45 37 | 57 43 43 43 37

 52 55 44 42 40 | 53 52 42 39 37 | 49 51 51 51 41 | 48 50 50 50 40
 52 51 44 40 40 | 56 52 42 39 39 | 49 52 52 52 37 | 48 51 51 51 37
 51 51 44 40 37 | 52 52 42 42 39 | 49 49 53 53 37 | 48 48 52 52 37
 51 45 45 40 37 | 52 44 44 42 39 | 58 49 50 50 37 | 57 48 49 49 37
 51 57 45 45 45 | 57 49 44 44 44 | 50 50 50 45 45 | 49 49 49 43 43
 """


def parse_solution_columns(raw):
    lines = [line.rstrip() for line in raw.strip().splitlines()]
    lines = [line for line in lines if line.strip()]

    # Split each line into the 4 solution columns
    split_lines = []
    for line in lines:
        cols = [c.strip() for c in line.split("|")]
        if len(cols) != 4:
            raise ValueError(f"Expected 4 columns: {line}")
        split_lines.append(cols)

    # Organize:
    # solutions[solution_index][z][y][x]
    solutions = [[[None for _ in range(5)] for _ in range(5)] for _ in range(4)]

    for global_y, cols in enumerate(split_lines):
        z = global_y // 5
        y = global_y % 5

        for s, col in enumerate(cols):
            nums = [int(n) for n in re.findall(r"-?\d+", col)]

            if len(nums) != 5:
                raise ValueError(f"Expected 5 numbers: {col}")

            solutions[s][z][y] = nums

    return solutions


def solution_to_coords(solution):
    """
    Convert one solution:
        solution[z][y][x]
    into:
        label -> [(x,y,z), ...]
    """
    pieces = defaultdict(list)

    for z in range(5):
        for y in range(5):
            for x in range(5):
                label = solution[z][y][x]

                if label == 0:
                    continue

                pieces[label].append((x, y, z))

    return dict(pieces)


def normalize_piece(coords):
    """
    Sort coordinates for stable output.
    """
    return sorted(coords)


def print_solution(idx, pieces):
    print(f"\n# Solution {idx + 1}\n")

    for label in sorted(pieces):
        coords = normalize_piece(pieces[label])

        print(f"{label}: {coords}")

        # sanity checks
        if len(coords) != 5:
            print(f"  ERROR: piece {label} has {len(coords)} cells")


def main():
    solutions = parse_solution_columns(RAW)

    for idx, sol in enumerate(solutions):
        pieces = solution_to_coords(sol)
        print_solution(idx, pieces)


if __name__ == "__main__":
    main()