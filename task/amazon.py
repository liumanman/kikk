import sys
from boto.mws import connection
from dateutil import parser as tp
import time
import datetime
from jinja2 import Template
import requests
from bs4 import BeautifulSoup
import task.fantasyard as fantasyard

merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'
source = 'Amazon'
order_fulfillment_template = 'order_fulfillment_template.xml'
adjust_q4s_bypass_list = ['T50109P', 'T50109P-2']

headers_for_get_prices = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def _submit_feed(feed_type, feed_content):
    conn = connection.MWSConnection(Merchant=merchant_id)
    feed = conn.submit_feed(
        FeedType=feed_type,
        PurgeAndReplace=False,
        MarketplaceIdList=[marketplace_id],
        content_type='text/xml',
        FeedContent=feed_content.encode('utf-8')
    )

    feed_info = feed.SubmitFeedResult.FeedSubmissionInfo
    _logger.info('Submitted product feed: ' + str(feed_info))
    # print(feed_info.FeedSubmissionId)

    while True:
        submission_list = conn.get_feed_submission_list(
            FeedSubmissionIdList=[feed_info.FeedSubmissionId]
        )
        info = submission_list.GetFeedSubmissionListResult.FeedSubmissionInfo[0]
        id = info.FeedSubmissionId
        status = info.FeedProcessingStatus
        _logger.info('Submission Id: {}. Current status: {}'.format(id, status))

        if status in ('_SUBMITTED_', '_IN_PROGRESS_', '_UNCONFIRMED_'):
            _logger.info('Sleeping and check again....')
            time.sleep(60)
        elif status == '_DONE_':
            feed_result = conn.get_feed_submission_result(FeedSubmissionId=id)
            _logger.debug(feed_result)
            # _logger.info('{} tracking number(s) uploaded.'.format(len(tn_list)))
            break
        else:
            _logger.error("Submission processing error. Status: {}".format(status))
            break


def _sku_to_item_id(sku):
    return sku.split('-')[0]


def insert_unshipped_order():
    conn = connection.MWSConnection(Merchant=merchant_id)

    kw = {
        'CreatedAfter': '2016-07-01T18:12:21',
        'MarketplaceId': [marketplace_id],
        'OrderStatus': ['Unshipped', 'PartiallyShipped']
    }
    order_list = conn.list_orders(**kw).ListOrdersResult.Orders.Order
    for order in order_list:
        if not get_by_source_id(source, order.AmazonOrderId):
            shipping_state = _short_state(order.ShippingAddress.StateOrRegion)
            item_list = conn.list_order_items(
                AmazonOrderId=order.AmazonOrderId).ListOrderItemsResult.OrderItems.OrderItem
            order_date = tp.parse(order.PurchaseDate).astimezone()
            for item in item_list:
                try:
                    # item_id = item.SellerSKU.split('-')[0]
                    item_id = _sku_to_item_id(item.SellerSKU)
                    insert_order(source=source, source_id=order.AmazonOrderId, order_date=order_date, item_id=item_id,
                                 price=int(float(item.ItemPrice.Amount) * 100) / int(item.QuantityOrdered),
                                 qty=item.QuantityOrdered, customer_name=order.ShippingAddress.Name,
                                 shipping_address=order.ShippingAddress.AddressLine1,
                                 shipping_address2='{0} {1}'.format(getattr(order.ShippingAddress, 'AddressLine2', ''),
                                                                    getattr(order.ShippingAddress, 'AddressLine3', '')),
                                 shipping_city=order.ShippingAddress.City,
                                 shipping_state=shipping_state,
                                 shipping_zipcode=order.ShippingAddress.PostalCode,
                                 shipping_full_addr=_addr_to_str(order.ShippingAddress),
                                 order_item_id=item.OrderItemId)
                    _logger.info('Insert order: order# {0}, item# {1}'.format(order.AmazonOrderId, item.SellerSKU))
                except Exception as e:
                    # _logger.error('Exception with order# {0}, item# {1}'.format(order.AmazonOrderId, item.SellerSKU))
                    new_e = Exception(
                        'Fail to insert order# {0}, item# {1}'.format(order.AmazonOrderId, item.SellerSKU), e)
                    _logger.exception(new_e)
                time.sleep(1)


