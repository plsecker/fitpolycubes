#!/usr/bin/env python3
"""
Analyze the 30M parallel closure for SCC and 129-walk structure.
"""

import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.frontier.scc_aware_analysis import (
    tarjan_scc,
    compute_scc_internal_distances,
)

def load_closure_data(checkpoint_dir):
    """Load closure data from checkpoint."""
    import numpy as np
    
    macro_seen_arr = np.load(Path(checkpoint_dir) / "macro_seen.npy", allow_pickle=False)
    macro_seen = set(macro_seen_arr.tolist())
    
    succ_arr = np.load(Path(checkpoint_dir) / "succ.npy", allow_pickle=False)
    succ = {}
    i = 0
    while i < len(succ_arr):
        src = int(succ_arr[i])
        num_succ = int(succ_arr[i + 1])
        succs = set(int(x) for x in succ_arr[i + 2:i + 2 + num_succ])
        succ[src] = succs
        i += 2 + num_succ
    
    return macro_seen, succ

def find_129_walks(scc, succ, target_state=0, target_distance=129):
    """Find all walks of exactly 129 edges from target_state back to target_state within the SCC."""
    # Use BFS to find all walks of length 129
    # State: (current_state, distance)
    # We want to find all paths of length 129 that start and end at target_state
    
    walks = []
    
    # DFS with memoization
    def dfs(current, distance, path):
        if distance == target_distance:
            if current == target_state:
                walks.append(list(path))
            return
        
        if distance > target_distance:
            return
        
        for next_state in succ.get(current, set()):
            if next_state in scc:
                path.append(next_state)
                dfs(next_state, distance + 1, path)
                path.pop()
    
    dfs(target_state, 0, [target_state])
    return walks

def main():
    checkpoint_dir = "/tmp/parallel_30m_checkpoint"
    
    print("Loading closure data...")
    macro_seen, succ = load_closure_data(checkpoint_dir)
    
    print(f"Loaded {len(macro_seen):,} states and {len(succ):,} sources with successors")
    
    print("\nComputing SCCs...")
    sccs = tarjan_scc(macro_seen, succ)
    
    # Find SCC containing state 0
    scc_0 = None
    for scc in sccs:
        if 0 in scc:
            scc_0 = set(scc)
            break
    
    if scc_0 is None:
        print("ERROR: State 0 not found in any SCC!")
        return 1
    
    print(f"\nSCC containing state 0:")
    print(f"  Size: {len(scc_0):,}")
    
    # Count internal edges
    internal_edges = 0
    for state in scc_0:
        for next_state in succ.get(state, set()):
            if next_state in scc_0:
                internal_edges += 1
    
    print(f"  Internal edges: {internal_edges:,}")
    
    print("\nFinding 129-edge walks...")
    walks = find_129_walks(scc_0, succ, target_state=0, target_distance=129)
    
    print(f"\n129-edge walks:")
    print(f"  Total walks: {len(walks):,}")
    
    if len(walks) > 0:
        # Analyze walk structure
        walk_states = set()
        walk_edges = set()
        
        for walk in walks:
            for i in range(len(walk) - 1):
                walk_states.add(walk[i])
                walk_edges.add((walk[i], walk[i+1]))
        
        print(f"  Distinct states used: {len(walk_states):,}")
        print(f"  Distinct edges used: {len(walk_edges):,}")
    
    # Save results
    results = {
        'scc_size': len(scc_0),
        'scc_internal_edges': internal_edges,
        'num_walks': len(walks),
        'walk_states': len(walk_states) if len(walks) > 0 else 0,
        'walk_edges': len(walk_edges) if len(walks) > 0 else 0,
        'walks': walks,
    }
    
    with open('/tmp/parallel_30m_analysis.pkl', 'wb') as f:
        pickle.dump(results, f)
    
    print(f"\nResults saved to /tmp/parallel_30m_analysis.pkl")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
