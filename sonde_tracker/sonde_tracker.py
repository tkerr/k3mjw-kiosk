###############################################################################
# sonde_tracker.py
# Author: Tom Kerr AB3GY
#
# Track radiosondes using the sondehub.org API and generate URLs to track them
# on the sondehub.org website.
# References:
# https://tracker.sondehub.org
# https://github.com/projecthorus/sondehub-tracker/wiki/SondeHub-Tracker-User-Guide
# https://github.com/projecthorus/pysondehub/tree/main
# https://github.com/projecthorus/sondehub-infra/wiki/SondeHub-Telemetry-Format
#
# Designed for personal use by the author, but available to anyone under the
# license terms below.
#
# Acknowledgments
# The sondehub website and associated API tools are provided by Project Horus
# https://github.com/projecthorus
# http://www.projecthorus.org
###############################################################################

###############################################################################
# License
# CC BY-NC-SA 4.0
# https://creativecommons.org/licenses/by-nc-sa/4.0/ 
# 
# You are free to:
#   * Share - copy and redistribute the material in any medium or format
#   * Adapt — remix, transform, and build upon the material
#   The licensor cannot revoke these freedoms as long as you follow the license 
#   terms. 
# Under the following terms: 
#   * Attribution — You must give appropriate credit, provide a link to the 
#     license, and indicate if changes were made. You may do so in any reasonable 
#     manner, but not in any way that suggests the licensor endorses you or your use. 
#   * NonCommercial — You may not use the material for commercial purposes.
#   * ShareAlike — If you remix, transform, or build upon the material, you must 
#     distribute your contributions under the same license as the original. 
#   * No additional restrictions — You may not apply legal terms or technological 
#     measures that legally restrict others from doing anything the license permits. 
# Notices:
#   * You do not have to comply with the license for elements of the material in 
#     the public domain or where your use is permitted by an applicable exception 
#     or limitation.
#   * No warranties are given. The license may not give you all of the permissions 
#     necessary for your intended use. For example, other rights such as publicity, 
#     privacy, or moral rights may limit how you use the material. 
#   * You should carefully review all of the terms and conditions of the actual 
#     license in the above link before using the licensed material.
###############################################################################

# System level packages.
import atexit
import geopy.distance
import signal
import sondehub
import sys
import time

from datetime import datetime

# Local packages.
from TrackerConfig import TrackerConfig

##############################################################################
# Globals.
############################################################################## 

# Configuration.
# Values are shown for example. They are overwritten by the configuration file.
station_lat = 39.421177   # Latitude of observer station
station_lon = -83.821146  # Longitude of observer station
sonde_max_miles = 50.0    # A radiosonde within this distance will be tracked
sonde_timeout_sec = 180.0 # Telemetry timeout to start searching again
sonde_dwell_sec = 1800.0  # Max time to dwell on a timed out radiosonde before re-centering
follow = True             # Follow radiosonde if true
follow_miles = 40.0
sondehub_map_zoom = 9
sondehub_history = '3h'
sondehub_base_url = 'https://tracker.sondehub.org'
url_text_file = 'sondehub_url.txt'
log_file_base = 'logs/sonde_tracker_log'

# Runtime objects.
sonde_serial = ''
tracking_sonde = False
tracking_dwell = False
tracker_config = TrackerConfig()
dwell_start = time.time()
last_message = time.time()
telemetry_stream = None


##############################################################################
# Functions.
############################################################################## 

def do_message(message):
    global station_lat
    global station_lon
    global sonde_max_miles
    global follow
    global follow_miles
    global sonde_serial
    global tracking_sonde
    global tracking_dwell
    global last_message
    global telemetry_stream
    if tracking_sonde:
        # Tracking a radiosonde.
        if (sonde_serial == message['serial']):
            # Serial number match. Update message timestamp.
            last_message = time.time()
            if follow:
                lat = message['lat']
                lon = message['lon']
                distance = geopy.distance.geodesic((station_lat, station_lon), (lat, lon)).miles
                if (distance >= follow_miles):
                    station_lat = (station_lat + lat) / 2.0
                    station_lon = (station_lon + lon) / 2.0
                    log_msg('Radiosonde distance {:.1f} miles, re-centering map'.format(distance))
                    url = make_url(lat=station_lat, lon=station_lon, serial=sonde_serial)
                    log_msg(url)
                    make_text(url)
        else:
            pass
            # Sometimes mismatches will occur upon detecting a nearby sonde as the
            # message queue backlog is processed
            #log_msg('Sonde mismatch: {} vs {}'.format(sonde_serial, message['serial']))
    else:
        # Searching for a radiosonde to track.
        lat = message['lat']
        lon = message['lon']
        distance = geopy.distance.geodesic((station_lat, station_lon), (lat, lon)).miles
        if (distance <= sonde_max_miles):
            # Found a radiosonde to track.
            tracking_sonde = True
            tracking_dwell = False
            last_message = time.time()
            sonde_serial = message['serial']
            telemetry_stream.remove_sonde('#')
            telemetry_stream.add_sonde(sonde_serial)
            log_msg('Found radiosonde {} at {:.1f} miles'.format(sonde_serial, distance))
            url = make_url(serial=sonde_serial)
            log_msg(url)
            make_text(url)

