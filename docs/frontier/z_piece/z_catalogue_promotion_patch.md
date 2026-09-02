# Z Catalogue Promotion Patch — for human review

**Date**: 2026-08-28  
**Status**: NOT APPLIED. `catalogues/z_catalogue.py` is untouched; every
number below was measured against a temporary in-memory copy.

## 1. What the patch does

* Adds `PUBLISHED_SOLUTIONS` — exactly **77 boxes**, one per Shirakawa
  Z-page row with solution count `1+` and no prime marker
  (source-semantics audit: all four questions resolved, no blockers).
* Wires it into the `ZCatalogue` constructor
  (`published_solutions=set()` -> `published_solutions=PUBLISHED_SOLUTIONS`).
* Changes **nothing** else: `RAW_PRIMES`, `PRIMES`, impossible rules,
  `SEARCHED_NO_SOLUTION`, `ROW_FAMILIES`, `WIDTH_SPLITS`,
  `MINIMAL_ODD`/`MINIMAL_EVEN` and the class body are byte-identical.
* The **50 derived closures are NOT added manually** — they are re-derived
  automatically by the existing decomposition engine from the promoted
  evidence (list in §5).
* The **s:0 / family zero rows are deliberately excluded** (8 per-box
  rows incl. `3x23x50 s:0`, 10 family rows). They are a separate policy
  question per the evidence package (task 8) and are not part of this
  patch in any form.

## 2. Patch verification (pre-apply checks)

| check | result |
|---|---|
| additions | 77 |
| duplicate dimensions | 0 (must be 0) |
| non-canonical ordering | 0 (must be 0) |
| overlap with RAW_PRIMES | 0 |
| overlap with SEARCHED_NO_SOLUTION | 0 |
| inside impossible_reason rules | 0 |
| rows with provenance comment (1+ / year / Shirakawa) | 77/77 |
| **all pre-apply checks pass** | **YES** |

## 3. Exact proposed diff

