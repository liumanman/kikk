from selenium import webdriver
from bs4 import BeautifulSoup
import time
import functools

import os, sys
import configparser

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

# config = configparser.ConfigParser()
config = configparser.RawConfigParser()
config.read('fantasyard.ini')
_email = config['Default']['email'] 
_password = config['Default']['password'] 
_cookie = config['Default']['cookie']

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

import requests
s = requests.Session()
s.mount('https://', MyAdapter())

_url_for_inventory = ['https://www.fantasyard.com/portal/itemreport.php?page=1&category=290',
           'https://www.fantasyard.com/portal/itemreport.php?page=2&category=290',
           'https://www.fantasyard.com/portal/itemreport.php?page=3&category=290',
           'https://www.fantasyard.com/portal/itemreport.php?page=4&category=290']
_url_for_single_item_inventory = 'https://www.fantasyard.com/portal/itemreport.php?keyword={}'
_headers_for_inventory_request = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
    'Cookie': _cookie 
}
_request_get_inventory = functools.partial(s.get, headers=_headers_for_inventory_request)

_shipment_page_url = 'https://www.fantasyard.com/index.php?dispatch=orders.details&order_id={}'

def _init_driver():
    # driver = webdriver.Firefox()
    driver = webdriver.PhantomJS()
    driver.implicitly_wait(30)
    driver.base_url = "http://www.fantasyard.com"
    driver.verificationErrors = []
    driver.accept_next_alert = True
    driver.get(driver.base_url + "/")
    return driver


def _login(driver):
    _logger.info('login....')
    driver.find_element_by_id("sw_login").click()
    driver.find_element_by_id("psw_").clear()
    driver.find_element_by_id("psw_").send_keys(_password)
    driver.find_element_by_id("login_").clear()
    driver.find_element_by_id("login_").send_keys(_email)
    driver.find_element_by_name("dispatch[auth.login]").click()

def _create_shipment(order):
    driver = _init_driver()
    _login(driver)

    # driver.get(self.base_url + "/jansport-superbreak-school-backpack-multi-blue-drip-dye.html")
    _logger.info('clear cart...')
    time.sleep(3)
    driver.get(driver.base_url + '/index.php?dispatch=checkout.clear')  # clear cart
    time.sleep(3)
    _logger.info('Add to cart...')
    driver.get(order.item.product_url)
    _check_cart_empty(driver)
    driver.find_element_by_css_selector('div.center.valign.cm-value-changer > input').clear()
    driver.find_element_by_css_selector('div.center.valign.cm-value-changer > input').send_keys(order.qty)
    driver.find_element_by_css_selector('div.buttons-container.nowrap > div > span > span > input').click()
    time.sleep(6)
    _logger.info('Checkout...')
    driver.find_element_by_link_text("Checkout").click()
    driver.find_element_by_id("coupon_field").clear()
    driver.find_element_by_id("coupon_field").send_keys("DROPSHIP")
    driver.find_element_by_link_text("Apply").click()
    driver.find_element_by_css_selector("span.button-action > a").click() # checkout
    driver.find_element_by_css_selector("span.button-tool > a.cm-ajax.cm-ajax-force").click()
    # driver.find_element_by_id("elm_15").click()
    driver.find_element_by_id("elm_15").clear()
    driver.find_element_by_id("elm_15").send_keys(order.customer_name)
    # driver.find_element_by_id("elm_17").click()
    driver.find_element_by_id("elm_17").clear()
    driver.find_element_by_id("elm_17").send_keys(" ")
    # driver.find_element_by_id("elm_19").click()
    driver.find_element_by_id("elm_19").clear()
    driver.find_element_by_id("elm_19").send_keys(order.shipping_address)
    driver.find_element_by_id("elm_21").clear()
    driver.find_element_by_id("elm_21").send_keys(order.shipping_address2)
    driver.find_element_by_id("elm_23").clear()
    driver.find_element_by_id("elm_23").send_keys(order.shipping_city)
    # driver.find_element_by_id("elm_25").click()
    driver.find_element_by_css_selector("#elm_25 > option[value=\"" + order.shipping_state + "\"]").click()
    driver.find_element_by_id("elm_29").clear()
    driver.find_element_by_id("elm_29").send_keys(order.shipping_zipcode)
    driver.find_element_by_name("dispatch[checkout.update_steps]").click()

    # driver.find_element_by_link_text("Continue").click()
    # driver.find_element_by_id("step_three_but").click()
    driver.find_element_by_css_selector("span.button > a").click()


    driver.find_element_by_name("customer_notes").clear()
    driver.find_element_by_name("customer_notes").send_keys(order.source_id)
    screenshot_path = os.path.join(sys.path[0], 'screenshot/', '{}.png'.format(order.order_id))
    # print(screenshot_path)
    driver.get_screenshot_as_file(screenshot_path)
    # choice = input('Confirm to place order?')
    choice = 'y'
    if choice == 'y':
        driver.find_element_by_id('place_order').click()
        for i in range(10):
            time.sleep(3)
            current_url = driver.current_url
            _logger.info(current_url)
            index = current_url.find('order_id=')
            if index > -1:
                shipment_id = current_url[index + 9:]
                if not shipment_id:
                    raise Exception('Fail to get shipment_id')
                update_shipment(order.order_id, shipment_id)
                driver.quit()
                return shipment_id
        raise Exception('Fail to read the fantasyard order id')
    raise Exception('Abort Exception')


