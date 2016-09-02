import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
r = requests.get('https://www.amazon.com/dp/B0007QCSF2', headers=headers)
# r = requests.get('https://www.amazon.com/dp/B015TP5L4K', headers=headers)


with open('test', 'w') as fd:
    fd.write(r.text)
bs = BeautifulSoup(r.text, 'html.parser')
div_list = bs.find_all('div', class_='a-box mbc-offer-row pa_mbc_on_amazon_offer')
price = div_list[1].find('span', class_='a-size-medium a-color-price').string.strip()
shipping = list(div_list[1].find('span', class_='a-size-small a-color-secondary').descendants)
seller = div_list[1].find('span', class_='a-size-small mbcMerchantName').string.strip()
print(price, shipping, seller)

'''
['+\xa0Free Shipping']
[' ', <b>FREE Shipping</b>, ' on orders over $49.00 & FREE Returns. ', <a href="/gp/feature.html/ref=mk_fr_ret_dp_1?ie=UTF8&amp;docId=1000508701" onclick="return amz_js_PopWin(this.href,'AmazonHelp','width=550,height=550,resizable=1,scrollbars=1,toolbar=0,status=0');" target="AmazonHelp">Details</a>]
['+\xa0$5.00\xa0shipping']
'''