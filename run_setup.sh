# get wlan address
$WLAN_ADDRESS = iw wlan0 info | grep addr | awk '{print $2}'


# put address in net rules
cat << _EOF_ > /etc/udev/rules.d/70-persistent-net.rules
SUBSYSTEM=="ieee80211", \
ACTION=="add|change", \
ATTR{macaddress}=="$WLAN_ADDRESS", \
KERNEL=="phy0", \
RUN+="/sbin/iw phy phy0 interface add ap0 type __ap", \
RUN+="/bin/ip link set ap0 address $WLAN_ADDRESS"
_EOF_


# install dnsmasq and hostapd
sudo apt-get install -y dnsmasq hostapd


# update dnsmask conf
cat << _EOF_ > /etc/dnsmasq.conf
interface=lo,ap0
no-dhcp-interface=lo,wlan0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=192.168.100.1,192.168.100.100,12h
_EOF_


# update hostapd conf
cat << _EOF_ > /etc/hostapd/hostapd.conf
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=ap0
driver=nl80211
ssid=yardengnome
hw_mode=g
channel=11
wmm_enabled=0
macaddr_acl=0
auth_algs=1
wpa=2
wpa_passphrase=gnome123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
_EOF_


# point hostapd to the hostapd conf
cat << _EOF_ > /etc/default/hostapd
DAEMON_CONF="/etc/hostapd/hostapd.conf"
_EOF_


cat << _EOF_ > /etc/network/interfaces
# interfaces(5) file used by ifup(8) and ifdown(8)

# Please note that this file is written to be used with dhcpcd
# For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'

# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d

auto lo
auto ap0
auto wlan0
iface lo inet loopback

allow-hotplug ap0
iface ap0 inet static
        address 192.168.100.1
        netmask 255.255.255.0
        hostapd /etc/hostapd/hostapd.conf

allow-hotplug wlan0
iface wlan0 inet dhcp
        wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
_EOF_


# install nodgosplash
sudo apt install -y git libmicrohttpd-dev
# https://ftp.gnu.org/gnu/libmicrohttpd/libmicrohttpd-latest.tar.gz
git clone https://github.com/nodogsplash/nodogsplash.git
cd nodogsplash
make
sudo make install


# configure nodogsplash
cp nodogsplash.conf /etc/nodogsplash
cp index.html /etc/nodogsplash/htdocs
cp binauth.sh /etc/nodogsplash