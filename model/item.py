# from model.database import db
from model.database import db
from model.model_base import Model


class Item(Model):
    item_id = db.Column(db.String(20), primary_key=True, nullable=False)
    description = db.Column(db.String(128), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    shipping_cost = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(512))
    product_url = db.Column(db.String(512))

    def __init__(self):
        pass

    def create(self):
        with db.session.begin():
            db.session.add(self)

    def update_shipping_cost(self, shipping_cost):
        if shipping_cost is None:
            raise Exception('shipping_cost can''t be null.')
        with db.session.begin(subtransactions=True):
            self.shipping_cost = shipping_cost
            db.session.commit()

    def delete(self):
        # db.session.rollback()
        with db.session.begin():
            db.session.delete(self)
        # db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Item.query.get(id)
