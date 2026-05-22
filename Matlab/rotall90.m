function c = rotall90(R,c)
% Rot 4 times
plot3(c(1,:),c(2,:),c(3,:),'-x')
c = R*c;
plot3(c(1,:),c(2,:),c(3,:),'-x')
c = R*c;
plot3(c(1,:),c(2,:),c(3,:),'-x')
c = R*c;
plot3(c(1,:),c(2,:),c(3,:),'-x')
c = R*c;
