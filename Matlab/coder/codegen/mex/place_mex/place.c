/*
 * place.c
 *
 * Code generation for function 'place'
 *
 * C source code generated on: Thu Dec 26 18:34:40 2013
 *
 */

/* Include files */
#include "rt_nonfinite.h"
#include "place.h"
#include "reject.h"

/* Function Definitions */
void place(const boolean_T box[125], real_T cube, real_T transno, real_T rotvec,
           boolean_T newbox[125], real_T *nextcube)
{
  (void)transno;
  (void)rotvec;

  /*  % Place a piece given current box, target cube and valid rotation vector */
  /*  % (choose first rotation) */
  /*   */
  /*  global P RM */
  /*   */
  /*  piece = P(:,:,transno);         % only deal with this translation */
  /*   */
  /*  % find 1's based coordinate of empty cube */
  /*  [xi,yi,zi] = ind2sub3d(length(box),cube); */
  /*  cubeoffset = repmat([xi-1;yi-1;zi-1],1,length(piece)); % find zero-based translation of cube */
  /*  % place first rotation */
  /*  Ri = rotvec(1); */
  /*  pr = cubeoffset + RM(:,:,Ri)*piece; */
  /*  [filled,newbox] = boxit(box,pr); */
  /*   */
  /*   */
  /*  % find next free cube in linear space */
  /*  boxlinear = newbox(:);             % turn box into a linear array with ones at filled locs */
  /*  for nextemptyind=1:numel(newbox)      % scan through empty cubes in turn */
  /*      if ~boxlinear(nextemptyind) */
  /*          %disp(nextempty) */
  /*          break;                     % found next empty cube */
  /*      end */
  /*  end */
  /*  nextcube = nextemptyind;        % record this target cube */
  *nextcube = cube + 1.0;
  memcpy(&newbox[0], &box[0], 125U * sizeof(boolean_T));
}

/* End of code generation (place.c) */
