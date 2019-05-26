#! /bin/bash
# Author: Izaak Neutelings (May 2018)
# Description: Run skimming postprocessor in NanoAOD and copy to PSI's T3 SE
#              Assume environment is set.

cat <<EOF


##########################################
###           SKIM BATCH JOB           ###
##########################################

EOF

# USER INPUT
YEAR="$1"
SAMPLE="$2"
INFILES="$3"
OUTDIR="$4"
TAG="_${TASKID}"
[ "$YEAR"    = "" ] && echo ">>> ERROR! Year is not given!" && exit 1
[ "$SAMPLE"  = "" ] && echo ">>> ERROR! Sample is not given!" && exit 1
[ "$INFILES" = "" ] && echo ">>> ERROR! Input files is not given!" && exit 1
[ "$OUTDIR"  = "" ] && echo ">>> ERROR! Output directory is not given!" && exit 1

# SETTINGS
DBG=2
SCRIPT="postprocessors/skim.py"
XROOTD="root://t3dcachedb.psi.ch:1094"
GFAL="gsiftp://t3se01.psi.ch"
SEHOME="/pnfs/psi.ch/cms/trivcat/store/user/$USER"
SERESULTDIR="$SEHOME/samples/NANOAOD_${YEAR}/$SAMPLE"
RESULTFILES="$OUTDIR/*${TAG}.root"
function peval { echo ">>> $@"; eval "$@"; }

# ENSURE RESULT DIRECTORY ON PSI T3 SE
peval "mkdir -p $OUTDIR"
[ ! -d $SERESULTDIR ] && peval "gfal-mkdir -p $GFAL/$SERESULTDIR" # always before cmsenv!
if [ ! -d $SERESULTDIR ]; then
    echo "ERROR: Failed to create resultdir on the SE ($SERESULTDIR)! Aborting..." >&2
    exit 1
fi

# MAIN FUNCTIONALITY
printf "\n# MAIN FUNCTIONALITY\n"
peval "python $SCRIPT -y $YEAR -i '$INFILES' -o $OUTDIR --tag $TAG"
peval "ls -hlt $OUTDIR"

# COPY RESULTS
printf "\n# COPY RESULTS\n"
if [[ ! -d $SERESULTDIR ]]; then
    echo ">>> $SERESULTDIR does not exist!"
fi
[ 0"$DBG" -gt 2 ] && debug="-v"
for outfile in "$RESULTFILES"; do
  if [ -e $outfile ]; then
    seoutfile=`basename $outfile`
    echo ">>> copying $outfile to $SERESULTDIR/$seoutfile"
    peval "xrdcp -d $DBG $debug --force $outfile $XROOTD/$SERESULTDIR/$seoutfile >&2"
    if test $? -ne 0; then
      echo "ERROR: Failed to copy $outfile to $SERESULTDIR/$seoutfile" >&2
    fi
  else
    echo ">>> outfile(s) $outfile does not exist in $OUTDIR!"
  fi
done

# CLEANING
printf "\n# CLEANING\n"
peval "rm $RESULTFILES"