def _addr_to_str(address):
    attr_list = dir(address)
    addr_str = '{0}\n{1}'.format(address.Name, address.AddressLine1)
    if 'AddressLine2' in attr_list:
        addr_str = addr_str + '\n' + address.AddressLine2
    if 'AddressLine3' in attr_list:
        addr_str = addr_str + '\n' + address.AddressLine3
    addr_str += '\n{0},{1} {2}'.format(address.City, address.StateOrRegion, address.PostalCode)
    return addr_str


def _short_state(state):
    if state.title() in _states:
        return _states[state.title()]
    state = state.replace('.', '')
    if state.upper() in _states.values():
        return state.upper()
    raise Exception('Invalid state {}'.format(state))


def close_order():
    local_order_list = get_shipped_order()
    if not local_order_list:
        return
    source_id_list = list(set([order.source_id for order in local_order_list]))
    conn = connection.MWSConnection(Merchant=merchant_id)
    order_list = conn.get_order(AmazonOrderId=source_id_list).GetOrderResult.Orders.Order
    order_dict = {order.AmazonOrderId: order for order in order_list}

    n = 0
    for order in local_order_list:
        if order_dict[order.source_id].OrderStatus == 'Shipped':
            try:
                close_order_by_id(order.order_id)
            except Exception as e:
                _logger.error('Fail to close order {}'.format(order.order_id))
                _logger.exception(e)
            else:
                n += 1
    _logger.info('{} order(s) are closed.'.format(n))


def upload_tracking_number():
    tn_list = list(get_open_tracking_number())
    if not tn_list:
        return
    with open(order_fulfillment_template) as fd:
        xml_template = fd.read()
    template = Template(xml_template)
    feed_content = template.render(tracking_number_list=tn_list)

    _submit_feed('_POST_ORDER_FULFILLMENT_DATA_', feed_content)
    _logger.info('{} tracking number(s) uploaded.'.format(len(tn_list)))

    # conn = connection.MWSConnection(Merchant=merchant_id)
    # feed = conn.submit_feed(
    #     FeedType='_POST_ORDER_FULFILLMENT_DATA_',
    #     PurgeAndReplace=False,
    #     MarketplaceIdList=[marketplace_id],
    #     content_type='text/xml',
    #     FeedContent=feed_content.encode('utf-8')
    # )

    # feed_info = feed.SubmitFeedResult.FeedSubmissionInfo
    # _logger.info('Submitted product feed: ' + str(feed_info))
    # # print(feed_info.FeedSubmissionId)

    # while True:
    #     submission_list = conn.get_feed_submission_list(
    #         FeedSubmissionIdList=[feed_info.FeedSubmissionId]
    #     )
    #     info =  submission_list.GetFeedSubmissionListResult.FeedSubmissionInfo[0]
    #     id = info.FeedSubmissionId
    #     status = info.FeedProcessingStatus
    #     _logger.info('Submission Id: {}. Current status: {}'.format(id, status))

    #     if status in ('_SUBMITTED_', '_IN_PROGRESS_', '_UNCONFIRMED_'):
    #         _logger.info('Sleeping and check again....')
    #         time.sleep(60)
    #     elif status == '_DONE_':
    #         feedResult = conn.get_feed_submission_result(FeedSubmissionId=id)
    #         _logger.debug(feedResult)
    #         _logger.info('{} tracking number(s) uploaded.'.format(len(tn_list)))
    #         break
    #     else:
    #         _logger.error("Submission processing error. Status: {}".format(status))
    #         break


