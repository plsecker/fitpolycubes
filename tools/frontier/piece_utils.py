#!/usr/bin/env python3
"""
Generic piece orientation utilities for the Macro framework.

Provides piece-agnostic functions for:
- Generating all unique orientations of any pentacube
- Computing layer occupancy profiles
- Validating placements against any piece's orientation set
- Building template sets for any piece and cross-section

Usage:
    from tools.frontier.piece_utils import (
        generate_orientations, get_orientation_table,
        build_templates, validate_placement,
        layer_mask, first_empty, apply_template, shift_state
    )
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Rotation matrices (24 cube rotations)
# Generated once and cached
_ROTATION_MATRICES: Optional[List[np.ndarray]] = None


def _get_rotation_matrices() -> List[np.ndarray]:
    """Get the 24 rotation matrices of a cube."""
    global _ROTATION_MATRICES
    if _ROTATION_MATRICES is not None:
        return _ROTATION_MATRICES
    
    # Generate all 3x3 rotation matrices with entries in {-1, 0, 1}
    # and determinant +1 (proper rotations)
    matrices = []
    for axes in [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]:
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    m = np.zeros((3, 3), dtype=int)
                    m[0, axes[0]] = sx
                    m[1, axes[1]] = sy
                    m[2, axes[2]] = sz
                    if np.linalg.det(m) > 0:
                        matrices.append(m)
    
    _ROTATION_MATRICES = matrices
    return matrices


def generate_orientations(
    coords: np.ndarray,
    include_reflections: bool = False,
) -> List[np.ndarray]:
    """Generate all unique orientations of a polycube.
    
    Args:
        coords: Nx3 array of canonical coordinates
        include_reflections: If True, include reflected orientations
                             (improper rotations). Default: False.
    
    Returns:
        List of unique orientation arrays, each normalized to origin.
    """
    rotations = _get_rotation_matrices()
    
    seen: Set[Tuple[Tuple[int, int, int], ...]] = set()
    orientations: List[np.ndarray] = []
    
    # If including reflections, also use matrices with det = -1
    if include_reflections:
        all_mats = list(rotations)
        for axes in [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        m = np.zeros((3, 3), dtype=int)
                        m[0, axes[0]] = sx
                        m[1, axes[1]] = sy
                        m[2, axes[2]] = sz
                        if np.linalg.det(m) < 0:
                            all_mats.append(m)
        mats_to_use = all_mats
    else:
        mats_to_use = rotations
    
    for rot in mats_to_use:
        rp = coords @ rot.T
        rp = rp - rp.min(axis=0)
        rp_tuple = tuple(sorted(tuple(map(int, p)) for p in rp))
        
        if rp_tuple not in seen:
            seen.add(rp_tuple)
            orientations.append(np.array(rp_tuple))
    
    return orientations


def get_orientation_table(
    coords: np.ndarray,
    include_reflections: bool = False,
) -> Dict[str, dict]:
    """Build a detailed orientation feature table for any polycube.
    
    Returns a dict mapping orientation IDs to feature dicts with:
        id, cells, z_span, layer_occ, x_span, y_span, xy_proj_size
    """
    orientations = generate_orientations(coords, include_reflections)
    
    table = {}
    for i, o in enumerate(orientations):
        z_span = int(o[:, 2].max() - o[:, 2].min() + 1)
        x_span = int(o[:, 0].max() - o[:, 0].min() + 1)
        y_span = int(o[:, 1].max() - o[:, 1].min() + 1)
        
        layer_occ = [0, 0, 0]
        for cell in o:
            z = int(cell[2])
            if z < len(layer_occ):
                layer_occ[z] += 1
        
        xy_proj = set((int(c[0]), int(c[1])) for c in o)
        
        table[f"O{i}"] = {
            "id": i,
            "cells": [[int(c[0]), int(c[1]), int(c[2])] for c in o],
            "z_span": z_span,
            "layer_occ": layer_occ,
            "x_span": x_span,
            "y_span": y_span,
            "xy_proj_size": len(xy_proj),
            "l0_cells": layer_occ[0],
            "l1_cells": layer_occ[1] if len(layer_occ) > 1 else 0,
            "l2_cells": layer_occ[2] if len(layer_occ) > 2 else 0,
        }
    
    return table


def get_orientation_set(
    coords: np.ndarray,
    include_reflections: bool = False,
) -> Set[Tuple[Tuple[int, int, int], ...]]:
    """Get the set of all unique orientation canonical forms.
    
    Each orientation is a sorted tuple of (x, y, z) tuples normalized
    so the minimum coordinate is at the origin.
    """
    orientations = generate_orientations(coords, include_reflections)
    return {
        tuple(sorted(tuple(map(int, c)) for c in o))
        for o in orientations
    }


def build_templates(
    coords: np.ndarray,
    a: int,
    b: int,
    max_z: int = 20,
) -> Tuple[Dict[int, List[int]], int, int, int, int]:
    """Build template set for a piece in a×b cross-section.
    
    This is the generic version of build_templates_general.
    
    Args:
        coords: Nx3 array of piece coordinates
        a, b: Cross-section dimensions
        max_z: Maximum z to search for placements (default: 20)
    
    Returns:
        (templates, NCELLS, WORD_MASK, concrete_count, total_templates)
    """
    from common.polycube_utils import generate_placements
    
    # Build piece dict for generate_placements
    piece_key = "generic"
    from common.registry import PENTACUBES
    # Use the actual piece if it's in the registry
    # Otherwise use the provided coords directly
    actual_piece = coords
    
    raw, _ = generate_placements(
        actual_piece,
        (a, b, max_z),
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
            packed = make_shifted_template(cells, z, a, b)
            
            if packed is None:
                continue
            
            if packed in seen[target]:
                continue
            
            seen[target].add(packed)
            result[target].append(packed)
    
    total_templates = sum(len(v) for v in result.values())
    
    return result, NCELLS, WORD_MASK, concrete_count, total_templates


def make_shifted_template(
    placement_cells: Tuple[Tuple[int, int, int], ...],
    target_z: int,
    a: int,
    b: int,
    layers: int = 3,
) -> Optional[int]:
    """Translate a placement so the chosen target cell lies on layer 0.
    
    Args:
        placement_cells: Tuple of (x, y, z) cells
        target_z: The z-coordinate of the cell to place on layer 0
        a, b: Cross-section dimensions
        layers: Number of layers in the state (default: 3)
    
    Returns:
        Packed state integer, or None if placement extends beyond layers
    """
    NCELLS = a * b
    min_z = min(z for _, _, z in placement_cells)
    shifted_masks = [0] * layers
    target_rel = target_z - min_z
    
    for x, y, z in placement_cells:
        rel = z - min_z - target_rel
        
        if rel < 0 or rel >= layers:
            return None
        
        cell_id = x + a * y
        shifted_masks[rel] |= (1 << cell_id)
    
    state = 0
    for i, mask in enumerate(shifted_masks):
        state |= (mask << (i * NCELLS))
    
    return state


def layer_mask(state: int, layer: int, NCELLS: int) -> int:
    """Extract layer mask from state."""
    return (state >> (layer * NCELLS)) & ((1 << NCELLS) - 1)


def first_empty(mask: int, NCELLS: int) -> int:
    """Find first empty cell in mask."""
    WORD_MASK = (1 << NCELLS) - 1
    missing = WORD_MASK & ~mask
    
    if not missing:
        return -1
    
    low = missing & -missing
    return low.bit_length() - 1


def apply_template(state: int, template: int) -> Optional[int]:
    """Apply template to state if disjoint."""
    if state & template:
        return None
    return state | template


def shift_state(state: int, NCELLS: int) -> int:
    """Shift state down by one layer."""
    return state >> NCELLS


def validate_placement(
    placement: Tuple[Tuple[int, int, int], ...],
    orientation_set: Set[Tuple[Tuple[int, int, int], ...]],
    a: int,
    b: int,
    z: int,
) -> Dict:
    """Validate a single placement against a piece's orientation set.
    
    Args:
        placement: Sorted tuple of (x, y, z) cells
        orientation_set: Set of canonical orientation tuples
        a, b, z: Box dimensions
    
    Returns:
        Dict with validation results
    """
    errors = []
    
    # Check length
    if len(placement) != 5:
        return {"valid": False, "errors": [f"Has {len(placement)} cells, expected 5"]}
    
    # Check bounds
    for x, y, zc in placement:
        if not (0 <= x < a and 0 <= y < b and 0 <= zc < z):
            errors.append(f"Cell ({x},{y},{zc}) out of bounds")
    
    # Check shape matches piece
    arr = np.array(placement)
    arr = arr - arr.min(axis=0)
    canonical = tuple(sorted(tuple(map(int, r)) for r in arr))
    if canonical not in orientation_set:
        errors.append("Placement shape does not match any piece orientation")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_placement_list(
    placements: List,
    orientation_set: Set[Tuple[Tuple[int, int, int], ...]],
    a: int,
    b: int,
    z: int,
) -> Dict:
    """Validate a list of placements independently.
    
    Each placement can be:
    - Tuple of 15 ints (flat format: x1,y1,z1,...,x5,y5,z5)
    - Tuple of 5 (x,y,z) tuples
    
    Returns dict with validation results.
    """
    errors: List[str] = []
    
    expected_cells = a * b * z
    expected_pieces = expected_cells // 5 if expected_cells % 5 == 0 else 0
    
    # Normalize placements
    normalized: List[Tuple[Tuple[int, int, int], ...]] = []
    for p in placements:
        if len(p) == 15:
            cells = tuple(sorted((p[i], p[i+1], p[i+2]) for i in range(0, 15, 3)))
            normalized.append(cells)
        elif len(p) == 5 and all(isinstance(c, (tuple, list)) for c in p):
            cells = tuple(sorted(tuple(c) for c in p))
            normalized.append(cells)
        else:
            errors.append(f"Unrecognized placement format: {p}")
    
    # Check piece count
    actual_pieces = len(normalized)
    if expected_pieces and actual_pieces != expected_pieces:
        errors.append(f"Piece count: got {actual_pieces}, expected {expected_pieces}")
    
    # Check each placement
    all_cells: Set[Tuple[int, int, int]] = set()
    invalid_shapes = 0
    out_of_bounds = 0
    overlaps = 0
    
    for i, placement in enumerate(normalized):
        if len(placement) != 5:
            errors.append(f"Placement {i}: has {len(placement)} cells, expected 5")
            continue
        
        for x, y, zc in placement:
            if not (0 <= x < a and 0 <= y < b and 0 <= zc < z):
                out_of_bounds += 1
        
        # Check shape
        arr = np.array(placement)
        arr = arr - arr.min(axis=0)
        canonical = tuple(sorted(tuple(map(int, r)) for r in arr))
        if canonical not in orientation_set:
            invalid_shapes += 1
        
        for cell in placement:
            if cell in all_cells:
                overlaps += 1
            all_cells.add(cell)
    
    # Check coverage
    expected_set = {(x, y, zc) for x in range(a) for y in range(b) for zc in range(z)}
    missing = expected_set - all_cells
    extra = all_cells - expected_set
    
    valid = (
        len(errors) == 0
        and invalid_shapes == 0
        and out_of_bounds == 0
        and overlaps == 0
        and len(missing) == 0
        and len(extra) == 0
        and len(all_cells) == expected_cells
    )
    
    return {
        "valid": valid,
        "a": a,
        "b": b,
        "z": z,
        "expected_cells": expected_cells,
        "expected_pieces": expected_pieces,
        "actual_pieces": actual_pieces,
        "actual_cells": len(all_cells),
        "errors": errors,
        "invalid_shapes": invalid_shapes,
        "out_of_bounds": out_of_bounds,
        "overlaps": overlaps,
        "missing_cells": len(missing),
        "extra_cells": len(extra),
    }