#!/bin/bash

# Anas Katib, July 8, 2016
#
# Script to run Tuffy commands: Weight Learning, MAP Inference, Marginal Inference 
#
#
# Notes:
#	* Path to tuffy.jar is hard-coded. Must be set in the script before 
#	  execution.
#	* tuffy.conf must be in the script's directory.
#
#
# Excpects:
#	* Command to be executed: 'lrnwt', 'map', 'mar'
#	* Evidence Database fie: DB
#	* Experiment Number: XN
#	* Three directories: input/, output/, log/
#		+ the input/ direcoty has an XN/ directory with the following files:
#			- query-file /input/XN/query.XN.db  
#			- program-file /input/XN/prog.XN.mln
#		+ for the Inferencing commands an additional file is expected
#			- program-file /input/XN/lrnt.prog.XN.mln
#		
#
#
#

tuffy_path=/mnt/cs2/postgres/tuffy
scriptname=$0

function usage {
    echo "USAGE: $scriptname -c <cmd> -db <evidence.db> -x <experiment_id> [-s <num_samples> -it <num_iterations>]"
    echo "  -c  <command> :  tuffy command to be executed: lrnwt, map, mar"
    echo "  -db <filename>:  evidence file, aka evidence.db"
    echo "  -x  <num_id>  :  experiment id to distinguish multiple runs"
    echo "  -s  <num>     :  number of samples used by MC-SAT (default 4)"
    echo "  -it <num>     :  max number of iterations for learning (defualt 20)"
    echo "  -h            :  print this message"
    echo ""
    exit 1
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
parentDIR="$(dirname "$DIR")"

XN=$RANDOM
smpl=4
itr=20
DBNAME="defualt"
MMem=23G # java max memory

function aparse {
while [[ $# > 0 ]] ; do
  case "$1" in
     -c)
      CMD=${2}
      shift
      ;;
     -db)
      DB=${2}
      DBNAME=$(echo `basename  $DB` |  sed 's/db//g')
      shift
      ;;
     -x)
      XN=${2}
      shift
      ;;
     -s)
      smpl=${2}
      shift
      ;;
     -it)
      itr=${2}
      shift
      ;;
      -h)
    	usage
      ;;
 
  esac
  shift
done
}


if [[ ($# -eq 0) || ( "$1" == "-h")  ]] ; then
    usage
    exit 1
fi

aparse "$@"


FTAG=$DBNAME$XN

if [ 1 -eq 0 ]; then
	echo CMD  $CMD
	echo DB $DB
	echo XN $XN
	echo NAME $DBNAME
	echo FTAG $FTAG
	echo S $smpl
	echo IT $itr
	
	exit 1
fi



# create output and log dirs for this experiment
mkdir -p $parentDIR/output/$XN
mkdir -p $parentDIR/log/$XN

if [ $CMD == "lrnwt" ]; then
	echo 'Learning Weights..'
	/usr/bin/time -v java  -Xmx$MMem -jar $tuffy_path/tuffy.jar -learnwt -i $parentDIR/input/$XN/prog.$XN.mln -e $DB -queryFile $parentDIR/input/$XN/query.$XN.db -r $parentDIR/output/$XN/lrnwt.$FTAG.out.txt -mcsatSamples $smpl -dMaxIter $itr > $parentDIR/log/$XN/lrnwt.$FTAG.log.txt 2>&1
	echo 'Done.'

	echo 'Parsing learned weights..'
	$parentDIR/scripts/parse-lrnt-rules.py $parentDIR/output/$XN/lrnwt.$FTAG.out.txt > $parentDIR/input/$XN/lrnt.prog.$XN.mln

elif [ $CMD == "map" ]; then
	echo 'MAP Inference..'
	/usr/bin/time -v java -Xmx$MMem  -jar  $tuffy_path/tuffy.jar -i $parentDIR/input/$XN/lrnt.prog.$XN.mln -e $DB -queryFile $parentDIR/input/$XN/query.$XN.db -r $parentDIR/output/$XN/map.infr.$FTAG.out.txt  > $parentDIR/log/$XN/map.infr.$FTAG.log.txt 2>&1
	echo 'Done.'

elif [ $CMD == "mar" ]; then
	echo 'Marginal Inference..'
	/usr/bin/time -v java -Xmx$MMem -jar  $tuffy_path/tuffy.jar -marginal -i $parentDIR/input/$XN/lrnt.prog.$XN.mln -e $DB -queryFile $parentDIR/input/$XN/query.$XN.db -r $parentDIR/output/$XN/mar.infr.$FTAG.out.txt  > $parentDIR/log/$XN/mar.infr.$FTAG.log.txt 2>&1
	echo 'Done.'

fi

