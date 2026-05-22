/*
 * place_mex_api.c
 *
 * Code generation for function 'place_mex_api'
 *
 * C source code generated on: Thu Dec 26 18:34:40 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "reject.h"
#include "place_mex_api.h"

/* Function Declarations */
static boolean_T (*b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId))[125];
static const mxArray *b_emlrt_marshallOut(real_T u);
static real_T c_emlrt_marshallIn(const mxArray *cube, const char_T *identifier);
static const mxArray *c_emlrt_marshallOut(boolean_T u);
static real_T d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId);
static boolean_T (*e_emlrt_marshallIn(const mxArray *src, const
  emlrtMsgIdentifier *msgId))[125];
static boolean_T (*emlrt_marshallIn(const mxArray *box, const char_T *identifier))
  [125];
static const mxArray *emlrt_marshallOut(boolean_T u[125]);
static real_T f_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId);

/* Function Definitions */
static boolean_T (*b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId))[125]
{
  boolean_T (*y)[125];
  y = e_emlrt_marshallIn(emlrtAlias(u), parentId);
  emlrtDestroyArray(&u);
  return y;
}
  static const mxArray *b_emlrt_marshallOut(real_T u)
{
  const mxArray *y;
  const mxArray *m1;
  y = NULL;
  m1 = mxCreateDoubleScalar(u);
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

static const mxArray *c_emlrt_marshallOut(boolean_T u)
{
  const mxArray *y;
  const mxArray *m2;
  y = NULL;
  m2 = mxCreateLogicalScalar(u);
  emlrtAssign(&y, m2);
  return y;
}

static real_T d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId)
{
  real_T y;
  y = f_emlrt_marshallIn(emlrtAlias(u), parentId);
  emlrtDestroyArray(&u);
  return y;
}

static boolean_T (*e_emlrt_marshallIn(const mxArray *src, const
  emlrtMsgIdentifier *msgId))[125]
{
  boolean_T (*ret)[125];
  int32_T iv2[3];
  int32_T i;
  for (i = 0; i < 3; i++) {
    iv2[i] = 5;
  }

  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "logical", FALSE, 3U,
    iv2);
  ret = (boolean_T (*)[125])mxGetData(src);
  emlrtDestroyArray(&src);
  return ret;
}
  static boolean_T (*emlrt_marshallIn(const mxArray *box, const char_T
  *identifier))[125]
{
  boolean_T (*y)[125];
  emlrtMsgIdentifier thisId;
  thisId.fIdentifier = identifier;
  thisId.fParent = NULL;
  y = b_emlrt_marshallIn(emlrtAlias(box), &thisId);
  emlrtDestroyArray(&box);
  return y;
}

static const mxArray *emlrt_marshallOut(boolean_T u[125])
{
  const mxArray *y;
  static const int32_T iv0[3] = { 0, 0, 0 };

  const mxArray *m0;
  static const int32_T iv1[3] = { 5, 5, 5 };

  y = NULL;
  m0 = mxCreateLogicalArray(3, iv0);
  mxSetData((mxArray *)m0, (void *)u);
  mxSetDimensions((mxArray *)m0, iv1, 3);
  emlrtAssign(&y, m0);
  return y;
}

static real_T f_emlrt_marshallIn(const mxArray *src, const emlrtMsgIdentifier
  *msgId)
{
  real_T ret;
  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "double", FALSE, 0U, 0);
  ret = *(real_T *)mxGetData(src);
  emlrtDestroyArray(&src);
  return ret;
}

void place_api(const mxArray * const prhs[4], const mxArray *plhs[2])
{
  boolean_T (*newbox)[125];
  boolean_T (*box)[125];
  real_T cube;
  real_T transno;
  real_T rotvec;
  real_T nextcube;
  newbox = (boolean_T (*)[125])mxMalloc(sizeof(boolean_T [125]));

  /* Marshall function inputs */
  box = emlrt_marshallIn(emlrtAlias(prhs[0]), "box");
  cube = c_emlrt_marshallIn(emlrtAliasP(prhs[1]), "cube");
  transno = c_emlrt_marshallIn(emlrtAliasP(prhs[2]), "transno");
  rotvec = c_emlrt_marshallIn(emlrtAliasP(prhs[3]), "rotvec");

  /* Invoke the target function */
  place(*box, cube, transno, rotvec, *newbox, &nextcube);

  /* Marshall function outputs */
  plhs[0] = emlrt_marshallOut(*newbox);
  plhs[1] = b_emlrt_marshallOut(nextcube);
}

void reject_api(const mxArray * const prhs[4], const mxArray *plhs[1])
{
  boolean_T (*box)[125];
  real_T cube;
  real_T transno;
  real_T rotvec;
  boolean_T status;

  /* Marshall function inputs */
  box = emlrt_marshallIn(emlrtAlias(prhs[0]), "box");
  cube = c_emlrt_marshallIn(emlrtAliasP(prhs[1]), "cube");
  transno = c_emlrt_marshallIn(emlrtAliasP(prhs[2]), "transno");
  rotvec = c_emlrt_marshallIn(emlrtAliasP(prhs[3]), "rotvec");

  /* Invoke the target function */
  status = reject(*box, cube, transno, rotvec);

  /* Marshall function outputs */
  plhs[0] = c_emlrt_marshallOut(status);
}

/* End of code generation (place_mex_api.c) */
