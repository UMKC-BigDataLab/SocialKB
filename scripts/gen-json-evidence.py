#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib Nov 20, 2016
#
# Usage ./gen-json-evidence.py  evidence_file tweets_dir/ > output.json 
# Reads tweets from an input directory and generate json evidence for every tweet.
# The evidence file is used to get the malicious urls. 
#
# To-Do:
#	* include trending hashtags.
#
# malicious		(link)
# verified		(user)
# friend		(user1,user2)
# isFollowedBy		(user1,user2)
# mentions		(tweet,user)
# retweeted		(user,tweet)
# tweeted		(user,tweet)
# isPossiblySensitive 	(tweet)
# containsHashtag 	(tweet,hashtag)
# containsLink		(tweet,link)
# followersCount	(user,count)
# friendsCount		(user,count)
# retweetCount		(tweet,count)
# favouritesCount 	(tweet,count)
# statusesCount		(user,count)
# trending		(hashtag)	NOT INCLUDED
#
#	Output Example:
#	 
#
#	[
#	 { 	tweetId:tweet11, userId:user11, verified:false, isPossiblySensitive:true, mentions:[],
#		containsLink:[], containsHashtag:[], malicious:[],
#		followersCount:"n", friendsCount:"n", favouritesCount:"n",
#		statusesCount:"n", retweeted:tweet12, retweetCount:"n" 
#	 },
#	 { 	tweetId:tweet12, userId:user12, verified:"", isPossiblySensitive:"", mentions:[],
#		containsLink:[], containsHashtag:[], malicious:[],
#		followersCount:"", friendsCount:"", favouritesCount:"",
#		statusesCount:"", retweeted:"", retweetCount:"recount12" 
#	 }  
#	]
#


import sys, getopt, os
import json
import glob

def eprint(obj):
    sys.stderr.write(obj+"\n")

def getJPredicates(tweet):
	user = tweet["user"]
	job = {"tweetId":tweet["id"], "isPossiblySensitive":tweet["isPossiblySensitive"], "retweetCount":tweet["retweetCount"] }

	job["malicious"]=[]	

	job["friend"]=[]	
	job["isFollowedBy"]=[]	

	job["containsLink"]=[]	
	for url in tweet["urlEntities"]:
		job["containsLink"].append(url["expandedURL"])
 
	job["containsHashtag"]=[]	
	for hashtag in tweet["hashtagEntities"]:
		job["containsHashtag"].append(hashtag["text"])
 
	job["mentions"]=[]	
	for mention in tweet["userMentionEntities"]:
		job["mentions"].append(mention["id"])
 
	job["userId"] = user["id"]
	job["verified"] = user["isVerified"]
	job["followersCount"] = user["followersCount"]
	job["friendsCount"] = user["friendsCount"] 
	job["favouritesCount"] = user["favouritesCount"]
	job["statusesCount"] = user["statusesCount"]
	job["retweeted"] = "0"
	
	rjob = {}
	if "retweetedStatus" in tweet.keys():
		in_tweet = tweet["retweetedStatus"]
		job["retweeted"] = in_tweet["id"]
		job["retweetCount"] = in_tweet["retweetCount"]

		rjob["tweetId"] = in_tweet["id"]
		rjob["userId"] =  in_tweet["user"]["id"]
		rjob["retweetCount"] = in_tweet["retweetCount"]
		
		# add other empty keys:
		for k in job.keys():
			if k not in rjob.keys():
				rjob[k] = ""

	return job,rjob

 
def  getPredicteTokens(record):
	tokens = record.split('(')[1].split(')')[0].strip()
	if ',' in tokens:
		tokens = tokens.split(',')
		tokens[0] = tokens[0].strip()
		tokens[1] =  tokens[1].strip()
		return tokens
	return [tokens]
	


def main(args):

	# get malicious links
	malLinks = []
	friends = {}
	followers = {}

	evdf = open(args[0],"r")
	eprint("Reading evidence file:" + args[0])
	
 	for line in evdf:
                if line.startswith('malicious'):
                        malLinks.append(getPredicteTokens(line)[0][1:-1])
                elif line.startswith('friend('):
                        users = getPredicteTokens(line)
                        if users[0] not in friends:
                                friends[users[0]] = [users[1]]
                        else:
                                friends[users[0]].append(users[1])
                elif line.startswith('isFollowedBy'):
                        users = getPredicteTokens(line)
                        if users[0] not in followers:
                                followers[users[0]] = [users[1]]
                        else:
                                followers[users[0]].append(users[1])

	eprint("Found "+str(len(malLinks))+" malicious links")
	tdir = args[1]
	# generate a json object for every tweet
	eprint("Opening Tweets Dir:" + tdir)
	print "[",
	for filename in glob.iglob(os.path.join(tdir, '*', 'part-*')):
    		with open(filename) as f:
			for line in f:
				tweet = json.loads(line)
				jobs = getJPredicates(tweet)

				# check if links are malicious
				tweetLinks = jobs[0]["containsLink"]
				for link in tweetLinks:
					if link in malLinks:
						jobs[0]["malicious"].append(link)

				if jobs[0]["verified"]: # add friends and followers
					userId = str(jobs[0]["userId"])
					try:
						jobs[0]["friend"] = friends[userId]
					except KeyError as kErr:
						eprint("No friends for: "+userId)
					try:
						jobs[0]["isFollowedBy"] = followers[userId]
					except KeyError as kErr:
						eprint("No followers for: "+userId)

				# print tweeted and retweeted tweeets
				print(json.dumps(jobs[0]))
				print ",",
				if len(jobs[1]) > 0:
					print(json.dumps(jobs[1]))
					print ",",
			f.close()
	print("]")

	eprint("Done.")

if __name__ == "__main__":
   main(sys.argv[1:])

