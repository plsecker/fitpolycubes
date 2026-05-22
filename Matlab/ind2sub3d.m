function [xi,yi,zi] = ind2sub3d(len,ndx)
% fast version for 3d box of side length len

lensq = len^2;


  vi = rem(ndx-1, lensq) + 1;         
  zi = (ndx - vi)/lensq + 1; 
  ndx = vi;     

  vi = rem(ndx-1, len) + 1;         
  yi = (ndx - vi)/len + 1; 
  ndx = vi;
  
  xi = ndx;
