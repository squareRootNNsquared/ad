#!/bin/bash

###
### Ensure this file is executable ( cmhod +x [[path]] )
###

clear
sleep 1
echo "[[ Anomaly Detection has begun ]]"
sleep 2
clear
sleep 1

python /home/e/Desktop/ad/src/s.py &
python /home/e/Desktop/ad/src/ad.py
