## Yarden Gnome Station

Components for assisting the user with initial setup.

## Yarden Gnome Station

Work in progress

Goals:
* Mobile first
* Capacitive soil moisture sensor (replaceable)
* Waterproof
* Store data centrally using python, Wifi, REST
* Solar-powered charging for li-ion batteries
* Software controlled solenoid valve
* Open source
* One-touch Wifi setup


### captive_portal.sh:
1. Runs at boot
1. Listens for 3 second hold of button on station
1. Turns up AP0
1. Runs nodogsplash
1. Continues listening

### conf/binauth.sh:
1. Takes in user's Wi-fi SSID and Password
1. Configures wpa_supplicant.conf
1. Restarts wlan0
1. Confirms connection is established
    1. TO-DO: Show confirmation on splash
1. Disables ap0
1. Stops nodogsplash
1. Starts sensor service