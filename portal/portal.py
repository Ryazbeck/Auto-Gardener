from bottle import Bottle, template, get, post, request
from gevent import sleep, monkey; monkey.patch_all()
from os import remove
import subprocess
import logging

# logging.basicConfig(filename=f'{__name__}.log', level=logging.INFO)
logging.basicConfig(filename=f'{__file__}.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

stage = None
username = None
password = None

app = Bottle()

@app.get('/')
def set_stage():
  logger.info('Loading wifi config page')
  global stage

  # Get SSIDs found on wlan0
  proc = subprocess.Popen('nmcli -f SSID device wifi | grep -vE "(SSID|--)"',
    shell=True, 
    stdout=subprocess.PIPE, 
    encoding='utf8')

  # clean up SSIDs
  ssids = [x.replace("\n", "").rstrip() for x in proc.stdout.readlines()]
  logger.info(f'SSIDs found:')
  logger.info(f'{",".join(ssids)}')

  return template('index.html', root='/home/pi', stage=stage, ssids=ssids, message='none')

@app.post('/')
def post():
  logger.info(f'Form submitted')
  if request.forms:
    if request.forms.get('username') is None:
      message = 'SSID was not selected'
      logger.info(message)
      return template('index.html', root='/home/pi', stage=stage, message=message)
    elif request.forms.get('password') is None:
      message = 'Key was not submitted'
      logger.info(message)
      return template('index.html', root='/home/pi', stage=stage, message=message)
    else:
      logger.info(f'Wifi SSID and key submitted')
      global stage, username, password, interfaces
      username = request.forms.get('username')
      password = request.forms.get('password')
      message = None
  exit()

    def make_wpa_supplicant(un,pw):
      return f'''
        ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev
        update_config=1
        network={{
          ssid="{un}"
          psk="{pw}"
        }}
        '''

    def failed(message):
      stage = None
      message = message
      logger.debug(message)

    # update wpa_supplicant
    try:
      logger.info(f'Updating wpa_supplicant-wlan0.conf')
      wpa_supplicant = open('/etc/wpa_supplicant/wpa_supplicant-wlan0.conf', 'w')
      wpa_supplicant.write(make_wpa_supplicant(username, password))
      wpa_supplicant.close()
    except Exception as e:
      failed(f'Updating wpa_supplicant-wlan0.conf failed: {e}')
      return template('index.html', root='/home/pi', stage=stage, message=message)

    # bounce wlan0
    try:
      logger.info(f'Restarting wpa_supplicant@wlan0.service')
      subprocess.check_call('sudo systemctl restart wpa_supplicant@wlan0.service', shell=True)
      logger.info(f'systemctl daemon-reload')
      subprocess.check_call('sudo systemctl daemon-reload', shell=True)
    except Exception as e:
      failed(f'Restarting wlan0 failed: {e}')
      return template('index.html', root='/home/pi', stage=stage, message=message)
    
    # ping test
    try:
      logger.info(f'Verifying connectivity...')
      ping = subprocess.check_call('timeout 3 ping -c 1 8.8.8.8', 
        shell=True, 
        encoding='utf8')
      logger.info(f'Success')
      stage = 'established'
    except Exception as e:
      failed(f'Ping test failed: {e}')
      return template('index.html', root='/home/pi', stage=stage, message=message)

    # update /etc/network/interfaces
    try:
      logger.info(f'Removing ap0 from interfaces')
      interfaces_file = open('/etc/network/interfaces', 'w')
      interfaces = f'''
        source-directory /etc/network/interfaces.d

        auto lo
        iface lo inet loopback

        allow-hotplug wlan0
        iface wlan0 inet dhcp
                wpa-conf /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
        '''
      interfaces_file.write(interfaces)
      interfaces_file.close()
    except Exception as e:
      failed(f'Updating interfaces file failed: {e}')
      return template('index.html', root='/home/pi', stage=stage, message=message)

    # remove udev file for ap0
    try:
      logging.info('Removing udev for ap0')
      remove('/etc/udev/rules.d/70-persistent-net.rules')
      logging.info('Disabling hotspot in 10 seconds...')
      command = 'bash -c \'sleep 10 && sudo reboot now\' &'
      subprocess.check_call(command, shell=True)
    except Exception as e:
      failed(f'Failed to disable hotspot: {e}')

  return template('index.html', root='/home/pi', stage=stage, message='none')


if __name__ == '__main__':
  logger.info('Starting wifi config portal')
  app.run(host='0.0.0.0', port=8000, server='gevent')