```diff
--- a/catalogues/z_catalogue.py (current)
+++ b/catalogues/z_catalogue.py (proposed)
@@ -111,6 +111,111 @@
 }
 
 
+# Published solvable, non-prime boxes: Shirakawa Z page rows
+# carrying solution count '1+' with NO prime marker.
+# Source: https://puzzlewillbeplayed.com/Shirakawa/Z.html
+# (3D section, page last updated Feb 18, 2015).
+# Each row self-checks as pieces * 5 == a*b*c.
+# Proposed 2026-08-28; evidence:
+#   docs/frontier/z_piece/z_catalogue_promotion_patch.md
+#   docs/frontier/z_piece/z_promotion_evidence_package.md
+#   docs/frontier/z_piece/z_promotion_semantics_audit.md
+PUBLISHED_SOLUTIONS = {
+    # 3x23
+    Box(3, 23, 150),  # 1+ 2014 Shirakawa
+    Box(3, 23, 175),  # 1+ 2014 Shirakawa
+    Box(3, 23, 200),  # 1+ 2014 Shirakawa
+    Box(3, 23, 225),  # 1+ 2014 Shirakawa
+    Box(3, 23, 250),  # 1+ 2014 Shirakawa
+    Box(3, 23, 275),  # 1+ 2014 Shirakawa
+    # 3x24
+    Box(3, 24, 300),  # 1+ 2014 Shirakawa
+    # 3x25
+    Box(3, 25, 63),  # 1+ 2014 Shirakawa
+    Box(3, 25, 74),  # 1+ 2014 Shirakawa
+    # 4x12
+    Box(4, 12, 50),  # 1+ 2013 Shirakawa
+    Box(4, 12, 75),  # 1+ 2013 Shirakawa
+    # 4x13
+    Box(4, 13, 50),  # 1+ 2013 Shirakawa
+    Box(4, 13, 75),  # 1+ 2013 Shirakawa
+    # 4x15
+    Box(4, 15, 30),  # 1+ 2013 Shirakawa
+    Box(4, 15, 35),  # 1+ 2013 Shirakawa
+    Box(4, 15, 40),  # 1+ 2013 Shirakawa
+    Box(4, 15, 45),  # 1+ 2013 Shirakawa
+    Box(4, 15, 50),  # 1+ 2013 Shirakawa
+    Box(4, 15, 55),  # 1+ 2013 Shirakawa
+    # 4x20
+    Box(4, 20, 30),  # 1+ 2013 Shirakawa
+    Box(4, 20, 35),  # 1+ 2013 Shirakawa
+    # 4x24
+    Box(4, 24, 25),  # 1+ 2015 Shirakawa
+    # 4x25
+    Box(4, 25, 25),  # 1+ 2015 Shirakawa
+    Box(4, 25, 26),  # 1+ 2015 Shirakawa
+    # 5x10
+    Box(5, 10, 39),  # 1+ 2013 Shirakawa
+    Box(5, 10, 40),  # 1+ 2013 Shirakawa
+    Box(5, 10, 41),  # 1+ 2013 Shirakawa
+    Box(5, 10, 42),  # 1+ 2013 Shirakawa
+    Box(5, 10, 43),  # 1+ 2013 Shirakawa
+    Box(5, 10, 44),  # 1+ 2013 Shirakawa
+    Box(5, 10, 45),  # 1+ 2013 Shirakawa
+    Box(5, 10, 46),  # 1+ 2013 Shirakawa
+    Box(5, 10, 47),  # 1+ 2013 Shirakawa
+    Box(5, 10, 48),  # 1+ 2013 Shirakawa
+    Box(5, 10, 49),  # 1+ 2013 Shirakawa
+    Box(5, 10, 50),  # 1+ 2013 Shirakawa
+    Box(5, 10, 51),  # 1+ 2013 Shirakawa
+    Box(5, 10, 52),  # 1+ 2013 Shirakawa
+    Box(5, 10, 53),  # 1+ 2013 Shirakawa
+    Box(5, 10, 54),  # 1+ 2013 Shirakawa
+    Box(5, 10, 55),  # 1+ 2013 Shirakawa
+    Box(5, 10, 56),  # 1+ 2013 Shirakawa
+    Box(5, 10, 57),  # 1+ 2013 Shirakawa
+    Box(5, 10, 58),  # 1+ 2013 Shirakawa
+    Box(5, 10, 59),  # 1+ 2013 Shirakawa
+    Box(5, 10, 60),  # 1+ 2013 Shirakawa
+    Box(5, 10, 61),  # 1+ 2013 Shirakawa
+    Box(5, 10, 62),  # 1+ 2013 Shirakawa
+    Box(5, 10, 63),  # 1+ 2013 Shirakawa
+    Box(5, 10, 64),  # 1+ 2013 Shirakawa
+    Box(5, 10, 65),  # 1+ 2013 Shirakawa
+    Box(5, 10, 67),  # 1+ 2013 Shirakawa
+    Box(5, 10, 68),  # 1+ 2013 Shirakawa
+    Box(5, 10, 71),  # 1+ 2013 Shirakawa
+    # 5x11
+    Box(5, 11, 40),  # 1+ 2013 Shirakawa
+    Box(5, 11, 60),  # 1+ 2013 Shirakawa
+    Box(5, 11, 65),  # 1+ 2014 Shirakawa
+    Box(5, 11, 70),  # 1+ 2013 Shirakawa
+    Box(5, 11, 75),  # 1+ 2014 Shirakawa
+    Box(5, 11, 85),  # 1+ 2014 Shirakawa
+    Box(5, 11, 90),  # 1+ 2013 Shirakawa
+    Box(5, 11, 95),  # 1+ 2014 Shirakawa
+    # 5x12
+    Box(5, 12, 30),  # 1+ 2013 Shirakawa
+    Box(5, 12, 35),  # 1+ 2013 Shirakawa
+    # 5x13
+    Box(5, 13, 30),  # 1+ 2013 Shirakawa
+    Box(5, 13, 35),  # 1+ 2014 Shirakawa
+    Box(5, 13, 40),  # 1+ 2013 Shirakawa
+    Box(5, 13, 45),  # 1+ 2014 Shirakawa
+    # 5x14
+    Box(5, 14, 30),  # 1+ 2013 Shirakawa
+    Box(5, 14, 35),  # 1+ 2013 Shirakawa
+    # 5x15
+    Box(5, 15, 20),  # 1+ 2014 Shirakawa
+    Box(5, 15, 21),  # 1+ 2014 Shirakawa
+    Box(5, 15, 22),  # 1+ 2013 Shirakawa
+    Box(5, 15, 23),  # 1+ 2014 Shirakawa
+    Box(5, 15, 24),  # 1+ 2013 Shirakawa
+    Box(5, 15, 25),  # 1+ 2014 Shirakawa
+    # 5x16
+    Box(5, 16, 30),  # 1+ 2014 Shirakawa
+}
+
 class ZCatalogue(Catalogue):
     def impossible_reason(self, box: Box) -> str | None:
         a, b, c = box.a, box.b, box.c
@@ -172,5 +277,5 @@
     searched_no_solution=SEARCHED_NO_SOLUTION,
     row_families=ROW_FAMILIES,
     width_splits=WIDTH_SPLITS,
-    published_solutions=set(),
+    published_solutions=PUBLISHED_SOLUTIONS,
 )
```

