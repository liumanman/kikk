from model.listing import Listing
from model.database import db

def insert_listing(**kwag):
    listing = Listing(**kwag)
    listing.insert()