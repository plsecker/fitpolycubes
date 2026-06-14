import argparse
import ast
from collections import defaultdict
import glob
import io
import os
import re
import sys

# Set up path for common imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.polycube_utils import PENTACUBES


def find_all_files(piece_name=None, box_size=None):
    """Find all valid solution files for the given piece and box."""
    suffixes = ["hybrid", "numba", "fast", "mp"]
    found_files = []

    def is_valid_file(p):
        if not os.path.exists(p):
            return False
        if os.path.getsize(p) < 50:
            return False
        return True

    box_str = ""
    if box_size:
        if isinstance(box_size, int):
            box_size = (box_size, box_size, box_size)
        box_str = f"_{box_size[0]}x{box_size[1]}x{box_size[2]}"

    # Base directories to search
    base_dirs = [
        "data",
        ".",
        os.path.join(os.path.dirname(__file__), "../data"),
    ]

    # Priority 1: Specific piece requested
    if piece_name:
        for s in suffixes:
            pattern = f"solutions_{s}_{piece_name.lower()}"

            # 1. Try with specific box_str if provided
            if box_str:
                for d in base_dirs:
                    p = os.path.join(d, f"{pattern}{box_str}.dat")
                    if is_valid_file(p) and p not in found_files:
                        found_files.append(p)

            # 2. Try with glob for any box size or just the piece name
            for d in base_dirs:
                matches = glob.glob(os.path.join(d, f"{pattern}_*.dat"))
                matches += glob.glob(os.path.join(d, f"{pattern}.dat"))
                for m in matches:
                    if is_valid_file(m) and m not in found_files:
                        found_files.append(m)

    # Priority 2: Generic files (only if no specific piece files found)
    if not found_files:
        for s in suffixes:
            for d in base_dirs:
                p = os.path.join(d, f"solutions_{s}.dat")
                if is_valid_file(p) and p not in found_files:
                    found_files.append(p)

    return found_files


def parse_solutions_gen(filepath):
    """Generator that parses solutions from the .dat file format."""
    current_id = None
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.isdigit():
                current_id = int(line)
                continue
            if current_id is not None:
                # Handle both list format [...][...] and tuple format (...)(...)
                formatted = line.replace("][", "], [").replace(")(", "), (")
                try:
                    pieces = ast.literal_eval(f"[{formatted}]")
                    yield pieces
                except Exception as e:
                    print(
                        f"Failed to parse line for ID {current_id} in {filepath}: {e}"
                    )


def get_24_rotations():
    """Generates all 24 rotational symmetries of a cube."""
    transforms = []
    # All 6 permutations of (x,y,z)
    for p in [
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    ]:
        # Parity of permutation
        if p in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
            parity = 1
        else:
            parity = -1
        for sx in [1, -1]:
            for sy in [1, -1]:
                for sz in [1, -1]:
                    # Determinant must be 1 for rotation (no reflection)
                    if sx * sy * sz * parity == 1:
                        transforms.append((p, (sx, sy, sz)))
    return transforms


def get_48_transformations():
    """Generates all 48 combined 3D rotations and reflections."""
    transforms = []
    for p in [
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    ]:
        for sx in [1, -1]:
            for sy in [1, -1]:
                for sz in [1, -1]:
                    transforms.append((p, (sx, sy, sz)))
    return transforms


def apply_transform_and_normalize(solution, transform):
    """Applies transformation and normalizes to a stable tuple-based format."""
    p, s = transform
    new_solution = []
    for piece in solution:
        transformed_piece = []
        for coord in piece:
            # Apply permutation and scale
            tx = coord[p[0]] * s[0]
            ty = coord[p[1]] * s[1]
            tz = coord[p[2]] * s[2]
            transformed_piece.append((tx, ty, tz))
        new_solution.append(transformed_piece)

    # Global normalization: shift the entire assembly to start at (0,0,0)
    all_coords = [c for piece in new_solution for c in piece]
    min_x = min(c[0] for c in all_coords)
    min_y = min(c[1] for c in all_coords)
    min_z = min(c[2] for c in all_coords)

    normalized_solution = []
    for piece in new_solution:
        # Each piece is a sorted tuple of coordinates
        normalized_piece = tuple(
            sorted(
                (x - min_x, y - min_y, z - min_z) for x, y, z in piece
            )
        )
        normalized_solution.append(normalized_piece)

    # The solution is a sorted tuple of normalized pieces
    return tuple(sorted(normalized_solution))


def get_canonical(solution, transforms):
    """Returns the lexicographically smallest representation of a solution across given symmetries."""
    return min(
        apply_transform_and_normalize(solution, t) for t in transforms
    )


