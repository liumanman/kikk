from model.listing import Listing
from model.database import db

def insert_listing(**kwag):
    listing = Listing(**kwag)
    listing.insert()

def get_listing_by_source_id(source, source_id):
    return Listing.query.filter_by(listing_source=source, listing_source_id=source_id).first()

def update_qty_by_source_id(source, source_id, qty, pending_qty=0):
    listing = get_listing_by_source_id(source, source_id)
    if not listing:
        raise Exception("Can't find listing {} in db.".format(listing_id))
    listing.update_qty(qty, pending_qty)

