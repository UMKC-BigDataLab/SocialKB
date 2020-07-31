#!/bin/bash

# Config Variables.
CONSUMER_KEY=woXMpqi4UT3BIIlLjIbBQ7yEX
CONSUMER_SECRET=2z5eL2hQ5CgG6ampBmpPINT4Fu9mzyoIXDvCbOdsiLlgeIgHYw
ACCESS_TOKEN=1269650848864321537-bITb3jsYvcuUUOqYnHHpGe8aY10Q0O
ACCESS_TOKEN_SECRET=E1tGXGnMYozoanulZN23w3aB1DR9rXRUtadYAPn28s89z
NUM_TO_COLLECT=10

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




