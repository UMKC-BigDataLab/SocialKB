#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib Oct 18, 2016
#
# Usage ./process-rel-evd.py rel-evd-file.json
# 
#       Generate evidence indexed by tweet ids from evidence that is indexed by user ids
#
#       Prints out the tweets to std.
#

import sys
import json
import time

def  getPredicteTokens(record):
        tokens = record.split('(')[-1].split(')')[0].strip()
        if ',' in tokens:
                tokens = tokens.split(',')
                tokens[0] = tokens[0].strip()
                tokens[1] =  tokens[1].strip()
                return tokens
        return [tokens]

def printerr(arg):
	sys.stderr.write(arg) 
def main(args):
	with open(args[0],'r') as json_data:
		evd = json.load(json_data)		
		t_count = 0
		tweets = {}
		pending = []
		for uid in evd:
			raw_evd = evd[uid]
			others = []
			tweet = {}	
			t_count += 1
			printerr(str(t_count)+" ")
			for e in raw_evd:
				tokens = getPredicteTokens(e)
				if e.startswith("tweeted"):
					tweet[tokens[1]] =  {"isPossiblySensitive":False,"containsLink":[],"containsHashtag":[],"retweetCount":"","mentions":[],"verified":False , "followersCount":"" , "friendsCount":"" , "statusesCount":"","friends":[],"followers":[]}
				else:	
					others.append(e)
			
				for oe in others: # other evidence
					predicate = oe.split("(")[0].strip()
					tokens = getPredicteTokens(oe)

					if predicate in ["isPossiblySensitive","containsLink","containsHashtag","retweetCount","mentions","friend","isFollowedBy"]:
						tid = tokens[0]
						try :
							if predicate == "isPossiblySensitive":
								tweet[tid]["isPossiblySensitive"]= True
							elif  predicate == "retweetCount":
								tweet[tid]["retweetCount"] = tokens[1]
							elif  predicate in ["friend","isFollowedBy"]:
								uid1 = tokens[0]
								uid2 = tokens[1]
								//Stopped here, if frinds and followers are not needed discard changes
								//else continue working

							else:
								tweet[tid][predicate].append(tokens[1])
						except KeyError:
							pending.append(oe)

					elif predicate in ["verified","followersCount" , "friendsCount" , "statusesCount"]:
						for k in tweet.keys():
							if predicate == "verified":
								tweet[k]["verified"]=True
							else:
								tweet[k][predicate]=tokens[1]		
			for t in tweet:
				tweet[t]["userID"]=uid
				tweets[t] = tweet[t]
			printerr("Done.\n")
			#if (len(tweets) > 1):
			#	break
			
		printerr ("Processing pendings..\n")
		for p in pending:
			if p.startswith("mentions"):
				tokens = getPredicteTokens(p)
				tweets[tokens[0]]["mentions"].append(tokens[1])
			else:
				printerr("WARN: "+p)
		printerr ("Printing JSON..\n")
		print json.dumps(tweets)
		printerr ("Done.\n")
		
if __name__ == "__main__":
   main(sys.argv[1:])
