/**
  * Created by raopr on 5/6/16.
  */

import com.google.gson.Gson
import org.apache.spark.streaming._
import org.apache.spark.streaming.twitter.TwitterUtils
import org.apache.spark.{SparkConf, SparkContext}
import twitter4j.TwitterFactory

object CollectTweets {
  private var gson = new Gson()
  private var numTweetsCollected = 0L
  var numTweetsToCollect = 0L

  def main(args: Array[String]) = {
    val conf = new SparkConf()
      .setMaster("local[2]")
      .setAppName("TweetCollector")
    val sc = new SparkContext(conf)

    //var args = Array("/home/anask/tweets","30","100")

    args.foreach(println)
    // args starts with 0 for the first argument
    if(args.length != 3) {
      println("Usage: " + "CollectTweets <output_dir> <interval_in_secs> <num_to_collect>")
      System.exit(0)
    }

    //val myFile = sc.textFile(args(0))
    //println("Number of lines in the file: " + myFile.count())
    numTweetsToCollect = args(2).toInt

    // Streaming part
    getTwitterData(sc, args(0), args(1).toInt)
    System.exit(0)
  }

  // Function to fetch tweets
  def getTwitterData(mySc: SparkContext, outputFile: String, intrv: Int): Any = {

    // Praveen's Twitter keys
    val consumerKey = "0cGZi"
    val consumerSecret = "awnBln"
    val accessToken = "xoWgsYD"
    val accessTokenSecret = "kuspIzJ"

    val config = new twitter4j.conf.ConfigurationBuilder()
      .setOAuthConsumerKey(consumerKey)
      .setOAuthConsumerSecret(consumerSecret)
      .setOAuthAccessToken(accessToken)
      .setOAuthAccessTokenSecret(accessTokenSecret)
      .build

    val ssc = new StreamingContext(mySc, Seconds(intrv))

    //val filter = Array("Trump", "baseball", "movies")

    val twitter_auth = new TwitterFactory(config)
    val a = new twitter4j.auth.OAuthAuthorization(config)

    val atwitter : Option[twitter4j.auth.Authorization] = Some(twitter_auth.getInstance(a).getAuthorization())

    val tweets = TwitterUtils.createStream(ssc, atwitter).map(gson.toJson(_))

    tweets.foreachRDD((rdd, time) => {
      val count = rdd.count()
      if (count > 0) {
        //val outputRDD = rdd.repartition(partitionsEachInterval)
        rdd.saveAsTextFile(outputFile + "/tweets_" + time.milliseconds.toString)

        numTweetsCollected += count
        if (numTweetsCollected > numTweetsToCollect) {
          println("Collected required number of tweets.")
          System.exit(0)
        }
      }
    })

    print("Collecting Twitter tweets via streaming APIs...")
    ssc.start()
    ssc.awaitTermination()
  }
}
