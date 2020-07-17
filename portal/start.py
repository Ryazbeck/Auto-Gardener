from gpiozero import Button
from subprocess import check_call, run, PIPE, STDOUT, Popen, check_output
from signal import pause
from os import path, remove, system
from time import sleep
import re

mac_address = check_output('sudo cat /sys/class/net/wlan0/address', shell=True).decode('utf-8').replace('\n', '')

ap_udev_rule = f'SUBSYSTEM=="ieee80211", ACTION=="add|change", \
ATTR{{macaddress}}=="{mac_address}", KERNEL=="phy0", \
RUN+="/sbin/iw phy phy0 interface add ap0 type __ap", \
RUN+="/bin/ip link set ap0 address {mac_address}"'

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

interfaces_clean = '''
source-directory /etc/network/interfaces.d

auto lo
iface lo inet loopback

allow-hotplug wlan0
iface wlan0 inet dhcp
        wpa-conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
'''

def clean_up():
  print("CLEANING UP...")
  remove('/etc/udev/rules.d/70-persistent-net.rules')
  interfaces_file = open('/etc/network/interfaces', 'w')
  interfaces_file.write(interfaces_clean)
  interfaces_file.close()
  run('sudo systemctl disable hostapd.service dnsmasq.service', shell=True)
  run('sudo systemctl stop hostapd.service dnsmasq.service', shell=True)
  run('sudo ifdown ap0', shell=True)
  run('sudo ndsctl stop', shell=True)
  run('sudo udevadm trigger', shell=True)
  run('sudo systemctl restart networking.service', shell=True)


def run_splash():
    print("Setting up AP Hotspot...")

    try:
      print("Creating /etc/udev/rules.d/70-persistent-net.rules...")
      udev_rules = open('/etc/udev/rules.d/70-persistent-net.rules', 'w+')
      udev_rules.write(ap_udev_rule)
      udev_rules.close()
    except Exception as e:
      print(f'Failed to create udev rule: {e}')
      exit()

    try:
      print("Updating /etc/network/interfaces...")
      interfaces_file = open('/etc/network/interfaces', 'w')
      interfaces_file.write(interfaces)
      interfaces_file.close()
    except Exception as e:
      print(e)
      remove('/etc/udev/rules.d/70-persistent-net.rules')
      exit()

    try:
      print("Routing all traffic to gateway...")
      check_call("sudo sed -e '/^#address/ s/^#//' -i /etc/dnsmasq.conf", shell=True)
    except Exception as e:
      print(f'Failed to update dnsmasq.conf: {e}')

    print('Reloading udevadmin...')
    check_call('sudo udevadm trigger', shell=True)
    print('Restarting networking.service...')
    check_call('sudo systemctl restart networking.service', shell=True)
    
    try:
      print('Starting dnsmasq and hostapd...')
      check_call('sudo systemctl enable hostapd.service dnsmasq.service', shell=True)
      check_call('sudo systemctl start hostapd.service dnsmasq.service', shell=True)
    except Exception as e:
      if path.exists('/var/run/hostapd/ap0'):
        print('Removing /var/run/hostapd/ap0...')
        try:
          check_call('sudo rm /var/run/hostapd/ap0', shell=True)
        except Exception as e:
          print(f'Unable to remove /var/run/hostapd/ap0: {e}')

      sleep(3)
      if system('sudo systemctl is-active --quiet hostapd') != 0:
        print(f'hostapd failed: {e}')
        clean_up()
        exit()

    print('Starting AP...')
    check_call('sudo ip addr flush dev ap0', shell=True)
    check_call('sudo ifup ap0', shell=True)
    check_call('sudo ifdown ap0', shell=True)
    check_call('sudo ifup ap0', shell=True)

    try:
      print('Starting nodogsplash...')
      check_call('sudo nodogsplash &> /etc/nodogsplash/log.txt &', shell=True,
        stdout=PIPE,
        stderr=STDOUT)
    except:
      print('nodogsplash failed')


    # iter = 0
    # while iter < 30:
    #   hostapd_log = check_call('sudo journalctl -u hostapd -n 15 --no-pager', shell=True).decode('utf-8')
    #   for line in hostapd_log:
    #     if 'invalid state' in line:
    #       print('Invalid AP state detected. Restarting ap0...')
    #       check_call('sudo ifdown ap0', shell=True)
    #       check_call('sudo ifup ap0', shell=True)
    #       iter = 30
    #       break
    #   sleep(2)

button = Button(24, hold_time=3, pull_up=False)
button.when_held = run_splash

try:
  print("Button is ready...")
  pause()
except KeyboardInterrupt:
  close()