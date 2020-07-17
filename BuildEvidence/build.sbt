name := "BuildEvidence"

version := "0.1"

scalaVersion := "2.11.8"

libraryDependencies ++= Seq(
  "com.google.code.gson" % "gson" % "2.7",
  "org.apache.spark" %% "spark-core" % "2.2.0",
  "org.apache.spark" %% "spark-hive" % "2.2.0",
  "org.apache.spark" %% "spark-sql" % "2.2.0",
  "org.apache.spark" %% "spark-streaming-twitter" % "1.3.1",
  "org.apache.spark" %% "spark-streaming" % "1.6.1"
)

assemblyMergeStrategy in assembly := {
  case PathList ("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
