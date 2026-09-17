# EE4 5-R — query to George Sicherman (status note)

**Date:** 2026-09-17 · **Branch:** `frontier-solutions` · **State:** research
question handed back to George; no further image archaeology.

## Verified result

A 5-R EE4 construction exists and is machine-verified:

- **Class:** EE4 — dual orthogonal mirror symmetry: mirrors x = 0 and
  y = 0, product c2 about the z-axis (matches George's "mirror symmetry
  through two different coordinate axes").
- **Volume:** 25 cells; five proper-rotation R pentacubes (reflections
  forbidden), pairwise disjoint, exact cover.
- **Exhaustive search (5×5×5 box):** 16 tilings, 4 canonical targets —
  all one target shape under O_h; 119,023 nodes; 2,072,331 connected
  25-cell targets.  Only EE4 and CE3 of the nine order-4 classes admit
  5-R tilings; CE3's second mirror is diagonal (x = y), so it does not
  match George's definition.
- **Regression tests:** `tests/test_ee4_R_witness.py` and
  `tests/test_ee4_coordinate_frame.py` pass; independent verifier
  `tools/verify_ee4_R_witness.py` reports ALL CHECKS PASSED.

## Witness identifiers

- Fixture: `tests/fixtures/ee4_R_5.json` (canonical target #1, first
  tiling; orientation-multiset class {RM 3, 5, 11, 17, 23}).
- Placements:

  | piece | RM | rotation (x,y,z) -> | translation |
  |---|---|---|---|
  | R0 | RM[5] | `(-z, x, -y)` | (1, -1, 0) |
  | R1 | RM[11] | `(z, -y, x)` | (0, 2, -1) |
  | R2 | RM[3] | `(z, y, -x)` | (0, -2, 0) |
  | R3 | RM[17] | `(-y, -z, x)` | (0, 1, -2) |
  | R4 | RM[23] | `(-y, z, -x)` | (0, -1, 1) |

- Target: 25 cells, bbox x[-1,1] y[-2,2] z[-2,1]; z-layer counts
  (top to bottom) 2, 10/11, 11/10, 2.
- Package for George: `reports/ee4_R_5_witness.png` (render),
  `reports/ee4_R_5_witness_description.md` (description),
  `reports/ee4_R_5_george_message.md` (draft message).

## Unresolved question

Whether our particular decomposition is George's pictured 5-17p
construction.  The palette diagrams could not be unambiguously decoded
and the figure's perspective projection could not be pinned, so the
piece correspondence was **not** established from the image.  The
comparison is reported as DISTINCT/UNRESOLVED; no match is claimed.

## Exact question sent to George

> "I've independently reproduced a 5-R EE4 construction.  Our formal EE4
> is the two coordinate-plane mirrors with their product the C2 about
> the intersection axis.  We find 16 tilings, corresponding to one
> target shape under O_h, and have a machine-verified witness.  I
> haven't yet established that our particular decomposition is your
> 5-17p figure.  Could you confirm whether this is your construction?"

(Full draft message with figure and coordinate appendix:
`reports/ee4_R_5_george_message.md`.)

## Follow-up

- If George confirms the construction: record the confirmation, mark the
  correspondence as confirmed, and identify the matching placement
  (y-wall vs x-wall, and which z-axis fixed cell).
- If George says it is a different construction: the EE4 result stands
  on its own; the 5-17p figure remains unmatched.
- Nothing has been committed (per instruction).