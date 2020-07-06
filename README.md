## Yarden Gnome Station

Components for assisting the user with initial setup.

### run_udev_mac.sh:
1. Runs at boot before hostapd/dnsmasq
1. Greps WLAN0 mac from udev rules
1. Updates udev rules if AP0 mac does not match WLAN0

### run_splash.sh:
1. Listens for 3 second hold of physical button on device
1. Turns up AP0
1. Runs nodogsplash
1. Back to listening

### run_wifi_config.sh:
1. Takes in user's Wi-fi SSID and Password
1. Configures wpa_supplicant.conf
1. Restarts wlan0
1. Confirms connection is established
    1. TO-DO: Show confirmation on splash
1. Disables ap0
1. Stops nodogsplash
1. Starts sensor service