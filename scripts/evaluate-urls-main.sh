#!/bin/bash

# Runs evaluate-urls.py on a set of url files in an input directory. 
# This way the evaluation can be continued from the last crashed run
# instead of re-running the whole process.
#
#
# Usage: ./evaluate-urls-main evdfile.db mals-indir/ mals-outdir/ mals-logdir/
#
#	Sample url files content:
#	
#		mals-indir/file1:
#			malicious("http://j.mp/1UuRSQV")
#		mals-indir/file2:
#			malicious("http://j.mp/ACa3Cf")
#			malicious("http://j.mp/FamousAF")
#	

EVDB=$1
EVDFILE=$EVDB".malEvdOnly.db"
INDIR=$2
OTDIR=$3
LGDIR=$4
echo Input Dir: $INDIR
echo Output Dir: $OTDIR
echo Log Dir: $LGDIR

mkdir -p $OTDIR
mkdir -p $LGDIR

echo "Exctracting malicious evidence from: "$EVDB
grep ^malicious $EVDB > $EVDFILE


FILES=$INDIR/*

for F in $FILES
do
	FNAME=`basename $F`
	date +"%c"  
	echo "Processing "$FNAME
	./evaluate-urls.py $EVDFILE $F > $OTDIR/$FNAME.out 2> $LGDIR/$FNAME.log
done

rm $EVDFILE

exit 0

