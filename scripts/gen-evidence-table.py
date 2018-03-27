#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib Oct 15, 2016
#
# Usage ./gen-evidence-table evidence_file
#
# Create Logistic Regression table using evidence db.
#
# Table:
# 
# ------| type        malicious   tweetID   userID   linkHash   isVerified   isPossiblySensitive
# row0 	| train/test  true/false  str       str      int        true/false   true/false
# row1 	| train/test  true/false  str       str      int        true/false   true/false
# ...

import tweepy
import sys, getopt
import logging
import requests
import sys
import json

def eprint(obj):
    sys.stderr.write(obj+"\n")

def  getPredicteTokens(record):
	tokens = record.split('(',1)[-1].split(')',1)[0].strip()
	if ',' in tokens:
		tokens = tokens.split(',')
		tokens[0] = tokens[0].strip()
		tokens[1] =  tokens[1].strip()	
		if tokens[0].startswith('"') and tokens[0].endswith('"'):
			tokens[0] = tokens[0][1:-1]
		if tokens[1].startswith('"') and tokens[1].endswith('"'):
			tokens[1] = tokens[1][1:-1]

		return tokens
	else:
		if tokens.startswith('"') and tokens.endswith('"'):
                        tokens = tokens[1:-1]
	return [tokens]
	

def parseEvidence(ev_filename):
	f = open(ev_filename)

	#terms = {'malicious','verified','friend','isFollowedBy','mentions','retweeted','tweeted','isPossiblySensitive','containsHashtag','containsLink','followersCount','friendsCount','retweetCount','statusesCount'}
	terms = {'malicious':set(),'verified':set(),'tweeted':{},'isPossiblySensitive':set(),'containsLink':{}}
	#tweetID = {}
	#row = {'malicious':'na', 'verified':'na', 'tid':0, 'uid':0,'link':'na', 'sensitive':'na'} 
	for line in f:
		predicate = line.split('(',1)[0]
		if predicate in terms:
			tokens = getPredicteTokens(line)
			if predicate == 'tweeted':
				terms[predicate][tokens[1]]=tokens[0]  # TID -> UID
			elif predicate == 'containsLink':
				if tokens[0] not in terms[predicate].keys():
					terms[predicate][tokens[0]]=[tokens[1]]  # TID -> [URL]
				else:
					terms[predicate][tokens[0]].append(tokens[1])  # TID[] append URL_NEW
			else:
				terms[predicate].add(tokens[0])
	links = 0
	for t in terms:
		if t != 'containsLink':
			print t +' '+str(len(terms[t]))
		else:
			for tids in terms[t]:
				links += len(terms[t][tids])
			print t +' '+str(links)
				
	return terms

def createTable(data):
    #type	malicious	tweetID	userID	link	isVerified	isPossiblySensitive
    for tid in data['tweeted'].keys():
	uid = data['tweeted'][tid]

	if tid in data['containsLink'].keys():
		row = tid + '\t' + uid + '\t'
		rows = []
		# add urls
		for url in data['containsLink'][tid]:
			if url.split("//")[-1].split("/")[0] in ['t.co','twitter.com', 'pinterest.com', 'instagram.com' ,'youtube.com', 'flickr.com']:
				malicious = 'false'
			elif  url in data['malicious']:
				malicious = 'true'
			else:
				malicious = 'na'

			rtype = 'test'
			if malicious != 'na':
				rtype = 'train'
			hurl = str(hash(url))
			rows.append(str(rtype) + '\t' + str(malicious) + '\t' + row + hurl + '\t')
			eprint(hurl+'\t' + url)
		# add verified and isPosSen
		verified = sensitive = 'false'
		if uid in data['verified']:
			verified = 'true'
	
		if tid in data['isPossiblySensitive']:
			sensitive = 'true'
	
		for r in rows:
			r = r + str(verified) + '\t' + str(sensitive)
			print r

def main(args):
    	logging.getLogger('requests').setLevel(logging.CRITICAL)
	data = parseEvidence(args[0])
	print('type\tmalicious\ttweetID\tuserID\tlink\tisVerified\tisPossiblySensitive')
	createTable(data)


if __name__ == "__main__":
   main(sys.argv[1:])

