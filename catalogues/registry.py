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
from catalogues.q_catalogue import Q_CATALOGUE
from catalogues.l_catalogue import L_CATALOGUE
from catalogues.p_catalogue import P_CATALOGUE
from catalogues.z_catalogue import Z_CATALOGUE
from catalogues.w_catalogue import W_CATALOGUE
from catalogues.t_catalogue import T_CATALOGUE
from catalogues.u_catalogue import U_CATALOGUE

CATALOGUES = {
    "F": F_CATALOGUE,
    "N": N_CATALOGUE,
    "V": V_CATALOGUE,
    "L35": L35_CATALOGUE,
    "Q": Q_CATALOGUE,
    "L": L_CATALOGUE,
    "P": P_CATALOGUE,
    "Z": Z_CATALOGUE,
    "W": W_CATALOGUE,
    "T": T_CATALOGUE,
    "U": U_CATALOGUE,
}
