#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 25, 2016
#
# Usage ./parse-lrnt-rules.py <file>
# 
#	Retrieves a set of rules from the output of tuffy command "learnwieghts"
#	that contains the form attacker(usrid). Then checks if user's
#	Twitter account is still avalible using the twitter api.  
#
#	The optional flag -p1 will only process attackers with 
#	probabilty 1.0000 if found.
#

import sys, getopt

def main(args):
	start="AVERAGE WEIGHT OF ALL THE ITERATIONS"
	end="WEIGHT OF LAST ITERATION" 
	ignore = False
    	f = open(args[0])
    	for line in f:
		if (start in line):
			ignore = True

		elif (end in line):
			ignore = False

        	if (ignore == False):
			print line,
    	f.close()

if __name__ == "__main__":
   main(sys.argv[1:])