## 4. Validation of the temporary patched catalogue

Method: the patched file was written to `/tmp`, imported, and installed
into the `CATALOGUES` registry under the name `Z` **in memory only**; the
repo's real audit and validation tools were then run unchanged.

* `tools/validate_catalogue.py` result: **PASSED**
* Audit D (published solutions) now reports the 77 promoted rows.
* Audit dim<=20 after patch: B (unproven composites) = 329, C (discovered composites) = 70.
* Source provenance: Shirakawa Z page 3D section, rows `1+` with no
  prime marker; years 2013/2014/2015; every row satisfies
  `pieces*5 == a*b*c` (77/77, enforced by the extraction parser).

<details><summary>full validate_catalogue output</summary>

```
Validating catalogue: Z
==================================================

CHECK 1: Prime boxes classify as Prime
----------------------------------------
PASSED: All 60 primes classify correctly

CHECK 2: Prime boxes are not impossible
----------------------------------------
PASSED: No primes marked impossible

CHECK 3: Row generator lengths are prime
----------------------------------------
PASSED: All 0 row generators classify as Prime

CHECK 3b: Family periods are valid
----------------------------------------
PASSED: All family periods are valid

CHECK 4: Canonical duplicates
----------------------------------------
Raw prime entries: 60
Unique prime boxes: 60

CHECK 4b: Orientation duplicates
----------------------------------------
PASSED: No orientation duplicates

CHECK 4c: RAW_PRIMES canonicality
----------------------------------------
PASSED: All RAW_PRIMES entries are canonical

CHECK 5: Published solutions consistency
----------------------------------------
PASSED: All 77 published solutions are consistent

CHECK 6: Redundant published solutions
----------------------------------------
None

==================================================
✓ Catalogue Z validation PASSED
```

</details>

<details><summary>full audit output (dim<=20, patched)</summary>

