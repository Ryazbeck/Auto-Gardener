import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import yaml

from apscheduler.schedulers.blocking import BlockingScheduler

from get_sensors import read_and_store_sensor

def load_sensor_config(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def schedule_sensor_readings(sched, sensors, db):
    for sensor_id in sensors:
        sensor_data = sensors[sensor_id]
        doc_ref = db.collection('sensors').document(sensor_id)
        doc = doc_ref.get()
        doc_dict = doc.to_dict()
        sched.add_job(
            func=read_and_store_sensor, 
            trigger='interval', 
            args=[sensor_id, sensor_data, db], 
            minutes=doc_dict['intervalMin'], 
            name=sensor_id
        )

config = load_sensor_config('./config.yaml')
sensors = config['sensors']

creds = credentials.Certificate(config['auth_file'])
firebase_admin.initialize_app(creds)
db = firestore.client()

sched = BlockingScheduler()

schedule_sensor_readings(sched, sensors, db)

sched.start()