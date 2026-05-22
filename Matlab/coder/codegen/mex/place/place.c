/*
 * place.c
 *
 * Code generation for function 'place'
 *
 * C source code generated on: Fri Dec 27 17:33:31 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "place_data.h"

/* Function Definitions */
void place(const boolean_T box[125], real_T cube, real_T transno, real_T rot,
           boolean_T newbox[125], real_T *nextcube)
{
  real_T r;
  real_T b_r;
  real_T a[3];
  real_T cubeoffset[15];
  int32_T ib;
  int32_T jtilecol;
  int32_T ia;
  int32_T k;
  real_T pr[15];
  real_T boxidx[5];
  boolean_T y;
  boolean_T exitg2;
  boolean_T exitg1;

  /*  Place a piece into target cube with valid trans and valid rotation */
  /*  into a known good box */
  /*  only deal with this translation */
  /*  find 1's based coordinate of empty cube */
  /*  fast version for 3d box of side length len */
  r = muDoubleScalarRem(cube - 1.0, 25.0);
  b_r = muDoubleScalarRem((muDoubleScalarRem(cube - 1.0, 25.0) + 1.0) - 1.0, 5.0);
  a[0] = (b_r + 1.0) - 1.0;
  a[1] = (((r + 1.0) - (b_r + 1.0)) / 5.0 + 1.0) - 1.0;
  a[2] = ((cube - (r + 1.0)) / 25.0 + 1.0) - 1.0;
  ib = 0;
  for (jtilecol = 0; jtilecol < 5; jtilecol++) {
    ia = 0;
    for (k = 0; k < 3; k++) {
      cubeoffset[ib] = a[ia];
      ia++;
      ib++;
    }
  }

  /*  find zero-based translation of cube */
  /*  place first rotation */
  for (ib = 0; ib < 3; ib++) {
    for (jtilecol = 0; jtilecol < 5; jtilecol++) {
      r = 0.0;
      for (k = 0; k < 3; k++) {
        r += RM[(ib + 3 * k) + 9 * ((int32_T)rot - 1)] * P[(k + 3 * jtilecol) +
          15 * ((int32_T)transno - 1)];
      }

      pr[ib + 3 * jtilecol] = cubeoffset[ib + 3 * jtilecol] + r;
    }
  }

  memcpy(&newbox[0], &box[0], 125U * sizeof(boolean_T));

  /*  Check if piece will clash if inserted into box, insert if it does */
  /*  piece is zero-based coords */
  /*  convert p's cube coordinates to linear indicies of box */
  /* boxidx=sub2ind(size(box),p(1,:)+1,p(2,:)+1,p(3,:)+1); */
  /* blen = length(box); */
  /* boxidx = blen^2*p(3,:) + blen*p(2,:) + p(1,:)+1;   % fast version */
  for (ib = 0; ib < 5; ib++) {
    boxidx[ib] = ((25.0 * pr[2 + 3 * ib] + 5.0 * pr[1 + 3 * ib]) + pr[3 * ib]) +
      1.0;
  }

  /*  faster version */
  y = FALSE;
  k = 0;
  exitg2 = FALSE;
  while ((exitg2 == FALSE) && (k < 5)) {
    if (!(box[(int32_T)boxidx[k] - 1] == 0)) {
      y = TRUE;
      exitg2 = TRUE;
    } else {
      k++;
    }
  }

  if (y) {
  } else {
    /*  Insert piece array into box and return true */
    for (ib = 0; ib < 5; ib++) {
      newbox[(int32_T)boxidx[ib] - 1] = TRUE;
    }
  }

  /*  find next free cube in linear space */
  /*  turn box into a linear array with ones at filled locs */
  ib = 1;
  jtilecol = 0;
  exitg1 = FALSE;
  while ((exitg1 == FALSE) && (jtilecol < 125)) {
    ib = jtilecol + 1;

    /*  scan through empty cubes in turn */
    if (!newbox[jtilecol]) {
      /* disp(nextempty) */
      exitg1 = TRUE;
    } else {
      jtilecol++;
      emlrtBreakCheckFastR2012b(emlrtBreakCheckR2012bFlagVar, emlrtRootTLSGlobal);
    }
  }

  *nextcube = ib;

  /*  record this target cube */
}

/* End of code generation (place.c) */
