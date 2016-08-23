from boto.mws import connection


merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'
conn = connection.MWSConnection(Merchant=merchant_id)

report = conn.get_report(ReportId='2657077211017035')
with open('temp.list', 'w+b') as fd:
    # flat = report.decode('ascii')
    # fd.write(report)
    report.split('\n')
# print(flat)
