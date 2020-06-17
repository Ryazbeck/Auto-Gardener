import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from sensor import Sensor
import yaml

def load_sensor_config(filename):
  with open(filename, 'r') as stream:
    try:
      return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)

def request_sensors(sensors, db):
  for sensor in sensors:
    pin = sensors[sensor]['pin']
    user_id = sensors[sensor]['userId']
    zone_id = sensors[sensor]['zoneId']
    _sensor = Sensor(pin, sensor, user_id, zone_id, db)
    print('sensor', _sensor)
    _sensor.post_to_firestore()
    print('destruct', pin, sensor, user_id, zone_id)

def get_db(auth_file):
    creds = credentials.Certificate(auth_file)
    firebase_admin.initialize_app(creds)
    db = firestore.client()
    return db

config = load_sensor_config('config.yaml')
auth_file = config['auth_file']
db = get_db(auth_file)
sensors = config['sensors']
request_sensors(sensors, db)