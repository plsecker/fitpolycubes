MATLAB="/usr/local/MATLAB/R2013b"
Arch=glnxa64
ENTRYPOINT=mexFunction
MAPFILE=$ENTRYPOINT'.map'
PREFDIR="/home/psecker/.matlab/R2013b"
OPTSFILE_NAME="./mexopts.sh"
. $OPTSFILE_NAME
COMPILER=$CC
. $OPTSFILE_NAME
echo "# Make settings for place" > place_mex.mki
echo "CC=$CC" >> place_mex.mki
echo "CFLAGS=$CFLAGS" >> place_mex.mki
echo "CLIBS=$CLIBS" >> place_mex.mki
echo "COPTIMFLAGS=$COPTIMFLAGS" >> place_mex.mki
echo "CDEBUGFLAGS=$CDEBUGFLAGS" >> place_mex.mki
echo "CXX=$CXX" >> place_mex.mki
echo "CXXFLAGS=$CXXFLAGS" >> place_mex.mki
echo "CXXLIBS=$CXXLIBS" >> place_mex.mki
echo "CXXOPTIMFLAGS=$CXXOPTIMFLAGS" >> place_mex.mki
echo "CXXDEBUGFLAGS=$CXXDEBUGFLAGS" >> place_mex.mki
echo "LD=$LD" >> place_mex.mki
echo "LDFLAGS=$LDFLAGS" >> place_mex.mki
echo "LDOPTIMFLAGS=$LDOPTIMFLAGS" >> place_mex.mki
echo "LDDEBUGFLAGS=$LDDEBUGFLAGS" >> place_mex.mki
echo "Arch=$Arch" >> place_mex.mki
echo OMPFLAGS= >> place_mex.mki
echo OMPLINKFLAGS= >> place_mex.mki
echo "EMC_COMPILER=" >> place_mex.mki
echo "EMC_CONFIG=optim" >> place_mex.mki
"/usr/local/MATLAB/R2013b/bin/glnxa64/gmake" -B -f place_mex.mk
