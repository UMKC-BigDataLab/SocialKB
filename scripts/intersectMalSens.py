#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 15, 2016
#
# Usage ./intersectMalSens.py  query_results input_db tureMalSens_list
# 
#	Checks which 'isPossiblySensitive' and 'malicious' predictes from query_results
#	exist in input_db. It also checks which predicates are originally labeled as
#	either 'malicious' or 'isPossiblySensitive' by Twitter and urlblacklist.
#
#
#

import sys, getopt
import json

def getMalSensPredictes(filename):
	mal_set = set()
	sen_set = set()
	f = open(filename)
	for line in f:
		if 'malicious' in line:
			if '\t' in line:
				mal_set.add(line.split('\t')[1].strip())
			else:
				mal_set.add(line.strip())
		elif  'isPossiblySensitive' in line:
			if '\t' in line:
				sen_set.add(line.split('\t')[1].strip())
			else:
				sen_set.add(line.strip())
	f.close()
	return mal_set,sen_set
		
def eprint(obj):
    sys.stderr.write(obj+"\n")

def main(args):
	print ("Input files:")
	print ("L: "+args[0])
	print ("R: "+args[1])
	print ("T: "+args[2])

	eprint("Collecting predictes from: "+args[0]+" as L")
	left_mal,left_sen = getMalSensPredictes(args[0])	
	
	eprint("Collecting predictes from: "+args[1]+" as R")
	right_mal,right_sen = getMalSensPredictes(args[1])

	eprint("Collecting predictes from: "+args[2]+" as T")
	t_mal,t_sen = getMalSensPredictes(args[2])



	print("\nmalicious in L:		   "+str(len(left_mal)))
	print("malicious in R:		   "+str(len(right_mal)))
	print("malicious in T:		   "+str(len(t_mal)))

	left_I_right_mal = left_mal & right_mal
	print("malicious L ^ R: 	   "+str(len(left_I_right_mal)))

	left_S_right_mal = left_mal - right_mal
	lsr_mal_len = len(left_S_right_mal)
	print("malicious L - R: 	   "+str(lsr_mal_len))


	left_S_t_mal = left_mal - t_mal
	lst_mal_len = len(left_S_t_mal)

	print("malicious L - T: 	   "+str(lst_mal_len))

	left_I_t_mal = left_mal & t_mal
	lit_mal_len = len(left_I_t_mal)
	print("malicious L ^ T: 	   "+str(lit_mal_len))


	left_I_t_S_right_mal = (left_mal & t_mal) -  right_mal
	litsr_mal_len = len(left_I_t_S_right_mal)
	print("malicious (L ^ T) - R:	   "+str(litsr_mal_len ))


	if lsr_mal_len > 0:
		print("malicious items in L not in R:")
		for i in left_S_right_mal:
			print("	"+i)


	if lst_mal_len > 0:
		print("malicious items in L not in T:")
		for i in left_S_t_mal:
			print("	"+i)

        if lit_mal_len  > 0:
                print("malicious items in L and T:")
                for i in left_I_t_mal:
                        print("	"+i)	

        if litsr_mal_len > 0:
                print("malicious items in L and T not in R:")
                for i in left_I_t_S_right_mal:
                        print("	"+i)	




	print("\nisPossiblySensitive in L:  	 "+str(len(left_sen)))
	print("isPossiblySensitive in R:  	 "+str(len(right_sen)))
	print("isPossiblySensitive in T:  	 "+str(len(t_sen)))

	left_I_right_sen = left_sen & right_sen
	print("isPossiblySensitive L ^ R: 	 "+str(len(left_I_right_sen)))
 

	left_S_right_sen = left_sen - right_sen
	lsr_sen_len = len(left_S_right_sen)
	print("isPossiblySensitive L - R: 	 "+str(lsr_sen_len))


	left_S_t_sen = left_sen - t_sen
	lst_sen_len = len(left_S_t_sen)
	print("isPossiblySensitive L - T: 	 "+str(lst_sen_len))

	left_I_t_sen = left_sen & t_sen
	lit_sen_len = len(left_I_t_sen)
	print("isPossiblySensitive L ^ T: 	 "+str(lit_sen_len))

	left_I_t_S_right_sen = (left_sen & t_sen) - right_sen
	litsr_sen_len = len(left_I_t_S_right_sen)
	print("isPossiblySensitive (L ^ T) - R: "+str(litsr_sen_len))

	if lsr_sen_len > 0:
		print("isPossiblySensitive items in L not in R:")
		for i in left_S_right_sen:
			print("	"+i)

	if lst_sen_len > 0:
		print("isPossiblySensitive items in L not in T:")
		for i in left_S_t_sen:
			print("	"+i)

        if lit_sen_len  > 0:
                print("isPossiblySensitive items in L and T:")
                for i in left_I_t_sen:
                        print("	"+i)	
    
        if litsr_sen_len > 0:
                print("isPossiblySensitive items in L and T not in R:")
                for i in left_I_t_S_right_sen:
                        print("	"+i)	


	eprint("Finished.")

if __name__ == "__main__":
   main(sys.argv[1:])

