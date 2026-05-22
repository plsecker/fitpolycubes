/*
 * place_api.c
 *
 * Code generation for function 'place_api'
 *
 * C source code generated on: Fri Dec 27 17:33:31 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "place_api.h"
#include "place_data.h"

/* Function Declarations */
static boolean_T (*b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId))[125];
static const mxArray *b_emlrt_marshallOut(const real_T u[216]);
static real_T c_emlrt_marshallIn(const mxArray *cube, const char_T *identifier);
static const mxArray *c_emlrt_marshallOut(boolean_T u[125]);
static real_T d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId);
static const mxArray *d_emlrt_marshallOut(real_T u);
static void e_emlrt_marshallIn(const mxArray *c_P, const char_T *identifier,
  real_T y[75]);
static boolean_T (*emlrt_marshallIn(const mxArray *box, const char_T *identifier))
  [125];
static const mxArray *emlrt_marshallOut(const real_T u[75]);
static void f_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId, real_T y[75]);
static void g_emlrt_marshallIn(const mxArray *c_RM, const char_T *identifier,
  real_T y[216]);
static void h_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId, real_T y[216]);
static boolean_T (*i_emlrt_marshallIn(const mxArray *src, const
  emlrtMsgIdentifier *msgId))[125];
static real_T j_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId);
static void k_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId, real_T ret[75]);
static void l_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId, real_T ret[216]);

/* Function Definitions */
static boolean_T (*b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId))[125]
{
  boolean_T (*y)[125];
  y = i_emlrt_marshallIn(emlrtAlias(u), parentId);
  emlrtDestroyArray(&u);
  return y;
}
  static const mxArray *b_emlrt_marshallOut(const real_T u[216])
{
  const mxArray *y;
  static const int32_T iv1[3] = { 3, 3, 24 };

  const mxArray *m1;
  real_T (*pData)[];
  y = NULL;
  m1 = mxCreateNumericArray(3, (int32_T *)&iv1, mxDOUBLE_CLASS, mxREAL);
  pData = (real_T (*)[])mxGetPr(m1);
  memcpy(&(*pData)[0], &u[0], 216U * sizeof(real_T));
  emlrtAssign(&y, m1);
  return y;
}

static real_T c_emlrt_marshallIn(const mxArray *cube, const char_T *identifier)
{
  real_T y;
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  y = d_emlrt_marshallIn(emlrtAlias(cube), &thisId);
  emlrtDestroyArray(&cube);
  return y;
}

static const mxArray *c_emlrt_marshallOut(boolean_T u[125])
{
  const mxArray *y;
  static const int32_T iv2[3] = { 0, 0, 0 };

  const mxArray *m2;
  static const int32_T iv3[3] = { 5, 5, 5 };

  y = NULL;
  m2 = mxCreateLogicalArray(3, iv2);
  mxSetData((mxArray *)m2, (void *)u);
  mxSetDimensions((mxArray *)m2, iv3, 3);
  emlrtAssign(&y, m2);
  return y;
}

static real_T d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId)
{
  real_T y;
  y = j_emlrt_marshallIn(emlrtAlias(u), parentId);
  emlrtDestroyArray(&u);
  return y;
}

static const mxArray *d_emlrt_marshallOut(real_T u)
{
  const mxArray *y;
  const mxArray *m3;
  y = NULL;
  m3 = mxCreateDoubleScalar(u);
  emlrtAssign(&y, m3);
  return y;
}

static void e_emlrt_marshallIn(const mxArray *c_P, const char_T *identifier,
  real_T y[75])
{
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  f_emlrt_marshallIn(emlrtAlias(c_P), &thisId, y);
  emlrtDestroyArray(&c_P);
}

static boolean_T (*emlrt_marshallIn(const mxArray *box, const char_T *identifier))
  [125]
{
  boolean_T (*y)[125];
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  y = b_emlrt_marshallIn(emlrtAlias(box), &thisId);
  emlrtDestroyArray(&box);
  return y;
}
  static const mxArray *emlrt_marshallOut(const real_T u[75])
{
  const mxArray *y;
  static const int32_T iv0[3] = { 3, 5, 5 };

  const mxArray *m0;
  real_T (*pData)[];
  y = NULL;
  m0 = mxCreateNumericArray(3, (int32_T *)&iv0, mxDOUBLE_CLASS, mxREAL);
  pData = (real_T (*)[])mxGetPr(m0);
  memcpy(&(*pData)[0], &u[0], 75U * sizeof(real_T));
  emlrtAssign(&y, m0);
  return y;
}

