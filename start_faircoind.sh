#!/bin/sh
#
# Replace the path placeholders below
# with the proper paths

sleep 20

# start faircoin daemon
rm ~/faircoin2-cce-4.0/dataload.lock 2> /dev/null
~/faircoin/faircoind -daemon -blocknotify=/home/faircoin/faircoin2-cce-4.0/run_dbloader.sh 2> /dev/null &
# ~/faircoin/faircoind -daemon -conf=/home/faircoin/.faircoin2/faircoin.conf -blocknotify=/home/faircoin/faircoin2-cce-4.0/run_dbloader.sh 2> /dev/null &
