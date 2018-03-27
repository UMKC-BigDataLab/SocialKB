/**
  * Created by monica on 9/9/16.
  */
// Last Updated: May 1 2017
// Anas Katib anaskatib@mail.umkc.edu

// Generate evidence data for tweets. Needs blacklist urls and domain names.
// Evidence is written to output file.
//
//
// Usage: ProcessTweets <input_tweets_directory> <domains_file> <urls_file> <output_file> <col_rel_bool> {katib,rao}
//
//	  col_rel_bool: collect friend/follower lists (default: true)
//


//Generated:
//
// tweeted
// isPossiblySensitive
// statusesCount
// friendsCount
// followersCount
// verified
// friend         [disable for faster execution by seting col_rel_bool to false]
// isFollowedBy   [disable for faster execution by seting col_rel_bool to false]
// retweeted
// tweeted
// retweetCount
// containsLink
// mentions
// containsHashtag
// malicious

//Not Generated:
//      trending(hashtag)
//      attacker(user)

// Uses:
//    Java 1.7
//    Scala 2.11.8
//    com.google.code.gson:gson:2.6.2
//    org.apache.spark:spark-core_2.11:1.6.1
//    org.apache.spark:spark-hive_2.11:1.6.1
//    org.apache.spark:spark-sql_2.11:1.6.1
//    org.apache.spark:spark-streaming-twitter_2.11:1.3.1
//    org.apache.spark:spark-streaming_2.11:1.6.1

//Example jar run java parms: -Xmx70g -Xms1g -XX:MaxPermSize=1g -XX:ReservedCodeCacheSize=2g

import java.io.{BufferedWriter, File, FileWriter}

import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.SQLContext
import org.apache.spark.sql.functions._
import org.apache.spark.{SparkConf, SparkContext}
import twitter4j.conf.ConfigurationBuilder
import twitter4j.{IDs, Twitter, TwitterException, TwitterFactory}

import scala.collection.mutable.ListBuffer


object ProcessTweets {

  var bw: BufferedWriter = null

  //method to write predicates into evidence file
  def writeToOutput(predicate: String, param_1: Any, param_2: Any): Unit = {

    val output = predicate + "(" + param_1.toString + "," + param_2.toString + ")"
    bw.write(output + "\n")
    //println(output)

  }

  //method to write predicates into evidence file
  def writeToOutput(predicate: String, param: Any): Unit = {

    val output = predicate + "(" + param.toString + ")"
    bw.write(output + "\n")
    //println(output)
  }

  //Get the list of 'friends' or 'followers' for a twitter user
  // * sleeps if call limit is exceeded
  def getList(uid: Long, twitter: Twitter, listType: String): List[Long] = {

    println("\nGetting " + listType + " for User: " + uid)

    var statuses = null: IDs
    var remainingCalls = 0
    var waitTime = 0
    var cursor = -1.toLong  //why -1 ?
    var curCount = 0
    var folCount = 0
    var resetTime = 0.toLong
    var list = new ListBuffer[Long]

    while (cursor != 0.toLong) {    ////cursor for ?
      try {

        if (listType.equalsIgnoreCase("friends"))
          statuses = twitter.getFriendsIDs(uid, cursor)
        else if (listType.equalsIgnoreCase("followers"))
          statuses = twitter.getFollowersIDs(uid, cursor)

        else {
          println("\nError: getList, unidentified type " + listType)
          return null
        }

        var ids = null: Iterator[Long]
        try {
          remainingCalls = statuses.getRateLimitStatus.getRemaining
          waitTime = Math.abs(statuses.getRateLimitStatus.getSecondsUntilReset) + 20
          resetTime = statuses.getRateLimitStatus.getResetTimeInSeconds
          ids = statuses.getIDs.iterator
          curCount += 1
          while (ids.hasNext) {
            list.append(ids.next())
            folCount += 1

          }

          cursor = statuses.getNextCursor

        } catch {
          case e: NullPointerException => {
            remainingCalls = 0
            waitTime = 35
            resetTime = System.currentTimeMillis() + 30000
          }
        }

        if (remainingCalls == 0 && cursor != 0.toLong) {
          println("\nGoing to Sleep. Be back in " + waitTime + " seconds")
          Thread.sleep(waitTime * 1000)
          println("\nTime Now: " + System.currentTimeMillis() + " Reset in " + resetTime)

        }

      }
      catch {
        case e: TwitterException => {
          println("\nTwitter Exception! Proccessing User: " + uid)

          try {
            remainingCalls = e.getRateLimitStatus.getRemaining
            waitTime = Math.abs(e.getRateLimitStatus.getSecondsUntilReset) + 20
            resetTime = e.getRateLimitStatus.getResetTimeInSeconds

            val notfound = e.resourceNotFound()
            val ercode = e.getErrorCode()
            val stcode = e.getStatusCode()

            if(notfound == true && ercode == 34 && stcode == 404){
              println("User Not Found: "+e)
              return list.toList
            }


          }
          catch {
            case e: NullPointerException => {
              remainingCalls = 0
              waitTime = 35
              resetTime = System.currentTimeMillis() + 30000
            }
          }

          if (remainingCalls == 0) {
            println("\nCalls Limit Exception, going to Sleep. Be back in " + waitTime + " seconds")
            Thread.sleep(waitTime * 1000)
            println("\nTime Now: " + System.currentTimeMillis() + " Reset in " + resetTime)

          }
        }
      }

    }
    println("\nUser: " + uid + "  has " + folCount + "  " + listType)
    return list.toList
  }

