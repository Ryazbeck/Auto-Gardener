#!/usr/bin/env python
from gpiozero import Button
from subprocess import check_call, run, PIPE, STDOUT, Popen, check_output
from signal import pause
from os import path, remove, system
from time import sleep
import re
import logging

yg_dir = path.dirname(path.realpath(__file__))
logger = logging.basicConfig(
    filename=f'{yg_dir}/log/{path.basename(__file__)}.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

mac_address = check_output(
    'sudo cat /sys/class/net/wlan0/address',
    shell=True,
    encoding='utf8').replace('\n', '')

interfaces = f'''
source-directory /etc/network/interfaces.d

auto lo
iface lo inet loopback

allow-hotplug wlan0
iface wlan0 inet manual
        #wpa-roam /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
iface AP inet dhcp

allow-hotplug ap0
iface ap0 inet static
        pre-up ifdown --force wlan0
        pre-up iw phy phy0 interface add ap0 type __ap
        pre-up ip link set ap0 address {mac_address}
        post-up systemctl restart dnsmasq
        post-up ifup wlan0
        post-down iw dev ap0 del
        post-down systemctl stop dnsmasq
        address 192.168.100.1
        netmask 255.255.255.0
        hostapd /etc/hostapd/hostapd.conf
'''


def run_splash():
    # LED flashing yellow


    # configure interfaces
    try:
      logging.info("Updating /etc/network/interfaces...")
      interfaces_file = open('/etc/network/interfaces', 'w')
      interfaces_file.write(interfaces)
      interfaces_file.close()
    except Exception as e:
      logging.debug(f'Failed to update interfaces: {e}')
      exit()


    # start wlan and ap
    try:
        logging.info('Starting wlan0 and ap0')
        check_call('sudo ifup ap0', shell=True)
    except Exception as e:
        logging.debug(f'failed to start WLAN: {e}')


    # NDS will trigger the CPD popup
    try:
        logging.info('Starting nodogsplash')
        nds = check_call(
            f'sudo nodogsplash &> {yg_dir}/log/nds.log',
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            encoding='utf8')
        logging.info(nds)
    except Exception as e:
        logging.debug(f'nodogsplash failed: {e}')


    # serve page to NDS
    def start_splash():
        logging.info('Starting splash page')
        check_call(
            f'sudo -E python3 {yg_dir}/portal.py &', shell=True)

    try:
        start_splash()
    except Exception as e:
        logging.debug(f'failed to start splash page: {e}')


    # LED solid green


button = Button(24, hold_time=3, pull_up=False)
button.when_held = run_splash

try:
    logging.info("Button is ready...")
    pause()
except KeyboardInterrupt:
    exit()
