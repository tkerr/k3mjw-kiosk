#!/usr/bin/bash
# Start the K3MJW weather kiosk application
HN=$(hostname)
KIOSK_URL=http://${HN}.local/index.html

# Start the python tracker script in a screen terminal
${HOME}/sonde_tracker/start_sonde_tracker.sh
sleep 5

# Start Firefox 
#echo ${KIOSK_URL}
#firefox -kiosk ${KIOSK_URL}
firefox ${KIOSK_URL}
