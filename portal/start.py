from gpiozero import Button
from subprocess import check_call, run, PIPE, STDOUT, Popen, check_output
from signal import pause
from os import path, remove, system
from time import sleep
import re
import logging

# logging.basicConfig(filename=f'{__name__}.log', level=logging.INFO)
logging.basicConfig(filename=f'{__file__}.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

mac_address = check_output('sudo cat /sys/class/net/wlan0/address',
  shell=True,
  encoding='utf8').replace('\n', '')

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

def run_splash():
    try:
      logging.info("Creating /etc/udev/rules.d/70-persistent-net.rules...")
      udev_rules = open('/etc/udev/rules.d/70-persistent-net.rules', 'w+')
      udev_rules.write(ap_udev_rule)
      udev_rules.close()
    except Exception as e:
      logging.debug(f'Failed to create udev rule: {e}')
      exit()

    try:
      logging.info("Updating /etc/network/interfaces...")
      interfaces_file = open('/etc/network/interfaces', 'w')
      interfaces_file.write(interfaces)
      interfaces_file.close()
    except Exception as e:
      logging.debug(f'Failed to update interfaces: {e}')
      remove('/etc/udev/rules.d/70-persistent-net.rules')
      exit()

    try:
      logging.info("Routing all traffic to gateway...")
      check_call("sudo sed -e '/^#address/ s/^#//' -i /etc/dnsmasq.conf", shell=True)
    except Exception as e:
      logging.debug(f'Failed to update dnsmasq.conf: {e}')

    try:
      logging.info('Reloading udevadmin...')
      check_call('sudo udevadm trigger', shell=True)
      logging.info('Restarting networking.service...')
      check_call('sudo systemctl restart networking.service', shell=True)
    except Exception as e:
      logging.debug(f'{e}')
    
    try:
      logging.info('Starting dnsmasq and hostapd...')
      check_call('sudo systemctl enable hostapd.service dnsmasq.service', shell=True)
      check_call('sudo systemctl start hostapd.service dnsmasq.service', shell=True)
    except Exception as e:
      if path.exists('/var/run/hostapd/ap0'):
        logging.debug('Removing /var/run/hostapd/ap0...')
        try:
          check_call('sudo rm /var/run/hostapd/ap0', shell=True)
        except Exception as e:
          logging.debug(f'Unable to remove /var/run/hostapd/ap0: {e}')

      sleep(3)
      if system('sudo systemctl is-active --quiet hostapd') != 0:
        logging.debug(f'hostapd failed: {e}')
        exit()

    try:
      logging.info('Starting splash page')
      check_call('python3 portal.py &>portal.log &')
    except Exception as e:
      logging.debug(f'failed to start splash page: {e}')

    try:
      logging.info('Starting AP...')
      check_call('sudo ip addr flush dev ap0', shell=True)
      check_call('sudo ifup ap0', shell=True)
      check_call('sudo ifdown ap0', shell=True)
      check_call('sudo ifup ap0', shell=True)
    except Exception as e:
      logging.debug(f'failed to start AP: {e}')

    try:
      logging.info('Starting nodogsplash...')
      check_call('sudo nodogsplash &> /etc/nodogsplash/log.txt &', shell=True,
        stdout=PIPE,
        stderr=STDOUT)
    except Exception as e:
      logging.debug(f'nodogsplash failed: {e}')


button = Button(24, hold_time=3, pull_up=False)
button.when_held = run_splash

try:
  logging.info("Button is ready...")
  pause()
except KeyboardInterrupt:
  close()