static void f_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId, real_T y[75])
{
  k_emlrt_marshallIn(emlrtAlias(u), parentId, y);
  emlrtDestroyArray(&u);
}

static void g_emlrt_marshallIn(const mxArray *c_RM, const char_T *identifier,
  real_T y[216])
{
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  h_emlrt_marshallIn(emlrtAlias(c_RM), &thisId, y);
  emlrtDestroyArray(&c_RM);
}

static void h_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId, real_T y[216])
{
  l_emlrt_marshallIn(emlrtAlias(u), parentId, y);
  emlrtDestroyArray(&u);
}

static boolean_T (*i_emlrt_marshallIn(const mxArray *src, const
  emlrtMsgIdentifier *msgId))[125]
{
  boolean_T (*ret)[125];
  int32_T iv4[3];
  int32_T i;
  for (i = 0; i < 3; i++) {
    iv4[i] = 5;
  }

  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "logical", FALSE, 3U,
    iv4);
  ret = (boolean_T (*)[125])mxGetData(src);
  emlrtDestroyArray(&src);
  return ret;
}
  static real_T j_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier *
  msgId)
{
  real_T ret;
  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "double", FALSE, 0U, 0);
  ret = *(real_T *)mxGetData(src);
  emlrtDestroyArray(&src);
  return ret;
}

static void k_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId, real_T ret[75])
{
  int32_T iv5[3];
  int32_T i;
  static const int8_T iv6[3] = { 3, 5, 5 };

  int32_T i0;
  int32_T i1;
  for (i = 0; i < 3; i++) {
    iv5[i] = iv6[i];
  }

  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "double", FALSE, 3U,
    iv5);
  for (i = 0; i < 5; i++) {
    for (i0 = 0; i0 < 5; i0++) {
      for (i1 = 0; i1 < 3; i1++) {
        ret[(i1 + 3 * i0) + 15 * i] = (*(real_T (*)[75])mxGetData(src))[(i1 + 3 *
          i0) + 15 * i];
      }
    }
  }

  emlrtDestroyArray(&src);
}

static void l_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId, real_T ret[216])
{
  int32_T iv7[3];
  int32_T i;
  static const int8_T iv8[3] = { 3, 3, 24 };

  int32_T i2;
  int32_T i3;
  for (i = 0; i < 3; i++) {
    iv7[i] = iv8[i];
  }

  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "double", FALSE, 3U,
    iv7);
  for (i = 0; i < 24; i++) {
    for (i2 = 0; i2 < 3; i2++) {
      for (i3 = 0; i3 < 3; i3++) {
        ret[(i3 + 3 * i2) + 9 * i] = (*(real_T (*)[216])mxGetData(src))[(i3 + 3 *
          i2) + 9 * i];
      }
    }
  }

  emlrtDestroyArray(&src);
}

void place_api(const mxArray * const prhs[4], const mxArray *plhs[2])
{
  boolean_T (*newbox)[125];
  boolean_T (*box)[125];
  real_T cube;
  real_T transno;
  real_T rot;
  const mxArray *tmp;
  real_T nextcube;
  newbox = (boolean_T (*)[125])mxMalloc(sizeof(boolean_T [125]));

  /* Marshall function inputs */
  box = emlrt_marshallIn(emlrtAlias(prhs[0]), "box");
  cube = c_emlrt_marshallIn(emlrtAliasP(prhs[1]), "cube");
  transno = c_emlrt_marshallIn(emlrtAliasP(prhs[2]), "transno");
  rot = c_emlrt_marshallIn(emlrtAliasP(prhs[3]), "rot");

  /* Marshall in global variables */
  tmp = mexGetVariable("global", "P");
  if (tmp) {
    e_emlrt_marshallIn(tmp, "P", P);
    P_dirty = 0U;
  }

  tmp = mexGetVariable("global", "RM");
  if (tmp) {
    g_emlrt_marshallIn(tmp, "RM", RM);
    RM_dirty = 0U;
  }

  /* Invoke the target function */
  place(*box, cube, transno, rot, *newbox, &nextcube);

  /* Marshall out global variables */
  mexPutVariable("global", "P", emlrt_marshallOut(P));
  mexPutVariable("global", "RM", b_emlrt_marshallOut(RM));

  /* Marshall function outputs */
  plhs[0] = c_emlrt_marshallOut(*newbox);
  plhs[1] = d_emlrt_marshallOut(nextcube);
}

/* End of code generation (place_api.c) */
