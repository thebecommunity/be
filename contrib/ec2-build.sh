#!/bin/bash
#
# This script will grab and build all the components needed to deploy
# Kataspace on EC2 from a base *Ubuntu* image (the base Linux image
# provided by Amazon is not supported).

DIR=`pwd`

# Bail out with a message for the user
function bail {
    echo $1
    exit -1
}

# Install dependencies for Sirikata space server
sudo apt-get install -y \
git-core cmake sed unzip zip automake1.9 jam g++ \
libzzip-dev autoconf libtool bison patch \
gperf subversion libtool ruby libgsl0-dev \
libssl-dev libbz2-dev || \
bail "Couldn't install required base system packages."

# Install dependencies for KataSpace/KataJS, including web
# server. protojs requires java to build unfortunately.
sudo apt-get install -y lighttpd default-jre || \
bail "Couldn't install required lighttpd system packages."

# Install monit.
sudo apt-get install -y monit || \
bail "Couldn't install required monit system packages."

# Install flup for handling fcgi requests from lighttpd, i.e. for all
# our server-side web application logic. Also install repoze.who which
# is used for auth, and genshi for templates
sudo apt-get install -y python-flup python-repoze.who python-genshi ||
bail "Couldn't install flup."

# Install encfs to encrypt the database.
sudo apt-get install -y encfs || \
bail "Couldn't install required encfs system packages."

# Check out and build Sirikata space server
git clone git://github.com/sirikata/sirikata.git sirikata.git && \
cd sirikata.git && \
make minimal-depends && \
cd build/cmake && \
cmake -DCMAKE_BUILD_TYPE=Release . && \
make space tcpsst servermap-tabular core-local weight-exp weight-sqr weight-const space-local space-standard || \
bail "Couldn't build space server."

# Checkout and "build" Kataspace
cd ${DIR} && \
git clone git://github.com/thebecommunity/be.git be.git && \
cd be.git && \
make || \
bail "Couldn't build kataspace."

# Create the space for the encrypted filesystem. You *must* run this
# interactively in order to set the password for the filesystem. Make
# sure you can remember this password or store it some place secure --
# it cannot be reset!
cd ${DIR} && \
cd be.git && \
./contrib/encfs.sh create ||
bail "Couldn't create encrypted directory for database."

# Create database, adding user 'admin' with password 'admin'. Be sure to change this!
cd ${DIR} && \
cd be.git && \
./contrib/db.py init admin admin admin