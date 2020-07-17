name := "CollectData"

version := "0.1"

scalaVersion := "2.11.8"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "1.6.0",
  "org.apache.spark" %% "spark-hive" % "1.6.0",
  "org.apache.spark" % "spark-streaming_2.11" % "1.6.0",
  "com.google.code.gson" % "gson" % "2.7",
  "org.apache.spark" % "spark-streaming-twitter_2.11" % "1.6.0"
)

assemblyMergeStrategy in assembly := {
  case PathList ("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
