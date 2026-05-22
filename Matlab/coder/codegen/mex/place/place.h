/*
 * place.h
 *
 * Code generation for function 'place'
 *
 * C source code generated on: Fri Dec 27 17:33:31 2013
 *
 */

#ifndef __PLACE_H__
#define __PLACE_H__
/* Include files */
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "mwmathutil.h"

#include "tmwtypes.h"
#include "mex.h"
#include "emlrt.h"
#include "blas.h"
#include "rtwtypes.h"
#include "place_types.h"

/* Function Declarations */
extern void place(const boolean_T box[125], real_T cube, real_T transno, real_T rot, boolean_T newbox[125], real_T *nextcube);
#endif
/* End of code generation (place.h) */
