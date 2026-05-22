% Attempt to fill box by linear filling.
% Scans for next empty cube, then trys to fit all rotations that
% apply to that cube (for the particular piece translation)

% Run computevalids.m first

tic
maxnumpiecesplaced = 0;
numboxestried = 0;
transno = 5;
piece = P(:,:,transno);         % only deal with this translation

while true
    numboxestried = numboxestried+1;
    % clear box
    box = zeros(5,5,5);
    numpiecesplaced = 0;
    
    canfill = 1;                    % empty box
    while canfill
        
        %         boxlinearind = find(~box(:));
        %         % randomize selection
        %         nextemptyind = boxlinearind(randi(length(boxlinearind)));
        
        boxlinear = box(:);                % turn box into a linear array with ones at filled locs
        for nextemptyind=1:numel(box)      % scan through empty cubes in turn
            if ~boxlinear(nextemptyind)
                %disp(nextempty)
                break;                     % found next empty cube
            end
            if nextemptyind==numel(box)
                disp('Filled Box!')
            end
        end
        
        %        [xi,yi,zi] = ind2sub(size(box),nextemptyind);   % find 1's based coordinate of empty cube
        [xi,yi,zi] = ind2sub3d(length(box),nextemptyind);
        
        if box(xi,yi,zi)
            error('Not empty')      % should always be true
        end
        
        thiscubesrots = boxcuberots(nextemptyind,:,transno);   % extract valid rotations for this cube
        
        validx = find(thiscubesrots);                % get all rots for this cube/translation
        if isempty(validx)          % possible to have no valid rotations for this cube
            %disp('No valid rots available for current cube');
            canfill = false;
            break
        end
        validxlen = length(validx);
        
        % randomize selection
        permvec = randperm(validxlen);
        validx = validx(permvec);
        
        
        cubeoffset = repmat([xi-1;yi-1;zi-1],1,numcubes); % find zero-based translation of piece
        % start with first rotation and continue until find a rotation that fits
        placed = false;
        for rotnum = 1:validxlen
            Ri = validx(rotnum);
            pr = cubeoffset + RM(:,:,Ri)*piece;
            
            [placed,box] = boxit(box,pr);         % see if can place it
            if placed
                break;
            end
        end
        if ~placed
            %disp('No rots fit for current cube')
            canfill = false;
            emptycubeindex = false;
        else
            canfill = true;
            numpiecesplaced = numpiecesplaced+1;
            %             if accept(box,pr)
            %                 error('Filled Box!')
            %             end
        end
    end
    %fprintf(1,'Num pieces placed in this box: %d\n',numpiecesplaced);
    
    if numpiecesplaced > maxnumpiecesplaced
        maxnumpiecesplaced = numpiecesplaced;
        fprintf(1,'Max num pieces placed: %d, boxes tried: %d\n',maxnumpiecesplaced,numboxestried);
        box
    end
    
    if ~mod(numboxestried,10000)
        fprintf(1,'Max num pieces placed: %d, boxes tried: %d\n',maxnumpiecesplaced,numboxestried);
        toc
    end
end