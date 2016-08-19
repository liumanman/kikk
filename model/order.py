# from model.database import db
from sqlalchemy import and_
from model.database import db
from model.model_base import Model
from datetime import datetime, timedelta
from model.shipping import TrackingNumber


class Order(Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.String(8), nullable=False)
    source_id = db.Column(db.String(20), nullable=False)
    # item_id = db.Column(db.String(20), nullable=False)
    item_id = db.Column(db.String(20), db.ForeignKey('item.item_id'))
    item_desc = db.Column(db.String(128), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    item_cost = db.Column(db.Integer, nullable=False)
    shipping_cost = db.Column(db.Integer)
    other_cost = db.Column(db.Integer)
    status = db.Column(db.String(1), nullable=False)
    customer_name = db.Column(db.String(128))
    shipping_full_addr = db.Column(db.String(256))
    shipping_address = db.Column(db.String(256))
    shipping_address2 = db.Column(db.String(256))
    shipping_city = db.Column(db.String(128))
    shipping_state = db.Column(db.String(32))
    shipping_zipcode = db.Column(db.String(16))
    shipping_date = db.Column(db.DateTime)
    in_date = db.Column(db.DateTime, nullable=False)
    edit_date = db.Column(db.DateTime)
    pending_date = db.Column(db.DateTime)
    close_date = db.Column(db.DateTime)
    void_date = db.Column(db.DateTime)
    shipment_id = db.Column(db.String(16))
    order_item_id = db.Column(db.String(20))

    memo = db.Column(db.Text)
    tracking_numbers = db.relationship('TrackingNumber', backref='order', lazy='dynamic')
    item = db.relationship('Item')

    default_fields = ['source', 'source_id', 'item_id', 'item_desc', 'order_date']

    STATUS_OPEN = 'O'
    STATUS_PENDING = 'P'
    STATUS_SHIPPED = 'S'
    STATUS_CLOSED = 'C'
    STATUS_VOID = 'V'
    STATUS_SHIP_READY = 'R'

    SOURCE_EBAY = 'eBay'
    SOURCE_AMAZON = 'Amazon'

    # def __init__(self, source=None, source_id=None, item_id=None,
    #              item_desc=None, order_date=None, price=None,
    #              qty=None, item_cost=None, customer_name=None,
    #              shipping_address=None, shipping_address2=None,
    #              shipping_city=None, shipping_state=None,
    #              shipping_zipcode=None, shipping_full_addr=None):
    #     self.source = source
    #     self.source_id = source_id
    #     self.item_id = item_id
    #     self.item_desc = item_desc
    #     self.order_date = order_date
    #     self.price = price
    #     self.qty = qty
    #     self.item_cost = item_cost
    #     self.shipping_full_addr = shipping_full_addr
    #     self.customer_name = customer_name
    #     self.shipping_address = shipping_address
    #     self.shipping_address2 = shipping_address2
    #     self.shipping_city = shipping_city
    #     self.shipping_state = shipping_state
    #     self.shipping_zipcode = shipping_zipcode

    def __init__(self, **kwag):
        for name,value in kwag.items():
            setattr(self, name, value)

    def __repr__(self):
        return '<Order {} - {}>'.format(self.item_id, self.item_desc)

    def create(self):
        with db.session.begin(subtransactions=True):
            self.status = Order.STATUS_OPEN
            self.total_price = int(self.price) * int(self.qty) 
            self.in_date = datetime.now()

            db.session.add(self)
            # db.session.commit()

    # def modify(self):
    #     with db.session.begin():
    #         if self.status != Order.STATUS_OPEN:
    #             raise Exception('Only open order can be modified.')
    #         self.edit_date = datetime.now()

    def void(self):
        if self.status not in [Order.STATUS_OPEN, Order.STATUS_PENDING]:
            raise Exception('Only open or pending order can be voided.')
        self.void_date = datetime.now()
        self.status = Order.STATUS_VOID

        db.session.commit()

    def pending(self):
        if self.status != Order.STATUS_OPEN:
            raise Exception('Only open order can be pending.')
        self.pending_date = datetime.now()

        db.session.commit()

    def update_shipment(self, shipment_id):
        if not shipment_id:
            raise Exception('shipment_id is null.')
        if self.status != Order.STATUS_OPEN:
            raise Exception('Only open order can be updated shipment.')
        with db.session.begin():
            self.shipment_id = shipment_id
            self.status = Order.STATUS_SHIP_READY
            # self.shipping_date = datetime.now()


    def ship(self):
        if self.status != Order.STATUS_SHIP_READY:
            raise Exception('Only SHIP_READY order can be shipped.')
        # if not tracking_number:
        #     raise Exception('Tracking number can''t null')
        # self.tracking_number = tracking_number
        # self.shipping_cost = shipping_cost
        with db.session.begin():
            self.status = Order.STATUS_SHIPPED
            self.shipping_date = datetime.now()

    def cancel_ship(self):
        if self.status != Order.STATUS_SHIPPED:
            raise Exception('Order status is not shippped')
        with db.session.begin():
            self.shipping_cost = None
            self.shipping_date = None
            self.status = Order.STATUS_OPEN

    def close(self):
        if self.status != Order.STATUS_SHIPPED:
            raise Exception('Only shipped order can be close')
        with db.session.begin():
            self.close_date = datetime.now()
            self.status = Order.STATUS_CLOSED

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def split(self):
        if self.status not in [Order.STATUS_OPEN, Order.STATUS_PENDING]:
            raise Exception('Only open or pending order can be splited.')
        if self.qty < 2:
            raise Exception('Cannot split an order which qty is less than 2.')
        qty = self.qty
        self.qty = 1
        new_order_list = []
        for i in range(qty - 1):
            # new_order = copy.copy(self)
            new_order = Order()
            new_order.source = self.source
            new_order.source_id = self.source_id
            new_order.item_id = self.item_id
            new_order.item_desc = self.item_desc
            new_order.order_date = self.order_date
            new_order.price = self.price
            new_order.total_price = self.total_price
            new_order.qty = self.qty
            new_order.item_cost = self.item_cost
            new_order.shipping_cost = self.shipping_cost
            new_order.shipping_full_addr = self.shipping_full_addr
            new_order.customer_name = self.customer_name
            new_order.status = self.status
            new_order.in_date = self.in_date
            new_order.memo = new_order.memo or ''
            new_order.memo = new_order.memo + 'Create from splited order {}\n'.format(self.id)
            db.session.add(new_order)
            new_order_list.append(new_order)
        self.memo = self.memo or ''
        self.memo = self.memo + 'Splitd to order(s).'
        db.session.commit()
        return new_order_list

    def update_memo(self, memo):
        with db.session.begin():
            self.memo = memo

    @staticmethod
    def get_by_id(id):
        return Order.query.get(id)

    @staticmethod
    def get_by_status(status):
        return Order.query.filter_by(status=status).all()

    @staticmethod
    def get_by_tracking_number(tn):
        return Order.query.join(TrackingNumber) \
            .filter(TrackingNumber.tracking_number == tn).first()

    @staticmethod
    def get_by_source_id(source, source_id):
        if source not in [Order.SOURCE_AMAZON, Order.SOURCE_EBAY]:
            raise Exception('Invalid source {}'.format(source))
        return Order.query.filter_by(source=source, source_id=source_id).all()


    @staticmethod
    def query_by(**filters):
        # keys = filters.keys()
        # condition = []
        # if 'order_id' in keys:
        #     condition.append(Order.id == filters['order_id'])
        # if 'tracking_number' in keys:
        #     condition.append(getattr(TrackingNumber,'tracking_number') == filters['tracking_number'])
        # if 'status' in keys:
        #     condition.append(Order.status == filters['status'])
        # if 'item_id' in keys:
        #     condition.append(Order.item_id == filters['item_id'])

        condition = []
        for k, v in filters.items():
            if k == 'tracking_number':
                condition.append(getattr(TrackingNumber, 'tracking_number') == filters['tracking_number'])
            elif k in ('order_date', 'shipping_date'):
                if v[0]:
                    condition.append(getattr(Order, k) >= datetime.strptime(v[0], '%m/%d/%Y'))
                if len(v) > 1 and v[1]:
                    condition.append(getattr(Order, k) < datetime.strptime(v[1], '%m/%d/%Y') + timedelta(days=1))
            else:
                condition.append(getattr(Order, k) == v)

        order_list =  Order.query.outerjoin(TrackingNumber).filter(and_(*condition)).all()
        return order_list
