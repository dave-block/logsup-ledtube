#!/usr/bin/python
from os import system

system('mkdir -p /opt/lib/firmware')
system('mkdir -p /opt/etc/init.d')

system('cp BB-SPI0-LPD8806.dtbo /opt/lib/firmware')
system('mkdir -p /opt/logsup-ledtube')
system('cp *.py /opt/logsup-ledtube')
system('cp logsup-ledtube /opt/etc/init.d/')
#system('update-rc.d logsup-ledtube defaults')
