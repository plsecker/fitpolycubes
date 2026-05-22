function nextrotvec = nextrot(cube, transno)
% Return next rotation vector for a cube and translation

global boxcuberots
global boxcubelevels

%thiscubesrots = boxcuberots(cube,:,transno);
%nextrotvec = find(thiscubesrots);       % get all rots for this cube/translation

thiscubesrots = boxcuberots(cube,:,transno);
nextrotsum = sum(thiscubesrots);       % get number of rots for this cube/translation
thiscubeslevels = boxcubelevels(cube,:,transno);
[~,nextrotvec]=sort(thiscubeslevels);
nextrotvec = nextrotvec(1:nextrotsum);
