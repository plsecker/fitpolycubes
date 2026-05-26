import ast
import sys
import argparse
import os

def parse_solution_file(filepath, expected_cells=125):
    solutions = []
    if not os.path.exists(filepath):
        return solutions
        
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#') or not line:
            i += 1
            continue
        
        # Next line is the solution index
        try:
            int(line)
            i += 1
            if i >= len(lines): break
            
            # This line contains the solution string
            sol_str = lines[i].strip()
            # Handle both list format [...][...] and tuple format (...)(...)
            sol_str = sol_str.replace('][', ']||[').replace(')(', ')||(')
            pieces_raw = sol_str.split('||')
            
            sol_normalized = []
            all_cells = []
            for p_raw in pieces_raw:
                # Parse piece as a list/tuple of tuples
                piece = ast.literal_eval(p_raw)
                all_cells.extend(piece)
                # Normalize piece: sort coordinates within the piece
                piece = tuple(sorted(piece))
                sol_normalized.append(piece)
            
            # Check validity: unique cells covering the entire box
            is_valid = len(all_cells) == expected_cells and len(set(all_cells)) == expected_cells
            
            # Normalize solution: sort pieces within the solution
            sol_normalized = tuple(sorted(sol_normalized))
            solutions.append({'sol': sol_normalized, 'valid': is_valid})
            i += 1
        except Exception:
            i += 1
            
    return solutions

def analyze_solver(name, data):
    unique_sols = {s['sol'] for s in data}
    print(f"{name} solutions found: {len(unique_sols)} (Raw entries: {len(data)})")
    if data:
        valid_count = sum(1 for s in data if s['valid'])
        print(f"  Valid: {valid_count}/{len(data)}")
    return unique_sols

def main():
    parser = argparse.ArgumentParser(description="Verify and Compare Polycube Solver Outputs")
    parser.add_argument("files", nargs="+", help="Solution files to compare")
    parser.add_argument("--box", nargs="+", type=int, default=[5, 5, 5], help="Box dimensions (default 5 5 5)")
    
    args = parser.parse_args()
    
    box_size = tuple(args.box) if len(args.box) == 3 else (args.box[0], args.box[0], args.box[0])
    expected_cells = box_size[0] * box_size[1] * box_size[2]
    
    print(f"Verifying solutions for {box_size} box (expected cells: {expected_cells})")
    
    solver_data = []
    for fpath in args.files:
        name = os.path.basename(fpath)
        data = parse_solution_file(fpath, expected_cells)
        unique_sols = analyze_solver(name, data)
        solver_data.append((name, unique_sols))
        
    if len(solver_data) < 2:
        return
        
    print("\n--- Cross-Validation ---")
    ref_name, ref_set = solver_data[0]
    print(f"Using {ref_name} as reference")
    
    for name, s_set in solver_data[1:]:
        common = ref_set.intersection(s_set)
        print(f"Common solutions ({ref_name} & {name}): {len(common)}")
        if len(s_set) > 0 and len(s_set) == len(common):
            print(f"SUCCESS: All {name} solutions are in {ref_name}.")
        elif len(s_set) > 0:
            print(f"INFO: {name} and {ref_name} have different solution sets.")

if __name__ == "__main__":
    main()

