###############################################################################
# TrackerConfig.py
# Author: Tom Kerr AB3GY (ab3gy@arrl.net)
#
# TrackerConfig class.
# Implements an interface to a tracker.cfg configuration file for the
# sonde_tracker application.  
# File format is similar to Microsoft Windows .INI files.
# Parameters are stored in sections as key/value pairs.
#
# Designed for personal use by the author, but available to anyone under the
# license terms below.
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
import os
import sys
import configparser

# Local packages.


##############################################################################
# Globals.
##############################################################################


##############################################################################
# Functions.
##############################################################################


##############################################################################
# TrackerConfig class.
##############################################################################
class TrackerConfig(object):
    """
    TrackerConfig class.
    Implements an interface to a tracker.cfg configuration file for the
    sonde_tracker application.  File format is similar to Microsoft Windows 
    .INI files. Parameters are stored in sections as key/value pairs.
    """
    
    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Class constructor.
    
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        """
        # The tracker.cfg file should be in the same directory as the application script.
        self.cfg_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        
        # Construct the full config file name.
        self.cfg_file = os.path.join(self.cfg_path, 'tracker.cfg')
        
        # The configuration file parser object.
        self.config = configparser.ConfigParser()

    # ------------------------------------------------------------------------
    def get(self, section, key):
        """
        Get the specified parameter from the specified section.
        
        Parameters
        ----------
        section : str
            The config file section name.
        key : str
            The parameter key.
        
        Returns
        -------
        value : str
            The parameter value as a string if found, or an empty string 
            if not found.
        """
        value = ''
        try:
            value = str(self.config[str(section)][str(key)])
        except Exception as err:
            print('Error reading ["{}"] "{}" '.format(section, key))
            pass
        return value

    # ------------------------------------------------------------------------
    def has_section(self, section):
        """
        Return True if the specified section exists, False otherwise.
        
        Parameters
        ----------
        section : str
            The config file section name.

        Returns
        -------
        True if the section exists, False otherwise.
        """
        found = (str(section) in self.config.sections())
        return found

    # ------------------------------------------------------------------------
    def read(self):
        """
        Read the config file and get all config parameters.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        (status, err_msg) : tuple
            status : bool
                True if config file read was successful, False otherwise.
            err_msg : str
                Error message if an error occurred.
        """
        status = False
        err_msg = ''

        # See if the config file exists.
        if os.path.isfile(self.cfg_file):
            try:
                self.config.read(self.cfg_file)
                status = True
            except Exception as err:
                status = False
                err_msg = str(err)
        return (status, err_msg)


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    
    status = ''
    errmsg = ''
    my_config = TrackerConfig()
    print('Config file: ' + my_config.cfg_file)
    
    (status, errmsg) = my_config.read()
    if not status:
        print('Error reading ' + my_config.cfg_file + ': ' + errmsg)
    
    # Print the config file section names.
    print('Config file sections: ', end='')
    print(my_config.config.sections())
    
    # Get some config parameters.
    station_lat = my_config.get('location', 'station_lat')
    print('station_lat: "{}"'.format(station_lat))
    
    station_lon = my_config.get('location', 'station_lon')
    print('station_lon: "{}"'.format(station_lon))
    
    sonde_timeout_sec = my_config.get('tracking', 'sonde_timeout_sec')
    print('sonde_timeout_sec: "{}"'.format(sonde_timeout_sec))

    sondehub_base_url = my_config.get('sondehub', 'sondehub_base_url')
    print('sondehub_base_url: "{}"'.format(sondehub_base_url))

