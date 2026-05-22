/*
 * place_mex_terminate.c
 *
 * Code generation for function 'place_mex_terminate'
 *
 * C source code generated on: Thu Dec 26 18:34:40 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "reject.h"
#include "place_mex_terminate.h"

/* Function Definitions */
void place_mex_atexit(void)
{
  emlrtCreateRootTLS(&emlrtRootTLSGlobal, &emlrtContextGlobal, NULL, 1);
  emlrtEnterRtStackR2012b(emlrtRootTLSGlobal);
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

void place_mex_terminate(void)
{
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

/* End of code generation (place_mex_terminate.c) */
