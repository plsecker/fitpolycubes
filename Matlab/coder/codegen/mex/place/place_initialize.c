/*
 * place_initialize.c
 *
 * Code generation for function 'place_initialize'
 *
 * C source code generated on: Fri Dec 27 17:33:31 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "place_initialize.h"
#include "place_data.h"

/* Function Declarations */
static void place_once(void);

/* Function Definitions */
static void place_once(void)
{
  static const real_T dv0[216] = { 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
    0.0, 0.0, 1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
    -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
    1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -1.0,
    0.0, -1.0, 0.0, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0,
    -1.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0, 0.0, -1.0,
    0.0, -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0, 1.0,
    0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, -1.0,
    0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, -1.0, 0.0,
    0.0, 0.0, -1.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0,
    0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0
  };

  static const real_T dv1[75] = { 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0,
    2.0, 0.0, 1.0, 3.0, 0.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
    1.0, 0.0, 1.0, 2.0, 0.0, 1.0, -2.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 1.0, 0.0, 1.0, -2.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0.0,
    -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -3.0, 0.0, -1.0, -2.0, 0.0, -1.0, -1.0,
    0.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0 };

  memcpy(&RM[0], &dv0[0], 216U * sizeof(real_T));
  memcpy(&P[0], &dv1[0], 75U * sizeof(real_T));
  RM_dirty = 0U;
  P_dirty = 0U;
}

void place_initialize(emlrtContext *aContext)
{
  emlrtBreakCheckR2012bFlagVar = emlrtGetBreakCheckFlagAddressR2012b();
  emlrtCreateRootTLS(&emlrtRootTLSGlobal, aContext, NULL, 1);
  emlrtClearAllocCountR2012b(emlrtRootTLSGlobal, FALSE, 0U, 0);
  emlrtEnterRtStackR2012b(emlrtRootTLSGlobal);
  if (emlrtFirstTimeR2012b(emlrtRootTLSGlobal)) {
    place_once();
  }
}

/* End of code generation (place_initialize.c) */
