MATLAB="/usr/local/MATLAB/R2013b"
Arch=glnxa64
ENTRYPOINT=mexFunction
MAPFILE=$ENTRYPOINT'.map'
PREFDIR="/home/psecker/.matlab/R2013b"
OPTSFILE_NAME="./mexopts.sh"
. $OPTSFILE_NAME
COMPILER=$CC
. $OPTSFILE_NAME
echo "# Make settings for nextrot" > nextrot_mex.mki
echo "CC=$CC" >> nextrot_mex.mki
echo "CFLAGS=$CFLAGS" >> nextrot_mex.mki
echo "CLIBS=$CLIBS" >> nextrot_mex.mki
echo "COPTIMFLAGS=$COPTIMFLAGS" >> nextrot_mex.mki
echo "CDEBUGFLAGS=$CDEBUGFLAGS" >> nextrot_mex.mki
echo "CXX=$CXX" >> nextrot_mex.mki
echo "CXXFLAGS=$CXXFLAGS" >> nextrot_mex.mki
echo "CXXLIBS=$CXXLIBS" >> nextrot_mex.mki
echo "CXXOPTIMFLAGS=$CXXOPTIMFLAGS" >> nextrot_mex.mki
echo "CXXDEBUGFLAGS=$CXXDEBUGFLAGS" >> nextrot_mex.mki
echo "LD=$LD" >> nextrot_mex.mki
echo "LDFLAGS=$LDFLAGS" >> nextrot_mex.mki
echo "LDOPTIMFLAGS=$LDOPTIMFLAGS" >> nextrot_mex.mki
echo "LDDEBUGFLAGS=$LDDEBUGFLAGS" >> nextrot_mex.mki
echo "Arch=$Arch" >> nextrot_mex.mki
echo OMPFLAGS= >> nextrot_mex.mki
echo OMPLINKFLAGS= >> nextrot_mex.mki
echo "EMC_COMPILER=" >> nextrot_mex.mki
echo "EMC_CONFIG=optim" >> nextrot_mex.mki
"/usr/local/MATLAB/R2013b/bin/glnxa64/gmake" -B -f nextrot_mex.mk
