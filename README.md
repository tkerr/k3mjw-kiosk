# K3MJW Kiosk  

Custom files used for the K3MJW weather kiosk display at Skyview Radio Society.  
www.skyviewradio.net  

Hardware: Cybergeek Nano J1  
OS: Ubuntu 22.04  
Hostname: k3mjw-Wx1  

The kiosk runs an Apache server and hosts a Firefox web page in full screen mode.  
The web page links to NWS and NOAA web site graphics and updates them once per minute.  
The web page also displays the sondehub.org web page and tracks radiosondes in the local area.  

### File locations

Files in the `www` folder should be placed at /var/www/k3mjw-wx  
Exception: `k3mjw-wx.conf` should be placed in /etc/apache2/sites-available  
(See Apache documentation for instructions on setting up the Apache web server)

Files in the `sonde_tracker` folder should be placed at /home/k3mjw/sonde_tracker  

`start_k3mjw_kiosk.sh` should be placed at /home/k3mjw  

Use the Ubuntu startup applications app to configure the above script to run at startup.  
