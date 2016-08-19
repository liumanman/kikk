from model.item import Item
from model.order import Order
from model.shipping import TrackingNumber

from model.database import db


def insert_order_2(source, source_id, order_date, item_id, price,
                 qty, customer_name, shipping_full_addr):
    item = Item.get_by_id(item_id)
    if not item:
        raise Exception('Can''t find item {}'.format(item_id))
    order = Order()
    order.source = source
    order.source_id = source_id
    order.order_date = order_date
    order.item_id = item.item_id
    order.item_desc = item.description
    order.price = price
    order.qty = qty
    order.item_cost = item.cost
    order.customer_name = customer_name
    order.shipping_full_addr = shipping_full_addr
    order.shipping_cost = item.shipping_cost

    order.create()
    return order

def insert_order(**kwag):
    if 'item_id' not in kwag:
        raise Exception('item_id is required.')
    item_id = kwag['item_id']
    item = Item.get_by_id(item_id)
    if not item:
        raise Exception('Can''t find item {}'.format(item_id))

    order = Order()
    order.item_desc = item.description
    order.item_cost = item.cost
    for name,value in kwag.items():
        setattr(order, name, value)
    order.create()
    return order


def ship_order(order_id, shipping_cost=None,
               *tracking_number_list):
    if not tracking_number_list:
        raise Exception('Tracking numbers cannot be null.')
    order = Order.get_by_id(order_id)
    if not order:
        raise Exception('Cannot find order {}'.format(order_id))
    if len(tracking_number_list) > 1 and len(tracking_number_list) != order.qty:
        raise Exception('tracking number qty has to be 1 or equal item qty.')
    item = Item.get_by_id(order.item_id)
    if shipping_cost is not None:
        item.update_shipping_cost(shipping_cost)
    else:
        if not item.shipping_cost:
            raise Exception('Please input shipping cost.')
        shipping_cost = item.shipping_cost
    new_order_list = None
    if len(tracking_number_list) > 1:
        new_order_list = order.split()
        for i in range(len(new_order_list)):
            new_order_list[i].ship(tracking_number_list[i], shipping_cost)
    order.ship(tracking_number_list[-1], shipping_cost)

    new_order_list = new_order_list or []
    new_order_list.append(order)
    return new_order_list


def split_order(order_id):
    order = Order.get_by_id(order_id)
    return order.split()


def update_order(order_id, status, memo, *tracking_number_list):
    with db.session.begin(subtransactions=True):
        order = Order.get_by_id(order_id)
        if not order:
            raise Exception('Can''t find order {}'.format(order_id))
        if status == Order.STATUS_VOID:
            order.void()
        elif tracking_number_list and order.status in [Order.STATUS_OPEN, Order.STATUS_SHIPPED]:
            if order.status == Order.STATUS_OPEN:
                order.ship()
            elif order.status == Order.STATUS_SHIPPED:
                for tn in order.tracking_numbers:
                    tn.remove()

            for tn in tracking_number_list:
                if 'tracking_number' not in tn or not tn['tracking_number']:
                    raise Exception('tracking number cannot be null.')
                tracking_number = TrackingNumber(order_id, tn['tracking_number'], tn['cost'])
                tracking_number.create()
        elif status == Order.STATUS_SHIPPED and not tracking_number_list:
            for tn in order.tracking_numbers:
                tn.remove()
            order.cancel_ship()

        order.update_memo(memo)

def update_shipment(order_id, shipment_id):
    order = Order.get_by_id(order_id)
    if not order:
        raise Exception("Can't find order {}".format(order_id))
    order.update_shipment(shipment_id)

def update_tracking_number(order_id, *tn_data):
    if not tracking_numbers:
        raise Exception('tracking number is null.')
    order = Order.get_by_id(order_id)
    if not order:
        raise Exception("can't find order {}".format(order_id))
    with db.session.begin():
        for tn in tn_data:
            tracking_number = TrackingNumber(order_id, tn.tracking_number, 0)
            tracking_number.shipped_qty = tn.qty
            tracking_number.carrier = tn.carrier 
            tracking_number.shipping_method = tn.shipping_method 
            # tracking_number.shipping_method = 'First Class' 
            tracking_number.create()
        order.ship()

def close_order(order_id):
    order = Order.get_by_id(order_id)
    if not order:
        raise Exception("Can't find order {}".format(order_id))
    order.close()        


def get_by_tracking_number(tracking_number):
    return Order.get_by_tracking_number(tracking_number)


def query_by(**filters):
    return Order.query_by(**filters)

def get_by_source_id(source, source_id):
    return Order.get_by_source_id(source, source_id)

def get_open_orders():
    return query_by(status=Order.STATUS_OPEN)

def get_ship_ready_order():
    return query_by(status=Order.STATUS_SHIP_READY)

def get_shipped_order():
    return query_by(status=Order.STATUS_SHIPPED)

def get_by_id(order_id):
    return Order.get_by_id(order_id)

def get_open_tracking_number():
    return TrackingNumber.query.join(Order).filter(Order.status==Order.STATUS_SHIPPED)
    # return TrackingNumber.query.filter_by(status=TrackingNumber.STATUS_OPEN)