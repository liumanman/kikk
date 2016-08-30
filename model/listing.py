from datetime import datetime
from model.database import db
from model.model_base import Model
from model.item import Item

class Listing(Model):
    listing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listing_source_id = db.Column(db.String(50), nullable=False)
    listing_source = db.Column(db.String(20), nullable=False)
    item_id = db.Column(db.String(20), db.ForeignKey('item.item_id'))
    item_desc = db.Column(db.String(128), nullable=False)
    q4s = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer)
    price = db.Column(db.Integer, nullable=False)
    pending_qty = db.Column(db.Integer, nullable=False)
    source_item_id = db.Column(db.String(20), nullable=True)
    listing_date = db.Column(db.DateTime, nullable=True)
    memo = db.Column(db.Text)
    status = db.Column(db.String(1), nullable=False)
    in_date = db.Column(db.DateTime, nullable=False)
    sync_status = db.Column(db.String(1), nullable=False)

    STATUS_OPEN = 'O'
    STATUS_CLOSED = 'C'

    SYNC_STATUS_PENDING = 'P'
    SYNC_STATUS_DONE = 'D'

    def __init__(self, **kwag):
        for name, value in kwag.items():
            setattr(self, name, value)
        
    def __repr__(self):
        return '<Listing {0} - {1} {2} {3} {4}>'.format(self.listing_id,
            self.listing_source_id, self.item_id, self.price, self.q4s)

    def insert(self):
        if not self.item_id:
            raise Exception("item id can't be null.")
        item = Item.get_by_id(self.item_id)
        if not item:
            raise Exception("Can't find item {}.".format(self.item_id))
        with db.session.begin():
            self.item_desc = item.description
            self.status = Listing.STATUS_OPEN
            self.in_date = datetime.now()
            self.sync_status = Listing.SYNC_STATUS_DONE
            db.session.add(self)

    def update_qty(self, qty, pending_qty):
        if qty is None:
            qty = self.qty
        if pending_qty is None:
            pending_qty =self.pending_qty
        q4s = int(qty / 2) - pending_qty
        q4s = q4s if q4s > 0 else 0
        q4s = q4s if q4s < 10 else 10
        if q4s == self.q4s and qty == self.qty:
            return False
        else:
            with db.session.begin():
                self.qty = qty 
                self.pending_qty = pending_qty
                self.q4s = q4s
                self.sync_status = Listing.SYNC_STATUS_PENDING
            return True

    # def update_pending_qty(self, pending_qty):
    #     pass
