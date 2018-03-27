#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 15, 2016
#
# Usage ./countMalSens.py json_file
# 
#	Reads a json file of user objects each having an array of different predictes.
#	Meanwhile, counting the number of 'isPossiblySensitive' and 'malicious'
#	predicates for each user.
#
#
#	JSON INPUT: {123:[pred1,pred2],1421:[pred2,pred5]}
#

import sys, getopt
import json

def eprint(obj):
    sys.stderr.write(obj+"\n")

def main(args):
	eprint("Reading JSON file: "+args[0])
	jfile = open(args[0])
    	users = json.load(jfile)

	eprint("Counting sensitive and malicious..")
	s_count = m_count = none_count = both_count = 0
	n_users = 0
	for u in users:
		n_users += 1
		s_flag = m_flag = False
		for p in users[u]:
			if 'isPossiblySensitive' in p:
				s_count += 1
				s_flag = True
			elif 'malicious' in p:
				m_count += 1
				m_flag = True
		if s_flag == False and m_flag == False:
				none_count += 1
		elif s_flag == True and m_flag == True:
				both_count += 1

	eprint ("Done.")
	print ("Processed "+str(n_users)+" users.")
	print ("isPossiblySensitive: 	"+str(s_count))
	print ("malicious: 		"+str(m_count))
	print ("none: 			"+str(none_count))
	print ("both: 			"+str(both_count))

	eprint("Finished.")

if __name__ == "__main__":
   main(sys.argv[1:])

