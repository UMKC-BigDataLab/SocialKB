#!/bin/bash

# Config Variables.
CONSUMER_KEY=<CONSUMER_KEY>
CONSUMER_SECRET=<CONSUMER_SECRET>
ACCESS_TOKEN=<ACCESS_TOKEN>
ACCESS_TOKEN_SECRET=<ACCESS_TOKEN_SECRET>
NUM_TO_COLLECT=<NUM_TO_COLLECT>

# Constant Variables.
INTERVAL_IN_SECONDS=40
SOFT_LIMIT=10000
TWEETS_PARTS_DIR=$HOME/Tweets_Parts
TWEETS_OUTPUT_DIR=$HOME/Tweets_Output
EVIDENCE_DIR=$HOME/Evidence_Data

# Build CollectData.
cd ../CollectData && sbt clean assembly

# Collect tweets.
spark-submit --class edu.umkc.CollectTweets target/scala-2.11/CollectData-assembly-0.1.jar $TWEETS_PARTS_DIR $INTERVAL_IN_SECONDS $NUM_TO_COLLECT $CONSUMER_KEY $CONSUMER_SECRET $ACCESS_TOKEN $ACCESS_TOKEN_SECRET

#Consolidate collected tweets.
cd ../scripts/tweet-processing && ./tweets-copier.sh $SOFT_LIMIT $TWEETS_PARTS_DIR $TWEETS_OUTPUT_DIR

# Build BuildEvidence
cd ../../BuildEvidence && sbt clean assembly

# Construct the evidence
cd ../scripts/tweet-processing && bash gen-dbs.sh $TWEETS_OUTPUT_DIR $EVIDENCE_DIR $CONSUMER_KEY $CONSUMER_SECRET $ACCESS_TOKEN $ACCESS_TOKEN_SECRET




