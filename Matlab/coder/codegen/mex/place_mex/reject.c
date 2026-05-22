/*
 * reject.c
 *
 * Code generation for function 'reject'
 *
 * C source code generated on: Thu Dec 26 18:34:40 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "reject.h"
#include "place_mex_data.h"

/* Function Definitions */
boolean_T reject(const boolean_T box[125], real_T cube, real_T transno, real_T
                 rotvec)
{
  boolean_T status;
  real_T dv3[3];
  real_T dv4[15];
  real_T dv5[15];
  int32_T k;
  int32_T i0;
  int32_T i1;
  real_T boxidx[5];
  real_T pr[15];
  boolean_T exitg1;

  /*  Return status = TRUE if this candidate piece can't be filled */
  /*  only deal with this translation */
  /*  find 1's based coordinate of empty cube */
  /* [xi,yi,zi] = ind2sub3d(5,cube); */
  /*  LUT version */
  /* cubeoffset = repmat([xi-1;yi-1;zi-1],1,length(piece)); % find zero-based translation of piece */
  /* cubeoffset = repmat(a',1,length(piece)); % find zero-based translation of piece */
  /*  quick version */
  /*  check first rotation */
  for (k = 0; k < 3; k++) {
    dv3[k] = IND2SUBLUT[((int32_T)cube + 125 * k) - 1] - 1.0;
    for (i0 = 0; i0 < 5; i0++) {
      dv5[k + 3 * i0] = dv3[k];
      dv4[k + 3 * i0] = 0.0;
      for (i1 = 0; i1 < 3; i1++) {
        dv4[k + 3 * i0] += RM[(k + 3 * i1) + 9 * ((int32_T)rotvec - 1)] * P[(i1
          + 3 * i0) + 15 * ((int32_T)transno - 1)];
      }
    }
  }

  for (k = 0; k < 5; k++) {
    for (i0 = 0; i0 < 3; i0++) {
      pr[i0 + 3 * k] = dv5[i0 + 3 * k] + dv4[i0 + 3 * k];
    }

    /* % this is vital parts of boxit.m */
    boxidx[k] = ((25.0 * pr[2 + 3 * k] + 5.0 * pr[1 + 3 * k]) + pr[3 * k]) + 1.0;
  }

  /*  faster version */
  status = FALSE;
  k = 0;
  exitg1 = FALSE;
  while ((exitg1 == FALSE) && (k < 5)) {
    if (!(box[(int32_T)boxidx[k] - 1] == 0)) {
      status = TRUE;
      exitg1 = TRUE;
    } else {
      k++;
    }
  }

  return status;
}

/* End of code generation (reject.c) */
