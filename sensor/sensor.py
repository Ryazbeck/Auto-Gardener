
from google.cloud import firestore
from grove.adc import ADC
import time

class Sensor:
  def __init__(self, channel, manuf, sensor_type, sensor_id, user_id, zone_id, db):
    self.channel = channel
    self.manuf = manuf
    self.sensor_type = sensor_type
    self.sensor_id = sensor_id
    self.user_id = user_id
    self.zone_id = zone_id
    self.db = db
    self.adc = ADC()


  @property
  def voltage(self):
    return self.adc.read_voltage(self.channel)


  @property
  def percentage(self):
    voltage = self.voltage
    if self.sensor_type == 'moisture':
      if self.manuf == 'seeed':
        return self.calculate_percentage(1300,2000,voltage)
      else:
        return self.calculate_percentage(1130,2400,voltage)
    if self.sensor_type == 'sunlight':
      return self.calculate_percentage(20,3260,voltage)


  def calculate_percentage(self, min, max, input):
    range = max - min
    correctedStartValue = input - min
    percentage = int((1 - (correctedStartValue / range)) * 100)
    if percentage < 0:
        return 0
    elif percentage > 100:
        return 100
    return percentage


  def post_to_firestore(self):
    self.db.collection('moisture').add({
      'created': firestore.SERVER_TIMESTAMP,
      'sensorId': self.sensor_id,
      'userId': self.user_id,
      'value': self.percentage,
      'zoneId': self.zone_id
    })