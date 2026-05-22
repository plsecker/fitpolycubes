/*
 * nextrot.c
 *
 * Code generation for function 'nextrot'
 *
 * C source code generated on: Fri Dec 27 11:55:29 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "nextrot.h"
#include "eml_sort.h"
#include "nextrot_data.h"

/* Function Definitions */
void nextrot(real_T cube, real_T transno, real_T nextrotvec_data[24], int32_T
             nextrotvec_size[2])
{
  real_T nextrotsum;
  int32_T k;
  real_T dv1[24];
  int32_T iidx[24];
  real_T unusedU0[24];
  int32_T loop_ub;

  /*  Return next rotation vector for a cube and translation */
  /* thiscubesrots = boxcuberots(cube,:,transno); */
  /* nextrotvec = find(thiscubesrots);       % get all rots for this cube/translation */
  nextrotsum = boxcuberots[((int32_T)cube + 3000 * ((int32_T)transno - 1)) - 1];
  for (k = 0; k < 23; k++) {
    nextrotsum += boxcuberots[(((int32_T)cube + 125 * (k + 1)) + 3000 *
      ((int32_T)transno - 1)) - 1];
  }

  /*  get number of rots for this cube/translation */
  for (k = 0; k < 24; k++) {
    dv1[k] = boxcubelevels[(((int32_T)cube + 125 * k) + 3000 * ((int32_T)transno
      - 1)) - 1];
  }

  eml_sort(dv1, unusedU0, iidx);
  if (1.0 > nextrotsum) {
    loop_ub = 0;
  } else {
    loop_ub = (int32_T)nextrotsum;
  }

  nextrotvec_size[0] = 1;
  nextrotvec_size[1] = loop_ub;
  for (k = 0; k < loop_ub; k++) {
    nextrotvec_data[k] = iidx[k];
  }
}

/* End of code generation (nextrot.c) */