```
Auditing catalogue: Z
==================================================

NOTABLE BOXES
=============

Minimal odd RAW_PRIME: 5 x 9 x 15   (volume 675)
    verified: in RAW_PRIMES, parity ok, canonical order, classifies as PRIME, smallest in parity class

Minimal even RAW_PRIME: 6 x 10 x 10   (volume 600)
    verified: in RAW_PRIMES, parity ok, canonical order, classifies as PRIME, smallest in parity class

Family information:
------------------------------
Testing 724 boxes...

AUDIT A: Prime mismatches
------------------------------
Count: 0
No issues found

AUDIT B: Unproven composites
------------------------------
Count: 329
  4x11x15 -> Unknown
  4x11x20 -> Unknown
  4x12x15 -> Unknown
  4x12x20 -> Unknown
  4x13x15 -> Unknown
  4x13x20 -> Unknown
  4x14x15 -> Unknown
  4x14x20 -> Unknown
  4x15x15 -> Unknown
  4x15x16 -> Unknown
  4x15x17 -> Unknown
  4x15x18 -> Unknown
  4x15x19 -> Unknown
  4x15x20 -> Unknown
  4x16x20 -> Unknown
  4x17x20 -> Unknown
  4x18x20 -> Unknown
  4x19x20 -> Unknown
  5x8x8 -> Unknown
  5x8x9 -> Unknown
  5x8x11 -> Unknown
  5x8x12 -> Unknown
  5x8x13 -> Unknown
  5x8x14 -> Unknown
  5x8x16 -> Unknown
  5x8x17 -> Unknown
  5x8x18 -> Unknown
  5x8x19 -> Unknown
  5x9x9 -> Unknown
  5x9x11 -> Unknown
  5x9x12 -> Unknown
  5x9x13 -> Unknown
  5x9x14 -> Unknown
  5x9x16 -> Unknown
  5x9x17 -> Unknown
  5x9x18 -> Unknown
  5x9x19 -> Unknown
  5x10x10 -> Unknown
  5x10x11 -> Unknown
  5x10x12 -> Unknown
  5x10x13 -> Unknown
  5x10x14 -> Unknown
  5x10x15 -> Unknown
  5x10x16 -> Unknown
  5x10x17 -> Unknown
  5x10x18 -> Unknown
  5x10x19 -> Unknown
  5x10x20 -> Unknown
  5x11x11 -> Unknown
  5x11x12 -> Unknown
  5x11x13 -> Unknown
  5x11x14 -> Unknown
  5x11x15 -> Unknown
  5x11x16 -> Unknown
  5x11x17 -> Unknown
  5x11x18 -> Unknown
  5x11x19 -> Unknown
  5x11x20 -> Unknown
  5x12x12 -> Unknown
  5x12x13 -> Unknown
  5x12x14 -> Unknown
  5x12x15 -> Unknown
  5x12x16 -> Unknown
  5x12x17 -> Unknown
  5x12x18 -> Unknown
  5x12x19 -> Unknown
  5x13x13 -> Unknown
  5x13x14 -> Unknown
  5x13x15 -> Unknown
  5x13x16 -> Unknown
  5x13x17 -> Unknown
  5x13x18 -> Unknown
  5x13x19 -> Unknown
  5x13x20 -> Unknown
  5x14x14 -> Unknown
  5x14x15 -> Unknown
  5x14x16 -> Unknown
  5x14x17 -> Unknown
  5x14x18 -> Unknown
  5x14x19 -> Unknown
  5x15x15 -> Unknown
  5x15x16 -> Unknown
  5x16x16 -> Unknown
  5x16x17 -> Unknown
  5x16x18 -> Unknown
  5x16x19 -> Unknown
  5x17x17 -> Unknown
  5x17x18 -> Unknown
  5x17x19 -> Unknown
  5x18x18 -> Unknown
  5x18x19 -> Unknown
  5x18x20 -> Unknown
  5x19x19 -> Unknown
  5x19x20 -> Unknown
  6x6x10 -> Unknown
  6x6x15 -> Unknown
  6x6x20 -> Unknown
  6x7x10 -> Unknown
  6x7x15 -> Unknown
  6x7x20 -> Unknown
  6x8x10 -> Unknown
  6x8x15 -> Unknown
  6x8x20 -> Unknown
  6x9x10 -> Unknown
  6x9x15 -> Unknown
  6x9x20 -> Unknown
  6x10x11 -> Unknown
  6x10x12 -> Unknown
  6x10x13 -> Unknown
  6x10x14 -> Unknown
  6x10x16 -> Unknown
  6x10x17 -> Unknown
  6x10x18 -> Unknown
  6x10x19 -> Unknown
  6x11x15 -> Unknown
  6x11x20 -> Unknown
  6x12x15 -> Unknown
  6x12x20 -> Unknown
  6x13x15 -> Unknown
  6x13x20 -> Unknown
  6x14x15 -> Unknown
  6x14x20 -> Unknown
  6x15x16 -> Unknown
  6x15x17 -> Unknown
  6x15x18 -> Unknown
  6x15x19 -> Unknown
  6x16x20 -> Unknown
  6x17x20 -> Unknown
  6x18x20 -> Unknown
  6x19x20 -> Unknown
  7x8x10 -> Unknown
  7x8x15 -> Unknown
  7x8x20 -> Unknown
  7x9x10 -> Unknown
  7x9x15 -> Unknown
  7x9x20 -> Unknown
  7x10x11 -> Unknown
  7x10x12 -> Unknown
  7x10x13 -> Unknown
  7x10x14 -> Unknown
  7x10x16 -> Unknown
  7x10x17 -> Unknown
  7x10x18 -> Unknown
  7x10x19 -> Unknown
  7x11x15 -> Unknown
  7x11x20 -> Unknown
  7x12x15 -> Unknown
  7x12x20 -> Unknown
  7x13x15 -> Unknown
  7x13x20 -> Unknown
  7x14x15 -> Unknown
  7x14x20 -> Unknown
  7x15x15 -> Unknown
  7x15x16 -> Unknown
  7x15x17 -> Unknown
  7x15x18 -> Unknown
  7x15x19 -> Unknown
  7x16x20 -> Unknown
  7x17x20 -> Unknown
  7x18x20 -> Unknown
  7x19x20 -> Unknown
  8x8x10 -> Unknown
  8x8x15 -> Unknown
  8x8x20 -> Unknown
  8x9x10 -> Unknown
  8x9x15 -> Unknown
  8x9x20 -> Unknown
  8x10x11 -> Unknown
  8x10x12 -> Unknown
  8x10x13 -> Unknown
  8x10x14 -> Unknown
  8x10x16 -> Unknown
  8x10x17 -> Unknown
  8x10x18 -> Unknown
  8x10x19 -> Unknown
  8x11x15 -> Unknown
  8x11x20 -> Unknown
  8x12x15 -> Unknown
  8x12x20 -> Unknown
  8x13x15 -> Unknown
  8x13x20 -> Unknown
  8x14x15 -> Unknown
  8x14x20 -> Unknown
  8x15x16 -> Unknown
  8x15x17 -> Unknown
  8x15x18 -> Unknown
  8x15x19 -> Unknown
  8x16x20 -> Unknown
  8x17x20 -> Unknown
  8x18x20 -> Unknown
  8x19x20 -> Unknown
  9x9x10 -> Unknown
  9x9x15 -> Unknown
  9x9x20 -> Unknown
  9x10x11 -> Unknown
  9x10x12 -> Unknown
  9x10x13 -> Unknown
  9x10x14 -> Unknown
  9x10x16 -> Unknown
  9x10x17 -> Unknown
  9x10x18 -> Unknown
  9x10x19 -> Unknown
  9x11x15 -> Unknown
  9x11x20 -> Unknown
  9x12x15 -> Unknown
  9x12x20 -> Unknown
  9x13x15 -> Unknown
  9x13x20 -> Unknown
  9x14x15 -> Unknown
  9x14x20 -> Unknown
  9x15x16 -> Unknown
  9x15x17 -> Unknown
  9x15x18 -> Unknown
  9x15x19 -> Unknown
  9x16x20 -> Unknown
  9x17x20 -> Unknown
  9x18x20 -> Unknown
  9x19x20 -> Unknown
  10x11x11 -> Unknown
  10x11x12 -> Unknown
  10x11x13 -> Unknown
  10x11x14 -> Unknown
  10x11x15 -> Unknown
  10x11x16 -> Unknown
  10x11x17 -> Unknown
  10x11x18 -> Unknown
  10x11x19 -> Unknown
  10x12x12 -> Unknown
  10x12x13 -> Unknown
  10x12x14 -> Unknown
  10x12x16 -> Unknown
  10x12x17 -> Unknown
  10x12x18 -> Unknown
  10x12x19 -> Unknown
  10x13x13 -> Unknown
  10x13x14 -> Unknown
  10x13x16 -> Unknown
  10x13x17 -> Unknown
  10x13x18 -> Unknown
  10x13x19 -> Unknown
  10x14x14 -> Unknown
  10x14x16 -> Unknown
  10x14x17 -> Unknown
  10x14x18 -> Unknown
  10x14x19 -> Unknown
  10x16x16 -> Unknown
  10x16x17 -> Unknown
  10x16x18 -> Unknown
  10x16x19 -> Unknown
  10x17x17 -> Unknown
  10x17x18 -> Unknown
  10x17x19 -> Unknown
  10x18x18 -> Unknown
  10x18x19 -> Unknown
  10x19x19 -> Unknown
  11x11x15 -> Unknown
  11x11x20 -> Unknown
  11x12x15 -> Unknown
  11x12x20 -> Unknown
  11x13x15 -> Unknown
  11x13x20 -> Unknown
  11x14x15 -> Unknown
  11x14x20 -> Unknown
  11x15x15 -> Unknown
  11x15x16 -> Unknown
  11x15x17 -> Unknown
  11x15x18 -> Unknown
  11x15x19 -> Unknown
  11x16x20 -> Unknown
  11x17x20 -> Unknown
  11x18x20 -> Unknown
  11x19x20 -> Unknown
  12x12x15 -> Unknown
  12x12x20 -> Unknown
  12x13x15 -> Unknown
  12x13x20 -> Unknown
  12x14x15 -> Unknown
  12x14x20 -> Unknown
  12x15x16 -> Unknown
  12x15x17 -> Unknown
  12x15x18 -> Unknown
  12x15x19 -> Unknown
  12x16x20 -> Unknown
  12x17x20 -> Unknown
  12x18x20 -> Unknown
  12x19x20 -> Unknown
  13x13x15 -> Unknown
  13x13x20 -> Unknown
  13x14x15 -> Unknown
  13x14x20 -> Unknown
  13x15x15 -> Unknown
  13x15x16 -> Unknown
  13x15x17 -> Unknown
  13x15x18 -> Unknown
  13x15x19 -> Unknown
  13x16x20 -> Unknown
  13x17x20 -> Unknown
  13x18x20 -> Unknown
  13x19x20 -> Unknown
  14x14x15 -> Unknown
  14x14x20 -> Unknown
  14x15x16 -> Unknown
  14x15x17 -> Unknown
  14x15x18 -> Unknown
  14x15x19 -> Unknown
  14x16x20 -> Unknown
  14x17x20 -> Unknown
  14x18x20 -> Unknown
  14x19x20 -> Unknown
  15x16x16 -> Unknown
  15x16x17 -> Unknown
  15x16x18 -> Unknown
  15x16x19 -> Unknown
  15x17x17 -> Unknown
  15x17x18 -> Unknown
  15x17x19 -> Unknown
  15x18x18 -> Unknown
  15x18x19 -> Unknown
  15x19x19 -> Unknown
  16x16x20 -> Unknown
  16x17x20 -> Unknown
  16x18x20 -> Unknown
  16x19x20 -> Unknown
  17x17x20 -> Unknown
  17x18x20 -> Unknown
  17x19x20 -> Unknown
  18x18x20 -> Unknown
  18x19x20 -> Unknown
  19x19x20 -> Unknown

AUDIT C: Discovered composites
------------------------------
Count: 70
  5x15x18 -> Slab
  5x16x20 -> Breadth
  5x20x20 -> Slab
  6x10x20 -> Slab
  6x15x20 -> Slab
  6x20x20 -> Slab
  7x10x20 -> Slab
  7x15x20 -> Slab
  7x20x20 -> Slab
  8x10x20 -> Slab
  8x15x20 -> Slab
  8x20x20 -> Slab
  9x10x15 -> Breadth
  9x10x20 -> Slab
  9x15x15 -> Slab
  9x15x20 -> Slab
  9x20x20 -> Slab
  10x10x12 -> Slab
  10x10x13 -> Slab
  10x10x14 -> Slab
  10x10x15 -> Slab
  10x10x16 -> Slab
  10x10x17 -> Slab
  10x10x18 -> Slab
  10x10x19 -> Slab
  10x10x20 -> Slab
  10x11x20 -> Slab
  10x12x15 -> Breadth
  10x12x20 -> Slab
  10x13x15 -> Breadth
  10x13x20 -> Slab
  10x14x15 -> Breadth
  10x14x20 -> Slab
  10x15x15 -> Slab
  10x15x16 -> Slab
  10x15x17 -> Slab
  10x15x18 -> Slab
  10x15x19 -> Slab
  10x15x20 -> Slab
  10x16x20 -> Slab
  10x17x20 -> Slab
  10x18x20 -> Slab
  10x19x20 -> Slab
  10x20x20 -> Slab
  11x15x20 -> Width
  11x20x20 -> Slab
  12x15x15 -> Width
  12x15x20 -> Slab
  12x20x20 -> Slab
  13x15x20 -> Slab
  13x20x20 -> Slab
  14x15x15 -> Width
  14x15x20 -> Slab
  14x20x20 -> Slab
  15x15x15 -> Slab
  15x15x16 -> Slab
  15x15x17 -> Slab
  15x15x18 -> Slab
  15x15x19 -> Slab
  15x15x20 -> Slab
  15x16x20 -> Slab
  15x17x20 -> Slab
  15x18x20 -> Slab
  15x19x20 -> Slab
  15x20x20 -> Slab
  16x20x20 -> Slab
  17x20x20 -> Slab
  18x20x20 -> Slab
  19x20x20 -> Slab
  20x20x20 -> Slab

AUDIT D: Published solutions
------------------------------
Count: 77
  3x23x250
  5x10x45
  3x23x225
  4x12x75
  5x15x25
  4x12x50
  4x15x30
  5x10x59
  5x10x68
  4x25x25
  3x23x275
  5x11x75
  5x10x61
  5x15x20
  5x10x54
  5x10x63
  5x11x95
  5x11x40
  5x15x22
  5x16x30
  4x15x55
  5x11x70
  5x12x35
  5x10x47
  5x10x56
  5x10x65
  5x15x24
  5x14x35
  4x20x35
  5x10x40
  5x10x49
  5x13x45
  5x10x58
  5x11x90
  5x10x67
  3x24x300
  4x15x50
  5x11x65
  5x12x30
  5x10x42
  4x24x25
  5x10x51
  5x10x60
  5x14x30
  3x25x63
  4x20x30
  5x10x44
  5x13x40
  5x10x53
  5x11x85
  5x10x62
  5x15x21
  5x10x71
  4x15x45
  3x25x74
  5x11x60
  3x23x150
  4x13x75
  5x10x46
  5x10x55
  5x10x64
  5x15x23
  4x13x50
  5x10x39
  5x13x35
  5x10x48
  5x10x57
  4x15x40
  3x23x200
  4x25x26
  5x10x41
  5x10x50
  3x23x175
  5x13x30
  5x10x43
  5x10x52
  4x15x35

==================================================
Audit complete for Z
```

