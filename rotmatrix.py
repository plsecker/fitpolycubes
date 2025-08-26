"""
Rotation matrices for cube symmetries
Created on Sun May  1 20:40:22 2016
@author: Philip
"""

import numpy as np

# Create rotation matrices R where Rp rotates column vector p
# equivalently, p @ R.T rotates row vector p

# Rotations about x-axis
Rx90   = np.array([[1, 0, 0],
                   [0, 0, -1],
                   [0, 1, 0]], dtype=int)

Rxm90  = np.array([[1, 0, 0],
                   [0, 0, 1],
                   [0, -1, 0]], dtype=int)

Rx180  = np.array([[1, 0, 0],
                   [0, -1, 0],
                   [0, 0, -1]], dtype=int)

# Rotations about y-axis
Ry90   = np.array([[0, 0, 1],
                   [0, 1, 0],
                   [-1, 0, 0]], dtype=int)

Rym90  = np.array([[0, 0, -1],
                   [0, 1, 0],
                   [1, 0, 0]], dtype=int)

Ry180  = np.array([[-1, 0, 0],
                   [0, 1, 0],
                   [0, 0, -1]], dtype=int)

# Rotations about z-axis
Rz90   = np.array([[0, -1, 0],
                   [1,  0, 0],
                   [0,  0, 1]], dtype=int)

Rzm90  = np.array([[0, 1, 0],
                   [-1, 0, 0],
                   [0, 0, 1]], dtype=int)

Rz180  = np.array([[-1, 0, 0],
                   [0, -1, 0],
                   [0,  0, 1]], dtype=int)

# Identity (no rotation)
Meye = np.eye(3, dtype=int)

# Build master rotation list (24 cube symmetries)
RM = [None] * 24
RM[0]  = Meye
RM[1]  = Rym90
RM[2]  = Ry180
RM[3]  = Ry90
RM[4]  = Meye @ Rz90
RM[5]  = Rym90 @ Rz90
RM[6]  = Ry180 @ Rz90
RM[7]  = Ry90 @ Rz90
RM[8]  = Meye @ (Rz90 @ Rz90)
RM[9]  = Rym90 @ (Rz90 @ Rz90)
RM[10] = Ry180 @ (Rz90 @ Rz90)
RM[11] = Ry90 @ (Rz90 @ Rz90)
RM[12] = Meye @ (Rz90 @ Rz90 @ Rz90)
RM[13] = Rym90 @ (Rz90 @ Rz90 @ Rz90)
RM[14] = Ry180 @ (Rz90 @ Rz90 @ Rz90)
RM[15] = Ry90 @ (Rz90 @ Rz90 @ Rz90)
RM[16] = Meye @ Rx90
RM[17] = Rym90 @ Rx90
RM[18] = Ry180 @ Rx90
RM[19] = Ry90 @ Rx90
RM[20] = Meye @ Rxm90
RM[21] = Rym90 @ Rxm90
RM[22] = Ry180 @ Rxm90
RM[23] = Ry90 @ Rxm90
