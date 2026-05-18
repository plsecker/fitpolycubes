import ast

def parse_solution_file(filepath):
    solutions = []
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return solutions
        
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
            
            # Check validity: 125 unique cells for a 5x5x5 box
            is_valid = len(all_cells) == 125 and len(set(all_cells)) == 125
            
            # Normalize solution: sort pieces within the solution
            sol_normalized = tuple(sorted(sol_normalized))
            solutions.append({'sol': sol_normalized, 'valid': is_valid})
            i += 1
        except Exception as e:
            i += 1
            
    return solutions

sol_std_data = parse_solution_file('data/solutions_n.dat')
sol_fast_data = parse_solution_file('data/solutions_fast.dat')
sol_numba_data = parse_solution_file('data/solutions_numba.dat')
sol_mp_data = parse_solution_file('data/solutions_mp.dat')
sol_hybrid_data = parse_solution_file('data/solutions_hybrid.dat')

def analyze_solver(name, data):
    unique_sols = {s['sol'] for s in data}
    print(f"{name} solutions found: {len(unique_sols)} (Raw output lines: {len(data)})")
    if data:
        print(f"  All valid: {all(s['valid'] for s in data)}")
    return unique_sols

sol_std = analyze_solver("Standard", sol_std_data)
sol_fast = analyze_solver("Fast", sol_fast_data)
sol_numba = analyze_solver("Numba", sol_numba_data)
sol_mp = analyze_solver("Multiprocess", sol_mp_data)
sol_hybrid = analyze_solver("Hybrid", sol_hybrid_data)

all_sets = [("Standard", sol_std), ("Fast", sol_fast), ("Numba", sol_numba), 
            ("Multiprocess", sol_mp), ("Hybrid", sol_hybrid)]

print("\n--- Cross-Validation ---")
# Pick a reference set (the largest one, assuming it explored the most)
non_empty_sets = [s for s in all_sets if len(s[1]) > 0]
if non_empty_sets:
    ref_name, ref_set = max(non_empty_sets, key=lambda x: len(x[1]))
    print(f"Using {ref_name} as reference ({len(ref_set)} solutions)")
    
    for name, s_set in non_empty_sets:
        if name == ref_name: continue
        common = ref_set.intersection(s_set)
        print(f"Common solutions ({ref_name} & {name}): {len(common)}")
        if len(s_set) == len(common):
            print(f"SUCCESS: All {name} solutions are in the {ref_name} output.")
        else:
            print(f"INFO: {name} solver is exploring different parts of the search space.")
else:
    print("No solutions found by any solver.")


