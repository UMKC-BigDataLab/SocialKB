#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib Aug 1, 2016
#
# Usage ./update-relevant-evidence.py <evidince.json> <positiveMals.txt>
# 
#	Reads a json file of attackers evidence. Then for every link an attacker
#	has tweeted if the link is not lableld as malicious and it is considered
#	as so in positiveMals.txt, insert a malicious predicate for the link in
#	the json element.
#

import sys
import json
from sets import Set
from dateutil.parser import parse
###############
# Ref: http://stackoverflow.com/questions/3368969/find-string-between-two-substrings
# By: cji
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False


###############
def main(args):
	
	# read json string
    	evd_f = open(args[0])
    	evidence = json.load(evd_f)
    	evd_f.close()
 	
	# read true postives
	malicious = []
    	pos_f = open(args[1])
	for line in pos_f:
		line = line.split("\t")
		if is_date(line[0]):# if line contains a record
			if (int(line[1][0])> 0):# if record is true positive
				address = line[3].strip()
				malicious.append(address)
	pos_f.close()
	malicious = Set(malicious)
	inserts = 0
	only_malicious = 0
	only_sensitive = 0
	both = 0
	nither = 0
	num_attackers = 0
	for key in evidence:
		print key
		num_attackers += 1
		sen_count  =  0
		mal_count  =  0
		mals  = []
		links = []
		for pred in evidence[key]:
			
			print "\t"+pred.encode('utf-8')
			if   'containsLink' in pred:
				links.append(pred.split(",")[1].strip()[1:-2])
			elif 'isPossiblySensitive' in pred:
				sen_count += 1
			elif 'malicious'in pred:
				mal_count += 1
				mals.append(pred.split("(")[1].strip()[1:-2])

		for link in links:
			if link not in mals:
				if link in malicious:
					# newly discovered malicious
					inserts += 1
					mal_count += 1
					m = "malicious("+link+")"
					print "\t"+m
					evidence[key].append(m)
					mals.append(link)

		ns = "sensitivesCount("+str(sen_count)+")"
		nm = "maliciousCount("+str(mal_count)+")"		
		evidence[key].append(ns)
		evidence[key].append(nm)
		
		print "\t"+ns
		print "\t"+nm
		if sen_count  == 0 and mal_count > 0:
			only_malicious += 1
		elif mal_count  == 0 and sen_count > 0:
			only_sensitive += 1
		elif mal_count  > 0 and sen_count > 0: 
			both += 1
		elif mal_count  == 0 and sen_count == 0:
			nither += 1
	
        j = open(args[2],'w+')
        j.write(json.dumps(evidence))
        j.close()



	print "\nTOTAL ATTACKERS:         "+str(num_attackers)
	print "NEW MALICIOUS PREDICATES:"+str(inserts)
	print "\nATTACKERS PREDICATE DISTRIBUTION: "
	print "ONLY MALICIOUS:   "+str(only_malicious)
	print "ONLY SENSITIVE:   "+str(only_sensitive)
	print "BOTH:             "+str(both)
	print "NITHER:           "+str(nither)

if __name__ == "__main__":
   main(sys.argv[1:])