def _check_cart_empty(driver):
    t = driver.find_element_by_css_selector("strong").text
    if t.strip().lower() != 'cart is empty':
        raise Exception('The cart is not empty.')
        # driver.find_element_by_link_text("Checkout").click()
        # driver.find_element_by_link_text("Clear Cart").click()
        # self.assertRegexpMatches(self.close_alert_and_get_its_text(), r"^Are you sure you want to proceed[\s\S]$")


def create_shipment_by_batch():
    order_list = get_open_orders()
    for order in order_list:
        try:
            shipment_id = _create_shipment(order)
        except Exception as e:
            # _logger.error('Fail to create shipment for order {}'.format(order.order_id))
            new_e = Exception('Fail to create shipment for order {}'.format(order.order_id), e)
            _logger.exception(new_e)
        else:
            _logger.info('Success: {0} {1}'.format(order, shipment_id))

def update_tracking_number(order_id, driver):
    order =  get_by_id(order_id)
    if not order:
        raise Exception("Can't find order {}".format(order_id))
    tracking_data_list = _dowload_tracking_number(order.shipment_id, driver)
    if tracking_data_list:
        update_tn(order_id, *tracking_data_list)
    return [td.tracking_number for td in tracking_data_list] 

def update_tn_by_batch():
    order_list = get_ship_ready_order()
    if not order_list:
        return
    driver = _init_driver()
    _login(driver)
    for order in order_list:
        try:
            tn_list = update_tracking_number(order.order_id, driver)
        except Exception as e:
            # _logger.error('Fail to update tracking number for order {}'.format(order.order_id))
            new_e = Exception('Fail to update tracking number for order {}'.format(order.order_id), e)
            _logger.exception(new_e)
        else:
            _logger.info('Success: {} {}'.format(order, tn_list))

# def _dowload_tracking_number_old(shipment_id, driver):
#     html = _download_shipment_page(shipment_id, driver)
#     bs = BeautifulSoup(html, 'html.parser')
#     for link in bs.find_all('a'):
#         href = link.get('href')
#         if href and href.startswith('http://trkcnfrm1.smi.usps.com'):
#             return href.split('=')[-1].strip()
#     return None


def _dowload_tracking_number(shipment_id, driver):
    html = _download_shipment_page(shipment_id, driver)
    # print(html)
    bs = BeautifulSoup(html, 'html.parser')
    div = bs.find_all(name='div', id='content_shipment_info')[0]

    tracking_number_list = []
    tables = div.find_all('table')
    for i in range(len(tables)):
        qty = tables[i].find_all('td')[1].string.strip()
        p = div.find_all('p', recursive=False)[i]
        tracking_number = p.select('a')[0].string
        shipping_method = p.select('br')[0].contents[0].string.split('(')[0].strip()

        tn = type('', (object,), {})()
        tn.qty = qty
        tn.tracking_number = tracking_number
        tn.shipping_method = shipping_method
        tn.carrier = 'USPS'

        tracking_number_list.append(tn)
    return tracking_number_list


def _download_shipment_page(shipment_id, driver):
    # res = requests.get(_shipment_page_url.format(shipment_id), headers=_headers)
    # if res.status_code != 200:
    #     raise Exception('Fail to download shipment page. Code[{}]'.res.status_code)
    # return res.text

    # driver = _init_driver()
    # _login(driver)
    driver.get(_shipment_page_url.format(shipment_id))
    return driver.page_source


def get_inventory_data(item_id=None):
    inventory_data = {}
    url = [_url_for_single_item_inventory.format(item_id)] if item_id else _url_for_inventory
    for response in map(_request_get_inventory, url):
        data = _read_inventory_from_html(response.text)
        inventory_data.update(data)
    return inventory_data[item_id] if item_id else inventory_data
  

def _read_inventory_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('table')[1].find_all('tr', class_='table-row')
    if not rows:
        raise Exception('Fail to get inventory data.')
    result = {}
    for row in rows:
        tds = row.find_all('td', recursive=False)
        result[tds[3].string.strip()] = int(tds[6].string.strip())
    return result

def init(flask_app, moduel_path, db_uri, logger):
    import sys
    sys.path.append(moduel_path)
    from model.database import init_db

    init_db(flask_app, db_uri)
    # from service.order import get_by_source_id, update_shipment, get_open_orders, get_by_id, update_tracking_number as update_tn, get_ship_ready_order
    import service.order as order_svc
    global _logger, get_by_source_id, update_shipment, get_open_orders, get_by_id, update_tn, get_ship_ready_order
    _logger = logger
    get_by_source_id = order_svc.get_by_source_id
    update_shipment = order_svc.update_shipment
    get_open_orders = order_svc.get_open_orders
    get_by_id = order_svc.get_by_id
    update_tn = order_svc.update_tracking_number
    get_ship_ready_order = order_svc.get_ship_ready_order


if __name__ == '__main__':
    # import sys
    # sys.path.append('../')
    # from flask import Flask
    # from model.database import init_db

    # app = Flask(__name__)
    # init_db(app, uri='sqlite:///../kikk.db')

    # from service.order import get_by_source_id, update_shipment, get_open_orders, get_by_id, update_tracking_number as update_tn, get_ship_ready_order
    sys.path.append('../')

    import common.log as logging
    logging.config('logger.config', 'task')

    from flask import Flask
    _app = Flask(__name__)

    init(_app, '../', 'sqlite:///../kikk.db', logging.logger)

    # create_shipment_by_batch()

    # update_tn_by_batch()
    inventory = get_inventory_data()
    print(len(inventory))



