function RM = rotmatrix
% Rot about x axis
Rx90 = [[1 0 0];[0 0 -1];[0 1 0]];
Rxm90 = [[1 0 0];[0 0 1];[0 -1 0]];
Rx180 = [[1 0 0];[0 -1 0];[0 0 -1]];

% Rot about y axis
Ry90 = [[0 0 1];[0 1 0];[-1 0 0]];
Rym90 = [[0 0 -1];[0 1 0];[1 0 0]];
Ry180 = [[-1 0 0];[0 1 0];[0 0 -1]];

% Rot about z axis
Rz90 = [[0 -1 0];[1 0 0];[0 0 1]];
Rzm90 = [[0 1 0];[-1 0 0];[0 0 1]];
Rz180 = [[-1 0 0];[0 -1 0];[0 0 1]];

%Create master Rot matrix consisting of 4 yrots for each Z plus 4 yrots for
%remaining 2 X rots, ie. each face of cube
RM = zeros(3,3,4*6);

RM(:,:,1) = eye(3);
RM(:,:,2) = Rym90;
RM(:,:,3) = Ry180;
RM(:,:,4) = Ry90;
RM(:,:,5) = eye(3)*Rz90;
RM(:,:,6) = Rym90*Rz90;
RM(:,:,7) = Ry180*Rz90;
RM(:,:,8) = Ry90*Rz90;
RM(:,:,9) = eye(3)*Rz90^2;
RM(:,:,10) = Rym90*Rz90^2;
RM(:,:,11) = Ry180*Rz90^2;
RM(:,:,12) = Ry90*Rz90^2;
RM(:,:,13) = eye(3)*Rz90^3;
RM(:,:,14) = Rym90*Rz90^3;
RM(:,:,15) = Ry180*Rz90^3;
RM(:,:,16) = Ry90*Rz90^3;
RM(:,:,17) = eye(3)*Rx90;
RM(:,:,18) = Rym90*Rx90;
RM(:,:,19) = Ry180*Rx90;
RM(:,:,20) = Ry90*Rx90;
RM(:,:,21) = eye(3)*Rxm90;
RM(:,:,22) = Rym90*Rxm90;
RM(:,:,23) = Ry180*Rxm90;
RM(:,:,24) = Ry90*Rxm90;

%% Dev
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% % ROT ABOUT Z 4 times with each ROT ABOUT Y
% 
% c = Rz90*c;
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% c = Rz90*c;
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% c = Rz90*c;
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% c = Rz90*c;
% 
% % ROT ABOUT X
% c = Rx90*c;
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% c = Rx90*c;
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% c = Rx90*c;
% % Rot around Y
% c = rotall90(Rym90,c)
% 
% c = Rx90*c;