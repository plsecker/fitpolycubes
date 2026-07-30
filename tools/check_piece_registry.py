#!/usr/bin/env python3
import sys
import os
import importlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from common.registry import PIECES
from catalogues.registry import CATALOGUES
from common.rotmatrix import RM
import numpy as np

def normalize(p):
    min_x = min(c[0] for c in p)
    min_y = min(c[1] for c in p)
    min_z = min(c[2] for c in p)
    return tuple(sorted((int(c[0]-min_x), int(c[1]-min_y), int(c[2]-min_z)) for c in p))

def get_all_rotations(p):
    p_arr = np.array(p)
    rots = set()
    for rot in RM:
        rp = p_arr @ rot.T
        rots.add(normalize(rp))
    return rots

def main():
    errors = []
    warnings = []
    
    letters = set()
    geometries = []
    catalogue_modules = set()
    kurnells = set()
    shirakawas = set()
    
    for letter, piece in PIECES.items():
        if letter in letters:
            errors.append(f"Duplicate letter: {letter}")
        letters.add(letter)
        
        # Check geometry
        rots = get_all_rotations(piece.coords)
        found_dup = False
        for g_letter, g_rots in geometries:
            if any(r in g_rots for r in rots):
                warnings.append(f"Duplicate geometry: {letter} and {g_letter} appear identical")
                found_dup = True
                break
        if not found_dup:
            geometries.append((letter, rots))
            
        # Check catalogue module
        if piece.catalogue_module:
            if piece.catalogue_module in catalogue_modules:
                errors.append(f"Duplicate catalogue module: {piece.catalogue_module} in {letter}")
            catalogue_modules.add(piece.catalogue_module)
            
            # Check if catalogue module exists by actually importing it (matching check_repo.py logic)
            try:
                importlib.import_module(piece.catalogue_module)
            except (ImportError, Exception) as exc:
                errors.append(f"Catalogue module does not exist or failed to import: {piece.catalogue_module} in {letter} ({exc})")
                
        # Check Kurnell
        if piece.kurnell is not None:
            if piece.kurnell in kurnells:
                errors.append(f"Duplicate Kurnell number: {piece.kurnell} in {letter}")
            kurnells.add(piece.kurnell)
            
        # Check Shirakawa
        if piece.shirakawa_url is not None and piece.shirakawa_piece is not None:
            shirakawa_ref = f"{piece.shirakawa_url}:{piece.shirakawa_piece}"
            if shirakawa_ref in shirakawas:
                warnings.append(f"Duplicate Shirakawa reference: {shirakawa_ref} in {letter}")
            shirakawas.add(shirakawa_ref)
            
        # Check metadata completeness
        if piece.catalogue_module is None:
            warnings.append(f"Missing catalogue module for {letter}")
        if piece.kurnell is None:
            warnings.append(f"Missing Kurnell number for {letter}")
        if piece.shirakawa_url is None:
            warnings.append(f"Missing Shirakawa URL for {letter}")
            
    print("=== Registry Audit Report ===")
    print(f"Total pieces in registry: {len(PIECES)}")
    
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
            
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        print("\nValidation failed.")
        sys.exit(1)
        
    print("\nValidation passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
