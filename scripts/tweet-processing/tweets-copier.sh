#!/bin/bash
# Anas Katib
#
# Copy a supplied number <soft_limit_int> of tweets from subdirectories inside 
# an input directory to an output directory. The intention is to extarct a 
# subset of tweets from a much larger set. The tweets in the output directory
# are copied in groups of at most 5k per output subdirectory.
#
# Example:
#
#   ./tweets-copier.sh  15000 /in_dir /out_dir
# 
#   in_dir/
#       in_dir/111/part-xxa (has 4k tweets)
#       in_dir/222/part-xxb (has 1k tweets)
#       in_dir/333/part-xxc (has 10 tweets)
#
#   out_dir/
#       out_dir/1/part-xxa
#       out_dir/1/part-xxb
#       out_dir/2/part-xxc1
#       out_dir/3/part-xxc2
#       -------------------------------------------------
#       out_dir/1 now has 5k tweets
#       out_dir/2 now has 5k tweets
#       out_dir/3 now has 5k tweets
#
# Notes: 
#
# * it is possible that the output directory has a little over the specified number
#   <soft_limit_int>. If a the additional numeber of tweets is not need you have to 
#   manually from the output files.

if [ "$#" -ne 3 ]; then
    echo "Usage: ./tweets-copier.sh  <soft_limit_int> </in_dir> </out_dir>"
    exit 0
fi

errcho() { echo "$@" 1>&2; }

MX=$1
INDIR=$2
OTDIR=$3

errcho "Number of lines to copy (soft limit):" $MX
errcho "Input directory:" $INDIR

errcho "copying tweets in all 'part-*' files.."$'\n'


d=0
lines=0
fk=5001
for file in $INDIR/*/part-*; do
    echo $file
    if [ $fk -ge 5000 ]; then        
            # make a new dir to store 5k tweets
            d=$(($d+1))
            mkdir -p $OTDIR/$d
            fk=0
    fi

    count=$(grep ^'{"createdAt"' $file  | wc -l)
    lines=$(($count+$lines))
    fk=$(($fk+$count))
    dirn="$(basename "$(dirname "$file")")"
    dirn=$(echo $dirn | cut -d_ -f2)
    dstpfix=$(sed 's#.*/\([^:]*\).*#\1#' <<< $file)
    dstpfix=$(echo $dstpfix | cut -d- -f2)
    dstfile="part-"$dirn$dstpfix
    cp $file $OTDIR/$d/$dstfile
    if [[ $lines -gt $MX ]];then
        errcho $'\n''TOTAL LINES ' $lines
        errcho 'LAST FILE ' $file
        exit 1
    fi
done

errcho 'TOTAL LINES ' $lines