</details>

## 5. Impact (dims <= 60, full canonical scan)

| metric | before | after patch | delta |
|---|---|---|---|
| Unknown boxes | 10580 | 10478 | **-102** |
| closed constructions (non-prime, non-impossible) | 5659 | 5761 | +102 |
| Audit B (unproven composites, dim<=20) | 331 | 329 | -2 |
| Audit C (discovered composites, dim<=20) | 69 | 70 | +1 |

Classification transitions observed: {('Unknown', 'PublishedSolution'): 52, ('Unknown', 'Slab'): 43, ('Breadth', 'Slab'): 23, ('Unknown', 'Breadth'): 5, ('Breadth', 'Width'): 3, ('Unknown', 'Width'): 2, ('Width', 'Slab'): 3}  
Benign proof re-shapes among already-closed boxes: {('Breadth', 'Slab'): 23, ('Breadth', 'Width'): 3, ('Width', 'Slab'): 3} (total 29) — the box stays closed; only the
first-found closing branch changes once the evidence set grows.
Unknown -> closed promotions: 102 (expected 102).  
Boxes entering/leaving Impossible: **0** (must be 0).  
**Regressions (closed -> open or similar): 0**

Newly closed boxes: 102 total = 52 direct published rows (in-window) + **50 derived automatically**.

