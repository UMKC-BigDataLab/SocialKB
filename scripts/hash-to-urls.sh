#!/bin/bash

# Convert hash numbers to urls, expects two arguments a file that contains hashs
# and a tab separated map file.

hfile=$1
mfile=$2
echo 'Reading map from: '$mfile
echo 'Reading hashes from: '$hfile

for hcode in $(cat $hfile)
do

	if [ $hcode -eq $hcode ] 2>/dev/null; then #if a number
		#echo 'Mapping '$hcode
		if (( $hcode < 0 )); then #negative number must be escaped
			grep '\'$hcode $mfile | cut -d $'\t' -f2
		else		
			grep $hcode $mfile | cut -d $'\t' -f2
		fi
	fi
done
