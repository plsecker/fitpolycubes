# Draft message to George Sicherman

*Attachment: `ee4_R_5_witness.png` (rendered figure, five pieces in
distinct colours).  Appendix below contains the full coordinates.*

---

**Subject: A 5-R construction with dual orthogonal mirror symmetry — is
this your 5-17p?**

Dear George,

I've independently reproduced a 5-R EE4 construction: five R-pentacubes
(reflections forbidden) forming a 25-cell figure with dual orthogonal
mirror symmetry.

Our formal EE4 is the two coordinate-plane mirrors (x = 0 and y = 0),
with their product the C2 about the intersection axis (z).  An
exhaustive search of the 5×5×5 box shows that EE4 admits 16 tilings,
all corresponding to one target shape under O_h (the full cube group).
We have a machine-verified witness — the attached figure, with the five
piece orientations and full coordinates in the appendix.

I haven't yet established that our particular decomposition is your
5-17p figure: the piece correspondence could not be pinned down from
the image alone.  Could you confirm whether this is your construction?

Best regards,

---

## Appendix — witness data

**The R pentacube** (canonical coordinates):

```text
R = (0,0,0) (1,0,0) (1,1,0) (1,1,1) (2,1,0)
```

**The five placements.**  Each placement is the rotation `RM[k]` applied
to R, then translated by `t`.  The rotation is written as an axis
permutation `(x,y,z) -> (...)`.

| piece | RM | rotation (x,y,z) -> | translation t | placed cells |
|---|---|---|---|---|
| R0 | RM[5] | `(-z, x, -y)` | (1, -1, 0) | `(0,0,-1) (1,-1,0) (1,0,-1) (1,0,0) (1,1,-1)` |
| R1 | RM[11] | `(z, -y, x)` | (0, 2, -1) | `(0,1,0) (0,1,1) (0,2,-1) (0,2,0) (1,1,0)` |
| R2 | RM[3] | `(z, y, -x)` | (0, -2, 0) | `(0,-2,-1) (0,-2,0) (0,-1,-2) (0,-1,-1) (1,-1,-1)` |
| R3 | RM[17] | `(-y, -z, x)` | (0, 1, -2) | `(-1,0,-1) (-1,1,-1) (-1,1,0) (0,1,-2) (0,1,-1)` |
| R4 | RM[23] | `(-y, z, -x)` | (0, -1, 1) | `(-1,-1,-1) (-1,-1,0) (-1,0,0) (0,-1,0) (0,-1,1)` |

All five rotations are proper (determinant +1); the five pieces are
pairwise disjoint and cover the target exactly.

**The target** (25 cells, bounding box x[-1,1] y[-2,2] z[-2,1]):

```text
(-1,-1,-1) (-1,-1,0) (-1,0,-1) (-1,0,0) (-1,1,-1) (-1,1,0)
(0,-2,-1) (0,-2,0) (0,-1,-2) (0,-1,-1) (0,-1,0) (0,-1,1)
(0,0,-1) (0,1,-2) (0,1,-1) (0,1,0) (0,1,1) (0,2,-1) (0,2,0)
(1,-1,-1) (1,-1,0) (1,0,-1) (1,0,0) (1,1,-1) (1,1,0)
```

Layer by layer, z from top to bottom:

```text
z=1:  (0,-1,1) (0,1,1)
z=0:  (-1,-1,0) (-1,0,0) (-1,1,0) (0,-2,0) (0,-1,0) (0,1,0) (0,2,0) (1,-1,0) (1,0,0) (1,1,0)
z=-1: (-1,-1,-1) (-1,0,-1) (-1,1,-1) (0,-2,-1) (0,-1,-1) (0,0,-1) (0,1,-1) (0,2,-1) (1,-1,-1) (1,0,-1) (1,1,-1)
z=-2: (0,-1,-2) (0,1,-2)
```

**Verification.**  The witness is machine-verified
(`tools/verify_ee4_R_witness.py`, ALL CHECKS PASSED): 25 cells,
face-connected, exact EE4 symmetry (order 4), five proper-rotation R
placements, pairwise disjoint, exact cover.  Exhaustive search context:
16 tilings, 4 canonical targets (one shape under O_h), 119,023 nodes.