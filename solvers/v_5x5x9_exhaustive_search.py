#!/usr/bin/env python3
"""
Exhaustive, resumable, parallel search for V pentacube tilings in 5×5×9.

Uses the Macro state representation with memoized explore_source to avoid
revisiting the same macro state.  Splits at depth 1 (9,000 frontier states)
for parallel independent tasks.

Key optimizations:
- Memoized explore_source: each macro state explored once, cached forever.
- Memoized transition sequences: each macro transition reconstructed once.
- Lazy DFS: never builds the full state graph.
- Checkpointing: each task writes solutions and status to disk.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import re
import multiprocessing as mp
from collections import deque
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

# ---------------------------------------------------------------------------
# Macro state constants
# ---------------------------------------------------------------------------
X_SIZE = 5
Y_SIZE = 5
NCELLS = X_SIZE * Y_SIZE  # 25
LAYERS = 3
WORD_MASK = (1 << NCELLS) - 1
TARGET_DEPTH = 9

# ---------------------------------------------------------------------------
# Working directories
# ---------------------------------------------------------------------------
SOLVER_DIR = Path(__file__).resolve().parent
WORK_DIR = REPO_ROOT / "data" / "v_5x5x9_search"
FRONTIER_FILE = WORK_DIR / "frontier_depth1.json"
TASKS_DIR = WORK_DIR / "tasks"
SOLUTIONS_DIR = WORK_DIR / "solutions"
MERGED_FILE = WORK_DIR / "all_solutions_merged.dat"
SUMMARY_FILE = WORK_DIR / "search_summary.json"

# ---------------------------------------------------------------------------
# Macro state helpers
# ---------------------------------------------------------------------------

def cell_id(x: int, y: int) -> int:
    return x + X_SIZE * y


def layer_mask(state: int, layer: int) -> int:
    return (state >> (layer * NCELLS)) & WORD_MASK


def first_empty(mask: int) -> int:
    missing = WORD_MASK & ~mask
    if not missing:
        return -1
    low = missing & -missing
    return low.bit_length() - 1


def pack_layers(layers: List[int]) -> int:
    state = 0
    for i, mask in enumerate(layers):
        state |= (mask << (i * NCELLS))
    return state


def shift_state(state: int) -> int:
    return state >> NCELLS


def make_shifted_template(
    placement_cells: List[Tuple[int, int, int]],
    target_z: int,
) -> Optional[int]:
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        if rel < 0 or rel >= LAYERS:
            return None
        shifted_masks[rel] |= (1 << cell_id(x, y))
    return pack_layers(shifted_masks)


def build_templates() -> Dict[int, List[int]]:
    raw, _ = generate_placements(
        PENTACUBES["V"],
        (X_SIZE, Y_SIZE, 20),
        break_symmetry=False,
    )
    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    for placement in raw.values():
        cells = tuple(placement)
        for x, y, z in cells:
            target = cell_id(x, y)
            packed = make_shifted_template(cells, z)
            if packed is None:
                continue
            if packed in seen[target]:
                continue
            seen[target].add(packed)
            result[target].append(packed)
    return result


def apply_template(state: int, template: int) -> Optional[int]:
    if state & template:
        return None
    return state | template


# ---------------------------------------------------------------------------
# Memoized macro operations
# ---------------------------------------------------------------------------

class MacroCache:
    """
    Thread-local cache for macro operations.
    Each worker process gets its own instance.
    """
    
    def __init__(self, templates: Dict[int, List[int]]):
        self.templates = templates
        # Cache: macro_state -> (successors_set, intermediate_count)
        self._succ_cache: Dict[int, Tuple[frozenset, int]] = {}
        # Cache: (start_state, end_state) -> list of templates
        self._trans_cache: Dict[Tuple[int, int], Optional[List[int]]] = {}
        # Stats
        self.succ_hits = 0
        self.succ_misses = 0
        self.trans_hits = 0
        self.trans_misses = 0
    
    def get_successors(self, source: int) -> Tuple[Set[int], int]:
        """Get successors of a macro state (memoized)."""
        if source in self._succ_cache:
            self.succ_hits += 1
            cached_succ, cached_interm = self._succ_cache[source]
            return set(cached_succ), cached_interm
        
        self.succ_misses += 1
        successors: Set[int] = set()
        seen: Set[int] = {source}
        queue: deque = deque([source])
        
        while queue:
            state = queue.popleft()
            if layer_mask(state, 0) == WORD_MASK:
                successors.add(shift_state(state))
                continue
            target = first_empty(layer_mask(state, 0))
            for template in self.templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in seen:
                    continue
                seen.add(nxt)
                queue.append(nxt)
        
        interm = len(seen) - 1
        self._succ_cache[source] = (frozenset(successors), interm)
        return successors, interm
    
    def get_transition(
        self,
        start_state: int,
        end_state: int,
        max_steps: int = 5000,
    ) -> Optional[List[int]]:
        """Find template sequence between macro states (memoized)."""
        key = (start_state, end_state)
        if key in self._trans_cache:
            self.trans_hits += 1
            result = self._trans_cache[key]
            return list(result) if result is not None else None
        
        self.trans_misses += 1
        queue: deque = deque([(start_state, [])])
        seen: Set[int] = {start_state}
        result = None
        
        while queue:
            state, tmpls = queue.popleft()
            if layer_mask(state, 0) == WORD_MASK:
                shifted = shift_state(state)
                if shifted == end_state:
                    result = tmpls
                    break
                continue
            target = first_empty(layer_mask(state, 0))
            for template in self.templates[target]:
                nxt = apply_template(state, template)
                if nxt is None or nxt in seen:
                    continue
                if len(tmpls) >= max_steps:
                    continue
                seen.add(nxt)
                queue.append((nxt, tmpls + [template]))
        
        self._trans_cache[key] = result
        return list(result) if result is not None else None
    
    def cache_stats(self) -> Dict:
        return {
            "succ_cache_size": len(self._succ_cache),
            "succ_hits": self.succ_hits,
            "succ_misses": self.succ_misses,
            "trans_cache_size": len(self._trans_cache),
            "trans_hits": self.trans_hits,
            "trans_misses": self.trans_misses,
        }


# ---------------------------------------------------------------------------
# Tiling reconstruction
# ---------------------------------------------------------------------------

def extract_placement_from_template(template: int, z_offset: int) -> Optional[List[Tuple[int, int, int]]]:
    cells = []
    for layer in range(LAYERS):
        lm = (template >> (layer * NCELLS)) & WORD_MASK
        for cid in range(NCELLS):
            if lm & (1 << cid):
                x = cid % X_SIZE
                y = cid // X_SIZE
                z = z_offset + layer
                cells.append((x, y, z))
    if len(cells) != 5:
        return None
    return cells


def reconstruct_tiling_from_macro_path(
    path: List[int],
    cache: MacroCache,
) -> Optional[List[Tuple[int, int, int]]]:
    """Reconstruct actual V piece placements from a macro path."""
    placements = []
    for depth in range(len(path) - 1):
        start_state = path[depth]
        end_state = path[depth + 1]
        tmpls = cache.get_transition(start_state, end_state)
        if tmpls is None:
            return None
        for tmpl in tmpls:
            placement = extract_placement_from_template(tmpl, depth)
            if placement is None:
                return None
            placements.append(tuple(sorted(placement)))
    if len(placements) != 45:
        return None
    return placements


# ---------------------------------------------------------------------------
# Canonical tiling representation
# ---------------------------------------------------------------------------

def canonicalize_tiling(placements: List[Tuple]) -> Tuple:
    sorted_pieces = [tuple(sorted(p)) for p in placements]
    sorted_pieces.sort()
    return tuple(sorted_pieces)


def tiling_to_string(placements: List[Tuple]) -> str:
    parts = []
    for piece in placements:
        piece_str = "(" + ", ".join(f"({x},{y},{z})" for x, y, z in piece) + ")"
        parts.append(piece_str)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def verify_tiling(placements: List[Tuple], box_dims=(5, 5, 9)) -> Tuple[bool, str]:
    bx, by, bz = box_dims
    if len(placements) != 45:
        return False, f"Expected 45 pieces, got {len(placements)}"
    for i, p in enumerate(placements):
        if len(p) != 5:
            return False, f"Piece {i} has {len(p)} cells"
    cells = set()
    for pi, p in enumerate(placements):
        for x, y, z in p:
            if not (0 <= x < bx and 0 <= y < by and 0 <= z < bz):
                return False, f"Cell ({x},{y},{z}) out of bounds in piece {pi}"
            if (x, y, z) in cells:
                return False, f"Overlap at ({x},{y},{z})"
            cells.add((x, y, z))
    if len(cells) != bx * by * bz:
        return False, f"Expected {bx*by*bz} cells, got {len(cells)}"
    return True, "Valid"


# ---------------------------------------------------------------------------
# Frontier generation
# ---------------------------------------------------------------------------

def generate_frontier(templates: Dict[int, List[int]]) -> List[int]:
    sources: Set[int] = set()
    seen: Set[int] = {0}
    queue: deque = deque([0])
    while queue:
        state = queue.popleft()
        if layer_mask(state, 0) == WORD_MASK:
            sources.add(shift_state(state))
            continue
        target = first_empty(layer_mask(state, 0))
        for template in templates[target]:
            nxt = apply_template(state, template)
            if nxt is None or nxt in seen:
                continue
            seen.add(nxt)
            queue.append(nxt)
    return sorted(sources)


# ---------------------------------------------------------------------------
# Lazy DFS with memoization (single task)
# ---------------------------------------------------------------------------

def dfs_task(
    task_id: int,
    frontier_state: int,
    cache: MacroCache,
    task_dir: Path,
    solutions_dir: Path,
) -> Dict:
    """
    Perform lazy DFS from a depth-1 frontier state to depth 9.
    Uses memoized MacroCache to avoid recomputing explore_source.
    """
    start_time = time.time()
    solutions: List[Tuple] = []
    dfs_calls = 0
    last_checkpoint = time.time()
    
    def dfs(state: int, depth: int, path: List[int]):
        nonlocal dfs_calls, last_checkpoint
        dfs_calls += 1
        
        if depth == TARGET_DEPTH:
            if state == 0:
                full_path = [0] + path
                placements = reconstruct_tiling_from_macro_path(full_path, cache)
                if placements is not None:
                    solutions.append(canonicalize_tiling(placements))
            return
        
        successors, _ = cache.get_successors(state)
        
        for s in successors:
            path.append(s)
            dfs(s, depth + 1, path)
            path.pop()
        
        # Periodic checkpoint
        now = time.time()
        if now - last_checkpoint > 60:
            _write_checkpoint(task_id, task_dir, solutions_dir, solutions,
                              dfs_calls, start_time, "running")
            last_checkpoint = now
    
    dfs(frontier_state, 1, [frontier_state])
    
    elapsed = time.time() - start_time
    
    _write_solutions(task_id, solutions_dir, solutions)
    _write_checkpoint(task_id, task_dir, solutions_dir, solutions,
                      dfs_calls, start_time, "completed")
    
    return {
        "task_id": task_id,
        "frontier_state": frontier_state,
        "solutions_found": len(solutions),
        "dfs_calls": dfs_calls,
        "elapsed": elapsed,
        "cache_stats": cache.cache_stats(),
    }


def _write_solutions(task_id: int, solutions_dir: Path, solutions: List[Tuple]):
    sol_file = solutions_dir / f"task_{task_id:06d}.dat"
    with open(sol_file, "w") as f:
        f.write(f"# Task {task_id} solutions\n")
        for i, sol in enumerate(solutions):
            pieces = [list(p) for p in sol]
            f.write(f"{i+1}\n")
            f.write(tiling_to_string(pieces) + "\n")


def _write_checkpoint(
    task_id: int,
    task_dir: Path,
    solutions_dir: Path,
    solutions: List[Tuple],
    dfs_calls: int,
    start_time: float,
    status: str,
):
    ckpt = {
        "task_id": task_id,
        "status": status,
        "solutions_found": len(solutions),
        "dfs_calls": dfs_calls,
        "elapsed": time.time() - start_time,
        "solutions_file": str(solutions_dir / f"task_{task_id:06d}.dat"),
    }
    ckpt_file = task_dir / f"task_{task_id:06d}.json"
    with open(ckpt_file, "w") as f:
        json.dump(ckpt, f, indent=2)


# ---------------------------------------------------------------------------
# Worker wrapper for multiprocessing
# ---------------------------------------------------------------------------

def _worker_init(templates_dict):
    """Initialize worker with templates and its own MacroCache."""
    global _worker_cache
    _worker_cache = MacroCache(templates_dict)


def _worker_run(task_spec):
    """Run a single task (wrapped for multiprocessing)."""
    task_id, frontier_state = task_spec
    global _worker_cache
    result = dfs_task(
        task_id, frontier_state,
        _worker_cache,
        TASKS_DIR, SOLUTIONS_DIR,
    )
    return result


# ---------------------------------------------------------------------------
# Merge and deduplicate
# ---------------------------------------------------------------------------

def merge_solutions(output_file: Path) -> Tuple[int, int]:
    """Merge all task solution files, deduplicate."""
    all_solutions: Set[Tuple] = set()
    total_raw = 0
    
    sol_files = sorted(SOLUTIONS_DIR.glob("task_*.dat"))
    print(f"Merging {len(sol_files)} task solution files...")
    
    for sf in sol_files:
        with open(sf) as f:
            content = f.read()
        lines = content.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                i += 1
                continue
            if line.isdigit():
                if i + 1 < len(lines):
                    placements_line = lines[i + 1].strip()
                    placements = []
                    pat = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
                    matches = re.findall(pat, placements_line)
                    for j in range(0, len(matches), 5):
                        if j + 5 <= len(matches):
                            piece = tuple(
                                (int(matches[j + k][0]), int(matches[j + k][1]), int(matches[j + k][2]))
                                for k in range(5)
                            )
                            placements.append(piece)
                    if len(placements) == 45:
                        total_raw += 1
                        canonical = canonicalize_tiling(placements)
                        all_solutions.add(canonical)
                    i += 2
                else:
                    i += 1
            else:
                i += 1
    
    with open(output_file, "w") as f:
        f.write(f"# V 5x5x9 merged solutions (raw={total_raw}, unique={len(all_solutions)})\n")
        for idx, sol in enumerate(sorted(all_solutions)):
            pieces = [list(p) for p in sol]
            f.write(f"{idx + 1}\n")
            f.write(tiling_to_string(pieces) + "\n")
    
    return total_raw, len(all_solutions)


# ---------------------------------------------------------------------------
# Validate merged solutions
# ---------------------------------------------------------------------------

def validate_merged(output_file: Path) -> Dict:
    with open(output_file) as f:
        content = f.read()
    
    lines = content.strip().split("\n")
    solutions = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        if line.isdigit():
            if i + 1 < len(lines):
                pl = lines[i + 1].strip()
                placements = []
                pat = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"
                matches = re.findall(pat, pl)
                for j in range(0, len(matches), 5):
                    if j + 5 <= len(matches):
                        piece = [
                            (int(matches[j + k][0]), int(matches[j + k][1]), int(matches[j + k][2]))
                            for k in range(5)
                        ]
                        placements.append(piece)
                if len(placements) == 45:
                    solutions.append(placements)
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    print(f"Validating {len(solutions)} solutions...")
    valid = 0
    invalid = []
    for idx, sol in enumerate(solutions):
        ok, msg = verify_tiling(sol)
        if ok:
            valid += 1
        else:
            invalid.append((idx, msg))
    
    return {
        "total": len(solutions),
        "valid": valid,
        "invalid": len(invalid),
        "invalid_details": invalid,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Exhaustive resumable search for V 5×5×9 tilings"
    )
    parser.add_argument("--generate-frontier", action="store_true",
                        help="Generate depth-1 frontier")
    parser.add_argument("--search", action="store_true",
                        help="Run search (process frontier tasks)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of parallel workers")
    parser.add_argument("--merge", action="store_true",
                        help="Merge and deduplicate all task solutions")
    parser.add_argument("--validate", action="store_true",
                        help="Validate merged solutions")
    parser.add_argument("--all", action="store_true",
                        help="Run full pipeline")
    parser.add_argument("--no-resume", action="store_false", dest="resume",
                        help="Re-run completed tasks")
    parser.set_defaults(resume=True)
    
    args = parser.parse_args()
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Building templates...")
    t0 = time.time()
    templates = build_templates()
    print(f"  {sum(len(v) for v in templates.values())} templates, "
          f"{len(templates)} cells ({time.time() - t0:.1f}s)")
    
    # Generate frontier
    if args.generate_frontier or args.all:
        print("\n=== Generating depth-1 frontier ===")
        t0 = time.time()
        frontier = generate_frontier(templates)
        print(f"  {len(frontier)} frontier states ({time.time() - t0:.1f}s)")
        with open(FRONTIER_FILE, "w") as f:
            json.dump({"frontier": frontier, "count": len(frontier)}, f)
        print(f"  Saved to {FRONTIER_FILE}")
    
    # Search
    if args.search or args.all:
        print("\n=== Search ===")
        
        if not FRONTIER_FILE.exists():
            print("ERROR: Frontier file not found. Run --generate-frontier first.")
            return 1
        
        with open(FRONTIER_FILE) as f:
            frontier = json.load(f)["frontier"]
        print(f"  {len(frontier)} frontier states loaded")
        
        tasks_to_run = []
        for task_id, state in enumerate(frontier):
            ckpt_file = TASKS_DIR / f"task_{task_id:06d}.json"
            if ckpt_file.exists() and args.resume:
                with open(ckpt_file) as f:
                    ckpt = json.load(f)
                if ckpt.get("status") == "completed":
                    continue
            tasks_to_run.append((task_id, state))
        
        print(f"  Tasks to process: {len(tasks_to_run)}/{len(frontier)}")
        
        if tasks_to_run:
            t0 = time.time()
            
            if args.workers <= 1:
                print(f"  Single-process ({len(tasks_to_run)} tasks)...")
                cache = MacroCache(templates)
                results = []
                for idx, (task_id, state) in enumerate(tasks_to_run):
                    result = dfs_task(task_id, state, cache, TASKS_DIR, SOLUTIONS_DIR)
                    results.append(result)
                    elapsed = time.time() - t0
                    print(f"    Task {task_id}: {result['solutions_found']} sols, "
                          f"{result['elapsed']:.1f}s, "
                          f"{result['dfs_calls']:,} calls "
                          f"({(idx+1)/elapsed:.2f}/s, {elapsed:.0f}s elapsed)")
            else:
                print(f"  Parallel ({args.workers} workers, {len(tasks_to_run)} tasks)...")
                with mp.Pool(args.workers, initializer=_worker_init,
                             initargs=(templates,)) as pool:
                    results = list(pool.imap_unordered(_worker_run, tasks_to_run))
                results.sort(key=lambda r: r["task_id"])
                
                for r in results:
                    if r["solutions_found"] > 0:
                        print(f"    Task {r['task_id']}: {r['solutions_found']} sols, "
                              f"{r['elapsed']:.1f}s, {r['dfs_calls']:,} calls")
            
            total_elapsed = time.time() - t0
            total_solutions = sum(r["solutions_found"] for r in results)
            total_dfs_calls = sum(r["dfs_calls"] for r in results)
            
            print(f"\n  Search results:")
            print(f"    Tasks completed: {len(results)}")
            print(f"    Total solutions: {total_solutions}")
            print(f"    Total DFS calls: {total_dfs_calls:,}")
            print(f"    Elapsed: {total_elapsed:.1f}s")
            
            # Aggregate cache stats
            total_succ_hits = sum(r.get("cache_stats", {}).get("succ_hits", 0) for r in results)
            total_succ_misses = sum(r.get("cache_stats", {}).get("succ_misses", 0) for r in results)
            total_trans_hits = sum(r.get("cache_stats", {}).get("trans_hits", 0) for r in results)
            total_trans_misses = sum(r.get("cache_stats", {}).get("trans_misses", 0) for r in results)
            print(f"    Cache: succ {total_succ_hits}/{total_succ_misses + total_succ_hits} "
                  f"({total_succ_misses + total_succ_hits} unique), "
                  f"trans {total_trans_hits}/{total_trans_misses + total_trans_hits}")
            
            summary = {
                "tasks_completed": len(results),
                "total_solutions": total_solutions,
                "total_dfs_calls": total_dfs_calls,
                "elapsed": total_elapsed,
                "workers": args.workers,
                "frontier_size": len(frontier),
            }
            with open(SUMMARY_FILE, "w") as f:
                json.dump(summary, f, indent=2)
        else:
            print("  All tasks already completed!")
    
    # Merge
    if args.merge or args.all:
        print("\n=== Merge ===")
        t0 = time.time()
        total_raw, total_unique = merge_solutions(MERGED_FILE)
        print(f"  Raw: {total_raw}, Unique: {total_unique} ({time.time() - t0:.1f}s)")
        print(f"  Output: {MERGED_FILE}")
    
    # Validate
    if args.validate or args.all:
        print("\n=== Validate ===")
        if not MERGED_FILE.exists():
            print("ERROR: Merged file not found. Run --merge first.")
            return 1
        t0 = time.time()
        vresult = validate_merged(MERGED_FILE)
        print(f"  Total: {vresult['total']}, Valid: {vresult['valid']}, "
              f"Invalid: {vresult['invalid']} ({time.time() - t0:.1f}s)")
        if vresult["invalid"] > 0:
            for idx, msg in vresult["invalid_details"]:
                print(f"    Solution {idx}: {msg}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())