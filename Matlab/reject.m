function status = reject(box,cube,transno,rotvec)
% Return status = TRUE if this candidate piece can't be filled

global P RM IND2SUBLUT

piece = P(:,:,transno);         % only deal with this translation

% find 1's based coordinate of empty cube
%[xi,yi,zi] = ind2sub3d(5,cube);
% LUT version
a = IND2SUBLUT(cube,:)-1;

%cubeoffset = repmat([xi-1;yi-1;zi-1],1,length(piece)); % find zero-based translation of piece
%cubeoffset = repmat(a',1,length(piece)); % find zero-based translation of piece
cubeoffset = a'*ones(1,5);                % quick version

% check first rotation
Ri = rotvec(1);
pr = cubeoffset + RM(:,:,Ri)*piece;

%% this is vital parts of boxit.m

boxidx = 25*pr(3,:) + 5*pr(2,:) + pr(1,:)+1;   % faster version
status = any(box(boxidx));