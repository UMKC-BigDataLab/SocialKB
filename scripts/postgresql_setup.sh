#!/usr/bin/env bash

POSTGRESQL_URL=https://ftp.postgresql.org/pub/source/v9.2.3/postgresql-9.2.3.tar.gz

# Creating the PostgreSQL data directory.
mkdir /mydata/Postgres_Data

# Downloading and extracting PostgreSQL.
wget https://ftp.postgresql.org/pub/source/v9.2.3/postgresql-9.2.3.tar.gz
tar -xvf postgresql-9.2.3.tar.gz
cd postgresql-9.2.3/

# Compiling PostgreSQL.
./configure --without-readline && make
sudo make install

# Initializing the database.
/usr/local/pgsql/bin/initdb -D /mydata/Postgres_Data
/usr/local/pgsql/bin/postmaster -D /mydata/Postgres_Data 2>&1 &

# Installing additional modules.
cd contrib/intarray && make && sudo make install
cd ../intagg && make && sudo make install && cd ../..

# Starting the PostgreSQL daemon process.
/usr/local/pgsql/bin/postgres -D /mydata/Postgres_Data >logfile 2>&1 &
sleep 30

# Creating the database for Tuffy.
/usr/local/pgsql/bin/createdb tuffydb
/usr/local/pgsql/bin/createlang plpgsql tuffydb
