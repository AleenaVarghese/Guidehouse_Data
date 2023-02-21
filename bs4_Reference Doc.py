# bs4 libraries
from bs4 import BeautifulSoup
import requests
import warnings
warnings.simplefilter(
    'ignore',
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

r = requests.get(self.main_url_Refrigerator, verify=False , auth=('user', 'pass'),proxies={'http': '222.255.169.74:8080'},
timeout=25, headers={
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"})
print("2***")
base_soup = BeautifulSoup(r.content, 'html.parser')
#print(base_soup.text)
mydivs = soup.find_all("div", {"class": "stylelistrow"})
row_list = base_soup.findAll('a')

for EachPart in soup.select('div[class*="listing-col-"]'):
    print EachPart.get_text()
product_number = 1
product_details = soup.select('div[data-tile='+'"'+str(product_number)+'"'+']')


