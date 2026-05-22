/*
 * nextrot_api.c
 *
 * Code generation for function 'nextrot_api'
 *
 * C source code generated on: Fri Dec 27 11:55:29 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "nextrot.h"
#include "nextrot_api.h"
#include "nextrot_data.h"

/* Function Declarations */
static real_T b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId);
static const mxArray *b_emlrt_marshallOut(real_T u_data[24], int32_T u_size[2]);
static void c_emlrt_marshallIn(const mxArray *c_boxcuberots, const char_T
  *identifier, real_T y[15000]);
static void d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId, real_T y[15000]);
static real_T e_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId);
static real_T emlrt_marshallIn(const mxArray *cube, const char_T *identifier);
static const mxArray *emlrt_marshallOut(const real_T u[15000]);
static void f_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId, real_T ret[15000]);

/* Function Definitions */
static real_T b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId)
{
  real_T y;
  y = e_emlrt_marshallIn(emlrtAlias(u), parentId);
  emlrtDestroyArray(&u);
  return y;
}

static const mxArray *b_emlrt_marshallOut(real_T u_data[24], int32_T u_size[2])
{
  const mxArray *y;
  static const int32_T iv2[2] = { 0, 0 };

  const mxArray *m1;
  y = NULL;
  m1 = mxCreateNumericArray(2, (int32_T *)&iv2, mxDOUBLE_CLASS, mxREAL);
  mxSetData((mxArray *)m1, (void *)u_data);
  mxSetDimensions((mxArray *)m1, u_size, 2);
  emlrtAssign(&y, m1);
  return y;
}

static void c_emlrt_marshallIn(const mxArray *c_boxcuberots, const char_T
  *identifier, real_T y[15000])
{
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  d_emlrt_marshallIn(emlrtAlias(c_boxcuberots), &thisId, y);
  emlrtDestroyArray(&c_boxcuberots);
}

static void d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId, real_T y[15000])
{
  f_emlrt_marshallIn(emlrtAlias(u), parentId, y);
  emlrtDestroyArray(&u);
}

static real_T e_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId)
{
  real_T ret;
  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "double", FALSE, 0U, 0);
  ret = *(real_T *)mxGetData(src);
  emlrtDestroyArray(&src);
  return ret;
}

static real_T emlrt_marshallIn(const mxArray *cube, const char_T *identifier)
{
  real_T y;
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  y = b_emlrt_marshallIn(emlrtAlias(cube), &thisId);
  emlrtDestroyArray(&cube);
  return y;
}

static const mxArray *emlrt_marshallOut(const real_T u[15000])
{
  const mxArray *y;
  static const int32_T iv1[3] = { 125, 24, 5 };

  const mxArray *m0;
  real_T (*pData)[];
  y = NULL;
  m0 = mxCreateNumericArray(3, (int32_T *)&iv1, mxDOUBLE_CLASS, mxREAL);
  pData = (real_T (*)[])mxGetPr(m0);
  memcpy(&(*pData)[0], &u[0], 15000U * sizeof(real_T));
  emlrtAssign(&y, m0);
  return y;
}

static void f_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId, real_T ret[15000])
{
  int32_T iv3[3];
  int32_T i;
  static const int8_T iv4[3] = { 125, 24, 5 };

  int32_T i1;
  int32_T i2;
  for (i = 0; i < 3; i++) {
    iv3[i] = iv4[i];
  }

  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "double", FALSE, 3U,
    iv3);
  for (i = 0; i < 5; i++) {
    for (i1 = 0; i1 < 24; i1++) {
      for (i2 = 0; i2 < 125; i2++) {
        ret[(i2 + 125 * i1) + 3000 * i] = (*(real_T (*)[15000])mxGetData(src))
          [(i2 + 125 * i1) + 3000 * i];
      }
    }
  }

  emlrtDestroyArray(&src);
}

void nextrot_api(const mxArray * const prhs[2], const mxArray *plhs[1])
{
  real_T (*nextrotvec_data)[24];
  real_T cube;
  real_T transno;
  const mxArray *tmp;
  int32_T nextrotvec_size[2];
  nextrotvec_data = (real_T (*)[24])mxMalloc(sizeof(real_T [24]));

  /* Marshall function inputs */
  cube = emlrt_marshallIn(emlrtAliasP(prhs[0]), "cube");
  transno = emlrt_marshallIn(emlrtAliasP(prhs[1]), "transno");

  /* Marshall in global variables */
  tmp = mexGetVariable("global", "boxcuberots");
  if (tmp) {
    c_emlrt_marshallIn(tmp, "boxcuberots", boxcuberots);
    boxcuberots_dirty = 0U;
  }

  tmp = mexGetVariable("global", "boxcubelevels");
  if (tmp) {
    c_emlrt_marshallIn(tmp, "boxcubelevels", boxcubelevels);
    boxcubelevels_dirty = 0U;
  }

  /* Invoke the target function */
  nextrot(cube, transno, *nextrotvec_data, nextrotvec_size);

  /* Marshall out global variables */
  mexPutVariable("global", "boxcuberots", emlrt_marshallOut(boxcuberots));
  mexPutVariable("global", "boxcubelevels", emlrt_marshallOut(boxcubelevels));

  /* Marshall function outputs */
  plhs[0] = b_emlrt_marshallOut(*nextrotvec_data, nextrotvec_size);
}

/* End of code generation (nextrot_api.c) */
