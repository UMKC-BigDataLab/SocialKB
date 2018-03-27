#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib Aug 2, 2016
#
# ./prob-attackers.py <min_prob> <mar_infr_file>
#
#	Return the ids of those attackers with a minimum probabilty
# 	from an input file

import sys


def main(args):
	min_prob = float(args[0])
	mar_file = open(args[1])
	for line in mar_file:
		if 'isPossiblySensitive' in line:
			if float(line[0:6]) >= min_prob:
				attId = line.split("(")[1].strip().split(")")[0]
				print "isPossiblySensitive("+attId+")"
	mar_file.close()
if __name__ == "__main__":
   main(sys.argv[1:])

