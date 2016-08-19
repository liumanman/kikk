import unittest
from flask import Flask
import os
import sys
from datetime import datetime

sys.path.append('../../')
from model.database import init_db


class TestOrder(unittest.TestCase):
    def setUp(self):
        self._create_items()

    def tearDown(self):
        self._clear_items()


    def _clear_items(self):
        for item in self._item_list:
            item.delete()

    def _create_items(self):
        item1 = Item()
        item1.item_id = '00-00-001'
        item1.description = 'item 00-00-001'
        item1.cost = 199
        item1.shipping_cost = 319
        item1.create()

        item2 = Item()
        item2.item_id = '00-00-002'
        item2.description = 'item 00-00-002'
        item2.cost = 299
        item2.shipping_cost = 329
        item2.create()

        item3 = Item()
        item3.item_id = '00-00-003'
        item3.description = 'item 00-00-003'
        item3.cost = 399
        item3.shipping_cost = 339
        item3.create()

        self._item_list = [item1, item2, item3]

    def create_order(self):
        order_date = datetime(2016, 6, 13, 14, 59, 25)
        shipping_full_addr = '16351 brancusi LN, Chino Hills , CA 91709'
        shipping_address='16351 brancusi ln'
        shipping_address2='test'
        shipping_city='Chino hills'
        shipping_state='CA'
        shipping_zipcode='91709'
        order = insert_order(source='AMZ', source_id='AMZ-001', order_date=order_date, item_id=self._item_list[0].item_id,
                             item_desc=self._item_list[0].description, item_cost=self._item_list[0].cost,
                             shipping_cost=self._item_list[0].shipping_cost,
                             price=999, qty=1, customer_name='evan liu', shipping_full_addr=shipping_full_addr,
                             shipping_address=shipping_address, shipping_address2=shipping_address2,
                             shipping_city=shipping_city, shipping_state=shipping_state, shipping_zipcode=shipping_zipcode)
        self.assertEqual(order.order_id > 0, True)
        self.assertEqual(order.source, 'AMZ')
        self.assertEqual(order.source_id, 'AMZ-001')
        self.assertEqual(order.order_date, order_date)
        self.assertEqual(order.item_id, self._item_list[0].item_id)
        self.assertEqual(order.item_cost, self._item_list[0].cost)
        self.assertEqual(order.shipping_cost, self._item_list[0].shipping_cost)
        self.assertEqual(order.price, 999)
        self.assertEqual(order.qty, 1)
        self.assertEqual(order.customer_name, 'evan liu')
        self.assertEqual(order.shipping_full_addr, shipping_full_addr)
        self.assertEqual(order.shipping_address, shipping_address)
        self.assertEqual(order.shipping_address2, shipping_address2)
        self.assertEqual(order.shipping_city, shipping_city)
        self.assertEqual(order.shipping_state, shipping_state)
        self.assertEqual(order.shipping_zipcode, shipping_zipcode)

        return order

    def test_create_order(self):
        self.create_order()

    def test_full_process(self):
        order = self.create_order()
        update_shipment(order.order_id, '12345')

        order2 = Order.get_by_id(order.order_id)
        self.assertIsNotNone(order2.shipping_date)
        self.assertEqual(order2.shipment_id, '12345')
        self.assertEqual(order2.status, Order.STATUS_SHIP_READY)

        update_tracking_number(order2.order_id, 't123456')
        order3 = Order.get_by_id(order2.order_id)
        self.assertEqual(order3.status, Order.STATUS_SHIPPED)

        close_order(order3.order_id)
        order4 = Order.get_by_id(order3.order_id)
        self.assertEqual(order4.status, Order.STATUS_CLOSED)





    def split_order(self):
        order_date = datetime(2016, 6, 13, 14, 59, 25)
        shipping_full_addr = '16351 brancusi LN, Chino Hills , CA 91709'
        order = create_order('AMZ', 'AMZ-001', order_date,
                             self._item_list[0].id, 999, 3, 'evan liu',
                             shipping_full_addr)
        new_order_list = split_order(order.id)
        self.assertEqual(order.qty, 1)
        self.assertEqual(len(new_order_list), 2)
        for new_order in new_order_list:
            self.assertEqual(new_order.id > 0, True)
            self.assertNotEqual(new_order.id, order.id)
            self.assertEqual(new_order.source, order.source)
            self.assertEqual(new_order.source_id, order.source_id)
            self.assertEqual(new_order.order_date, order.order_date)
            self.assertEqual(new_order.item_id, order.item_id)
            self.assertEqual(new_order.item_cost, order.item_cost)
            self.assertEqual(new_order.shipping_cost, order.shipping_cost)
            self.assertEqual(new_order.price, order.price)
            self.assertEqual(order.qty, 1)
            self.assertEqual(new_order.customer_name, order.customer_name)
            self.assertEqual(new_order.shipping_full_addr,
                             order.shipping_full_addr)

    def ship_order_3_tracking(self):
        order_date = datetime(2016, 6, 13, 14, 59, 25)
        shipping_full_addr = '16351 brancusi LN, Chino Hills , CA 91709'
        order = create_order('AMZ', 'AMZ-001', order_date,
                             self._item_list[0].id, 999, 3, 'evan liu',
                             shipping_full_addr)
        tracking_number_list = ['tracking1', 'tracking2', 'tracking3']
        order_list = ship_order(order.id, 339, *tracking_number_list)
        self.assertEqual(len(order_list), 3)
        for order in order_list:
            self.assertEqual(order.shipping_cost, 339)
            self.assertEqual(order.tracking_number in tracking_number_list, True)
            self.assertEqual(order.status, Order.STATUS_Shipped)
            self.assertIsNotNone(order.shipping_date)
        tracking_number_set = set(map(lambda x : x.tracking_number, order_list))
        self.assertEqual(tracking_number_set, set(tracking_number_list))

    def ship_order_1_tracking(self):
        order_date = datetime(2016, 6, 13, 14, 59, 25)
        shipping_full_addr = '16351 brancusi LN, Chino Hills , CA 91709'
        order = create_order('AMZ', 'AMZ-001', order_date,
                             self._item_list[0].id, 999, 3, 'evan liu',
                             shipping_full_addr)
        order_list = ship_order(order.id, None, 'tracking1')
        self.assertEqual(len(order_list), 1)
        self.assertEqual(order.shipping_cost, 319)
        self.assertEqual(order.status, Order.STATUS_Shipped)
        self.assertIsNotNone(order.shipping_date)
        self.assertEqual(order.tracking_number, 'tracking1')

    def no_test_update_order(self):
        order_date = datetime(2016, 6, 13, 14, 59, 25)
        shipping_full_addr = '16351 brancusi LN, Chino Hills , CA 91709'
        order = create_order('AMZ', 'AMZ-001', order_date,
                             self._item_list[0].id, 999, 3, 'evan liu',
                             shipping_full_addr)

        t1 = type('', (object,), {'tracking_number': 'xxx', 'cost': 399})
        update_order(order.id, 'O', 'test', t1)

        new_order = Order.get_by_id(order.id)
        self.assertEqual(new_order.status, Order.STATUS_SHIPPED)
        # self.assertEqual(new_order.tracking_numbers, True)
        self.assertEqual(new_order.tracking_numbers[0].tracking_number, 'xxx')
        # order2 = get_by_tracking_number('xxx')
        order2 = query_by(tracking_number='xxx', order_date=(None,'2016-06-12'))[0]
        self.assertEqual(order.id, order2.id)
        print(order2.order_date)


    def no_test_update_order_rollback(self):
        order_date = datetime(2016, 6, 13, 14, 59, 25)
        shipping_full_addr = '16351 brancusi LN, Chino Hills , CA 91709'
        order = create_order('AMZ', 'AMZ-001', order_date,
                             self._item_list[0].id, 999, 3, 'evan liu',
                             shipping_full_addr)

        t1 = type('', (object,), {'tracking_number': None, 'cost': 399})
        try:
            update_order(order.id, 'O', 'test', t1)
        except:
            pass

        new_order = Order.get_by_id(order.id)
        self.assertEqual(new_order.status, Order.STATUS_OPEN)



def _get_db_path(db_name):
    dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    return os.path.join(dir_path, '{}.db'.format(db_name))

if __name__ == '__main__':
    name = 'order_test'
    app = Flask(name)
    # init_db(app, 'sqlite:///{}.db'.format(name))
    init_db(app,'sqlite:///:memory:')

    from model.item import Item
    from model.order import Order
    from service.order import insert_order, split_order, ship_order, update_order, get_by_tracking_number, query_by, update_shipment, update_tracking_number, close_order

    unittest.main()

    db_path = _get_db_path(name)
    os.remove(db_path)

