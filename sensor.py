
from google.cloud import firestore
# from grove_moisture_sensor import GroveMoistureSensor

class Sensor:
  def __init__(self, pin, sensor_id, user_id, zone_id, db):
    self.pin = pin
    self.sensor_id = sensor_id
    self.user_id = user_id
    self.zone_id = zone_id
    self.db = db

  @staticmethod
  def compute_moisture(pin):
    pass
    # from grove.helper import SlotHelper
    # sh = SlotHelper(SlotHelper.ADC)
    # pin = sh.argv2pin()

    # sensor = GroveMoistureSensor(pin)

    # print('Detecting moisture...')
    # while True:
    #     m = sensor.moisture
    #     if 0 <= m and m < 300:
    #         result = 'Dry'
    #     elif 300 <= m and m < 600:
    #         result = 'Moist'
    #     else:
    #         result = 'Wet'
    #     print('Moisture value: {0}, {1}'.format(m, result))
    #     time.sleep(1)


  def post_to_firestore(self):
    self.db.collection('moisture').add({
      'created': firestore.SERVER_TIMESTAMP,
      'sensor_id': self.sensor_id,
      'user_id': self.user_id,
      'value': 45,
      # 'value': self.compute_moisture(self.pin),
      'zone_id': self.zone_id
    })
