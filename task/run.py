import sys
import os
import time
from flask import Flask
import amazon
import fantasyard

_app = Flask(__name__)

running_path = sys.path[0]
db_uri = 'sqlite:///{}'.format(os.path.join(running_path, 'kikk.db'))

amazon.init(_app, running_path, db_uri)
fantasyard.init(_app, running_path, db_uri)

while True:
    amazon.insert_unshipped_order()
    fantasyard.create_shipment_by_batch()
    fantasyard.update_tn_by_batch()
    amazon.upload_tracking_number()
    time.sleep(5 * 60)
