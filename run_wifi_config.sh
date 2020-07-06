#!/usr/bin/env bash

while getopts h:s:k:r: option
do
case "${option}"
in
s) WSSID=${OPTARG};;
k) WKEY=${OPTARG};;
esac
done


echo "Updating wpa_supplicant.conf..."
cat << _EOF_ > /etc/wpa_supplicant/wpa_supplicant.conf
# Grant all members of group "netdev" permissions to configure WiFi, e.g. via wpa_cli or wpa_gui
ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev
# Allow wpa_cli/wpa_gui to overwrite this config file
update_config=1
network={
  ssid="$WSSID"
  scan_ssid=1
  key_mgmt=WPA-PSK
  psk="$WKEY"
}
_EOF_