/*
 * eml_sort.c
 *
 * Code generation for function 'eml_sort'
 *
 * C source code generated on: Fri Dec 27 11:55:29 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "nextrot.h"
#include "eml_sort.h"

/* Function Definitions */
void eml_sort(const real_T x[24], real_T y[24], int32_T idx[24])
{
  int32_T k;
  boolean_T p;
  int8_T idx0[24];
  int32_T i;
  int32_T i2;
  int32_T j;
  int32_T pEnd;
  int32_T b_p;
  int32_T q;
  int32_T qEnd;
  int32_T kEnd;
  for (k = 0; k < 24; k++) {
    idx[k] = k + 1;
  }

  for (k = 0; k < 24; k += 2) {
    if ((x[k] <= x[k + 1]) || muDoubleScalarIsNaN(x[k + 1])) {
      p = TRUE;
    } else {
      p = FALSE;
    }

    if (p) {
    } else {
      idx[k] = k + 2;
      idx[k + 1] = k + 1;
    }
  }

  for (i = 0; i < 24; i++) {
    idx0[i] = 1;
  }

  i = 2;
  while (i < 24) {
    i2 = i << 1;
    j = 1;
    for (pEnd = 1 + i; pEnd < 25; pEnd = qEnd + i) {
      b_p = j;
      q = pEnd - 1;
      qEnd = j + i2;
      if (qEnd > 25) {
        qEnd = 25;
      }

      k = 0;
      kEnd = qEnd - j;
      while (k + 1 <= kEnd) {
        if ((x[idx[b_p - 1] - 1] <= x[idx[q] - 1]) || muDoubleScalarIsNaN
            (x[idx[q] - 1])) {
          p = TRUE;
        } else {
          p = FALSE;
        }

        if (p) {
          idx0[k] = (int8_T)idx[b_p - 1];
          b_p++;
          if (b_p == pEnd) {
            while (q + 1 < qEnd) {
              k++;
              idx0[k] = (int8_T)idx[q];
              q++;
            }
          }
        } else {
          idx0[k] = (int8_T)idx[q];
          q++;
          if (q + 1 == qEnd) {
            while (b_p < pEnd) {
              k++;
              idx0[k] = (int8_T)idx[b_p - 1];
              b_p++;
            }
          }
        }

        k++;
      }

      for (k = 0; k + 1 <= kEnd; k++) {
        idx[(j + k) - 1] = idx0[k];
      }

      j = qEnd;
    }

    i = i2;
  }

  for (k = 0; k < 24; k++) {
    y[k] = x[idx[k] - 1];
  }
}

/* End of code generation (eml_sort.c) */
