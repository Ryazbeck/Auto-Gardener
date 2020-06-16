import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('smart-gardening.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

zones_ref = db.collection('zones')
# cukes_ref = zones_ref.document('cucumbers01')
# sensors_ref = cukes_ref.collection('sensors')

print(zones_ref.stream())
exit

for zone in zones_ref.stream():
    this_ref = zones_ref.document(zone.id)
    print(this_ref.id)
    # print(f'{zone.id} => {zone.to_dict()}')

# for sensor in sensors_ref.stream():
#     print(f'{sensor.id} => {sensor.to_dict()}')
#     moisture_ref = sensor.collection('moisture')
#     for moisture in moisture_ref.stream():
#         print(f'{moisture.id} => {moisture.to_dict()}')
