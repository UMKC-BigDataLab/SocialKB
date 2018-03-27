#!/bin/bash
# Anas Katib, July 8, 2016
#
# Script to run a set of weight learning, map and marginal inferencing experiments. 
#
# Usage: ./run-experiment.sh  <db_file> <exp_num> <bool_str>
#
# 
#
# Experiments:
#	1. weight learning, map and mariginal on the full evidence db.
#	2. map and mariginal on the evidence db with  50% malicious predicates removed.
#	3. map and mariginal on the evidence db with 100% malicious predicates removed.
#
#
# Excpects:
#	* Evidence Database fie: DB
#	* Experiment Number: XN
#
#
# Notes:
#	* check if tuffy-cmd.sh conditions are satisfied.
#	* bool_str is a string of length 3 where each character is either 1 or 0
#	  and the character index corresponds to an experiment.
#	  For example, the string 011 means that only the 2nd and 3rd experiments will 
#	  be executed.



if [ $( expr length $3 ) -ne 3 ] ; then
	echo 'boolean string error!'
	exit 0
fi

DB=$1
XN=$2
BS=$3
DBDIR=$( dirname $DB )
DBNAME=$(echo `basename  $DB` |  sed 's/db//g')

scripts="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
tuffy=$scripts/tuffy-cmd.sh

REPO=$( dirname $scripts )

if [  ${BS:0:1} -eq 1 ] ; then
	echo 'Step 1: weight lerning, map and mariginal on full evidence..'
	date +"%c"
	$tuffy -c lrnwt -db $DB -x $XN -s 4 -it 20
	date +"%c"
	$tuffy -c map -db $DB -x $XN
	date +"%c"
	$tuffy -c mar -db $DB -x $XN

	echo 'Getting relevant evidence for prob. 1.0000 attackers..'
	date +"%c"
	# extract attackers with probability 1.0000
	$scripts/p1-attackers.sh $REPO/output/$XN/mar.infr.$DBNAME$XN.out.txt > tmp-p1.txt

	# get relevant evidence for those attackers
	$scripts/relevant-evidence.py tmp-p1.txt $DB $REPO/output/$XN/mar.infr.$DBNAME$XN.p1.attackers-evidence.json > $REPO/output/$XN/mar.infr.$DBNAME$XN.p1.attackers-evidence.txt
	rm tmp-p1.txt

	# get malicious and isPossiblySensitive details
	echo 'Finding intersections..'
	date +"%c"
	$scripts/intersectMalSens.py  $REPO/output/$XN/map.infr.$DBNAME$XN.out.txt $DB $REPO/true-malSen-list.txt > $REPO/output/$XN/map.infr.$DBNAME$XN.malSens-intersect.txt
	$scripts/intersectMalSens.py  $REPO/output/$XN/mar.infr.$DBNAME$XN.out.txt $DB $REPO/true-malSen-list.txt > $REPO/output/$XN/mar.infr.$DBNAME$XN.malSens-intersect.txt

	echo 'Organizing directories..'
	# move ALL FILES to 0p/
	mkdir -p $REPO/output/$XN/0p
	mkdir -p $REPO/log/$XN/0p
	mv $REPO/output/$XN/*$DBNAME$XN* $REPO/output/$XN/0p/
	mv $REPO/log/$XN/*$DBNAME$XN* $REPO/log/$XN/0p/
fi

if [  ${BS:1:1} -eq 1 ] ; then
	echo 'Step 2: map and mariginal with 50% malicious removed from evidence..'
	mkdir -p $REPO/output/$XN/50p
	mkdir -p $REPO/log/$XN/50p

	# remove 50% malicious
	DB50=$DBDIR/$DBNAME'50mal.db'
	
	$scripts/rm-pred.py $DB malicious 50 > $DB50

	# run map and mar inference 
	date +"%c"
	$tuffy -c map -db $DB50 -x $XN
	date +"%c"
	$tuffy -c mar -db $DB50 -x $XN

	# extract attackers with probability 1.0000
        $scripts/p1-attackers.sh $REPO/output/$XN/mar.infr.$DBNAME'50mal'.$XN.out.txt > tmp-p1.txt

        # get relevant evidence for those attackers
        $scripts/relevant-evidence.py tmp-p1.txt $DB50 $REPO/output/$XN/50p/mar.infr.$DBNAME'50mal'.$XN.p1.attackers-evidence.json > $REPO/output/$XN/50p/mar.infr.$DBNAME'50mal'.$XN.p1.attackers-evidence.txt
        rm tmp-p1.txt

        # get malicious and isPossiblySensitive details
        echo 'Finding intersections..'
        date +"%c"
        $scripts/intersectMalSens.py  $REPO/output/$XN/map.infr.$DBNAME'50mal'.$XN.out.txt $DB50 $REPO/true-malSen-list.txt > $REPO/output/$XN/50p/map.infr.$DBNAME'50mal'.$XN.malSens-intersect.txt
        $scripts/intersectMalSens.py  $REPO/output/$XN/mar.infr.$DBNAME'50mal'.$XN.out.txt $DB50 $REPO/true-malSen-list.txt > $REPO/output/$XN/50p/mar.infr.$DBNAME'50mal'.$XN.malSens-intersect.txt

	echo 'Organizing directories..(Step 2)'
	mv $REPO/output/$XN/*'50mal'* $REPO/output/$XN/50p/
	mv $REPO/log/$XN/*'50mal'* $REPO/log/$XN/50p/

fi

if [  ${BS:2:2} -eq 1 ] ; then
	echo 'Step 3: map and mariginal with 100% malicious removed from evidence..'
	mkdir -p $REPO/output/$XN/100p
	mkdir -p $REPO/log/$XN/100p


	# remove 100% malicious
	DB100=$DBDIR/$DBNAME'100mal.db'
	$scripts/rm-pred.py $DB malicious 100 > $DB100

	# run map and mar inference 
	date +"%c"
	$tuffy -c map -db $DB100 -x $XN
	date +"%c"
	$tuffy -c mar -db $DB100 -x $XN
	# extract attackers with probability 1.0000
        $scripts/p1-attackers.sh $REPO/output/$XN/mar.infr.$DBNAME'100mal'.$XN.out.txt > tmp-p1.txt

        # get relevant evidence for those attackers
        $scripts/relevant-evidence.py tmp-p1.txt $DB100 $REPO/output/$XN/100p/mar.infr.$DBNAME'100mal'.$XN.p1.attackers-evidence.json > $REPO/output/$XN/100p/mar.infr.$DBNAME'100mal'.$XN.p1.attackers-evidence.txt
        rm tmp-p1.txt

        # get malicious and isPossiblySensitive details
        echo 'Finding intersections..'
        date +"%c"
        $scripts/intersectMalSens.py  $REPO/output/$XN/map.infr.$DBNAME'100mal'.$XN.out.txt $DB100 $REPO/true-malSen-list.txt > $REPO/output/$XN/100p/map.infr.$DBNAME'100mal'.$XN.malSens-intersect.txt
        $scripts/intersectMalSens.py  $REPO/output/$XN/mar.infr.$DBNAME'100mal'.$XN.out.txt $DB100 $REPO/true-malSen-list.txt > $REPO/output/$XN/100p/mar.infr.$DBNAME'100mal'.$XN.malSens-intersect.txt

	echo 'Organizing directories..(Step 3)'
	mv $REPO/output/$XN/*'100mal'* $REPO/output/$XN/100p/
	mv $REPO/log/$XN/*'100mal'* $REPO/log/$XN/100p/
fi

