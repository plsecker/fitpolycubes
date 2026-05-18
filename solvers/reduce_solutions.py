import os
import ast
from collections import defaultdict


def find_file():
    """Look for solutions_fast.dat in standard relative positions to prevent FileNotFoundError."""
    possible_paths = [
        "data/solutions_fast.dat",
        "solutions_fast.dat",
        os.path.join(os.path.dirname(__file__), "../data/solutions_hybrid.dat"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None


def parse_solutions(filepath):
    """Parses raw polycube lines from the .dat file format."""
    solutions = {}
    current_id = None
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.isdigit():
                current_id = int(line)
                continue
            if current_id is not None:
                formatted = line.replace(')((', '), ((')
                try:
                    pieces = ast.literal_eval(f"[{formatted}]")
                    solutions[current_id] = pieces
                except Exception as e:
                    print(f"Failed to parse line for ID {current_id}: {e}")
    return solutions


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
    filepath = find_file()
    if not filepath:
        print("Error: Could not locate 'solutions_fast.dat' in any standard path combinations.")
        return

    print(f"Loading data from: {filepath}")
    raw_solutions = parse_solutions(filepath)
    print(f"Parsed {len(raw_solutions)} raw solutions.\n")

    transforms = get_48_transformations()
    unique_groups = []

    # Group solutions via geometric equivalence
    for raw_id, pieces in sorted(raw_solutions.items()):
        found_match = False
        for group in unique_groups:
            for t in transforms:
                transformed_set = apply_transform(pieces, t)
                if transformed_set == group['representative']:
                    group['raw_ids'].append(raw_id)
                    found_match = True
                    break
            if found_match:
                break

        if not found_match:
            # Initialize a new unique fundamental layout group
            identity_transform = ((0, 1, 2), (1, 1, 1))
            rep_set = apply_transform(pieces, identity_transform)
            unique_groups.append({
                'representative': rep_set,
                'raw_ids': [raw_id],
                'first_raw_solution': pieces
            })

    print(f"Found {len(unique_groups)} fundamental unique solutions!\n")

    for idx, group in enumerate(unique_groups, 1):
        print(f"=========================================")
        print(f"   UNIQUE SOLUTION {idx} SELECTION")
        print(f"=========================================")
        print(f"Matches {len(group['raw_ids'])} raw file configurations:")
        print(f"Raw IDs: {group['raw_ids']}\n")
        print(f"Representative Grid Layout:")
        print_grid(group['first_raw_solution'])
        print("\n")


if __name__ == "__main__":
    main()