/*
 * reject_api.c
 *
 * Code generation for function 'reject_api'
 *
 * C source code generated on: Thu Dec 26 18:41:51 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "reject.h"
#include "reject_api.h"

/* Function Declarations */
static boolean_T (*b_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId))[125];
static real_T c_emlrt_marshallIn(const mxArray *cube, const char_T *identifier);
static real_T d_emlrt_marshallIn(const mxArray *u, const emlrtMsgIdentifier
  *parentId);
static boolean_T (*e_emlrt_marshallIn(const mxArray *src, const
  emlrtMsgIdentifier *msgId))[125];
static boolean_T (*emlrt_marshallIn(const mxArray *box, const char_T *identifier))
  [125];
static const mxArray *emlrt_marshallOut(boolean_T u);
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
  int32_T iv0[3];
  int32_T i;
  for (i = 0; i < 3; i++) {
    iv0[i] = 5;
  }

  emlrtCheckBuiltInR2012b(emlrtRootTLSGlobal, msgId, src, "logical", FALSE, 3U,
    iv0);
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

static const mxArray *emlrt_marshallOut(boolean_T u)
{
  const mxArray *y;
  const mxArray *m0;
  y = NULL;
  m0 = mxCreateLogicalScalar(u);
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
  plhs[0] = emlrt_marshallOut(status);
}

/* End of code generation (reject_api.c) */
