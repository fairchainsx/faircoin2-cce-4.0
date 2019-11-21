#!/bin/sh
#
# Replace the path placeholders below
# with the proper paths

sleep 20

# start faircoin daemon
rm ~/faircoin2-cce-4.0/dataload.lock 2> /dev/null
~/faircoin/faircoind --daemon 2> /dev/null &
