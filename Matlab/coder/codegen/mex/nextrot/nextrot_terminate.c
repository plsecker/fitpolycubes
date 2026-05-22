/*
 * nextrot_terminate.c
 *
 * Code generation for function 'nextrot_terminate'
 *
 * C source code generated on: Fri Dec 27 11:55:29 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "nextrot.h"
#include "nextrot_terminate.h"

/* Function Definitions */
void nextrot_atexit(void)
{
  emlrtCreateRootTLS(&emlrtRootTLSGlobal, &emlrtContextGlobal, NULL, 1);
  emlrtEnterRtStackR2012b(emlrtRootTLSGlobal);
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

void nextrot_terminate(void)
{
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

/* End of code generation (nextrot_terminate.c) */
