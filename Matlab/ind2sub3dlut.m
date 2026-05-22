function [xi,yi,zi] = ind2sub3dlut(ndx)
% fast version for 3d box of side length 5 using LUT

global IND2SUBLUT

a = IND2SUBLUT(ndx,:);
xi = a(1);
yi = a(2);
zi = a(3);

