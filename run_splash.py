from gpiozero import Button
from subprocess import check_call, run, PIPE
from signal import pause

mac_address = run('cat /sys/class/net/wlan0/address', shell=True, stdin=PIPE, stdout=PIPE).stdout.read()

ap_udev_rule = 'SUBSYSTEM=="ieee80211", ACTION=="add|change", ATTR\{macaddress\}=="b8:27:eb:32:24:84", KERNEL=="phy0", RUN+="/sbin/iw phy phy0 interface add ap0 type __ap", RUN+="/bin/ip link set ap0 address b8:27:eb:32:24:84"'
ap_udev_rule_file = open("/etc/udev/rules.d/70-persistent-net.rules", "w")

interfaces = '''
source-directory /etc/network/interfaces.d

auto lo
iface lo inet loopback

allow-hotplug ap0
iface ap0 inet static
       address 192.168.100.1
       netmask 255.255.255.0
       hostapd /etc/hostapd/hostapd.conf

allow-hotplug wlan0
iface wlan0 inet dhcp
        wpa-conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
'''
interfaces_file = open("/etc/network/interfaces", "w")

def run_splash():
    print("Starting splash page...")
    ap_udev_rule_file.write(ap_udev_rule)
    ap_udev_rule_file.close()

    interfaces_file.write(interfaces)
    interfaces_file.close()

    check_call(['sudo', 'ifup', 'ap0'])

button = Button(24, hold_time=3, pull_up=False)
button.when_held = run_splash

pause()