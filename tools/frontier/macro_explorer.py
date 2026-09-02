#!/usr/bin/env python3
"""
Generic Macro explorer for any pentacube in a×b×N boxes.

This is the piece-agnostic version of macro_generalized.py.
It accepts a piece letter (or coordinates) and cross-section dimensions.

Usage:
    # Explore T in 3×10 cross-section
    python3 tools/frontier/macro_explorer.py --piece T --a 3 --b 10
    
    # Explore S in 5×6 (same as original macro_generalized)
    python3 tools/frontier/macro_explorer.py --piece S --a 5 --b 6
    
    # With checkpointing
    python3 tools/frontier/macro_explorer.py --piece T --a 3 --b 10 \
        --checkpoint /tmp/t_3x10.ckpt --checkpoint-interval 500000
    
    # Resume from checkpoint
    python3 tools/frontier/macro_explorer.py --resume /tmp/t_3x10.ckpt
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

from common.registry import PENTACUBES, PIECES
from tools.frontier.piece_utils import (
    build_templates,
    layer_mask,
    first_empty,
    apply_template,
    shift_state,
)

CHECKPOINT_VERSION = 2


def save_checkpoint(
    checkpoint_path: Path,
    phase: str,
    piece_letter: str,
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
    """Save checkpoint atomically."""
    checkpoint_path = Path(checkpoint_path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_dir = checkpoint_path.parent / f".ckpt_temp_{int(time.time())}"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        metadata = {
            "version": CHECKPOINT_VERSION,
            "phase": phase,
            "piece": piece_letter,
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
        
        temp_meta = temp_dir / "metadata.json"
        with open(temp_meta, "w") as f:
            json.dump(metadata, f, indent=2)
        
        temp_seen = temp_dir / "seen.json"
        with open(temp_seen, "w") as f:
            json.dump(sorted(seen), f)
        
        temp_queue = temp_dir / "queue.json"
        with open(temp_queue, "w") as f:
            json.dump(list(queue), f)
        
        if sources is not None:
            temp_sources = temp_dir / "sources.json"
            with open(temp_sources, "w") as f:
                json.dump(sorted(sources), f)
        
        if macro_seen is not None:
            temp_macro_seen = temp_dir / "macro_seen.json"
            with open(temp_macro_seen, "w") as f:
                json.dump(sorted(macro_seen), f)
        
        if succ is not None:
            temp_succ = temp_dir / "succ.json"
            succ_serializable = {
                str(src): sorted(succs)
                for src, succs in sorted(succ.items())
            }
            with open(temp_succ, "w") as f:
                json.dump(succ_serializable, f)
        
        # Atomic rename
        if checkpoint_path.exists():
            import shutil
            shutil.rmtree(checkpoint_path)
        temp_dir.rename(checkpoint_path)
        
    except Exception as e:
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to save checkpoint: {e}")


def load_checkpoint(checkpoint_path: Path) -> dict:
    """Load checkpoint and validate contents."""
    checkpoint_path = Path(checkpoint_path)
    
    if not checkpoint_path.exists():
        raise RuntimeError(f"Checkpoint does not exist: {checkpoint_path}")
    if not checkpoint_path.is_dir():
        raise RuntimeError(f"Checkpoint path is not a directory: {checkpoint_path}")
    
    meta_path = checkpoint_path / "metadata.json"
    if not meta_path.exists():
        raise RuntimeError(f"Checkpoint missing metadata.json")
    
    with open(meta_path, "r") as f:
        metadata = json.load(f)
    
    version = metadata.get("version")
    if version != CHECKPOINT_VERSION:
        raise RuntimeError(
            f"Checkpoint version mismatch: expected {CHECKPOINT_VERSION}, got {version}"
        )
    
    required_fields = ["phase", "piece", "a", "b", "NCELLS", "WORD_MASK", "max_states"]
    for field in required_fields:
        if field not in metadata:
            raise RuntimeError(f"Checkpoint missing required field: {field}")
    
    seen_path = checkpoint_path / "seen.json"
    with open(seen_path, "r") as f:
        seen = set(json.load(f))
    
    queue_path = checkpoint_path / "queue.json"
    with open(queue_path, "r") as f:
        queue = deque(json.load(f))
    
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
        succ = {
            int(src): set(succs)
            for src, succs in succ_serializable.items()
        }
    
    return {
        "metadata": metadata,
        "phase": metadata["phase"],
        "piece": metadata["piece"],
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


_interrupted = False


def signal_handler(signum, frame):
    global _interrupted
    _interrupted = True
    print(f"\nInterrupted (signal {signum}). Saving checkpoint and exiting...")


def macro_closure(
    piece_letter: str,
    a: int,
    b: int,
    max_states: int = 10_000_000,
    verbose: bool = True,
    checkpoint_path: Path | None = None,
    checkpoint_interval: int = 500_000,
    resume_checkpoint: Path | None = None,
):
    """Compute Macro closure for piece in a×b cross-section."""
    global _interrupted
    
    original_sigint = signal.signal(signal.SIGINT, signal_handler)
    original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        start_time = time.perf_counter()
        
        if resume_checkpoint is not None:
            if verbose:
                print(f"Resuming from checkpoint: {resume_checkpoint}")
            
            ckpt = load_checkpoint(resume_checkpoint)
            
            if ckpt["piece"] != piece_letter:
                raise RuntimeError(
                    f"Checkpoint piece mismatch: checkpoint is {ckpt['piece']}, "
                    f"requested {piece_letter}"
                )
            if ckpt["a"] != a or ckpt["b"] != b:
                raise RuntimeError(
                    f"Checkpoint dimensions mismatch: checkpoint is {ckpt['a']}×{ckpt['b']}, "
                    f"requested {a}×{b}"
                )
            if ckpt["max_states"] > max_states:
                raise RuntimeError(
                    f"Checkpoint max_states ({ckpt['max_states']}) > requested ({max_states})"
                )
            
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
        else:
            piece_coords = PENTACUBES[piece_letter]
            
            if verbose:
                print(f"Building templates for {piece_letter} in {a}×{b} cross-section...")
            
            templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates(
                piece_coords, a, b
            )
            
            if verbose:
                print(f"  NCELLS: {NCELLS}")
                print(f"  Concrete placements: {concrete_count}")
                print(f"  Target templates: {total_templates}")
                print(f"  State size: {3 * NCELLS} bits")
            
            phase = "first_generation"
            sources = set()
            seen = {0}
            queue = deque([0])
            macro_seen = None
            succ = {}
            edge_count = 0
            total_intermediate = 0

        # Ensure templates are available (needed for resume from checkpoint)
        if 'templates' not in dir() or templates is None:
            piece_coords = PENTACUBES[piece_letter]
            templates, NCELLS, WORD_MASK, concrete_count, total_templates = build_templates(
                piece_coords, a, b
            )
            if verbose:
                print(f"  Rebuilt templates: {concrete_count} placements, {total_templates} templates")

        last_checkpoint_count = len(seen)
        
        # Phase 1: First Generation
        if phase == "first_generation":
            if verbose:
                print("Computing first-generation sources...")
            
            while queue and not _interrupted:
                if len(seen) >= max_states:
                    if verbose:
                        print(f"  First-gen cap hit at {len(seen):,} states")
                    break
                
                state = queue.popleft()
                
                if layer_mask(state, 0, NCELLS) == WORD_MASK:
                    sources.add(shift_state(state, NCELLS))
                    continue
                
                target = first_empty(layer_mask(state, 0, NCELLS), NCELLS)
                
                for template in templates[target]:
                    nxt = apply_template(state, template)
                    if nxt is None or nxt in seen:
                        continue
                    seen.add(nxt)
                    queue.append(nxt)
                
                if checkpoint_path and len(seen) - last_checkpoint_count >= checkpoint_interval:
                    if verbose:
                        print(f"  [checkpoint] Saving at {len(seen):,} states...")
                    save_checkpoint(
                        checkpoint_path,
                        phase="first_generation",
                        piece_letter=piece_letter,
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
            
            phase = "macro_closure"
            macro_seen = set(sources)
            queue = deque(sources)
            last_checkpoint_count = len(macro_seen)
        
        # Phase 2: Macro Closure
        if phase == "macro_closure" and not _interrupted:
            if verbose:
                print("Computing Macro closure...")
            
            while queue and not _interrupted:
                if len(macro_seen) >= max_states:
                    if verbose:
                        print(f"  Macro closure cap hit at {len(macro_seen):,} states")
                    break
                
                src = queue.popleft()
                
                successors = set()
                explore_seen = {src}
                explore_queue = deque([src])
                
                while explore_queue:
                    state = explore_queue.popleft()
                    
                    if layer_mask(state, 0, NCELLS) == WORD_MASK:
                        successors.add(shift_state(state, NCELLS))
                        continue
                    
                    target = first_empty(layer_mask(state, 0, NCELLS), NCELLS)
                    
                    for template in templates[target]:
                        nxt = apply_template(state, template)
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
                
                if checkpoint_path and len(macro_seen) - last_checkpoint_count >= checkpoint_interval:
                    if verbose:
                        print(f"  [checkpoint] Saving at {len(macro_seen):,} macro states...")
                    save_checkpoint(
                        checkpoint_path,
                        phase="macro_closure",
                        piece_letter=piece_letter,
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
        
        # Final checkpoint
        if checkpoint_path:
            if verbose:
                status = "interrupted" if _interrupted else "completed"
                print(f"  [checkpoint] Final save ({status})...")
            save_checkpoint(
                checkpoint_path,
                phase=phase,
                piece_letter=piece_letter,
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
        zero_reachable = 0 in macro_seen if macro_seen else False
        
        stats = {
            "piece": piece_letter,
            "a": a,
            "b": b,
            "NCELLS": NCELLS,
            "state_size_bits": 3 * NCELLS,
            "concrete_placements": concrete_count,
            "target_templates": total_templates,
            "first_gen_sources": len(sources) if sources else 0,
            "first_gen_tree_states": len(seen) if phase == "first_generation" else 0,
            "first_gen_cap_hit": phase == "first_generation" and len(seen) >= max_states,
            "macro_states": len(macro_seen) if macro_seen else 0,
            "macro_edges": edge_count,
            "macro_cap_hit": phase == "macro_closure" and len(macro_seen) >= max_states,
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
                print("Status: INTERRUPTED")
        
        return macro_seen if macro_seen else set(), succ, sources if sources else set(), stats
    
    finally:
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)
        _interrupted = False


def main():
    parser = argparse.ArgumentParser(
        description="Generic Macro explorer for any pentacube in a×b×N boxes."
    )
    
    parser.add_argument("--piece", type=str, default="S",
                        help="Piece letter (e.g., T, S, V, W). Default: S")
    parser.add_argument("--a", type=int, help="First cross-section dimension")
    parser.add_argument("--b", type=int, help="Second cross-section dimension")
    parser.add_argument("--checkpoint", type=str, help="Path to save checkpoints")
    parser.add_argument("--checkpoint-interval", type=int, default=500_000,
                        help="Save checkpoint every N new states")
    parser.add_argument("--resume", type=str, help="Path to checkpoint to resume from")
    parser.add_argument("--max-states", type=int, default=10_000_000,
                        help="Maximum total states to discover")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    
    args = parser.parse_args()
    
    if args.resume:
        resume_path = Path(args.resume)
        if not resume_path.exists():
            print(f"Error: Resume checkpoint does not exist: {resume_path}", file=sys.stderr)
            return 1
        
        ckpt = load_checkpoint(resume_path)
        piece_letter = ckpt["piece"]
        a, b = ckpt["a"], ckpt["b"]
        
        if args.piece != "S" and args.piece != piece_letter:
            print(f"Warning: --piece {args.piece} ignored, using checkpoint piece {piece_letter}",
                  file=sys.stderr)
    else:
        if args.a is None or args.b is None:
            print("Error: --a and --b are required when not using --resume", file=sys.stderr)
            return 1
        piece_letter = args.piece.upper()
        a, b = args.a, args.b
        if a > b:
            a, b = b, a
    
    verbose = not args.quiet
    
    if verbose:
        print(f"Generic Macro explorer for {piece_letter} pentacube")
        print(f"Cross-section: {a}×{b}")
        print(f"Max states: {args.max_states:,}")
        if args.checkpoint:
            print(f"Checkpoint: {args.checkpoint}")
        if args.resume:
            print(f"Resuming from: {args.resume}")
        print()
    
    checkpoint_path = Path(args.checkpoint) if args.checkpoint else None
    resume_checkpoint = Path(args.resume) if args.resume else None
    
    macro_seen, succ, sources, stats = macro_closure(
        piece_letter, a, b,
        max_states=args.max_states,
        verbose=verbose,
        checkpoint_path=checkpoint_path,
        checkpoint_interval=args.checkpoint_interval,
        resume_checkpoint=resume_checkpoint,
    )
    
    output_file = Path(f"/tmp/macro_{piece_letter}_{a}x{b}_results.txt")
    with open(output_file, "w") as f:
        for key, value in stats.items():
            f.write(f"{key}={value}\n")
    
    if verbose:
        print(f"\nResults written to {output_file}")
    
    return 1 if stats.get("interrupted", False) else 0


if __name__ == "__main__":
    raise SystemExit(main())