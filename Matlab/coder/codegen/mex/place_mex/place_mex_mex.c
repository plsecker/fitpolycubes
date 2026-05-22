/*
 * place_mex_mex.c
 *
 * Code generation for function 'place'
 *
 * C source code generated on: Thu Dec 26 18:34:40 2013
 *
 */

/* Include files */
#include "mex.h"
#include "place_mex_api.h"
#include "place_mex_initialize.h"
#include "place_mex_terminate.h"

/* Function Declarations */
static void place_mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);
static void reject_mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]);

/* Variable Definitions */
emlrtContext emlrtContextGlobal = { true, false, EMLRT_VERSION_INFO, NULL, "place_mex", NULL, false, {2045744189U,2170104910U,2743257031U,4284093946U}, NULL };
void *emlrtRootTLSGlobal = NULL;
emlrtEntryPoint emlrtEntryPoints[2] = {
  { "place", place_mexFunction },
  { "reject", reject_mexFunction },
};

/* Function Definitions */
static void place_mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
  mxArray *outputs[2];
  mxArray *inputs[4];
  int n = 0;
  int nOutputs = (nlhs < 1 ? 1 : nlhs);
  int nInputs = nrhs;
  /* Module initialization. */
  place_mex_initialize(&emlrtContextGlobal);
  /* Check for proper number of arguments. */
  if (nrhs != 4) {
    emlrtErrMsgIdAndTxt(emlrtRootTLSGlobal, "EMLRT:runTime:WrongNumberOfInputs", 5, mxINT32_CLASS, 4, mxCHAR_CLASS, 5, "place");
  } else if (nlhs > 2) {
    emlrtErrMsgIdAndTxt(emlrtRootTLSGlobal, "EMLRT:runTime:TooManyOutputArguments", 3, mxCHAR_CLASS, 5, "place");
  }
  /* Temporary copy for mex inputs. */
  for (n = 0; n < nInputs; ++n) {
    inputs[n] = (mxArray *)prhs[n];
  }
  /* Call the function. */
  place_api((const mxArray**)inputs, (const mxArray**)outputs);
  /* Copy over outputs to the caller. */
  for (n = 0; n < nOutputs; ++n) {
    plhs[n] = emlrtReturnArrayR2009a(outputs[n]);
  }
  /* Module finalization. */
  place_mex_terminate();
}
static void reject_mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
  mxArray *outputs[1];
  mxArray *inputs[4];
  int n = 0;
  int nOutputs = (nlhs < 1 ? 1 : nlhs);
  int nInputs = nrhs;
  /* Module initialization. */
  place_mex_initialize(&emlrtContextGlobal);
  /* Check for proper number of arguments. */
  if (nrhs != 4) {
    emlrtErrMsgIdAndTxt(emlrtRootTLSGlobal, "EMLRT:runTime:WrongNumberOfInputs", 5, mxINT32_CLASS, 4, mxCHAR_CLASS, 6, "reject");
  } else if (nlhs > 1) {
    emlrtErrMsgIdAndTxt(emlrtRootTLSGlobal, "EMLRT:runTime:TooManyOutputArguments", 3, mxCHAR_CLASS, 6, "reject");
  }
  /* Temporary copy for mex inputs. */
  for (n = 0; n < nInputs; ++n) {
    inputs[n] = (mxArray *)prhs[n];
  }
  /* Call the function. */
  reject_api((const mxArray**)inputs, (const mxArray**)outputs);
  /* Copy over outputs to the caller. */
  for (n = 0; n < nOutputs; ++n) {
    plhs[n] = emlrtReturnArrayR2009a(outputs[n]);
  }
  /* Module finalization. */
  place_mex_terminate();
}

void place_mex_atexit_wrapper(void)
{
   place_mex_atexit();
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
{
  emlrtMexFunction method;
  method = emlrtGetMethod(nrhs, prhs, emlrtEntryPoints, 2);
  /* Initialize the memory manager. */
  mexAtExit(place_mex_atexit_wrapper);
  /* Dispatch the entry-point. */
  method(nlhs, plhs, nrhs-1, prhs+1);
}
/* End of code generation (place_mex_mex.c) */
