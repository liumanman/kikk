from model.database import db
from model.model_base import Model
from datetime import datetime


class TrackingNumber(Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    tracking_number = db.Column(db.String(50), nullable=False)
    carrier = db.Column(db.String(10))
    cost = db.Column(db.Integer, nullable=False)
    in_date = db.Column(db.DateTime, nullable=False)
    shipping_method = db.Column(db.String(20))
    shipped_qty = db.Column(db.Integer, nullable=False)
    # status = db.Column(db.String(1))
    # order = db.relationship('Order')

    STATUS_OPEN = 'O'
    STATUS_CLOSED = 'C'


    default_fields = ['id', 'order_id', 'tracking_number', 'cost']

    def __init__(self, order_id, tracking_number, cost=0, carrier=None):
        self.order_id = order_id
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.cost = cost


    def create(self):
        if not self.tracking_number:
            raise Exception('Tracking number can''t be null.')
        if not self.order_id:
            raise Exception('Order id can''t be empany')

        with db.session.begin():
            if TrackingNumber.query.filter_by(tracking_number=self.tracking_number).first():
                raise Exception('Tracking# {} has been added into another order'.format(self.tracking_number))
            self.in_date = datetime.now()
            db.session.add(self)

    def remove(self):
        with db.session.begin():
            db.session.delete(self)
