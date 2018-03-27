#!/bin/sh

#by Anas Katib
#runs the trends collection script and stores everything in one file without timestamps
#./trender,sh FULL_PATH_TO_TRENDER_DIR

TPATH=$1
prefix=$(date +%m%d%Y_%H%M)
$TPATH/twtTrend.py >> $TPATH/trends/trending.txt
sort $TPATH/trends/trending.txt | uniq > $TPATH/trends/$prefix.txt
mv $TPATH/trends/$prefix.txt $TPATH/trends/trending.txt

