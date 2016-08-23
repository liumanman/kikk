from boto.mws import connection


merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'
conn = connection.MWSConnection(Merchant=merchant_id)

t = conn.get_lowest_offer_listings_for_asin(MarketplaceId=marketplace_id, ASINList=['B015TP5L4K'], ItemCondition='New')
# print(dir(t.GetLowestOfferListingsForASINResult[0].Product.LowestOfferListings.LowestOfferListing[0]))
for listing in t.GetLowestOfferListingsForASINResult[0].Product.LowestOfferListings.LowestOfferListing:
	# print(listing.Price.LandedPrice, listing.Price.ListingPrice, listing.Price.Shipping)
	print(listing.Qualifiers.FulfillmentChannel, listing.Price)
	# print(listing)


t2 = conn.get_competitive_pricing_for_asin(MarketplaceId=marketplace_id, ASINList=['B015TP5L4K'])
# print(dir(t2.GetCompetitivePricingForASINResult[0].Product.CompetitivePricing[0].CompetitivePrices.CompetitivePrice[0]))
for pricing in t2.GetCompetitivePricingForASINResult[0].Product.CompetitivePricing:
	print('------')
	# print(pricing)
	for price in pricing.CompetitivePrices.CompetitivePrice:
		print(price)