_states = dict()
_states['Alabama'] = 'AL'
_states['Alaska'] = 'AK'
_states['Arizona'] = 'AZ'
_states['Arkansas'] = 'AR'
_states['California'] = 'CA'
_states['Colorado'] = 'CO'
_states['Connecticut'] = 'CT'
_states['Delaware'] = 'DE'
_states['Florida'] = 'FL'
_states['Georgia'] = 'GA'
_states['Hawaii'] = 'HI'
_states['Idaho'] = 'ID'
_states['Illinois'] = 'IL'
_states['Indiana'] = 'IN'
_states['Iowa'] = 'IA'
_states['Kansas'] = 'KS'
_states['Kentucky'] = 'KY'
_states['Louisiana'] = 'LA'
_states['Maine'] = 'ME'
_states['Maryland'] = 'MD'
_states['Massachusetts'] = 'MA'
_states['Michigan'] = 'MI'
_states['Minnesota'] = 'MN'
_states['Mississippi'] = 'MS'
_states['Missouri'] = 'MO'
_states['Montana'] = 'MT'
_states['Nebraska'] = 'NE'
_states['Nevada'] = 'NV'
_states['New Hampshire'] = 'NH'
_states['New Jersey'] = 'NJ'
_states['New Mexico'] = 'NM'
_states['New York'] = 'NY'
_states['North Carolina'] = 'NC'
_states['North Dakota'] = 'ND'
_states['Ohio'] = 'OH'
_states['Oklahoma'] = 'OK'
_states['Oregon'] = 'OR'
_states['Pennsylvania'] = 'PA'
_states['Rhode Island'] = 'RI'
_states['South Carolina'] = 'SC'
_states['South Dakota'] = 'SD'
_states['Tennessee'] = 'TN'
_states['Texas'] = 'TX'
_states['Utah'] = 'UT'
_states['Vermont'] = 'VT'
_states['Virginia'] = 'VA'
_states['Washington'] = 'WA'
_states['West Virginia'] = 'WV'
_states['Wisconsin'] = 'WI'
_states['Wyoming'] = 'WY'


def _insert_single_listing(listing_from_amazon):
    listing_dict = {'listing_source_id': listing_from_amazon['listing-id'], 'listing_source': source,
                    'item_id': _sku_to_item_id(listing_from_amazon['seller-sku']),
                    'sku': listing_from_amazon['seller-sku'], 'q4s': listing_from_amazon['quantity'],
                    'price': int(float(listing_from_amazon['price']) * 100),
                    'pending_qty': int(listing_from_amazon['pending-quantity']),
                    'source_item_id': listing_from_amazon['asin1'],
                    'listing_date': tp.parse(listing_from_amazon['open-date']).astimezone(),
                    'qty': listing_from_amazon.get('qty', None)}

    # listing = Listing(**listing_dict)
    # listing.insert()
    insert_listing(**listing_dict)


def _get_listing_data_from_amazon():
    conn = connection.MWSConnection(Merchant=merchant_id)
    request_resp = conn.request_report(ReportType='_GET_MERCHANT_LISTINGS_DATA_')
    request_id = request_resp.RequestReportResult.ReportRequestInfo.ReportRequestId
    # request_status = request_resp.RequestReportResult.ReportRequestInfo.ReportProcessingStatus
    # report_id = None
    while True:
        request_result = conn.get_report_request_list(ReportRequestIdList=[request_id])
        info = request_result.GetReportRequestListResult.ReportRequestInfo[0]
        id = info.ReportRequestId
        status = info.ReportProcessingStatus
        if status in ('_SUBMITTED_', '_IN_PROGRESS_'):
            _logger.info('Sleeping and check again....')
            time.sleep(60)
        elif status in ('_DONE_', '_DONE_NO_DATA_'):
            report_id = info.GeneratedReportId
            break
        else:
            # print("Report processing error. Quit.", status)
            raise Exception('Report processing error: {}'.format(status))

    _logger.info('report id: {}'.format(report_id))
    report = conn.get_report(ReportId=report_id)

    # with open('report', 'b+w') as fd:
    #     fd.write(report)
    lines = report.decode('ISO-8859-1').strip().split('\n')
    column_names = lines[0].split('\t')
    # for column in column_names:
    #     print(column)
    item_qty_in_pending = _get_item_qty_in_pending()
    listing_data = []
    item_listing_qty = {}
    for i in range(1, len(lines)):
        v_list = lines[i].split('\t')
        listing_data.append({column_names[j]: v_list[j] for j in range(len(column_names))})
        listing = listing_data[-1]
        listing['item-id'] = _sku_to_item_id(listing['seller-sku'])
        listing['pending-quantity'] = item_qty_in_pending.get(listing['seller-sku'], 0)
        if listing['item-id'] in item_listing_qty:
            item_listing_qty[listing['item-id']] += 1
        else:
            item_listing_qty[listing['item-id']] = 1

    for listing in listing_data:
        listing['item-listing-qty'] = item_listing_qty[listing['item-id']]
    return listing_data


