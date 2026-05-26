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
    if isinstance(box_size, int):
        box_size = (box_size, box_size, box_size)
    
    # Calculate expected number of pieces
    volume = box_size[0] * box_size[1] * box_size[2]
    num_cubes_per_piece = len(piece)
    if volume % num_cubes_per_piece != 0:
        print(f"Warning: Box volume {volume} is not divisible by piece size {num_cubes_per_piece}")
        # We might still want to try to fill it as much as possible, 
        # but for exact cover it must be divisible.
    
    expected_pieces = volume // num_cubes_per_piece
    
    print(f"Generating placements for piece in {box_size} box...")
    with Timer() as t:
        placements, canonical_p_000 = generate_placements(piece, box_size, break_symmetry=break_symmetry)
    print(f"Placements found: {len(placements)}")

    if break_symmetry and canonical_p_000:
        placements = filter_and_reindex_placements(placements, canonical_p_000)

    X, box_list = build_exact_cover_data(placements, box_size)

    print(f"Starting Numba solver (expecting {expected_pieces} pieces)...")
    with Timer() as t:
        solutions = solve(X, placements, box_list, solution_length=expected_pieces)
        
        with open(output_file, "w") as f:
            f.write(f"# Polycube solutions - Numba (Box: {box_size}, Pieces: {expected_pieces})\n")

        c = 0
        for sol in solutions:
            # sol is a list of row indices padded with -1
            clean_sol = [idx for idx in sol if idx != -1]
            
            # Verify solution length
            if len(clean_sol) != expected_pieces:
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
    import argparse
    parser = argparse.ArgumentParser(description="Polycube Exact Cover Solver (Numba)")
    parser.add_argument("piece", nargs="?", default="N", help="Piece name (e.g. N, Y, L)")
    parser.add_argument("--box", nargs="+", type=int, default=[5, 5, 5], help="Box dimensions (e.g. 5 5 5 or 4 4 5)")
    parser.add_argument("--no-symmetry", action="store_false", dest="symmetry", help="Disable symmetry breaking")
    parser.set_defaults(symmetry=True)
    
    args = parser.parse_args()
    
    if args.piece not in PENTACUBES:
        print(f"Error: Piece '{args.piece}' not found in PENTACUBES.")
        print(f"Available pieces: {', '.join(sorted(PENTACUBES.keys()))}")
        sys.exit(1)
        
    p = PENTACUBES[args.piece]
    box_size = tuple(args.box) if len(args.box) == 3 else (args.box[0], args.box[0], args.box[0])
    
    print(f"Solving for {args.piece} pentacube (Numba solver)...")
    print(f"Box size: {box_size}")
    
    box_str = "x".join(map(str, box_size))
    output_fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"data/solutions_numba_{args.piece.lower()}_{box_str}.dat")
    
    run_solver(p, box_size, output_fname, break_symmetry=args.symmetry)
