#This software is released under the GNU GPL license.

# This is an example script for BinAuth
# It verifies a client username and password and sets the session length.
#
# If BinAuth is enabled, NDS will call this script as soon as it has received an authentication request
# from the web page served to the client's CPD (Captive Portal Detection) Browser by one of the following:
#
# 1. splash_sitewide.html
# 2. PreAuth
# 3. FAS
#
# The username and password entered by the clent user will be included in the query string sent to NDS via html GET
# For an example, see the file splash_sitewide.html

METHOD="$1"
CLIENTMAC="$2"

case "$METHOD" in
        auth_client)
                USERNAME="$3"
                PASSWORD="$4"
                REDIR="$5"
                USER_AGENT="$6"
                CLIENTIP="$7"

                if [[ ! -z $USERNAME && ! -z $PASSWORD ]]; then
                        echo "Updating wpa_supplicant.conf..."
                        cat << _EOF_ > /etc/wpa_supplicant/wpa_supplicant.conf
# Grant all members of group "netdev" permissions to configure WiFi, e.g. via wpa_cli or wpa_gui
ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev
# Allow wpa_cli/wpa_gui to overwrite this config file
update_config=1
network={
  ssid="$USERNAME"
  scan_ssid=1
  key_mgmt=WPA-PSK
  psk="$PASSWORD"
}
_EOF_
                        ifdown wlan0
                        sleep 3
                        ifup wlan0
                        
                        sleep 5
                        echo 'Stopping Wifi AP...'
                        ifdown ap0
                        exit 0
                fi

                exit 1
                ;;
        client_auth|client_deauth|idle_deauth|timeout_deauth|ndsctl_auth|ndsctl_deauth|shutdown_deauth)
                INGOING_BYTES="$3"
                OUTGOING_BYTES="$4"
                SESSION_START="$5"
                SESSION_END="$6"
                # client_auth: Client authenticated via this script.
                # client_deauth: Client deauthenticated by the client via splash page.
                # idle_deauth: Client was deauthenticated because of inactivity.
                # timeout_deauth: Client was deauthenticated because the session timed out.
                # ndsctl_auth: Client was authenticated by the ndsctl tool.
                # ndsctl_deauth: Client was deauthenticated by the ndsctl tool.
                # shutdown_deauth: Client was deauthenticated by Nodogsplash terminating.
                ;;
esac
