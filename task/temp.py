from boto.mws import connection
import time

merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'

conn = connection.MWSConnection(Merchant=merchant_id)
requset_resp = conn.request_report(ReportType='_GET_MERCHANT_LISTINGS_DATA_')
request_id = requset_resp.RequestReportResult.ReportRequestInfo.ReportRequestId
request_status = requset_resp.RequestReportResult.ReportRequestInfo.ReportProcessingStatus

while True:
    request_result = conn.get_report_request_list(ReportRequestIdList=[request_id])
    info = request_result.GetReportRequestListResult.ReportRequestInfo[0]
    id = info.ReportRequestId
    status = info.ReportProcessingStatus
    if status in ('_SUBMITTED_', '_IN_PROGRESS_'):
        print('Sleeping and check again....')
        time.sleep(60)
    elif status in ('_DONE_', '_DONE_NO_DATA_'):
        report_id = info.GeneratedReportId
        break
    else:
        print("Report processing error. Quit.", status)
        break

if report_id:
    print(report_id)
    report = conn.get_report(ReportId=report_id)