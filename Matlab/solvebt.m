% Run computevalids.m to precalculate global vars for box and piece
addpath('coder')

global boxfilllevel boxfilllevelcount boxmaxfilllevel recursedepth recurserec
global transvec maxpieces_placed

maxpieces_placed = 1e8;

boxfilllevelcount = 1;
boxmaxfilllevel = 1;

transvec = [1 2 3 4 5];       % list of translations

recurserec = zeros(1,25);

cube = 1;                   % start filling from this cube

tic
rng('shuffle')
% while true
%     transvec = randperm(5)
    for transno = 5;        % cube = 1 can only be filled with a 1 or a 5 translation for N polycube
        validrots = find(boxcuberots(cube,:,transno));
        for rot=validrots(5)
            disp('Trans Rot'); [transno rot]
            boxfilllevelcount = 1;
            recursedepth = 0;
            box = logical(zeros(5,5,5));
            ret = bt(box,cube,transno,rot);
            if boxmaxfilllevel == 25
                error('Found 25!')
            else
                boxmaxfilllevel
                boxmaxfilllevel = 0;
            end
        end
    end
% end


% Start cube = 1, 24 pieces:
%transno = [1]
%validrots = [Inf 12382 240364 Inf 292405 216246], Inf = > 1e6
%transno = [5]
%validrots = [1721668 Inf Inf 35331  ? 1637974], Inf = > 1e6

% Trans Rot
% ans =
%      5    19
% Max num pieces placed: 25, total pieces tried: 19383844, recurse depth 25
% depth: 25, cube: 116, trans: 5, rot: 19
% depth: 24, cube: 111, trans: 1, rot: 21
% depth: 23, cube: 109, trans: 5, rot: 14
% depth: 22, cube: 103, trans: 4, rot: 17
% depth: 21, cube: 82, trans: 1, rot: 8
% depth: 20, cube: 78, trans: 1, rot: 8
% depth: 19, cube: 57, trans: 1, rot: 8
% depth: 18, cube: 55, trans: 1, rot: 5
% depth: 17, cube: 53, trans: 1, rot: 8
% depth: 16, cube: 47, trans: 1, rot: 2
% depth: 15, cube: 34, trans: 1, rot: 12
% depth: 14, cube: 32, trans: 1, rot: 8
% depth: 13, cube: 31, trans: 1, rot: 18
% depth: 12, cube: 30, trans: 1, rot: 6
% depth: 11, cube: 29, trans: 1, rot: 12
% depth: 10, cube: 26, trans: 5, rot: 10
% depth: 9, cube: 25, trans: 5, rot: 4
% depth: 8, cube: 21, trans: 1, rot: 18
% depth: 7, cube: 20, trans: 1, rot: 22
% depth: 6, cube: 16, trans: 5, rot: 24
% depth: 5, cube: 13, trans: 3, rot: 13
% depth: 4, cube: 10, trans: 5, rot: 16
% depth: 3, cube: 6, trans: 5, rot: 14
% depth: 2, cube: 3, trans: 3, rot: 9
% Error using solvebt (line 30)  -- always do lowest layer fill nextpiece.m

% Trans Rot
% ans =
%      5    19
% Max num pieces placed: 25, total pieces tried: 2001598, recurse depth 25
% depth: 25, cube: 116, trans: 5, rot: 19
% depth: 24, cube: 111, trans: 1, rot: 21
% depth: 23, cube: 109, trans: 5, rot: 14
% depth: 22, cube: 103, trans: 4, rot: 17
% depth: 21, cube: 91, trans: 5, rot: 19
% depth: 20, cube: 86, trans: 1, rot: 21
% depth: 19, cube: 85, trans: 3, rot: 13
% depth: 18, cube: 78, trans: 3, rot: 23
% depth: 17, cube: 66, trans: 1, rot: 21
% depth: 16, cube: 53, trans: 3, rot: 23
% depth: 15, cube: 47, trans: 5, rot: 4
% depth: 14, cube: 42, trans: 1, rot: 1
% depth: 13, cube: 38, trans: 4, rot: 11
% depth: 12, cube: 31, trans: 1, rot: 18
% depth: 11, cube: 29, trans: 4, rot: 17
% depth: 10, cube: 26, trans: 5, rot: 10
% depth: 9, cube: 21, trans: 1, rot: 1
% depth: 8, cube: 20, trans: 5, rot: 20
% depth: 7, cube: 17, trans: 1, rot: 21
% depth: 6, cube: 15, trans: 1, rot: 2
% depth: 5, cube: 12, trans: 3, rot: 9
% depth: 4, cube: 10, trans: 1, rot: 2
% depth: 3, cube: 6, trans: 1, rot: 5
% depth: 2, cube: 3, trans: 3, rot: 9 -- never do lowest layer fill nextpiece.m

%% Y piece solved with [1 2 5 4 3] and [5 23] in 262k