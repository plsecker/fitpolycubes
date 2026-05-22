/*
 * place_terminate.c
 *
 * Code generation for function 'place_terminate'
 *
 * C source code generated on: Fri Dec 27 17:33:31 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "place_terminate.h"

/* Function Definitions */
void place_atexit(void)
{
  emlrtCreateRootTLS(&emlrtRootTLSGlobal, &emlrtContextGlobal, NULL, 1);
  emlrtEnterRtStackR2012b(emlrtRootTLSGlobal);
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

void place_terminate(void)
{
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

/* End of code generation (place_terminate.c) */
