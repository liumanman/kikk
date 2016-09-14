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
    sku = db.Column(db.String(20), nullable=False)
    q4s = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer)
    price = db.Column(db.Integer, nullable=False)
    min_price = db.Column(db.Integer)
    regular_price = db.Column(db.Integer)
    pending_qty = db.Column(db.Integer, nullable=False)
    source_item_id = db.Column(db.String(20), nullable=True)
    listing_date = db.Column(db.DateTime, nullable=True)
    memo = db.Column(db.Text)
    status = db.Column(db.String(1), nullable=False)
    in_date = db.Column(db.DateTime, nullable=False)
    last_sync_date = db.Column(db.DateTime, nullable=False)
    last_q4s_date = db.Column(db.DateTime)
    last_q4s = db.Column(db.Integer)
    last_price_date = db.Column(db.DateTime)
    last_price = db.Column(db.Integer)
    buy_box_price = db.Column(db.Integer)
    buy_box_seller = db.Column(db.String(64))
    offer_box_price_1 = db.Column(db.Integer)
    offer_box_seller_1 = db.Column(db.String(64))
    offer_box_price_2 = db.Column(db.Integer)
    offer_box_seller_2 = db.Column(db.String(64))
    offer_box_price_3 = db.Column(db.Integer)
    offer_box_seller_3 = db.Column(db.String(64))
    last_competitive_prices_date = db.Column(db.DateTime)

    auto_q4s = db.Column(db.Integer, nullable=False)
    auto_price = db.Column(db.Integer, nullable=False)
    listing_url = db.Column(db.String(512))

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
        # if not item:
        #     raise Exception("Can't find item {}.".format(self.item_id))
        with db.session.begin():
            self.item_desc = item.description if item else self.item_id
            # self.item_desc = item.description
            self.status = Listing.STATUS_OPEN
            self.in_date = datetime.now()
            self.last_sync_date = datetime.now()
            self.auto_q4s = 0
            self.auto_price = 0
            # self.sync_status = Listing.SYNC_STATUS_DONE
            db.session.add(self)

    def sync(self, **kwag):
        with db.session.begin():
            for k, v in kwag.items():
                setattr(self, k, v)
                self.last_sync_date = datetime.now()

    def update_qty_old(self, qty, pending_qty):
        if qty is None:
            qty = self.qty
        if pending_qty is None:
            pending_qty = self.pending_qty
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
                # self.sync_status = Listing.SYNC_STATUS_PENDING
            return True

    def update_qty(self, qty):
        with db.session.begin():
            self.qty = qty

    def update_last_q4s(self, q4s):
        with db.session.begin():
            self.last_q4s = q4s
            self.last_q4s_date = datetime.now()

    def update_competitive_prices(self, last_competitive_prices_datae, buy_box_price, *offer_box_prices):
        if offer_box_prices is None:
            offer_box_prices = []
        with db.session.begin():
            self.buy_box_seller, self.buy_box_price = (None, None) if buy_box_price is None else (
                buy_box_price.seller, buy_box_price.total_price)
            self.offer_box_price_1, self.offer_box_seller_1 = (
                offer_box_prices[0].total_price, offer_box_prices[0].seller) if offer_box_prices else (None, None)
            self.offer_box_price_2, self.offer_box_seller_2 = (
                offer_box_prices[1].total_price, offer_box_prices[1].seller) if len(offer_box_prices) > 1 else (None, None)
            self.offer_box_price_3, self.offer_box_seller_3 = (
                offer_box_prices[2].total_price, offer_box_prices[2].seller) if len(offer_box_prices) > 2 else (None, None)
            self.last_competitive_prices_date = last_competitive_prices_datae

    def update_last_price(self, price):
        if price == self.price:
            return
        with db.session.begin():
            self.last_price = price
            self.last_price_date = datetime.now()

    def append_memo(self, memo):
        new_content = '[{}]\n{}\n'.format(datetime.now(), memo)
        with db.session.begin():
            self.memo = '' if self.memo is None else self.memo
            self.memo = new_content + self.memo

            # def update_pending_qty(self, pending_qty):
            #     pass
