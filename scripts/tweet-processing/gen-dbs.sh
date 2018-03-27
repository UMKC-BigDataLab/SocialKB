#!/bin/bash

# Generate evidance datasets by processing tweets stored in multiple directories inside input directory (e.g. tweets-dir/)
# Usage: ./gen-dbs.sh tweets-dir/ evd-dbs-out/  [> gen-dbs.log]
#
#	Example: 
#	INPUT:
#	   tweets-dir/
#		tweets-dir/1/tweets1.txt
#		tweets-dir/1/tweets2.txt
#		tweets-dir/2/tweets1.txt
#
#	OUTPUT:
#	   evd-dbs-out/
#		evd-dbs-out/1/evidence.1.db
#		evd-dbs-out/1/evidence.2.db
#		evd-dbs-out/2/evidence.1.db
#
#
#	NOTES:
#	   Output must be combined into one file to be used in Tuffy.
#

echo Input Dir: $1
echo Output Dir: $2
echo Output file name format:  evidence.*.db 
mkdir -p $2
DIRS=$1/*

for F in $DIRS
do
   f=$( echo $F |  tr '/' '\n' | tail -1)
   echo $F '>>>>>'
   java -Xmx70g -Xms1g -XX:MaxPermSize=1g -XX:ReservedCodeCacheSize=2g  -jar ProcTweets/GenerateEvd.jar  $F BLKLSTS/domains.txt BLKLSTS/urls.txt $2/evidence.$f.db true
done

exit 0