# def _insert_new_listing(listing_from_amazon):
#     for listing in listing_from_amazon:
#         try:
#             listing_in_db = get_listing_by_source_id(source, listing['listing-id'])
#             if not listing_in_db:
#                 _insert_single_listing(listing)
#         except Exception as e:
#             new_e = Exception('Fail to insert listing {}'.format(listing['listing-id']), e)
#             _logger.exception(e)

def _adjust_qty_old(listing_from_amazon):
    all_inventory_data = fantasyard.get_inventory_data()
    for listing in listing_from_amazon:
        listing_in_db = get_listing_by_source_id(source, listing['listing-id'])
        if not listing_in_db:
            _logger.error("Can't find listing {} in db.".format(listing['listing-id']))
            continue
        qty = all_inventory_data[listing_in_db.item_id]
        update_qty_by_source_id(source, listing_in_db.listing_source_id, qty, int(listing['pending-quantity']))
        _logger.info('Qty of list {} is updated.'.format(listing_in_db.listing_source_id))


def _get_item_qty_in_pending():
    conn = connection.MWSConnection(Merchant=merchant_id)

    kw = {
        'CreatedAfter': '2016-07-01T18:12:21',
        'MarketplaceId': [marketplace_id],
        'OrderStatus': ['Pending']
    }
    result = {}
    order_list = conn.list_orders(**kw).ListOrdersResult.Orders.Order
    for order in order_list:
        item_list = conn.list_order_items(AmazonOrderId=order.AmazonOrderId).ListOrderItemsResult.OrderItems.OrderItem
        for item in item_list:
            if item.SellerSKU in result:
                result[item.SellerSKU] += int(item.QuantityOrdered)
            else:
                result[item.SellerSKU] = int(item.QuantityOrdered)
    return result


def _adjust_q4s(listing_from_amazon):
    all_inventory_data = fantasyard.get_inventory_data()
    # item_qty_in_pending = _get_item_qty_in_pending()
    changed = []
    for listing in listing_from_amazon:
        qty = all_inventory_data[listing['item-id']]
        listing['qty'] = qty
        if listing['seller-sku'] in adjust_q4s_bypass_list:
            continue
        if qty < 10:
            q4s = 0
        else:
            # pending_qty = item_qty_in_pending.get(listing['seller-sku'], 0)
            q4s = int(qty / 2 / listing['item-listing-qty']) - listing['pending-quantity']
            q4s = q4s if q4s > 0 else 0
            q4s = q4s if q4s < 10 else 9
        # q4s = 125
        if int(listing['quantity']) != q4s:
            listing['quantity'] = q4s
            changed.append(listing)
    _upload_q4s(changed)


