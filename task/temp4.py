from boto.mws import connection
import time

merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'

with open('inventory_update_template.xml') as fd:
    feed_content = fd.read()

conn = connection.MWSConnection(Merchant=merchant_id)
feed = conn.submit_feed(
    FeedType='_POST_INVENTORY_AVAILABILITY_DATA_',
    PurgeAndReplace=False,
    MarketplaceIdList=[marketplace_id],
    content_type='text/xml',
    FeedContent=feed_content.encode('utf-8')
)

feed_info = feed.SubmitFeedResult.FeedSubmissionInfo
print('Submitted product feed: ' + str(feed_info))

while True:
    submission_list = conn.get_feed_submission_list(
        FeedSubmissionIdList=[feed_info.FeedSubmissionId]
    )
    info =  submission_list.GetFeedSubmissionListResult.FeedSubmissionInfo[0]
    id = info.FeedSubmissionId
    status = info.FeedProcessingStatus
    print('Submission Id: {}. Current status: {}'.format(id, status))

    if status in ('_SUBMITTED_', '_IN_PROGRESS_', '_UNCONFIRMED_'):
        print('Sleeping and check again....')
        time.sleep(60)
    elif status == '_DONE_':
        feedResult = conn.get_feed_submission_result(FeedSubmissionId=id)
        print(feedResult)
        break
    else:
        print("Submission processing error. Status: {}".format(status))
        break