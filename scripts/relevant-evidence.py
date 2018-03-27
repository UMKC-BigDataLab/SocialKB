#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 11, 2016
#
# Usage ./relevant-evidence.py ids_file evidence_file json_output_file
# 
#	Retrieves data related to a list of given user ids from an evidence file.
#	ids_file contains one id per line, lines staring with # will be ignored.
#
#	Prints out the details to std, and saves the results as a json object
#	to to an output file.
#

import sys, getopt
import logging
import requests
import json
import time

def eprint(obj):
    sys.stderr.write(obj+"\n")

def readIds(filename):
    eprint("Reading attackers ids file "+filename)
    f = open(filename)
    ids = {}
    for line in f:
	aid = line.strip()
	if line.startswith("#") == False and len(aid) > 0:
		ids[aid]={}
		#eprint ("ID:" + aid)
    f.close()
    return ids

def  getPredicteTokens(record):
	tokens = record.split('(')[-1].split(')')[0].strip()
	if ',' in tokens:
		tokens = tokens.split(',')
		tokens[0] = tokens[0].strip()
		tokens[1] =  tokens[1].strip()
		return tokens
	return [tokens]
	
def  getPredicateTweetId(line):
	tokens = getPredicteTokens(line)
	predicate = line.split("(")[0].strip()
	id = []
	if predicate in ["mentions" , "isPossiblySensitive" ,"retweetCount","containsHashtag","containsLink","favouritesCount"]:
		id.append(tokens[0])
	elif predicate in ["tweeted", "retweeted"]:
		id.append(tokens[1])
	elif predicate not in  ['verified' , 'trending','malicious', 'isFollowedBy','friend','followersCount','friendsCount','statusesCount']:
		eprint ("Assuming no user id in : "+line.strip("\n"))
	return id


def  getPredicateId(line):
	tokens = getPredicteTokens(line)
	predicate = line.split("(")[0].strip()
	id = []
	if predicate in ["verified", "tweeted", "retweeted", "followersCount","friendsCount","statusesCount"]:
		id.append(tokens[0])
	elif (predicate == "friend") or (predicate == "isFollowedBy"):
		id = tokens
	elif predicate == "mentions":
		id.append(tokens[1])
	elif predicate not in  ['favouritesCount', 'trending','containsLink','malicious','isPossiblySensitive', 'containsHashtag', 'retweetCount']:
		eprint ("Assuming no user id in : "+line.strip("\n"))
	return id

def getEvidence(ids,ev_filename):
	f = open(ev_filename)
	evidence = [] # hard evidence
	potential = [] # potential evidence
	tweetids = [] # hard evidence tweet ids 

	# potential evidence terms

	terms = ['favouritesCount', 'trending','containsLink','malicious','isPossiblySensitive', 'containsHashtag', 'retweetCount']
	eprint("Reading evidence file..")
    	for line in f:
		user_id = getPredicateId(line)
		found = False
    		# store direct user evidence
		if len(user_id) > 0:
			if user_id[0] in ids:
				found = True
			elif len(user_id) == 2 and found == False:
				if user_id[1] in ids:
					found = True
		   	if found:
				evidence.append(line.strip())
				if 'tweeted' in line:
					tweetids.append(line.split(",")[1].strip()[0:-1])
    		# store potential evidence
		if found == False:
			if any(t in line for t in terms):
				potential.append(line.strip())

	eprint("Refining potential evidence 1/2")
	# refine potential evidence
	links = []
	r = 0
	R = len(potential)

	while r < R:
		if 'malicious' not in potential[r]:
			id = getPredicateTweetId(potential[r])
			found = False
			if len(id) > 0:
				if id[0] in tweetids:
					found = True
				elif len(id) == 2:
					if id[1] in tweetids:
						found = True
				if found: # if id found, keep relevant data
					# get relevant links
					if 'containsLink' in potential[r]:
						link = potential[r].split(",")[1].strip()[0:-1]
						links.append(link)
					#if "favouritesCount" in  potential[r]:
					#	eprint  (potential[r])
			if found == False:# else remove non-relevant datai
				potential.remove(potential[r])
				r-=1
				R-=1
		r+=1
	#remove non-relevant malicious links
	eprint("Refining potential evidence 2/2")
	r = 0
	while r < R:
		if 'malicious' in potential[r]:
			if potential[r][10:-1] not in links:
				potential.remove(potential[r])
				r-=1
				R-=1
		r+=1

    	f.close()
    	return evidence + potential