def run_sanity_check(solution, transforms):
    """Verifies that all transforms of a solution collapse to the same canonical key."""
    keys = set()
    for t in transforms:
        p, s = t
        transformed = []
        for piece in solution:
            transformed_piece = tuple(
                (c[p[0]] * s[0], c[p[1]] * s[1], c[p[2]] * s[2])
                for c in piece
            )
            transformed.append(transformed_piece)
        keys.add(get_canonical(transformed, transforms))
    return len(keys) == 1


def find_valid_cuts(grid, box_size):
    """
    Tests every possible axis-aligned plane cut.
    Returns a list of tuples: (axis, position, box1_dims, box2_dims)
    """
    X, Y, Z = box_size
    valid_cuts = []
    
    for axis, limit, idx in [('x', X, 0), ('y', Y, 1), ('z', Z, 2)]:
        for pos in range(1, limit):
            pieces_on_left = set()
            pieces_on_right = set()
            for (x, y, z), p in grid.items():
                val = x if axis == 'x' else (y if axis == 'y' else z)
                if val < pos:
                    pieces_on_left.add(p)
                else:
                    pieces_on_right.add(p)
            
            if pieces_on_left.isdisjoint(pieces_on_right):
                d1, d2 = list(box_size), list(box_size)
                d1[idx], d2[idx] = pos, box_size[idx] - pos
                valid_cuts.append((axis, pos, tuple(d1), tuple(d2)))
    return valid_cuts


def print_grid(pieces_list, box_size, file=sys.stdout):
    """Visualizes the 3D polycube grid layer by layer to a specified output stream."""
    if isinstance(box_size, int):
        box_size = (box_size, box_size, box_size)

    grid = {}
    for piece_idx, piece in enumerate(pieces_list):
        for x, y, z in piece:
            grid[(x, y, z)] = piece_idx

    label_map = {}
    next_letter_idx = 0
    letters = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    )

    # Order scanning: Z -> Y -> X
    for z in range(box_size[2]):
        for y in range(box_size[1]):
            for x in range(box_size[0]):
                p_idx = grid.get((x, y, z))
                if p_idx is not None and p_idx not in label_map:
                    if next_letter_idx < len(letters):
                        label_map[p_idx] = letters[next_letter_idx]
                        next_letter_idx += 1
                    else:
                        label_map[p_idx] = "?"

    for z in range(box_size[2]):
        print(f"Layer Z={z}:", file=file)
        for y in range(box_size[1]):
            row_chars = []
            for x in range(box_size[0]):
                p_idx = grid.get((x, y, z))
                char = (
                    label_map[p_idx] if p_idx is not None else "."
                )
                row_chars.append(char)
            print(" ".join(row_chars), file=file)
        print("", file=file)


