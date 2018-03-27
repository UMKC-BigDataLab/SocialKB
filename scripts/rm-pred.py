#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 26, 2016
#
# Usage ./rm-pred.py <file> <predicate> <removal_percentage>
# 
#	Reads an input file and outputs the file after removing the specified 
#	percentage of the supplied predicate.
#
#	Expects:
#	* one predicate
#	* 0 <= removal_percentage:integer <= 100
#
#



import sys, getopt
from random import shuffle

def main(args):
   	filename  = args[0]
	predicate = args[1]
	percentage = int(args[2])

	if percentage < 0 or percentage > 100:
		print "Percentage Error: expected 0 <=  p <= 100"
		return 0

	preds = []
	f = open(filename)
    	for line in f:
		if line.startswith(predicate):
			preds.append(line.strip())	
		else:
			print line,
    	f.close()

	plen = len(preds)
	shuffle(preds)
	rmc = plen * percentage / 100
	#print "Removing "+str(percentage)+"% of "+str(plen)+" (i.e. "+str(rmc)+")"
	for p in range(plen-rmc):
		print preds[p]

if __name__ == "__main__":
   main(sys.argv[1:])

