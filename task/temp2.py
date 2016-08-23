from boto.mws import connection


merchant_id = 'A2BD7G5CIBE1BV'
marketplace_id = 'ATVPDKIKX0DER'
conn = connection.MWSConnection(Merchant=merchant_id)

report = conn.get_report(ReportId='2657077211017035')
# with open('temp.list', 'w+b') as fd:
#     fd.write(report)
lines = report.decode('ISO-8859-1').strip().split('\n')
column_names = lines[0].split('\t')
for column in column_names:
	print(column)
listing_data = []
for i in range(1, len(lines)):
	v_list = lines[i].split('\t')
	listing_data.append({column_names[j]: v_list[j] for j in range(len(column_names))})
for listing in listing_data:
	print(listing['seller-sku'])
