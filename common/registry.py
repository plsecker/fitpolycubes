from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass(frozen=True)
class PieceInfo:
    letter: str
    coords: np.ndarray
    catalogue_module: Optional[str]
    kurnell: Optional[int]
    shirakawa_url: Optional[str]
    shirakawa_piece: Optional[int]

PIECES = {
    "F": PieceInfo(
        letter="F",
        coords=np.array([[1,0,0],[0,1,0],[1,1,0],[1,2,0],[2,2,0]]),
        catalogue_module="catalogues.f_catalogue",
        kurnell=70, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/F.html", shirakawa_piece=9
    ),
    "I": PieceInfo(
        letter="I",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0]]),
        catalogue_module=None,
        kurnell=10, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/I.html", shirakawa_piece=1
    ),
    "L": PieceInfo(
        letter="L",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [3, 1, 0]]),
        catalogue_module="catalogues.l_catalogue",
        kurnell=11, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/L.html", shirakawa_piece=2
    ),
    "N": PieceInfo(
        letter="N",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 0, 1], [3, 0, 1]]),
        catalogue_module="catalogues.n_catalogue",
        kurnell=40, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/N.html", shirakawa_piece=8
    ),
    "P": PieceInfo(
        letter="P",
        coords=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [2, 0, 0]]),
        catalogue_module="catalogues.p_catalogue",
        kurnell=60, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/P.html", shirakawa_piece=4
    ),
    "T": PieceInfo(
        letter="T",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 2, 0]]),
        catalogue_module="catalogues.t_catalogue",
        kurnell=80, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/T.html", shirakawa_piece=7
    ),
    "U": PieceInfo(
        letter="U",
        coords=np.array([[0, 0, 0], [0, 1, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0]]),
        catalogue_module="catalogues.u_catalogue",
        kurnell=90, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/U.html", shirakawa_piece=5
    ),
    "V": PieceInfo(
        letter="V",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [0, 2, 0]]),
        catalogue_module="catalogues.v_catalogue",
        kurnell=13, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/V.html", shirakawa_piece=6
    ),
    "W": PieceInfo(
        letter="W",
        coords=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 1, 0], [2, 2, 0]]),
        catalogue_module="catalogues.w_catalogue",
        kurnell=30, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/W.html", shirakawa_piece=10
    ),
    "X": PieceInfo(
        letter="X",
        coords=np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [1, 2, 0], [2, 1, 0]]),
        catalogue_module=None,
        kurnell=50, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/X.html", shirakawa_piece=12
    ),
    "Y": PieceInfo(
        letter="Y",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [2, 1, 0]]),
        catalogue_module="catalogues.y_catalogue",
        kurnell=12, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/Y.html", shirakawa_piece=3
    ),
    "Z": PieceInfo(
        letter="Z",
        coords=np.array([[0, 0, 0],[1, 0, 0],[1, 1, 0],[1, 2, 0],[2, 2, 0]]),
        catalogue_module="catalogues.z_catalogue",
        kurnell=20, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/Z.html", shirakawa_piece=11
    ),
    "A": PieceInfo(
        letter="A",
        coords=np.array([[0, 0, 0],[1, 0, 0],[1, 0, 1],[0, 1, 0],[0, 1, 1]]),
        catalogue_module="catalogues.a_catalogue",
        kurnell=37, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-24.html", shirakawa_piece=24
    ),
    "B": PieceInfo(
        letter="B",
        coords=np.array([[0, 0, 0],[1, 0, 0],[2, 0, 0],[1, 1, 0],[1, 0, 1]]),
        catalogue_module=None,
        kurnell=82, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-19.html", shirakawa_piece=19
    ),
    "K": PieceInfo(
        letter="K",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [2, 0, 1]]),
        catalogue_module="catalogues.k_catalogue",
        kurnell=81, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-13.html", shirakawa_piece=13
    ),
    "M": PieceInfo(
        letter="M",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [1, 1, 0], [1, 1, 1]]),
        catalogue_module="catalogues.m_catalogue",
        kurnell=51, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-18.html", shirakawa_piece=18
    ),
    "Q": PieceInfo(
        letter="Q",
        coords=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[2,2,0]]),
        catalogue_module="catalogues.q_catalogue",
        kurnell=61, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-22.html", shirakawa_piece=22
    ),
    "E": PieceInfo(
        letter="E",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [1, 0, 1]]),
        catalogue_module="catalogues.e_catalogue",
        kurnell=71, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-14.html", shirakawa_piece=14
    ),
    "S": PieceInfo(
        letter="S",
        coords=np.array([[0,0,0],[1,0,0],[2,0,0],[0,0,1],[2,1,0],]),
        catalogue_module="catalogues.s_catalogue",
        kurnell=21, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-15.html", shirakawa_piece=15
    ),
    "J": PieceInfo(
        letter="J",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [2, 1, 1]]),
        catalogue_module="catalogues.j_catalogue",
        kurnell=41, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-16.html", shirakawa_piece=16
    ),
    "R": PieceInfo(
        letter="R",
        coords=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1], [2, 1, 0]]),
        catalogue_module="catalogues.r_catalogue",
        kurnell=33, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-26.html", shirakawa_piece=26
    ),
    "H": PieceInfo(
        letter="H",
        coords=np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 1], [2, 0, 1],]),
        catalogue_module="catalogues.h_catalogue",
        kurnell=31, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-23.html", shirakawa_piece=23
    ),
    "G": PieceInfo(
        letter="G",
        coords=np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 1], [2, 1, 1]]),
        catalogue_module=None,
        kurnell=36, shirakawa_url="https://puzzlewillbeplayed.com/Shirakawa/5-28.html", shirakawa_piece=28
    ),
}

PENTACUBES = {
    letter: piece.coords
    for letter, piece in PIECES.items()
}
