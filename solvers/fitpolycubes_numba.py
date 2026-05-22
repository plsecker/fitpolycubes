"""
Polycube Exact Cover Solver - Optimized with Numba

Created on Sun May  1 19:43:13 2016
@author: Philip
"""

import os
import sys
import numpy as np

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.rotmatrix import RM
from common.utils import Timer, timer
from common.polycube_utils import (generate_placements, build_exact_cover_data, 
                                   filter_and_reindex_placements, PENTACUBES)
from common.algorithm_x_numba import solve

def run_solver(piece, box_size, output_file, break_symmetry=False):
    print(f"Generating placements for piece in {box_size} box...")
    with Timer() as t:
        placements, canonical_p_000 = generate_placements(piece, box_size, break_symmetry=break_symmetry)
    print(f"Placements found: {len(placements)}")

    if break_symmetry and canonical_p_000:
        placements = filter_and_reindex_placements(placements, canonical_p_000)

    X, box_list = build_exact_cover_data(placements, box_size)

    print("Starting Numba solver...")
    with Timer() as t:
        solutions = solve(X, placements, box_list)
        
        with open(output_file, "w") as f:
            f.write(f"# Polycube solutions - Numba (Box: {box_size})\n")

        c = 0
        for sol in solutions:
            # sol is a list of row indices padded with -1
            clean_sol = [idx for idx in sol if idx != -1]
            
            # We expect 25 pieces for a 5x5x5 box
            if len(clean_sol) != 25:
                continue
                
            c += 1
            if c % 100 == 0:
                print(f"Found {c} solutions...")

            sol_str = "".join([str(placements[p_index]) for p_index in clean_sol])
            with open(output_file, "a") as f:
                f.write(f"{c}\n{sol_str}\n")
    
    print(f"Total solutions written: {c}")
    print(f"Results written to {output_file}")

if __name__ == "__main__":
    piece_name = sys.argv[1] if len(sys.argv) > 1 else "N"
    if piece_name not in PENTACUBES:
        print(f"Error: Piece '{piece_name}' not found in PENTACUBES.")
        print(f"Available pieces: {', '.join(sorted(PENTACUBES.keys()))}")
        sys.exit(1)
        
    p = PENTACUBES[piece_name]
    print(f"Solving for {piece_name} pentacube (Numba solver)...")
    
    output_fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"data/solutions_numba_{piece_name.lower()}.dat")
    
    run_solver(p, 5, output_fname, break_symmetry=True)
