MATLAB="/usr/local/MATLAB/R2013b"
Arch=glnxa64
ENTRYPOINT=mexFunction
MAPFILE=$ENTRYPOINT'.map'
PREFDIR="/home/psecker/.matlab/R2013b"
OPTSFILE_NAME="./mexopts.sh"
. $OPTSFILE_NAME
COMPILER=$CC
. $OPTSFILE_NAME
echo "# Make settings for reject" > reject_mex.mki
echo "CC=$CC" >> reject_mex.mki
echo "CFLAGS=$CFLAGS" >> reject_mex.mki
echo "CLIBS=$CLIBS" >> reject_mex.mki
echo "COPTIMFLAGS=$COPTIMFLAGS" >> reject_mex.mki
echo "CDEBUGFLAGS=$CDEBUGFLAGS" >> reject_mex.mki
echo "CXX=$CXX" >> reject_mex.mki
echo "CXXFLAGS=$CXXFLAGS" >> reject_mex.mki
echo "CXXLIBS=$CXXLIBS" >> reject_mex.mki
echo "CXXOPTIMFLAGS=$CXXOPTIMFLAGS" >> reject_mex.mki
echo "CXXDEBUGFLAGS=$CXXDEBUGFLAGS" >> reject_mex.mki
echo "LD=$LD" >> reject_mex.mki
echo "LDFLAGS=$LDFLAGS" >> reject_mex.mki
echo "LDOPTIMFLAGS=$LDOPTIMFLAGS" >> reject_mex.mki
echo "LDDEBUGFLAGS=$LDDEBUGFLAGS" >> reject_mex.mki
echo "Arch=$Arch" >> reject_mex.mki
echo OMPFLAGS= >> reject_mex.mki
echo OMPLINKFLAGS= >> reject_mex.mki
echo "EMC_COMPILER=" >> reject_mex.mki
echo "EMC_CONFIG=optim" >> reject_mex.mki
"/usr/local/MATLAB/R2013b/bin/glnxa64/gmake" -B -f reject_mex.mk