def adjust_q4s():
    listing_list = Listing.query.filter_by(status=Listing.STATUS_OPEN, fixed_q4s=0).all()
    all_inventory_data = fantasyard.get_inventory_data()
    _logger.info('item qty in inventory list: {}'.format(len(all_inventory_data)))
    item_qty_in_pending = _get_item_qty_in_pending()
    changed = []
    item_list_qty_col = {}
    item_pending_qty_col = {}
    open_order_qty_col = {}
    for listing in listing_list:
        if listing.item_id in item_list_qty_col:
            item_list_qty_col[listing.item_id] += 1
        else:
            item_list_qty_col[listing.item_id] = 1

        pending_qty = item_qty_in_pending.get(listing.sku, 0)
        if listing.item_id in item_pending_qty_col:
            item_pending_qty_col[listing.item_id] += pending_qty
        else:
            item_pending_qty_col[listing.item_id] = pending_qty

        if listing.item_id not in open_order_qty_col:
            open_order_qty = Order.query.filter_by(status=Order.STATUS_OPEN, item_id=listing.item_id).count()
            open_order_qty_col[listing.item_id] = open_order_qty

    for listing in listing_list:
        if listing.item_id in all_inventory_data:
            qty = all_inventory_data[listing.item_id]
        else:
            qty = fantasyard.get_inventory_data(listing.item_id)
        if qty < 10:
            q4s = 0
            listing_qty = pending_qty = open_order_qty = None
        else:
            listing_qty = item_list_qty_col[listing.item_id]
            pending_qty = item_pending_qty_col[listing.item_id]
            open_order_qty = open_order_qty_col[listing.item_id]
            q4s = int(qty / 2 / listing_qty - pending_qty - open_order_qty)
            q4s = q4s if q4s > 0 else 0
            q4s = q4s if q4s < 10 else 9
            listing.update_q4s(q4s)
        _logger.debug('sku {}, orginal q4s {}, new q4s {}, qty {}'.format(listing.sku, listing.q4s, q4s, qty))
        if listing.q4s != q4s:
            # listing.q4s = q4s
            changed.append(listing)
        # listing.qty = qty
        listing.update_qty(qty)
        # _logger.debug('item:{} qty:{} q4s:{} pending: {} open order:{}'.format(listing.sku, listing.qty, listing.q4s, pending_qty, open_order_qty))

    _upload_q4s(changed)


def _upload_q4s(listing_list):
    if not listing_list:
        return
    with open('inventory_update_template.xml') as fd:
        xml_template = fd.read()
    template = Template(xml_template)
    feed_content = template.render(listing_list=listing_list)
    # print(feed_content)
    _submit_feed('_POST_INVENTORY_AVAILABILITY_DATA_', feed_content)
    _logger.info('{} listing(s) uploaded.'.format(len(listing_list)))




def _upload_q4s_old(listing_from_amazon):
    if not listing_from_amazon:
        return
    with open('inventory_update_template.xml') as fd:
        xml_template = fd.read()
    template = Template(xml_template)
    feed_content = template.render(listing_from_amazon=listing_from_amazon)
    print(feed_content)
    # _submit_feed('_POST_ORDER_FULFILLMENT_DATA_', feed_content)
    _logger.info('{} listing(s) uploaded.'.format(len(listing_from_amazon)))



def _save_listing(listing_from_amazon):
    for listing in listing_from_amazon:
        try:
            listing_in_db = get_listing_by_source_id(source, listing['listing-id'])
            if listing_in_db:
                listing_in_db.q4s = listing['quantity']
                listing_in_db.price = int(float(listing['price']) * 100)
                listing_in_db.pending_qty = int(listing['pending-quantity'])
                listing_in_db.qty = listing['qty']
            else:
                _insert_single_listing(listing)
        except Exception as e:
            _logger.exception(e)


def sync_listing_from_amazon():
    listing_list = _get_listing_data_from_amazon()
    for listing in listing_list:
        try:
            listing_in_local = get_listing_by_source_id(source, listing['listing-id'])
            if listing_in_local:
                kwag = {'q4s': listing['quantity'],
                        'price': int(float(listing['price']) * 100)}
                # listing_in_local.q4s = listing['quantity']
                # listing_in_local.price = int(float(listing['price']) * 100)
                # listing_in_local.last_sync_date = datetime.datetime.now()
                listing_in_local.sync(**kwag)
            else:
                _insert_single_listing(listing)
        except Exception as e:
            _logger.exception(e)


