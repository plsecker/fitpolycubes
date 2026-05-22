/*
 * reject_terminate.c
 *
 * Code generation for function 'reject_terminate'
 *
 * C source code generated on: Thu Dec 26 18:41:51 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "reject.h"
#include "reject_terminate.h"

/* Function Definitions */
void reject_atexit(void)
{
  emlrtCreateRootTLS(&emlrtRootTLSGlobal, &emlrtContextGlobal, NULL, 1);
  emlrtEnterRtStackR2012b(emlrtRootTLSGlobal);
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

void reject_terminate(void)
{
  emlrtLeaveRtStackR2012b(emlrtRootTLSGlobal);
  emlrtDestroyRootTLS(&emlrtRootTLSGlobal);
}

/* End of code generation (reject_terminate.c) */
