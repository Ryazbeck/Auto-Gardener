#! /etc/yarden-gnome-station/portal/venv/bin/python3
from gpiozero import Button
from subprocess import check_call, run, PIPE, STDOUT, Popen, check_output
from signal import pause
from os import path, remove, system
from time import sleep
from systemd.journal import JournaldLogHandler
import re
import logging

# setup logger
logger = logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# log to systemd
journald_handler = JournaldLogHandler()
journald_handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(message)s'
))
logger.addHandler(journald_handler)

def get_mac_address():
    try:
        return check_output(
            'cat /sys/class/net/wlan0/address',
            shell=True,
            encoding='utf8').replace('\n', '')
    except Exception as e:
        return None
        logger.error(e)

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
        pre-up ip link set ap0 address {get_mac_address}
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
    def configure_interfaces():
        try:
        logging.info("Updating /etc/network/interfaces...")
        interfaces_file = open('/etc/network/interfaces', 'w')
        interfaces_file.write(interfaces)
        interfaces_file.close()
        except Exception as e:
        logging.debug(f'Failed to update interfaces: {e}')
        exit()

    # start wlan and ap
    def start_ap():
        try:
            logging.info('Starting wlan0 and ap0')
            check_call('sudo ifup ap0', shell=True)
        except Exception as e:
            logging.debug(f'failed to start WLAN: {e}')

    # NDS will trigger the CPD popup
    def start_nodogsplash():
        try:
            logging.info('Starting nodogsplash')
            nds = check_call(
                f'sudo nodogsplash &> log/nds.log',
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
            f'sudo -E python3 log/portal.py &', shell=True)

    try:
        configure_interfaces()
        start_ap()
        start_nodogsplash()
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
