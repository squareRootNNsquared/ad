#!/bin/bash

clear
sleep 1
echo "[[ Anomaly Detection has begun ]]"
sleep 2
clear
sleep 1

rootPath=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
python "$rootPath/src/s.py" &
echo "[[ s.py operational ]]"
python "$rootPath/src/ad.py"
kill $(pgrep -f 's.py')
echo "[[ s.py terminated ]]"
