#!/usr/bin/bash
# Run the radiosonde tracker python script in a screen session
SESSION_NAME=sonde_tracker
SCRIPT_PATH=${HOME}/sonde_tracker

cd ${SCRIPT_PATH}
sess=$(screen -ls | grep -F "$SESSION_NAME" | grep -v grep)
if [[ $sess == *"$SESSION_NAME"* ]]; then
    echo Screen session "$SESSION_NAME" already running, restarting
    screen -S ${SESSION_NAME} -X quit
fi
screen -dmS ${SESSION_NAME} -t tracker
sleep 5
screen -S ${SESSION_NAME} -p 0 -X stuff $'python3 sonde_tracker.py\r'
