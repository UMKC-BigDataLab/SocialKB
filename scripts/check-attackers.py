#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 8, 2016
#
# Usage ./check-attackers.py file [-p1]
#
#	Retrieves a list of attacker ids from a Tuffy query output file
#	that contains the form attacker(usrid). Then checks if user's
#	Twitter account is still avalible using the twitter api.
#
#	The optional flag -p1 will only process attackers with
#	probabilty 1.0000 if found.
#

import tweepy
import sys, getopt
import logging
import requests

def getIds(filename,minp):

    f = open(filename)
    ids = []
    for line in f:
        l = line.split('(')
	if l[0] == 'attacker':
		ids.append(str.replace(l[1],")","").rstrip())

	else:
		l = line.split()
		if len(l) == 2:
			probability = float(l[0].strip())
			l=l[1].split('(')
			if l[0] == 'attacker' and probability >= minp:
				ids.append(str.replace(l[1],")","").rstrip())
    f.close()
    return ids

def lookup_ids(ids,api):
    users = api.lookup_users(user_ids = ids)
    f = 1
    for u in users:
    	ids.remove(str(u.id))
	f+=1

    return {'found':f-1, 'not_found':len(ids),'not_found_ids':ids}

def main(args):
    logging.getLogger('requests').setLevel(logging.CRITICAL)

    # // Anas Katib's Twitter keys
    consumer_key = "207"
    consumer_secret = "rqD"
    access_token = "MAR"
    access_token_secret = "CBUV"

    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    prob = 0.0000
    if(len(args)>1):
        try:
            prob = float(args[1].strip())
	    if prob < 0 or prob > 1:
            	print ("#EXPECTING NUMBER IN [0,1]")
		return 0

        except:
            print ("#UNKNOWN ARGUMENT: "+args[1]+" (NAN)")
            return 0

    #ids = ['611613851','714019054571429888','714698586','729000189743214593','729404139554353152','731807962763776000','733227591264546816']
    ids = getIds(args[0],prob)
    read_count =  len(ids)
    found_count = 0
    notfound_count = 0
    notfound_ids = []
    done = False

    while (done == False):
	if len(ids) > 100:
		proc_ids = ids[0:100]
		ids = ids[100:]
	else:
		proc_ids = ids
		done = True

    	totals = lookup_ids(proc_ids,api)
  	found_count    += totals['found']
    	notfound_count += totals['not_found']
    	notfound_ids   += totals['not_found_ids']

    print "#NOT FOUND IDs:"
    for i in notfound_ids:
	print i
    print "\n#TOTAL NOT FOUND:" + str(notfound_count)
    print "#TOTAL FOUND:" + str(found_count)
    print "#TOTAL:" + str(found_count+notfound_count)
    print "\n#TOTAL READ: "+ str(read_count)

if __name__ == "__main__":
   main(sys.argv[1:])