### The derived closures (NOT added manually — engine derives them)

* 5x15x29  [Slab]
* 5x15x30  [Slab]
* 5x20x23  [Slab]
* 5x15x31  [Slab]
* 5x15x32  [Slab]
* 5x15x33  [Slab]
* 5x20x27  [Slab]
* 5x15x39  [Slab]
* 5x15x40  [Slab]
* 5x15x41  [Slab]
* 5x15x42  [Slab]
* 5x21x30  [Slab]
* 5x12x55  [Slab]
* 5x22x30  [Slab]
* 11x15x20  [Width]
* 5x23x30  [Slab]
* 5x20x35  [Slab]
* 5x13x55  [Slab]
* 4x15x60  [Slab]
* 4x30x30  [Slab]
* 5x15x48  [Slab]
* 5x24x30  [Slab]
* 5x15x49  [Slab]
* 5x21x35  [Breadth]
* 5x15x50  [Slab]
* 5x19x40  [Breadth]
* 5x14x55  [Slab]
* 5x22x35  [Slab]
* 5x13x60  [Slab]
* 4x30x35  [Slab]
* 5x15x58  [Slab]
* 5x15x59  [Slab]
* 5x30x30  [Slab]
* 4x23x50  [Breadth]
* 5x30x31  [Slab]
* 5x19x50  [Breadth]
* 4x30x40  [Slab]
* 5x30x32  [Slab]
* 4x35x35  [Slab]
* 10x11x45  [Breadth]
* 11x15x30  [Width]
* 5x29x35  [Slab]
* 5x19x55  [Slab]
* 4x30x45  [Slab]
* 4x35x40  [Slab]
* 5x21x55  [Slab]
* 5x22x55  [Slab]
* 5x30x41  [Slab]
* 4x35x45  [Slab]
* 11x15x40  [Slab]

