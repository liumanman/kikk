from boto.mws import connection
import time

merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'

conn = connection.MWSConnection(Merchant=merchant_id)
destination = {'DeliveryChannel': 'SQS',
               'AttributeList':[{'Key': 'sqsQueueUrl', 'Value': 'https://sqs.us-west-2.amazonaws.com/822634784734/AnyOfferChangedQueue'}]}
# conn.register_destination(MarketplaceId=marketplace_id, Destination=destination)
# conn.send_test_notification_to_destination(MarketplaceId=marketplace_id, Destination=destination)

subscription = {'NotificationType': 'AnyOfferChanged',
                'Destination': destination,
                'IsEnabled': True}
# r = conn.create_subscription(MarketplaceId=marketplace_id, Subscription=subscription)
r = conn.list_subscriptions(MarketplaceId=marketplace_id)
print(r)
