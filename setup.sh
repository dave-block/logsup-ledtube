#!/bin/bash
# install python and supporting files for logsup-ledtube

# update and install apt prereqs
apt-get update
apt-get install build-essential python-dev python-setuptools python-pip python-smbus -y

# update and install python library
easy_install -u
pip install Adafruit_BBIO

# overlay
cp BB-SPI0-LPD8806.dtbo /lib/firmware
if [ $? -ne 0 ]
    echo "failed to install overlay."
    exit 1;
fi

# code
mkdir -p /opt/logsup-ledtube
cp *.py /opt/logsup-ledtube
if [ $? -ne 0 ]
    echo "failed to install python files to /opt/logsup-ledtube."
    exit 1;
fi

# upstart job
cp logsup-ledtube /etc/init.d/
update-rc.d logsup-ledtube defaults
if [ $? -ne 0 ]
    echo "failed to create upstart job."
    exit 1;
fi