def main():
    parser = argparse.ArgumentParser(
        description="Reduce Polycube Solutions by Symmetry (Optimized)"
    )
    parser.add_argument(
        "piece",
        nargs="?",
        help="Piece name (e.g. N, Y, L) or path to a .dat file",
    )
    parser.add_argument(
        "--box", nargs="+", type=int, help="Box dimensions (e.g. 5 5 5)"
    )
    parser.add_argument(
        "--limit", type=int, help="Limit number of solutions to process"
    )
    parser.add_argument(
        "--reflections",
        action="store_true",
        help="Include reflections (48 symmetries) instead of just rotations (24 symmetries)",
    )
    parser.add_argument(
        "--output",
        help="Path to save the results report (auto-generated if omitted)",
    )

    args = parser.parse_args()

    filepaths = []
    piece_name = None

    if args.piece:
        if os.path.exists(args.piece):
            filepaths = [args.piece]
            piece_name = os.path.splitext(
                os.path.basename(args.piece)
            )[0]
        elif args.piece.upper() in PENTACUBES:
            piece_name = args.piece.upper()
        else:
            print(
                f"Error: '{args.piece}' is not a valid file path or piece name."
            )
            sys.exit(1)

    box_size = None
    if args.box:
        box_size = (
            tuple(args.box)
            if len(args.box) == 3
            else (args.box[0], args.box[0], args.box[0])
        )

    if not filepaths:
        filepaths = find_all_files(piece_name, box_size)

    if not filepaths:
        print("Error: Could not locate solution files.")
        return

    # Infer box size if not provided
    if box_size is None:
        for fp in filepaths:
            match = re.search(
                r"(\d+)x(\d+)x(\d+)", os.path.basename(fp)
            )
            if match:
                box_size = (
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )
                print(
                    f"Inferred box size {box_size} from {os.path.basename(fp)}"
                )
                break
        if box_size is None:
            box_size = (5, 5, 5)
            print(f"Using default box size {box_size}")

    # --- AUTOMATIC NAMING LOGIC ---
        # --- AUTOMATIC NAMING LOGIC ---
    if not args.output:
        p_label = piece_name if piece_name else "all"
        b_label = f"{box_size[0]}x{box_size[1]}x{box_size[2]}" if box_size else "default"
        filename = f"reduce_{p_label.lower()}_{b_label}.txt"

        # If a valid source filepath exists, extract its directory path
        if filepaths:
            target_dir = os.path.dirname(filepaths[0])
            # Handle edge case where file is in the current working directory
            args.output = os.path.join(target_dir, filename) if target_dir else filename
        else:
            args.output = filename
    if args.reflections:
        print("Using 48 symmetries (rotations + reflections)")
        transforms = get_48_transformations()
    else:
        print("Using 24 rotational symmetries")
        transforms = get_24_rotations()

    unique_groups = {}

    print(f"Processing files: {', '.join(filepaths)}")

    total_processed = 0
    sanity_checked = False

    for fp in filepaths:
        print(f"Loading data from: {fp}")
        for pieces in parse_solutions_gen(fp):
            total_processed += 1
            if args.limit and total_processed > args.limit:
                break

            if not sanity_checked:
                if run_sanity_check(pieces, transforms):
                    print(
                        "  [Sanity Check] Passed: All symmetries collapse to a single key."
                    )
                else:
                    print(
                        "  [Sanity Check] FAILED: Symmetries do not collapse to a single key."
                    )
                sanity_checked = True

            canonical_key = get_canonical(pieces, transforms)

            if canonical_key not in unique_groups:
                unique_groups[canonical_key] = {
                    'match_count': 1,
                    'first_raw_solution': pieces,
                }
            else:
                unique_groups[canonical_key]['match_count'] += 1

            if total_processed % 100 == 0:
                sys.stdout.write(
                    f"\rProcessed {total_processed} solutions... Found {len(unique_groups)} unique."
                )
                sys.stdout.flush()

    print(f"\n\nTotal solutions processed: {total_processed}")
    print(
        f"Found {len(unique_groups)} fundamental unique solutions!\n"
    )

    sorted_groups = sorted(
        unique_groups.values(),
        key=lambda x: x['match_count'],
        reverse=True,
    )

    # Unified printing function to output cleanly to both streams
    def out_print(*print_args, **print_kwargs):
        print(*print_args, **print_kwargs)
        if f_out:
            print(*print_args, **print_kwargs, file=f_out)

    # Initialize counters for subbox summary
    total_analyzed = 0
    with_cut = 0
    no_cut = 0

    print(f"Saving results report to: {args.output} ...")
    with open(args.output, "w") as f_out:
        f_out.write(
            f"# Reduction Results\n# Source: {', '.join(filepaths)}\n"
        )
        f_out.write(
            f"# Mode: {'48 symmetries' if args.reflections else '24 rotations'}\n"
        )
        f_out.write(f"# Total Unique: {len(unique_groups)}\n\n")

        for idx, group in enumerate(sorted_groups, 1):
            out_print("=========================================")
            out_print(  f"   UNIQUE SOLUTION {idx}")
            out_print("=========================================")
            out_print(
                f"Matches {group['match_count']} instances (including symmetries/duplicates)"
            )
            
            # Add Subbox analysis
            # Reconstruct grid for analysis
            grid = {}
            for p_idx, coords in enumerate(group['first_raw_solution']):
                for coord in coords:
                    grid[coord] = p_idx
            cuts = find_valid_cuts(grid, box_size)
            out_print("Subbox analysis:")
            total_analyzed += 1
            if cuts:
                with_cut += 1
                for axis, pos, d1, d2 in cuts:
                    out_print(f"  Valid cut: {axis}={pos} -> {d1[0]}x{d1[1]}x{d1[2]} + {d2[0]}x{d2[1]}x{d2[2]}")
            else:
                no_cut += 1
                out_print("  No valid rectangular decomposition")
            
            out_print("\nRepresentative Grid Layout:")

            # Cleaned up: Pass target streams directly into print_grid
            print_grid(group['first_raw_solution'], box_size, file=sys.stdout)
            if f_out:
                print_grid(group['first_raw_solution'], box_size, file=f_out)

            out_print("\n")

            if idx % 10 == 0:
                sys.stdout.write(
                    f"\rOutputting results: {idx}/{len(sorted_groups)}"
                )
                sys.stdout.flush()

    print("\nSubbox summary:")
    print(f"  Fundamental solutions analysed: {total_analyzed}")
    print(f"  Solutions with a valid cut: {with_cut}")
    print(f"  Solutions with no valid cut: {no_cut}")

    print(f"\nAll tasks complete! Results written to {args.output}")


if __name__ == "__main__":
    main()
