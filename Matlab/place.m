function [newbox,nextcube] = place(box, cube, transno, rot)
% Place a piece into target cube with valid trans and valid rotation
% into a known good box

global P RM

piece = P(:,:,transno);         % only deal with this translation

% find 1's based coordinate of empty cube
[xi,yi,zi] = ind2sub3d(length(box),cube);
cubeoffset = repmat([xi-1;yi-1;zi-1],1,length(piece)); % find zero-based translation of cube
% place first rotation
Ri = rot;
pr = cubeoffset + RM(:,:,Ri)*piece;
[~,newbox] = boxit(box,pr);


% find next free cube in linear space
boxlinear = newbox(:);             % turn box into a linear array with ones at filled locs
for nextemptyind=1:numel(newbox)      % scan through empty cubes in turn
    if ~boxlinear(nextemptyind)
        %disp(nextempty)
        break;                     % found next empty cube
    end
end
nextcube = nextemptyind;        % record this target cube
