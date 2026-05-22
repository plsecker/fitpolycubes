function [status,box] = boxit(box,p)
% Check if piece will clash if inserted into box, insert if it does
% piece is zero-based coords

% convert p's cube coordinates to linear indicies of box
%boxidx=sub2ind(size(box),p(1,:)+1,p(2,:)+1,p(3,:)+1);

%blen = length(box);
%boxidx = blen^2*p(3,:) + blen*p(2,:) + p(1,:)+1;   % fast version

boxidx = 25*p(3,:) + 5*p(2,:) + p(1,:)+1;   % faster version

if any(box(boxidx))
    status = false;
    return
else
    
    % Insert piece array into box and return true
    box(boxidx) = ones(1,length(p));
    status = true;
end