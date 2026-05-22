global boxcuberots P RM IND2SUBLUT
global boxcubelevels

% Create rot matrix
RM=rotmatrix;


% Declare one instance of piece and translate every cube to zero
p = [[0 0 0];[1 0 0];[2 0 0];[2 0 1];[3 0 1]]';     % N polycube
%p = [[0 0 0];[1 0 0];[2 0 0];[2 0 1];[3 0 0]]';     % Y polycube
%p = [[0 0 0];[1 0 0];[2 0 0];[3 0 0];[4 0 0]]';     % I polycube
%p = [[0 0 0];[1 0 0];[0 0 1];[1 1 0];[1 1 1]]';     % 3D polycube A

numcubes = length(p);
P(:,:,1) = p;           % save 1st piece, compute all translations
for Ri = 2:numcubes
    P(:,:,Ri) = P(:,:,1)-repmat(p(:,Ri),1,numcubes);
end
%ptrans = P(:,:,1)       % choose particular translation

box = logical(zeros(5,5,5));

scatter3(p(1,:),p(2,:),p(3,:),500,'s','filled')
view(45,20)


% for all piece translations, iterate through all box locations and count
% no. of valid 'fits'
boxcuberots = zeros(numel(box),24,numcubes);     % linear index of potential rots from RM
boxcubecnts = zeros([size(box), numcubes]);
boxcubelevels = inf(numel(box),24,numcubes);

boxcubepieceindexs = cell(125,5);

% eg. for N, compute all 960 unique starting positions (a block has 24 rotations, for
% the N piece (and Y) it can cover one plane in 2*4 ways and hence 24*2*4*5
% ie. sum(boxcuberots(:)) = 960  starting positions

for transno = 1:numcubes
    transno
    for zi = 1:5        % each plane
        for yi = 1:5
            for xi = 1:5
                boxidx = sub2ind(size(box),xi,yi,zi);   % find linear index
                
                cubeoffset = [xi-1;yi-1;zi-1];           % use zero offsets for rots
                cubeoffset = repmat(cubeoffset,1,numcubes);
                
                box = logical(zeros(5,5,5));
                box(1:boxidx-1) = ones(1,boxidx-1);     % fill box up to (not including) this index
                % determine valid rotations
                for Ri = 1:24
                    pr = cubeoffset + RM(:,:,Ri)*P(:,:,transno);
                    %   plot3(pr(1,:),pr(2,:),pr(3,:),'-x');
                    %disp(i);
                    if ~any(pr(:)<0) && ~any(pr(:)>4)   % check if fits box
                        %plot3(pr(1,:),pr(2,:),pr(3,:),'-x');
                        % these lines record all valid rots assuming an empty box
%                        boxcuberots(boxidx,Ri,transno) = true;  % save as valid rot
%                        boxcubecnts(xi,yi,zi,transno) = boxcubecnts(xi,yi,zi,transno)+1;    % count valid rot

                        % only retain rots for partially filled box (up to boxidx)
                        filled = boxit(box,pr);
                        if filled
                            boxcuberots(boxidx,Ri,transno) = true;  % save as valid rot
                            boxcubecnts(xi,yi,zi,transno) = boxcubecnts(xi,yi,zi,transno)+1;    % count valid rot
                            pieceindexs = 25*pr(3,:) + 5*pr(2,:) + pr(1,:)+1;   % find indexes of placed piece
                            boxcubelevels(boxidx,Ri,transno) = sum(pieceindexs);    % sum indexes as a metric of fullness

                            boxcubepieceindexs{boxidx,transno} = [boxcubepieceindexs{boxidx,transno} pieceindexs];
                        end
                    end
                end
            end
        end
    end
    bar3(boxcubecnts(:,:,1,transno))
%    bar3(boxcubelevels(:,:,transno))
    title(sprintf('Bottom plane, Trans: %d',transno))
    pause
end

numways = sum(boxcuberots(:))

% compute ind2sub LUTs
IND2SUBLUT = zeros(125,3);
for i = 1:125
    [a,b,c] = ind2sub3d(5,i);
    IND2SUBLUT(i,:) = [a,b,c];
end

%boxcubecnts
%box

% xlabel('x')
% ylabel('y')
% zlabel('z')
% title('Valid rotations for base layer')
% xlim([-1,4])
% ylim([-1,4])
% zlim([-1,4])