def refresh_listing_from_amazon():
    listing_data = _get_listing_data_from_amazon()
    _adjust_q4s(listing_data)
    _save_listing(listing_data)


def _get_listing_prices(asin):
    r = requests.get('https://www.amazon.com/dp/{}'.format(asin), headers=headers_for_get_prices)
    bs = BeautifulSoup(r.text, 'html.parser')
    div_list = bs.find_all('div', class_='a-box mbc-offer-row pa_mbc_on_amazon_offer')
    price_list = []
    for div in div_list:
        price = div.find('span', class_='a-size-medium a-color-price').string.strip()
        seller = div.find('span', class_='a-size-small mbcMerchantName').string.strip()
        shipping_contents = div.find('span', class_='a-size-small a-color-secondary').descendants
        shipping_contents = [c for c in shipping_contents if isinstance(c, str)]
        shipping_fee = _parser_shipping_fee(shipping_contents)
        if shipping_fee is None:
            continue
        o = type('', (object,), {})
        o.price = price
        o.seller = seller
        o.shipping = shipping_fee
        price_list.append(o)
    return price_list


def _parser_shipping_fee(contents):
    show_free_shipping = False
    price = None
    for c in contents:
        c2 = c.upper()
        if 'OVER' in c2:
            return None
        elif 'FREE SHIPPING' in c2:
            show_free_shipping = True
        else:
            for c3 in c2.split('\xa0'):
                if '$' in c3:
                    price = c3
    if not show_free_shipping and not price:
        raise Exception('Fail to parser shipping fee, contents:{}'.format(contents))
    return '0.00' if show_free_shipping else price



def init(flask_app, module_path, db_uri, logger):
    sys.path.append(module_path)

    from model.database import init_db
    init_db(flask_app, uri=db_uri)
    # from service.order import get_by_source_id, insert_order, get_open_tracking_number, get_shipped_order, close_order as close_order_by_id
    import model.listing
    import model.order
    import service.order as order_svc
    import service.listing as listing_svc
    global _logger, get_by_source_id, insert_order, get_open_tracking_number, get_shipped_order, close_order_by_id
    global insert_listing, get_listing_by_source_id, update_qty_by_source_id
    global Listing, Order
    _logger = logger
    get_by_source_id = order_svc.get_by_source_id
    insert_order = order_svc.insert_order
    get_open_tracking_number = order_svc.get_open_tracking_number
    get_shipped_order = order_svc.get_shipped_order
    close_order_by_id = order_svc.close_order

    insert_listing = listing_svc.insert_listing
    get_listing_by_source_id = listing_svc.get_listing_by_source_id
    update_qty_by_source_id = listing_svc.update_qty_by_source_id

    Listing = model.listing.Listing
    Order = model.order.Order


if __name__ == '__main__':
    sys.path.append('../')

    import common.log as logging

    logging.config('logger.config', 'task')

    from flask import Flask

    app = Flask(__name__)

    init(app, '../', 'sqlite:///../kikk.db', logging.logger)
    # insert_unshipped_order()
    # upload_tracking_number()
    # refresh_listing_from_amazon()

    # print([(i.price, i.shipping, i.seller) for i in _get_listing_prices('B015TP5L4K')])
    # sync_listing_from_amazon()
    adjust_q4s()



    # import sys
    # sys.path.append('../')
    # from flask import Flask
    # from model.database import init_db

    # app = Flask(__name__)
    # init_db(app, uri='sqlite:///../kikk.db')
    # from service.order import get_by_source_id, insert_order, get_open_tracking_number, get_shipped_order, close_order as close_order_by_id
    # # init(get_by_source_id, insert_order)
    # insert_unshipped_order()
    # upload_tracking_number()
    # # close_order()
