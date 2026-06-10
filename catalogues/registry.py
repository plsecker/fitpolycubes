"""
Centralized registry for all polycube catalogues.

Adding a new pentacube catalogue requires only:
1. Create catalogues/{name}_catalogue.py
2. Add {NAME}_CATALOGUE to this registry
"""

from catalogues.f_catalogue import F_CATALOGUE
from catalogues.n_catalogue import N_CATALOGUE
from catalogues.v_catalogue import V_CATALOGUE
from catalogues.l35_catalogue import L35_CATALOGUE


CATALOGUES = {
    "F": F_CATALOGUE,
    "N": N_CATALOGUE,
    "V": V_CATALOGUE,
    "L35": L35_CATALOGUE,
}
