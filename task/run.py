import sys
import os
from datetime import datetime, timedelta
import multiprocessing
import signal
running_path = sys.path[0]
sys.path.append(os.path.normpath(os.path.join(running_path, '../')))
import time
from flask import Flask
import task.amazon as amazon
import task.fantasyard as fantasyard
from common.daemon import Daemon


_app = Flask(__name__)

# db_uri = 'sqlite:///{}'.format(os.path.normpath(os.path.join(running_path, '../kikk.db')))
db_uri = 'mysql+pymysql://root:521000@172.17.0.2/kikk'


def _init():
    amazon.init(_app, running_path, db_uri)
    fantasyard.init(_app, running_path, db_uri)


def import_order_process():
    amazon.insert_unshipped_order()
    fantasyard.create_shipment_by_batch()


def fulfill_order_process():
    fantasyard.update_tn_by_batch()
    amazon.upload_tracking_number()
    amazon.close_order()


def sync_competitive_prices_process():
    amazon.sync_competitive_prices()


def sync_listing_from_amazon_process():
    amazon.sync_listing_from_amazon()


def adjust_q4s_process():
    amazon.calculate_q4s()
    amazon.upload_q4s()


def adjust_price_process():
    amazon.calculate_price()
    amazon.upload_price()


def run_in_loop(fun, interval=1, is_running=None, init=None, *args, **kwargs):
    if init is not None:
        init()
    last_run_time = None
    delta_interval = timedelta(seconds=interval)
    while True:
        if is_running is not None and not is_running.value:
            break
        time.sleep(0.1)
        if last_run_time:
            delta = datetime.now() - last_run_time
            if delta < delta_interval:
                continue
        fun(*args, **kwargs)
        last_run_time = datetime.now()


def _test():
    print('test')


def _stop(sig, frame):
    print('stopping', sig)
    is_running.value = False

signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGQUIT, _stop)
# signal.signal(signal.SIGKILL, _stop)


def _start():
    global is_running
    is_running = multiprocessing.Value('b', True)
    p_list = [
              # multiprocessing.Process(target=run_in_loop, args=(_test, 2, is_running)),
              multiprocessing.Process(target=run_in_loop, args=(import_order_process, 300, is_running, _init)),
              multiprocessing.Process(target=run_in_loop, args=(fulfill_order_process, 3600, is_running, _init)),
              multiprocessing.Process(target=run_in_loop, args=(sync_competitive_prices_process, 60, is_running, _init)),
              multiprocessing.Process(target=run_in_loop, args=(sync_listing_from_amazon_process, 3600, is_running, _init)),
              multiprocessing.Process(target=run_in_loop, args=(adjust_q4s_process, 600, is_running, _init)),
              # multiprocessing.Process(target=run_in_loop, args=(adjust_price_process, 60, is_running)),
              ]
    for p in p_list:
        p.start()

    for p in p_list:
        p.join()


class TaskDaemon(Daemon):
    def run(self):
        _start()


if __name__ == '__main__':
    daemon = TaskDaemon(pidfile='/tmp/kikk.pid', stderr='kikk.err')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            raise Exception("Unknown command")
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
    # with daemon.DaemonContext():
    #     _start()
# while True:
    # amazon.insert_unshipped_order()
    # fantasyard.create_shipment_by_batch()
    # fantasyard.update_tn_by_batch()
    # amazon.upload_tracking_number()
    # amazon.close_order()
    # amazon.sync_competitive_prices()
    # time.sleep(10)
