"""
Polycube Exact Cover Solver

Created on Sun May  1 19:43:13 2016
@author: Philip
"""

import os
import sys
import numpy as np

PENTACUBES = {
    "F": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 1], [0, 2, 0]]),
    "I": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0]]),
    "L": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [3, 1, 0]]),
    "N": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [3, 1, 0]]),
    "P": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]]),
    "T": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 0, 1]]),
    "U": np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0]]),
    "V": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [0, 2, 0]]),
    "W": np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]),
    "X": np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [1, 2, 0], [2, 1, 0]]),
    "Y": np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [2, 1, 0]]),
    "Z": np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]),
}

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM
from common.utils import Timer, timer
from common.polycube_utils import (generate_placements, build_exact_cover_data, 
                                   filter_and_reindex_placements)
from common.algorithm_x import solve

def run_solver(piece, box_size, output_file, break_symmetry=False):
    print(f"Generating placements for piece in {box_size} box...")
    with Timer() as t:
        placements, canonical_p_000 = generate_placements(piece, box_size, break_symmetry=break_symmetry)
    print(f"Placements found: {len(placements)}")

    if break_symmetry and canonical_p_000:
        placements = filter_and_reindex_placements(placements, canonical_p_000)

    X, box_list = build_exact_cover_data(placements, box_size)

    print("Starting solver...")
    with Timer() as t:
        solutions = solve(X, placements)
        
        with open(output_file, "w") as f:
            f.write(f"# Polycube solutions - Standard (Box: {box_size})\n")

        c = 0
        for sol in solutions:
            c += 1
            if c % 100 == 0:
                print(f"Found {c} solutions...")

            sol_str = "".join([str(placements[p_index]) for p_index in sol])
            with open(output_file, "a") as f:
                f.write(f"{c}\n{sol_str}\n")
    
    print(f"Total solutions found: {c}")
    print(f"Results written to {output_file}")

if __name__ == "__main__":
    # Example polycube piece (N pentacube)
    p = np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[2, 0, 1],[3, 0, 1]])   # N piece
    
    output_fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/solutions_n.dat")
    
    run_solver(p, 5, output_fname, break_symmetry=True)
