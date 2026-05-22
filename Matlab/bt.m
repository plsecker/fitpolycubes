function ret = bt(box,cube,transvec,rotvec)

global recursedepth recurserec maxpieces_placed

ret = 0;

if recursedepth <= 4
    %fprintf(1,'Recurse depth is <= 4: %d\n',int32(recursedepth))
end

recursedepth = recursedepth+1;
recurserec(recursedepth) = recurserec(recursedepth)+1;

%disp('Entering BT with')
%[transvec rotvec]
if reject(box,cube,transvec,rotvec)
    %    disp('Leaving BT with same')
    recursedepth = recursedepth-1;
    return
end

% with box, target cube and valid rotvec (1st element) place piece, return
% new box, new target cube, new piece translations and valid rotations for
% the first translation
[box,cube] = place(box,cube,transvec(1),rotvec(1));
[transvec,rotvec] = nextpiece(box,cube);

% monitor
global boxfilllevelcount boxmaxfilllevel
boxfilllevelcount = boxfilllevelcount+1;
if sum(box(:))/5 > boxmaxfilllevel
    boxmaxfilllevel = sum(box(:))/5;
    [boxmaxfilllevel boxfilllevelcount]
    %box
    if boxmaxfilllevel == 25        %  exit
        fprintf(1,'Max num pieces placed: %d, total pieces tried: %d, recurse depth %d\n',int32(boxmaxfilllevel),int32(boxfilllevelcount),int32(recursedepth));
        box
        ret = 1;
        return
    end
end
if ~mod(boxfilllevelcount,100000)
    toc
    fprintf(1,'Max num pieces placed: %d, total pieces tried: %d, recurse depth %d\n',int32(boxmaxfilllevel),int32(boxfilllevelcount),int32(recursedepth));
    if ~mod(boxfilllevelcount,maxpieces_placed)
        fprintf(1,'Max num pieces placed: %d, total pieces tried: %d, recurse depth %d\n',int32(boxmaxfilllevel),int32(boxfilllevelcount),int32(recursedepth));
        ret = 1;
        return
    end
end

while ~isempty(transvec)
    while ~isempty(rotvec)
        ret = bt(box,cube,transvec(1),rotvec(1));     % use next translation and its rotations
        if ret
            fprintf(1,'depth: %d, cube: %d, trans: %d, rot: %d\n',recursedepth,cube,transvec(1),rotvec(1));
            recursedepth = recursedepth-1;
            return;
        end
        rotvec = rotvec(2:end);         % choose next rot
    end
    transvec = transvec(2:end);         % use next translation
    % determine next rotations for this cube and next translation
    if ~isempty(transvec)

        rotvec = nextrot(cube, transvec(1));

    end
end

recursedepth = recursedepth-1;
end