  def main(args: Array[String]) = {


    Logger.getLogger("org").setLevel(Level.OFF)
    Logger.getLogger("akka").setLevel(Level.OFF)

    // Read command line arguments
    // Comment out Sys exit below if no argument will be passed
    if (args.length < 4) {
      println("Usage: ProcessTweets " + "<input_tweets_directory> " +
        "<domains_file> <urls_file> <output_file> <collect_rel_bool> {rao,katib}")
      System.exit(1)
    }

    val tweetsDir = args(0)
    val domainsFilename = args(1)
    val urlsFilename = args(2)
    val outputFilename = args(3)
    var collect_relationships = true
    var userToken = "katib"
    if (args.length > 4) {
      collect_relationships = args(4).toBoolean
      userToken = args(5)
    }

    if (userToken != "katib" || userToken != "rao"){
      println("Username options: katib or rao.")
      System.exit(1)
    }


    //val tweetsDir       = "/home/anask/20kTweets/x"
    //val domainsFilename = "/home/anask/BLKLSTS/domains.txt"
    //val urlsFilename    = "/home/anask/BLKLSTS/urls.txt"
    //val outputFilename  = "/home/anask/evidence/evidence.x.db"


    val file = new File(outputFilename)
    bw = new BufferedWriter(new FileWriter(file, true))


    println("Reading Tweets From: " + tweetsDir)
    println("Reading Domains From: " + domainsFilename)
    println("Reading URLs From: " + urlsFilename)
    println("Appending output to: " + outputFilename)


    val cb = new ConfigurationBuilder

    // Anas Katib's Twitter keys
    var consumerKey = "Q3207"
    var consumerSecret = "oh9Rq0fBBerqD"
    var accessToken = "1946741SKYkV2wMAR"
    var accessTokenSecret = "CBf7yct8fgJkI6KyUV"

    if (userToken == "rao") {
      // Praveen's Twitter keys
      consumerKey = "0csQhdfi"
      consumerSecret = "eNebBoOFCGzyawnBln"
      accessToken = "448605EKSVxoWgsYD"
      accessTokenSecret = "kusGXCMMXspIzJ"
    }


    cb.setDebugEnabled(true)
      .setOAuthConsumerKey(consumerKey)
      .setOAuthConsumerSecret(consumerSecret)
      .setOAuthAccessToken(accessToken)
      .setOAuthAccessTokenSecret(accessTokenSecret)
      .setUseSSL(true)

    val tf = new TwitterFactory(cb.build)
    val twt = tf.getInstance

    val conf = new SparkConf()
      .setMaster("local[*]")
      .setAppName("TweetProcessor")

    println("Memory:")
    println("   Tot: " + String.valueOf(sys.runtime.totalMemory() / 1073741824) + " gb")
    println("   Max: " + String.valueOf(sys.runtime.maxMemory() / 1073741824) + " gb")
    println("   Min: " + String.valueOf(sys.runtime.freeMemory() / 1073741824) + " gb")


    val sc = new SparkContext(conf)

    val t0 = System.nanoTime()


    //    val collectedTweets = sc.textFile("/home/anask/10ktweets" + "/tweets_1465248180000/")
    //    val collectedTweets = tweets.map(r => {r.replace("[]","[\"\"]")})

    val sqlContext = new SQLContext(sc)


    //  Read input files
    val domains = sqlContext.read.text(domainsFilename)
    domains.registerTempTable("Domains")

    val urls = sqlContext.read.text(urlsFilename)
    urls.registerTempTable("Urls")

    val myTweets = sqlContext.read.json(tweetsDir)
    myTweets.registerTempTable("Tweets")


    // Get certain fields from the tweets -- SQLContext
    var query = "SELECT id as t, retweetCount, isPossiblySensitive as sensitive, " +
      "userMentionEntities.id as mentioned, " +
      "hashtagEntities.text as hashtags, " +
      "urlEntities.expandedURL as fullLinks, " +
      "user.id as user, " +
      "user.isVerified as isVerified, " +
      "user.followersCount as followersCount, " +
      "user.friendsCount as friendsCount, " +
      "user.statusesCount as statusesCount, " +
      "user.favouritesCount as favouritesCount, "+
      "retweetedStatus.id as rsT, " +
      "retweetedStatus.retweetCount as rsRetweetCount, " +
      "retweetedStatus.user.id as rsUser " +
      "FROM Tweets "

    var results = sqlContext.sql(query)
    results.registerTempTable("Tweets")

    //Generate Predicates
    results.foreach(x => {

      val usr = x.getAs[Long]("user")
      val tid = x.getAs[Long]("t")
      val verified = x.getAs[Boolean]("isVerified")
      val retweetedStatusTid = x.getAs[Long]("rsT")
      val favCount = x.getAs[Long]("favouritesCount")

      writeToOutput("tweeted", usr, tid)

      if (x.getAs[Boolean]("sensitive") == true)
        writeToOutput("isPossiblySensitive", tid)

      writeToOutput("statusesCount", usr, x.getAs[Long]("statusesCount"))
      writeToOutput("friendsCount", usr, x.getAs[Int]("friendsCount"))
      writeToOutput("followersCount", usr, x.getAs[Int]("followersCount"))


      if(favCount != 0)
        writeToOutput("favouritesCount", tid, favCount)

      if (verified) {
        writeToOutput("verified", usr)
        if (collect_relationships) {
          //write friends
          val friends = getList(usr, twt, "friends")
          for (f <- friends)
            writeToOutput("friend", usr, f)

          //write followers
          val followers = getList(usr, twt, "followers")
          for (f <- followers)
            writeToOutput("isFollowedBy", usr, f)
        }
      }


      if (retweetedStatusTid > 0) {
        writeToOutput("retweeted", usr, retweetedStatusTid)

        val retweetedStatusUserId = x.getAs[Long]("rsUser")
        writeToOutput("tweeted", retweetedStatusUserId, retweetedStatusTid)

        val retweetedStatusRetweetCount = x.getAs[Long]("rsRetweetCount")
        writeToOutput("retweetCount", retweetedStatusTid, retweetedStatusRetweetCount)

        //          val rsFavCount = x.getAs("rsFavouritesCount")
        //          if(rsFavCount == 0)
        //            println("No favourites for ID " +tid.toString())
        //          else
        //            writeToOutput("favouritesCount", tid, rsFavCount)

      }


      else if (x.getAs[Long]("retweetCount") > 0)
        writeToOutput("retweetCount", tid, x.getAs[Long]("retweetCount"))


      var links = x.getAs[Seq[String]]("fullLinks")
      var nl = links.length
      var l = 0
      while (l < nl) {
        if (links(l).length > 3)
          writeToOutput("containsLink", tid, "\"" + links(l) + "\"")
        l += 1
      }

      var mentioned = x.getAs[Seq[String]]("mentioned")
      var ml = mentioned.length
      var m = 0
      while (m < ml) {
        writeToOutput("mentions", tid, mentioned(m))
        m += 1
      }

      var hashtags = x.getAs[Seq[String]]("hashtags")
      var hl = hashtags.length
      var h = 0
      while (h < hl) {
        writeToOutput("containsHashtag", tid, "\"" + hashtags(h) + "\"")
        h += 1
      }
    })




    // Filter Tweets: keep the ones that contain urls (aka fullLinks)
    query = "SELECT t, " +
      "explode(fullLinks) as fullLink, " +
      "user, isVerified, sensitive " +
      "FROM Tweets "

    results = sqlContext.sql(query)

    //Generate columns:
    //    1) url column as (remove [http(s)] and [www.] from fullLink)
    //    2) domain column as (remove everything from fullLink except domain name)

    // var tweetsTable = results.select(results.col("t"),results.col("user"),results.col("fullLink"),regexp_replace(lower(results.col("fullLink")),"""(?:https?://)?(?:www\.)?([A-Za-z0-9._%+-]+)/?.*""","$1").alias("domain"))
    var tweetsTable = results.select(results.col("t"), results.col("user"),results.col("isVerified"),results.col("sensitive"), results.col("fullLink"), regexp_replace(results.col("fullLink"),"""(https?://)?(?:www\.)?""", "").alias("url"), regexp_replace(results.col("fullLink"),"""(?:https?://)?(?:www\.)?([A-Za-z0-9._%+-]+)/?.*""", "$1").alias("domain"))
    //    //var tweetsTable = results.select(results.col("t"),results.col("user"),results.col("retweetCount"),results.col("mentioned"),results.col("hashtags") ,results.col("fullLink"))
    //
    tweetsTable.registerTempTable("Tweets")

    //Try to match tweet domains with the blacklist domains
    //some tweet domains won't be matched
    query = "SELECT t, user, fullLink, url, domain, value as malDomain, isVerified, sensitive " +
      "FROM Tweets " +
      "LEFT JOIN Domains " +
      "ON domain = value "

    var domainResults = sqlContext.sql(query)
    domainResults.registerTempTable("TweetsMalDomains")

    //Branch 1
    //Create a table of matched domains
    query = "SELECT * " +
      "FROM TweetsMalDomains " +
      "WHERE malDomain IS NOT NULL"

    domainResults = sqlContext.sql(query)



    //Branch 2
    //For those that did not match domains, match tweet urls with the blacklist urls
    query = "SELECT  t as t_u, user as user_u, fullLink as fullLink_u, url as url_u, domain as domain_u,"+
      "malDomain as malDomain_u, isVerified as isVerified_u, sensitive as sensitive_u " +
      "FROM TweetsMalDomains " +
      "JOIN Urls " +
      "ON url = value "+
      "WHERE malDomain IS NULL"



    val urlResults = sqlContext.sql(query)


    //Mark as malicious
    //Links from Branch 1
    domainResults.foreach(x => {
      val link = x.getAs[String]("fullLink")
      if (link.length > 3)
        writeToOutput("malicious", "\"" + link + "\"")
    })

    //Links from Branch 2
    urlResults.foreach(x => {
      val link = x.getAs[String]("fullLink_u")
      if (link.length > 3)
        writeToOutput("malicious", "\"" + link + "\"")
    })

    val t1 = System.nanoTime()
    println("Elapsed time: " + ((t1 - t0) / 1000000000.0) + " s")

    println("Memory:")
    println("   Tot: " + String.valueOf(sys.runtime.totalMemory() / 1073741824) + " gb")
    println("   Max: " + String.valueOf(sys.runtime.maxMemory() / 1073741824) + " gb")
    println("   Min: " + String.valueOf(sys.runtime.freeMemory() / 1073741824) + " gb")

    bw.close()
    System.exit(0)
  }
}


