function [nexttrans,nextrotvec] = nextpiece(box, nextcube)
% Return next piece translation and valid rotation vector for a cube
% (which could be empty)

global boxcuberots P RM transvec recursedepth
global IND2SUBLUT


%nexttrans = randperm(5);       % random option

if recursedepth > 1
    
    %%
    nexttrans = transvec;           % return new translations to try
    % extract valid rotations for this cube and 1st translation
    thiscubesrots = boxcuberots(nextcube,:,nexttrans(1));
    nextrotvec = find(thiscubesrots);       % get all rots for this cube/translation
    % if isempty(nextrotvec)                  % possible to have no valid rotations for this cube
    %     disp('No valid rots available for current cube?');
    % end
    
else
    
    %% Choose transvec which fills lowest layers
    % find 1's based coordinate of empty cube
%     [xi,yi,zi] = ind2sub3d(length(box),nextcube);
%     nextcubeoffset = repmat([xi-1;yi-1;zi-1],1,length(P)); % find zero-based translation of cube
 
    a = IND2SUBLUT(nextcube,:)-1;
    nextcubeoffset = a'*ones(1,5);                % quick version

    
    lowesttranssum = inf(1,5);
    
    for transno = 1:5
        
        thiscubesrots = boxcuberots(nextcube,:,transno);
        nextrotvec = find(thiscubesrots);       % get all rots for this cube/translation
                
        %        nextrotvec = nextrot(nextcube, transno);
        
        piece = P(:,:,transno);                 % only deal with this translation
        for Ri = nextrotvec  %%%%%%%%%%%%%%%%%%%
            pr = nextcubeoffset + RM(:,:,Ri)*piece;
            boxidx = 25*pr(3,:) + 5*pr(2,:) + pr(1,:)+1;   % find indexes of placed piece
            status = any(box(boxidx));
            if ~status
                indexsum = sum(boxidx);
                if indexsum < lowesttranssum(transno)
                    lowesttranssum(transno) = indexsum;
                end
            end
        end
    end
    
    valid = isfinite(lowesttranssum);
    [lowest,nexttrans] = sort(lowesttranssum);
    valid = isfinite(lowest);
    nexttrans = nexttrans(valid);           % weed out trans with no fills
    if ~isempty(nexttrans)
        nextrotvec = nextrot(nextcube, nexttrans(1));
    else
        nextrotvec = [];
    end
    
end

%        for Ri = nextrotvec
% OR
%         while ~isempty(nextrotvec)
%             Ri = nextrotvec(1);
%             nextrotvec = nextrotvec(2:end);
%

%             pr = nextcubeoffset + RM(:,:,Ri)*piece;
%             boxidx = 25*pr(3,:) + 5*pr(2,:) + pr(1,:)+1;   % find indexes of placed piece
%             status = any(box(boxidx));
%             if ~status
%                 indexsum = sum(boxidx);
%                 if indexsum < lowesttranssum(transno)
%                     lowesttranssum(transno) = indexsum;
%                     %lowestrot(transno) = nextrotvec;
%                 end
%             end
