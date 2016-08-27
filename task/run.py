import sys
import os
import time
from flask import Flask
import task.amazon as amazon
import task.fantasyard as fantasyard
import common.log as logging

running_path = sys.path[0]

logging.config(os.path.join(running_path, 'task.log'), 'task')

_app = Flask(__name__)

db_uri = 'sqlite:///{}'.format(os.path.join(running_path, 'kikk.db'))

amazon.init(_app, running_path, db_uri, logging.logger)
fantasyard.init(_app, running_path, db_uri, logging.logger)

while True:
    amazon.insert_unshipped_order()
    fantasyard.create_shipment_by_batch()
    fantasyard.update_tn_by_batch()
    amazon.upload_tracking_number()
    amazon.close_order()
    time.sleep(5 * 60)
