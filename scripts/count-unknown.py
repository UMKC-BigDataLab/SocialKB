#!/usr/bin/python

import sys, getopt

def main(argv):
    #preds=['attacker', 'malicious', 'verified', 'friend', 'isFollowedBy', 'mentions', 'retweeted', 'tweeted', 'isPossiblySensitive', 'containsHashtag', 'containsLink', 'followersCount', 'friendsCount', 'retweetCount', 'statusesCount', 'trending']

    nlines = 0
    tot = 0

    preds={'attacker':0, 'malicious':0, 'verified':0, 'friend':0, 'isFollowedBy':0, 'mentions':0, 'retweeted':0, 'tweeted':0, 'isPossiblySensitive':0, 'containsHashtag':0, 'containsLink':0, 'followersCount':0, 'friendsCount':0, 'retweetCount':0, 'statusesCount':0, 'trending':0}
    f = open(argv[0])
    for line in f:
        l = line.split('(')
        preds[l[0]]+=1
        nlines+=1
    f.close()

    print("There are "+str(nlines)+" lines")
    print("The Total is "+str(preds['attacker']+preds['malicious']+preds['verified']+preds['friend']+preds['isFollowedBy']+preds['mentions']+preds['retweeted']+preds['tweeted']+preds['isPossiblySensitive']+preds['containsHashtag']+preds['containsLink']+preds['followersCount']+preds['friendsCount']+preds['retweetCount']+preds['statusesCount']+preds['trending']))

    print preds['attacker']
    print preds['malicious']
    print preds['verified']
    print preds['friend']
    print preds['isFollowedBy']
    print preds['mentions']
    print preds['retweeted']
    print preds['tweeted']
    print preds['isPossiblySensitive']
    print preds['containsHashtag']
    print preds['containsLink']
    print preds['followersCount']
    print preds['friendsCount']
    print preds['retweetCount']
    print preds['statusesCount']
    print preds['trending'] 
 
    

if __name__ == "__main__":
    main(sys.argv[1:])
