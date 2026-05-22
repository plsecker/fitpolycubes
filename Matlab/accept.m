function [filled] = accept(box, piece)
% Return status = TRUE if this candidate completes the box

filled = 0;
status = boxit(box,piece);
if status
    if all(box(:))
        filled = 1;
    end
end
