from boto.mws import connection
from dateutil import parser as tp
import time
from jinja2 import Template


merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'
source = 'Amazon'
order_fulfillment_template = 'order_fulfillment_template.xml'

# def init(get_by_source_id_fun, insert_order_fun):
#     global get_by_source_id, insert_order
#     get_by_source_id = get_by_source_id_fun
#     insert_order = insert_order_fun


def insert_unshipped_order():
    conn = connection.MWSConnection(Merchant=merchant_id)

    kw = {
        'CreatedAfter': '2016-07-01T18:12:21',
        'MarketplaceId': [marketplace_id],
        'OrderStatus': ['Unshipped', 'PartiallyShipped']
    }
    order_list = conn.list_orders(**kw).ListOrdersResult.Orders.Order
    # item_list = conn.list_order_items(AmazonOrderId=order_list[0].AmazonOrderId)
    for order in order_list:
        if not get_by_source_id(source, order.AmazonOrderId):
            shipping_state = _short_state(order.ShippingAddress.StateOrRegion)
            item_list = conn.list_order_items(AmazonOrderId=order.AmazonOrderId).ListOrderItemsResult.OrderItems.OrderItem
            order_date = tp.parse(order.PurchaseDate).astimezone() 
            for item in item_list:
                try:
                    item_id = item.SellerSKU.split('-')[0]
                    insert_order(source=source, source_id=order.AmazonOrderId, order_date=order_date, item_id=item_id,
                                 price=int(float(item.ItemPrice.Amount)*100)/int(item.QuantityOrdered), qty=item.QuantityOrdered, customer_name=order.ShippingAddress.Name,
                                 shipping_address=order.ShippingAddress.AddressLine1,
                                 shipping_address2='{0} {1}'.format(getattr(order.ShippingAddress, 'AddressLine2', ''),getattr(order.ShippingAddress, 'AddressLine3', '')), 
                                 shipping_city=order.ShippingAddress.City,
                                 shipping_state=shipping_state,
                                 shipping_zipcode=order.ShippingAddress.PostalCode,
                                 shipping_full_addr=_addr_to_str(order.ShippingAddress),
                                 order_item_id=item.OrderItemId)
                    _logger.info('order# {0}, item# {1}'.format(order.AmazonOrderId, item.SellerSKU))
                except Exception as e:
                    logger.error('Exception with order# {0}, item# {1}'.format(order.AmazonOrderId, item.SellerSKU))
                    logger.exception(e)
                time.sleep(1)

def _addr_to_str(address):
    attr_list = dir(address)
    addr_str = '{0}\n{1}'.format(address.Name, address.AddressLine1)
    if 'AddressLine2' in attr_list:
        addr_str = addr_str + '\n' + address.AddressLine2
    if 'AddressLine3' in attr_list:
        addr_str = addr_str + '\n' + address.AddressLine3
    addr_str = addr_str + '\n{0},{1} {2}'.format(address.City, address.StateOrRegion, address.PostalCode)
    return addr_str

    # return '{0}\n{1}\n{2}\n{3}\{4},{5} {6}'.format(address.Name, address.AddressLine1, address.AddressLine2,
    #                                                address.AddressLine3, address.City, address.StateOrRegion,
    #                                                address.PostalCode) 

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
                n = n + 1
    _logger.info('{} order(s) are closed.'.format(n))


def upload_tracking_number():
    tn_list = list(get_open_tracking_number())
    if not tn_list:
        return
    with open(order_fulfillment_template) as fd:
        xml_template = fd.read()
    template = Template(xml_template)
    feed_content = template.render(tracking_number_list=tn_list)

    conn = connection.MWSConnection(Merchant=merchant_id)
    feed = conn.submit_feed(
        FeedType='_POST_ORDER_FULFILLMENT_DATA_',
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
        info =  submission_list.GetFeedSubmissionListResult.FeedSubmissionInfo[0]
        id = info.FeedSubmissionId
        status = info.FeedProcessingStatus
        _logger.info('Submission Id: {}. Current status: {}'.format(id, status))

        if status in ('_SUBMITTED_', '_IN_PROGRESS_', '_UNCONFIRMED_'):
            _logger.info('Sleeping and check again....')
            time.sleep(60)
        elif status == '_DONE_':
            feedResult = conn.get_feed_submission_result(FeedSubmissionId=id)
            _logger.debug(feedResult)
            _logger.info('{} tracking number(s) uploaded.'.format(len(tn_list)))
            break
        else:
            print("Submission processing error. Quit.", status)
            break




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


def init(flask_app, module_path, db_uri, logger):
    import sys
    sys.path.append(module_path)

    from model.database import init_db
    init_db(flask_app, uri=db_uri)
    from service.order import get_by_source_id, insert_order, get_open_tracking_number, get_shipped_order, close_order as close_order_by_id
    global _logger
    _logger = logger


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    init(app, '../', 'sqlite:///../kikk.db')
    insert_unshipped_order()
    upload_tracking_number()

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