def organizeEvidence(ids, evidence):
	eprint("Grouping evidence by user ids..")
	orgd_evidence = {}
	issued = {}
	mentioned = {}
	mal_links = []
	pending = []
	relations = {}
	for id in ids:
		orgd_evidence[id] = []
	for e in evidence:
                e_obj = e.split("(")
                pred = e_obj[0].strip()
                if pred in ['attacker','verified']:
                        uid = e_obj[1].strip()[0:-1]
                        try:
                                orgd_evidence[uid].append(e)
                        except KeyError:
                                eprint(uid + " not an attacker. Evidence: "+e)
                elif pred in ['statusesCount','followersCount','friendsCount']:
                        uid = e_obj[1].split(",")[0].strip()
                        try:
                                orgd_evidence[uid].append(e)
                        except KeyError:
                                eprint(uid + " not an attacker. Evidence: "+e)
		elif pred in ['friend','isFollowedBy']:
			uids = e_obj[1].split(",")
			uids[0] = uids[0].strip()
			uids[1] = uids[1].strip()[0:-1]
		
			u1 = u2 = False
			if uids[0] in ids:	
				orgd_evidence[uids[0]].append(e)
				if uids[1] in relations:
					relations[uids[1]].append(uids[0])
				else:
					relations[uids[1]]=[uids[0]]
				u1 = True

			if uids[1] in ids:
				orgd_evidence[uids[1]].append(e)
				if uids[0] in relations:
					relations[uids[0]].append(uids[1])
				else:
					relations[uids[0]]=[uids[1]]
				u2 = True

			if u1 == u2 == False: # process later:
				pending.append(e)
			
		elif pred in ['tweeted','retweeted']:
			usr_twt = e_obj[1].split(",")
			uid = usr_twt [0].strip()
			tid = usr_twt [1].strip()[0:-1]	
			orgd_evidence[uid].append(e)
			issued[tid] = uid
			

		elif pred in ['mentions']:
			usr_twt = e_obj[1].split(",")
			tid = usr_twt [0].strip()
			uid = usr_twt [1].strip()[0:-1]	
			#if attacker was mentioned
			if uid in ids:
				orgd_evidence[uid].append(e)
			#if attacker mentioned another user 
			#   set aside evidence and look for an attacker who issued the tweet later
			else:
				if tid not in mentioned:
					mentioned[tid]=[e]
				else:
					mentioned[tid].append(e)
		elif pred in ['malicious']:
			mal_links.append(e.strip()[10:-1])
		else: # delay processing to the end
			pending.append(e)

	# done, then:
	# process mentions:
	for t in mentioned: # mentioning tweets
		# if tweet was issued by an attacker
		if t in issued:
			# attach mentioned evidence to the attacker who issued the tweet
			for m in mentioned[t]:
				orgd_evidence[issued[t]].append(m)

		else:
			eprint("WARN: mention was not handled!")	
	                eprint("Evidence: " + str(mentioned[t]))
	# delayed processing
	for p in pending:
		evd = p.split("(")
                pred = evd[0].strip()
		if pred in ['isPossiblySensitive']:
			tid = evd[1].strip()[0:-1]
			orgd_evidence[issued[tid]].append(p)
		elif pred in ['containsHashtag','retweetCount','favouritesCount' ]:
			tid = evd[1].split(",")[0].strip()
			orgd_evidence[issued[tid]].append(p)
		elif pred in ['containsLink']:
			twt_link = evd[1].split(",")
			tid = twt_link[0].strip()
			link = twt_link[1].strip()[0:-1]
			orgd_evidence[issued[tid]].append(p)
			if link in mal_links:
				orgd_evidence[issued[tid]].append('malicious('+link+')')
		elif pred in ['verified']:
			uid = evd[1].strip()[0:-1]
			orgd_evidence[uid].append(p)

		elif pred in ['friend','isFollowedBy']:
			uids = evd[1].split(",")
			uid1 = uids[0].strip()
			uid2 = uids[1].strip()[0:-1]
			if uid1 in relations:
				for u in relations[uid1]:
					orgd_evidence[u].append(p)
			if uid2 in relations:
				for u in relations[uid2]:
					orgd_evidence[u].append(p)			
		else:
	                eprint("WARN: evidence not recognized!")
	                eprint("Evidence: " + p)

	return orgd_evidence
def detailed_print(users):
	for u in users:
		print (u)
		for e in users[u]:
			print ("\t"+(e))
	

def main(args):
    	logging.getLogger('requests').setLevel(logging.CRITICAL)
	start = time.time()	
	#ids = ['611613851','714019054571429888','714698586','729000189743214593','729404139554353152','731807962763776000','733227591264546816']
	ids = readIds(args[0])
	data = getEvidence(ids,args[1]) # not formated

	#print("Relevant Evidence:")
	#for d in data:
	#	print d

	users = organizeEvidence(ids,data) # format data

	eprint ("Saving JSON output to: "+args[2])	
	j = open(args[2],'w+')
	j.write(json.dumps(users))
	j.close()

	print("Relevant Evidence:")
	detailed_print(users)
	eprint("Done.")
	end = time.time()
	dur = float("{0:.2f}".format(end-start))
	eprint("Finished in: "+str(dur)+"s")
if __name__ == "__main__":
   main(sys.argv[1:])