Direct published rows inside the window (closed as `PublishedSolution`):

* `5x15x20`, `5x15x21`, `5x15x22`, `5x15x23`, `4x15x30`, `5x12x30`, `5x15x24`, `5x15x25`, `5x10x39`, `5x13x30`, `5x10x40`, `5x10x41`, `4x15x35`, `5x10x42`, `5x12x35`, `5x14x30`, `5x10x43`, `5x10x44`, `5x11x40`, `5x10x45`, `5x13x35`, `5x10x46`, `5x10x47`, `4x12x50`, `4x15x40`, `4x20x30`, `4x24x25`, `5x10x48`, `5x16x30`, `5x10x49`, `5x14x35`, `4x25x25`, `5x10x50`, `5x10x51`, `4x13x50`, `4x25x26`, `5x10x52`, `5x13x40`, `5x10x53`, `4x15x45`, `5x10x54`, `5x10x55`, `4x20x35`, `5x10x56`, `5x10x57`, `5x10x58`, `5x13x45`, `5x10x59`, `4x15x50`, `5x10x60`, `4x15x55`, `5x11x60`

Outside the 60-window, further cascades also become derivable (e.g.
`5x10x72 = PRIME 5x10x33 + PUB 5x10x39`); they are outside the measured
window and require no action.

## 6. Review checklist for the approver

1. §2 table all-green (duplicates / conflicts / ordering / provenance).
2. §3 diff touches only the `PUBLISHED_SOLUTIONS` block and the
   constructor argument.
3. §4 validation PASSED; §5 shows only `Unknown -> closed` transitions.
4. s:0 / family rows absent from the diff (deliberate; separate policy).
5. On approval: apply §3 verbatim to `catalogues/z_catalogue.py`, then
   run `tools/validate_catalogue.py Z` and
   `tools/audit_catalogue.py Z --max-dim 20`.

## 7. Provenance

* Source rows: package §1 table (77 rows, verbatim page strings).
* Semantics: `z_promotion_semantics_audit.md` (Q1-Q4 resolved).
* Replay: package §2 (127/127 trees close and validate).
* This artifact regenerable via `tools/frontier/z_piece/build_promotion_patch.py`.
