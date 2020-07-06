from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
import os
from time import sleep
from os import path, getcwd
import subprocess

app = Flask(__name__, static_url_path='/')
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

'''
This enables interacting with the Pi directly so we can 
- Enable and disable hotspot
- Configure wpa_supplicant.conf for user's wi-fi
- Confirm connection is established
- docker-compose down once everything is configured
'''

@app.route('/')
def index():
    return render_template('index.html')


def run_shell_command(cmd):
  subprocess.run(cmd, shell=True)
  

def hotspot(status):
  if status == 'start':
    print("Starting ap0...")
    run_shell_command("ifdown --force wlan0")
    run_shell_command("ifdown --force ap0")

    ap0_file = "/var/run/hostapd/ap0"
    if path.exists(ap0_file):
      os.remove(ap0_file)
    
    run_shell_command("ifup ap0")
    run_shell_command("ifup wlan0")
    run_shell_command("sysctl -w net.ipv4.ip_forward=1")
    run_shell_command("iptables -t nat -A POSTROUTING -s 192.168.100.0/24 ! -d 192.168.100.0/24 -j MASQUERADE")
    run_shell_command("systemctl restart dnsmasq")

  elif status == 'stop':
    return run_shell_command("ifdown --force ap0")

  return jsonify('Status must equal either "start" or "stop"')


def restart_wlan0():
  print("Restarting wlan0...")
  return run_shell_command("ifdown --force wlan0 && ifup wlan0")


def check_ping():
  response = os.system("ping -c 1 8.8.8.8")
  if response == 0:
      return True
  return False

@app.route('/wifi_creds')
def wifi_creds():
  print("Setting up wi-fi creds for wlan0...")
  ssid = request.args.get('ssid', None)
  key = request.args.get('key', None)

  # open wpa_supplicant.conf and write creds to it
  if ssid and key:
    connected = False
    try:
      with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as wpa_supplicant:
        conf = f'''
          network={{
            ssid="{ssid}"
            scan_ssid=1
            key_mgmt=WPA-PSK
            psk="{key}"
          }}
        '''
        wpa_supplicant.write()
        wpa_supplicant.close()

      restart_wlan0()

      for i in range(10):
        if check_ping():
          message = ['Success: Connection established.']
          message.append('Hotspot will be disabled in 10 seconds.')
          hotspot('stop')
          return jsonify(message=' '.join(message))
        sleep(3)

      return jsonify(message='Failure: unable to establish connection.')

    except:
      return jsonify(message='Unknown error, unable to establish connection.')
  else:
    return jsonify(message='Failure: Wifi SSID and Key were not provided')
  

if __name__ == '__main__':
  # hotspot('start')
  print("testing")
  app.run(debug=True, host='0.0.0.0', port=5001)
