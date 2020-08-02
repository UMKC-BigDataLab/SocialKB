#!/bin/bash

# Downloading Java.
sudo apt-get -y update
cd $HOME && wget -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.tar.gz
tar -xvf jdk-8u131-linux-x64.tar.gz

# Adding Java to the path.
export JAVA_HOME=$HOME/jdk1.8.0_131
echo 'export JAVA_HOME='$HOME'/jdk1.8.0_131' >> /users/$USER/.profile
export PATH=$PATH:$JAVA_HOME/bin
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /users/$USER/.profile

# Downloading Scala.
cd $HOME && wget https://downloads.lightbend.com/scala/2.11.8/scala-2.11.8.tgz
tar -xvf scala-2.11.8.tgz

# Adding Scala to the path.
export SCALA_HOME=$HOME/scala-2.11.8
echo 'export SCALA_HOME='$HOME'/scala-2.11.8' >> /users/$USER/.profile
export PATH=$PATH:$SCALA_HOME/bin
echo 'export PATH=$PATH:$SCALA_HOME/bin' >> /users/$USER/.profile

# Setting up sbt.
echo "deb https://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo apt-key add
sudo apt-get update
sudo apt-get install sbt

# Setting up Spark.
cd $HOME && wget https://archive.apache.org/dist/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar -xvf spark-2.4.5-bin-hadoop2.7.tgz

# Adding Spark to the path.
export SPARK_HOME=$HOME/spark-2.4.5-bin-hadoop2.7
echo 'export SPARK_HOME='$HOME'/spark-2.4.5-bin-hadoop2.7' >> /users/$USER/.profile
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> /users/$USER/.profile
