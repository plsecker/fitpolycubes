#!/usr/bin/env python3
"""
Generalized Macro explorer for S pentacube in a×b×N boxes.

This is an architectural prototype to test whether the Macro technique
generalizes beyond 4×8.

Usage:
    # Start new computation
    python3 tools/frontier/macro_generalized.py --a 5 --b 6
    
    # Start with checkpointing
    python3 tools/frontier/macro_generalized.py --a 4 --b 9 \
        --checkpoint /path/to/4x9.ckpt \
        --checkpoint-interval 500000
    
    # Resume from checkpoint
    python3 tools/frontier/macro_generalized.py --resume /path/to/4x9.ckpt
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import tempfile
import time
from collections import deque
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

# Checkpoint format version
CHECKPOINT_VERSION = 1


def make_shifted_template_general(placement_cells, target_z, a, b):
    """
    Translate a concrete S placement so that the chosen target occurrence
    lies on frontier layer 0.
    
    Return packed occupancy (3 layers of a×b bits each).
    """
    NCELLS = a * b
    LAYERS = 3
    
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * LAYERS
    target_rel = target_z - min_z
    
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        
        if rel < 0 or rel >= LAYERS:
            return None
        
        cell_id = x + a * y
        shifted_masks[rel] |= (1 << cell_id)
    
    state = 0
    for i, mask in enumerate(shifted_masks):
        state |= (mask << (i * NCELLS))
    
    return state


def build_templates_general(a: int, b: int):
    """Generate templates for a×b cross-section."""
    raw, _ = generate_placements(
        PENTACUBES["S"],
        (a, b, 20),  # 20 is arbitrary; just needs to be large enough
        break_symmetry=False,
    )
    
    NCELLS = a * b
    WORD_MASK = (1 << NCELLS) - 1
    
    result = {cell: [] for cell in range(NCELLS)}
    seen = {cell: set() for cell in range(NCELLS)}
    
    concrete_count = len(raw)
    
    for placement in raw.values():
        cells = tuple(placement)
        
        for x, y, z in cells:
            target = x + a * y
            
            packed = make_shifted_template_general(cells, z, a, b)
            
            if packed is None:
                continue
            
            if packed in seen[target]:
                continue
            
            seen[target].add(packed)
            result[target].append(packed)
    
    total_templates = sum(len(v) for v in result.values())
    
    return result, NCELLS, WORD_MASK, concrete_count, total_templates


def layer_mask_general(state: int, layer: int, NCELLS: int) -> int:
    """Extract layer mask from state."""
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)


def first_empty_general(mask: int, NCELLS: int) -> int:
    """Find first empty cell in mask."""
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    
    if not missing:
        return -1
    
    low = missing & -missing
    return low.bit_length() - 1


def apply_template_general(state: int, template: int) -> int | None:
    """Apply template to state if disjoint."""
    if state & template:
        return None
    return state | template


def shift_state_general(state: int, NCELLS: int) -> int:
    """Shift state down by one layer."""
    return state >> NCELLS


# ============================================================================
# Checkpoint/Resume Support
# ============================================================================

def save_checkpoint(
    checkpoint_path: Path,
    phase: str,
    a: int,
    b: int,
    NCELLS: int,
    WORD_MASK: int,
    max_states: int,
    seen: set[int],
    queue: deque[int],
    sources: set[int] | None = None,
    macro_seen: set[int] | None = None,
    succ: dict[int, set[int]] | None = None,
    edge_count: int = 0,
    total_intermediate: int = 0,
    concrete_placements: int = 0,
    target_templates: int = 0,
) -> None:
    """
    Save checkpoint atomically using write-to-temp + rename.
    
    Checkpoint format:
    - Header (JSON): metadata, dimensions, counters
    - State sets: stored as sorted lists of integers (JSON for portability)
    - Successor dict: stored as nested dict (JSON for portability)
    
    All data is sorted for deterministic output.
    """
    checkpoint_path = Path(checkpoint_path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create temp file in same directory for atomic rename
    temp_dir = checkpoint_path.parent / ".checkpoint_temp"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Prepare metadata
        metadata = {
            "version": CHECKPOINT_VERSION,
            "phase": phase,
            "a": a,
            "b": b,
            "NCELLS": NCELLS,
            "WORD_MASK": WORD_MASK,
            "max_states": max_states,
            "edge_count": edge_count,
            "total_intermediate": total_intermediate,
            "concrete_placements": concrete_placements,
            "target_templates": target_templates,
            "timestamp": time.time(),
        }
        
        # Save metadata as JSON
        temp_meta = temp_dir / "metadata.json"
        with open(temp_meta, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save state sets as sorted lists (JSON handles arbitrary-precision integers)
        temp_seen = temp_dir / "seen.json"
        with open(temp_seen, "w") as f:
            json.dump(sorted(seen), f)
        
        temp_queue = temp_dir / "queue.json"
        with open(temp_queue, "w") as f:
            json.dump(list(queue), f)
        
        # Save sources if in macro closure phase
        if sources is not None:
            temp_sources = temp_dir / "sources.json"
            with open(temp_sources, "w") as f:
                json.dump(sorted(sources), f)
        
        # Save macro_seen if in macro closure phase
        if macro_seen is not None:
            temp_macro_seen = temp_dir / "macro_seen.json"
            with open(temp_macro_seen, "w") as f:
                json.dump(sorted(macro_seen), f)
        
        # Save successor dict as nested structure
        if succ is not None:
            temp_succ = temp_dir / "succ.json"
            # Convert sets to sorted lists for JSON serialization
            succ_serializable = {
                str(src): sorted(succs)
                for src, succs in sorted(succ.items())
            }
            with open(temp_succ, "w") as f:
                json.dump(succ_serializable, f)
        
        # Atomic rename: move temp directory to final location
        # First, remove old checkpoint if it exists
        if checkpoint_path.exists():
            import shutil
            shutil.rmtree(checkpoint_path)
        
        # Rename temp directory to checkpoint path
        temp_dir.rename(checkpoint_path)
        
    except Exception as e:
        # Clean up temp directory on error
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to save checkpoint: {e}")


def load_checkpoint(checkpoint_path: Path) -> dict:
    """
    Load checkpoint and validate contents.
    
    Returns dict with all checkpoint data.
    Raises RuntimeError if checkpoint is invalid or incompatible.
    """
    checkpoint_path = Path(checkpoint_path)
    
    if not checkpoint_path.exists():
        raise RuntimeError(f"Checkpoint file does not exist: {checkpoint_path}")
    
    if not checkpoint_path.is_dir():
        raise RuntimeError(f"Checkpoint path is not a directory: {checkpoint_path}")
    
    # Load metadata
    meta_path = checkpoint_path / "metadata.json"
    if not meta_path.exists():
        raise RuntimeError(f"Checkpoint missing metadata.json")
    
    with open(meta_path, "r") as f:
        metadata = json.load(f)
    
    # Validate version
    version = metadata.get("version")
    if version != CHECKPOINT_VERSION:
        raise RuntimeError(
            f"Checkpoint version mismatch: expected {CHECKPOINT_VERSION}, got {version}"
        )
    
    # Validate required fields
    required_fields = ["phase", "a", "b", "NCELLS", "WORD_MASK", "max_states"]
    for field in required_fields:
        if field not in metadata:
            raise RuntimeError(f"Checkpoint missing required field: {field}")
    
    # Load state sets from JSON (handles arbitrary-precision integers)
    seen_path = checkpoint_path / "seen.json"
    if not seen_path.exists():
        raise RuntimeError(f"Checkpoint missing seen.json")
    with open(seen_path, "r") as f:
        seen = set(json.load(f))
    
    queue_path = checkpoint_path / "queue.json"
    if not queue_path.exists():
        raise RuntimeError(f"Checkpoint missing queue.json")
    with open(queue_path, "r") as f:
        queue = deque(json.load(f))
    
    # Load optional arrays based on phase
    sources = None
    macro_seen = None
    succ = None
    
    sources_path = checkpoint_path / "sources.json"
    if sources_path.exists():
        with open(sources_path, "r") as f:
            sources = set(json.load(f))
    
    macro_seen_path = checkpoint_path / "macro_seen.json"
    if macro_seen_path.exists():
        with open(macro_seen_path, "r") as f:
            macro_seen = set(json.load(f))
    
    succ_path = checkpoint_path / "succ.json"
    if succ_path.exists():
        with open(succ_path, "r") as f:
            succ_serializable = json.load(f)
        # Convert back to dict[int, set[int]]
        succ = {
            int(src): set(succs)
            for src, succs in succ_serializable.items()
        }
    
    return {
        "metadata": metadata,
        "phase": metadata["phase"],
        "a": metadata["a"],
        "b": metadata["b"],
        "NCELLS": metadata["NCELLS"],
        "WORD_MASK": metadata["WORD_MASK"],
        "max_states": metadata["max_states"],
        "seen": seen,
        "queue": queue,
        "sources": sources,
        "macro_seen": macro_seen,
        "succ": succ,
        "edge_count": metadata.get("edge_count", 0),
        "total_intermediate": metadata.get("total_intermediate", 0),
        "concrete_placements": metadata.get("concrete_placements", 0),
        "target_templates": metadata.get("target_templates", 0),
    }


# Global flag for signal handling
_interrupted = False


def signal_handler(signum, frame):
    """Handle SIGINT/SIGTERM for graceful shutdown."""
    global _interrupted
    _interrupted = True
    print(f"\nInterrupted (signal {signum}). Saving checkpoint and exiting...")


def macro_closure_general(
    a: int,
    b: int,
    max_states: int = 10_000_000,
    verbose: bool = True,
    checkpoint_path: Path | None = None,
    checkpoint_interval: int = 500_000,
    resume_checkpoint: Path | None = None,
):
    """
    Compute Macro closure for a×b cross-section.
    
    Supports checkpoint/resume for long-running computations.
    
    Args:
        a, b: Cross-section dimensions
        max_states: Maximum total states to discover (not incremental on resume)
        verbose: Print progress
        checkpoint_path: Path to save checkpoints (if None, no checkpointing)
        checkpoint_interval: Save checkpoint every N new states
        resume_checkpoint: Path to resume from (if None, start fresh)
    
    Returns (macro_states, succ, sources, stats).
    """
    global _interrupted
    
    # Set up signal handlers
    original_sigint = signal.signal(signal.SIGINT, signal_handler)
    original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        start_time = time.perf_counter()
        
        # Check if resuming from checkpoint
        if resume_checkpoint is not None:
            if verbose:
                print(f"Resuming from checkpoint: {resume_checkpoint}")
            
            ckpt = load_checkpoint(resume_checkpoint)
            
            # Validate dimensions match
            if ckpt["a"] != a or ckpt["b"] != b:
                raise RuntimeError(
                    f"Checkpoint dimensions mismatch: checkpoint is {ckpt['a']}×{ckpt['b']}, "
                    f"but requested {a}×{b}"
                )
            
            # Validate max_states is compatible
            if ckpt["max_states"] > max_states:
                raise RuntimeError(
                    f"Checkpoint max_states ({ckpt['max_states']}) > requested max_states ({max_states}). "
                    f"Cannot resume with a smaller limit."
                )
            
            # Restore state
            phase = ckpt["phase"]
            NCELLS = ckpt["NCELLS"]
            WORD_MASK = ckpt["WORD_MASK"]
            seen = ckpt["seen"]
            queue = ckpt["queue"]
            sources = ckpt["sources"]
            macro_seen = ckpt["macro_seen"]
            succ = ckpt["succ"]
            edge_count = ckpt["edge_count"]
            total_intermediate = ckpt["total_intermediate"]
            concrete_count = ckpt["concrete_placements"]
            total_templates = ckpt["target_templates"]
            
            if verbose:
                print(f"  Phase: {phase}")
                print(f"  Discovered states: {len(seen):,}")
                print(f"  Queue size: {len(queue):,}")
                print(f"  Resuming computation...")
                print()
        else:
            # Start fresh
            if verbose:
                print(f"Building templates for {a}×{b} cross-section...")
            
            templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates_general(a, b)
            
            if verbose:
                print(f"  NCELLS: {NCELLS}")
                print(f"  Concrete placements: {concrete_count}")
                print(f"  Target templates: {total_templates}")
                print(f"  State size: {3 * NCELLS} bits")
                print()
            
            # Initialize for first generation phase
            phase = "first_generation"
            sources = set()
            seen = {0}
            queue = deque([0])
            macro_seen = None
            succ = {}
            edge_count = 0
            total_intermediate = 0
        
        # Track last checkpoint state count for interval-based checkpointing
        last_checkpoint_count = len(seen)
        
        # ====================================================================
        # Phase 1: First Generation
        # ====================================================================
        if phase == "first_generation":
            if verbose:
                print("Computing first-generation sources...")
            
            first_gen_cap_hit = False
            
            while queue and not _interrupted:
                # Check max_states limit (total discovered states)
                if len(seen) >= max_states:
                    first_gen_cap_hit = True
                    if verbose:
                        print(f"  First-gen cap hit at {len(seen):,} states")
                    break
                
                state = queue.popleft()
                
                if layer_mask_general(state, 0, NCELLS) == WORD_MASK:
                    sources.add(shift_state_general(state, NCELLS))
                    continue
                
                target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
                
                for template in templates[target]:
                    nxt = apply_template_general(state, template)
                    
                    if nxt is None or nxt in seen:
                        continue
                    
                    seen.add(nxt)
                    queue.append(nxt)
                
                # Periodic checkpoint
                if checkpoint_path and len(seen) - last_checkpoint_count >= checkpoint_interval:
                    if verbose:
                        print(f"  [checkpoint] Saving at {len(seen):,} states...")
                    save_checkpoint(
                        checkpoint_path,
                        phase="first_generation",
                        a=a, b=b,
                        NCELLS=NCELLS, WORD_MASK=WORD_MASK,
                        max_states=max_states,
                        seen=seen, queue=queue,
                        sources=sources,
                        concrete_placements=concrete_count,
                        target_templates=total_templates,
                    )
                    last_checkpoint_count = len(seen)
            
            if verbose:
                print(f"  First-generation sources: {len(sources):,}")
                print(f"  First-gen tree states: {len(seen):,}")
                print()
            
            # Transition to macro closure phase
            phase = "macro_closure"
            macro_seen = set(sources)
            queue = deque(sources)
            last_checkpoint_count = len(macro_seen)
        
        # ====================================================================
        # Phase 2: Macro Closure
        # ====================================================================
        if phase == "macro_closure" and not _interrupted:
            if verbose:
                print("Computing Macro closure...")
            
            macro_cap_hit = False
            
            while queue and not _interrupted:
                # Check max_states limit (total discovered macro states)
                if len(macro_seen) >= max_states:
                    macro_cap_hit = True
                    if verbose:
                        print(f"  Macro closure cap hit at {len(macro_seen):,} states")
                    break
                
                src = queue.popleft()
                
                # Explore source: BFS until next layer shift
                successors = set()
                explore_seen = {src}
                explore_queue = deque([src])
                
                while explore_queue:
                    state = explore_queue.popleft()
                    
                    if layer_mask_general(state, 0, NCELLS) == WORD_MASK:
                        successors.add(shift_state_general(state, NCELLS))
                        continue
                    
                    target = first_empty_general(layer_mask_general(state, 0, NCELLS), NCELLS)
                    
                    for template in templates[target]:
                        nxt = apply_template_general(state, template)
                        
                        if nxt is None or nxt in explore_seen:
                            continue
                        
                        explore_seen.add(nxt)
                        explore_queue.append(nxt)
                
                intermediate = len(explore_seen) - 1
                total_intermediate += intermediate
                
                if successors:
                    succ[src] = successors
                    edge_count += len(successors)
                
                for s in successors:
                    if s not in macro_seen:
                        macro_seen.add(s)
                        queue.append(s)
                
                if verbose and len(macro_seen) % 1_000_000 == 0:
                    print(f"  Progress: {len(macro_seen):,} macro states, {edge_count:,} edges")
                
                # Periodic checkpoint
                if checkpoint_path and len(macro_seen) - last_checkpoint_count >= checkpoint_interval:
                    if verbose:
                        print(f"  [checkpoint] Saving at {len(macro_seen):,} macro states...")
                    save_checkpoint(
                        checkpoint_path,
                        phase="macro_closure",
                        a=a, b=b,
                        NCELLS=NCELLS, WORD_MASK=WORD_MASK,
                        max_states=max_states,
                        seen=macro_seen, queue=queue,
                        sources=sources,
                        macro_seen=macro_seen,
                        succ=succ,
                        edge_count=edge_count,
                        total_intermediate=total_intermediate,
                        concrete_placements=concrete_count,
                        target_templates=total_templates,
                    )
                    last_checkpoint_count = len(macro_seen)
        
        # Final checkpoint if interrupted or completed
        if checkpoint_path and (_interrupted or not _interrupted):
            if verbose:
                status = "interrupted" if _interrupted else "completed"
                print(f"  [checkpoint] Final save ({status})...")
            save_checkpoint(
                checkpoint_path,
                phase=phase,
                a=a, b=b,
                NCELLS=NCELLS, WORD_MASK=WORD_MASK,
                max_states=max_states,
                seen=macro_seen if macro_seen else seen,
                queue=queue,
                sources=sources,
                macro_seen=macro_seen,
                succ=succ,
                edge_count=edge_count,
                total_intermediate=total_intermediate,
                concrete_placements=concrete_count,
                target_templates=total_templates,
            )
        
        elapsed = time.perf_counter() - start_time
        
        # Check if state 0 is reachable
        zero_reachable = 0 in macro_seen if macro_seen else False
        
        # Determine if caps were hit
        first_gen_cap_hit = phase == "first_generation" and len(seen) >= max_states
        macro_cap_hit = phase == "macro_closure" and len(macro_seen) >= max_states
        
        stats = {
            "a": a,
            "b": b,
            "NCELLS": NCELLS,
            "state_size_bits": 3 * NCELLS,
            "concrete_placements": concrete_count if 'concrete_count' in locals() else 0,
            "target_templates": total_templates if 'total_templates' in locals() else 0,
            "first_gen_sources": len(sources) if sources else 0,
            "first_gen_tree_states": len(seen) if phase == "first_generation" else 0,
            "first_gen_cap_hit": first_gen_cap_hit,
            "macro_states": len(macro_seen) if macro_seen else 0,
            "macro_edges": edge_count,
            "macro_cap_hit": macro_cap_hit,
            "total_intermediate": total_intermediate,
            "zero_reachable": zero_reachable,
            "elapsed": elapsed,
            "interrupted": _interrupted,
        }
        
        if verbose:
            print()
            print("=== Results ===")
            if macro_seen:
                print(f"Macro states: {len(macro_seen):,}")
                print(f"Macro edges: {edge_count:,}")
                print(f"Total intermediate states: {total_intermediate:,}")
                print(f"State 0 reachable: {zero_reachable}")
            else:
                print(f"First-gen tree states: {len(seen):,}")
                print(f"First-gen sources: {len(sources):,}")
            print(f"Elapsed: {elapsed:.2f} s")
            if _interrupted:
                print(f"Status: INTERRUPTED (checkpoint saved)")
        
        return macro_seen if macro_seen else set(), succ, sources if sources else set(), stats
    
    finally:
        # Restore original signal handlers
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)
        _interrupted = False


def main():
    parser = argparse.ArgumentParser(
        description="Generalized Macro explorer for S pentacube in a×b×N boxes."
    )
    
    # Cross-section dimensions (optional if resuming)
    parser.add_argument(
        "--a",
        type=int,
        help="First cross-section dimension (optional if --resume)",
    )
    parser.add_argument(
        "--b",
        type=int,
        help="Second cross-section dimension (optional if --resume)",
    )
    
    # Checkpoint/resume options
    parser.add_argument(
        "--checkpoint",
        type=str,
        help="Path to save checkpoints (enables checkpointing)",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=500_000,
        help="Save checkpoint every N new states (default: 500000)",
    )
    parser.add_argument(
        "--resume",
        type=str,
        help="Path to checkpoint to resume from",
    )
    
    # Computation limits
    parser.add_argument(
        "--max-states",
        type=int,
        default=10_000_000,
        help="Maximum total states to discover (default: 10M)",
    )
    
    # Output control
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.resume:
        # Resuming from checkpoint
        resume_path = Path(args.resume)
        if not resume_path.exists():
            print(f"Error: Resume checkpoint does not exist: {resume_path}", file=sys.stderr)
            return 1
        
        # Load checkpoint to get dimensions
        try:
            ckpt = load_checkpoint(resume_path)
            a, b = ckpt["a"], ckpt["b"]
            
            # Warn if user provided different dimensions
            if args.a is not None and args.a != a:
                print(f"Warning: --a {args.a} ignored, using checkpoint dimension a={a}", file=sys.stderr)
            if args.b is not None and args.b != b:
                print(f"Warning: --b {args.b} ignored, using checkpoint dimension b={b}", file=sys.stderr)
        except RuntimeError as e:
            print(f"Error loading checkpoint: {e}", file=sys.stderr)
            return 1
    else:
        # Starting fresh - dimensions required
        if args.a is None or args.b is None:
            print("Error: --a and --b are required when not using --resume", file=sys.stderr)
            return 1
        a, b = args.a, args.b
        
        if a > b:
            a, b = b, a  # canonicalize
    
    verbose = not args.quiet
    
    if verbose:
        print(f"Generalized Macro explorer for S pentacube")
        print(f"Cross-section: {a}×{b}")
        print(f"Max states: {args.max_states:,}")
        if args.checkpoint:
            print(f"Checkpoint: {args.checkpoint}")
            print(f"Checkpoint interval: {args.checkpoint_interval:,} states")
        if args.resume:
            print(f"Resuming from: {args.resume}")
        print()
    
    # Run computation
    checkpoint_path = Path(args.checkpoint) if args.checkpoint else None
    resume_checkpoint = Path(args.resume) if args.resume else None
    
    macro_seen, succ, sources, stats = macro_closure_general(
        a, b,
        max_states=args.max_states,
        verbose=verbose,
        checkpoint_path=checkpoint_path,
        checkpoint_interval=args.checkpoint_interval,
        resume_checkpoint=resume_checkpoint,
    )
    
    # Write stats to file
    output_file = Path(f"/tmp/macro_generalized_{a}x{b}_results.txt")
    with open(output_file, "w") as f:
        for key, value in stats.items():
            f.write(f"{key}={value}\n")
    
    if verbose:
        print(f"\nResults written to {output_file}")
    
    # Return non-zero if interrupted
    return 1 if stats.get("interrupted", False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
