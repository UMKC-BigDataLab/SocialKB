#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib Oct 12, 2016
#
# Usage ./collect-tweets-by-ids.py ids_file
# 
#       Retrieves tweets associated with Twitter tweet ids.
#
#       Prints out the tweets to std.
#

import sys
import string
import json
import time

from twython import Twython

# Anas Katib's Twitter keys
consumerKey = "Q3YvTFGaa77Qaa4TMh6JDE207"
consumerSecret = "oh9wcxkey3gp6oeEdC3NOIQBkh43EoSv3kpIfRqnVn0fBBerqD"
accessToken = "194674174-uhVbXvRYDJaBVNXw2uMxpWpmawMxcbSKYkV2wMAR"
accessTokenSecret = "CBf7yct8fgJqBMzLZaitqYA1AwdGXFMhEzrscMkI6KyUV"

def printerr(arg):
	sys.stderr.write(arg) 
def main(args):
	t = Twython(app_key=consumerKey, app_secret=consumerSecret,oauth_token=accessToken,oauth_token_secret=accessTokenSecret)
	tids = [line.rstrip('\n') for line in open(args[0],"r")]
	n = len(tids)
	s = 0 # start index for tids
	e = 100 # end index fot tids
	r = 0 # received response counter
	requests = 0 # sent requests counter
	done = False
	while (done == False):
		if (e > n): # if end > size 
			e = n-1	
		results = t.lookup_status(id=tids[s:e]) # request lookup for tids[s to e]
		requests += 1
		for tweet in results:
			print json.dumps(tweet)
			r += 1
		# advance lookup indexes
		s += 100
		e += 100
		
		# wait before sending next request
		time.sleep(5)

		if (s >= n):
			done = True
		# if reached request limit (i.e. 180): sleep 
		elif (requests == 180):
			requests = 0
			printerr("Sleeping: ["+str(s)+","+str(e)+"]\n")
			time.sleep(1000)

	printerr("Asked: "+str(n)+"\n")
	printerr("Received: "+str(r)+"\n")
	
if __name__ == "__main__":
   main(sys.argv[1:])
