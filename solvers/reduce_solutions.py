import os
import sys
import ast
from collections import defaultdict

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.polycube_utils import PENTACUBES


def find_all_files(piece_name=None):
    """Find all valid solution files for the given piece."""
    suffixes = ["hybrid", "numba", "fast", "mp"]
    found_files = []
    
    def is_valid_file(p):
        if not os.path.exists(p):
            return False
        if os.path.getsize(p) < 50:
            return False
        return True

    # Priority 1: Specific piece requested
    if piece_name:
        for s in suffixes:
            paths = [
                f"data/solutions_{s}_{piece_name.lower()}.dat",
                f"solutions_{s}_{piece_name.lower()}.dat",
                os.path.join(os.path.dirname(__file__), f"../data/solutions_{s}_{piece_name.lower()}.dat")
            ]
            for p in paths:
                if is_valid_file(p) and p not in found_files:
                    found_files.append(p)

    # Priority 2: Generic files (only if no specific piece files found)
    if not found_files:
        for s in suffixes:
            paths = [
                f"data/solutions_{s}.dat",
                f"solutions_{s}.dat",
                os.path.join(os.path.dirname(__file__), f"../data/solutions_{s}.dat")
            ]
            for p in paths:
                if is_valid_file(p) and p not in found_files:
                    found_files.append(p)
                
    return found_files


def parse_solutions(filepath, aggregated_solutions):
    """Parses raw polycube lines from the .dat file format and adds to aggregation."""
    current_id = None
    count = 0
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.isdigit():
                current_id = int(line)
                continue
            if current_id is not None:
                # Handle both list format [...][...] and tuple format (...)(...)
                formatted = line.replace('][', '], [').replace(')(', '), (')
                try:
                    pieces = ast.literal_eval(f"[{formatted}]")
                    # Use the normalized frozenset of pieces as key to avoid duplicates across files
                    normalized_pieces = []
                    for p in pieces:
                        normalized_pieces.append(frozenset(p))
                    sol_key = frozenset(normalized_pieces)
                    
                    if sol_key not in aggregated_solutions:
                        aggregated_solutions[sol_key] = pieces
                        count += 1
                except Exception as e:
                    print(f"Failed to parse line for ID {current_id} in {filepath}: {e}")
    return count


def get_48_transformations():
    """Generates all 48 combined 3D rotations and reflections."""
    transforms = []
    for p in [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]:
        for sx in [1, -1]:
            for sy in [1, -1]:
                for sz in [1, -1]:
                    transforms.append((p, (sx, sy, sz)))
    return transforms


def apply_transform(solution, transform):
    """Applies a spatial transformation and normalizes coordinates back to a 0..4 bounding box."""
    p, s = transform
    new_solution = []
    for piece in solution:
        new_piece = []
        for coord in piece:
            reordered = [coord[p[0]], coord[p[1]], coord[p[2]]]
            transformed = (reordered[0] * s[0], reordered[1] * s[1], reordered[2] * s[2])
            new_piece.append(transformed)
        new_solution.append(new_piece)

    # Translate minimum boundaries to align perfectly with 0,0,0
    all_coords = [c for piece in new_solution for c in piece]
    min_x = min(c[0] for c in all_coords)
    min_y = min(c[1] for c in all_coords)
    min_z = min(c[2] for c in all_coords)

    normalized_solution = []
    for piece in new_solution:
        normalized_piece = frozenset((x - min_x, y - min_y, z - min_z) for x, y, z in piece)
        normalized_solution.append(normalized_piece)

    return frozenset(normalized_solution)


def print_grid(pieces_list):
    """Visualizes the 3D polycube grid layer by layer matching Silke's letter format."""
    grid = {}
    for piece_idx, piece in enumerate(pieces_list):
        for x, y, z in piece:
            grid[(x, y, z)] = piece_idx

    label_map = {}
    next_letter_idx = 0
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    # Order scanning: Z -> Y -> X to match standard appearance indexing
    for z in range(5):
        for y in range(5):
            for x in range(5):
                p_idx = grid.get((x, y, z))
                if p_idx is not None and p_idx not in label_map:
                    if next_letter_idx < len(letters):
                        label_map[p_idx] = letters[next_letter_idx]
                        next_letter_idx += 1
                    else:
                        label_map[p_idx] = '?'

    for z in range(5):
        print(f"Layer Z={z}:")
        for y in range(5):
            row_chars = []
            for x in range(5):
                p_idx = grid.get((x, y, z))
                char = label_map[p_idx] if p_idx is not None else '.'
                row_chars.append(char)
            print(" ".join(row_chars))
        print()


def main():
    piece_name = sys.argv[1] if len(sys.argv) > 1 else None
    if piece_name and piece_name.upper() not in PENTACUBES:
        print(f"Error: Piece '{piece_name}' not found in PENTACUBES.")
        print(f"Available pieces: {', '.join(sorted(PENTACUBES.keys()))}")
        sys.exit(1)

    filepaths = find_all_files(piece_name)
    if not filepaths:
        target = f"'{piece_name}' " if piece_name else ""
        print(f"Error: Could not locate solution files for {target}in any standard path combinations.")
        return

    aggregated_solutions = {}
    for fp in filepaths:
        print(f"Loading data from: {fp}")
        count = parse_solutions(fp, aggregated_solutions)
        print(f"  Added {count} new unique solutions.")

    raw_solutions_list = list(aggregated_solutions.values())
    print(f"\nTotal aggregated unique raw solutions: {len(raw_solutions_list)}\n")

    transforms = get_48_transformations()
    unique_groups = []

    print("Grouping solutions via geometric equivalence...")
    total = len(raw_solutions_list)
    
    # Progress tracking variables
    last_p = -1

    # Group solutions via geometric equivalence
    for i, pieces in enumerate(raw_solutions_list):
        # Manual progress bar
        progress = int((i / total) * 100)
        if progress > last_p:
            sys.stdout.write(f"\rProgress: [{('=' * (progress // 2)).ljust(50)}] {progress}% ({i}/{total})")
            sys.stdout.flush()
            last_p = progress

        found_match = False
        # To optimize, we can check if the current piece (identity) is already in any group's symmetry set.
        # However, it's safer and easier to just transform the NEW piece once per group.
        # Actually, the most efficient way is to pre-calculate all 48 symmetries of the FIRST piece 
        # and see if it matches any existing group.
        
        # Identity transform for the new candidate
        identity_transform = ((0, 1, 2), (1, 1, 1))
        candidate_rep = apply_transform(pieces, identity_transform)

        for group in unique_groups:
            # Check if this candidate_rep matches ANY of the symmetries of the group representative
            if candidate_rep in group['symmetries']:
                group['match_count'] += 1
                found_match = True
                break

        if not found_match:
            # Initialize a new unique fundamental layout group
            # We cache all 48 symmetries of the representative to speed up future checks
            symmetries = set()
            for t in transforms:
                symmetries.add(apply_transform(pieces, t))
            
            unique_groups.append({
                'representative': candidate_rep,
                'symmetries': symmetries,
                'match_count': 1,
                'first_raw_solution': pieces
            })

    print(f"\n\nFound {len(unique_groups)} fundamental unique solutions!\n")

    for idx, group in enumerate(unique_groups, 1):
        print(f"=========================================")
        print(f"   UNIQUE SOLUTION {idx} SELECTION")
        print(f"=========================================")
        print(f"Matches {group['match_count']} raw file configurations (including symmetries/duplicates)")
        print(f"Representative Grid Layout:")
        print_grid(group['first_raw_solution'])
        print("\n")


if __name__ == "__main__":
    main()