# ----------------------------------------------------------------------------
def exit_handler():
    log_msg('Application exit')

# ----------------------------------------------------------------------------
def get_config():
    global tracker_config
    global station_lat
    global station_lon
    global sonde_max_miles
    global sonde_timeout_sec
    global sonde_dwell_sec
    global follow
    global follow_miles
    global sondehub_map_zoom
    global sondehub_history
    global sondehub_base_url
    global url_text_file
    global log_file_base
    (status, err_msg) = tracker_config.read()
    if not status:
        print('Error reading configuration file: {}'.format(err_msg))
        return False
        
    var = tracker_config.get('location', 'station_lat')
    if (len(var) == 0): return False
    station_lat = float(var)
    
    var = tracker_config.get('location', 'station_lon')
    if (len(var) == 0): return False
    station_lon = float(var)
    
    var = tracker_config.get('location', 'sonde_max_miles')
    if (len(var) == 0): return False
    sonde_max_miles = float(var)
    
    var = tracker_config.get('tracking', 'sonde_timeout_sec')
    if (len(var) == 0): return False
    sonde_timeout_sec = float(var)
    
    var = tracker_config.get('tracking', 'sonde_dwell_sec')
    if (len(var) == 0): return False
    sonde_dwell_sec = float(var)
    
    var = tracker_config.get('tracking', 'follow')
    if (len(var) == 0): return False
    follow = bool(var)
    
    var = tracker_config.get('tracking', 'follow_miles')
    if (len(var) == 0): return False
    follow_miles = float(var)
    
    var = tracker_config.get('sondehub', 'sondehub_map_zoom')
    if (len(var) == 0): return False
    sondehub_map_zoom = int(var)
    
    var = tracker_config.get('sondehub', 'sondehub_history')
    if (len(var) == 0): return False
    sondehub_history = var
    
    var = tracker_config.get('sondehub', 'sondehub_base_url')
    if (len(var) == 0): return False
    sondehub_base_url = var
    
    var = tracker_config.get('application', 'url_text_file')
    if (len(var) == 0): return False
    url_text_file = var
    
    var = tracker_config.get('application', 'log_file_base')
    if (len(var) == 0): return False
    log_file_base = var
    
    return True

# ----------------------------------------------------------------------------
def log_msg(msg):
    global log_file
    now = datetime.now()
    date_suffix = now.strftime('%Y-%m-%d')
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    with open('{}_{}.txt'.format(log_file_base, date_suffix), 'a') as f:
        f.write('{} {}\n'.format(timestamp, msg))

# ----------------------------------------------------------------------------
def make_text(sondehub_url):
    with open(url_text_file, 'w') as f:
        f.write('{}\n'.format(sondehub_url))

# ----------------------------------------------------------------------------
def make_url(
    mt='Mapnik',
    mz=None,
    sh=None,
    lat=None,
    lon=None,
    serial=''):
    
    global sondehub_map_zoom
    global sondehub_history
    global station_lat
    global station_lon
    
    if mz is None:
        mz = sondehub_map_zoom
    if sh is None:
        sh = sondehub_history
    if lat is None:
        lat = station_lat
    if lon is None:
        lon = station_lon
    
    url = '{}/#!mt={}&mz={}&qm={}&mc={:.6f},{:.6f}'.format(sondehub_base_url, mt, mz, sh, lat, lon)
    if (len(serial) > 0):
        url += '&f={}&q={}'.format(serial, serial)
    else:
        url += '&f=""&q=""' # Use invalid values to clear these parameters
    return url


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":

    # Get configuration parameters. Exit if error.
    if not get_config():
        sys.exit(1)
    
    # Register exit handlers.
    atexit.register(exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)
    
    # Open the telemetry stream.
    telemetry_stream = sondehub.Stream(
        on_message=do_message,
    )
    
    # Run forever.
    log_msg('Application start')
    log_msg('Searching for radiosonde')
    url = make_url()
    log_msg(url)
    make_text(url)
    try:
        while (True):
            now = time.time()
            if tracking_sonde:
                if (now - last_message) >= sonde_timeout_sec:
                    # Message timeout while tracking. Begin post-tracking dwell.
                    tracking_sonde = False
                    tracking_dwell = True
                    dwell_start = time.time()
                    telemetry_stream.remove_sonde(sonde_serial)
                    telemetry_stream.add_sonde('#')
                    sonde_serial = ''
                    log_msg('Telemetry timeout, starting dwell')
                    station_lat = float(tracker_config.get('location', 'station_lat'))
                    station_lon = float(tracker_config.get('location', 'station_lon'))
            elif tracking_dwell:
                # Post-tracking dwell mode. Check for timeout.
                if (now - dwell_start) >= sonde_dwell_sec:
                    tracking_dwell = False
                    log_msg('Dwell timeout, searching for radiosonde')
                    url = make_url()
                    log_msg(url)
                    make_text(url)
            time.sleep(5)
    except KeyboardInterrupt as err:
        log_msg('KeyboardInterrupt')
    except Exception as err:
        log_msg(str(err))
    telemetry_stream.disconnect()
    sys.exit(0)
