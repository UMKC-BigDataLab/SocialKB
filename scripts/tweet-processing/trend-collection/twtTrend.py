#!/usr/bin/python
# -*- coding: utf-8 -*-

# Call twitter api to collect trending topics and hashtags.

import tweepy
import sys, getopt

def main(args):

    # // Anas Katib's Twitter keys
    consumer_key = "Q3"
    consumer_secret = "ohqD"
    access_token = "MAR"
    access_token_secret = "CV"

    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)


    trends1 = api.trends_place(1)
    trends = set([trend['name'] for trend in trends1[0]['trends']])
    for t in trends:
        print t.encode('utf-8').strip()


if __name__ == "__main__":
   main(sys.argv[1:])

